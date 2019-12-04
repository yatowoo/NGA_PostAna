#!/usr/bin/env python3

# Script for NGA saimoe group analysis
# ChangeLogs
## v1.4: 增加验证功能-beta，匹配前去除候选舰娘中的重复别名
## v1.3: 输出格式适配腾讯文档，改为<TAB>分隔
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
MATCH_COUNT = {'总计':0, '尝试':0, '本名':0, '别名':0, '谐音':0, '总楼层':0, '新号':0, '超票':0, '验证通过':0, '验证失败':0}

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

# Import ship alias after distincted
aliasDB = metadata['ShipAliasDB']
# Remove duplicate alias in candidates
import functools
  # Flatten
allAlias = functools.reduce(
  (lambda x,y: x+y),
  [aliasDB[name] for name in candidates])
duplicate = {alias for alias in allAlias if allAlias.count(alias) > 1}
for alias in duplicate:
  for name in candidates:
    if(aliasDB[name].count(alias)):
      aliasDB[name].remove(alias)

def pass_register_time_check(row):
  # Registered before REG_TIME_LIMIT
  if(date2unix(row['注册时间']) > REG_TIME_LIMIT):
    return False
  return True

def pass_selection_num_check(row):
  # Selections less than SELECTION_MAX
  selection_num = 0
  for name in candidates:
    if(row[name]):
      selection_num += 1
  row['Nselection'] = selection_num
  if(selection_num > SELECTION_MAX):
    return False
  return True

# Validate result with number of splitted words
MEANINGLESS_WORD = ['zsbd', 'zs', '字数补丁', '字数布丁', '紫薯布丁', '字数', '紫薯', '补丁', "补字数", 'sgnb', '冲鸭', 'exe', 'jpg', 'txt', '单票', '单投', "_\(:з&#39;∠\)_", "&#92;", 'awsl']
NGA_TAG = ['quote', 'collapse', 'img', 'del', 'url']
def trim_content(text, delimiter='|'):
  # Remove NGA tags
  text = re.sub('\[s:.*?\]', '', text)
  text = re.sub('\[/?b\]','',text)
  text = re.sub('\[/?size.*?\]','',text)
  for tag in NGA_TAG:
    text = re.sub('\['+tag+'.*?\].*?\[/'+tag+'\]', '', text)

  # Remove meaningless words / characters in post content
  for w in MEANINGLESS_WORD:
    text = re.sub(w, '', text, flags=re.I)
  text = re.sub('[~`@#$%^…&*()（）_\-+=·——]', '', text)

  # Replace delimiter (if for match, remove them)
  text = re.sub('[?？!！:：;；.。,，、　 ]', delimiter, text)
  text = text.replace('<br/>',delimiter)
  text = text.replace('&amp;',delimiter)
  return text

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

def pass_validation(row):
  text = zhconv.convert(row['回帖内容'], 'zh-cn')
  text = text.lower()
  # Remove <BLANK> in name to avoid being splitted
  for name in candidates:
    if(row[name]):
      if(name == '欧根'):
        text = text.replace('prinz eugen', 'PrinzEugen')
      elif(name == '甘比尔湾'):
        text = text.replace('gambier bay', 'GambierBay')
      elif(name == '皇家方舟'):
        text = text.replace('ark royal', 'ArkRoyal')
      elif(name == '路易吉'):
        text = text.replace('luigi torelli', 'LuigiTorelli')
      elif(name == '特斯特'):
        text = text.replace('commandant teste', 'CommandantTeste')
      elif(name == '齐柏林'):
        text = text.replace('graf zeppelin', 'GrafZeppelin')
      elif(name == '罗伯茨'):
        text = text.replace('samuel b.roberts', 'SamuelBRoberts')
        text = text.replace('samuel b. roberts', 'SamuelBRoberts')
      elif(name == '甘古特'):
        text = text.replace('Гангут два','Гангутдва')
      elif(name == '德鲁伊特'):
        text = text.replace('de ruyter','DeRuyter')
  
  # Split text
  text = trim_content(text, delimiter='|')

  # Remove same entry in splitted list
  word_set = set(text.split('|'))
  if({''}.issubset(word_set)):
    word_set.remove('')
  # Validate matching result
  word_num = len(word_set)
  # Dev - correct word number by counting matched word
  hit_num = 0
  try:
    text = text.replace('|', '')
    for name in sorted(candidates, key=(lambda x:len(x)), reverse=True):
      if(row[name]):
        REAL_HIT = False
        for alias in ([name]+aliasDB[name]):
          if(re.search(alias, text, re.I)):
            text = re.sub(alias, '', text, flags=re.I)
            hit_num += 1
            REAL_HIT = True
            break
        # Check multi-hit
        if(not REAL_HIT and not pinyin_match(text, name)):
          print('[X] 重复识别 - ' + row['回帖内容'] + '\t|\t' + name)
          row[name] = None
    if(text):
      hit_num += 1
  except Exception as e:
    print(text)
    raise e
  # 分词数
  if(word_num > 1):
    row['Nword'] = word_num
  else:
    row['Nword'] = hit_num
  # 选择数
  selection_num = 0
  for name in candidates:
    if(row[name]):
      selection_num += 1
  # 校验
  if(selection_num != row['Nword']):
    # Debug
    print('[+] 分词失败 - ' +  repr(selection_num) + '/' + repr(row['Nword']) + ' | ' + row['回帖内容'])
    return False
  else:
    return True

