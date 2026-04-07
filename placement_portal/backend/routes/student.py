from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_login import login_required, current_user
from backend.utils.decorators import student_required
from backend.models.student import Student
from backend.models.job import Job
from backend.models.application import Application
from backend.models.placement import Placement
from backend.app import db
from backend.tasks import export_student_applications
from backend.app import cache

student_bp = Blueprint('student', __name__)

@student_bp.route('/jobs')
@login_required
@student_required
@cache.cached(timeout = 60)
def get_jobs():
    jobs = Job.query.filter_by(job_status="approved").all()

    return jsonify([
        {
            "id": j.id,
            "title": j.job_title,
            "company": j.company.company_name,
            "location": j.job_location,
            "salary": j.job_salary,
            "description": j.job_description,
            "type": j.job_type,
            "requirements": j.job_requirements,
            "spots": j.job_spots or 1,
            "total_applicants": len(j.applications),
            "total_selected": Placement.query.join(Application).filter(Application.job_id == j.id).count(),
            "min_cgpa": j.job_min_cgpa or 0.0,
            "required_branch": j.job_required_branch or "All",
            "required_batch": j.job_required_batch or "All",
            "deadline": j.job_deadline.isoformat() if j.job_deadline else None
        } for j in jobs
    ])

@student_bp.route('/job/<int:job_id>')
@login_required
@student_required
def get_single_job(job_id):
    """Fetch a single job by ID regardless of status — used for viewing closed/applied drives."""
    j = Job.query.get(job_id)
    if not j:
        return jsonify({"message": "Drive not found"}), 404
    return jsonify({
        "id": j.id,
        "title": j.job_title,
        "company": j.company.company_name,
        "location": j.job_location,
        "salary": j.job_salary,
        "description": j.job_description,
        "type": j.job_type,
        "requirements": j.job_requirements,
        "spots": j.job_spots or 1,
        "total_applicants": len(j.applications),
        "total_selected": Placement.query.join(Application).filter(Application.job_id == j.id).count(),
        "status": j.job_status,
        "min_cgpa": j.job_min_cgpa or 0.0,
        "required_branch": j.job_required_branch or "All",
        "required_batch": j.job_required_batch or "All",
        "deadline": j.job_deadline.isoformat() if j.job_deadline else None
    })


@student_bp.route('/search')
@login_required
@student_required
@cache.cached(timeout = 60, query_string = True)
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

    job = Job.query.get_or_404(job_id)

    if job.job_deadline and datetime.utcnow() > job.job_deadline:
        return jsonify({"message": "Application deadline has passed"}), 400

    if job.job_min_cgpa and (student.student_cgpa or 0.0) < job.job_min_cgpa:
        return jsonify({"message": f"Ineligible: Minimum CGPA required is {job.job_min_cgpa}"}), 400

    if job.job_required_branch and job.job_required_branch.lower() != "all":
        if not student.student_department or student.student_department.lower() not in job.job_required_branch.lower():
             return jsonify({"message": f"Ineligible: Only students from {job.job_required_branch} can apply"}), 400

    if job.job_required_batch and job.job_required_batch.lower() != "all":
        if not student.student_batch or student.student_batch.lower() not in job.job_required_batch.lower():
             return jsonify({"message": f"Ineligible: Only students from the {job.job_required_batch} batch can apply"}), 400

    app = Application(
        student_id=student.id,
        job_id=job_id,
        application_status='applied'
    )

    db.session.add(app)
    db.session.commit()

    from backend.app import cache
    cache.clear()

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
            "job_id": a.job_id,
            "company": a.job.company.company_name,
            "status": a.application_status,
            "date": a.application_date.strftime("%Y-%m-%d")
        })

    return jsonify(result)


@student_bp.route('/profile', methods=['GET'])
@login_required
@student_required
def get_profile():
    student = Student.query.filter_by(user_id=current_user.id).first()
    return jsonify({
        "name": student.user.name,
        "email": student.user.email,
        "roll_number": student.student_roll_number or "",
        "batch": student.student_batch or "",
        "department": student.student_department or "",
        "education": student.student_education or "",
        "skills": student.student_skills or "",
        "cgpa": student.student_cgpa or 0.0,
        "resume": student.student_resume or ""
    })

import os
from werkzeug.utils import secure_filename
from flask import current_app

@student_bp.route('/update_profile', methods=['POST'])
@login_required
@student_required
def update_profile():
    student = Student.query.filter_by(user_id=current_user.id).first()

    new_roll = request.form.get('roll_number', student.student_roll_number)
    new_batch = request.form.get('batch', student.student_batch)
    if new_roll and new_batch:
        conflict = Student.query.filter(
            Student.student_roll_number == new_roll,
            Student.student_batch == new_batch,
            Student.id != student.id
        ).first()
        if conflict:
            return jsonify({"message": f"Roll number {new_roll} is already registered for batch {new_batch}."}), 400

    new_edu = request.form.get('education', student.student_education)
    new_skills = request.form.get('skills', student.student_skills)
    new_cgpa_raw = request.form.get('cgpa', student.student_cgpa or 0.0)
    new_dept = request.form.get('department', student.student_department)

    try:
        new_cgpa = float(new_cgpa_raw)
        if new_cgpa < 0 or new_cgpa > 10:
            return jsonify({"message": "Please enter a sensible CGPA between 0 and 10."}), 400
    except ValueError:
        return jsonify({"message": "Invalid CGPA format."}), 400

    try:
        if new_batch:
            year = int(new_batch)
            if year < 1900 or year > 2100:
                return jsonify({"message": "Please enter a sensible Graduation Year (e.g., 2025)."}), 400
    except ValueError:
        return jsonify({"message": "Graduation Year must be a number."}), 400

    student.student_education = new_edu
    student.student_skills = new_skills
    student.student_cgpa = new_cgpa
    student.student_roll_number = new_roll
    student.student_batch = new_batch
    student.student_department = new_dept

    if 'resume' in request.files:
        file = request.files['resume']
        if file and file.filename != '':
            # Prevent malicious bypassing by strictly enforcing pdf
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({"message": "Only PDF files are allowed!"}), 400
            
            filename = secure_filename(f"student_{student.id}_{file.filename}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            student.student_resume = f"http://127.0.0.1:5000/static/uploads/{filename}"

    db.session.commit()

    return jsonify({"message": "Profile updated"})

@student_bp.route('/export', methods=['POST'])
@login_required
@student_required
def export_data():
    student = Student.query.filter_by(user_id=current_user.id).first()

    task = export_student_applications.delay(student.id)

    return jsonify({
        "message": "Export started",
        "task_id": task.id
    })

@student_bp.route('/export/status/<task_id>')
@login_required
@student_required
def export_status(task_id):
    from backend.celery_worker import celery
    res = celery.AsyncResult(task_id)
    return jsonify({
        "status": res.state
    })
