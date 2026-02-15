"""
OCR Module - Extracts text from images
Uses OCR.space API (Free Cloud OCR Service)
No installation required - works via internet
"""
import requests
import base64
from PIL import Image
import io

# Free OCR.space API key (public demo key - works for everyone)
OCR_API_KEY = 'K87899142388957'
OCR_API_URL = 'https://api.ocr.space/parse/image'

# Supported languages for OCR (OCR.space free tier supported languages)
# You can add more languages if needed
SUPPORTED_LANGUAGES = {
    'Auto Detect': 'eng',  # Automatically detects language
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
    
    How it works:
    1. Takes the uploaded image file
    2. Sends it to OCR.space cloud service
    3. Gets back the extracted text
    4. Returns the text to display
    
    Args:
        uploaded_file: Image file uploaded by user (from Streamlit)
        language: Language for OCR (default: Auto Detect)
    
    Returns:
        str: Extracted text from image OR error message if something goes wrong
    """
    try:
        # Step 1: Reset file pointer to beginning (important for reading file)
        uploaded_file.seek(0)
        
        # Step 2: Read image as bytes (raw data)
        image_bytes = uploaded_file.read()
        
        # Step 3: Get language code from our supported languages dictionary
        lang_code = SUPPORTED_LANGUAGES.get(language, 'eng')
        
        # Step 4: Prepare the settings for OCR API
        payload = {
            'apikey': OCR_API_KEY,  # Our API key
            'language': lang_code,  # Which language to detect
            'isOverlayRequired': False,  # We don't need overlay
            'detectOrientation': True,  # Auto-rotate image if needed
            'scale': True,  # Scale image for better accuracy
            'OCREngine': 2,  # Engine 2 is more accurate than Engine 1
            'isTable': True,  # Better for receipts and structured text
            'detectCheckbox': False,  # We don't need checkbox detection
        }
        
        # Step 5: Prepare the image file for upload
        files = {
            'file': (uploaded_file.name, image_bytes, 'image/png')
        }
        
        # Step 6: Send request to OCR.space API (wait max 30 seconds)
        response = requests.post(
            OCR_API_URL,
            files=files,
            data=payload,
            timeout=30
        )
        
        # Step 7: Parse the JSON response from API
        result = response.json()
        
        # Step 8: Check if there was an error during processing
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
            return f"ERROR: {error_msg}"
        
        # Step 9: Extract text from all parsed results
        parsed_results = result.get('ParsedResults', [])
        
        # Step 10: If no results found, return empty string
        if not parsed_results:
            return ""
        
        # Step 11: Combine text from all results (in case of multiple pages)
        extracted_text = ""
        for parsed in parsed_results:
            text = parsed.get('ParsedText', '')
            if text:
                extracted_text += text + "\n"
        
        # Step 12: Return the final extracted text (remove extra spaces)
        return extracted_text.strip()
    
    # Handle timeout errors (if API takes too long)
    except requests.exceptions.Timeout:
        return "ERROR: OCR request timed out. Please try again."
    
    # Handle network errors (no internet, API down, etc.)
    except requests.exceptions.RequestException as e:
        return f"ERROR: Network error - {str(e)}"
    
    # Handle any other unexpected errors
    except Exception as e:
        return f"ERROR: {str(e)}"
