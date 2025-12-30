from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import psycopg
from psycopg.rows import dict_row
import secrets
import jwt
from typing import Optional
import os
from dotenv import load_dotenv
import bcrypt
from email_service import email_service
import random
import string
# Load environment variables
load_dotenv()

app = FastAPI(title="Tally Connector API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))

# Password hashing functions using bcrypt directly
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# Database connection with Neon SSL support
def get_db():
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "neondb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "your_password"),
        sslmode=os.getenv("DB_SSLMODE", "prefer"),
        connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "30")),
        row_factory=dict_row
    )
    try:
        yield conn
    finally:
        conn.close()

# Models
class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Helper functions for JWT
def create_access_token(user_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "user_id": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes
@app.get("/")
def root():
    return {
        "message": "Tally Connector API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/signup", response_model=TokenResponse)
def signup(user: UserSignup, conn=Depends(get_db)):
    try:
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = hash_password(user.password)
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, phone, email_verification_token)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id, email, full_name, phone, is_verified, created_at
        """, (user.full_name, user.email, password_hash, user.phone, verification_token))
        
        new_user = cursor.fetchone()
        conn.commit()
        
        # Send verification email
        email_service.send_verification_email(
            new_user['email'],
            verification_token,
            new_user['full_name']
        )
        
        # Generate token
        access_token = create_access_token(new_user['user_id'], new_user['email'])
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        cursor.execute("""
            INSERT INTO user_sessions (user_id, session_token, device_type, expires_at)
            VALUES (%s, %s, %s, %s)
        """, (new_user['user_id'], session_token, 'mobile', expires_at))
        conn.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": dict(new_user)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Signup Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")
    
@app.post("/api/auth/login", response_model=TokenResponse)
def login(credentials: UserLogin, conn=Depends(get_db)):
    cursor = conn.cursor()
    
    # Get user
    cursor.execute("""
        SELECT user_id, email, password_hash, full_name, phone, 
               is_active, is_verified, created_at, last_login
        FROM users 
        WHERE email = %s
    """, (credentials.email,))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user['is_active']:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Update last login
    cursor.execute("""
        UPDATE users SET last_login = NOW() WHERE user_id = %s
    """, (user['user_id'],))
    conn.commit()
    
    # Generate token
    access_token = create_access_token(user['user_id'], user['email'])
    
    # Create session
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    cursor.execute("""
        INSERT INTO user_sessions (user_id, session_token, device_type, expires_at)
        VALUES (%s, %s, %s, %s)
    """, (user['user_id'], session_token, 'mobile', expires_at))
    conn.commit()
    
    # Remove password_hash from response
    user_data = {k: v for k, v in user.items() if k != 'password_hash'}
    
    # Ensure all required fields are present
    user_response = {
        'user_id': user_data['user_id'],
        'email': user_data['email'],
        'full_name': user_data['full_name'],
        'phone': user_data.get('phone'),  # Can be null
        'is_verified': user_data.get('is_verified', False),
        'created_at': user_data['created_at'].isoformat() if user_data.get('created_at') else None,
        'last_login': user_data['last_login'].isoformat() if user_data.get('last_login') else None,
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }
@app.post("/api/auth/forgot-password")
def forgot_password(data: ForgotPassword, conn=Depends(get_db)):
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, email, full_name FROM users WHERE email = %s", (data.email,))
    user = cursor.fetchone()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, password reset link has been sent"}
    
    reset_token = secrets.token_urlsafe(32)
    reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    cursor.execute("""
        UPDATE users 
        SET password_reset_token = %s, password_reset_expires = %s
        WHERE user_id = %s
    """, (reset_token, reset_expires, user['user_id']))
    conn.commit()
    
    # Send password reset email
    email_service.send_password_reset_email(
        user['email'],
        reset_token,
        user['full_name']
    )
    
    return {"message": "Password reset link sent to your email"}

@app.post("/api/auth/reset-password")
def reset_password(data: ResetPassword, conn=Depends(get_db)):
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, password_reset_expires 
        FROM users 
        WHERE password_reset_token = %s
    """, (data.token,))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if user['password_reset_expires'] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    new_password_hash = hash_password(data.new_password)
    
    cursor.execute("""
        UPDATE users 
        SET password_hash = %s, 
            password_reset_token = NULL,
            password_reset_expires = NULL,
            updated_at = NOW()
        WHERE user_id = %s
    """, (new_password_hash, user['user_id']))
    conn.commit()
    
    return {"message": "Password reset successful"}

