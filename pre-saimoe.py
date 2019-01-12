for i in range(95,103):
  thread = tlist[i].split('\t')
  gname = '8-' + chr(ord('A')+i-95)
  meta[gname] = {}
  meta[gname]['tid'] = int(thread[1])
  meta[gname]['selection_max'] = 1
  meta[gname]['deadline'] = "2017-02-13 10:00:00"
  tfile = 'output/NGA-' + thread[1] + '.json'
  f = open(tfile)
  raw = json.load(f)
  f.close()
  head = raw[0]['data']['__R']['0']['content']
  cdd = re.search('\[quote\](.*?)\[/quote\]',head,re.S).groups()[0]
  cdd = re.sub('\[img\].*?\[/img\]','',cdd,re.S)
  cdd = re.findall('\[i\](.*?)\[/i\]',head,re.S)
  meta[gname]['candidates'] = [name.split('，')[1] for name in cdd]

for gname in sorted(meta.keys()):
  g = meta[gname]
  print('"'+gname+'":{')
  print('  "tid": '+repr(g['tid'])+',')
  print('  "candidates": '+repr(g['candidates']).replace("'",'"')+',')
  print('  "selection_max": '+repr(g['selection_max'])+',')
  print('  "deadline": "'+g['deadline']+'"\n},')

# Candidate list
meta[gname]['candidates'] = cdd.replace('<br/>',' ').split()[1:]
  # 2014 group_stage
cdd = re.search('\[quote\](.*?)\[/quote\]',head,re.S).groups()[0]
  # 2014 repechage
cdd = head[head.find('复活'):]
  # 2014 semi-final
cdd = head[head.find('半决赛'):]
  # 2016 1v1 16, 8,
cdd = re.findall('\[i\](.*?)\[/i\]',head,re.S)
meta[gname]['candidates'] = [name.split('，')[1] for name in cdd]