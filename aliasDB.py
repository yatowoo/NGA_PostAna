#!/usr/bin/env python3

# Script for generating basic alias database for Kancolle ships

import zhconv
import json
from pprint import pprint
from pypinyin import lazy_pinyin
import sys

EXPORT_MODE = ['json', 'excel', 'csv']

NGA_SHIPS = [
    "秋月", "照月", "凉月", "初月", "岛风", "晓", "响/Верный", "雷", "电", "白露", "时雨", "村雨",
    "夕立", "春雨", "五月雨", "凉风", "江风", "海风", "山风", "阳炎", "不知火", "黑潮", "初风", "雪风",
    "天津风", "时津风", "浦风", "矶风", "滨风", "谷风", "野分", "舞风", "秋云", "萩风", "岚", "亲潮",
    "朝潮", "大潮", "满潮", "荒潮", "霞", "霰", "朝云", "山云", "初春", "子日", "若叶", "初霜", "吹雪",
    "白雪", "初雪", "深雪", "丛云", "矶波", "绫波", "敷波", "天雾", "狭雾", "浦波", "胧", "曙", "涟 ",
    "潮 ", "睦月 ", "如月 ", "弥生", "卯月", "皋月", "文月", "长月", "菊月", "三日月", "望月", "水无月",
    "夕云", "卷云", "风云", "长波", "早霜", "清霜", "高波", "朝霜", "藤波", "滨波", "岸波", "冲波",
    "神风", "朝风", "春风", "松风", "旗风", "Maestrale", "Libeccio", "Jervis", "Z1",
    "Z3", "Ташкент", "Samuel B.Roberts", "北上", "大井", "木曾", "大淀", "夕张", "天龙",
    "龙田", "川内", "神通", "那珂", "阿贺野", "能代", "矢矧", "酒匂", "长良", "五十铃", "名取", "由良",
    "鬼怒", "阿武隈", "球磨", "多摩", "Gotland", "Prinz Eugen", "爱宕", "高雄", "摩耶", "鸟海",
    "利根", "筑摩", "妙高", "那智", "足柄", "羽黑", "青叶", "衣笠", "古鹰", "加古", "最上", "三隈",
    "Zara", "Pola", "大和", "武藏", "Bismarck", "长门", "陆奥", "Nelson", "Italia",
    "Roma", "Iowa", "Warspite", "Richelieu", "Гангут два", "金刚", "比睿", "榛名",
    "雾岛", "扶桑", "山城", "伊势", "日向", "大凤", "Graf Zeppelin", "Saratoga",
    "Ark Royal", "赤城", "加贺", "飞龙", "苍龙", "翔鹤", "瑞鹤", "云龙", "天城", "葛城",
    "Aquila", "Intrepid", "龙骧", "千代田", "千岁", "龙凤", "飞鹰", "隼鹰", "凤翔", "瑞凤",
    "祥凤", "春日丸/大鹰", "神鹰", "铃谷", "熊野", "Gambier Bay", "吕500", "U-511", "まるゆ",
    "伊400", "伊401", "伊168", "伊58", "伊19", "伊8", "伊26", "伊13", "伊14",
    "Luigi Torelli/伊504", "秋津洲", "瑞穗", "Commandant Teste", "香取", "鹿岛", "大鲸",
    "明石", "秋津丸", "速吸", "神威", "占守", "国后", "择捉", "松轮", "佐渡", "对马", "福江", "日振",
    "大东"]

# Data from Akashi-Toolkit 明石工具箱
## https://github.com/kcwikizh/Akashi-Toolkit
def extract_alias():
  f = open('Ship.json')
  db = json.load(f)
  f.close()

  alias = {}
  for ship in db:
    if(not ship.get('remodel') or ship['remodel']['from_id']):
      continue
    if(not ship.get('name_for_search')):
      print(ship['name']['zh_cn'])
      continue
    alias[ship['name']['zh_cn']] = alias[ship['name']['zh_cn']] = ship['name_for_search'].split(',')

# Export ship alias for Excel
def export_alias_excel(mode='json'):
  f = open('metadata.json')
  meta = json.load(f)
  f.close()
  for group in sorted(meta['2018']['group_stage']): 
    ships = meta['2018']['group_stage'][group]['candidates']
    aliasDB = meta['ShipAliasDB']
    for name in ships:
      pinyin = ''.join(lazy_pinyin(name))
      alias = []
      # From current alias
      if(meta['ShipAliasDB'].get(name)):
        alias += meta['ShipAliasDB'][name]
      if(alias.count(name)):
        alias.remove(name)
      if(alias.count(pinyin)):
        alias.remove(pinyin)
      alias = list(set(alias))
      alias.sort()
      if(mode == 'json'):
        print('"'+name+'": ',end='')
        print(alias,end='')
        print(',')
      elif(mode == 'excel'):
        print(name+'\t'+'\t'.join(alias))
      elif(mode == 'csv'):
        print(name+','+','.join(alias))
          

if __name__ == "__main__":
  mode = 'json'
  if(len(sys.argv) > 1):
    mode = sys.argv[1]
    if(mode not in EXPORT_MODE):
      print('[X] ERROR - Mode input not in config : ' + mode)
      print('\tSupoort export mode : ', end='')
      print(EXPORT_MODE)
      exit()
  export_alias_excel(mode)
  