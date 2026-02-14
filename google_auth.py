"""
Google OAuth Authentication
"""
import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv
from database import get_user_by_email, insert_user
import bcrypt

load_dotenv()

def google_login_button():
    """
    Display Google login button and handle authentication
    """
    # Get Google Client ID from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    
    if not client_id:
        st.info("🔧 Google Sign-In not configured. Add GOOGLE_CLIENT_ID to .env file")
        return None
    
    # Display Google Sign-In button using HTML/JavaScript
    google_button_html = f"""
    <div id="g_id_onload"
         data-client_id="{client_id}"
         data-callback="handleCredentialResponse">
    </div>
    <div class="g_id_signin" data-type="standard"></div>
    
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <script>
        function handleCredentialResponse(response) {{
            // Send token to Streamlit
            window.parent.postMessage({{
                type: 'google_auth',
                token: response.credential
            }}, '*');
        }}
    </script>
    """
    
    st.components.v1.html(google_button_html, height=50)
    
    return None

def verify_google_token(token):
    """
    Verify Google ID token and return user info
    """
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            client_id
        )
        
        # Get user info
        user_info = {
            'email': idinfo.get('email'),
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'email_verified': idinfo.get('email_verified', False)
        }
        
        return user_info
    
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def handle_google_login(user_info):
    """
    Handle Google login - create user if doesn't exist
    """
    if not user_info or not user_info.get('email'):
        return {'success': False, 'message': 'Invalid user info'}
    
    email = user_info['email']
    name = user_info.get('name', email.split('@')[0])
    
    # Check if user exists
    user = get_user_by_email(email)
    
    if not user:
        # Create new user with Google account
        # Generate a random password hash (won't be used for Google login)
        random_password = os.urandom(32).hex()
        password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        success = insert_user(name, email, password_hash)
        
        if not success:
            return {'success': False, 'message': 'Error creating account'}
        
        # Get the newly created user
        user = get_user_by_email(email)
    
    # Set session
    st.session_state.logged_in = True
    st.session_state.username = user['username']
    st.session_state.user_id = user['id']
    st.session_state.google_user = True
    
    return {
        'success': True,
        'message': f'Welcome, {user["username"]}!'
    }
