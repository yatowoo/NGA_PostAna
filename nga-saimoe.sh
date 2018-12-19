#!/bin/bash -

# Crontab Script for NGA Saimoe Analysis
CODE_DIR=/home/wu_topgun/CODE/NGA_PostAna
WEB_DIR=/var/www/html/nga_saimoe
exec 2>&1 >> $WEB_DIR/crontab.log
set -v
cd $CODE_DIR 
cat run.log >> run_history.log
echo > run.log
./run-analysis.py --info 2018 group64 1>run.out 2>run.err
mkdir -p $WEB_DIR 
cp run.* $WEB_DIR/
# Validation file
echo > validation.log
for file in $(ls output/*validation*);
do
  echo '------> '$file >> validation.log;
  cat $file >> validation.log;
  echo -e '\n\n' >> validation.log;
done
cp validation.log $WEB_DIR/
set +v
