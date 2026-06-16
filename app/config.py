import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))


def get_upload_folder():
    upload_folder = os.getenv('UPLOAD_FOLDER')
    if upload_folder:
        if os.path.isabs(upload_folder):
            return upload_folder
        return os.path.abspath(os.path.join(PROJECT_ROOT, upload_folder))
    return os.path.join(BASE_DIR, 'static', 'uploads')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = get_upload_folder()
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB