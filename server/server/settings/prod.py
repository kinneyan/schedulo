import os

from .default import *

DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]
ALLOWED_HOSTS = [h for h in os.environ["ALLOWED_HOSTS"].split(",") if h]
CORS_ALLOWED_ORIGINS = [h for h in os.environ["CORS_ALLOWED_ORIGINS"].split(",") if h]
# All three above raise KeyError at startup if the env var is not set — intentional
