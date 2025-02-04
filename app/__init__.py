from flask import Flask
from .config import Config
from .models.models import db
from .routes.routes import main
from app.routes.admin_routes import admin_bp
from app.routes.prof_routes import prof_bp
from app.routes.student_routes import student_bp
    
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(admin_bp)
    app.register_blueprint(prof_bp)
    app.register_blueprint(student_bp)
    return app