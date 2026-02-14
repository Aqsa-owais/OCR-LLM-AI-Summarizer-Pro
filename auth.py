"""
Authentication Module
Handles user signup, login, and logout
"""
import bcrypt
import streamlit as st
from database import insert_user, get_user_by_email, create_users_table, create_ocr_history_table

# Initialize database tables
create_users_table()
create_ocr_history_table()

def hash_password(password):
    """
    Hash password using bcrypt
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify password against hashed password
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def signup_user(username, email, password):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = get_user_by_email(email)
    if existing_user:
        return {
            'success': False,
            'message': 'Email already registered'
        }
    
    # Hash password
    password_hash = hash_password(password)
    
    # Insert user
    success = insert_user(username, email, password_hash)
    
    if success:
        return {
            'success': True,
            'message': 'Account created successfully!'
        }
    else:
        return {
            'success': False,
            'message': 'Error creating account. Please try again.'
        }

def login_user(email, password):
    """
    Authenticate user and create session
    """
    user = get_user_by_email(email)
    
    if not user:
        return {
            'success': False,
            'message': 'Invalid email or password'
        }
    
    # Verify password
    if verify_password(password, user['password_hash']):
        # Set session state
        st.session_state.logged_in = True
        st.session_state.username = user['username']
        st.session_state.user_id = user['id']
        st.session_state.user_role = user.get('role', 'user')
        
        return {
            'success': True,
            'message': f'Welcome back, {user["username"]}!'
        }
    else:
        return {
            'success': False,
            'message': 'Invalid email or password'
        }

def logout_user():
    """
    Clear session and logout user
    """
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_role = None
