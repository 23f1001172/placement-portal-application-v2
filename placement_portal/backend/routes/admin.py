from flask import Blueprint, jsonify, request
from flask_login import login_required
from backend.utils.decorators import admin_required
from backend.models.user import User
from backend.models.company import Company
from backend.models.student import Student
from backend.models.job import Job
from backend.models.application import Application
from backend.app import db

admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    return jsonify({
        "students": total_students,
        "companies": total_companies,
        "jobs": total_jobs,
        "applications": total_applications
    })

@admin_bp.route('/companies')
@login_required
@admin_required
def get_companies():
    companies = Company.query.all()

    result = []
    for c in companies:
        result.append({
            "id": c.id,
            "name": c.company_name,
            "industry": c.company_industry,
            "approved": c.user.is_approved
        })

    return jsonify(result)

@admin_bp.route('/approve_company/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_company(id):
    company = Company.query.get(id)

    if not company:
        return jsonify({"message": "Company not found"}), 404

    company.user.is_approved = True
    db.session.commit()

    return jsonify({"message": "Company approved"})

@admin_bp.route('/remove_company/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def remove_company(id):
    company = Company.query.get(id)

    if not company:
        return jsonify({"message": "Company not found"}), 404

    db.session.delete(company)
    db.session.commit()

    return jsonify({"message": "Company removed"})

@admin_bp.route('/approve_job/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_job(id):
    job = Job.query.get(id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.job_status = "approved"
    db.session.commit()

    return jsonify({"message": "Job approved"})

@admin_bp.route('/jobs')
@login_required
@admin_required
def get_jobs():
    jobs = Job.query.all()

    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.job_title,
            "company": j.company.company_name,
            "status": j.job_status
        })

    return jsonify(result)

@admin_bp.route('/search_companies')
@login_required
@admin_required
def search_companies():
    query = request.args.get('q')

    companies = Company.query.filter(
        Company.company_name.ilike(f"%{query}%")
    ).all()

    return jsonify([
        {"id": c.id, "name": c.company_name}
        for c in companies
    ])

@admin_bp.route('/blacklist_user/<int:id>', methods=['POST'])
@login_required
@admin_required
def blacklist_user(id):
    user = User.query.get(id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    user.is_blacklisted = True
    db.session.commit()

    return jsonify({"message": "User blacklisted"})
