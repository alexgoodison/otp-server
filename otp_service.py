import os
import random
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import redis
import json
from typing import Optional
from fastapi import HTTPException

# Initialize Redis for storing OTPs (you can also use in-memory dict for development)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
except:
    # Fallback to in-memory storage if Redis is not available
    redis_client = None
    otp_storage = {}


class OTPService:
    def __init__(self):
        # Twilio configuration
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        # Initialize Twilio client if credentials are available
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def store_otp(self, user_id: str, otp: str, expires_in: int = 300):
        """Store OTP with expiration (5 minutes default)"""
        otp_data = {
            "code": otp,
            "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
            "attempts": 0
        }
        
        if redis_client:
            redis_client.setex(f"otp:{user_id}", expires_in, json.dumps(otp_data))
        else:
            otp_storage[user_id] = otp_data
    
    def get_otp(self, user_id: str) -> Optional[dict]:
        """Retrieve OTP data for user"""
        if redis_client:
            data = redis_client.get(f"otp:{user_id}")
            return json.loads(data) if data else None
        else:
            return otp_storage.get(user_id)
    
    def delete_otp(self, user_id: str):
        """Delete OTP data for user"""
        if redis_client:
            redis_client.delete(f"otp:{user_id}")
        else:
            otp_storage.pop(user_id, None)
    
    def send_sms(self, phone: str, otp: str) -> bool:
        """Send OTP via SMS using Twilio"""
        if not self.twilio_client:
            raise HTTPException(status_code=500, detail="Twilio not configured")
        
        try:
            message = self.twilio_client.messages.create(
                body=f"Your verification code is: {otp}. This code expires in 5 minutes.",
                from_=self.twilio_phone_number,
                to=phone
            )
            return True
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False
    
    def send_email(self, email: str, otp: str) -> bool:
        """Send OTP via email"""
        if not self.email_address or not self.email_password:
            raise HTTPException(status_code=500, detail="Email not configured")
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = email
            msg['Subject'] = "Your Verification Code"
            
            body = f"""
            <html>
                <body>
                    <h2>Verification Code</h2>
                    <p>Your verification code is: <strong>{otp}</strong></p>
                    <p>This code expires in 5 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def verify_otp(self, user_id: str, provided_code: str) -> tuple[bool, str]:
        """Verify the provided OTP code"""
        otp_data = self.get_otp(user_id)
        
        if not otp_data:
            return False, "No OTP found for this user or OTP has expired"
        
        # Check if OTP has expired
        expires_at = datetime.fromisoformat(otp_data["expires_at"])
        if datetime.now() > expires_at:
            self.delete_otp(user_id)
            return False, "OTP has expired"
        
        # Check attempt limit
        if otp_data["attempts"] >= 3:
            self.delete_otp(user_id)
            return False, "Too many failed attempts"
        
        # Verify the code
        if otp_data["code"] == provided_code:
            self.delete_otp(user_id)
            return True, "OTP verified successfully"
        else:
            # Increment attempts
            otp_data["attempts"] += 1
            if redis_client:
                remaining_ttl = redis_client.ttl(f"otp:{user_id}")
                redis_client.setex(f"otp:{user_id}", remaining_ttl, json.dumps(otp_data))
            else:
                otp_storage[user_id] = otp_data
            
            remaining_attempts = 3 - otp_data["attempts"]
            return False, f"Invalid OTP. {remaining_attempts} attempts remaining"
