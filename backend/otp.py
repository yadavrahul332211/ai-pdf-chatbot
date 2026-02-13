from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import OTP, User
from schemas import SendOTPSchema, VerifyOTPSchema, FinalResetPassword
from email_service import send_email
import random
import time
import uuid
import hashlib

router = APIRouter()


# -------------------------------------------
# 1) SEND OTP
# -------------------------------------------
@router.post("/send-otp")
def send_otp(payload: SendOTPSchema, db: Session = Depends(get_db)):
    email = payload.email

    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

    # Generate OTP
    otp_code = str(random.randint(100000, 999999))
    expiry = int(time.time()) + 300  # 5 min expire

    # Save OTP
    otp_obj = OTP(email=email, code=otp_code, expiry=expiry)
    db.add(otp_obj)
    db.commit()

    # Send OTP to email
    send_email(email, f"Your OTP is {otp_code}")

    return {"message": "OTP sent successfully"}


# -------------------------------------------
# 2) VERIFY OTP
# -------------------------------------------
@router.post("/verify-otp")
def verify_otp(payload: VerifyOTPSchema, db: Session = Depends(get_db)):
    email = payload.email
    code = payload.code

    # Get latest OTP for user
    otp_entry = (
        db.query(OTP)
        .filter(OTP.email == email)
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_entry:
        raise HTTPException(404, "OTP not found")

    if otp_entry.code != code:
        raise HTTPException(400, "Invalid OTP")

    if otp_entry.expiry < int(time.time()):
        raise HTTPException(400, "OTP expired")

    # Create reset token
    reset_token = str(uuid.uuid4())

    # Save token in user table
    user = db.query(User).filter(User.email == email).first()
    user.reset_token = reset_token
    db.commit()

    return {
        "message": "OTP verified successfully",
        "reset_token": reset_token
    }


# -------------------------------------------
# 3) FINAL RESET PASSWORD
# -------------------------------------------
@router.post("/reset-password-final")
def reset_password_final(payload: FinalResetPassword, db: Session = Depends(get_db)):
    reset_token = payload.reset_token
    new_password = payload.new_password

    # Check user
    user = db.query(User).filter(User.reset_token == reset_token).first()
    if not user:
        raise HTTPException(404, "Invalid reset token")

    # Hash password
    hashed_pass = hashlib.sha256(new_password.encode()).hexdigest()

    user.password = hashed_pass
    user.reset_token = None  # clear token
    db.commit()

    return {"message": "Password reset successfully"}

