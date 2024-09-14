from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///your_database.db"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from .routes import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # type: ignore
