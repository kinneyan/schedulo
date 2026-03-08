import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-key")
