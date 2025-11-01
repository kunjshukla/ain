"""
ResumeRAG: Retrieval-Augmented Generation system for resume analysis.

This module provides semantic search capabilities over resume content using:
- Sentence transformers for embedding generation
- Redis for vector storage and retrieval
- Cosine similarity for relevance scoring

Used by the interview system to retrieve relevant context from candidate resumes
for question generation and evaluation.
"""

import os
# Disable TensorFlow to avoid Keras 3 compatibility issues
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import re
import json
import numpy as np
import redis
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class ResumeRAG:
    """
    Retrieval-Augmented Generation system for resume content.
    
    Features:
    - Intelligent resume chunking (section-aware and paragraph-based)
    - Semantic embedding generation using MiniLM
    - Redis-backed vector storage with TTL
    - Efficient semantic search with relevance scoring
    """
    
    def __init__(
        self,
        model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        redis_db: int = 0,
        ttl: int = 3600
    ):
        """
        Initialize ResumeRAG system.
        
        Args:
            model_name: HuggingFace sentence transformer model name
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            ttl: Time-to-live for stored embeddings (seconds)
        """
        logger.info(f"Initializing ResumeRAG with model: {model_name}")
        
        # Initialize embedding model
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize Redis client
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=False,  # We'll handle decoding manually for embeddings
            socket_timeout=5
        )
        
        self.ttl = ttl
        
        # Verify connections
        try:
            self.redis_client.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    def chunk_resume(self, resume_text: str, max_chunk_size: int = 500) -> List[Dict[str, str]]:
        """
        Chunk resume into logical segments for embedding.
        
        Attempts to detect resume sections (EXPERIENCE, SKILLS, etc.) and split
        intelligently. Falls back to paragraph-based chunking for unstructured resumes.
        
        Args:
            resume_text: Raw resume text
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of chunks with type and content
        """
        if not resume_text or not resume_text.strip():
            return []
        
        chunks = []
        
        # Remove HTML tags if present
        resume_text = re.sub(r'<[^>]+>', ' ', resume_text)
        resume_text = re.sub(r'\s+', ' ', resume_text).strip()
        
        if not resume_text:
            return []
        
        # Common resume section headers
        section_patterns = {
            'experience': r'(?i)(EXPERIENCE|WORK\s+HISTORY|EMPLOYMENT|PROFESSIONAL\s+EXPERIENCE)',
            'skills': r'(?i)(SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|EXPERTISE)',
            'education': r'(?i)(EDUCATION|ACADEMIC|QUALIFICATIONS)',
            'projects': r'(?i)(PROJECTS|PORTFOLIO)',
            'summary': r'(?i)(SUMMARY|PROFILE|OBJECTIVE|ABOUT)'
        }
        
        # Try to detect sections
        section_matches = []
        for section_type, pattern in section_patterns.items():
            for match in re.finditer(pattern, resume_text):
                section_matches.append((match.start(), section_type))
        
        # If sections detected, split by sections
        if section_matches:
            section_matches.sort()  # Sort by position
            
            for i, (start_pos, section_type) in enumerate(section_matches):
                # Get end position (start of next section or end of text)
                end_pos = section_matches[i + 1][0] if i + 1 < len(section_matches) else len(resume_text)
                
                section_text = resume_text[start_pos:end_pos].strip()
                
                # Split large sections into smaller chunks
                if len(section_text) > max_chunk_size:
                    # Split by newlines, bullets, or dashes (job entries)
                    paragraphs = re.split(r'\n\n+|\n-\s+|\n•\s+|\n(?=\w+\s+\w+\s+at\s+)', section_text)
                    
                    current_chunk = ""
                    for para in paragraphs:
                        para = para.strip()
                        if not para:
                            continue
                        
                        # If single paragraph is too large, split by sentences
                        if len(para) > max_chunk_size:
                            sentences = re.split(r'(?<=[.!?])\s+', para)
                            for sent in sentences:
                                if len(current_chunk) + len(sent) + 1 <= max_chunk_size:
                                    current_chunk += " " + sent if current_chunk else sent
                                else:
                                    if current_chunk:
                                        chunks.append({
                                            'type': section_type,
                                            'content': current_chunk.strip()
                                        })
                                    current_chunk = sent
                        elif len(current_chunk) + len(para) + 1 <= max_chunk_size:
                            current_chunk += " " + para if current_chunk else para
                        else:
                            if current_chunk:
                                chunks.append({
                                    'type': section_type,
                                    'content': current_chunk.strip()
                                })
                            current_chunk = para
                    
                    if current_chunk:
                        chunks.append({
                            'type': section_type,
                            'content': current_chunk.strip()
                        })
                else:
                    chunks.append({
                        'type': section_type,
                        'content': section_text
                    })
        else:
            # No clear sections - fall back to paragraph chunking
            paragraphs = re.split(r'\n\n+', resume_text)
            
            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                if len(current_chunk) + len(para) <= max_chunk_size:
                    current_chunk += " " + para if current_chunk else para
                else:
                    if current_chunk:
                        chunks.append({
                            'type': 'general',
                            'content': current_chunk.strip()
                        })
                    current_chunk = para
            
            if current_chunk:
                chunks.append({
                    'type': 'general',
                    'content': current_chunk.strip()
                })
        
        logger.info(f"Chunked resume into {len(chunks)} segments")
        return chunks
    
    def embed_chunks(self, chunks: List[Dict[str, str]]) -> np.ndarray:
        """
        Generate embeddings for resume chunks.
        
        Args:
            chunks: List of chunks with 'content' field
            
        Returns:
            numpy array of shape (num_chunks, embedding_dim) with normalized embeddings
        """
        if not chunks:
            return np.array([]).reshape(0, self.embedding_dim)
        
        # Extract content
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings (automatically normalized by sentence-transformers)
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,  # L2 normalization
            show_progress_bar=False
        )
        
        logger.info(f"Generated embeddings for {len(chunks)} chunks with shape {embeddings.shape}")
        return embeddings
    
    def store_embeddings(
        self,
        session_id: str,
        chunks: List[Dict[str, str]],
        embeddings: np.ndarray
    ) -> None:
        """
        Store embeddings in Redis with session ID.
        
        Args:
            session_id: Unique session identifier
            chunks: List of chunks
            embeddings: numpy array of embeddings
        """
        key = f"rag:{session_id}"
        
        # Serialize data
        data = {
            'chunks': chunks,
            'embeddings': embeddings.tolist()  # Convert to list for JSON serialization
        }
        
        serialized = json.dumps(data)
        
        # Store with TTL
        self.redis_client.setex(key, self.ttl, serialized)
        
        logger.info(f"Stored {len(chunks)} chunks for session {session_id} with TTL {self.ttl}s")
    
    def query_resume(
        self,
        session_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Query resume using semantic search.
        
        Args:
            session_id: Session identifier
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of dicts with 'content', 'type', and 'score' fields, sorted by relevance
        """
        if not query or not query.strip():
            return []
        
        key = f"rag:{session_id}"
        
        # Retrieve stored data
        data = self.redis_client.get(key)
        if not data:
            logger.warning(f"No data found for session {session_id}")
            return []
        
        # Deserialize
        parsed = json.loads(data)
        chunks = parsed['chunks']
        stored_embeddings = np.array(parsed['embeddings'])
        
        # Generate query embedding
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, stored_embeddings)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'content': chunks[idx]['content'],
                'type': chunks[idx]['type'],
                'score': float(similarities[idx])
            })
        
        logger.info(f"Query '{query[:50]}...' returned {len(results)} results for session {session_id}")
        return results
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete stored embeddings for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        key = f"rag:{session_id}"
        result = self.redis_client.delete(key)
        
        logger.info(f"Deleted session {session_id}: {result > 0}")
        return result > 0
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about stored session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with num_chunks, embedding_dim, and ttl, or None if not found
        """
        key = f"rag:{session_id}"
        
        data = self.redis_client.get(key)
        if not data:
            return None
        
        parsed = json.loads(data)
        ttl = self.redis_client.ttl(key)
        
        return {
            'num_chunks': len(parsed['chunks']),
            'embedding_dim': len(parsed['embeddings'][0]) if parsed['embeddings'] else 0,
            'ttl': ttl
        }


# Singleton instance for import
_rag_instance: Optional[ResumeRAG] = None


def get_rag_instance() -> ResumeRAG:
    """
    Get or create singleton ResumeRAG instance.
    
    Returns:
        ResumeRAG instance
    """
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = ResumeRAG()
    return _rag_instance
