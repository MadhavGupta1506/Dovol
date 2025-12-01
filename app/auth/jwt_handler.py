from datetime import datetime, timedelta
from jose import jwt
from ..config import settings
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.access_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str):
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])