import celery
import scanner

broker_url = "amqp://192.168.2.12"
backend_url = "redis://192.168.2.12"

app = celery.Celery("scanner", broker=broker_url, backend=backend_url)
scanner = scanner.Scanner()


@app.task
def submit_scan(name, target, policy, email_addr, description=None):
    data = scanner.scan_task(name, target, policy, email_addr, description)
    return data     # data to be restored in redis
