"""
PDF OCR Module - Extract Text from PDF Files
Handles both text-based PDFs and scanned PDFs
Uses PyPDF2 for text extraction and OCR for scanned pages
"""
import PyPDF2  # For reading PDF files
import io
from PIL import Image  # For image processing
import pdf2image  # For converting PDF pages to images
from ocr import extract_text_from_image  # Our OCR function

def extract_text_from_pdf(pdf_file, ocr_language="Auto Detect"):
    """
    Extract text from PDF file
    
    How it works:
    1. First tries direct text extraction (for text-based PDFs)
    2. If no text found, converts PDF to images
    3. Uses OCR on each page image
    4. Combines all text from all pages
    
    Args:
        pdf_file: Uploaded PDF file from Streamlit
        ocr_language (str): Language for OCR (default: Auto Detect)
    
    Returns:
        str: Extracted text from all pages OR error message
    """
    try:
        # Step 1: Reset file pointer to beginning
        pdf_file.seek(0)
        
        # Step 2: Try direct text extraction first (faster for text PDFs)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Loop through all pages
        for page in pdf_reader.pages:
            page_text = page.extract_text()  # Extract text from page
            if page_text:
                text += page_text + "\n"
        
        # Step 3: If text found, return it (text-based PDF)
        if text.strip():
            return text.strip()
        
        # Step 4: No text found - PDF is scanned images
        # Convert PDF pages to images and use OCR
        pdf_file.seek(0)
        images = pdf2image.convert_from_bytes(pdf_file.read())
        
        ocr_text = ""
        
        # Step 5: Process each page image with OCR
        for i, image in enumerate(images):
            # Convert PIL image to bytes for OCR
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            img_bytes.name = f'page_{i}.png'  # Give it a name
            
            # Extract text using OCR
            page_text = extract_text_from_image(img_bytes, ocr_language)
            
            # Add page text if successful
            if page_text and not page_text.startswith("ERROR:"):
                ocr_text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        # Step 6: Return combined text from all pages
        return ocr_text.strip() if ocr_text else "No text found in PDF"
    
    # Handle any errors
    except Exception as e:
        return f"ERROR: {str(e)}"
