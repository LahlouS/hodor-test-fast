# backend/app/auth/routes.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError
from passlib.context import CryptContext
from app.models import User

from app.db.dependencies import db_dependency

from .services import validate_token, get_current_user, authenticate_user, create_access_token, create_refresh_token, bcrypt_context

from .schemas import CreateUserRequest, Token
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import UTC
from app.config import settings
from uuid import UUID

TIMEOUT = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

router = APIRouter(
	prefix='/auth',
	tags=['auth']
)

def get_user_by_username(db: Session, username: str):
	return db.query(User).filter(User.username == username).first()


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user: CreateUserRequest):
	db_user = get_user_by_username(db, username=create_user.username)
	if db_user:
		raise HTTPException(status_code=400, detail="Username already registered")
	create_user_model = User(
		username = create_user.username,
		email = create_user.email,
		hash_password = bcrypt_context.hash(create_user.password)
	)
	db.add(create_user_model)
	db.commit()
	return "complete"

@router.post('/token', response_model=Token)
async def login_for_access_token(response: Response,
									form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
									db: db_dependency):
	user = authenticate_user(form_data.username, form_data.password, db=db)
	if not user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to authenticate user")
	safe_user_id = user.user_id
	if isinstance(user.user_id, UUID):
		safe_user_id = str(user.user_id)
	access_token = create_access_token(safe_user_id, user.username, expiration=int(TIMEOUT))

	refresh_token = create_refresh_token(safe_user_id, user.username)
	max_age = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 # because expected in seconds

	response.set_cookie(
		key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
	)
	return {'access_token': access_token, 'token_type': 'bearer'}

@router.get("/verify-token/{token}")
async def verify_user_token(token: str):
	await get_current_user(token)
	return {"message": "Token is valid"}


@router.get("/refresh")
async def refresh_access_token(request: Request) -> dict[str, str]:
	try: 
		refresh_token = request.cookies.get("refresh_token")
		if not refresh_token:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing")
		user_data = await validate_token(refresh_token, refresh=True)
		if not user_data or not user_data.get('rt', False):
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unvalid refresh token")
	except ExpiredSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired: you must login again")
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user token")

	new_access_token = create_access_token(user_data["id"], user_data["username"], expiration=int(TIMEOUT))
	return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/logout")
async def logout(
	response: Response,
	request: Request
) -> dict[str, str]:
	try:
		refresh_token = request.cookies.get("refresh_token")
		if not refresh_token:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")
		response.delete_cookie(key="refresh_token")
		return {"message": "Logged out successfully"}
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid")