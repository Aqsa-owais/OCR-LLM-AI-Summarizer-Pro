"""
Google OAuth Module - Google Sign-In Integration
Handles "Continue with Google" functionality
Creates user accounts from Google login
"""
import streamlit as st
import os
from dotenv import load_dotenv
from database import get_user_by_email, insert_user
import bcrypt  # For password hashing
import secrets  # For generating random passwords

# Load environment variables
load_dotenv()

def create_google_oauth_url():
    """
    Create Google OAuth URL for authentication
    
    How it works:
    1. Gets Google Client ID from environment
    2. Creates OAuth URL with required parameters
    3. User clicks this URL to sign in with Google
    
    Returns:
        str: Google OAuth URL OR None if not configured
    """
    # Get Google Client ID from .env
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501')
    
    # Check if Google OAuth is configured
    if not client_id:
        return None
    
    # Build Google OAuth URL
    # This URL takes user to Google sign-in page
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"  # Request email and profile
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return oauth_url

def handle_google_signup(email, name):
    """
    Create or login user account from Google
    
    How it works:
    1. Check if user already exists with this email
    2. If exists, return existing user
    3. If new, create account with random password
    4. Return user data
    
    Args:
        email (str): User's email from Google
        name (str): User's name from Google
    
    Returns:
        dict: User data OR None if failed
    """
    # Step 1: Check if user already exists
    user = get_user_by_email(email)
    
    # Step 2: If user doesn't exist, create new account
    if not user:
        # Generate random secure password
        # User won't need this - they login with Google
        random_password = secrets.token_urlsafe(32)
        
        # Hash the password for security
        password_hash = bcrypt.hashpw(
            random_password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user in database
        success = insert_user(name, email, password_hash)
        if not success:
            return None
        
        # Get the newly created user
        user = get_user_by_email(email)
    
    # Step 3: Return user data
    return user
