"""
This module contains functions and objects related to scheduling jobs using
the `apscheduler` library and the Django framework.

The `scheduler` object is an instance of the `BlockingScheduler` class from the
`apscheduler.schedulers.blocking` module, configured to use the timezone
defined in the Django `settings` module. It also has a jobstore created using
the `DjangoJobStore` class from the `django_apscheduler.jobstores` module.

The `define_schedule_job` function takes three parameters: `my_job`, a callable
object representing the job to be scheduled; `schedule`, a `datetime.datetime`
object representing the time and date when the job should run; and `_id`, a
string representing the ID of the job. The function schedules the job using the
`add_job` method of the `scheduler` object, with the `trigger` argument set to
'date', the `run_date` argument set to the `schedule` parameter, and the `id`
argument set to the `_id` parameter. If a job with the same ID already exists,
it will be replaced by the new job.

The function then starts the `scheduler` object using the `start` method, which
will run indefinitely until it is stopped or an exception is raised. If an
exception is raised, the function retrieves and prints the list of scheduled
jobs using the `get_jobs` method of the `scheduler` object.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore

scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")


def define_schedule_job(my_job, schedule, _id):
    scheduler.add_job(my_job,
                      trigger='date',
                      id=_id,
                      run_date=schedule,
                      replace_existing=True)

    try:
        print("Starting scheduler...")
        scheduler.start()
    except Exception as err:
        scheduler.get_jobs()