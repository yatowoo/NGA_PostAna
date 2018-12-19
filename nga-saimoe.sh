#!/bin/bash -

# Crontab Script for NGA Saimoe Analysis
CODE_DIR=/home/wu_topgun/CODE/NGA_PostAna
SCRIPT_NAME=nga-saimoe.sh
WEB_DIR=/var/www/html/nga_saimoe
set -v
cd $CODE_DIR
git pull
rm /etc/cron.hourly/$SCRIPT_NAME
cp $SCRIPT_NAME /etc/cron.hourly/$SCRIPT_NAME
cat run.log >> run_history.log
echo > run.log
./run-analysis.py --info 2018 group64 1>run.out 2>run.err
mkdir -p $WEB_DIR 
cp run.* $WEB_DIR/ 
set +v
