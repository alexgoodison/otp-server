# OTP Service API

A FastAPI server that provides OTP (One-Time Password) functionality with SMS delivery via Twilio. The service uses a user database lookup system to automatically retrieve phone numbers for registered users.

## Features

- 🚀 FastAPI-based REST API
- 📱 SMS OTP delivery via Twilio
- 👤 User database lookup for phone numbers
- 🔒 Secure OTP storage with Redis (fallback to in-memory)
- ⏰ Configurable OTP expiration (default: 5 minutes)
- 🛡️ Rate limiting with attempt tracking
- 📊 Comprehensive error handling and validation
- 🔄 Case-insensitive user ID handling

## API Endpoints

### 1. Send OTP Code
**POST** `/send-code`

Send an OTP code to a user via SMS. The system automatically looks up the user's phone number from the database.

**Request Body:**
```json
{
  "user_id": "abc"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully via SMS",
  "user_id": "abc",
  "phone": "+11111111111"
}
```

**Error Responses:**
- `404`: User not found in database
- `404`: Phone number not found for user
- `500`: Failed to send SMS

### 2. Verify OTP Code
**POST** `/verify-code`

Verify the OTP code provided by the user.

**Request Body:**
```json
{
  "user_id": "abc",
  "passcode": "123456"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user_id": "abc"
}
```

**Error Responses:**
- `400` (Bad Request) - Invalid OTP code:
```json
{
  "detail": {
    "success": false,
    "message": "Invalid OTP. 2 attempts remaining",
    "user_id": "abc",
    "error_type": "invalid_code"
  }
}
```

- `404` (Not Found) - OTP not found:
```json
{
  "detail": {
    "success": false,
    "message": "No OTP found for this user or OTP has expired",
    "user_id": "abc",
    "error_type": "not_found"
  }
}
```

- `410` (Gone) - OTP expired:
```json
{
  "detail": {
    "success": false,
    "message": "OTP has expired",
    "user_id": "abc",
    "error_type": "expired"
  }
}
```

- `429` (Too Many Requests) - Too many failed attempts:
```json
{
  "detail": {
    "success": false,
    "message": "Too many failed attempts",
    "user_id": "abc",
    "error_type": "too_many_attempts"
  }
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
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

#### User Database Setup
The service includes a mock database (`mock_database.py`) with user-to-phone number mappings. Currently configured user:
- User ID: `abc`
- Phone: `+11111111111`

To add more users, edit the `USER_PHONE_DATABASE` dictionary in `mock_database.py`.

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

### 5. Expose Server to Internet with ngrok (Optional)

To make your local server accessible from the internet (useful for webhook testing, mobile app development, or sharing with others), you can use ngrok:

#### Install ngrok

**macOS (using Homebrew):**
```bash
brew install ngrok
```

**Windows/Linux:**
1. Download from [ngrok.com](https://ngrok.com/download)
2. Extract and add to your PATH

#### Setup ngrok Account (Optional but Recommended)
1. Sign up at [ngrok.com](https://ngrok.com/)
2. Get your authtoken from the dashboard
3. Configure ngrok with your authtoken:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

#### Expose Your Server

1. **Start your OTP server first:**
```bash
python main.py
```

2. **In a new terminal, start ngrok:**
```bash
# Expose port 8000 with HTTP tunnel
ngrok http 8000

# Or with a custom subdomain (requires paid plan)
ngrok http --subdomain=my-otp-server 8000
```

3. **ngrok will provide you with public URLs:**
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
Forwarding                    http://abc123.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

#### Using the Public URLs

Once ngrok is running, you can access your API using the provided URLs:

- **API**: https://abc123.ngrok.io
- **Interactive Docs**: https://abc123.ngrok.io/docs
- **ReDoc**: https://abc123.ngrok.io/redoc

#### Example API Calls with ngrok

```bash
# Send OTP using the ngrok URL
curl -X POST "https://abc123.ngrok.io/send-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "abc"
     }'

# Verify OTP using the ngrok URL
curl -X POST "https://abc123.ngrok.io/verify-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "abc",
       "passcode": "123456"
     }'
```

## Updating the Mock Database

The service uses a mock database (`mock_database.py`) to store user information. To add or modify users:

### Adding New Users

1. Open `mock_database.py`
2. Edit the `USER_PHONE_DATABASE` dictionary:

```python
USER_PHONE_DATABASE = {
    "abc": "+11111111111",
    "user456": "+12345678901",
    "john_doe": "+19876543210",
    # Add more users as needed
}
```

### Database Structure

Each entry in the database maps a `user_id` to a phone number:
- **Key**: `user_id` (string) - The unique identifier for the user
- **Value**: `phone` (string) - The phone number in E.164 format (e.g., `+1234567890`)

### Important Notes

- **Phone Format**: Use E.164 format with country code (e.g., `+1` for US)
- **User IDs**: Are case-insensitive (automatically converted to lowercase)
- **Restart Required**: After modifying the database, restart the server to apply changes


## Usage Examples

### Send SMS OTP
```bash
curl -X POST "http://localhost:8000/send-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "abc"
     }'
```

**Response:**
```json
{
  "message": "OTP sent successfully via SMS",
  "user_id": "abc",
  "phone": "+11111111111"
}
```

### Verify OTP
```bash
curl -X POST "http://localhost:8000/verify-code" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "abc",
       "passcode": "123456"
     }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "OTP verified successfully",
  "user_id": "abc"
}
```

**Error Response Example (400 for invalid code):**
```json
{
  "detail": {
    "success": false,
    "message": "Invalid OTP. 2 attempts remaining",
    "user_id": "abc",
    "error_type": "invalid_code"
  }
}
```

## Development

### Project Structure
```
otp-server/
├── main.py              # Main FastAPI application and API endpoints
├── otp_service.py       # OTP service class with SMS/storage functionality
├── mock_database.py     # Mock user database for phone number lookup
├── requirements.txt     # Python dependencies
├── env.example          # Environment variables template
└── README.md            # This file
```

### Testing

You can test the endpoints using:
- FastAPI's built-in docs at `/docs`
- Postman or similar API testing tools
- curl commands as shown in the examples above
