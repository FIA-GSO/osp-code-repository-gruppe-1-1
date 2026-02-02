from sqlalchemy.orm import Session
from database.model.accountModel import AccountModel
from database.model.base import db


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
