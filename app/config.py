from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./serials.db")
