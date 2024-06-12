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
    app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    with app.app_context():
        # Importurile sunt plasate aici pentru a evita importurile circulare
        from . import routes, models, auth, ai, payments
        from .ai import update_property_clusters  # Importă funcția de actualizare a clusterelor

        db.create_all()

        # Actualizarea proprietăților cu clusterele calculate
        update_property_clusters()

        # Înregistrare blueprint-uri
        app.register_blueprint(auth.auth_bp, url_prefix='/auth')
        app.register_blueprint(routes.routes_bp)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return models.RevokedToken.is_jti_blacklisted(jti)

    return app
