#!/usr/bin/env python3

# Generate json data for display

import json, re, time, datetime, sys, os

DATA_FORMAT = '%a %b %d %H:%M:%S %Z %Y'

if(len(sys.argv) > 1):
  HISTORY_FILE = sys.argv[1]
else:
  HISTORY_FILE = 'run_history.log'

log = []
history = ''
current_vote = set()

def buildLogEntry(history):
  if( history != '' and re.search('---.* ..:0.:', history)):
    entry = {}
    entry['text'] = history
    # Analysis Date
    entry['date'] = re.search('---.*: (.*)\n', history).group(1)
    # Group info
    group_name = re.search('INFO - (.*) loading',history).group(1)
    entry['group'] = group_name
    current_vote.add(group_name)
    # Analysis efficiency
    eff_raw = re.search('test : \n(.*)\n.*Preliminary',history,re.S).group(1)
    entry['efficiency'] = json.loads(eff_raw)
    # Preliminary result
    text = re.search('result\n(.*)\n.*INFO',history,re.S).group(1)
    entry['result'] = {}
    for row in text.split('\n'):
      entry['result'][row.split()[0]] = int(row.split()[1])
    log.append(entry)

with open(HISTORY_FILE) as f:
  for line in f:
    if(line.startswith('---')):
      buildLogEntry(history)
      history = line
    else:
      history += line
buildLogEntry(history)

# Generate output for ChartJS
output = {}
for group in current_vote:
  output[group] = {}
  output[group]['title'] = group
  for k in log[0]['efficiency'].keys():
    output[group][k] = []

for entry in log:
  g = output[entry['group']]
  if(not g.get('candidates')):
    try:
      g['start_hour'] = time.strptime(entry['date'], DATA_FORMAT).tm_hour
    except ValueError:
      g['start_hour'] = time.strptime(entry['date'].replace('CST', 'CET'), DATA_FORMAT).tm_hour
    g['candidates'] = sorted(entry['result'].keys())
    for name in g['candidates']:
      g[name] = []
  for name in g['candidates']:
    g[name].append(entry['result'][name])
  for k in entry['efficiency']:
    g[k].append(entry['efficiency'][k])

with open('history.json','w+') as f:
  json.dump(
    sorted(output.values(), key=(lambda g:g['title'])),
    f, ensure_ascii=False, indent=2)


