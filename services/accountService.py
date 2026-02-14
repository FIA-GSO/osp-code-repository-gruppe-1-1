from __future__ import annotations

from typing import Tuple, List
from flask import session

from utils.profanity import validate_text_fields
from utils.profanity_config import ACCOUNT_TEXT_FIELDS

from extensions import bcrypt
from database.model.accountModel import AccountModel, create_account, get_account_by_email


ALLOWED_EMAIL_DOMAIN = "@gso.schule.koeln"


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def service_create_account(form_data) -> tuple[bool, list[str]]:
    errors: List[str] = []
    ok, errors = validate_text_fields(form_data, ACCOUNT_TEXT_FIELDS)
    if not ok:
        return False, errors

    email = _norm_email(form_data.get("email"))
    password = (form_data.get("password") or "").strip()
    first_name = (form_data.get("first_name") or "").strip()
    last_name = (form_data.get("last_name") or "").strip()

    # Validation
    if not email:
        errors.append("E-Mail fehlt.")
    if not password:
        errors.append("Passwort fehlt.")
    if not first_name:
        errors.append("Vorname fehlt.")
    if not last_name:
        errors.append("Nachname fehlt.")

    if email and not email.endswith(ALLOWED_EMAIL_DOMAIN):
        errors.append(f"Bitte nutze eine {ALLOWED_EMAIL_DOMAIN}-Adresse.")

    if errors:
        return False, errors

    existing = get_account_by_email(email)
    if existing:
        errors.append("Diese E-Mail ist bereits registriert.")
        return False, errors

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")

    account = AccountModel(
        email=email,
        secret=hashed,
        first_name=first_name,
        last_name=last_name,
        role="USER",
        is_active=True,
        email_verified=False,
    )

    create_account(account)
    return True, []


def service_login_user(form_data) -> tuple[bool, list[str]]:
    errors: List[str] = []

    email = _norm_email(form_data.get("email"))
    password = (form_data.get("password") or "").strip()

    if not email or not password:
        return False, ["Bitte E-Mail und Passwort angeben."]

    account = get_account_by_email(email)
    if not account:
        return False, ["E-Mail oder Passwort ist falsch."]

    # Account Status Checks
    if not getattr(account, "is_active", True):
        return False, ["Dein Account ist deaktiviert."]

    if not bcrypt.check_password_hash(account.secret, password):
        return False, ["E-Mail oder Passwort ist falsch."]

    session["account_id"] = account.id
    return True, []
