from database.model.base import db
from sqlalchemy import ForeignKey, CheckConstraint
from datetime import datetime

class GroupActionModel(db.Model):
    __tablename__ = 'group_action'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(ForeignKey("group.id"), nullable=False)
    account_id = db.Column(ForeignKey("account.id"), nullable=False)
    type = db.Column(db.String(255), CheckConstraint("type in ('ACTION', 'MESSAGE')"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
