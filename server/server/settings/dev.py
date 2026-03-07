import os

from .default import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-only-key")
