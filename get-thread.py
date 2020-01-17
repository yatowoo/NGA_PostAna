#!/usr/bin/env python3
#coding=utf-8
# Cookie for guest : guestJs=time
import sys, os, time, datetime
import requests, bs4
import re, json, unicodedata

# TODO: New workflow for fully auto-processing
SAIMOE_YEAR = '2019'

def rm_ctrl_ch(text):
  text = text.replace('\\x5C','\\\\')
  return "".join(ch for ch in text if unicodedata.category(ch)[0]!="C")

def refresh_guest(ngack):
  ngack['guestJs'] = repr(int(time.time())-10)

def print_time(timestamp):
  return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))

MAX_PAGES = 1
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

def date2unix(str):
  return int(time.mktime(time.strptime(str,"%Y-%m-%d %H:%M:%S")))

metadb = json.load(open('metadata.json'))
def alias_correct(meta):
  for i,name in enumerate(meta['candidates']):
    if(metadb['ShipAliasDB'].get(name) is not None):
      continue
    else:
      isCorrected = False
      for ship,alias in metadb['ShipAliasDB'].items():
        if(re.search(name,','.join(alias),re.I)):
          meta['candidates'][i] = ship
          isCorrected = True
          print('[+] Ship alias corrected - ' + name + ' -> ' + ship)
          break
      if(not isCorrected):
        print('[X] Ship not found - ' + name)

def get_nga(url):
  for i_req in range(0,MAX_RETRY):
    try:
      time.sleep(REQUEST_DELAY)
      res = requests.get(url, headers=chrome_header,cookies=nga_cookie, timeout=CONNECTION_TIMEOUT)
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
    return None
  # Remove control character before json.loads
  raw_text = rm_ctrl_ch(res.text[33:])
  try:
    raw = json.loads(raw_text)
  except Exception as e:
    print("\n\n\n\n")
    print(e)
    print(raw_text)
    exit()
    return None
  finally:
    return raw

NEW_VOTE = False
for pageno in range(1,MAX_PAGES+1):
  raw = get_nga(base_url+thread_api+'&page='+repr(pageno))
  if(raw is None):
    continue
  # Check the last page of thread
    # Notice : lite=js response include "time"="[timestamp]"
  if(pageno > 1):
    outputJSON.write(",\n")
  outputJSON.write(json.dumps(raw,ensure_ascii=False,indent=2))
  # processing info.
  rows = raw['data']['__ROWS']
  rows_page = raw['data']['__T__ROWS']
  rows_per_page = raw['data']['__T__ROWS_PAGE']
  for rowno in range(rows_page):
    if(not raw['data']['__T'].get(repr(rowno))):
      print('[X] Fail to resolve row ' + repr(rowno))
      continue
    row = raw['data']['__T'][repr(rowno)]
    title = row['subject']
    tid = row['tid']
    # 判断正在进行的投票贴，非锁定
    if(title.find('投票贴') > -1 and not (1024 & row['type'])):
      print(title)
      if(title.find('附加赛') > -1):
        vote_info = re.search('\[活动\](.*?) 舰娘萌战 (.*?)(.)组附加赛',title).groups()
        group = vote_info[2] + 'X' # 分组
      else:
        vote_info = re.search('\[活动\](.*?) 舰娘萌战 (.*?)(.)组投票贴',title).groups()
        group = vote_info[2] # 分组
      event = vote_info[0] # 第N届
      stage = vote_info[1] # 阶段
      if(stage.find('上半区') > -1):
        stage = stage.replace('上半区', '')
        group = '1' + group
      elif(stage.find('下半区') > -1):
        stage = stage.replace('下半区', '')
        group = '2' + group
      # Check metadb
      if(metadb[SAIMOE_YEAR].get(stage) is None):
        metadb[SAIMOE_YEAR][stage] = {}
      if(metadb[SAIMOE_YEAR][stage].get(group) is None):
        print('[+] NEW Vote found - ' + event + '-' + stage + '-' + group)
      else:
        continue
      post = get_nga(base_url + '/read.php?tid=' + repr(tid) + '&lite=js')
      text = post['data']['__R']['0']['content']
      meta = {}
      meta['tid'] = tid
      meta['candidates'] = [s.split('，')[-1].replace('[i]','').replace('[/i]','').strip().split('/')[0] for s in re.findall('\[i].*?\[/i\]', text, re.I)]
      alias_correct(meta)
      meta['selection_max'] = int(re.search('每人(.*?)票',text).groups()[0])
      ddl = re.search('投票于(.*?)：',text).groups()[0]
      ddl = re.sub('月', '-', ddl)
      ddl = re.sub('日.午',' ', ddl)
      current_year = time.localtime().tm_year
      meta['deadline'] = repr(current_year) + '-' + ddl + ':00:00'
      if(date2unix(meta['deadline']) < time.time()):
        meta['deadline'] = repr(current_year+1) + '-' + ddl + ':00:00'
      print(json.dumps(meta, indent=2, ensure_ascii=False))
      metadb[SAIMOE_YEAR][stage][group] = meta
    row = raw['data']['__T'][repr(rowno)]
    outputCSV.write(repr(row['tid'])) # post id
    outputCSV.write(sep + repr(1024 & row['type'])) # locked
    outputCSV.write(sep + repr(row['subject']))
    outputCSV.write(sep + repr(row['authorid']))
    outputCSV.write(sep + print_time(row['postdate']))
    outputCSV.write(sep + repr(row['replies']))
    outputCSV.write(sep + print_time(row['lastpost']))
    outputCSV.write('\n')

json.dump(metadb, open('metadata.json', 'w'), indent=2, ensure_ascii=False)

print("\n[-] INFO - Finished")

outputJSON.write("\n]")
outputJSON.close()
outputCSV.close()
