import re,json,urllib.request,sys
ids=sys.argv[1:]; out={}
for v in ids:
    h=urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/watch?v='+v+'&hl=en',headers={'User-Agent':'Mozilla/5.0','Accept-Language':'en'}),timeout=20).read().decode('utf8','ignore')
    g=lambda p: (re.search(p,h) or [None,None])[1]
    L=g(r'"lengthSeconds":"(\d+)"'); ch=g(r'"ownerChannelName":"([^"]+)"'); em=g(r'"playableInEmbed":(true|false)'); t=g(r'<title>([^<]+)</title>')
    out[v]=dict(len=int(L) if L else None,channel=ch,embed=em,title=(t or '').replace(' - YouTube',''))
    print(v,L,em,ch,'|',out[v]['title'][:70])
json.dump(out,open('site/src/videos_verified.json','w'),indent=1)
