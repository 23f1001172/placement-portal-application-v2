from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from backend.utils.decorators import company_required
from backend.models.company import Company
from backend.models.job import Job
from backend.models.application import Application
from backend.models.student import Student
from backend.models.placement import Placement
from backend.app import db, cache
from backend.tasks import send_email

company_bp = Blueprint('company', __name__)

@company_bp.route('/dashboard')
@login_required
@company_required
def dashboard():
    company = Company.query.filter_by(user_id=current_user.id).first()

    drives_created = Job.query.filter_by(company_id=company.id).count()
    drives_accepted = Job.query.filter_by(company_id=company.id, job_status='approved').count()
    total_applications = Application.query.join(Job).filter(Job.company_id == company.id).count()
    candidates_selected = Placement.query.filter_by(company_id=company.id).count()

    return jsonify({
        "drives_created": drives_created,
        "drives_accepted": drives_accepted,
        "total_applications": total_applications,
        "candidates_selected": candidates_selected
    })

@company_bp.route('/create_job', methods=['POST'])
@login_required
@company_required
def create_job():
    data = request.get_json()

    company = Company.query.filter_by(user_id=current_user.id).first()

    job_title = data.get('title')
    job_description = data.get('description')
    job_salary = data.get('salary')
    job_type = data.get('type')

    if job_type != 'Internship':
        if not job_salary or float(job_salary) <= 0:
            return jsonify({"message": "Only internships can have a 0 dollar salary."}), 400

    if not job_title or not job_description:
        return jsonify({"message": "Title and description are required"}), 400

    job = Job(
        company_id=company.id,
        job_title=job_title,
        job_description=job_description,
        job_location=data.get('location'),
        job_salary=job_salary,
        job_type=job_type,
        job_requirements=data.get('requirements'),
        job_status='pending',
        job_spots=int(data.get('spots', 1)),
        job_min_cgpa=float(data.get('min_cgpa', 0.0)),
        job_required_branch=data.get('required_branch', 'All'),
        job_deadline=datetime.fromisoformat(data.get('deadline').replace('Z', '+00:00')) if data.get('deadline') else None
    )

    db.session.add(job)
    db.session.commit()

    from backend.app import cache
    cache.clear()

    return jsonify({"message": "Job created, waiting for admin approval"})

@company_bp.route('/edit_job/<int:id>', methods=['PUT'])
@login_required
@company_required
def edit_job(id):
    data = request.get_json()
    job = Job.query.get(id)
    if not job:
        return jsonify({"message": "Job not found"}), 404
    company = Company.query.filter_by(user_id=current_user.id).first()
    if job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403
    job.job_title = data.get('title', job.job_title)
    job.job_description = data.get('description', job.job_description)
    job.job_location = data.get('location', job.job_location)
    job.job_salary = data.get('salary', job.job_salary)
    job.job_type = data.get('type', job.job_type)
    job.job_requirements = data.get('requirements', job.job_requirements)
    job.job_spots = int(data.get('spots', job.job_spots or 1))
    job.job_min_cgpa = float(data.get('min_cgpa', job.job_min_cgpa or 0.0))
    job.job_required_branch = data.get('required_branch', job.job_required_branch or 'All')
    if data.get('deadline'):
        job.job_deadline = datetime.fromisoformat(data.get('deadline').replace('Z', '+00:00'))
    job.job_status = 'pending'
    db.session.commit()
    from backend.app import cache
    cache.clear()
    return jsonify({"message": "Job updated and marked pending"})

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
            "status": j.job_status,
            "location": j.job_location,
            "salary": j.job_salary,
            "type": j.job_type,
            "description": j.job_description,
            "requirements": j.job_requirements,
            "spots": j.job_spots or 1,
            "total_applicants": len(j.applications),
            "total_selected": Placement.query.join(Application).filter(Application.job_id == j.id).count()
        } for j in jobs
    ])

@company_bp.route('/profile', methods=['GET'])
@login_required
@company_required
def get_profile():
    company = Company.query.filter_by(user_id=current_user.id).first()
    return jsonify({
        "name": company.company_name or "",
        "email": company.company_email or current_user.email,
        "industry": company.company_industry or "",
        "description": company.company_description or "",
        "website": company.company_website or "",
        "location": company.company_location or ""
    })

