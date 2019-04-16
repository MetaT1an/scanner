#!/bin/bash

# to check whether the environment has been created
~/.local/bin/pipenv --venv

# if not, create
if [[ $? -eq 1 ]];then
    ~/.local/bin/pipenv --python python3 install
fi

# start a celery task in virtual environment in background, thus
~/.local/bin/pipenv run celery -A celery_task worker -l info --workdir main/ &

# thanks fabric for making my shell script so ugly!
# https://github.com/fabric/fabric/issues/1901