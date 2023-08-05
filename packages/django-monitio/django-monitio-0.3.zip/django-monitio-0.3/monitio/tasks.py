# -*- encoding: utf-8 -*-

from celery.schedules import crontab
from celery.task import periodic_task
from monitio.models import Monit


@periodic_task(run_every=crontab(minute="*/30"))
def remove_read_messages():
    Monit.objects.filter(read=True).delete()