@app.get("/api/auth/me")
def get_current_user(authorization: str = Header(None), conn=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, email, full_name, phone, is_verified, created_at, last_login
        FROM users 
        WHERE user_id = %s AND is_active = TRUE
    """, (payload['user_id'],))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return dict(user)

@app.post("/api/auth/logout")
def logout(authorization: str = Header(None), conn=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM user_sessions WHERE user_id = %s
    """, (payload['user_id'],))
    conn.commit()
    
    return {"message": "Logged out successfully"}
def generate_otp(length=6):
    """Generate numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))

# Email Verification Endpoint
@app.get("/api/auth/verify-email")
def verify_email(token: str, conn=Depends(get_db)):
    """Verify email using token"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, full_name 
        FROM users 
        WHERE email_verification_token = %s
    """, (token,))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    # Update user as verified
    cursor.execute("""
        UPDATE users 
        SET is_verified = TRUE, 
            email_verification_token = NULL,
            updated_at = NOW()
        WHERE user_id = %s
    """, (user['user_id'],))
    conn.commit()
    
    return {
        "message": "Email verified successfully!",
        "email": user['email']
    }

# Resend Verification Email
@app.post("/api/auth/resend-verification")
def resend_verification(email: str, conn=Depends(get_db)):
    """Resend verification email"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, full_name, is_verified 
        FROM users 
        WHERE email = %s
    """, (email,))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user['is_verified']:
        return {"message": "Email already verified"}
    
    # Generate new verification token
    verification_token = secrets.token_urlsafe(32)
    
    cursor.execute("""
        UPDATE users 
        SET email_verification_token = %s
        WHERE user_id = %s
    """, (verification_token, user['user_id']))
    conn.commit()
    
    # Send verification email
    email_service.send_verification_email(
        user['email'],
        verification_token,
        user['full_name']
    )
    
    return {"message": "Verification email sent successfully"}

# Send OTP
@app.post("/api/auth/send-otp")
def send_otp(email: str, conn=Depends(get_db)):
    """Send OTP to email"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email, full_name 
        FROM users 
        WHERE email = %s
    """, (email,))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate OTP
    otp = generate_otp(6)
    otp_expires = datetime.utcnow() + timedelta(minutes=10)
    
    # Store OTP in database (you'll need to add otp column to users table)
    cursor.execute("""
        UPDATE users 
        SET email_verification_token = %s,
            password_reset_expires = %s
        WHERE user_id = %s
    """, (otp, otp_expires, user['user_id']))
    conn.commit()
    
    # Send OTP email
    email_service.send_otp_email(
        user['email'],
        otp,
        user['full_name']
    )
    
    return {"message": "OTP sent successfully to your email"}

# Verify OTP
@app.post("/api/auth/verify-otp")
def verify_otp(email: str, otp: str, conn=Depends(get_db)):
    """Verify OTP"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, email_verification_token, password_reset_expires 
        FROM users 
        WHERE email = %s
    """, (email,))
    
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if OTP matches and not expired
    if user['email_verification_token'] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if user['password_reset_expires'] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Clear OTP after successful verification
    cursor.execute("""
        UPDATE users 
        SET email_verification_token = NULL,
            password_reset_expires = NULL,
            is_verified = TRUE
        WHERE user_id = %s
    """, (user['user_id']))
    conn.commit()
    
    return {"message": "OTP verified successfully"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0",
        port=8000,
        reload=True
    )