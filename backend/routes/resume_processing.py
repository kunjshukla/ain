# routes/resume_processing.py - Enhanced resume processing routes
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.resume_parser import ResumeParser, resume_parser
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resume", tags=["Resume Processing"])

@router.post("/upload")
async def upload_and_parse_resume(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload and parse a resume PDF file
    
    Args:
        file: PDF file upload
        
    Returns:
        Parsed resume data with structured information
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Parse the resume using enhanced parser
        result = resume_parser.parse_resume(file_content)
        
        if not result['success']:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to parse resume: {result.get('error', 'Unknown error')}"
            )
        
        # Return structured response
        return {
            "filename": file.filename,
            "size_bytes": len(file_content),
            "parsing_success": True,
            "text_content": result['text'],
            "metadata": result['metadata'],
            "structured_data": result['structured_data'],
            "message": "Resume parsed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during resume processing"
        )

@router.post("/validate")
async def validate_resume_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Validate a PDF resume file without full parsing
    
    Args:
        file: PDF file upload
        
    Returns:
        Validation results and diagnostic information
    """
    try:
        file_content = await file.read()
        
        # Validate using enhanced parser
        validation = resume_parser.validate_pdf(file_content)
        
        return {
            "filename": file.filename,
            "size_bytes": len(file_content),
            "validation": validation,
            "recommendations": _get_validation_recommendations(validation)
        }
        
    except Exception as e:
        logger.error(f"Resume validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during validation"
        )

@router.post("/extract-text")
async def extract_text_only(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract raw text from resume PDF without structure analysis
    
    Args:
        file: PDF file upload
        
    Returns:
        Raw extracted text
    """
    try:
        file_content = await file.read()
        
        # Extract text using enhanced parser
        text = resume_parser.extract_text_from_pdf(file_content)
        
        if not text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from PDF"
            )
        
        return {
            "filename": file.filename,
            "extracted_text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.split('\n'))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text extraction error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during text extraction"
        )

@router.get("/health")
async def resume_service_health():
    """Health check for resume processing service"""
    try:
        # Test the parser
        test_parser = ResumeParser()
        
        return {
            "service": "Resume Processing",
            "status": "healthy",
            "parser_available": True,
            "supported_formats": test_parser.supported_formats,
            "features": {
                "multiple_extraction_methods": True,
                "text_cleaning": True,
                "structure_extraction": True,
                "pdf_validation": True,
                "error_handling": True
            }
        }
        
    except Exception as e:
        return {
            "service": "Resume Processing", 
            "status": "unhealthy",
            "error": str(e),
            "parser_available": False
        }

def _get_validation_recommendations(validation: Dict[str, Any]) -> list:
    """Generate recommendations based on validation results"""
    recommendations = []
    
    if not validation['valid']:
        recommendations.append("PDF file appears to be corrupted or invalid")
        
    if validation.get('encrypted', False):
        recommendations.append("PDF is password protected - consider removing encryption")
        
    if validation.get('page_count', 0) == 0:
        recommendations.append("PDF has no pages")
    elif validation.get('page_count', 0) > 3:
        recommendations.append("Resume is quite long - consider condensing to 1-2 pages")
        
    if not validation.get('can_extract', False):
        recommendations.append("Text extraction may be difficult - ensure PDF contains selectable text")
    
    if not recommendations:
        recommendations.append("PDF appears to be in good format for processing")
        
    return recommendations
