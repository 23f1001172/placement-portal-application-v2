from celery import Celery
from celery.schedules import crontab

def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['backend.tasks']
    )

    celery.conf.beat_schedule = {
        'daily-student-reminder': {
            'task': 'backend.tasks.send_daily_reminders',
            'schedule': crontab(hour=9, minute=0),
        },
        'monthly-admin-report': {
            'task': 'backend.tasks.send_monthly_admin_report',
            'schedule': crontab(day_of_month='1', hour=0, minute=0),
        },
        'daily-interview-reminder': {
            'task': 'backend.tasks.interview_reminder',
            'schedule': crontab(hour=9, minute=30),
        },
    }
    celery.conf.timezone = 'Asia/Kolkata'

    return celery

celery = make_celery()
