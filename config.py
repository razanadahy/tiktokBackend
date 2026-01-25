import os

class Config:
    # MySQL Database configuration for XAMPP
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Niavo jr171102!@localhost:3306/tiktokshop'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
