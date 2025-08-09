"""
Main Flask application for You.FM Web Interface.

This module provides the web server entry point and application configuration.
"""

import os
import logging
from flask import Flask
from web.routes import web_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """
    Application factory function for creating Flask app.
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Basic Flask configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year for audio files

    # Configure timeouts for long-running requests (audio generation can take 3+ minutes)
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    # Note: Flask dev server doesn't have built-in timeout config, but we'll handle this in production
    
    # Development specific settings
    if config_name == 'development':
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
    elif config_name == 'testing':
        app.config['DEBUG'] = False
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    else:  # production
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    
    # Register blueprints
    app.register_blueprint(web_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return web_bp.not_found_error(error)
    
    @app.errorhandler(500)
    def internal_error(error):
        return web_bp.internal_error(error)
    
    logger.info(f"Flask application created with config: {config_name}")
    return app


# Create application instance
app = create_app()


if __name__ == '__main__':
    """
    Development server entry point.
    
    For production deployment, use a WSGI server like Gunicorn:
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
    """
    logger.info("Starting You.FM Web Interface...")
    logger.info("Access the application at: http://localhost:8080")
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=True
    ) 