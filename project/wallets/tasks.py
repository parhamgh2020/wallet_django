# Import the necessary modules
from apscheduler.schedulers.background import BackgroundScheduler
from myapp.models import MyModel

# Initialize the scheduler
scheduler = BackgroundScheduler()


# Define the task to be executed
def my_task():
    # Retrieve data from the database using Django's ORM
    data = MyModel.objects.filter(some_field='some_value')

    # Process the retrieved data
    for item in data:
        # do something with each item
        pass

    print("Task executed successfully!")


# Schedule the task to run at a specific time (in this case, every day at midnight)
scheduler.add_job(my_task, 'cron', hour=0, minute=0)

# Start the scheduler
scheduler.start()
