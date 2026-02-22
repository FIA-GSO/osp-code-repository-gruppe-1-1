from database.model.base import db
from database.model.accountModel import AccountModel
from extensions import bcrypt


def test_login_page_loads(client):
    res = client.get("/login")
    assert res.status_code == 200


def test_register_page_loads(client):
    res = client.get("/register_account")
    assert res.status_code == 200


def test_create_account_invalid_domain(client):
    res = client.post("/create_account", data={
        "email": "bad@gmail.com",
        "password": "test123",
        "first_name": "Max",
        "last_name": "Mustermann",
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"@gso.schule.koeln" in res.data


def test_login_success(client, app):
    with app.app_context():
        hashed = bcrypt.generate_password_hash("test123").decode("utf-8")
        acc = AccountModel(
            email="ok@gso.schule.koeln",
            secret=hashed,
            first_name="A",
            last_name="B",
            role="USER",
            is_active=True,
            email_verified=False,
        )
        db.session.add(acc)
        db.session.commit()

    res = client.post("/login_user", data={
        "email": "ok@gso.schule.koeln",
        "password": "test123",
    })
    assert res.status_code == 302  # redirect zur startseite


def test_login_fail_wrong_password(client, app):
    with app.app_context():
        hashed = bcrypt.generate_password_hash("correct").decode("utf-8")
        acc = AccountModel(
            email="user@gso.schule.koeln",
            secret=hashed,
            first_name="A",
            last_name="B",
            role="USER",
            is_active=True,
            email_verified=False,
        )
        db.session.add(acc)
        db.session.commit()

    res = client.post("/login_user", data={
        "email": "user@gso.schule.koeln",
        "password": "wrong",
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"falsch" in res.data or b"E-Mail" in res.data


def test_logout_redirects(client, app):
    res = client.get("/logout")
    assert res.status_code == 302