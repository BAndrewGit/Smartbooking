from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

load_dotenv(dotenv_path='Keys.env')


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    with app.app_context():
        # Importurile sunt plasate aici pentru a evita importurile circulare
        from . import routes, models, auth, ai, payments
        db.create_all()

        # Înregistrare blueprint-uri
        app.register_blueprint(auth.auth_bp, url_prefix='/auth')
        app.register_blueprint(routes.routes_bp)
        app.register_blueprint(payments.payments_bp, url_prefix='/payments')

    return app
