from dotenv import load_dotenv
import os
from pathlib import Path

# Get backend root path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env from backend folder
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print("DB_HOST:", DB_HOST)   # TEMP DEBUG
