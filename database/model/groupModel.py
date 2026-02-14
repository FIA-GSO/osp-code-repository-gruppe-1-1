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
    topic = db.Column(db.String(255), nullable=False)
    place = db.Column(db.String(255), nullable=False, default="Online")
    appointment = db.Column(db.Integer, nullable=False, comment="Unix timestamp (seconds)")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


def save_group(group: GroupModel) -> GroupModel:
    db.session.add(group)
    db.session.commit()
    db.session.refresh(group)
    return group


def edit_group(group_id: int, data: dict) -> None:
    group = db.session.get(GroupModel, group_id)
    if not group:
        return
    for key, value in data.items():
        setattr(group, key, value)
    db.session.commit()


def delete_group(group_id: int) -> None:
    group = db.session.get(GroupModel, group_id)
    if not group:
        return
    db.session.delete(group)
    db.session.commit()
