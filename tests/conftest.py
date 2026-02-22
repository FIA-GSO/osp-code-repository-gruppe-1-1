import os
import sys
import pytest
from flask import Flask, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect, CSRFError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extensions import bcrypt
from database.model.base import db
from database.model.accountModel import AccountModel


def _build_test_app():
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    app = Flask(
        __name__,
        template_folder=os.path.join(ROOT, "templates"),
        static_folder=os.path.join(ROOT, "static"),
    )

    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False
    })

    bcrypt.init_app(app)
    db.init_app(app)
    CSRFProtect(app)

    with app.app_context():
        db.create_all()

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash("Sicherheitscheck fehlgeschlagen (CSRF). Bitte Seite neu laden und erneut versuchen.", "danger")
        return redirect(url_for("main.index"))

    from blueprints.main import main_bp
    from blueprints.auth import auth_bp
    from blueprints.groups import groups_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(admin_bp)

    return app


@pytest.fixture
def app():
    app = _build_test_app()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def create_account(email="user@gso.schule.koeln", password="test123", role="USER", first_name="Max",
                   last_name="Mustermann"):
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    acc = AccountModel(
        email=email,
        secret=hashed,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=True,
        email_verified=False,
    )
    db.session.add(acc)
    db.session.commit()
    db.session.refresh(acc)
    return acc


@pytest.fixture
def logged_in_client(app, client):
    with app.app_context():
        create_account()

    client.post("/login_user", data={
        "email": "user@gso.schule.koeln",
        "password": "test123",
    })
    return client
