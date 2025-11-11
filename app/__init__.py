from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from google.cloud.sql.connector import Connector
import sqlalchemy
import os
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()

load_dotenv(dotenv_path)

db = SQLAlchemy()
migrate = Migrate()

# Initialize the Cloud SQL Connector
connector = Connector()

# Function to return the database connection
def getconn():
    conn = connector.connect(
        os.environ["INSTANCE_CONNECTION_NAME"], # e.g., "my-project:us-central1:my-instance"
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"]
    )
    return conn

def create_app():
    app = Flask(__name__)

    # --- THIS IS THE CORRECT FIX ---
    # We set a dummy URI (it can be anything)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+pg8000://"

    # We pass the 'getconn' function to the 'creator'
    # using SQLALCHEMY_ENGINE_OPTIONS
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "creator": getconn
    }
    # -------------------------------

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Load admin secret from .env
    app.config["ADMIN_SECRET"] = os.getenv("ADMIN_TOKEN")

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app