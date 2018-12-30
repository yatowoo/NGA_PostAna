#!/bin/bash -

# Crontab Script for NGA Saimoe Analysis
CODE_DIR=/home/wu_topgun/CODE/NGA_PostAna
SCRIPT_NAME=nga-saimoe.sh
WEB_DIR=/var/www/html/nga_saimoe
mkdir -p $WEB_DIR 
echo '\n------> Git Sync : '$(date) >> $WEB_DIR/crontab.log
exec 2>&1 >> $WEB_DIR/crontab.log
set -x
# Sync code with remote repo. on GitHub
cd $CODE_DIR
git pull
rm /etc/cron.hourly/$SCRIPT_NAME
cp $SCRIPT_NAME /etc/cron.hourly/$SCRIPT_NAME
# Run analysis
echo > run.log
echo '\n\n------> stdout : '$(date) > run.out
echo '\n\n------> stderr : '$(date) > run.err
./run-analysis.py 1>run.out 2>run.err
cat run.log >> run_history.log
cat run.out >> run_history.out
cat run.err >> run_history.err
cp run.* run_history.* $WEB_DIR/
# Validation file
echo > validation.log
for file in $(ls output/*validation*);
do
  echo '------> '$file >> validation.log;
  cat $file >> validation.log;
  echo -e '\n\n' >> validation.log;
done
cp validation.log $WEB_DIR/
# Web index page
# Generate result history for ChartJS display
./get-history.py
cp index.html history.json nga.ico $WEB_DIR/
set +x
