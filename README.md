# OTP Service API

A FastAPI server that provides OTP (One-Time Password) functionality with support for both SMS (via Twilio) and email delivery.

## Features

- 🚀 FastAPI-based REST API
- 📱 SMS OTP delivery via Twilio
- 📧 Email OTP delivery via SMTP
- 🔒 Secure OTP storage with Redis (fallback to in-memory)
- ⏰ Configurable OTP expiration (default: 5 minutes)
- 🛡️ Rate limiting with attempt tracking
- 📊 Comprehensive error handling and validation

## API Endpoints

### 1. Send OTP Code
**POST** `/send-code`

Send an OTP code to a user via SMS or email.

**Request Body:**
```json
{
  "user_id": "user123",
  "method": "sms",  // "sms" or "email"
  "phone": "+1234567890",  // required for SMS
  "email": "user@example.com"  // required for email
}
```

**Response:**
```json
{
  "message": "OTP sent successfully via sms",
  "user_id": "user123",
  "method": "sms"
}
```

### 2. Verify OTP Code
**POST** `/verify-code`

Verify the OTP code provided by the user.

**Request Body:**
```json
{
  "user_id": "user123",
  "passcode": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user_id": "user123"
}
```

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd opt-server
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your credentials:

```bash
cp env.example .env
```

Edit `.env` file with your actual credentials:

```env
# Twilio Configuration (for SMS)
TWILIO_ACCOUNT_SID=your_actual_account_sid
TWILIO_AUTH_TOKEN=your_actual_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email Configuration (for email OTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Service Setup

#### Twilio Setup (for SMS)
1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the console
3. Purchase a phone number or use the trial number
4. Add credentials to your `.env` file

#### Email Setup (for Gmail)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use your Gmail address and the app password in `.env`

#### Redis Setup (optional)
```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Install Redis (Ubuntu)
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

If Redis is not available, the service will automatically fall back to in-memory storage.

### 4. Run the Server

```bash
# Development
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Examples

### Send SMS OTP
```bash
curl -X POST "http://localhost:8000/send-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "method": "sms",
       "phone": "+1234567890"
     }'
```

### Send Email OTP
```bash
curl -X POST "http://localhost:8000/send-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "method": "email",
       "email": "user@example.com"
     }'
```

### Verify OTP
```bash
curl -X POST "http://localhost:8000/verify-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "passcode": "123456"
     }'
```

## Security Features

- **Expiration**: OTPs expire after 5 minutes
- **Rate Limiting**: Maximum 3 verification attempts per OTP
- **Secure Storage**: OTPs are stored securely and deleted after verification
- **Input Validation**: All inputs are validated using Pydantic models

## Error Handling

The API provides comprehensive error messages for various scenarios:
- Invalid or missing credentials
- Expired OTPs
- Too many failed attempts
- Service configuration issues
- Network/delivery failures

## Development

### Project Structure
```
opt-server/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
└── README.md           # This file
```

### Testing

You can test the endpoints using:
- FastAPI's built-in docs at `/docs`
- Postman or similar API testing tools
- curl commands as shown in the examples above

## License

This project is open source and available under the [MIT License](LICENSE).
