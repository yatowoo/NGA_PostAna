#!/usr/bin/env python3
#coding=utf-8
# Cookie for guest : guestJs=time
import sys
import time
import datetime
import requests
import bs4
import json
import unicodedata
import os

def rm_ctrl_ch(text):
  text = text.replace('\\x5C','\\\\')
  return "".join(ch for ch in text if unicodedata.category(ch)[0]!="C")

def refresh_guest(ngack):
  ngack['guestJs'] = repr(int(time.time())-10)

def print_time(timestamp):
  return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))
# User Params
user_tid = None
if(len(sys.argv) == 2):
  user_tid = sys.argv[1]
else:
  user_tid = input("NGA_TID : ")
NGA_TID = 6406100
try:
  NGA_TID = int(user_tid)
except ValueError:
  print("[+] ERROR - Invalid nga tid")
  exit()

MAX_PAGES = 100
MAX_RETRY = 10
REQUEST_DELAY = 0.2 # second
CONNECTION_TIMEOUT = (3.05, 1)

chrome_header = {
          'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36', 
           'Upgrade-Insecure-Requests' : '1',
           'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh;q=0.6,ja;q=0.5,de;q=0.4,zh-TW;q=0.3',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'DNT': '1',
           'Accept-Encoding': 'gzip, deflate',
           'Cache-Control':'max-age=0',
           'Connection':'keep-alive'
}
# NGA HTML Response
  # encoding=GBK
  # Last page : dom[id='m_pbtntop'][class_='uitxt1'][-2]
base_url = 'http://bbs.nga.cn'
# NGA Thread API lite=js
  # encoding=GBK
  # Response : window.script_muti_get_var_store={raw}
  # Pagination: raw['data']
  # -- "__T__ROWS":35//本页的主题数量 
  # -- "__T__ROWS_PAGE":35,//主题列表每页的主题数 
  # -- "__R__ROWS_PAGE":20//阅读主题时每页的回复数 
  # Post: raw['data']['__T']['n']
  # -- tid, subject, type, author, authorid, replies, postdate, lastpost, lastposter, lastmodify, recommend
  # -- type: 1024 = locked, 
thread_api = '/thread.php?&lite=js&fid=-7202235&authorid=6149351'

nga_encoding = 'gbk'
# Output
OUTPUT_FILENAME = 'output/NGA-poi-' + time.strftime('%Y%m%d%H%M%S')
outputJSON = open(OUTPUT_FILENAME + '.json',"w")
outputJSON.write("[\n")

outputCSV = open(OUTPUT_FILENAME + '.csv',"w")
sep = ','
outputCSV.write("TID"+sep+"锁定"+sep+"标题"+sep+"用户ID"+sep+"发帖时间"+sep+"回帖数"+sep+"最后回帖时间"+"\n")

# guestJs should be refreshed in 600 sec.
nga_cookie = {}
refresh_guest(nga_cookie)
last_page = ""
n_pages = 1
for pageno in range(1,MAX_PAGES):
  for i_req in range(0,MAX_RETRY):
    try:
      time.sleep(REQUEST_DELAY)
      res = requests.get(base_url+thread_api+'&page='+repr(pageno), headers=chrome_header,cookies=nga_cookie, timeout=CONNECTION_TIMEOUT)
    except requests.exceptions.RequestException as e:
      if(i_req + 1 == MAX_RETRY):
        print('\n[x] Connection error for page {}, exceed MAX_RETRY/{}'.format(pageno, MAX_RETRY))
        cmd = 'rm -f '+OUTPUT_FILENAME
        outputJSON.close()
        print('[+] Delete output file : '+cmd)
        os.system(cmd)
        exit()
      else:
        print('\n  [+] Connection error for page {}, and retry for {}/{} times'.format(pageno, i_req, MAX_RETRY)+' - '+repr(int(time.time())))
        continue
    else:
      break
  res.encoding = nga_encoding
  if(res.status_code == 403):
    refresh_guest(nga_cookie)
    print("[X] Page " + repr(pageno) + " - 403 ERROR")
    continue
  # Check the last page of thread
    # Notice : lite=js response include "time"="[timestamp]"
  if(pageno > 1):
    outputJSON.write(",\n")
  # Remove control character before json.loads
  raw_text = rm_ctrl_ch(res.text[33:])
  try:
    raw = json.loads(raw_text)
  except Exception as e:
    print("\n\n\n\n")
    print(e)
    print(raw_text)
    exit()
  outputJSON.write(json.dumps(raw,ensure_ascii=False,indent=2))
  # processing info.
  rows = raw['data']['__ROWS']
  rows_page = raw['data']['__T__ROWS']
  rows_per_page = raw['data']['__T__ROWS_PAGE']
  n_pages = 1
  if(pageno == 1):
    print("[-] Connected to NGA forum "+repr(raw['data']['__F']['fid']))
    print("\tRows : "+repr(rows)+", Pages : "+repr(n_pages))
  print("\r[-] Page " + repr(pageno) + " / " + repr(n_pages) + " - "+repr(res.status_code)+" OK", end='')
  for rowno in range(rows_page):
    if(not raw['data']['__T'].get(repr(rowno))):
      print('[X] Fail to resolve row ' + repr(rowno))
      continue
    row = raw['data']['__T'][repr(rowno)]
    outputCSV.write(repr(row['tid'])) # post id
    outputCSV.write(sep + repr(1024 & row['type'])) # locked
    outputCSV.write(sep + repr(row['subject']))
    outputCSV.write(sep + repr(row['authorid']))
    outputCSV.write(sep + print_time(row['postdate']))
    outputCSV.write(sep + repr(row['replies']))
    outputCSV.write(sep + print_time(row['lastpost']))
    outputCSV.write('\n')
  if(pageno == n_pages):
    break
print("\n[-] INFO - Finished")

outputJSON.write("\n]")
outputJSON.close()
outputCSV.close()
