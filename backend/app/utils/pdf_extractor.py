"""
PDF Extraction Utility
Extract text from uploaded CV PDF files (including image-based PDFs with OCR)
"""
import pdfplumber
import io
from typing import Optional
import os

# Try importing OCR libraries
try:
    from pdf2image import convert_from_bytes
    import pytesseract
    from PIL import Image
    
    # Set Tesseract path if on Windows
    if os.name == 'nt':
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    OCR_AVAILABLE = True
    print("OCR libraries loaded successfully")
except ImportError as e:
    OCR_AVAILABLE = False
    print(f"OCR not available: {e}")
except Exception as e:
    OCR_AVAILABLE = False
    print(f"OCR setup failed: {e}")

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text from PDF file bytes
    Handles PDFs with images and styling by trying multiple extraction methods
    If text extraction fails, uses OCR to extract text from images
    
    Args:
        pdf_file: PDF file content as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        text_content = []
        
        # Open PDF from bytes
        with pdfplumber.open(io.BytesIO(pdf_file)) as pdf:
            # Extract text from each page
            for page in pdf.pages:
                # Try standard extraction first
                page_text = page.extract_text()
                
                # If no text, try with layout preservation
                if not page_text or len(page_text.strip()) < 10:
                    page_text = page.extract_text(layout=True)
                
                # If still no text, try extracting from tables
                if not page_text or len(page_text.strip()) < 10:
                    tables = page.extract_tables()
                    if tables:
                        table_text = "\n".join([" ".join([str(cell) for cell in row if cell]) for table in tables for row in table])
                        page_text = table_text
                
                if page_text and page_text.strip():
                    text_content.append(page_text.strip())
        
        # Join all pages
        full_text = "\n\n".join(text_content)
        
        # Clean up text - remove excessive whitespace but preserve structure
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        full_text = "\n".join(lines)
        
        # If we got enough text, return it
        if full_text and len(full_text.strip()) >= 50:
            return full_text
        
        # If text extraction failed, try OCR only if available
        if len(full_text.strip()) < 50:
            print(f"Only extracted {len(full_text)} characters")
            
            if OCR_AVAILABLE:
                print("Attempting OCR extraction...")
                try:
                    ocr_text = extract_text_with_ocr(pdf_file)
                    if ocr_text and len(ocr_text.strip()) >= 50:
                        return ocr_text
                except Exception as ocr_error:
                    print(f"OCR failed: {ocr_error}")
                    # Continue to error message below
            else:
                print("OCR not available (missing Tesseract/Poppler)")
        
        # If we reach here, extraction failed
        raise ValueError(
            f"Could not extract sufficient text from PDF (only {len(full_text)} characters). "
            "This PDF may be image-based or scanned. "
            "Please use a text-based PDF (created from Word/Google Docs, not scanned)."
        )
    
    except ValueError as ve:
        raise ve
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_with_ocr(pdf_file: bytes) -> str:
    """
    Extract text from PDF using OCR (for image-based PDFs)
    
    Args:
        pdf_file: PDF file content as bytes
        
    Returns:
        Extracted text from images
    """
    if not OCR_AVAILABLE:
        raise Exception("OCR libraries not available. Text extraction only supports text-based PDFs currently.")
    
    try:
        print("Using OCR to extract text from images...")
        
        # Convert PDF pages to images
        # Note: Requires poppler installed and in PATH
        images = convert_from_bytes(pdf_file, dpi=200, fmt='jpeg')
        
        text_content = []
        for i, image in enumerate(images):
            print(f"  Processing page {i+1}/{len(images)} with OCR...")
            # Extract text from image using Tesseract
            page_text = pytesseract.image_to_string(image, lang='eng')
            if page_text and page_text.strip():
                text_content.append(page_text.strip())
        
        # Join all pages
        full_text = "\n\n".join(text_content)
        
        # Clean up text
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        full_text = "\n".join(lines)
        
        print(f"OCR extracted {len(full_text)} characters")
        return full_text
    
    except FileNotFoundError as e:
        raise Exception(
            "Poppler not found. For OCR support, install poppler: "
            "Download from https://github.com/oschwartz10612/poppler-windows/releases "
            "and add to PATH, or use a text-based PDF."
        )
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}. Try using a text-based PDF instead.")


def validate_pdf_file(filename: str, file_size: int, max_size_mb: int = 5) -> tuple[bool, Optional[str]]:
    """
    Validate uploaded PDF file
    
    Args:
        filename: Name of uploaded file
        file_size: Size of file in bytes
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        (is_valid, error_message)
    """
    # Check file extension
    if not filename.lower().endswith('.pdf'):
        return False, "Only PDF files are allowed"
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Check minimum size (empty file)
    if file_size < 100:
        return False, "File is too small or empty"
    
    return True, None