# 初始化文件
print('[-] INFO - '+SAIMOE_YEAR+' '+SAIMOE_STAGE+' '+SAIMOE_GROUP+' loading ...')
csvfile = open(sys.argv[1])
raw = csv.DictReader(csvfile)

dirname = os.path.dirname(sys.argv[1])
filename = SAIMOE_YEAR+'-'+SAIMOE_STAGE+'-'+SAIMOE_GROUP

result_file = open(dirname +"/" + filename + "-result.csv","w")
validation_file = open(dirname +"/" + filename + "-validation.csv","w")
logfile = open('analysis.log','a+')
logfile.write('\n------> Analysis log for NGA舰萌'+SAIMOE_YEAR+' '+SAIMOE_STAGE+' '+SAIMOE_GROUP+'组\n')
logfile.write('Date : '+ time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
header = ['楼层','用户ID','注册时间','回帖时间','回帖内容', '验证', '选择数'] + candidates
writer = csv.DictWriter(result_file, fieldnames=header, extrasaction='ignore', dialect="excel-tab")
writer.writeheader()

# 计数前准备
print('[-] INFO - All file loaded, ready for analysis.')
  # 初始化计数器
VOTE_COUNT = {}
for name in candidates:
  VOTE_COUNT[name] = 0
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
  # 候选舰娘依次匹配
  for name in candidates:
    # 预处理中文繁体
    post_content = zhconv.convert(row['回帖内容'], 'zh-cn')
    # 移除特殊字符
    post_content = trim_content(post_content, delimiter='')
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
      logfile.write('谐音\t'+row['楼层']+'\t'+row['回帖内容']+'\n')
    else:
      row[name] = ''
      MATCH_COUNT['总计'] -= 1
  # 检查匹配结果
    # 检查注册时间
  if(not pass_register_time_check(row)):
    # 清空结果，但仍输出回帖内容，表中注意标红
    for name in candidates:
      row[name] = ''
    logfile.write('新号\t'+row['楼层']+'\t'+row['注册时间']+'\t'+row['回帖内容']+'\n')
    row['验证'] = '-'
    MATCH_COUNT['新号'] += 1
  else:
    # 根据分词进行验证
    if(pass_validation(row)):
      row['验证'] = '●'
      MATCH_COUNT['验证通过'] += 1
    # 验证失败则导出以供分析
    else:
      row['验证'] = '×'
      MATCH_COUNT['验证失败'] += 1
    # 检查选择舰娘数
    if(not pass_selection_num_check(row)):
      validation_file.write('超票\t'+row['楼层']+'\t'+row['回帖内容']+'\n')
      logfile.write('超票\t'+row['楼层']+'\t'+row['回帖内容']+'\n')
      row['验证'] = '?'
      MATCH_COUNT['超票'] += 1
    # 输出验证失败楼层
    if(row['验证'] == '×'):
      validation_file.write(row['楼层']+'\t'+row['回帖内容']+'\t'+repr(row['Nselection'])+'\t'+repr(row['Nword'])+'\n')
  # 统计初步结果
  for name in candidates:
    if(row[name]):
      VOTE_COUNT[name] += 1
  writer.writerow(row)
  data.append(row)
# 输出计数效率统计
MATCH_COUNT['总楼层'] = len(data)
print('[-] INFO - Match efficiency test : ')
print(json.dumps(MATCH_COUNT, ensure_ascii=False, indent=2, sort_keys=True))
logfile.write('------> End of analysis log\n')
# 输出计数初步结果
print('[-] INFO - Preliminary result')
for name in sorted(VOTE_COUNT, key=lambda name:VOTE_COUNT[name], reverse=True):
  print(name+'\t'+repr(VOTE_COUNT[name]))
print('[-] INFO - All rows analysed, ready for result output')
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
# 根据楼层 - 第一页[1, 19]，中间[20(n-1), 20n-1], 最后[20(n-1), -]
# TODO: 考虑export-post.py时增加页码，尽管NGA删帖直接抽楼不改分页
ROW_PER_PAGE = 20
PAGE_TOTAL = int(int(data[-1]['楼层']) / ROW_PER_PAGE) + 1
current_page = 1
current_page_start_excel_row = 2
for row in data:
  if(int(row['楼层']) >= current_page * ROW_PER_PAGE):
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
  fPage[name] = "=SUM($" + excel_col[name] + "$" + repr(current_page_start_excel_row) + ":$" + excel_col[name] + "$" + repr(row['excel_row_no']) + ")"
writer.writerow(fPage)


csvfile.close()
result_file.close()
logfile.close()
validation_file.close()

