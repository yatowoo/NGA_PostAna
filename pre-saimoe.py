for i in range(16,21):
  thread = tlist[i].split('\t')
  gname = chr(ord('A')+i-16)
  meta[gname] = {}
  meta[gname]['tid'] = int(thread[1])
  meta[gname]['selection_max'] = 3
  meta[gname]['deadline'] = "2015-02-14 20:00:00"
  tfile = 'output/NGA-' + thread[1] + '.json'
  f = open(tfile)
  raw = json.load(f)
  f.close()
  head = raw[0]['data']['__R']['0']['content']
  cdd = head[head.find('半决赛'):]
  cdd = re.sub('\[img\].*?\[/img\]','',cdd,re.S)
  meta[gname]['candidates'] = cdd.replace('<br/>',' ').split()[1:]

# Candidate list
  # 2014 group_stage
cdd = re.search('\[quote\](.*?)\[/quote\]',head,re.S).groups()[0]
  # 2014 repechage
cdd = head[head.find('复活'):]
  # 2014 semi-final
cdd = head[head.find('半决赛'):]