import os

from celery import Celery

# Set the default Django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "video_sharing_web_app.settings")

app = Celery("video_sharing_web_app")

# Using a string here means the worker won't have to serialize the configuration object to child processes
# - namespace="CELERY" means all celery-related configuration keys will have a 'CELERY' prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"request: {self.request!r}")
