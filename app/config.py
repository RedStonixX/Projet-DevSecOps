import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')  # Change à une vraie clé secrète
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost/ent'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔒 Sécurité des sessions
    SESSION_COOKIE_HTTPONLY = True  # Empêche l’accès au cookie via JavaScript
    SESSION_COOKIE_SECURE = True  # Active la sécurité HTTPS (en production)
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protège contre les attaques CSRF intersites
    SESSION_PERMANENT = True  # Active les sessions permanentes
    PERMANENT_SESSION_LIFETIME = 1800  # Expiration après 30 minutes (1800 secondes)

    # 🔥 Protection Content Security Policy (CSP)
    CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",  # Charge uniquement les ressources depuis ton domaine
        "script-src": "'self'",  # Bloque les scripts externes
        "style-src": "'self' 'unsafe-inline'",  # Autorise uniquement les styles internes
        "img-src": "'self' data:",  # Autorise les images locales et en base64
        "frame-ancestors": "'none'",  # Empêche l’inclusion en iframe (Clickjacking)
    }
