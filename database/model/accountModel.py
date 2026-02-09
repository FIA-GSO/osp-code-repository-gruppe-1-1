from sqlalchemy import CheckConstraint
from datetime import datetime
from database.model.base import db


class AccountModel(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    secret = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), CheckConstraint("role in ('USER', 'ADMIN')"), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


def create_account(account):
    db.session.add(account)
    db.session.commit()
    db.session.refresh(account)
    return account


def edit_account(account_id, data: dict):
    account = db.session.get(AccountModel, account_id)
    if not account:
        return
    for k, v in data.items():
        setattr(account, k, v)
    db.session.commit()


def delete_account(account_id):
    account = db.session.get(AccountModel, account_id)
    if not account:
        return
    db.session.delete(account)
    db.session.commit()


def get_account_by_email(email) -> AccountModel:
    return AccountModel.query.filter_by(email=(email or "").strip().lower()).first()
