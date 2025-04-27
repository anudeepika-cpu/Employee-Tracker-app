from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  # Import UserMixin from flask_login

db = SQLAlchemy()

class User(db.Model, UserMixin):  # Inherit from UserMixin to provide the necessary methods
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    logs = db.relationship('PunchLog', backref='user', lazy=True)

class PunchLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    punch_in = db.Column(db.DateTime, nullable=True)
    punch_out = db.Column(db.DateTime, nullable=True)
    hours_worked = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='unique_punch_for_user_per_day'),
    )
