from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pirintechnologies.settings')

# Create a Celery instance.
app = Celery('pirintechnologies')

# Load the Celery configuration from celeryconfig.py.
app.config_from_object('pirintechnologies.celeryconfig')

# Automatically discover task modules in all installed apps.
app.autodiscover_tasks()

