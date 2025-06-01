"""
PDF Parser utility for extracting text from PDF resumes
"""
import io
from typing import Optional, Dict, Any
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from a PDF file using multiple methods with fallback
    
    Args:
        file_content: The binary content of the PDF file
        
    Returns:
        str: The extracted text from the PDF
    """
    # Try PyPDF2 first (faster but sometimes less accurate)
    try:
        text = _extract_with_pypdf2(file_content)
        if text and len(text.strip()) > 100:  # Ensure we got meaningful content
            return text
    except Exception as e:
        print(f"PyPDF2 extraction failed: {str(e)}")
    
    # Fallback to pdfminer (slower but more accurate)
    try:
        text = _extract_with_pdfminer(file_content)
        if text and len(text.strip()) > 100:
            return text
    except Exception as e:
        print(f"PDFMiner extraction failed: {str(e)}")
    
    # Last attempt with pdfminer's high-level API
    try:
        text = pdfminer_extract_text(io.BytesIO(file_content))
        return text
    except Exception as e:
        print(f"PDFMiner high-level extraction failed: {str(e)}")
        
    # If all methods fail, return an empty string
    return ""

def _extract_with_pypdf2(file_content: bytes) -> str:
    """Extract text using PyPDF2"""
    text = ""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() + "\n"
    return text

def _extract_with_pdfminer(file_content: bytes) -> str:
    """Extract text using PDFMiner's lower-level API for more control"""
    resource_manager = PDFResourceManager()
    output_string = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    converter = TextConverter(resource_manager, output_string, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(resource_manager, converter)
    
    pdf_file = io.BytesIO(file_content)
    for page in PDFPage.get_pages(pdf_file, check_extractable=True):
        interpreter.process_page(page)
    
    text = output_string.getvalue()
    converter.close()
    output_string.close()
    
    return text

def parse_resume_pdf(file_content: bytes) -> Dict[str, Any]:
    """
    Parse a resume PDF and return structured information
    
    Args:
        file_content: The binary content of the PDF file
        
    Returns:
        Dict: A dictionary containing the parsed resume information
    """
    text = extract_text_from_pdf(file_content)
    
    # For now, just return the raw text
    # In a more advanced implementation, we could extract structured data
    return {
        "text": text,
        "format": "pdf"
    }
