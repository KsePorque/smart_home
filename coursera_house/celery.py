# from core.tasks import smart_home_manager
# import time
# import schedule
#
# schedule.every(10).seconds.do(smart_home_manager)
#
# while True:
#     print("a")
#     schedule.run_pending()
#     time.sleep(1)


from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coursera_house.settings')
django.setup()

app = Celery('proj')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from coursera_house.core.tasks import smart_home_manager

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5, smart_home_manager.s(), name='Check Smart Home')
