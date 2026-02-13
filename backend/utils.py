import random
import hashlib
import jwt
import datetime

SECRET_KEY = "MYSECRET123456789"  # minimum 32 chars recommended


# ------------------------------------
# 1) GENERATE OTP
# ------------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# ------------------------------------
# 2) PASSWORD HASH
# ------------------------------------
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------------------------
# 3) PASSWORD VERIFY
# ------------------------------------
def verify_password(input_password: str, stored_hash: str):
    return hash_password(input_password) == stored_hash


# ------------------------------------
# 4) JWT TOKEN
# ------------------------------------
def create_jwt(data: dict):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    payload = {**data, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

