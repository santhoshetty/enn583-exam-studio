import pymupdf, glob, os, re, sys, hashlib
R=os.environ.get('ENN583_DIR', '..')  # subject folder holding Week-*/ and Final-Exam/
OUT=os.path.join(os.path.dirname(__file__),'extract')
docs={}
for p in glob.glob(R+'/Week-*/Lecture/*.pdf'):
    w=int(re.search(r'Week-(\d+)',p).group(1)); docs[f'L{w:02d}']=p
pap={'P02a':'Week-2*/Tutorial/SuperGlue/SuperGlue.pdf','P02b':'Week-2*/Tutorial/LightGlue/LightGlue-Paper.pdf','P02s':'Week-2*/Tutorial/SuperGlue/superglue_slides.pdf',
'P04':'Week-4*/Tutorial/VO_Part_I_Scaramuzza.pdf','P05':'Week-5*/Tutorial/VO_Part_II_Scaramuzza.pdf','P07':'Week-7*/Tutorial/ORB-SLAM3.pdf',
'P08':'Week-8*/Tutorial/Vision Transformers.pdf','P09':'Week-9*/Tutorial/DUSt3R.pdf','P10':'Week-10*/Tutorial/End-to-End*.pdf',
'P11':'Week-11*/Tutorial/Contact-GraspNet.pdf','P12':'Week-12*/Tutorial/AnyLoc.pdf','P13':'Week-13*/Tutorial/What-Uncertainties*.pdf','EX':'Final-Exam/*.pdf'}
for k,g in pap.items(): docs[k]=glob.glob(R+'/'+g)[0]
with open(OUT+'/index.tsv','w') as idx:
  for k,p in sorted(docs.items()):
    d=pymupdf.open(p); lines=[]; counts=[]
    for i,pg in enumerate(d):
        t=pg.get_text(); t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n\s*\n+','\n',t).strip()
        counts.append(len(t)); lines.append(f'=== p{i+1} [{len(t)}]\n{t}')
    open(f'{OUT}/{k}.txt','w').write('\n'.join(lines))
    idx.write(f'{k}\t{len(d)}\t{sum(counts)}\t{hashlib.md5(open(p,"rb").read()).hexdigest()[:8]}\t{p[len(R)+1:]}\n')
    low=[i+1 for i,c in enumerate(counts) if c<250]
    print(k,len(d),'pages',sum(counts),'ch; low-text pages:',len(low))
