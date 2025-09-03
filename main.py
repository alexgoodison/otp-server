from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from otp_service import OTPService
from mock_database import get_user_phone, user_exists

# Load environment variables
load_dotenv()

app = FastAPI(title="OTP Service", description="FastAPI server for sending and verifying OTP codes")

# Pydantic models
class SendCodeRequest(BaseModel):
    user_id: str

class VerifyCodeRequest(BaseModel):
    user_id: str
    passcode: str

class SendCodeResponse(BaseModel):
    message: str
    user_id: str
    phone: str

class VerifyCodeResponse(BaseModel):
    success: bool
    message: str
    user_id: str

# Initialize OTP service
otp_service = OTPService()

@app.get("/")
async def root():
    return {"message": "OTP Service API", "endpoints": ["/send-code", "/verify-code"]}

@app.post("/send-code", response_model=SendCodeResponse)
async def send_code(request: SendCodeRequest):
    """Send OTP code to user via SMS (default method)"""
    print("Received OTP request for user_id: ", request.user_id)

    user_id = request.user_id.lower()
    
    # Check if user exists in database
    if not user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Lookup phone number from database
    phone_number = get_user_phone(user_id)
    if not phone_number:
        raise HTTPException(status_code=404, detail="Phone number not found for user")
    
    # Generate OTP
    otp = otp_service.generate_otp()

    print("Generated OTP: ", otp)
    
    # Store OTP
    otp_service.store_otp(user_id, otp)
    
    # Send OTP via SMS (default method)
    success = otp_service.send_sms(phone_number, otp)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP via SMS")
    
    return SendCodeResponse(
        message="OTP sent successfully via SMS",
        user_id=user_id,
        phone=phone_number
    )

@app.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_code(request: VerifyCodeRequest):
    """Verify the OTP code provided by user"""
    print("Received OTP verification request for user_id: ", request.user_id, " passcode: ", request.passcode)

    user_id = request.user_id.lower()
    success, message, error_type = otp_service.verify_otp(user_id, request.passcode)

    print("OTP verification request for user_id: ", user_id, " success: ", success, " error_type: ", error_type)
    
    # Return appropriate HTTP status codes based on error type
    if success:
        return VerifyCodeResponse(
            success=success,
            message=message,
            user_id=user_id
        )
    else:
        # Map error types to appropriate HTTP status codes
        status_code_map = {
            "not_found": 404,        # OTP not found or expired
            "expired": 410,          # Gone - OTP has expired
            "too_many_attempts": 429, # Too Many Requests - rate limited
            "invalid_code": 400      # Bad Request - wrong code
        }
        
        status_code = status_code_map.get(error_type, 400)
        
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "message": message,
                "user_id": user_id,
                "error_type": error_type
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)
