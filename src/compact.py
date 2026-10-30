import re,sys,glob
for f in sorted(glob.glob('L*.txt')):
    if f.endswith('c.txt'): continue
    pages=re.split(r'(?m)^(=== p\d+ \[\d+\])\n',open(f).read())[1:]
    P=[(pages[i],pages[i+1].strip()) for i in range(0,len(pages),2)]
    out=[]
    for i,(h,t) in enumerate(P):
        L=set(l.strip() for l in t.split('\n') if l.strip())
        if i+1<len(P):
            N=set(l.strip() for l in P[i+1][1].split('\n') if l.strip())
            if L<=N: continue
        out.append(h.split(' [')[0]+'\n'+t)
    open(f[:-4]+'c.txt','w').write('\n'.join(out))
    print(f, len(P),'->',len(out))
