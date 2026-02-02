from database.model.accountmodel import AccountModel


class AccountService:
    def __init__(self, db):
        self.db = db

    def createAccount(self, account):
        with self.db.session as session:
            session.add(account)
            session.commit()

    def editAccount(self, accountId, dict):
        with self.db.session as session:
            account = AccountModel.query.get(accountId)
            account.update(dict)
            session.commit()

    def deleteAccount(self, accountId):
        with self.db.session as session:
            account = AccountModel.query.get(accountId)
            session.delete(account)
            session.commit()
