from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.utils.decorators import student_required
from backend.models.student import Student
from backend.models.job import Job
from backend.models.application import Application
from backend.app import db

student_bp = Blueprint('student', __name__)

@student_bp.route('/jobs')
@login_required
@student_required
def get_jobs():
    jobs = Job.query.filter_by(job_status="approved").all()

    return jsonify([
        {
            "id": j.id,
            "title": j.job_title,
            "company": j.company.company_name,
            "location": j.job_location,
            "salary": j.job_salary
        } for j in jobs
    ])

@student_bp.route('/search')
@login_required
@student_required
def search_jobs():
    q = request.args.get('q')

    jobs = Job.query.filter(
        Job.job_status == "approved",
        Job.job_title.ilike(f"%{q}%")
    ).all()

    return jsonify([
        {
            "id": j.id,
            "title": j.job_title,
            "company": j.company.company_name
        } for j in jobs
    ])

@student_bp.route('/apply/<int:job_id>', methods=['POST'])
@login_required
@student_required
def apply_job(job_id):
    student = Student.query.filter_by(user_id=current_user.id).first()

    # prevent duplicate application
    existing = Application.query.filter_by(
        student_id=student.id,
        job_id=job_id
    ).first()

    if existing:
        return jsonify({"message": "Already applied"}), 400

    app = Application(
        student_id=student.id,
        job_id=job_id,
        application_status='applied'
    )

    db.session.add(app)
    db.session.commit()

    return jsonify({"message": "Applied successfully"})

@student_bp.route('/applications')
@login_required
@student_required
def my_applications():
    student = Student.query.filter_by(user_id=current_user.id).first()

    apps = Application.query.filter_by(student_id=student.id).all()

    result = []
    for a in apps:
        result.append({
            "job": a.job.job_title,
            "company": a.job.company.company_name,
            "status": a.application_status
        })

    return jsonify(result)

@student_bp.route('/update_profile', methods=['POST'])
@login_required
@student_required
def update_profile():
    data = request.get_json()

    student = Student.query.filter_by(user_id=current_user.id).first()

    student.student_education = data.get('education')
    student.student_skills = data.get('skills')
    student.student_resume = data.get('resume')

    db.session.commit()

    return jsonify({"message": "Profile updated"})
