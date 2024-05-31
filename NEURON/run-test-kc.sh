#!/bin/bash

# Copyright 2024 Ankur Sinha
# Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com> 
# File : 
#

if [[ -z "${MODEL_DIR}" ]]; then
    export MODEL_DIR=$(pwd)
    echo "Setting model root directory to $MODEL_DIR"
    echo "To use a custom path, set the MODEL_DIR environment variable to the desired path."
fi

export PYTHONPATH="${MODEL_DIR}/mb:${MODEL_DIR}/nrn:${MODEL_DIR}/morphutils:${MODEL_DIR}/common"
nrnivmodl ./mb/mod/
python ./mb/test_cell/test_kc.py
