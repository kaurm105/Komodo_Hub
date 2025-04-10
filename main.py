import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging before importing app
log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

# Import app after environment setup
from app import app

if __name__ == "__main__":
    # ALWAYS serve the app on port 5000 and bind to all interfaces
    app.logger.info("Starting server on http://0.0.0.0:5000")
    app.logger.info("Using database: " + app.config["SQLALCHEMY_DATABASE_URI"])
    app.run(host="0.0.0.0", port=5000, debug=True)