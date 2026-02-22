from database.model.base import db
from database.model.accountModel import AccountModel
from extensions import bcrypt


def test_admin_requires_admin(logged_in_client):
    res = logged_in_client.get("/admin")
    assert res.status_code == 302  # redirect (keine berechtigung)


def test_admin_access_as_admin(logged_in_client, app):
    with app.app_context():
        me = AccountModel.query.first()
        me.role = "ADMIN"
        db.session.commit()

    res = logged_in_client.get("/admin")
    assert res.status_code == 200


def test_deactivate_activate_user_as_admin(logged_in_client, app):
    with app.app_context():
        me = AccountModel.query.first()
        me.role = "ADMIN"

        other = AccountModel(
            email="other@gso.schule.koeln",
            secret=bcrypt.generate_password_hash("x").decode("utf-8"),
            first_name="O",
            last_name="T",
            role="USER",
            is_active=True,
            email_verified=False,
        )
        db.session.add(other)
        db.session.commit()
        other_id = other.id

    res1 = logged_in_client.post(f"/account/{other_id}/deactivate")
    assert res1.status_code == 302

    res2 = logged_in_client.post(f"/account/{other_id}/activate")
    assert res2.status_code == 302