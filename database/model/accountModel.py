from sqlalchemy import CheckConstraint
from datetime import datetime

from sqlalchemy.orm import Session

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
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


def create_account(account):
    with Session(db.engine) as session:
        session.add(account)
        session.commit()
        session.refresh(account)
        return account


def edit_account(account_id, dict):
    with Session(db.engine) as session:
        account = AccountModel.query.get(account_id)
        account.update(dict)
        session.commit()


def delete_account(account_id):
    with Session(db.engine) as session:
        account = AccountModel.query.get(account_id)
        session.delete(account)
        session.commit()