"""Celery configuration for Academic Research Assistant."""
from celery import Celery
from celery.schedules import crontab
import os

# Celery broker
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Create Celery app
celery_app = Celery(
    "ara",
    broker=broker_url,
    backend=result_backend,
    include=[
        "src.tasks.briefing",
        "src.tasks.parser",
    ],
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Check for new papers every day at 8 AM
    "check-new-papers-daily": {
        "task": "src.tasks.briefing.check_new_papers",
        "schedule": crontab(hour=8, minute=0),
    },
    # Generate weekly briefings every Monday at 9 AM
    "generate-weekly-briefings": {
        "task": "src.tasks.briefing.generate_weekly_briefings",
        "schedule": crontab(hour=9, minute=0, day_of_week=1),
    },
    # Generate monthly briefings on the 1st of each month
    "generate-monthly-briefings": {
        "task": "src.tasks.briefing.generate_monthly_briefings",
        "schedule": crontab(1, 0, 1),
    },
}
