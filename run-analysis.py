#!/usr/bin/env python3

# Script for entire analysis workflow

import os
import json
import time
import sys

def date2unix(str):
  return int(time.mktime(time.strptime(str,"%Y-%m-%d %H:%M:%S")))

metafile = open("metadata.json")
metadata = json.load(metafile)
metafile.close()

SAIMOE_YEAR = '2018'
SAIMOE_STAGE = 'group_stage'

# Command-line arguments
debug = False
local = False
if(len(sys.argv) > 1):
  # Run mode
  debug = (sys.argv[1] == 'debug')
  local = (sys.argv[1] == 'local')

# Create output directory
print('\n------\n\tNGA舰萌计票辅助\n------\n')
cmd = 'mkdir -p output'
print('[-] INFO - Check output dir. : '+cmd)
os.system(cmd)
for group in sorted(metadata[SAIMOE_YEAR]['group_stage']):
  thread = metadata[SAIMOE_YEAR]['group_stage'][group]
  if(not thread.get('tid')):
    continue
  print("\n---> Processing : " + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group)

  # Check existence of post data
  postfile = 'output/NGA-' + repr(thread['tid']) + '.json'
  try:
    file_info = os.stat(postfile)
  except FileNotFoundError:
    print("[-] NEW post found in metadata.json")
    local = False
  else:
    deadline = date2unix(thread['deadline'])
    # Check file last modified time
    if(file_info.st_mtime > deadline):
      print("[-] INFO - Thread " + repr(thread['tid']) + " has already been latest version")
      continue
    else:
      print("[-] INFO - Thread " + repr(thread['tid']) + " will be updated to latest version")

  print("[-] INFO - Start analysis for " + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group)
  csvfile = 'output/' + SAIMOE_YEAR + '-' + SAIMOE_STAGE + '-' + group + '.csv'
  # Get post by NGA tid
  cmd = './get-post.py '+ repr(thread['tid'])
  print(cmd)
  if(not debug and not local):
    os.system(cmd)
  # Export post from raw json to csv
  cmd = './export-post.py '+ postfile + ' ' + csvfile
  print(cmd)
  if(not debug):
    os.system(cmd)
  # Analysis post content as csv
  cmd = './ana-group.py '+ csvfile + ' ' + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group
  print(cmd)
  if(not debug):
    os.system(cmd)