from datetime import datetime
from backend.celery_worker import celery
from backend.models.application import Application
from backend.models.student import Student
from backend.models.job import Job
from backend.models.company import Company
from backend.models.user import User
from backend.app import create_app, db
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import csv
import os

# Start the debug server before testing: python -m smtpd -n -c DebuggingServer localhost:1025
SMTP_HOST = 'localhost'
SMTP_PORT = 1025
SENDER_ADDRESS = 'placementportal@localhost'
ADMIN_EMAIL = 'admin@localhost'


@celery.task()
def send_email(to_address, subject, message, content="text", attachment_path=None):
    """
    Sends email via the local SMTP debug server.
    content: 'text' for plain text, 'html' for HTML body.
    attachment_path: optional path to a file to attach.
    """
    msg = MIMEMultipart()
    msg['To'] = to_address
    msg['From'] = SENDER_ADDRESS
    msg['Subject'] = subject

    if content == "html":
        msg.attach(MIMEText(message, 'html'))
    else:
        msg.attach(MIMEText(message, 'plain'))

    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
        msg.attach(part)

    # Always log to disk first (for auditability)
    try:
        with open("mail.log", "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] ATTEMPT TO: {to_address} | SUBJECT: {subject}\n")
    except Exception as e:
        print(f"FAILED TO WRITE TO mail.log: {e}")

    try:
        s = smtplib.SMTP(host=SMTP_HOST, port=SMTP_PORT)
        s.send_message(msg)
        s.quit()
        print(f"Email successfully sent to {to_address}")
    except Exception as e:
        print(f"Email delivery failed for {to_address} (is local SMTP server running?): {e}")


@celery.task()
def export_student_applications(student_id):
    """
    Exports a student's full placement application history to CSV.
    Required columns: Student ID, Name, Company Name, Drive Title, Status, Date.
    Triggered from the Student Dashboard and emailed back to the student.
    """
    app = create_app()
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            return "Student not found"

        applications = Application.query.filter_by(student_id=student_id).all()

        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/student_{student_id}_applications.csv"

        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                "Student ID", "Student Name", "Company Name",
                "Drive Title", "Application Status", "Application Date"
            ])
            for a in applications:
                writer.writerow([
                    student_id,
                    student.user.name,
                    a.job.company.company_name or "N/A",
                    a.job.job_title,
                    a.application_status,
                    a.application_date.strftime("%Y-%m-%d") if a.application_date else "N/A"
                ])

        body = (
            f"Dear {student.user.name},\n\n"
            "Your placement application export is ready. "
            "Please find your complete application history attached as a CSV file.\n\n"
            "— Placement Cell"
        )
        send_email(
            to_address=student.user.email,
            subject="Your Placement Application History Export",
            message=body,
            content="text",
            attachment_path=file_path
        )
        return file_path

@celery.task()
def send_daily_reminders():
    """
    Emails all approved students a list of currently open placement drives.
    Runs daily at 9:00 AM IST (configured in celery_worker.py).
    """
    app = create_app()
    with app.app_context():
        open_drives = Job.query.filter_by(job_status='approved').all()
        if not open_drives:
            print("No open drives today — skipping reminders.")
            return "No open drives"

        drives_list = "\n".join([
            f"  • {j.job_title} at {j.company.company_name or 'N/A'} ({j.job_location or 'Location TBD'})"
            for j in open_drives
        ])

        approved_students = Student.query.join(User).filter(User.is_approved == True).all()
        for student in approved_students:
            body = (
                f"Dear {student.user.name},\n\n"
                "Here are the placement drives currently open for applications:\n\n"
                f"{drives_list}\n\n"
                "Log in to the Placement Portal to apply before the deadlines close.\n\n"
                "Best regards,\n— Placement Cell"
            )
            send_email(
                to_address=student.user.email,
                subject="Daily Placement Drive Reminder",
                message=body,
                content="text"
            )
    return "Daily reminders processed"

@celery.task()
def send_monthly_admin_report():
    """
    Generates a monthly HTML email report for the admin.
    Runs on the 1st of each month (configured in celery_worker.py).
    Includes: drives conducted, total applications, students selected.
    """
    app = create_app()
    with app.app_context():
        total_drives = Job.query.count()
        approved_drives = Job.query.filter_by(job_status='approved').count()
        total_applications = Application.query.count()
        total_selected = Application.query.filter_by(application_status='selected').count()

        approved_jobs = Job.query.filter_by(job_status='approved').all()
        drive_rows = "".join([
            f"<tr><td>{j.job_title}</td>"
            f"<td>{j.company.company_name or 'N/A'}</td>"
            f"<td style='text-align:center'>{len(j.applications)}</td></tr>"
            for j in approved_jobs
        ]) or "<tr><td colspan='3' style='text-align:center'>No approved drives this month.</td></tr>"

        html_report = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 24px; color: #333;">
            <h1 style="color: #1a237e;">Monthly Placement Activity Report</h1>
            <hr>
            <h2>Summary</h2>
            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse:collapse; width:60%;">
                <tr style="background:#e3f2fd;"><th>Metric</th><th>Count</th></tr>
                <tr><td>Total Drives Created</td><td>{total_drives}</td></tr>
                <tr><td>Drives Approved</td><td>{approved_drives}</td></tr>
                <tr><td>Total Applications Submitted</td><td>{total_applications}</td></tr>
                <tr><td>Students Selected</td><td>{total_selected}</td></tr>
            </table>
            <br>
            <h2>Approved Drive Breakdown</h2>
            <table border="1" cellpadding="10" cellspacing="0" style="border-collapse:collapse; width:80%;">
                <tr style="background:#e3f2fd;"><th>Drive Title</th><th>Company</th><th>Applicants</th></tr>
                {drive_rows}
            </table>
            <br>
            <p style="color:gray; font-size:12px;">
                Auto-generated on the 1st of the month by the Placement Portal system.
            </p>
        </body>
        </html>
        """

        send_email(
            to_address=ADMIN_EMAIL,
            subject="Monthly Placement Activity Report",
            message=html_report,
            content="html"
        )
    return "Monthly admin report processed"

@celery.task()
def generate_company_report(company_id):
    app = create_app()
    with app.app_context():
        jobs = Job.query.filter_by(company_id=company_id).all()
        os.makedirs("exports", exist_ok=True)
        file_path = f"exports/company_{company_id}_report.txt"
        with open(file_path, 'w') as f:
            for j in jobs:
                f.write(f"Drive: {j.job_title}\nApplicants: {len(j.applications)}\n\n")
        return file_path


@celery.task()
def generate_all_monthly_reports():
    app = create_app()
    with app.app_context():
        companies = Company.query.all()
        for company in companies:
            generate_company_report.delay(company.id)


@celery.task()
def interview_reminder():
    app = create_app()
    with app.app_context():
        interview_apps = Application.query.filter_by(application_status="interview").all()
        for a in interview_apps:
            print(f"Interview reminder: Student {a.student_id} — Drive: {a.job.job_title}")
