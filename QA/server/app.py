"""
Flask app entry point
Create the Flask instance, register blueprints, and initialize database and CORS
"""
import os
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db


def create_app():
    """
    Application factory function
    Create and configure the Flask app instance
    :return: Flask app instance
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Enable CORS support
    CORS(app, supports_credentials=True)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints (route modules)
    from routes.auth import auth_bp
    from routes.knowledge_base import kb_bp
    from routes.document import doc_bp
    from routes.chat import chat_bp
    from routes.user import user_bp
    from routes.stats import stats_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(kb_bp, url_prefix='/api/knowledge_base')
    app.register_blueprint(doc_bp, url_prefix='/api/document')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

