import pymupdf,os,sys
R=os.environ.get('ENN583_DIR', '..')  # subject folder holding Week-*/ and Final-Exam/
idx={l.split('\t')[0]:l.strip().split('\t')[4] for l in open('src/extract/index.tsv')}
names={'EX':'notes/practice-exam.pdf','P02a':'notes/papers/SuperGlue.pdf','P02b':'notes/papers/LightGlue.pdf','P04':'notes/papers/VO_Part_I.pdf','P05':'notes/papers/VO_Part_II.pdf','P07':'notes/papers/ORB-SLAM3.pdf','P08':'notes/papers/ViT.pdf','P09':'notes/papers/DUSt3R.pdf','P10':'notes/papers/DETR.pdf','P11':'notes/papers/Contact-GraspNet.pdf','P12':'notes/papers/AnyLoc.pdf','P13':'notes/papers/Kendall-Gal-Uncertainty.pdf'}
for i in range(1,14): names[f'L{i:02d}']=f'notes/Week{i:02d}.pdf'
os.makedirs('notes/papers',exist_ok=True)
for k,out in sorted(names.items()):
    src=R+'/'+idx[k]; d=pymupdf.open(src)
    try: d.rewrite_images(dpi_threshold=130,dpi_target=110,quality=70)
    except Exception as e: print('rewrite fail',k,e)
    d.set_metadata({}); d.del_xml_metadata()
    d.save(out,garbage=4,deflate=True)
    print(f'{k} {os.path.getsize(src)/1e6:.1f}MB -> {os.path.getsize(out)/1e6:.1f}MB {out}',flush=True)
