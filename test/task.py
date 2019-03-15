import celery
import time

broker_url = "amqp://192.168.2.12"
backend_url = "redis://192.168.2.12"

app = celery.Celery(broker=broker_url, backend=backend_url)
ip_list = ["192.168.2.10", "192.168.2.11", "192.168.2.12"]
task_list = []

for ip in ip_list:
    task = app.send_task("celery_task.submit_scan", ["celery_launched", ip, "ubuntu", "tyc896@yeah.net"])
    task_list.append(task)

# wait and show the result
while task_list:
    for task in reversed(task_list):
        if not task.ready():
            print("working...")
        else:
            task_list.remove(task)
            print(task.get())

        time.sleep(10)