@company_bp.route('/profile', methods=['POST'])
@login_required
@company_required
def update_profile():
    data = request.get_json()
    company = Company.query.filter_by(user_id=current_user.id).first()
    company.company_name = data.get('name', company.company_name)
    company.company_email = data.get('email', company.company_email)
    company.company_industry = data.get('industry', company.company_industry)
    company.company_description = data.get('description', company.company_description)
    company.company_website = data.get('website', company.company_website)
    company.company_location = data.get('location', company.company_location)
    db.session.commit()
    from backend.app import cache
    cache.clear()
    return jsonify({"message": "Profile updated"})

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
            "student_name": student.user.name,
            "student_email": student.user.email,
            "student_roll_number": student.student_roll_number or "N/A",
            "student_batch": student.student_batch or "N/A",
            "student_department": student.student_department or "N/A",
            "education": student.student_education or "N/A",
            "skills": student.student_skills or "N/A",
            "resume": student.student_resume or "N/A",
            "status": app.application_status,
            "date": app.application_date.strftime("%Y-%m-%d") if app.application_date else "N/A"
        })

    return jsonify(result)

@company_bp.route('/update_application/<int:id>', methods=['POST'])
@login_required
@company_required
def update_application(id):
    data = request.get_json() or {}

    app = Application.query.get(id)

    if not app:
        return jsonify({"message": "Application not found"}), 404

    company = Company.query.filter_by(user_id=current_user.id).first()

    if app.job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403

    status = data.get('status')

    allowed = ["shortlisted", "interview", "selected", "rejected"]

    if status not in allowed:
        return jsonify({"message": "Invalid status"}), 400

    existing_placement = Placement.query.filter_by(application_id=app.id).first()

    if status == "selected":
        # Only create a NEW placement if one doesn't already exist
        if not existing_placement:
            # Enforce spot limit — count actual Placement records for this job
            job = app.job
            spots = job.job_spots or 1
            already_selected = Placement.query.join(Application).filter(Application.job_id == job.id).count()

            if already_selected >= spots:
                return jsonify({
                    "message": f"Cannot select more candidates. "
                               f"This drive only has {spots} spot(s) and all are filled."
                }), 400

            placement = Placement(
                student_id=app.student_id,
                company_id=app.job.company_id,
                application_id=app.id,
                position=app.job.job_title,
                salary=app.job.job_salary,
                placement_date=datetime.utcnow()
            )
            db.session.add(placement)
        # If placement already exists, we're just re-selecting — nothing to add

    else:
        # Candidate is being un-selected (shortlisted / interview / rejected)
        # Remove their Placement record so the spot becomes free again
        if existing_placement:
            db.session.delete(existing_placement)

    app.application_status = status
    db.session.commit()
    
    send_email.delay(app.student.user.email, "Application Status Updated", f"Hello {app.student.user.name}, your application for '{app.job.job_title}' at {app.job.company.company_name} has been updated to: {status.upper()}.")

    from backend.app import cache
    cache.clear()

    return jsonify({"message": "Updated"})


@company_bp.route('/close_job/<int:id>', methods=['POST'])
@login_required
@company_required
def close_job(id):
    job = Job.query.get(id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    job.job_status = "closed"
    db.session.commit()

    from backend.app import cache
    cache.clear()

    return jsonify({"message": "Job closed"})

@company_bp.route('/reopen_job/<int:id>', methods=['POST'])
@login_required
@company_required
def reopen_job(id):
    job = Job.query.get(id)
    if not job:
        return jsonify({"message": "Job not found"}), 404
    company = Company.query.filter_by(user_id=current_user.id).first()
    if job.company_id != company.id:
        return jsonify({"message": "Unauthorized"}), 403
    if job.job_status not in ('closed',):
        return jsonify({"message": "Only closed drives can be reopened"}), 400
    job.job_status = 'pending'  # Goes back to admin for re-approval
    db.session.commit()
    from backend.app import cache
    cache.clear()
    return jsonify({"message": "Drive resubmitted for admin approval"})

@company_bp.route('/export', methods=['POST'])
@login_required
@company_required
def export_report():
    from backend.tasks import generate_company_report  # 👈 move here

    company = Company.query.filter_by(user_id=current_user.id).first()
    task = generate_company_report.delay(company.id)

    return jsonify({
        "message": "Report generating",
        "task_id": task.id
    })

@company_bp.route('/export/status/<task_id>')
@login_required
@company_required
def export_status(task_id):
    from backend.celery_worker import celery
    res = celery.AsyncResult(task_id)
    return jsonify({
        "status": res.state
    })
