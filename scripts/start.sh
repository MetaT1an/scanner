#!/bin/bash

# to check whether the environment has been created
python3 -m pipenv --venv

# if not, create
if [[ $? -eq 1 ]];then
    python3 -m pipenv --python python3 install
fi

# start a celery task in virtual environment in background, thus
nohup python3 -m pipenv run celery -A celery_task worker -l info --workdir main/ >& /dev/null &

# thanks fabric for making my shell script so ugly!
# https://github.com/fabric/fabric/issues/1901