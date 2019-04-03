from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"
    hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(75), nullable=False)
    location = db.Column(db.String(100),nullable = True)
    education = db.Column(db.String(100),nullable = True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    bio = db.Column(db.Text(),nullable = True)
    id = db.Column(db.Integer(), primary_key=True)
    image = db.Column(db.String(500),nullable = True)

    def __repr__(self):
        return f"User({self.id}, {self.email})"

    @classmethod
    def new_member(cls, email, password, first_name, last_name):
        if cls.query.filter_by(email=email).one_or_none() is not None:
            return None
        u = cls(email=email, hash=password, first_name=first_name, last_name=last_name)
        db.session.add(u)
        db.session.commit()
        return u

    @classmethod
    def view_members(cls):
        return cls.query.all()

    @classmethod
    def check_password(cls, email, hpassword):
        # todo hash password before passing
        u = cls.query.filter_by(email=email).first()
        if hpassword == u.hash:
            return True
        else:
            return False

class Jobs (db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,nullable = False)
    updated_at = db.Column(db.DateTime,nullable = False)
    title = db.Column(db.String(255), nullable=False)
    salary = db.Column(db.Numeric, nullable=False)
    description = db.Column(db.Text, nullable = False)
    parent_skill = db.Column(db.String(255), nullable = False)

class Skills (db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,nullable = False)
    updated_at = db.Column(db.DateTime,nullable = False)
    title = db.Column(db.String(255), nullable=False)
    # description is nullable
    description = db.Column(db.Text, nullable = True)
    # check if parent skill can be null
    parent_skill = db.Column(db.String(255), nullable = True)
    importance = db.Column(db.Float, nullable = False)



