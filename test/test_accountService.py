from unittest import TestCase

from sqlalchemy.orm import Session, sessionmaker

from database.accountService import *

from database.model.accountModel import AccountModel


class TestAccountService(TestCase):
    def test_create_account(self):
        account = AccountModel(
            email="<EMAIL>",
            secret="secret",
            first_name="first",
            last_name="last",
            role="USER",
        )
        new_account = create_account(account)
        print(new_account.id)


    def test_edit_account(self):
        self.fail()

    def test_delete_account(self):
        self.fail()
