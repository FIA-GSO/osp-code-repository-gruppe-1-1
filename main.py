from dotenv import load_dotenv
import os

from flask import Flask, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_mail import Mail

from extensions import bcrypt
from database.model.base import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from config import Config

mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    db.init_app(app)
    csrf = CSRFProtect(app)

    with app.app_context():
        db.create_all()

    mail.init_app(app)

    # CSRF Fehler global
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Sicherheitscheck fehlgeschlagen (CSRF). Bitte Seite neu laden und erneut versuchen.", "danger")
        return redirect(url_for("main.index"))

    # Blueprints registrieren
    from blueprints.main import main_bp
    from blueprints.auth import auth_bp
    from blueprints.groups import groups_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(admin_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=4000, debug=False)
