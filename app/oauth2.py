from fastapi import Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

# Authorization process
def verify_access_token(token: str, cred_exception):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        id: str = payload.get("user_id")
        if id is None:
            raise cred_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise cred_exception
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    cred_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=f'Could not validate credentials', 
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = verify_access_token(token, cred_exception)
    user = db.query(models.User).filter(models.User.id == access_token.id).first()
    return user