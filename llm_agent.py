"""
LLM Agent Module - AI Summarization
Uses OpenAI GPT-3.5-turbo to create summaries
Works on both local (.env) and Streamlit Cloud (secrets)
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file (for local development)
load_dotenv()

# Get API key from environment or Streamlit secrets
def get_api_key():
    """
    Get OpenAI API key from two possible sources:
    1. Streamlit secrets (for cloud deployment)
    2. Environment variable (for local development)
    
    Returns:
        str: OpenAI API key
    """
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        # Fall back to environment variable (for local)
        return os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client with API key
client = OpenAI(api_key=get_api_key())

def get_summary_instructions(length):
    """
    Get summary instructions based on user's length preference
    
    Args:
        length (str): Short, Medium, or Detailed
    
    Returns:
        str: Instructions for AI on how to summarize
    """
    instructions = {
        # Short: Just the main points in 2-3 sentences
        "Short": "Provide a brief 2-3 sentence summary of the key points only.",
        
        # Medium: More details in 1-2 paragraphs
        "Medium": "Provide a comprehensive summary in 1-2 paragraphs covering main ideas and important details.",
        
        # Detailed: Everything! Don't skip anything
        "Detailed": "Provide a complete and detailed summary with ALL information from the text. Include every item, number, date, name, and detail. Don't skip anything. Organize in clear sections."
    }
    return instructions.get(length, instructions["Medium"])

def summarize_text(text, summary_length="Medium", output_language="English"):
    """
    Summarize text using OpenAI GPT-3.5-turbo AI
    
    How it works:
    1. Takes extracted text from OCR
    2. Sends it to OpenAI with instructions
    3. Gets back AI-generated summary
    4. Returns summary in requested language
    
    Args:
        text (str): Text to summarize (from OCR)
        summary_length (str): Short, Medium, or Detailed
        output_language (str): Language for the summary (English, Urdu, etc.)
    
    Returns:
        dict: Contains:
            - success: True/False
            - summary: The AI-generated summary
            - tokens: Number of tokens used (for billing)
            - message: Error message if failed
    """
    try:
        # Step 1: Get instructions based on summary length
        length_instruction = get_summary_instructions(summary_length)
        
        # Step 2: Create chat completion with OpenAI
        # This is like having a conversation with AI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 (faster and cheaper than GPT-4)
            messages=[
                {
                    # System message: Tell AI what its role is
                    "role": "system",
                    "content": f"""You are an expert AI summarizer. Your task is to analyze 
                    and summarize text extracted from images using OCR. {length_instruction}
                    Focus on clarity, accuracy, and key information.
                    IMPORTANT: 
                    - Provide the summary in {output_language} language.
                    - Include ALL important information from the text.
                    - Don't skip any details, items, or numbers.
                    - For receipts/invoices: include all items, prices, totals, dates, and store info.
                    - Organize information clearly and completely."""
                },
                {
                    # User message: The actual text to summarize
                    "role": "user",
                    "content": f"Please summarize the following text in {output_language}. Make sure to include ALL details:\n\n{text}"
                }
            ],
            temperature=0.3,  # Lower = more focused and accurate (0-1 range)
            max_tokens=800  # Maximum length of response (increased for complete summaries)
        )
        
        # Step 3: Extract the summary from AI response
        summary = response.choices[0].message.content
        
        # Step 4: Get token usage (for tracking costs)
        tokens_used = response.usage.total_tokens
        
        # Step 5: Return success with summary and token count
        return {
            'success': True,
            'summary': summary,
            'tokens': tokens_used
        }
    
    # Handle any errors (API errors, network issues, etc.)
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'summary': '',
            'tokens': 0
        }
