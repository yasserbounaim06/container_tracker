import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine the environment (development or production)
env = os.getenv('FLASK_ENV', 'development')

if env == 'production':
    # SQLite configuration for production (Render)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/container_tracker.db')
else:
    # MySQL configuration for development
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:yasser@localhost/container_tracker'

# Common configurations
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Create the instance folder if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'instance'), exist_ok=True)
