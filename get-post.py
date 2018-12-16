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

def rm_ctrl_ch(str):
  return "".join(ch for ch in str if unicodedata.category(ch)[0]!="C")

def refresh_guest(ngack):
  ngack['guestJs'] = repr(int(time.time())-10)

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
MAX_RETRY = 3
REQUEST_DELAY = 0.5 # second
OUTPUT_FILENAME = 'output/NGA-' + repr(NGA_TID) + '.json'

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
base_url = 'http://bbs.ngacn.cc/read.php?tid=' + repr(NGA_TID)
# NGA URL API lite=js
  # encoding=GBK
  # Response : window.script_muti_get_var_store={raw}
  # Register time : raw['data']['__U']["UID"]['regdate']
  # Post content : raw['data']['__R']["rowid"]['content']
  # UID : raw['data']['__R']["rowid"]['authorid']
  # Pagination : raw['data']['__ROWS'],['__R__ROWS_PAGE']
api_param = '&lite=js'
nga_encoding = 'gbk'
# Output
file = open(OUTPUT_FILENAME,"w")
file.write("[\n")

# guestJs should be refreshed in 600 sec.
nga_cookie = {}
refresh_guest(nga_cookie)
last_page = ""
n_pages = 100
for pageno in range(1,MAX_PAGES):
  for i_req in range(0,MAX_RETRY):
    try:
      time.sleep(REQUEST_DELAY)
      res = requests.get(base_url+api_param+'&page='+repr(pageno), headers=chrome_header,cookies=nga_cookie)
    except requests.exceptions.RequestException as e:
      if(i_req + 1 == MAX_RETRY):
        print('[x] Connection error for page {}, exceed MAX_RETRY/{}'.format(pageno, MAX_RETRY))
        cmd = 'rm -f '+OUTPUT_FILENAME
        file.close()
        print('[+] Delete output file : '+cmd)
        os.system(cmd)
        exit()
      else:
        print('[+] Connection error for page {}, and retry for {}/{} times'.format(pageno, i_req, MAX_RETRY))
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
  if(len(res.text) == len(last_page) and pageno >= n_pages):
  #if(res.text[:-20] == last_page[:-20]):
    break
  else:
    last_page = res.text
    if(pageno > 1):
      file.write(",\n")
  # Remove control character before json.loads
  raw_text = rm_ctrl_ch(res.text[33:])
  try:
    raw = json.loads(raw_text)
  except ValueError as e:
    print("\n\n\n\n")
    print(e)
    print(raw_text)
    exit()
  file.write(json.dumps(raw,ensure_ascii=False,indent=2))
  # processing info.
  rows = raw['data']['__ROWS']
  rows_page = raw['data']['__R__ROWS']
  rows_per_page = raw['data']['__R__ROWS_PAGE']
  n_pages = int((rows+1)/rows_per_page)+1
  if(pageno == 1):
    print("[-] Connected to NGA thread "+repr(NGA_TID))
    print("\t"+raw['data']['__T']['subject'])
    print("\tRows : "+repr(rows)+", Pages : "+repr(n_pages))
  print("\r[-] Page " + repr(pageno) + " / " + repr(n_pages) + " - "+repr(res.status_code)+" OK", end='')
print("\n[-] INFO - Finished")

file.write("\n]")
file.close()
