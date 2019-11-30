#!/bin/bash -

# Crontab Script for NGA Saimoe Analysis
CODE_DIR=/home/ubuntu/NGA_PostAna
SCRIPT_NAME=nga-saimoe.sh
WEB_DIR=/var/www/html/nga_saimoe
mkdir -p $WEB_DIR 
echo '\n------> Git Sync : '$(date) >> $WEB_DIR/crontab.log
exec 2>&1 >> $WEB_DIR/crontab.log
set -x
# Sync code with remote repo. on GitHub
cd $CODE_DIR
git pull
# Run analysis
mkdir -p output
echo > output/run.log
echo -e '\n\n------> run-analysis.py stdout : '$(date) > output/run.out
echo -e '\n\n------> run-analysis.py stderr : '$(date) > output/run.err
echo -e '\n\n------> ana-group.py analysis log : '$(date) > output/analysis.log
./run-analysis.py 1>>output/run.out 2>>output/run.err
cat output/run.log >> output/run_history.log
cat output/run.out >> output/run_history.out
cat output/run.err >> output/run_history.err
cp output/run.* output/run_history.* $WEB_DIR/
# Validation file
echo > output/validation.log
for file in $(ls output/*validation*);
do
  echo '------> '$file >> output/validation.log;
  cat $file >> output/validation.log;
  echo -e '\n\n' >> output/validation.log;
done
cp output/validation.log $WEB_DIR/
# Web index page
# Generate result history for ChartJS display
./get-history.py output/run_history.log
cp index.html validation.php history.json nga.ico output/*result*csv $WEB_DIR/
set +x
