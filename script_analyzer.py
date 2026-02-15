"""
Script Analyzer Module - Code Analysis with AI
Analyzes code/scripts from images
Detects programming language and provides detailed analysis
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def get_api_key():
    """
    Get OpenAI API key from Streamlit secrets or environment
    Works on both local and cloud deployment
    """
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=get_api_key())

def analyze_script(code_text, analysis_type="Full Analysis"):
    """
    Analyze code/script using OpenAI AI
    
    How it works:
    1. Takes extracted code from image
    2. Sends to OpenAI with specific analysis instructions
    3. Gets back detailed code analysis
    4. Returns analysis with token usage
    
    Args:
        code_text (str): Extracted code from image (via OCR)
        analysis_type (str): Type of analysis to perform:
            - Full Analysis: Complete review with best practices
            - Bug Detection: Find errors and issues
            - Code Review: Quality and maintainability check
            - Explanation: Step-by-step breakdown
    
    Returns:
        dict: Contains:
            - success: True/False
            - analysis: The AI-generated code analysis
            - tokens: Number of tokens used
            - message: Error message if failed
    """
    try:
        # Define different analysis prompts for each type
        prompts = {
            # Full Analysis: Everything about the code
            "Full Analysis": """You are an expert code analyzer. Analyze this code and provide:
            1. Language Detection - What programming language is this?
            2. Code Purpose/Functionality - What does this code do?
            3. Key Components - Main functions, classes, variables
            4. Potential Issues/Bugs - Any problems you see?
            5. Best Practices Suggestions - How to improve?
            6. Security Concerns (if any) - Any security risks?
            7. Performance Tips - How to make it faster?""",
            
            # Bug Detection: Focus on finding errors
            "Bug Detection": """You are a bug detection expert. Analyze this code and identify:
            1. Syntax errors - Wrong code structure
            2. Logic errors - Wrong logic/algorithm
            3. Potential runtime errors - Errors that happen when code runs
            4. Edge cases not handled - Special situations not covered
            5. Suggested fixes - How to fix each issue""",
            
            # Code Review: Focus on quality
            "Code Review": """You are a senior code reviewer. Review this code for:
            1. Code quality - Is it well-written?
            2. Readability - Is it easy to understand?
            3. Maintainability - Is it easy to update later?
            4. Best practices - Does it follow standards?
            5. Refactoring suggestions - How to make it better?""",
            
            # Explanation: Teach the code
            "Explanation": """You are a coding teacher. Explain this code in simple terms:
            1. What does this code do? - Overall purpose
            2. How does it work? (step by step) - Line by line explanation
            3. What are the key concepts used? - Important programming concepts
            4. Example use cases - When would you use this code?"""
        }
        
        # Get the appropriate prompt for selected analysis type
        system_prompt = prompts.get(analysis_type, prompts["Full Analysis"])
        
        # Create chat completion with OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5
            messages=[
                {
                    # System: Tell AI what to do
                    "role": "system",
                    "content": system_prompt
                },
                {
                    # User: Provide the code to analyze
                    "role": "user",
                    "content": f"Analyze this code completely and thoroughly:\n\n{code_text}"
                }
            ],
            temperature=0.5,  # Balanced between creative and focused
            max_tokens=1500  # Increased for complete analysis
        )
        
        # Extract analysis and token usage
        analysis = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return {
            'success': True,
            'analysis': analysis,
            'tokens': tokens_used
        }
    
    # Handle any errors
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'analysis': '',
            'tokens': 0
        }

def detect_language(code_text):
    """
    Detect programming language from code
    
    How it works:
    1. Takes code snippet
    2. Asks AI to identify the language
    3. Returns language name
    
    Args:
        code_text (str): Code to analyze
    
    Returns:
        str: Programming language name (e.g., "Python", "JavaScript")
    """
    try:
        # Ask AI to detect language (short and simple)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a programming language detector. Identify the programming language and respond with just the language name."
                },
                {
                    "role": "user",
                    "content": f"What programming language is this?\n\n{code_text[:500]}"  # Only send first 500 chars
                }
            ],
            temperature=0.3,  # Low temperature for accurate detection
            max_tokens=50  # Short response needed
        )
        
        return response.choices[0].message.content.strip()
    
    # If detection fails, return Unknown
    except:
        return "Unknown"

def analyze_receipt_categories(receipt_text):
    """
    Analyze receipt and categorize items
    
    How it works:
    1. Takes extracted receipt text
    2. Asks AI to identify item categories
    3. Returns categorized items
    
    Categories detected:
    - Vegetables
    - Fruits
    - Dairy Products
    - Meat & Poultry
    - Bakery
    - Beverages
    - Snacks
    - Cosmetics
    - Personal Care
    - Household Items
    - Electronics
    - Clothing
    - Others
    
    Args:
        receipt_text (str): Extracted text from receipt
    
    Returns:
        dict: Contains:
            - success: True/False
            - categories: Dictionary of categories with items
            - total_categories: Number of categories found
            - message: Error message if failed
    """
    try:
        # Ask AI to categorize receipt items
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a receipt analyzer expert. Analyze the receipt and categorize all items.
                    
                    Categories to use:
                    - Vegetables
                    - Fruits
                    - Dairy Products
                    - Meat & Poultry
                    - Bakery
                    - Beverages
                    - Snacks
                    - Cosmetics
                    - Personal Care
                    - Household Items
                    - Electronics
                    - Clothing
                    - Others
                    
                    For each category found, list the items with their prices.
                    Format your response clearly with category names as headers."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this receipt and categorize all items:\n\n{receipt_text}"
                }
            ],
            temperature=0.3,  # Low temperature for accurate categorization
            max_tokens=1000  # Enough for detailed categorization
        )
        
        # Extract categorization
        categorization = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return {
            'success': True,
            'categorization': categorization,
            'tokens': tokens_used
        }
    
    # Handle any errors
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'categorization': '',
            'tokens': 0
        }
