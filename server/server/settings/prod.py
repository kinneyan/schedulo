"""Production settings — requires all sensitive values to be set via environment variables."""

from typing import List

from .base import *
from server.utils import require_env

DEBUG = False
SECRET_KEY: str = require_env("SECRET_KEY")
ALLOWED_HOSTS: List[str] = [h for h in require_env("ALLOWED_HOSTS").split(",") if h]
