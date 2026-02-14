from flask import request, render_template, session, redirect, url_for, flash
from sqlalchemy import or_

from database.model.base import db
from database.model.accountModel import AccountModel

from blueprints.admin import admin_bp
from blueprints.common import admin_required
# @todo: Make user admin button
# @todo: gruppen löschen


@admin_bp.route("/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    account_id = session.get("account_id")
    current_user = db.session.get(AccountModel, account_id)
    current_user_email = current_user.email.strip() if current_user and current_user.email else "Unbekannt"

    query = (request.args.get("q") or "").strip()
    if query:
        users = (
            AccountModel.query
            .filter(or_(
                AccountModel.first_name.like(f"%{query}%"),
                AccountModel.email.like(f"%{query}%"),
                AccountModel.last_name.like(f"%{query}%"),
            ))
            .all()
        )
    else:
        users = AccountModel.query.all()

    return render_template(
        "dashboard.html",
        users=users,
        current_user_email=current_user_email,
        query=query,
    )


@admin_bp.route("/account/<int:user_id>/deactivate", methods=["GET", "POST"])
@admin_required
def account_deactivate(user_id):
    account = db.session.get(AccountModel, user_id)

    if not account:
        flash("Nutzer nicht gefunden.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    account.is_active = False
    db.session.commit()

    flash("Nutzer wurde deaktiviert.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/account/<int:user_id>/activate", methods=["GET", "POST"])
@admin_required
def account_activate(user_id):
    account = db.session.get(AccountModel, user_id)

    if not account:
        flash("Nutzer nicht gefunden.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    account.is_active = True
    db.session.commit()

    flash("Nutzer wurde aktiviert.", "success")
    return redirect(url_for("admin.admin_dashboard"))
