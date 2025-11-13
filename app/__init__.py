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


connector = Connector()

def getconn():
    conn = connector.connect(
        os.environ["INSTANCE_CONNECTION_NAME"], 
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"]
    )
    return conn

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+pg8000://"

    
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "creator": getconn
    }
    

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    app.config["ADMIN_SECRET"] = os.getenv("ADMIN_TOKEN")

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app