from flask import request, session, redirect, url_for, render_template, flash
from services.accountService import service_create_account, service_login_user
from blueprints.auth import auth_bp


@auth_bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@auth_bp.route("/login_user", methods=["POST"])
def login_user():
    ok, errors = service_login_user(request.form)
    for e in errors:
        flash(e, "danger")
    if ok:
        flash("Erfolgreich eingeloggt.", "success")
        return redirect(url_for("main.index"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.pop("account_id", None)
    flash("Du wurdest ausgeloggt.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/register_account", methods=["GET"])
def register_account():
    return render_template("register.html")


@auth_bp.route("/create_account", methods=["POST"])
def create_account():
    ok, errors = service_create_account(request.form)
    for e in errors:
        flash(e, "danger")
    if ok:
        flash("Account erstellt. Bitte einloggen.", "success")
        return redirect(url_for("auth.login"))
    return redirect(url_for("auth.register_account"))
