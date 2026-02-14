"""
Simple Google OAuth Implementation
"""
import streamlit as st
import os
from dotenv import load_dotenv
from database import get_user_by_email, insert_user
import bcrypt
import secrets

load_dotenv()

def create_google_oauth_url():
    """
    Create Google OAuth URL for authentication
    """
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501')
    
    if not client_id:
        return None
    
    # Google OAuth URL
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return oauth_url

def handle_google_signup(email, name):
    """
    Create user account from Google login
    """
    # Check if user exists
    user = get_user_by_email(email)
    
    if not user:
        # Create new user
        random_password = secrets.token_urlsafe(32)
        password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        success = insert_user(name, email, password_hash)
        if not success:
            return None
        
        user = get_user_by_email(email)
    
    return user
