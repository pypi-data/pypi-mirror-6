from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings.SETTINGS_MODULE)

project = '.'.join(settings.SETTINGS_MODULE.split('.')[:-1])
app = Celery(project)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')
