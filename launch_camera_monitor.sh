#! /usr/bin/bash

source /user/esenes/bin/AWAKE-camera-monitoring/venv/bin/activate
cd /user/esenes/bin/AWAKE-camera-monitoring
python ./camera_monitor_app.py $1 $2 $3
