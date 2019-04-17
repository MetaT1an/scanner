#!/bin/bash

# remove virtual environment
python3 -m pipenv --venv

if [[ $? -eq 0 ]];then
    python3 -m pipenv --rm
fi

# remove repository, this shell should be executed in the scanner/ directory
rm -rf ../scanner

# thanks fabric for making my shell script so ugly!
# https://github.com/fabric/fabric/issues/1901