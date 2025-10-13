import os

# Load environment variables from .env file if it exists

class Config:
    # API Configuration
    API_CONFIG = {
        'base_url': os.environ.get('API_BASE_URL', 'https://bastrado.co'),
        'retry_attempts': 3,
        'retry_backoff_factor': 0.5,
        'timeout': 30
    }

    # Database Configuration
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'todo_db')
    }

    # App Configuration
    APP_NAME = "Todo App"
    APP_VERSION = "1.0.0"
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'


    # UI Configuration
    THEME_PRIMARY_COLOR = "Blue"
    THEME_STYLE = "Light"  # or "Dark"
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 700

    @classmethod
    def load_config(cls):
        """Load configuration from environment variables and .env file"""
        # This method is called by ApiService but doesn't need to do anything
        # since we're already loading the .env file at module level
        pass 