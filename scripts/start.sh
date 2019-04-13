#!/bin/bash

# to check whether the environment has been created
pipenv --venv

# if not, create
if [[ $? -eq 1 ]];then
    pipenv --python python3 install
fi

# start a celery task in virtual environment
pipenv run celery -A celery_task worker -l info --workdir main/