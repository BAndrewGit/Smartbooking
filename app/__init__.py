from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .ai import ai_bp

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    with app.app_context():
        from . import routes, models, auth
        db.create_all()

        # Înregistrare blueprint-uri
        app.register_blueprint(auth.auth_bp, url_prefix='/auth')
        app.register_blueprint(routes.routes_bp)
        app.register_blueprint(ai_bp, url_prefix='/ai')

    return app
