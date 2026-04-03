from backend.celery_worker import celery
from backend.models.application import Application
from backend.models.student import Student
from backend.models.job import Job
from backend.app import create_app, db
import csv
import os
from backend.app import db


@celery.task
def export_student_applications(student_id):
    apps = Application.query.filter_by(student_id=student_id).all()

    file_path = f"exports/student_{student_id}.csv"

    os.makedirs("exports", exist_ok=True)

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(["Job", "Company", "Status"])

        for a in apps:
            writer.writerow([
                a.job.job_title,
                a.job.company.company_name,
                a.application_status
            ])

    return file_path

@celery.task
def generate_company_report(company_id):
    jobs = Job.query.filter_by(company_id=company_id).all()

    file_path = f"exports/company_{company_id}_report.txt"

    with open(file_path, 'w') as f:
        for j in jobs:
            f.write(f"Job: {j.job_title}\n")
            f.write(f"Applications: {len(j.applications)}\n\n")

    return file_path

@celery.task
def interview_reminder():
    apps = Application.query.filter_by(application_status="interview").all()

    for a in apps:
        print(f"Reminder: Interview for {a.job.job_title}")
