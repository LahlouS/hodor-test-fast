# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import model_validator
from pathlib import Path
import os
import enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Environment(enum.StrEnum):
	production = "production"
	development = "development"

# Alternative: Cleaner approach using different classes
class DockerSettings(BaseSettings):
	"""Settings for Docker environment - reads from environment variables"""

	SECRET_KEY: str
	ALGORITHM: str
	ACCESS_TOKEN_EXPIRE_MINUTES: int
	REFRESH_TOKEN_EXPIRE_MINUTES: int
	REFRESH_TOKEN_EXPIRE_DAYS: int

	POSTGRES_DB_URL: str
	POSTGRES_HOST: str
	POSTGRES_PORT: int
	POSTGRES_DATABASE: str
	POSTGRES_USER: str
	POSTGRES_PSWD: str
	API_VERSION: str



# Use this instead of direct instantiation
settings = DockerSettings()
