from backend.app import db
from datetime import datetime

class Job(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)

    job_title = db.Column(db.String(100), nullable = False)
    job_description = db.Column(db.Text)
    job_location = db.Column(db.String(100))
    job_salary = db.Column(db.String(50))
    job_type = db.Column(db.String(50)) # 'full-time', 'part-time', 'internship'
    job_requirements = db.Column(db.Text)
    job_posted_date = db.Column(db.DateTime, default = datetime.utcnow)

    applications = db.relationship('Application', backref = 'job', lazy = True) 