#!/usr/bin/env python3

# Generate json data for display

import json
import re
import time
import datetime

log = []
history = ''
current_vote = set()

def buildLogEntry(history):
  if( history != '' and re.search('---.* ..:0.:', history)):
    entry = {}
    entry['text'] = history
    # Analysis Date
    entry['date'] = re.search('---.*: (.*)\n', history).group(1)
    entry['date_format'] = '%a %b %d %H:%M:%S %Z %Y'
    # Group info
    group_name = re.search('INFO - (.*) loading',history).group(1)
    entry['group'] = group_name
    current_vote.add(group_name)
    # Analysis efficiency
    eff_raw = re.search('test : \n(.*)\n.*Preliminary',history,re.S).group(1)
    # Preliminary result
    text = re.search('result\n(.*)\n.*INFO',history,re.S).group(1)
    entry['result'] = {}
    for row in text.split('\n'):
      entry['result'][row.split()[0]] = int(row.split()[1])
    log.append(entry)

with open('run_history.log') as f:
  for line in f:
    if(line.startswith('---')):
      buildLogEntry(history)
      history = line
    else:
      history += line
buildLogEntry(history)

# Generate output for ChartJS
start_hour = time.strptime(log[0]['date'], log[0]['date_format']).tm_hour
output = {}
for group in current_vote:
  output[group] = {}
  output[group]['title'] = group
  output[group]['start_hour'] = start_hour

for entry in log:
  g = output[entry['group']]
  if(not g.get('candidates')):
    g['candidates'] = sorted(entry['result'].keys())
    for name in g['candidates']:
      g[name] = []
  for name in g['candidates']:
    g[name].append(entry['result'][name])

with open('history.json','w+') as f:
  json.dump(
    sorted(output.values(), key=(lambda g:g['title'])),
    f, ensure_ascii=False, indent=2)


