from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import database.model.accountModel
import database.model.groupModel
import database.model.groupMemberModel
import database.model.groupActionModel

class BaseModel(db.Model):
    __abstract__ = True