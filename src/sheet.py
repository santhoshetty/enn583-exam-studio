import pymupdf,sys,glob,os
from PIL import Image, ImageDraw
# sheet.py KEY pages out.png [cols] [width_per_page]
R=os.environ.get('ENN583_DIR', '..')  # subject folder holding Week-*/ and Final-Exam/
idx={l.split('\t')[0]:l.strip().split('\t')[4] for l in open(os.path.dirname(__file__)+'/extract/index.tsv')}
d=pymupdf.open(R+'/'+idx[sys.argv[1]])
pages=[]
for s in sys.argv[2].split(','):
    a,_,b=s.partition('-'); pages+=list(range(int(a),int(b or a)+1))
cols=int(sys.argv[4]) if len(sys.argv)>4 else 3; W=int(sys.argv[5]) if len(sys.argv)>5 else 420
ims=[]
for p in pages:
    pg=d[p-1]; z=W/pg.rect.width; pix=pg.get_pixmap(matrix=pymupdf.Matrix(z,z),colorspace=pymupdf.csGRAY)
    im=Image.frombytes('L',(pix.width,pix.height),pix.samples); ImageDraw.Draw(im).text((4,4),f'p{p}',fill=0); ims.append(im)
h=max(i.height for i in ims); rows=(len(ims)+cols-1)//cols
S=Image.new('L',(cols*W,rows*h),255)
for k,i in enumerate(ims): S.paste(i,((k%cols)*W,(k//cols)*h))
S.save(sys.argv[3]); print(S.size)
