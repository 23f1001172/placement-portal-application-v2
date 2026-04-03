from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.utils.decorators import company_required
from backend.models.company import Company
from backend.models.job import Job
from backend.models.application import Application
from backend.models.student import Student
from backend.app import db

company_bp = Blueprint('company', __name__)

@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    company = Company.query.filter_by(user_id=current_user.id).first()

    jobs = Job.query.filter_by(company_id=company.id).count()
    applications = Application.query.join(Job).filter(Job.company_id == company.id).count()

    return jsonify({
        "jobs": jobs,
        "applications": applications
    })

@company_bp.route('/create_job', methods=['POST'])
@login_required
@company_required
def create_job():
    data = request.get_json()

    company = Company.query.filter_by(user_id=current_user.id).first()

    job = Job(
        company_id=company.id,
        job_title=data.get('title'),
        job_description=data.get('description'),
        job_location=data.get('location'),
        job_salary=data.get('salary'),
        job_type=data.get('type'),
        job_requirements=data.get('requirements'),
        job_status='pending'
    )

    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created, waiting for admin approval"})

@company_bp.route('/jobs')
@login_required
@company_required
def get_jobs():
    company = Company.query.filter_by(user_id=current_user.id).first()
    jobs = Job.query.filter_by(company_id=company.id).all()

    return jsonify([
        {
            "id": j.id,
            "title": j.job_title,
            "status": j.job_status
        } for j in jobs
    ])

@company_bp.route('/applications/<int:job_id>')
@login_required
@company_required
def get_applications(job_id):
    applications = Application.query.filter_by(job_id=job_id).all()

    result = []
    for app in applications:
        student = Student.query.get(app.student_id)

        result.append({
            "application_id": app.id,
            "student_id": student.id,
            "skills": student.student_skills,
            "status": app.application_status
        })

    return jsonify(result)

@company_bp.route('/update_application/<int:id>', methods=['POST'])
@login_required
@company_required
def update_application(id):
    data = request.get_json()

    app = Application.query.get(id)

    if not app:
        return jsonify({"message": "Application not found"}), 404

    app.application_status = data.get('status')

    db.session.commit()

    return jsonify({"message": "Status updated"})

@company_bp.route('/close_job/<int:id>', methods=['POST'])
@login_required
@company_required
def close_job(id):
    job = Job.query.get(id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.job_status = "closed"
    db.session.commit()

    return jsonify({"message": "Job closed"})
