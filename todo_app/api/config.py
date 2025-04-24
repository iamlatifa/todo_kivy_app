import os
from dotenv import load_dotenv
load_dotenv()  # Load .env variables into the environment

class Config:
    DB_HOST = os.getenv('DB_HOST', None)
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', None)
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'todo_app')
