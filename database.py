"""
Database Connection and Operations
Handles Neon PostgreSQL connection
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_database_url():
    """Get database URL from Streamlit secrets or environment"""
    try:
        return st.secrets["DATABASE_URL"]
    except:
        return os.getenv('DATABASE_URL')

def get_db_connection():
    """
    Create and return a database connection
    """
    try:
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
    Create users table if it doesn't exist
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
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
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            return False
    return False

def insert_user(username, email, password_hash):
    """
    Insert a new user into the database
    Uses parameterized queries to prevent SQL injection
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except psycopg2.IntegrityError:
            return False
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False
    return False

def get_user_by_email(email):
    """
    Retrieve user by email
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    return None

def get_user_by_id(user_id):
    """
    Retrieve user by ID
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
    Create OCR history table if it doesn't exist
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ocr_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    image_name VARCHAR(255),
                    extracted_text TEXT,
                    summary TEXT,
                    summary_length VARCHAR(50),
                    language VARCHAR(50),
                    tokens_used INTEGER,
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

def save_ocr_result(user_id, image_name, extracted_text, summary, summary_length, language, tokens_used):
    """
    Save OCR result to history
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO ocr_history 
                (user_id, image_name, extracted_text, summary, summary_length, language, tokens_used) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (user_id, image_name, extracted_text, summary, summary_length, language, tokens_used)
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
    Get user's OCR history
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, image_name, extracted_text, summary, summary_length, 
                language, tokens_used, created_at 
                FROM ocr_history WHERE user_id = %s 
                ORDER BY created_at DESC LIMIT %s""",
                (user_id, limit)
            )
            history = cursor.fetchall()
            cursor.close()
            conn.close()
            return history
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    return []

def get_user_stats(user_id):
    """
    Get user statistics
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT 
                COUNT(*) as total_ocr,
                SUM(tokens_used) as total_tokens,
                MAX(created_at) as last_activity
                FROM ocr_history WHERE user_id = %s""",
                (user_id,)
            )
            stats = cursor.fetchone()
            cursor.close()
            conn.close()
            return stats
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None
    return None

def delete_history_item(history_id, user_id):
    """
    Delete a history item
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
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

def search_history(user_id, search_term):
    """
    Search in user's history
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, image_name, extracted_text, summary, summary_length, 
                language, tokens_used, created_at 
                FROM ocr_history WHERE user_id = %s 
                AND (extracted_text ILIKE %s OR summary ILIKE %s)
                ORDER BY created_at DESC LIMIT 50""",
                (user_id, f'%{search_term}%', f'%{search_term}%')
            )
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"Error searching history: {e}")
            return []
    return []

def create_ocr_history_table():
    """
    Create OCR history table for storing results
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
    Save OCR result to database
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
    Get OCR history for a user
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
            history = cursor.fetchall()
            cursor.close()
            conn.close()
            return history
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
    return []

def search_history(user_id, search_term):
    """
    Search in user's OCR history
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
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

def update_user_role(user_id, role):
    """
    Update user role (user/admin)
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
    Get all users (admin only)
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
    Get overall statistics (admin only)
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

def delete_history_item(history_id, user_id):
    """
    Delete a history item
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
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
