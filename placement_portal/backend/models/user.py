from backend.app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20)) # 'admin', 'company', 'student'

    is_approved = db.Column(db.Boolean, default = False)
    is_rejected = db.Column(db.Boolean, default = False)
    is_blacklisted = db.Column(db.Boolean, default = False)

    company = db.relationship('Company', backref = 'user', uselist = False)
    student = db.relationship('Student', backref = 'user', uselist = False)