import sys,json,re,urllib.request,urllib.parse
def search(q):
    url='https://www.youtube.com/results?search_query='+urllib.parse.quote(q)+'&hl=en&gl=AU'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'en'})
    h=urllib.request.urlopen(req,timeout=20).read().decode('utf8','ignore')
    m=re.search(r'var ytInitialData = (\{.*?\});</script>',h)
    if not m: return []
    d=json.loads(m.group(1)); out=[]
    def walk(o):
        if isinstance(o,dict):
            if 'videoRenderer' in o:
                v=o['videoRenderer']; 
                try:
                    out.append((v['videoId'],v['title']['runs'][0]['text'][:70],v['ownerText']['runs'][0]['text'][:28],v.get('lengthText',{}).get('simpleText','?')))
                except Exception: pass
            for x in o.values(): walk(x)
        elif isinstance(o,list):
            for x in o: walk(x)
    walk(d); return out
for q in sys.argv[1:]:
    print('#',q)
    for vid,t,c,l in search(q)[:7]:
        print(f'  {vid} | {l} | {c} | {t}')
