#!/usr/bin/env python3

# Script for post content splitting

import csv
import json
import sys

f = open('metadata.json')
meta = json.load(f)
f.close()

# Read from metadata with arguments
SAIMOE_YEAR = sys.argv[1]
SAIMOE_STAGE = sys.argv[2]
SAIMOE_GROUP = sys.argv[3]

candidates = meta[SAIMOE_YEAR][SAIMOE_STAGE][SAIMOE_GROUP]['candidates']

csvfile = open('output/'+ SAIMOE_YEAR + '-' + SAIMOE_STAGE + '-' + SAIMOE_GROUP +'-result.csv')
raw = csv.DictReader(csvfile, dialect="excel-tab")

post = []
selection = []
for row in raw:
  if(not row['post_no'].isdigit()):
    continue
  text = row['text']
  text = text.lower()
  selection_num = 0
  for name in candidates:
    if(row[name] == '1'):
      selection_num += 1
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
  text = text.replace('zsbd','')
  text = text.replace('紫薯布丁','')
  text = text.replace('字数补丁','')
  text = text.replace('字数','')
  text = text.replace('。', '|')
  text = text.replace('，', '|')
  text = text.replace('、', '|')
  text = text.replace('<br/>','|')
  text = text.replace(' ','|')
  post.append(text)
  word_set = set(text.split('|'))
  if({''}.issubset(word_set)):
    word_set.remove('')
  word_num = len(word_set)
  if(selection_num != word_num):
    print(row['post_no']+'\t'+row['text']+'\t'+repr(selection_num)+'\t'+repr(word_num))

csvfile.close()