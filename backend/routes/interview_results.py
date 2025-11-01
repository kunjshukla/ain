"""
Interview Results API Route

Provides endpoints for retrieving interview results, scores, and feedback.
Handles result caching, aggregation, and concurrent access.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis
import json
import logging
from collections import Counter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["interviews"])

# Redis client for caching
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=5)
    redis_client.ping()
    logger.info("Redis connected for results caching")
except Exception as e:
    logger.warning(f"Redis not available, caching disabled: {e}")
    redis_client = None


class EvaluationSummary(BaseModel):
    """Summary of interview evaluation"""
    strengths: List[str]
    improvements: List[str]


class InterviewResults(BaseModel):
    """Interview results response model"""
    session_id: str
    overall_score: float
    evaluation: EvaluationSummary
    question_count: int
    duration_minutes: float
    job_role: Optional[str] = None
    status: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    fallback: bool = False


def calculate_duration_minutes(started_at: str, ended_at: Optional[str] = None) -> float:
    """Calculate interview duration in minutes"""
    try:
        start = datetime.fromisoformat(started_at)
        if ended_at:
            end = datetime.fromisoformat(ended_at)
        else:
            end = datetime.utcnow()
        
        duration = (end - start).total_seconds() / 60
        return round(duration, 1)
    except Exception as e:
        logger.error(f"Error calculating duration: {e}")
        return 0.0


def aggregate_feedback(evaluations: List[Dict[str, Any]], top_k: int = 5) -> Dict[str, List[str]]:
    """
    Aggregate and deduplicate feedback from multiple evaluations.
    Prioritizes most frequent feedback items.
    """
    strength_counter = Counter()
    improvement_counter = Counter()
    
    for eval in evaluations:
        for strength in eval.get("strengths", []):
            strength_counter[strength] += 1
        for improvement in eval.get("improvements", []):
            improvement_counter[improvement] += 1
    
    # Get top_k most common items, maintaining order by frequency
    top_strengths = [item for item, count in strength_counter.most_common(top_k)]
    top_improvements = [item for item, count in improvement_counter.most_common(top_k)]
    
    return {
        "strengths": top_strengths,
        "improvements": top_improvements
    }


def calculate_overall_score(evaluations: List[Dict[str, Any]]) -> float:
    """Calculate average score from all evaluations"""
    if not evaluations:
        return 0.0
    
    scores = [eval.get("score", 0.0) for eval in evaluations if "score" in eval]
    if not scores:
        return 0.0
    
    avg_score = sum(scores) / len(scores)
    return round(avg_score, 1)


@router.get("/{session_id}/results", response_model=InterviewResults)
async def get_interview_results(
    session_id: str,
    bypass_cache: bool = Query(False, description="Bypass cache and fetch fresh data")
):
    """
    Retrieve interview results for a given session.
    
    Args:
        session_id: Unique interview session identifier
        bypass_cache: If True, bypasses cache and recalculates results
        
    Returns:
        InterviewResults: Comprehensive interview results including scores and feedback
    """
    logger.info(f"Fetching results for session: {session_id}")
    
    # Check cache first (unless bypassed)
    cache_key = f"results:{session_id}"
    
    if redis_client and not bypass_cache:
        try:
            cached_results = redis_client.get(cache_key)
            if cached_results:
                logger.info(f"Returning cached results for {session_id}")
                return InterviewResults(**json.loads(cached_results))
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
    
    # Fetch interview data from Redis
    interview_key = f"interview:{session_id}"
    
    try:
        if redis_client:
            interview_data_raw = redis_client.get(interview_key)
            if not interview_data_raw:
                # Session not found - return fallback data
                logger.warning(f"Session {session_id} not found, returning fallback data")
                return create_fallback_results(session_id)
            
            interview_data = json.loads(interview_data_raw)
        else:
            # No Redis - return fallback
            logger.warning("Redis unavailable, returning fallback data")
            return create_fallback_results(session_id)
        
    except Exception as e:
        logger.error(f"Error fetching interview data: {e}")
        return create_fallback_results(session_id)
    
    # Extract data
    evaluations = interview_data.get("evaluations", [])
    started_at = interview_data.get("started_at")
    ended_at = interview_data.get("ended_at")
    job_role = interview_data.get("job_role")
    status = interview_data.get("status", "completed")
    
    # Calculate metrics
    overall_score = calculate_overall_score(evaluations)
    aggregated_feedback = aggregate_feedback(evaluations)
    question_count = len(evaluations)
    duration_minutes = calculate_duration_minutes(started_at, ended_at) if started_at else 0.0
    
    # Build results
    results = InterviewResults(
        session_id=session_id,
        overall_score=overall_score,
        evaluation=EvaluationSummary(
            strengths=aggregated_feedback["strengths"],
            improvements=aggregated_feedback["improvements"]
        ),
        question_count=question_count,
        duration_minutes=duration_minutes,
        job_role=job_role,
        status=status,
        started_at=started_at,
        ended_at=ended_at,
        fallback=False
    )
    
    # Cache results
    if redis_client:
        try:
            redis_client.setex(
                cache_key,
                300,  # Cache for 5 minutes
                json.dumps(results.dict())
            )
            logger.info(f"Cached results for {session_id}")
        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")
    
    return results


def create_fallback_results(session_id: str) -> InterviewResults:
    """Create fallback results when session data is unavailable"""
    return InterviewResults(
        session_id=session_id,
        overall_score=7.0,
        evaluation=EvaluationSummary(
            strengths=["Completed the interview", "Showed up prepared"],
            improvements=["Continue practicing interview skills", "Review common interview questions"]
        ),
        question_count=0,
        duration_minutes=0.0,
        job_role=None,
        status="not_found",
        started_at=None,
        ended_at=None,
        fallback=True
    )


@router.delete("/{session_id}/results/cache")
async def invalidate_results_cache(session_id: str):
    """
    Invalidate cached results for a session.
    Useful when interview continues or data is updated.
    """
    if not redis_client:
        raise HTTPException(status_code=503, detail="Cache not available")
    
    cache_key = f"results:{session_id}"
    
    try:
        deleted = redis_client.delete(cache_key)
        return {
            "session_id": session_id,
            "cache_invalidated": deleted > 0,
            "message": "Cache invalidated successfully" if deleted > 0 else "No cache found"
        }
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invalidate cache: {str(e)}")


@router.get("/{session_id}/results/summary")
async def get_results_summary(session_id: str):
    """
    Get a quick summary of interview results without full details.
    Useful for dashboards and listings.
    """
    results = await get_interview_results(session_id)
    
    return {
        "session_id": results.session_id,
        "overall_score": results.overall_score,
        "question_count": results.question_count,
        "duration_minutes": results.duration_minutes,
        "status": results.status
    }
