import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///teddycare.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


TERRA_DEV_ID = os.environ.get("TERRA_DEV_ID", "4actk-swing-testing-WwNOgPcxJ8")
TERRA_API_KEY = os.environ.get("TERRA_API_KEY", "bYY_oG_vvUo5bK8LUgg5N47dcmg2zjk_")
TERRA_SECRET = os.environ.get("TERRA_SECRET", "your-terra-secret")
