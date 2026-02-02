from database.model.base import db
from sqlalchemy import ForeignKey
from datetime import datetime

class GroupModel(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(ForeignKey("account.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    klasse = db.Column(db.String(255), nullable=False)
    grade = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
