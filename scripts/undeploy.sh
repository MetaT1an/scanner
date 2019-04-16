#!/bin/bash

# remove virtual environment
~/.local/bin/pipenv --venv

if [[ $? -eq 0 ]];then
    ~/.local/bin/pipenv --rm
fi

# remove repository, this shell should be executed in the scanner/ directory
rm -rf ../scanner

# thanks fabric for making my shell script so ugly!
# https://github.com/fabric/fabric/issues/1901