from database.model.base import db
from sqlalchemy import ForeignKey
from datetime import datetime


class GroupMemberModel(db.Model):
    __tablename__ = 'group_member'

    group_id = db.Column(
        db.Integer,
        ForeignKey("group.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    account_id = db.Column(
        db.Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )

    accepted = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

