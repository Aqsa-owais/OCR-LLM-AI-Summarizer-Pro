"""
LLM Agent Module
Summarizes text using OpenAI API
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Get API key from environment or Streamlit secrets
def get_api_key():
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        # Fall back to environment variable (for local)
        return os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=get_api_key())

def get_summary_instructions(length):
    """
    Get summary instructions based on length preference
    """
    instructions = {
        "Short": "Provide a brief 2-3 sentence summary of the key points.",
        "Medium": "Provide a comprehensive summary in 1-2 paragraphs covering main ideas.",
        "Detailed": "Provide a detailed summary with all important points, organized in clear sections."
    }
    return instructions.get(length, instructions["Medium"])

def summarize_text(text, summary_length="Medium", output_language="English"):
    """
    Summarize text using OpenAI agent
    
    Args:
        text (str): Text to summarize
        summary_length (str): Length preference (Short, Medium, Detailed)
        output_language (str): Language for the summary output
    
    Returns:
        dict: Contains success status, summary, and token usage
    """
    try:
        # Get summary instructions
        length_instruction = get_summary_instructions(summary_length)
        
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an expert AI summarizer. Your task is to analyze 
                    and summarize text extracted from images using OCR. {length_instruction}
                    Focus on clarity, accuracy, and key information.
                    IMPORTANT: Provide the summary in {output_language} language."""
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following text in {output_language}:\n\n{text}"
                }
            ],
            temperature=0.6,
            max_tokens=500
        )
        
        # Extract summary and token usage
        summary = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return {
            'success': True,
            'summary': summary,
            'tokens': tokens_used
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'summary': '',
            'tokens': 0
        }
