"""
celery-task part

please type following command in the same directory with current file:

celery -A celery_task worker -l info

to start listening on the rabbitMQ to wait for tasks
"""

import celery
import scanner

broker_url = "amqp://192.168.2.12"
backend_url = "redis://192.168.2.12"

app = celery.Celery("scanner", broker=broker_url, backend=backend_url)
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_concurrency = 2

scanner = scanner.Scanner()


@app.task
def submit_scan(name, target, policy, description=None):
    data = scanner.scan_task(name, target, policy, description)
    return data     # data to be restored in redis
