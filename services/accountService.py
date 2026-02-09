from database.model.accountModel import AccountModel, create_account as model_create_account, get_account_by_email
from flask import request, session, flash, redirect, url_for


def create_account():

    form_data = get_form_data()

    account = AccountModel(
        email=form_data['email'],
        secret=form_data['secret'],
        first_name=form_data['first_name'],
        last_name=form_data['last_name'],
        role="USER",
    )

    model_create_account(account)
    session["account"] = True

    return

def login_user():
    form_data = get_form_data()
    account = get_account_by_email(form_data['email'])

    errors = []
    if account is None or account.secret != form_data['secret']:
        errors.append("User nicht gefunden!")

    if errors:
        for e in errors:
            flash(e, "danger")
    else:
        flash('Erfolgreich eingeloggt!', "success")
        session["account"] = True

    return redirect(url_for("index"))

def get_form_data():
    return {
        'email': (request.form.get("email") or "").strip(),
        'secret': (request.form.get("password") or "").strip(),
        'first_name': (request.form.get("first_name") or "").strip(),
        'last_name': (request.form.get("last_name") or "").strip(),
    }