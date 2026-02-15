"""
Email Notifications Module - Send Emails to Users
Sends email notifications when OCR processing is complete
Uses Gmail SMTP server
"""
import smtplib  # Python's email sending library
from email.mime.text import MIMEText  # For email body
from email.mime.multipart import MIMEMultipart  # For email with attachments
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def get_email_config():
    """
    Get email configuration settings
    Works on both local (.env) and cloud (st.secrets)
    
    Returns:
        dict: Email settings
            - smtp_server: Gmail SMTP server
            - smtp_port: Port 587 for TLS
            - sender_email: Your email address
            - sender_password: Your app password (not regular password!)
    """
    try:
        # Try Streamlit secrets first (for cloud)
        return {
            'smtp_server': st.secrets.get("SMTP_SERVER", "smtp.gmail.com"),
            'smtp_port': int(st.secrets.get("SMTP_PORT", "587")),
            'sender_email': st.secrets.get("SENDER_EMAIL", ""),
            'sender_password': st.secrets.get("SENDER_PASSWORD", "")
        }
    except:
        # Fall back to .env file (for local)
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL', ''),
            'sender_password': os.getenv('SENDER_PASSWORD', '')
        }

def send_email(to_email, subject, body):
    """
    Send email using Gmail SMTP
    
    How it works:
    1. Get email configuration
    2. Create email message
    3. Connect to Gmail SMTP server
    4. Send email
    
    Args:
        to_email (str): Recipient's email address
        subject (str): Email subject line
        body (str): Email content (HTML supported)
    
    Returns:
        bool: True if email sent successfully, False if failed
    """
    try:
        # Step 1: Get email settings
        config = get_email_config()
        
        # Step 2: Check if email is configured
        if not config['sender_email'] or not config['sender_password']:
            print("Email credentials not configured")
            return False
        
        # Step 3: Create email message
        message = MIMEMultipart()
        message['From'] = config['sender_email']  # From address
        message['To'] = to_email  # To address
        message['Subject'] = subject  # Subject line
        
        # Step 4: Add email body (HTML format)
        message.attach(MIMEText(body, 'html'))
        
        # Step 5: Connect to Gmail SMTP server and send
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()  # Start secure connection
            server.login(config['sender_email'], config['sender_password'])  # Login
            server.send_message(message)  # Send email
        
        return True
    
    # Handle any errors
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_processing_complete_email(to_email, username, filename, summary):
    """
    Send email notification when OCR processing is complete
    
    Email includes:
    - Personalized greeting with username
    - Filename that was processed
    - Complete AI-generated summary
    - Professional HTML formatting
    
    Args:
        to_email (str): User's email address
        username (str): User's name
        filename (str): Name of processed file
        summary (str): AI-generated summary
    
    Returns:
        bool: True if email sent successfully
    """
    # Email subject
    subject = "Your Image Summary is Ready!"
    
    # Email body with HTML formatting
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                <!-- Greeting -->
                <h2 style="color: #4285F4; border-bottom: 2px solid #4285F4; padding-bottom: 10px;">
                    Hello {username}! 👋
                </h2>
                
                <!-- Main message -->
                <p style="font-size: 16px;">
                    Your image summary is ready!
                </p>
                
                <!-- Summary box -->
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #34A853; margin-top: 0;">📄 File: {filename}</h3>
                    
                    <h4 style="color: #555;">Summary:</h4>
                    <p style="background: #f5f5f5; padding: 15px; border-left: 4px solid #4285F4; border-radius: 4px;">
                        {summary}
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
                    <p>Thank you for using <strong>OCR + AI Summarizer Pro</strong></p>
                    <p style="font-size: 12px;">This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Send the email
    return send_email(to_email, subject, body)
