import os
from dotenv import load_dotenv

# Charger les variables d'environnement AVANT de les utiliser
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sécurité des sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True 
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 1800  # En secondes (30 min)

    # Protection Content Security Policy (CSP)
    CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self' 'unsafe-inline'",
        "img-src": "'self' data:",
        "frame-ancestors": "'none'",
    }

    # Clé de chiffrement sécurisée
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default_encryption_key')
