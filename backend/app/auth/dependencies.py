# app/auth/dependencies.py
from typing import Annotated
from fastapi import Depends
from .services import get_current_user

user_dependency = Annotated[dict, Depends(get_current_user)]