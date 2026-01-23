
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-key-fallback'
    
    # Database URI Logic
    # 1. Prioritize generic DATABASE_URL (e.g. Neon, Heroku) over Vercel's POSTGRES_URL
    db_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
    
    # 2. SQLAlchemy Fix: postgres:// -> postgresql:// (Required for SQLAlchemy 1.4+)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///bms.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    PERMANENT_SESSION_LIFETIME = 604800 # 7 days in seconds, or handled by datetime timedelta usually

    # Cloudinary configs
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # Max file size 16MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
