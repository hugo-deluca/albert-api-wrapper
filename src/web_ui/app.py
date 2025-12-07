from flask import Flask
import os
from dotenv import load_dotenv
from albert_wrapper import AlbertAPIWrapper, APIConfig

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize Albert API wrapper
    api_config = APIConfig(
        api_key=os.getenv('ALBERT_API_KEY'),
        base_url=os.getenv('ALBERT_API_BASE_URL', 'https://albert.api.etalab.gouv.fr')
    )
    app.albert = AlbertAPIWrapper(api_config)
    
    # Register custom Jinja2 filters
    @app.template_filter('format_timestamp')
    def format_timestamp(timestamp):
        """Convert Unix timestamp to readable date."""
        from datetime import datetime
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        return 'N/A'
    
    # Register routes
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()