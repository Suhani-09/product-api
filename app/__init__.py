from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from google.cloud.sql.connector import Connector
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

db = SQLAlchemy()
migrate = Migrate()
connector = Connector()


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


def getconn():
    logger.log('INFO', 'Establishing database connection')
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


    @app.route('/health')
    def health():
        try:
            db.session.execute('SELECT 1')
            return {'status': 'healthy', 'database': 'connected'}, 200
        except:
            return {'status': 'unhealthy', 'database': 'disconnected'}, 503
    
    @app.route('/metrics')
    def metrics():
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    logger.log('INFO', 'Application initialized')
    
    return app