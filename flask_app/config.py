import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

CHALLENGE1_ADMIN_PASSWORD = required_env("CHALLENGE1_ADMIN_PASSWORD")
CHALLENGE1_FLAG = required_env("CHALLENGE1_FLAG")
CHALLENGE2_ADMIN_PASSWORD = required_env("CHALLENGE2_ADMIN_PASSWORD")
CHALLENGE2_FLAG = required_env("CHALLENGE2_FLAG")
CHALLENGE3_KARLIK_PASSWORD = required_env("CHALLENGE3_KARLIK_PASSWORD")
CHALLENGE3_ADMIN_PASSWORD = required_env("CHALLENGE3_ADMIN_PASSWORD")
CHALLENGE3_FLAG = required_env("CHALLENGE3_FLAG")
CHALLENGE4_FLAG = required_env("CHALLENGE4_FLAG")
SECRET_KEY = required_env("SECRET_KEY")
