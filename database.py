"""
Database Module - PostgreSQL Operations
Handles all database connections and operations
Uses Neon PostgreSQL (cloud database)
"""
import psycopg2  # PostgreSQL adapter for Python
from psycopg2.extras import RealDictCursor  # Returns results as dictionaries
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

def get_database_url():
    """
    Get database connection URL
    Works on both local and Streamlit Cloud
    
    Returns:
        str: Database connection URL
    """
    try:
        # Try Streamlit secrets first (for cloud)
        return st.secrets["DATABASE_URL"]
    except:
        # Fall back to .env file (for local)
        return os.getenv('DATABASE_URL')

def get_db_connection():
    """
    Create connection to PostgreSQL database
    
    How it works:
    1. Gets database URL
    2. Connects to Neon PostgreSQL
    3. Returns connection object
    
    Returns:
        connection: Database connection OR None if failed
    """
    try:
        # Connect to database
        # RealDictCursor makes results come back as dictionaries
        conn = psycopg2.connect(
            get_database_url(),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def create_users_table():
    """
    Create users table in database (if not exists)
    
    Table structure:
    - id: Unique user ID (auto-increment)
    - username: User's name
    - email: User's email (must be unique)
    - password_hash: Encrypted password
    - role: user or admin
    - created_at: When account was created
    
    Returns:
        bool: True if successful, False if failed
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # SQL command to create table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()  # Save changes
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            return False
    return False

def insert_user(username, email, password_hash):
    """
    Add new user to database
    
    Security: Uses parameterized queries to prevent SQL injection
    
    Args:
        username (str): User's name
        email (str): User's email
        password_hash (str): Encrypted password
    
    Returns:
        bool: True if user added, False if email already exists
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # %s are placeholders - prevents SQL injection
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()  # Save to database
            cursor.close()
            conn.close()
            return True
        except psycopg2.IntegrityError:
            # Email already exists
            return False
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False
    return False

def get_user_by_email(email):
    """
    Find user by email address
    
    Args:
        email (str): Email to search for
    
    Returns:
        dict: User data OR None if not found
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()  # Get one result
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    return None

def get_user_by_id(user_id):
    """
    Find user by ID number
    
    Args:
        user_id (int): User's ID
    
    Returns:
        dict: User data OR None if not found
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    return None

def create_ocr_history_table():
    """
    Create table to store OCR processing history
    
    Table structure:
    - id: Unique record ID
    - user_id: Which user processed this
    - filename: Name of uploaded file
    - extracted_text: Text extracted from image
    - summary: AI-generated summary
    - summary_length: Short/Medium/Detailed
    - language: Output language
    - tokens_used: OpenAI tokens used
    - processing_time: How long it took
    - created_at: When it was processed
    
    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ocr_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    filename VARCHAR(255),
                    extracted_text TEXT,
                    summary TEXT,
                    summary_length VARCHAR(50),
                    language VARCHAR(10),
                    tokens_used INTEGER,
                    processing_time FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating ocr_history table: {e}")
            return False
    return False

def save_ocr_result(user_id, filename, extracted_text, summary, summary_length, language, tokens_used, processing_time):
    """
    Save OCR processing result to history
    
    Args:
        user_id (int): User who processed this
        filename (str): Name of file
        extracted_text (str): Text from OCR
        summary (str): AI summary
        summary_length (str): Short/Medium/Detailed
        language (str): Output language
        tokens_used (int): OpenAI tokens
        processing_time (float): Time in seconds
    
    Returns:
        bool: True if saved successfully
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO ocr_history 
                (user_id, filename, extracted_text, summary, summary_length, language, tokens_used, processing_time) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, filename, extracted_text, summary, summary_length, language, tokens_used, processing_time)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving OCR result: {e}")
            return False
    return False

def get_user_history(user_id, limit=50):
    """
    Get user's OCR processing history
    
    Args:
        user_id (int): User's ID
        limit (int): Maximum number of records (default 50)
    
    Returns:
        list: List of history records (newest first)
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM ocr_history 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s""",
                (user_id, limit)
            )
            history = cursor.fetchall()  # Get all results
            cursor.close()
            conn.close()
            return history
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    return []

def search_history(user_id, search_term):
    """
    Search in user's history
    Searches in: extracted text, summary, and filename
    
    Args:
        user_id (int): User's ID
        search_term (str): What to search for
    
    Returns:
        list: Matching history records
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # ILIKE = case-insensitive search
            cursor.execute(
                """SELECT * FROM ocr_history 
                WHERE user_id = %s 
                AND (extracted_text ILIKE %s OR summary ILIKE %s OR filename ILIKE %s)
                ORDER BY created_at DESC""",
                (user_id, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')
            )
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"Error searching history: {e}")
            return []
    return []

def get_user_statistics(user_id):
    """
    Get statistics for a user
    
    Calculates:
    - Total OCR processed
    - Total tokens used
    - Average processing time
    - Number of active days
    
    Args:
        user_id (int): User's ID
    
    Returns:
        dict: Statistics data
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT 
                COUNT(*) as total_ocr,
                SUM(tokens_used) as total_tokens,
                AVG(processing_time) as avg_processing_time,
                COUNT(DISTINCT DATE(created_at)) as active_days
                FROM ocr_history 
                WHERE user_id = %s""",
                (user_id,)
            )
            stats = cursor.fetchone()
            cursor.close()
            conn.close()
            return stats
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return None
    return None

def delete_history_item(history_id, user_id):
    """
    Delete a history record
    
    Security: Only allows user to delete their own records
    
    Args:
        history_id (int): ID of record to delete
        user_id (int): User's ID (for security)
    
    Returns:
        bool: True if deleted successfully
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Only delete if it belongs to this user
            cursor.execute(
                "DELETE FROM ocr_history WHERE id = %s AND user_id = %s",
                (history_id, user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting history: {e}")
            return False
    return False

def update_user_role(user_id, role):
    """
    Update user's role (user or admin)
    Admin feature only
    
    Args:
        user_id (int): User's ID
        role (str): 'user' or 'admin'
    
    Returns:
        bool: True if updated
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (role, user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating role: {e}")
            return False
    return False

def get_all_users():
    """
    Get list of all users
    Admin feature only
    
    Returns:
        list: All users (without passwords)
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    return []

def get_admin_statistics():
    """
    Get overall platform statistics
    Admin feature only
    
    Returns:
        dict: Platform-wide stats
            - total_users: Total registered users
            - total_ocr: Total OCR processed
            - total_tokens: Total tokens used
            - today_ocr: OCR processed today
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM ocr_history) as total_ocr,
                (SELECT SUM(tokens_used) FROM ocr_history) as total_tokens,
                (SELECT COUNT(*) FROM ocr_history WHERE DATE(created_at) = CURRENT_DATE) as today_ocr
            """)
            stats = cursor.fetchone()
            cursor.close()
            conn.close()
            return stats
        except Exception as e:
            print(f"Error fetching admin statistics: {e}")
            return None
    return None
