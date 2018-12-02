#!/usr/bin/env python3
#coding=utf-8
import os
import sys
import json
import re
import time

# Arguments
  # ./ana-post.py [filename]
def print_usage():
  print('Usage : ./export-post.py [filename] [output]')

def print_time(timestamp):
  return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))

#filename = '夕立-榛名-13428951.json'
raw = None
output = None
if(len(sys.argv) == 3):
  filename = sys.argv[1]
  output = open(sys.argv[2],"w")
  # try : except FileNotFoundError
  file = open(filename,encoding='utf-8')
  raw = json.load(file)
else:
  print_usage()
  exit()

# Extract post data & output as text/csv
regtime = []
txt = []
uid = []
post_no = []
sep = ','
output.write("post_no"+sep+"uid"+sep+"reg_time"+sep+"post_time"+sep+"text"+"\n")
for page in raw:
  for rowno in range(page['data']['__R__ROWS']):
    row = page['data']['__R'][repr(rowno)]
    if(row['lou'] == 0):
      continue
    output.write(repr(row['lou'])) # post no.
    uid = row['authorid']
    output.write(sep + repr(uid))
    output.write(sep + print_time(page['data']['__U'][repr(uid)]['regdate']))
    output.write(sep + print_time(row['postdatetimestamp']))
    output.write(sep + row['content'].replace(',',' '))
    output.write('\n')
    
output.close()