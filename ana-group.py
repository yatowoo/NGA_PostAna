#!/usr/bin/env python3

# Script for NGA saimoe group analyse
# ChangeLogs
## v0: analysis output/18-GroupA.csv -> output/18-GroupA-result.csv

import csv
import json
import re

selection_max = 5
candidates = ["摩耶", "Maestrale", "朝潮", "球磨", "风云", "Aquila", "山城", "Intrepid", "晓", "朝云", "凉风", "旗风", "时雨", "北上", "Gotland", "葛城"]

csvfile = open("output/18-GroupA.csv")
raw = csv.DictReader(csvfile)

result_file = open("output/18-GroupA-result.csv","w")
header = ['post_no','uid','reg_time','post_time','text'] + candidates
writer = csv.DictWriter(result_file, fieldnames=header)
writer.writeheader()

data = []
for row in raw:
  for name in candidates:
    if(re.search(name, row['text'], re.I)):
      row[name] = 1
    else:
      row[name] = ''
  writer.writerow(row)
  print(row['post_no']+' '+row['text'])
  data.append(row)

csvfile.close()
result_file.close()

