import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///noticeboard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Admin settings
    ADMIN_EMAIL = 'admin@noticeboard.com'
    ADMIN_PASSWORD = 'admin123'  # Change in production
    
    # Pagination
    NOTICES_PER_PAGE = 9

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///notices.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Pagination
    NOTICES_PER_PAGE = 10
    
    # Admin credentials (for first setup)
    ADMIN_EMAIL = 'admin@college.edu'
    ADMIN_PASSWORD = 'admin123'    