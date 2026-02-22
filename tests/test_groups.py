from datetime import datetime, timedelta

from database.model.base import db
from database.model.groupModel import GroupModel
from database.model.groupMemberModel import GroupMemberModel
from database.model.accountModel import AccountModel


def _create_group(owner_id: int) -> GroupModel:
    appointment_ts = int((datetime.now() + timedelta(days=1)).timestamp())
    g = GroupModel(
        owner=owner_id,
        name="Testgruppe",
        klasse="FIA3F",
        grade="Mittelstufe",
        subject="FU1",
        topic="Flask",
        appointment=appointment_ts,
        place="Online",
        is_active=True,
    )
    db.session.add(g)
    db.session.commit()
    db.session.refresh(g)
    return g


def _ensure_membership(account_id: int, group_id: int, accepted: bool = True):
    existing = GroupMemberModel.query.filter_by(group_id=group_id, account_id=account_id).first()
    if not existing:
        db.session.add(
            GroupMemberModel(group_id=group_id, account_id=account_id, accepted=accepted)
        )
        db.session.commit()


def test_create_group_requires_login(client):
    res = client.post("/groups/create")
    assert res.status_code == 302
    assert "/login" in res.headers.get("Location", "")


def test_create_group_success(logged_in_client):
    res = logged_in_client.post("/groups/create", data={
        "name": "Meine Gruppe",
        "klasse": "FIA3F",
        "stufe": "Mittelstufe",
        "fach": "FU1",
        "thema": "FLASK",
        "appointment": "2099-01-01T10:00",
        "place": "Online",
    })
    assert res.status_code == 302


def test_join_group(logged_in_client, app):
    with app.app_context():
        acc = AccountModel.query.first()
        group = _create_group(acc.id)
        group_id = group.id

    res = logged_in_client.post(f"/groups/{group_id}/join")
    assert res.status_code == 302


def test_group_overview_requires_membership(logged_in_client, app):
    with app.app_context():
        acc = AccountModel.query.first()
        group = _create_group(acc.id)
        group_id = group.id

    res = logged_in_client.get(f"/groups/{group_id}", follow_redirects=True)
    assert res.status_code == 200

    assert b"login" in res.data.lower() or b"mitglied" in res.data.lower() or b"gruppe" in res.data.lower()


def test_leave_group(logged_in_client, app):
    with app.app_context():
        acc = AccountModel.query.first()
        group = _create_group(acc.id)
        group_id = group.id

        _ensure_membership(acc.id, group_id, accepted=True)

    res = logged_in_client.post(f"/groups/{group_id}/leave")
    assert res.status_code == 302


def test_send_message_requires_membership(logged_in_client, app):
    with app.app_context():
        acc = AccountModel.query.first()
        group = _create_group(acc.id)
        group_id = group.id

    res = logged_in_client.post(
        f"/groups/{group_id}/messages",
        data={"message": "Hi"},
        follow_redirects=True
    )
    assert res.status_code == 200
    assert b"login" in res.data.lower() or b"mitglied" in res.data.lower() or b"gruppe" in res.data.lower()


def test_send_message_success(logged_in_client, app):
    with app.app_context():
        acc = AccountModel.query.first()
        group = _create_group(acc.id)
        group_id = group.id

        _ensure_membership(acc.id, group_id, accepted=True)

    res = logged_in_client.post(
        f"/groups/{group_id}/messages",
        data={"message": "Hallo"},
        follow_redirects=False
    )
    assert res.status_code == 302


def test_profanity_blocked(logged_in_client, app):
    with app.app_context():
        acc = AccountModel.query.first()
        group = _create_group(acc.id)
        group_id = group.id

        _ensure_membership(acc.id, group_id, accepted=True)

    res = logged_in_client.post(
        f"/groups/{group_id}/messages",
        data={"message": "fuck"},
        follow_redirects=True
    )

    assert res.status_code == 200
    page = res.data.lower()
    assert (b"schimpf" in page)
