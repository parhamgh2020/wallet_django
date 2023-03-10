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