"""
OCR Module
Extracts text from images using OCR.space API (Free Cloud OCR)
No installation required!
"""
import requests
import base64
from PIL import Image
import io

# Free OCR.space API key (public demo key)
OCR_API_KEY = 'K87899142388957'
OCR_API_URL = 'https://api.ocr.space/parse/image'

# Supported languages for OCR (OCR.space free tier supported languages)
SUPPORTED_LANGUAGES = {
    'Auto Detect': 'eng',
    'English': 'eng',
    'Arabic': 'ara',
    'Bulgarian': 'bul',
    'Chinese (Simplified)': 'chs',
    'Chinese (Traditional)': 'cht',
    'Croatian': 'hrv',
    'Czech': 'cze',
    'Danish': 'dan',
    'Dutch': 'dut',
    'Finnish': 'fin',
    'French': 'fre',
    'German': 'ger',
    'Greek': 'gre',
    'Hungarian': 'hun',
    'Korean': 'kor',
    'Italian': 'ita',
    'Japanese': 'jpn',
    'Polish': 'pol',
    'Portuguese': 'por',
    'Russian': 'rus',
    'Slovenian': 'slv',
    'Spanish': 'spa',
    'Swedish': 'swe',
    'Turkish': 'tur'
}

def extract_text_from_image(uploaded_file, language='Auto Detect'):
    """
    Extract text from uploaded image file using OCR.space API
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        language: Language for OCR (default: Auto Detect)
    
    Returns:
        str: Extracted text or error message
    """
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read image bytes
        image_bytes = uploaded_file.read()
        
        # Get language code
        lang_code = SUPPORTED_LANGUAGES.get(language, 'eng')
        
        # Prepare the payload
        payload = {
            'apikey': OCR_API_KEY,
            'language': lang_code,
            'isOverlayRequired': False,
            'detectOrientation': True,
            'scale': True,
            'OCREngine': 2,  # Engine 2 is more accurate
        }
        
        # Prepare files
        files = {
            'file': (uploaded_file.name, image_bytes, 'image/png')
        }
        
        # Make API request
        response = requests.post(
            OCR_API_URL,
            files=files,
            data=payload,
            timeout=30
        )
        
        # Parse response
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
            return f"ERROR: {error_msg}"
        
        # Extract text from all parsed results
        parsed_results = result.get('ParsedResults', [])
        
        if not parsed_results:
            return ""
        
        # Combine text from all results
        extracted_text = ""
        for parsed in parsed_results:
            text = parsed.get('ParsedText', '')
            if text:
                extracted_text += text + "\n"
        
        return extracted_text.strip()
    
    except requests.exceptions.Timeout:
        return "ERROR: OCR request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"ERROR: Network error - {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"
