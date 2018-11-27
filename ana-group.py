#!/usr/bin/env python3

# Script for NGA saimoe group analysis
# ChangeLogs
## v1: use external metadata for analysis
## v0: analysis output/18-GroupA.csv -> output/18-GroupA-result.csv

# Usage: ./ana-group.py [csv_file] [year] [stage] [group]
## Example: ./ana-group.py output/18-GroupA.csv 2018 group_stage A

import csv
import json
import re
import time
import sys
import os

def date2unix(str):
  return int(time.mktime(time.strptime(str,"%Y-%m-%d %H:%M:%S")))

metafile = open("metadata.json")
metadata = json.load(metafile)
metafile.close()

# Read from metadata with arguments
SAIMOE_YEAR = sys.argv[2]
SAIMOE_STAGE = sys.argv[3]
SAIMOE_GROUP = sys.argv[4]
if(metadata.get(SAIMOE_YEAR)):
  REG_TIME_LIMIT = date2unix(metadata[SAIMOE_YEAR]['regtime_limit'])
else:
  print('[X] ERROR - Wrong YEAR for analysis')
  exit()
if(metadata[SAIMOE_YEAR].get(SAIMOE_STAGE) and metadata[SAIMOE_YEAR][SAIMOE_STAGE].get(SAIMOE_GROUP)):
  SELECTION_MAX = metadata[SAIMOE_YEAR][SAIMOE_STAGE][SAIMOE_GROUP]['selection_max']
  candidates = metadata[SAIMOE_YEAR][SAIMOE_STAGE][SAIMOE_GROUP]['candidates']
else:
  print('[X] ERROR - Wrong STAGE for analysis')
  exit()

aliasDB = metadata['ShipAliasDB']

def result_check(row):
  # Registered before REG_TIME_LIMIT
  if(date2unix(row['reg_time']) > REG_TIME_LIMIT):
    return False
  # Selections less than SELECTION_MAX
  selection_num = 0
  for name in candidates:
    if(row[name]):
      selection_num += 1
  if(selection_num > SELECTION_MAX):
    return False
  return True

def alias_match(post_content, name):
  for alias in aliasDB[name]:
    if(re.search(alias, post_content, re.I)):
      return True
  return False

csvfile = open(sys.argv[1])
raw = csv.DictReader(csvfile)

dirname = os.path.dirname(sys.argv[1])
filename = os.path.basename(sys.argv[1]).split('.')[0]

result_file = open(dirname +"/" + filename + "-result.csv","w")
header = ['post_no','uid','reg_time','post_time','text'] + candidates
writer = csv.DictWriter(result_file, fieldnames=header)
writer.writeheader()

data = []
for row in raw:
  for name in candidates:
    if(alias_match(row['text'], name)):
      row[name] = 1
    else:
      row[name] = ''
  writer.writerow(row)
  if(not result_check(row)):
    print(row['post_no']+' | '+row['reg_time']+' | '+row['text'])
  data.append(row)

csvfile.close()
result_file.close()

