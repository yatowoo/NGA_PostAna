#!/usr/bin/env python3

# Script for NGA saimoe group analysis
# ChangeLogs
## v1.1: 支持繁体与中文名谐音
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
import zhconv
from pypinyin import lazy_pinyin

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

def pass_register_time_check(row):
  # Registered before REG_TIME_LIMIT
  if(date2unix(row['reg_time']) > REG_TIME_LIMIT):
    return False
  return True

def pass_selection_num_check(row):
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

def pinyin_match(post_content, name):
  real_pinyin = ''.join(lazy_pinyin(name))
  input_pinyin = ''.join(lazy_pinyin(post_content))
  if(re.search(real_pinyin, input_pinyin, re.I)):
    return True
  return False

csvfile = open(sys.argv[1])
raw = csv.DictReader(csvfile)

dirname = os.path.dirname(sys.argv[1])
filename = os.path.basename(sys.argv[1]).split('.')[0]

result_file = open(dirname +"/" + filename + "-result.csv","w")
header = ['post_no','uid','reg_time','post_time','text','选择数'] + candidates
writer = csv.DictWriter(result_file, fieldnames=header)
writer.writeheader()

data = []
excel_row_no = 0 # 导入Excel后的行号
for row in raw:
  # 直接输出Excel公式，统计本行选择数
  # 求和公式格式：=SUM($G$2:$V$2)
  # TODO: 若修改输出格式需修改公式，如增加页码列
  excel_row_no += 1
  row['选择数'] = '=SUM($G$'+ repr(excel_row_no +1) + ':$V$' + repr(excel_row_no +1) + ')'
  for name in candidates:
    # 预处理中文繁体
    post_content = zhconv.convert(row['text'], 'zh-cn')
    if(re.search(name, post_content, re.I)):
      # 本名
      row[name] = 1
    elif(aliasDB.get(name) and alias_match(post_content, name)):
      # 别名
      row[name] = 1
    elif(pinyin_match(post_content, name)):
      # 谐音 / 错字
      row[name] = 1
    else:
      row[name] = ''
  if(not pass_register_time_check(row)):
    # 清空结果，但仍输出回帖内容，表中注意标红
    for name in candidates:
      row[name] = ''
    print(row['post_no']+'\t'+row['reg_time']+'\t'+row['text'])
  if(not pass_selection_num_check(row)):
    print(row['post_no']+'\t'+row['reg_time']+'\t'+row['text'])
  writer.writerow(row)

  data.append(row)

csvfile.close()
result_file.close()

