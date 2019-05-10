#!/usr/bin/env python3

# Script for post content splitting

import csv
import json
import sys
import re
import jieba
import pypinyin

csvfile = open('output/test.csv')
raw = csv.DictReader(csvfile)

MEANINGLESS_WORD = ['zsbd', 'zs', '字数补丁', '字数布丁', '紫薯布丁', '字数', '紫薯', '补丁', "补字数", 'sgnb', '冲鸭', 'exe', 'jpg', 'txt', '单票', '单投', "_\(:з&#39;∠\)_", "&#92;"]
NGA_TAG = ['quote', 'collapse', 'img', 'del', 'url', 'dice', 'code']
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

jieba.load_userdict('alias.dict')
for row in raw:
  text = trim_content(row['回帖内容'],'')
  print('|'.join(jieba.cut(text)))


csvfile.close()