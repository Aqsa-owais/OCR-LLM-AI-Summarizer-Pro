"""
Advanced Receipt Analyzer Module
Complete receipt processing with financial analysis and AI advice
"""
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st
import re
import json

load_dotenv()

def get_api_key():
    """Get OpenAI API key"""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=get_api_key())

def parse_receipt_to_structured_data(receipt_text):
    """
    Parse OCR text into structured format
    
    Extracts:
    - Store name
    - Date
    - Items with prices and quantities
    - Subtotal, tax, total
    
    Args:
        receipt_text (str): Raw OCR text
    
    Returns:
        dict: Structured receipt data
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a receipt parser. Extract structured data from receipt text.
                    
                    Return ONLY valid JSON in this exact format:
                    {
                        "store_name": "Store Name",
                        "date": "YYYY-MM-DD",
                        "items": [
                            {"name": "Item Name", "quantity": 1, "price": 10.50, "category": "Category"}
                        ],
                        "subtotal": 100.00,
                        "tax": 10.00,
                        "total": 110.00
                    }
                    
                    Categories: Vegetables, Fruits, Dairy, Meat, Bakery, Beverages, Snacks, Cosmetics, Personal Care, Household, Electronics, Clothing, Others
                    
                    If data is missing, use null or 0."""
                },
                {
                    "role": "user",
                    "content": f"Parse this receipt into JSON:\n\n{receipt_text}"
                }
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        # Extract JSON from response
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
        
        # Parse JSON
        structured_data = json.loads(json_text)
        
        return {
            'success': True,
            'data': structured_data,
            'tokens': response.usage.total_tokens
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'data': None,
            'tokens': 0
        }

def analyze_spending(structured_data):
    """
    Analyze spending by category
    
    Calculates:
    - Total per category
    - Percentage of total spending
    - Identifies overspending areas
    
    Args:
        structured_data (dict): Parsed receipt data
    
    Returns:
        dict: Spending analysis
    """
    try:
        items = structured_data.get('items', [])
        total = structured_data.get('total', 0)
        
        if not items or total == 0:
            return {
                'success': False,
                'message': 'No items or total found'
            }
        
        # Calculate category totals
        category_totals = {}
        for item in items:
            category = item.get('category', 'Others')
            price = item.get('price', 0)
            quantity = item.get('quantity', 1)
            item_total = price * quantity
            
            if category in category_totals:
                category_totals[category] += item_total
            else:
                category_totals[category] = item_total
        
        # Calculate percentages
        category_analysis = []
        for category, amount in category_totals.items():
            percentage = (amount / total) * 100
            category_analysis.append({
                'category': category,
                'amount': amount,
                'percentage': percentage
            })
        
        # Sort by amount (highest first)
        category_analysis.sort(key=lambda x: x['amount'], reverse=True)
        
        return {
            'success': True,
            'category_totals': category_totals,
            'category_analysis': category_analysis,
            'total_items': len(items),
            'total_amount': total
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }

def generate_financial_advice(structured_data, spending_analysis):
    """
    Generate AI-powered financial advice using LLM
    
    Provides:
    - Spending insights
    - Budget recommendations
    - Money-saving tips
    - Overspending alerts
    
    Args:
        structured_data (dict): Parsed receipt data
        spending_analysis (dict): Category spending analysis
    
    Returns:
        dict: Financial advice and recommendations
    """
    try:
        # Prepare data for LLM
        items = structured_data.get('items', [])
        total = structured_data.get('total', 0)
        category_analysis = spending_analysis.get('category_analysis', [])
        
        # Create summary for LLM
        summary = f"Total Spending: ${total:.2f}\n\n"
        summary += "Category Breakdown:\n"
        for cat in category_analysis:
            summary += f"- {cat['category']}: ${cat['amount']:.2f} ({cat['percentage']:.1f}%)\n"
        
        summary += f"\nTotal Items: {len(items)}"
        
        # Get AI advice
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a personal finance advisor. Analyze spending patterns and provide:
                    
                    1. SPENDING INSIGHTS
                       - What categories dominate spending?
                       - Any unusual patterns?
                    
                    2. BUDGET RECOMMENDATIONS
                       - Suggested budget allocation
                       - Areas to reduce spending
                    
                    3. MONEY-SAVING TIPS
                       - Practical tips for each category
                       - Alternative shopping strategies
                    
                    4. OVERSPENDING ALERTS
                       - Categories with high spending
                       - Warning signs
                    
                    Be specific, actionable, and friendly. Use emojis for better readability."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this spending and provide financial advice:\n\n{summary}"
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        advice = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return {
            'success': True,
            'advice': advice,
            'tokens': tokens_used
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e),
            'advice': '',
            'tokens': 0
        }

def detect_anomalies(spending_analysis):
    """
    Detect spending anomalies and overspending
    
    Identifies:
    - Categories with >30% of total spending
    - Unusual spending patterns
    
    Args:
        spending_analysis (dict): Category spending analysis
    
    Returns:
        list: List of anomalies/warnings
    """
    anomalies = []
    category_analysis = spending_analysis.get('category_analysis', [])
    
    for cat in category_analysis:
        # Flag if category is >30% of total
        if cat['percentage'] > 30:
            anomalies.append({
                'type': 'high_spending',
                'category': cat['category'],
                'percentage': cat['percentage'],
                'message': f"⚠️ {cat['category']} accounts for {cat['percentage']:.1f}% of total spending"
            })
    
    return anomalies
