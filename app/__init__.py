from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "main.login"  # type: ignore[assignment]
login_manager.login_message = "Bitte zuerst einloggen."
login_manager.login_message_category = "warning"


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)

    from app.logging_config import configure_logging

    configure_logging(app)

    from app.models import User

    @login_manager.user_loader  # type: ignore[misc]
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))

    from app import routes

    app.register_blueprint(routes.bp)
    with app.app_context():
        db.create_all()
    return app
