from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend') # backend= here, is the name od djangop project 

# Load settings from Django and add namespace CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all apps
app.autodiscover_tasks()
