#!/usr/bin/env python3

# Script for entire analysis workflow

import os
import json
import time
import sys
import argparse

def date2unix(str):
  return int(time.mktime(time.strptime(str,"%Y-%m-%d %H:%M:%S")))

metafile = open("metadata.json")
metadata = json.load(metafile)
metafile.close()

# Command-line arguments
parser = argparse.ArgumentParser(description='NGA Post Analysis for Kancolle Saimoe')
parser.add_argument('-l', '--local',help='Do not update thread data, analysis with existed local files', action="store_true", default=False)
parser.add_argument('-d', '--debug',help='Do not run any commands, only check metadata and output commands for analysis', action='store_true', default=False)
parser.add_argument('-a', '--all', help='Analyse all selected thread, ignore deadline', action='store_true', default=False)
parser.add_argument('-i','--info', nargs='+', help='Group information, SAIMOE_YEAR SAIMOE_STAGE (if not specified, latest votes will be selected)')

args = parser.parse_args()

# Select groups for analysis
latest_deadline = 0
if( not args.info):
  for year in metadata:
    if( not year.isdigit()):
      continue
    for stage in metadata[year]:
      if(stage == 'regtime_limit'):
        continue
      for gname,group in metadata[year][stage].items():
        if( group.get('tid') and group.get('deadline')):
          ddl = date2unix(group['deadline'])
          if( ddl > latest_deadline):
            latest_deadline = ddl
            SAIMOE_YEAR = year
            SAIMOE_STAGE = stage
else:
  SAIMOE_YEAR = args.info[0]
  SAIMOE_STAGE = args.info[1]

# Create output directory
print('\n------\n\tNGA舰萌计票辅助\n------\n')
cmd = 'mkdir -p output'
print('[-] INFO - Check output dir. : '+cmd)
os.system(cmd)
for group in sorted(metadata[SAIMOE_YEAR][SAIMOE_STAGE]):
  thread = metadata[SAIMOE_YEAR][SAIMOE_STAGE][group]
  if(not thread.get('tid')):
    continue
  print("\n---> Processing : " + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group)

  # Check existence of post data
  postfile = 'output/NGA-' + repr(thread['tid']) + '.json'
  try:
    file_info = os.stat(postfile)
  except FileNotFoundError:
    print("[-] NEW post found in metadata.json")
    args.local = False
  else:
    deadline = date2unix(thread['deadline'])
    # Check file last modified time
    if(file_info.st_mtime > deadline):
      print("[-] INFO - Thread " + repr(thread['tid']) + " has already been latest version")
      if(not args.all):
        continue
    else:
      print("[-] INFO - Thread " + repr(thread['tid']) + " will be updated to latest version")

  print("[-] INFO - Start analysis for " + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group)
  csvfile = 'output/NGA-' + repr(thread['tid']) + '.csv'
  # Get post by NGA tid
  cmd = './get-post.py '+ repr(thread['tid'])
  print(cmd)
  if(not args.debug and not args.local):
    os.system(cmd)
  # Analysis post content as csv
  cmd = './ana-group.py '+ csvfile + ' ' + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group
  print(cmd)
  if(not args.debug):
    os.system('echo "\n\n\n\n------> New analysis :" $(date) >> output/run.log')
    os.system(cmd+' >> output/run.log')