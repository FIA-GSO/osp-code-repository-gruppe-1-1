from main import db
from sqlalchemy import ForeignKey
from datetime import datetime

class AccountModel(db.Model):
    __tablename__ = 'group_member'

    group_id = db.Column(ForeignKey("group.id"), primary_key=True, nullable=False)
    account_id = db.Column(ForeignKey("account.id"), primary_key=True, nullable=False)
    accepted = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
