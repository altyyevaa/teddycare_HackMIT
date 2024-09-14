import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///teddycare.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key')
TERRA_API_KEY = os.environ.get('TERRA_API_KEY', 'your-terra-api-key')
TERRA_DEV_ID = os.environ.get('TERRA_DEV_ID', 'your-terra-dev-id')