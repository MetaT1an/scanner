#!/bin/bash

# remove virtual environment
pipenv --venv

if [[ $? -eq 1 ]];then
    pipenv --rm
fi

# remove repository, this shell should be executed in the scanner/ directory
rm -rf ../scanner