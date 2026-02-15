"""
Script Analyzer Module
Analyzes code/scripts from images
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=get_api_key())

def analyze_script(code_text, analysis_type="Full Analysis"):
    """
    Analyze code/Receipt using OpenAI
    
    Args:
        code_text (str): Extracted code from image
        analysis_type (str): Type of analysis (Full Analysis, Bug Detection, Code Review, Explanation)
    
    Returns:
        dict: Contains success status, analysis, and token usage
    """
    try:
        # Define analysis prompts
        prompts = {
            "Full Analysis": """You are an expert code analyzer. Analyze this code and provide:
            1. Language Detection
            2. Code Purpose/Functionality
            3. Key Components
            4. Potential Issues/Bugs
            5. Best Practices Suggestions
            6. Security Concerns (if any)
            7. Performance Tips""",
            
            "Bug Detection": """You are a bug detection expert. Analyze this code and identify:
            1. Syntax errors
            2. Logic errors
            3. Potential runtime errors
            4. Edge cases not handled
            5. Suggested fixes""",
            
            "Code Review": """You are a senior code reviewer. Review this code for:
            1. Code quality
            2. Readability
            3. Maintainability
            4. Best practices
            5. Refactoring suggestions""",
            
            "Explanation": """You are a coding teacher. Explain this code in simple terms:
            1. What does this code do?
            2. How does it work? (step by step)
            3. What are the key concepts used?
            4. Example use cases"""
        }
        
        system_prompt = prompts.get(analysis_type, prompts["Full Analysis"])
        
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Analyze this code completely and thoroughly:\n\n{code_text}"
                }
            ],
            temperature=0.5,
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
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a programming language detector. Identify the programming language and respond with just the language name."
                },
                {
                    "role": "user",
                    "content": f"What programming language is this?\n\n{code_text[:500]}"
                }
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        return response.choices[0].message.content.strip()
    
    except:
        return "Unknown"
