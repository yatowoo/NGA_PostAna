#!/usr/bin/env python3

# Script for generating basic alias database for Kancolle ships

import zhconv
import json
from pprint import pprint

ships = ["摩耶", "Maestrale", "朝潮", "球磨", "风云", "Aquila", "山城", "Intrepid", "晓", "朝云", "凉风", "旗风", "时雨", "北上", "Gotland", "葛城"]

db = {}
for name in ships:
  db[name] = [name] # NGA投票候选用名
  name_zhtw = zhconv.convert(name, 'zh-tw')
  if(name != name_zhtw):
    db[name].append(name_zhtw)

pprint(db)
