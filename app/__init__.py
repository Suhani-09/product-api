from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from prometheus_client import Counter, Histogram
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

db = SQLAlchemy()
migrate = Migrate()

class StructuredLogger:
    @staticmethod
    def log(level, message, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'severity': level.upper(),
            'message': message,
            'service': 'product-api',
            **kwargs
        }
        print(json.dumps(log_entry))

logger = StructuredLogger()

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

def create_app():
    app = Flask(__name__)
    
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per hour", "50 per minute"],
        storage_uri="memory://"
    )


    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME", "products")
    db_host = os.environ.get("DB_HOST", "localhost") 
    
    logger.log('INFO', 'Establishing database connection',
               host=db_host, database=db_name, user=db_user)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+pg8000://{db_user}:{db_password}@{db_host}:5432/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["ADMIN_SECRET"] = os.getenv("ADMIN_TOKEN")
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

    db.init_app(app)
    migrate.init_app(app, db)

    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.log('INFO', 'Incoming request',
                   method=request.method,
                   path=request.path,
                   remote_addr=request.remote_addr)

    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            latency = time.time() - g.start_time

            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).inc()

            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(latency)

            logger.log('INFO', 'Request completed',
                       method=request.method,
                       path=request.path,
                       status=response.status_code,
                       latency_ms=round(latency * 1000, 2))

        return response

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    logger.log('INFO', 'Application initialized')

    return app
