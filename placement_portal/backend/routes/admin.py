from flask import Blueprint, jsonify, request
from flask_login import login_required
from backend.utils.decorators import admin_required
from backend.models.user import User
from backend.models.company import Company
from backend.models.student import Student
from backend.models.job import Job
from backend.models.application import Application
from backend.models.placement import Placement
from backend.app import db, cache
from backend.tasks import send_email


admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    
    total_applications = Application.query.count()
    total_students_selected = Placement.query.count()
    total_drives_created = Job.query.count()
    total_drives_accepted = Job.query.filter_by(job_status='approved').count()
    total_approved_companies = Company.query.join(User).filter(User.is_approved == True).count()
    total_approved_students = Student.query.join(User).filter(User.is_approved == True).count()

    return jsonify({
        "applications": total_applications,
        "students_selected": total_students_selected,
        "drives_created": total_drives_created,
        "drives_accepted": total_drives_accepted,
        "approved_companies": total_approved_companies,
        "approved_students": total_approved_students
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
            "user_id": c.user.id,
            "name": c.company_name or c.user.name,
            "email": c.company_email or c.user.email,
            "industry": c.company_industry or "Pending setup",
            "description": c.company_description or "Not provided",
            "website": c.company_website or "Not provided",
            "location": c.company_location or "Not provided",
            "approved": c.user.is_approved,
            "rejected": c.user.is_rejected,
            "blacklisted": c.user.is_blacklisted
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
    company.user.is_rejected = False
    company.user.is_blacklisted = False
    db.session.commit()

    from backend.app import cache
    cache.clear()

    send_email.delay(company.user.email, "Registration Approved", f"Hello {company.user.name}, your company registration for '{company.company_name}' has been approved.")

    return jsonify({"message": "Company approved"})

@admin_bp.route('/reject_company/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject_company(id):
    company = Company.query.get(id)
    if not company:
        return jsonify({"message": "Company not found"}), 404
    company.user.is_approved = False
    company.user.is_rejected = True
    company.user.is_blacklisted = False
    db.session.commit()
    send_email.delay(company.user.email, "Registration Update", f"Hello {company.user.name}, your company registration was not approved.")
    return jsonify({"message": "Company rejected"})

@admin_bp.route('/students')
@login_required
@admin_required
def get_students():
    students = Student.query.all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "user_id": s.user.id,
            "name": s.user.name,
            "email": s.user.email,
            "roll_number": s.student_roll_number or "Not provided",
            "batch": s.student_batch or "Not provided",
            "department": s.student_department or "Not provided",
            "skills": s.student_skills or "Not provided",
            "education": s.student_education or "Not provided",
            "approved": s.user.is_approved,
            "rejected": s.user.is_rejected,
            "blacklisted": s.user.is_blacklisted,
            "applications": [{
                "job": a.job.job_title,
                "company": a.job.company.company_name,
                "status": a.application_status
            } for a in s.applications]
        })
    return jsonify(result)

@admin_bp.route('/approve_student/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
    student.user.is_approved = True
    student.user.is_rejected = False
    student.user.is_blacklisted = False
    db.session.commit()
    send_email.delay(student.user.email, "Profile Verified", f"Hello {student.user.name}, your student profile has been verified and approved.")
    return jsonify({"message": "Student approved"})

@admin_bp.route('/reject_student/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject_student(id):
    student = Student.query.get(id)
    if not student:
        return jsonify({"message": "Student not found"}), 404
    student.user.is_approved = False
    student.user.is_rejected = True
    student.user.is_blacklisted = False
    db.session.commit()
    send_email.delay(student.user.email, "Profile Update", f"Hello {student.user.name}, your student profile verification was unsuccessful.")
    return jsonify({"message": "Student rejected"})

@admin_bp.route('/approve_job/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_job(id):
    job = Job.query.get(id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.job_status = "approved"
    db.session.commit()

    from backend.app import cache
    cache.clear()

    send_email.delay(job.company.user.email, "Job Drive Approved", f"Hello {job.company.user.name}, your job drive '{job.job_title}' has been approved and is now visible to students.")

    return jsonify({"message": "Job approved"})

@admin_bp.route('/reject_job/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject_job(id):
    job = Job.query.get(id)
    if not job:
        return jsonify({"message": "Job not found"}), 404
    job.job_status = "rejected"
    db.session.commit()
    send_email.delay(job.company.user.email, "Job Drive Update", f"Hello {job.company.user.name}, your job drive '{job.job_title}' was not approved.")
    return jsonify({"message": "Job rejected"})

@admin_bp.route('/blacklist_job/<int:id>', methods=['POST'])
@login_required
@admin_required
def blacklist_job(id):
    job = Job.query.get(id)
    if not job:
        return jsonify({"message": "Job not found"}), 404
    job.job_status = "blacklisted"
    db.session.commit()
    return jsonify({"message": "Job blacklisted"})

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
            "company": j.company.company_name or "N/A",
            "status": j.job_status,
            "spots": j.job_spots or 1,
            "total_applicants": len(j.applications),
            "total_selected": Placement.query.join(Application).filter(Application.job_id == j.id).count()
        })
    return jsonify(result)

@admin_bp.route('/all_applications')
@login_required
@admin_required
def all_applications_detail():
    """All applications across the system, filterable by ?status=selected|shortlisted|interview|applied|rejected"""
    status_filter = request.args.get('status', '')
    query = Application.query
    if status_filter:
        query = query.filter_by(application_status=status_filter)
    apps = query.all()
    return jsonify([
        {
            "application_id": a.id,
            "student_name": a.student.user.name,
            "student_email": a.student.user.email,
            "student_roll": a.student.student_roll_number or "N/A",
            "student_batch": a.student.student_batch or "N/A",
            "student_department": a.student.student_department or "N/A",
            "student_skills": a.student.student_skills or "N/A",
            "student_education": a.student.student_education or "N/A",
            "student_resume": a.student.student_resume or "",
            "job_title": a.job.job_title,
            "company": a.job.company.company_name or "N/A",
            "status": a.application_status
        } for a in apps
    ])




@admin_bp.route('/search_companies')
@login_required
@admin_required
@cache.cached(timeout = 60, query_string = True)
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
    user.is_approved = False
    user.is_rejected = False
    db.session.commit()

    return jsonify({"message": "User blacklisted"})

@admin_bp.route('/applications')
@login_required
@admin_required
def all_applications():
    apps = Application.query.all()

    return jsonify([
        {
            "student": a.student.student_roll_number,
            "job": a.job.job_title,
            "company": a.job.company.company_name,
            "status": a.application_status
        } for a in apps
    ])
