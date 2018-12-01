#!/usr/bin/env python3

# Script for NGA saimoe group analysis
# ChangeLogs
## v1.2: 直接输出excel公式统计单帖选择数、总计、分页统计
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

# 统一不同匹配策略命中次数
MATCH_COUNT = {'总计':0, '尝试':0, '本名':0, '别名':0, '谐音':0, '总楼层':0}

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
    MATCH_COUNT['尝试'] += 1
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
logfile = open('analysis.log','a+')
logfile.write('\n------> Analysis log for NGA舰萌'+SAIMOE_YEAR+' '+SAIMOE_STAGE+' '+SAIMOE_GROUP+'组\n')
logfile.write('Date : '+ time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
header = ['post_no','uid','reg_time','post_time','text','选择数'] + candidates
writer = csv.DictWriter(result_file, fieldnames=header, extrasaction='ignore', dialect="excel-tab")
writer.writeheader()

data = []
excel_row_no = 1 # 导入Excel后的行号，第一行为标题
excel_start_col = chr( ord('A') + len(header) - len(candidates))
excel_end_col = chr( ord('A') + len(header) - 1)
for row in raw:
  # 直接输出Excel公式，统计本行选择数
  # 求和公式格式：=SUM($G$2:$V$2)
  excel_row_no += 1
  row['excel_row_no'] = excel_row_no
  row['选择数'] = '=SUM($' + excel_start_col + '$'+ repr(excel_row_no) + ':$' + excel_end_col + '$' + repr(excel_row_no) + ')'
  for name in candidates:
    # 预处理中文繁体
    post_content = zhconv.convert(row['text'], 'zh-cn')
    MATCH_COUNT['总计'] += 1
    if(re.search(name, post_content, re.I)):
      # 本名
      row[name] = 1
      MATCH_COUNT['本名'] += 1
    elif(aliasDB.get(name) and alias_match(post_content, name)):
      # 别名
      row[name] = 1
      MATCH_COUNT['别名'] += 1
    elif(len(name) > 1 and pinyin_match(post_content, name)):
      # 谐音 / 错字 (移除单字舰娘，减少误判)
      row[name] = 1
      MATCH_COUNT['谐音'] += 1
      print('谐音\t'+row['post_no']+'\t'+row['text'])
    else:
      row[name] = ''
      MATCH_COUNT['总计'] -= 1
  if(not pass_register_time_check(row)):
    # 清空结果，但仍输出回帖内容，表中注意标红
    for name in candidates:
      row[name] = ''
    logfile.write('新号\t'+row['post_no']+'\t'+row['reg_time']+'\t'+row['text']+'\n')
  if(not pass_selection_num_check(row)):
    logfile.write('超票\t'+row['post_no']+'\t'+row['text']+'\n')
  writer.writerow(row)
  data.append(row)
MATCH_COUNT['总楼层'] = len(data)
print('[-] INFO - Match efficiency test : ')
print(json.dumps(MATCH_COUNT, ensure_ascii=False, indent=2))
logfile.write('------> End of analysis log\n')
# End of post analysis

# Output excel formula to sum the result in total & pages
def get_empty_row():
  new_row = {}
  for colName in header:
    new_row[colName] = ''
  return new_row

# Excel公式 - 总和
# 形式：=SUM($G$2:$G$800)
fTotal = get_empty_row()
fTotal['选择数'] = '总计'
excel_col = {}
for i,name in enumerate(candidates):
  excel_col[name] = chr(ord(excel_start_col) + i)
  fTotal[name] = "=SUM($" + excel_col[name] + "$2:$" + excel_col[name] + "$" + repr(excel_row_no) + ")"
writer.writerow(fTotal)
# 分页
# 根据楼层post_no - 第一页[1, 19]，中间[20(n-1), 20n-1], 最后[20(n-1), -]
# TODO: 考虑export-post.py时增加页码，尽管NGA删帖直接抽楼不改分页
ROW_PER_PAGE = 20
PAGE_TOTAL = int(int(data[-1]['post_no']) / ROW_PER_PAGE) + 1
current_page = 1
current_page_start_excel_row = 2
for row in data:
  if(int(row['post_no']) >= current_page * ROW_PER_PAGE):
    fPage = get_empty_row()
    fPage['选择数'] = current_page
    for name in candidates:
      fPage[name] = "=SUM($" + excel_col[name] + "$" + repr(current_page_start_excel_row) + ":$" + excel_col[name] + "$" + repr(row['excel_row_no'] -1) + ")"
    writer.writerow(fPage)
    current_page_start_excel_row = row['excel_row_no']
    current_page +=1
# 末页
# TODO: 合并为write_page_formula()
fPage = get_empty_row()
fPage['选择数'] = current_page
for name in candidates:
  fPage[name] = "=SUM($" + excel_col[name] + "$" + repr(current_page_start_excel_row) + ":$" + excel_col[name] + "$" + repr(row['excel_row_no'] -1) + ")"
writer.writerow(fPage)


csvfile.close()
result_file.close()
logfile.close()

