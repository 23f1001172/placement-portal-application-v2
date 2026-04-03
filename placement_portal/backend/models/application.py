from backend.app import db
from datetime import datetime

class Application(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable = False)

    application_date = db.Column(db.DateTime, default = datetime.utcnow)
    application_status = db.Column(db.String(50), default = 'applied') # 'applied', 'accepted', 'rejected'

    placement = db.relationship('Placement', backref = 'application', uselist = False)