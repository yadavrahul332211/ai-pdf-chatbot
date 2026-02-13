from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, OTP
from schemas import Register, Login
from utils import hash_password, verify_password, create_jwt, generate_otp
from email_service import send_email
import time

router = APIRouter()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======================================================
# 1) REGISTER
# ======================================================
@router.post("/register")
def register(user: Register, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email already exists")

    hashed_pwd = hash_password(user.password)
    new_user = User(email=user.email, username=user.username, password=hashed_pwd)

    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}



# ======================================================
# 2) LOGIN
# ======================================================
@router.post("/login")
def login(user: Login, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_jwt({"user_id": db_user.id})
    return {"token": token, "message": "Login successful"}



# ======================================================
# 3) SEND OTP (FORGOT PASSWORD)
# ======================================================
@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "Email not registered")

    otp_code = generate_otp()

    # Save OTP with expiry
    db_otp = OTP(
        email=email,
        code=otp_code,
        expiry=int(time.time()) + 300  # valid 5 min
    )
    db.add(db_otp)
    db.commit()

    send_email(email, otp_code)

    return {"message": "OTP sent to email"}



# ======================================================
# 4) VERIFY OTP
# ======================================================
@router.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):

    latest_otp = (
        db.query(OTP)
        .filter(OTP.email == email)
        .order_by(OTP.id.desc())
        .first()
    )

    if not latest_otp:
        raise HTTPException(400, "No OTP found")

    # Check expiration
    if latest_otp.expiry < int(time.time()):
        raise HTTPException(400, "OTP expired")

    # Check match
    if latest_otp.code != otp:
        raise HTTPException(400, "Invalid OTP")

    return {"message": "OTP verified successfully"}



# ======================================================
# 5) SET NEW PASSWORD (AFTER OTP VERIFIED)
# ======================================================
@router.post("/set-new-password")
def set_new_password(email: str, new_password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

