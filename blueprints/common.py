import time
from functools import wraps
from flask import session, flash, redirect, url_for
from database.model.base import db
from database.model.accountModel import AccountModel
from database.model.groupMemberModel import GroupMemberModel

ALLOWED_GRADES = {"Unterstufe", "Mittelstufe", "Oberstufe"}
MAX_GROUP_MEMBERS = 20


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("account_id") is None:
            flash("Bitte zuerst einloggen.", "danger")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("account_id") is None:
            flash("Bitte zuerst einloggen.", "danger")
            return redirect(url_for("auth.login"))

        acc = db.session.get(AccountModel, session["account_id"])
        if not acc or acc.role != "ADMIN":
            flash("Keine Berechtigung.", "danger")
            return redirect(url_for("main.index"))

        return view(*args, **kwargs)
    return wrapped


def require_membership(group_id: int):
    account_id = session.get("account_id")
    membership = GroupMemberModel.query.filter_by(
        group_id=group_id,
        account_id=account_id,
        accepted=True
    ).first()
    return membership is not None
