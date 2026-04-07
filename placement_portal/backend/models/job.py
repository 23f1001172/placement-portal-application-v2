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
    job_status = db.Column(db.String(50), default='pending')
    job_spots = db.Column(db.Integer, default=1)  

    job_min_cgpa = db.Column(db.Float, default=0.0)
    job_required_branch = db.Column(db.String(100)) 
    job_required_batch = db.Column(db.String(50)) 
    job_deadline = db.Column(db.DateTime)

    applications = db.relationship('Application', backref = 'job', lazy = True) 