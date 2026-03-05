from jose import ExpiredSignatureError, JWTError, jwt
from app.config import settings
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.models import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC

SECRET_KEY = settings.SECRET_KEY
H_ALGO = settings.ALGORITHM
REFRESH_TIMEOUT = settings.REFRESH_TOKEN_EXPIRE_MINUTES

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

async def validate_token(token: str, refresh=False):
	payload = jwt.decode(token, SECRET_KEY, algorithms=[H_ALGO])
	username: str = payload.get('sub')
	user_id: str = payload.get('id')
	if username is None or user_id is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Could not validate user token")
	user_payload = dict([("username", username), ("id", user_id)])
	is_rt = payload.get('rt', None)
	if refresh and is_rt is not None:
		user_payload.update({'rt': is_rt})
	return user_payload

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
	try:
		data = await validate_token(token)
		return data
	except ExpiredSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user token")

def authenticate_user(username: str, password: str, db: Session) -> User:
	if '@' in username:
		user = db.query(User).filter(User.email == username).first()
	else:
		user = db.query(User).filter(User.username == username).first()
	if not user:
		return False
	if not bcrypt_context.verify(password, user.hash_password):
		return False
	return user

def create_access_token(user_id, username, expiration):
	encode = {'sub': username, 'id': user_id, 'exp': datetime.now(UTC) + timedelta(minutes=expiration)}
	return jwt.encode(encode, SECRET_KEY, H_ALGO)

def create_refresh_token(user_id, username):
	encode = {'sub': username, 
		   		'id': user_id, 
				'exp': datetime.now(UTC) + timedelta(minutes=int(REFRESH_TIMEOUT)), 
				"rt": "oui"}
	return jwt.encode(encode, SECRET_KEY, H_ALGO)
