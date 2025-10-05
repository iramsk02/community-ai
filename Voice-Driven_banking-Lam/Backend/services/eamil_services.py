import smtplib
import os
import logging
from email.message import EmailMessage
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
logger = logging.getLogger(__name__)

# Get credentials from .env file
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_otp_email(recipient_email: str, otp: str) -> bool:
    """
    Formats an email with the provided OTP and sends it.

    Returns:
        True if the email was sent successfully, False otherwise.
    """
    if not SENDER_EMAIL or not EMAIL_APP_PASSWORD:
        logger.error("Email credentials (SENDER_EMAIL, EMAIL_APP_PASSWORD) not configured in .env file.")
        return False
        
    # Calculate the expiration time
    expiry_time = datetime.now() + timedelta(minutes=15)
    formatted_time = expiry_time.strftime("%I:%M %p") # e.g., "03:30 PM"

    # Create the email body using your template
    email_body = f"""
    To authenticate, please use the following One Time Password (OTP):
    {otp}

    This OTP will be valid for 15 minutes, until {formatted_time}.

    Do not share this OTP with anyone. If you didn't make this request, you can safely ignore this email.
    """

    # Create the EmailMessage object
    msg = EmailMessage()
    msg.set_content(email_body)
    msg['Subject'] = 'Your Voice Banking Verification Code'
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            print("SENDER_EMAIL:", SENDER_EMAIL)
            server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"OTP email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email: {e}", exc_info=True)
        return False

# --- Standalone Test ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("--- Running Email Service Test ---")
    
    # IMPORTANT: Replace with your own email address to receive the test OTP
    test_recipient = "Vickey@gamil.com"
    test_otp = "123456"
    
    success = send_otp_email(test_recipient, test_otp)
    
    if success:
        logger.info(f"✅ Test email sent successfully to {test_recipient}. Please check your inbox.")
    else:
        logger.error("❌ Test email failed to send. Check your .env credentials and error logs.")