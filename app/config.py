import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'learnhub-secret-2026')
    MYSQL_HOST = os.getenv('DB_HOST')
    MYSQL_USER = os.getenv('DB_USER', 'admin')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD')
    MYSQL_DB = os.getenv('DB_NAME', 'learnhub')
    MYSQL_CURSORCLASS = 'DictCursor'
    AWS_BUCKET = os.getenv('AWS_BUCKET')
    AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
