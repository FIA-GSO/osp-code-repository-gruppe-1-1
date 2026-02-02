from sqlalchemy.orm import Session
from database.model.accountmodel import AccountModel


class AccountService:
    def __init__(self, engine):
        self.engine = engine

    def create_account(self, account):
        with Session(self.engine) as session:

            session.add(account)
            session.commit()
            session.refresh(account)
            return account

    def edit_account(self, account_id, dict):
        with Session(self.engine) as session:
            account = AccountModel.query.get(account_id)
            account.update(dict)
            session.commit()

    def delete_account(self, account_id):
        with Session(self.engine) as session:
            account = AccountModel.query.get(account_id)
            session.delete(account)
            session.commit()
