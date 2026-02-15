"""
Authentication Module - User Security
Handles user signup, login, and logout with secure password hashing
Uses bcrypt for password encryption
"""
import bcrypt
import streamlit as st
from database import insert_user, get_user_by_email, create_users_table, create_ocr_history_table

# Initialize database tables when module loads
create_users_table()  # Create users table if not exists
create_ocr_history_table()  # Create history table if not exists

def hash_password(password):
    """
    Hash (encrypt) password using bcrypt for security
    
    How it works:
    1. Takes plain text password
    2. Generates a random salt (extra security)
    3. Hashes password with salt
    4. Returns encrypted password string
    
    Args:
        password (str): Plain text password from user
    
    Returns:
        str: Hashed (encrypted) password safe to store in database
    """
    # Generate random salt for extra security
    salt = bcrypt.gensalt()
    
    # Hash the password with salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Return as string (decode from bytes)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Verify if entered password matches stored hashed password
    
    How it works:
    1. Takes plain text password from login
    2. Takes hashed password from database
    3. Compares them securely
    4. Returns True if match, False if not
    
    Args:
        password (str): Plain text password entered by user
        hashed_password (str): Hashed password from database
    
    Returns:
        bool: True if passwords match, False otherwise
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),  # Convert to bytes
        hashed_password.encode('utf-8')  # Convert to bytes
    )

def signup_user(username, email, password):
    """
    Register a new user account
    
    How it works:
    1. Check if email already exists
    2. Hash the password for security
    3. Save user to database
    4. Return success or error message
    
    Args:
        username (str): User's chosen username
        email (str): User's email address
        password (str): User's chosen password
    
    Returns:
        dict: Contains:
            - success: True/False
            - message: Success or error message
    """
    # Step 1: Check if user already exists with this email
    existing_user = get_user_by_email(email)
    if existing_user:
        return {
            'success': False,
            'message': 'Email already registered'
        }
    
    # Step 2: Hash password for security (never store plain passwords!)
    password_hash = hash_password(password)
    
    # Step 3: Insert user into database
    success = insert_user(username, email, password_hash)
    
    # Step 4: Return result
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
    Authenticate user and create login session
    
    How it works:
    1. Find user by email in database
    2. Verify password matches
    3. Create session (save login state)
    4. Return success or error
    
    Args:
        email (str): User's email
        password (str): User's password
    
    Returns:
        dict: Contains:
            - success: True/False
            - message: Welcome message or error
    """
    # Step 1: Get user from database by email
    user = get_user_by_email(email)
    
    # Step 2: Check if user exists
    if not user:
        return {
            'success': False,
            'message': 'Invalid email or password'
        }
    
    # Step 3: Verify password matches hashed password in database
    if verify_password(password, user['password_hash']):
        # Password correct! Create session
        # Session state keeps user logged in while using app
        st.session_state.logged_in = True
        st.session_state.username = user['username']
        st.session_state.user_id = user['id']
        st.session_state.user_role = user.get('role', 'user')
        
        return {
            'success': True,
            'message': f'Welcome back, {user["username"]}!'
        }
    else:
        # Password incorrect
        return {
            'success': False,
            'message': 'Invalid email or password'
        }

def logout_user():
    """
    Clear session and logout user
    
    How it works:
    1. Clear all session variables
    2. User will be redirected to login page
    """
    # Clear all session data
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_role = None
