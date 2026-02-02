from sqlalchemy.orm import Session

from database.model.base import db
from sqlalchemy import ForeignKey
from datetime import datetime

class GroupModel(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(ForeignKey("account.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    klasse = db.Column(db.String(255), nullable=True)
    grade = db.Column(db.String(255), nullable=True)
    subject = db.Column(db.String(255), nullable=True)
    topic = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


def create_group(account):
    with Session(db.engine) as session:
        session.add(account)
        session.commit()
        session.refresh(account)
        return account


def edit_group(group_id, dict):
    with Session(db.engine) as session:
        account = GroupModel.query.get(group_id)
        account.update(dict)
        session.commit()


def delete_group(group_id):
    with Session(db.engine) as session:
        account = GroupModel.query.get(group_id)
        session.delete(account)
        session.commit()