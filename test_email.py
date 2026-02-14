"""
Test Email Configuration
"""
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

print("="*60)
print("TESTING EMAIL CONFIGURATION")
print("="*60)

# Check environment variables
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')

print(f"\nSMTP_SERVER: {smtp_server}")
print(f"SMTP_PORT: {smtp_port}")
print(f"SENDER_EMAIL: {sender_email}")
print(f"SENDER_PASSWORD: {'*' * len(sender_password) if sender_password else 'NOT SET'}")

if not all([smtp_server, smtp_port, sender_email, sender_password]):
    print("\n❌ ERROR: Missing email configuration in .env file")
    exit(1)

print("\n" + "="*60)
print("TESTING SMTP CONNECTION")
print("="*60)

try:
    # Test SMTP connection
    print(f"\nConnecting to {smtp_server}:{smtp_port}...")
    server = smtplib.SMTP(smtp_server, int(smtp_port))
    server.starttls()
    print("✅ TLS connection established")
    
    print(f"\nLogging in as {sender_email}...")
    server.login(sender_email, sender_password)
    print("✅ Login successful!")
    
    # Send test email
    print(f"\nSending test email to {sender_email}...")
    
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = sender_email
    message['Subject'] = "Test Email - OCR App"
    
    body = """
    <html>
        <body>
            <h2>Hello! 👋</h2>
            <p>This is a test email from your OCR + AI Summarizer app.</p>
            <p>If you received this, your email configuration is working correctly!</p>
        </body>
    </html>
    """
    
    message.attach(MIMEText(body, 'html'))
    
    server.send_message(message)
    print("✅ Test email sent successfully!")
    
    server.quit()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print(f"\nCheck your inbox: {sender_email}")
    print("Email configuration is working correctly!")
    
except smtplib.SMTPAuthenticationError:
    print("\n❌ ERROR: Authentication failed")
    print("   - Check if 2FA is enabled")
    print("   - Verify app password is correct")
    print("   - Generate new app password if needed")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check SENDER_EMAIL is correct")
    print("2. Check SENDER_PASSWORD has no spaces")
    print("3. Verify 2FA is enabled on Gmail")
    print("4. Generate new app password")
