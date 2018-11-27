#!/usr/bin/env python3

# Script for NGA saimoe group analysis
# ChangeLogs
## v0: analysis output/18-GroupA.csv -> output/18-GroupA-result.csv

import csv
import json
import re
import time

def date2unix(str):
  return int(time.mktime(time.strptime(str,"%Y-%m-%d %H:%M:%S")))

REG_TIME_LIMIT = date2unix("2018-11-11 00:00:00")

SELECTION_MAX = 5
candidates = ["摩耶", "Maestrale", "朝潮", "球磨", "风云", "Aquila", "山城", "Intrepid", "晓", "朝云", "凉风", "旗风", "时雨", "北上", "Gotland", "葛城"]
aliasDB = {
  '凉风': ['凉风', '涼風'], 
  '风云': ['风云', '風雲'], 
  '北上': ['北上'], 
  'Intrepid': ['Intrepid', '无畏'], 
  '摩耶': ['摩耶', 'maya'], 
  'Aquila': ['Aquila', '阿奎拉', '阿库娅', '鹫座', '天鹰'], 
  '朝潮': ['朝潮'], 
  '朝云': ['朝云', '朝雲'], 
  'Gotland': ['Gotland', '哥特兰'], 
  '旗风': ['旗风', '旗風'], 
  '球磨': ['球磨', 'kuma'], 
  '山城': ['山城'], 
  '葛城': ['葛城'], 
  'Maestrale': ['Maestrale', '西北风'], 
  '时雨': ['时雨', '時雨', "shigure", "大天使", "祥瑞", "忠犬"], 
  '晓': ['晓', 'lady', '曉', '暁']}

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

csvfile = open("output/18-GroupA.csv")
raw = csv.DictReader(csvfile)

result_file = open("output/18-GroupA-result.csv","w")
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

