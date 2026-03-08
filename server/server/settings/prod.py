from typing import List

from .default import *
from server.utils import require_env

DEBUG = False
SECRET_KEY: str = require_env("SECRET_KEY")
ALLOWED_HOSTS: List[str] = [h for h in require_env("ALLOWED_HOSTS").split(",") if h]
