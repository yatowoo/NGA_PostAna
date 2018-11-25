#!/usr/bin/env python3
#coding=utf-8
import os
import sys
import json
import re
import time

# Register time limit
REG_TIME_LIMIT = int(time.mktime(time.strptime("2017-11-25","%Y-%m-%d")))

# Arguments
  # ./ana-post.py [filename]
def print_usage():
  print('Usage : ./ana-post.py [filename]')

#filename = '夕立-榛名-13428951.json'
raw = None
nameA = None
nameB = None
if(len(sys.argv) == 2):
  filename = sys.argv[1]
  # try : except FileNotFoundError
  file = open(filename)
  raw = json.load(file)
  file.close()
  nameA = filename.split('-')[0]
  nameB = filename.split('-')[1]
else:
  print_usage()
  exit()

# NGA/poi kancolle vote
vote = {
  "夕立" : ['poi', 'p.*o.*i', 'yuudachi', '夕立', 'ぽい', '狂犬', '婆姨'],
  "榛名" : ['榛名','棒各','小天使','haruna'],
  "照月" : ['照月'],
  "翔鹤" : ['翔鹤','太太', '翔鶴', 'shoukaku'],
  "时雨" : ['时雨', 'shigure', '大天使', '祥瑞', '忠犬', '時雨'],
  "俾斯麦":['bismarck','俾斯麦','俾斯麥', 'bsm', '波斯猫', 'B子','麦姐'],
  "凉月":['涼月','凉月','suzutsuki']}

# try : except KeyError
voteA = vote[nameA]
voteB = vote[nameB]
print("\n>>>")
print('NGA舰娘萌战：'+nameA+' vs '+nameB)
print(">>>\n")

# string group match
def group_match(str, names):
  for alias in names:
    if(re.search(alias, str, re.I)):
      return True
  return False

# Extract vote data
regtime = []
txt = []
for page in raw:
  for rowno in range(page['data']['__R__ROWS']):
    row = page['data']['__R'][repr(rowno)]
    txt.append(row['content'])
    uid = row['authorid']
    regtime.append(page['data']['__U'][repr(uid)]['regdate'])

# Vote counting
countA = 0
countB = 0
countEff = 0
for i in range(1,len(txt)):
  if(regtime[i] > REG_TIME_LIMIT):
    continue
  countEff += 1
  isA = group_match(txt[i], voteA)
  isB = group_match(txt[i], voteB)
  if(isA ^ isB):
    if(isA):
      countA += 1
      # TODO: debug mode
      #print(repr(i)+'\tA\t'+txt[i])
    if(isB):
      countB += 1
      #print(repr(i)+'\tB\t'+txt[i])
  else:
    print(repr(i)+'\tX\t'+txt[i])
  
print("\n>>>Preliminary result")
print("Total post = "+repr(len(txt)-1))
print("Effective vote = "+repr(countEff))
print("Vote "+nameA+" = "+repr(countA))
print("Vote "+nameB+" = "+repr(countB))
print(">>>\n")
