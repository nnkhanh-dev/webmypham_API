import os
from dotenv import load_dotenv

load_dotenv()

# Basic configuration via environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")
SECRET_KEY = os.getenv("SECRET_KEY")
UVICORN_HOST = os.getenv("UVICORN_HOST", "0.0.0.0")
UVICORN_PORT = int(os.getenv("UVICORN_PORT", 8000))
RELOAD = os.getenv("RELOAD", "true").lower() in ("1", "true", "yes")

# token config centralised here
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALGORITHM = os.getenv("ALGORITHM", "HS256")