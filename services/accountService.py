from database.model.accountModel import AccountModel, create_account as model_create_account, get_account_by_email
from flask import request, session, flash, redirect, url_for


def create_account():
    form_data = get_form_data()
    from main import bcrypt

    errors = []
    try:
        validate_account_form(form_data)
    except Exception as e:
        errors.append(str(e))

    if errors:
        return errors

    account = AccountModel(
        email=form_data['email'],
        secret=bcrypt.generate_password_hash(form_data['password']).decode('utf-8'),
        first_name=form_data['first_name'],
        last_name=form_data['last_name'],
        role="USER",
    )

    model_create_account(account)
    session["account_id"] = account.id

    return


def login_user():
    from main import bcrypt
    form_data = get_form_data()
    account = get_account_by_email(form_data['email'])

    errors = []
    if account is None or not bcrypt.check_password_hash(account.secret, form_data["password"]):
        errors.append("User nicht gefunden!")

    if errors:
        for e in errors:
            flash(e, "danger")
    else:
        flash('Erfolgreich eingeloggt!', "success")
        session["account_id"] = account.id
        return redirect(url_for("index"))


def get_form_data():
    return {
        'email': (request.form.get("email") or "").strip(),
        'password': (request.form.get("password") or "").strip(),
        'first_name': (request.form.get("first_name") or "").strip(),
        'last_name': (request.form.get("last_name") or "").strip(),
    }


def validate_account_form(form_data: dict) -> None:

    required_fields = [
        "email",
        "password",
        "first_name",
        "last_name",
    ]

    # Pflichtfelder
    for field in required_fields:
        value = form_data.get(field)

        if value is None or not str(value).strip():
            raise Exception(f"Feld '{field}' fehlt oder ist leer.")

    email = form_data["email"].strip()

    if not email.endswith('@gso.schule.koeln'):
        raise Exception(f"E-Mail muss mit @gso.schule.koeln enden.")

    # Unique
    existing_account = get_account_by_email(email)
    if existing_account is not None:
        raise Exception("Diese E-Mail-Adresse ist bereits registriert.")
