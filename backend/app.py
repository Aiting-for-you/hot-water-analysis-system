import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from .extensions import db, migrate
from .logging_config import setup_logging
from .routes.auth import auth_bp
from .routes.datasets import datasets_bp
from .routes.analysis import analysis_bp
from .routes.conversion import conversion_bp
from .routes.ai_assistant import ai_assistant_bp
from .models.user import User
from .models.dataset import Dataset
from .models.conversion import ConversionTask, ConvertedDataset
from .models import user, dataset, conversion, analysis

def create_app():
    setup_logging()
    load_dotenv()

    app = Flask(__name__)

    # Initialize CORS with more specific settings
    CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})

    # Load configuration from config.py
    app.config.from_object('backend.config.Config')

    # --- Configuration ---
    # Get the absolute path of the project's root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(project_root, "instance", "database.db")}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'a-default-jwt-secret-key')
    app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'uploads')
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass

    # --- Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    # --- CLI Commands ---
    from . import commands
    commands.init_app(app)

    # --- Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(datasets_bp, url_prefix='/api/datasets')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(conversion_bp, url_prefix='/api/conversion')
    app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai')

    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    from .routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    from .routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    from .routes.weather import weather_bp
    app.register_blueprint(weather_bp, url_prefix='/api/weather')

    # --- Root Route ---
    @app.route('/')
    def index():
        return "Hello, from the Hot Water System Backend!"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True) 