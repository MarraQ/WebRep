from datetime import datetime

import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    hpasw = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.now())
    ads = orm.relationship("Ad", back_populates='user')

    def set_password(self, password):
        self.hpasw = generate_password_hash(password)

    def check_password(self, password):
        print(self.hpasw, password)
        return check_password_hash(self.hpasw, password)
