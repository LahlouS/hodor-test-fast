import time
from datetime import datetime

from fastapi import FastAPI, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import engine
from app import models
from app.db.dependencies import db_dependency
from app.auth.dependencies import user_dependency

from app import auth
from app import logic
from app import middleware
from app.config import settings


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
	title="HODOR test api",
	version=settings.API_VERSION,
	docs_url="/docs",
	redoc_url="/redoc" 
)

app.include_router(auth.router)
app.include_router(logic.router)
app.include_router(middleware.router)

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"http://localhost:3000",
		"http://localhost:3546",
	],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)



@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
	# Returning a proper Response lets CORSMiddleware add its headers.
	# Without this, unhandled exceptions propagate past CORSMiddleware
	# and the 500 response is built by ServerErrorMiddleware (outermost),
	# which knows nothing about CORS.
	return JSONResponse(
		status_code=500,
		content={"detail": "Internal server error"},
	)


@app.get("/health")
async def health_check():
	return {
		"status": "healthy",
		"environment": settings.ENVIRONMENT,
		"version": "1.0.0"
	}

@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification failed")
	return {"user": user}
