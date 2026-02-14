from flask import Flask, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect, CSRFError

from extensions import bcrypt
from database.model.base import db


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "dlajwasdhdddqwf98fg9f23803f"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Extensions
    bcrypt.init_app(app)
    db.init_app(app)
    csrf = CSRFProtect(app)

    # DB init
    with app.app_context():
        db.create_all()

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
    app.run(port=4000, debug=True)
