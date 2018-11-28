#!/usr/bin/env python3

# Script for entire analysis workflow

import os
import json

metafile = open("metadata.json")
metadata = json.load(metafile)
metafile.close()

SAIMOE_YEAR = '2018'
SAIMOE_STAGE = 'group_stage'

for group,thread in metadata[SAIMOE_YEAR]['group_stage'].items():
  print("[-] INFO - Start analysis for " + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group)
  postfile = 'output/NGA-' + repr(thread['tid']) + '.json'
  csvfile = 'output/' + SAIMOE_YEAR + '-' + SAIMOE_STAGE + '-' + group + '.csv'
  # Get post by NGA tid
  cmd = './get-post.py '+ repr(thread['tid'])
  print(cmd)
  os.system(cmd)
  # Export post from raw json to csv
  cmd = './export-post.py '+ postfile + ' ' + csvfile
  print(cmd)
  os.system(cmd)
  # Analysis post content as csv
  cmd = './ana-group.py '+ csvfile + ' ' + SAIMOE_YEAR + ' ' + SAIMOE_STAGE + ' ' + group
  print(cmd)
  os.system(cmd)