import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '8vC3BqPJueHIXmZC0JYe')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('SECRET_KEY', '8vC3BqPJueHIXmZC0JYe')