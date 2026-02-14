"""
PDF OCR Module
Extract text from PDF files
"""
import PyPDF2
import io
from PIL import Image
import pdf2image
from ocr import extract_text_from_image

def extract_text_from_pdf(pdf_file, ocr_language="Auto Detect"):
    """
    Extract text from PDF file
    
    Args:
        pdf_file: Uploaded PDF file
        ocr_language: Language for OCR
    
    Returns:
        str: Extracted text
    """
    try:
        # Reset file pointer
        pdf_file.seek(0)
        
        # Try direct text extraction first
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # If text found, return it
        if text.strip():
            return text.strip()
        
        # If no text, use OCR on images
        pdf_file.seek(0)
        images = pdf2image.convert_from_bytes(pdf_file.read())
        
        ocr_text = ""
        for i, image in enumerate(images):
            # Convert PIL image to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            img_bytes.name = f'page_{i}.png'
            
            # Extract text using OCR
            page_text = extract_text_from_image(img_bytes, ocr_language)
            if page_text and not page_text.startswith("ERROR:"):
                ocr_text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        return ocr_text.strip() if ocr_text else "No text found in PDF"
    
    except Exception as e:
        return f"ERROR: {str(e)}"
