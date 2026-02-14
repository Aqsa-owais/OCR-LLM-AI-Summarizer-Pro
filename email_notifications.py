"""
Email Notifications Module
Send email notifications to users
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    """
    Send email notification
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body (HTML supported)
    
    Returns:
        bool: Success status
    """
    try:
        # Email configuration (using Gmail as example)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('SENDER_EMAIL', '')
        sender_password = os.getenv('SENDER_PASSWORD', '')
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        # Create message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to_email
        message['Subject'] = subject
        
        # Add body
        message.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_processing_complete_email(to_email, username, filename, summary):
    """
    Send email when OCR processing is complete
    """
    subject = "Your Image Summary is Ready!"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                <h2 style="color: #4285F4; border-bottom: 2px solid #4285F4; padding-bottom: 10px;">
                    Hello {username}! 👋
                </h2>
                
                <p style="font-size: 16px;">
                    Your image summary is ready!
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #34A853; margin-top: 0;">📄 File: {filename}</h3>
                    
                    <h4 style="color: #555;">Summary:</h4>
                    <p style="background: #f5f5f5; padding: 15px; border-left: 4px solid #4285F4; border-radius: 4px;">
                        {summary}
                    </p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
                    <p>Thank you for using <strong>OCR + AI Summarizer Pro</strong></p>
                    <p style="font-size: 12px;">This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)
