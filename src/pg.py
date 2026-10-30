import re,sys
# usage: pg.py KEY pages(e.g. 1,3-5) [maxchars_per_page]
k=sys.argv[1]; sel=sys.argv[2]; mx=int(sys.argv[3]) if len(sys.argv)>3 else 10**6
t=open(f'extract/{k}.txt').read()
parts=re.split(r'(?m)^=== p(\d+) \[\d+\]\n',t)[1:]
P={int(parts[i]):parts[i+1] for i in range(0,len(parts),2)}
want=set()
for s in sel.split(','):
    a,_,b=s.partition('-'); want|=set(range(int(a),int(b or a)+1))
for n in sorted(want):
    if n in P: print(f'--- {k} p{n}'); print(re.sub(r'\n(?=\S{0,3}\n)','',P[n])[:mx])
