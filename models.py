from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    topic = db.Column(db.String(100), nullable=False)

    completed = db.Column(db.Boolean, default=False)

from datetime import datetime

class ResumeReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    score = db.Column(db.Integer)

    ats_score = db.Column(db.Integer)

    strength = db.Column(db.String(50))

    filename = db.Column(db.String(200))

    upload_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )