# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Integer, nullable=False)

class Attendance(db.Model):
    __tablename__ = 'Attendance'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('Sessions.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    status = db.Column(db.Integer)

class Class(db.Model):
    __tablename__ = 'Classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    no_location = db.Column(db.Integer, nullable=False)

class Enrollment(db.Model):
    __tablename__ = 'Enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.id'), nullable=False)

class Session(db.Model):
    __tablename__ = 'Sessions'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.id'))
    session_start_date = db.Column(db.String(50))
    session_end_date = db.Column(db.String(50))
    bypass_code = db.Column(db.String(50))
