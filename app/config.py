import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super_secret_key')  # Change à une vraie clé secrète
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@localhost/ent'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True  # Empêche l’accès au cookie via JavaScript
    SESSION_COOKIE_SECURE = True  # Active la sécurité HTTPS (en production)
    SESSION_PERMANENT = True  # Active les sessions permanentes
    PERMANENT_SESSION_LIFETIME = 1800  # Expiration après 30 minutes (1800 secondes)