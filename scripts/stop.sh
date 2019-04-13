#!/bin/bash

# this script is used to stop celery worker process

# 1.firstly, we need to find out all celery processes
# ps -e | grep 'celery'
# 6162 pts/0    00:00:00 celery
# 6172 pts/0    00:00:00 celery
# 6173 pts/0    00:00:00 celery
# 6174 pts/0    00:00:00 celery
# 6175 pts/0    00:00:00 celery

# 2.secondly, we need to get PIDs of theses processes
# ps -e | grep 'celery' | awk '{print $1}'
# 6162
# 6172
# 6173
# 6174
# 6175

# 3.Lastly, kill them without mercy
ps -e | grep 'celery' | awk '{print $1}' | xargs kill -9