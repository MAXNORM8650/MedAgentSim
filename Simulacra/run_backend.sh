#!/bin/bash

BACKEND_SCRIPT_PATH="reverie/backend_server"
BACKEND_SCRIPT_FILE="reverie.py"
CONDA_ENV="simulacra"
LOGS_PATH="../../logs"

echo "Running backend server at: http://127.0.0.1:8000/simulator_home"
cd ${BACKEND_SCRIPT_PATH}
source /home/${USER}/anaconda3/bin/activate ${CONDA_ENV}

timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
echo "Timestamp: ${timestamp}"
mkdir -p ${LOGS_PATH}
python3 ${BACKEND_SCRIPT_FILE} --origin ${1} --target ${2} | tee  ${LOGS_PATH}/${2}_${timestamp}.txt