(function(){
'use strict';
var PFX='enn583';
function ls(k,v){try{if(v===undefined)return localStorage.getItem(PFX+k);if(v===null)localStorage.removeItem(PFX+k);else localStorage.setItem(PFX+k,v);return true}catch(e){return v===undefined?null:false}}
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};

/* ---------- theme ---------- */
var root=document.documentElement;
function applyTheme(t){if(t)root.setAttribute('data-theme',t);else root.removeAttribute('data-theme')}
applyTheme(ls('theme'));
$('#themeBtn').addEventListener('click',function(){
  var cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
  var nxt=cur==='dark'?'light':'dark';applyTheme(nxt);ls('theme',nxt);
});

/* ---------- MathJax per panel ---------- */
var typeset={},mjQueue=[];
function typesetPanel(p){
  if(typeset[p.dataset.panel])return;
  if(window.MathJax&&MathJax.typesetPromise){typeset[p.dataset.panel]=1;MathJax.typesetPromise([p]).catch(function(){})}
  else mjQueue.push(p);
}
window.__mjReady=function(){var q=mjQueue;mjQueue=[];q.forEach(typesetPanel)};

/* ---------- tabs ---------- */
var tabs=$$('nav.tabs button[data-tab]'),panels=$$('section[data-panel]');
var ids=tabs.map(function(b){return b.dataset.tab});
function show(id,noScroll){
  if(ids.indexOf(id)<0)id=ids[0];
  tabs.forEach(function(b){b.setAttribute('aria-selected',b.dataset.tab===id?'true':'false')});
  panels.forEach(function(p){p.hidden=p.dataset.panel!==id});
  var p=$('section[data-panel="'+id+'"]');typesetPanel(p);
  if(location.hash!=='#'+id){try{history.replaceState(null,'','#'+id)}catch(e){location.hash=id}}
  ls('tab',id);
  if(!noScroll)window.scrollTo(0,0);
  if(id==='plan')renderPlanStats();
  Viewer.onTab(id);
}
tabs.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.tab)})});
window.addEventListener('hashchange',function(){show(location.hash.slice(1))});
document.addEventListener('click',function(e){var a=e.target.closest('[data-goto]');if(a){e.preventDefault();show(a.dataset.goto)}});

/* ---------- downloads ---------- */
var dlNS=null;
if(window.claude&&claude.use){claude.use('downloads').then(function(d){dlNS=d}).catch(function(){})}
function saveBlob(name,blob){
  if(dlNS)return dlNS.save({filename:name,data:blob}).catch(function(){});
  var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();
  setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},2000);return Promise.resolve();
}
function downloadPath(path){
  return fetch(path).then(function(r){if(!r.ok)throw new Error(r.status);return r.blob()})
  .then(function(b){return saveBlob(path.split('/').pop(),b)}).catch(function(err){flash('Download failed: '+err.message)});
}
document.addEventListener('click',function(e){var b=e.target.closest('[data-dl]');if(b){e.preventDefault();downloadPath(b.dataset.dl)}});
function flash(msg){var s=$('#vstatus');if(s){s.textContent=msg}}

/* ---------- videos ---------- */
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-play]');if(!b)return;
  var card=b.closest('.vid'),f=card.querySelector('.frame');if(f){f.remove();return}
  f=document.createElement('div');f.className='frame';
  f.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+b.dataset.play+'?autoplay=1&rel=0" title="YouTube video" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
  card.appendChild(f);
});

/* ---------- self-marks (quiz) ---------- */
function marks(){try{return JSON.parse(ls('marks')||'{}')}catch(e){return {}}}
function setMark(id,v){var m=marks();if(m[id]===v)delete m[id];else m[id]=v;ls('marks',JSON.stringify(m));paintMarks()}
function paintMarks(){var m=marks();$$('.q[data-qid]').forEach(function(q){var v=m[q.dataset.qid];
  var y=q.querySelector('.self .y'),n=q.querySelector('.self .n');if(y){y.classList.toggle('on',v==='y');n.classList.toggle('on',v==='n')}})}
document.addEventListener('click',function(e){var b=e.target.closest('.self button');if(!b)return;var q=b.closest('.q');setMark(q.dataset.qid,b.classList.contains('y')?'y':'n')});
document.addEventListener('toggle',function(e){var d=e.target;if(d.matches&&d.matches('details.sol')){var q=d.closest('.q');if(q)q.classList.toggle('rev',d.open)}},true);
paintMarks();

/* ---------- plan ---------- */
function planState(){try{return JSON.parse(ls('plan')||'{}')}catch(e){return {}}}
$$('.day input[type=checkbox]').forEach(function(cb){
  var st=planState();cb.checked=!!st[cb.id];cb.closest('.day').classList.toggle('done',cb.checked);
  cb.addEventListener('change',function(){var s=planState();s[cb.id]=cb.checked;ls('plan',JSON.stringify(s));cb.closest('.day').classList.toggle('done',cb.checked)});
});
function renderPlanStats(){
  var el=$('#weakList');if(!el)return;var m=marks(),cnt={},ok={};
  Object.keys(m).forEach(function(k){var t=k.split('-')[0];if(m[k]==='n')cnt[t]=(cnt[t]||0)+1;else ok[t]=(ok[t]||0)+1});
  var names=SITE.topicNames,rows=Object.keys(names).map(function(t){return [t,cnt[t]||0,ok[t]||0]}).filter(function(r){return r[1]||r[2]});
  rows.sort(function(a,b){return b[1]-a[1]});
  el.innerHTML=rows.length?'<div class="tw"><table><tr><th>Topic</th><th>✗ revisit</th><th>✓ got it</th></tr>'+rows.map(function(r){return '<tr><td><a href="#'+r[0]+'" data-goto="'+r[0]+'">'+names[r[0]]+'</a></td><td>'+r[1]+'</td><td>'+r[2]+'</td></tr>'}).join('')+'</table></div>':'<p class="note">No self-marks yet. Mark questions ✓ or ✗ as you practise and your weak topics will show up here.</p>';
}

/* ---------- widgets ---------- */
function f(x,d){if(!isFinite(x))return '∞';return Number(x).toFixed(d===undefined?3:d)}
function nums(s){return String(s).split(/[ ,;]+/).filter(Boolean).map(Number)}
var W={
 grad:{t:'Image gradient',in:[['Ix','∂I/∂x',-100,100,1,30],['Iy','∂I/∂y',-100,100,1,40]],run:function(v){var m=Math.hypot(v.Ix,v.Iy),th=Math.atan2(v.Iy,v.Ix)*180/Math.PI;return '|∇I| = √('+v.Ix+'² + '+v.Iy+'²) = '+f(m,2)+'\nθ = atan2(Iy, Ix) = '+f(th,1)+'°  (points across the edge, towards brighter)'}},
 chroma:{t:'Chromaticity vs raw red',in:[['R','R',0,255,1,200],['G','G',0,255,1,50],['B','B',0,255,1,50]],run:function(v){var s=v.R+v.G+v.B||1,r=v.R/s;return 'r = R/(R+G+B) = '+f(r)+'\nraw test R>150: '+(v.R>150?'RED':'not red')+'   chroma test r>0.5: '+(r>0.5?'RED':'not red')+'\nTry R=G=B=250 (white): raw says red, chromaticity says no.'}},
 ratio:{t:'Lowe ratio test',in:[['d1','best distance',0,100,1,35],['d2','second-best distance',1,100,1,40],['th','threshold θ',0.5,1,0.01,0.8]],run:function(v){var r=v.d1/v.d2;return 'ratio = '+v.d1+' / '+v.d2+' = '+f(r)+'\n'+(r<v.th?'ACCEPT (ratio < θ: best match is clearly better)':'REJECT (ratio ≥ θ: ambiguous, second best is too close)')}},
 pinhole:{t:'Pinhole projection',in:[['fmm','focal length f (mm)',1,20,0.1,5],['pum','pixel size (µm)',1,30,0.1,20],['X','X (m)',-2,2,0.05,0.4],['Y','Y (m)',-2,2,0.05,-0.2],['Z','Z depth (m)',0.2,20,0.1,2],['u0','u0 (px)',0,1000,1,320],['v0','v0 (px)',0,1000,1,240]],run:function(v){var fp=v.fmm*1e-3/(v.pum*1e-6);return 'f in pixels = f/ρ = '+f(fp,1)+' px\nu = u0 + f·X/Z = '+v.u0+' + '+f(fp,1)+'·'+v.X+'/'+v.Z+' = '+f(v.u0+fp*v.X/v.Z,1)+'\nv = v0 + f·Y/Z = '+v.v0+' + '+f(fp,1)+'·'+v.Y+'/'+v.Z+' = '+f(v.v0+fp*v.Y/v.Z,1)}},
 stereo:{t:'Stereo depth and baseline trade-off',in:[['f','focal length f (px)',100,1500,10,700],['b','baseline b (m)',0.02,1,0.01,0.12],['d','disparity d (px)',1,300,1,20],['dd','disparity noise δd (px)',0.1,2,0.1,0.5],['dmax','max search disparity (px)',16,512,1,128]],run:function(v){var Z=v.f*v.b/v.d;return 'Z = f·b/d = '+v.f+'·'+v.b+'/'+v.d+' = '+f(Z)+' m\ndepth error δZ ≈ Z²·δd/(f·b) = '+f(Z*Z*v.dd/(v.f*v.b))+' m\nclosest measurable depth Zmin = f·b/dmax = '+f(v.f*v.b/v.dmax)+' m\n↑ b: smaller δZ but larger Zmin.'}},
 ransac:{t:'RANSAC iterations',in:[['w','inlier ratio w',0.05,0.99,0.01,0.5],['n','minimal sample n',1,10,1,8],['p','confidence p',0.5,0.9999,0.0001,0.99]],run:function(v){var k=Math.log(1-v.p)/Math.log(1-Math.pow(v.w,v.n));return 'P(sample all inliers) = wⁿ = '+f(Math.pow(v.w,v.n),5)+'\nk = log(1−p)/log(1−wⁿ) = '+f(k,2)+'  → run '+Math.ceil(k)+' iterations\nCompare n = 8 (F), 5 (E), 3 (P3P), 2 (line).'}},
 reproj:{t:'PnP inlier test',in:[['pu','predicted u',0,640,1,100],['pv','predicted v',0,480,1,80],['ou','observed u',0,640,1,97],['ov','observed v',0,480,1,84],['th','threshold (px)',0.5,20,0.5,6]],run:function(v){var du=v.ou-v.pu,dv=v.ov-v.pv,e=Math.hypot(du,dv);return 'residual = observed − predicted = ('+du+', '+dv+')\n‖r‖ = '+f(e,2)+' px → '+(e<v.th?'INLIER':'OUTLIER')+' (threshold '+v.th+' px)'}},
 posegraph:{t:'1-D pose graph with a loop closure',in:[['so','σ odometry',0.05,1,0.01,0.1],['sl','σ loop',0.02,2,0.01,0.1],['z','loop measurement x2−x0',1,2.5,0.01,1.8]],run:function(v){var wo=1/(v.so*v.so),wl=1/(v.sl*v.sl);
   var a11=2*wo,a12=-wo,a22=wo+wl,b1=0,b2=wo*1+wl*v.z; b1=wo*1-wo*1; var det=a11*a22-a12*a12,x1=(b1*a22-a12*b2)/det,x2=(a11*b2-a12*b1)/det;
   return 'x0 = 0 fixed; odometry says x1−x0 = 1, x2−x1 = 1; loop says x2−x0 = '+v.z+'\nweights 1/σ²: odom '+f(wo,1)+', loop '+f(wl,1)+'\nMAP: x1 = '+f(x1)+', x2 = '+f(x2)+'\n(chained odometry alone would give x2 = 2.000)'}},
 fusion:{t:'Fusing two Gaussians',in:[['m1','prior mean',0,10,0.1,5],['s1','prior σ',0.1,3,0.05,1],['m2','measurement mean',0,10,0.1,6],['s2','measurement σ',0.1,3,0.05,0.5]],run:function(v){var w1=1/(v.s1*v.s1),w2=1/(v.s2*v.s2),m=(w1*v.m1+w2*v.m2)/(w1+w2),s=Math.sqrt(1/(w1+w2));return 'posterior mean = (m1/σ1² + m2/σ2²)/(1/σ1² + 1/σ2²) = '+f(m)+'\nposterior σ = '+f(s)+'  (smaller than both inputs)'}},
 ate:{t:'ATE RMSE',in:[['e','position errors after alignment (m)','text','0.3, 0.4, 0, 1.2']],run:function(v){var a=nums(v.e);if(!a.length)return 'enter numbers';var r=Math.sqrt(a.reduce(function(s,x){return s+x*x},0)/a.length),mean=a.reduce(function(s,x){return s+x},0)/a.length,b=a.slice().sort(function(x,y){return x-y}),med=b.length%2?b[(b.length-1)/2]:(b[b.length/2-1]+b[b.length/2])/2;return 'RMSE = √(Σe²/n) = '+f(r)+' m\nmean = '+f(mean)+' m, median = '+f(med)+' m\nOne big error inflates RMSE more than the median.'}},
 imu:{t:'IMU accelerometer bias drift',in:[['b','bias (m/s²)',0.001,0.5,0.001,0.05],['t','time (s)',1,120,1,10]],run:function(v){return 'position error = ½·b·t² = 0.5·'+v.b+'·'+v.t+'² = '+f(0.5*v.b*v.t*v.t,2)+' m (grows quadratically)'}},
 vit:{t:'ViT tokens and attention cost',in:[['H','image size (px)',32,1024,16,224],['P','patch size P',4,64,2,16]],run:function(v){var n=Math.floor(v.H/v.P)*Math.floor(v.H/v.P);return 'N = HW/P² = '+n+' patches (+1 class token = '+(n+1)+')\neach patch vector = P·P·3 = '+(v.P*v.P*3)+' numbers before projection\nattention pairs ≈ N² = '+n*n+'   (halve P → 4× tokens → 16× attention cost)'}},
 softmax:{t:'Attention weights from scores',in:[['s','query·key scores','text','2.4, 2.1, 0.8, -0.5']],run:function(v){var a=nums(v.s),m=Math.max.apply(null,a),e=a.map(function(x){return Math.exp(x-m)}),s=e.reduce(function(p,x){return p+x},0);return 'softmax weights: '+e.map(function(x){return f(x/s)}).join(', ')+'\n(sum to 1; the message is Σ aᵢⱼ vⱼ)'}},
 iou:{t:'Box IoU',in:[['a','box A x1,y1,x2,y2','text','0,0,4,4'],['b','box B x1,y1,x2,y2','text','2,2,6,6'],['th','IoU threshold',0.1,0.95,0.05,0.5]],run:function(v){var A=nums(v.a),B=nums(v.b);if(A.length<4||B.length<4)return 'enter 4 numbers each';var iw=Math.max(0,Math.min(A[2],B[2])-Math.max(A[0],B[0])),ih=Math.max(0,Math.min(A[3],B[3])-Math.max(A[1],B[1])),I=iw*ih,aA=(A[2]-A[0])*(A[3]-A[1]),aB=(B[2]-B[0])*(B[3]-B[1]),U=aA+aB-I;return 'intersection = '+f(I,2)+', union = '+aA+' + '+aB+' − '+f(I,2)+' = '+f(U,2)+'\nIoU = '+f(I/U)+' → '+(I/U>=v.th?'TP (if class right)':'FP at this threshold')}},
 pr:{t:'Precision, recall and AP from a ranked list',in:[['s','detections by confidence (1 = TP, 0 = FP)','text','1 1 0 1 0 0 1'],['g','ground-truth objects',1,30,1,5]],run:function(v){var a=nums(v.s),tp=0,fp=0,P=[],R=[];a.forEach(function(x){if(x)tp++;else fp++;P.push(tp/(tp+fp));R.push(tp/v.g)});
   var ap=0,prev=0;for(var i=0;i<P.length;i++){var mx=Math.max.apply(null,P.slice(i));if(R[i]>prev){ap+=(R[i]-prev)*mx;prev=R[i]}}
   return P.map(function(p,i){return '#'+(i+1)+' '+(a[i]?'TP':'FP')+'  P='+f(p)+'  R='+f(R[i])}).join('\n')+'\nAP (all-point interpolation) = '+f(ap)}},
 imbalance:{t:'Class imbalance in segmentation',in:[['o','obstacle pixel fraction',0.01,0.5,0.01,0.05]],run:function(v){var bg=1-v.o;return 'predict "background" everywhere:\npixel accuracy = '+f(bg)+'\nIoU(background) = '+f(bg)+', IoU(obstacle) = 0\nmean IoU = '+f(bg/2)+'\nAccuracy looks great; obstacle recall is zero.'}},
 cosine:{t:'Cosine similarity',in:[['q','query q','text','0.6, 0.8'],['a','database a','text','0.8, 0.6'],['b','database b','text','0, 1']],run:function(v){function c(x,y){var d=0,nx=0,ny=0;for(var i=0;i<x.length;i++){d+=x[i]*y[i];nx+=x[i]*x[i];ny+=y[i]*y[i]}return d/Math.sqrt(nx*ny)}var q=nums(v.q),a=nums(v.a),b=nums(v.b),ca=c(q,a),cb=c(q,b);return 'cos(q,a) = '+f(ca)+'\ncos(q,b) = '+f(cb)+'\nranked first: '+(ca>=cb?'a':'b')}},
 recallk:{t:'Recall@K',in:[['r','rank of first correct match per query (- = none)','text','2 5 1 6 -'],['k','K',1,10,1,2]],run:function(v){var a=String(v.r).split(/[ ,;]+/).filter(Boolean),hit=a.filter(function(x){return x!=='-'&&+x<=v.k}).length;return 'queries with a correct match in the top '+v.k+': '+hit+' of '+a.length+'\nRecall@'+v.k+' = '+f(hit/a.length)}},
 temp:{t:'Softmax, temperature and energy',in:[['z','logits','text','2, 1, 0'],['T','temperature T',0.25,5,0.05,1]],run:function(v){var z=nums(v.z),m=Math.max.apply(null,z),e=z.map(function(x){return Math.exp((x-m)/v.T)}),s=e.reduce(function(p,x){return p+x},0),p=e.map(function(x){return x/s}),H=-p.reduce(function(a,x){return a+(x>0?x*Math.log(x):0)},0),E=-(m+Math.log(z.reduce(function(a,x){return a+Math.exp(x-m)},0)));
   return 'p = '+p.map(function(x){return f(x)}).join(', ')+'\nmax prob = '+f(Math.max.apply(null,p))+', entropy H = '+f(H)+' nats\nenergy E = −log Σ exp(z) = '+f(E)+' (on raw logits, T=1)\nT>1 softens, T<1 sharpens; argmax never changes.'}},
 selective:{t:'Coverage and selective risk',in:[['n','inputs',1,500,1,50],['a','abstained',0,500,1,10],['w','wrong among predictions',0,500,1,4]],run:function(v){var p=v.n-v.a;if(p<=0)return 'no predictions made';return 'coverage = predicted/all = '+p+'/'+v.n+' = '+f(p/v.n)+'\nselective risk = wrong/predicted = '+v.w+'/'+p+' = '+f(v.w/p)}},
 calib:{t:'Reliability bin',in:[['c','mean confidence in bin',0,1,0.01,0.6],['n','predictions in bin',1,200,1,10],['k','correct',0,200,1,8]],run:function(v){var a=v.k/v.n,g=a-v.c;return 'accuracy = '+v.k+'/'+v.n+' = '+f(a)+'\naccuracy − confidence = '+f(g)+' → '+(Math.abs(g)<0.005?'calibrated':g>0?'UNDER-confident by '+f(g):'OVER-confident by '+f(-g))}}
};
function buildWidget(el){
  var spec=W[el.dataset.w];if(!spec)return;
  var h='<div class="wt">⚙ '+spec.t+'</div><div class="ctl">';
  spec.in.forEach(function(i){var id=el.dataset.w+'_'+i[0]+'_'+(el.dataset.n||'0');
    if(i[2]==='text')h+='<label for="'+id+'">'+i[1]+'<input type="text" id="'+id+'" data-k="'+i[0]+'" value="'+i[3]+'"></label>';
    else h+='<label for="'+id+'">'+i[1]+': <span>'+i[5]+'</span><input type="range" id="'+id+'" data-k="'+i[0]+'" min="'+i[2]+'" max="'+i[3]+'" step="'+i[4]+'" value="'+i[5]+'"></label>';});
  h+='</div><div class="out" aria-live="polite"></div>';el.innerHTML=h;
  function upd(){var v={};$$('input',el).forEach(function(x){v[x.dataset.k]=x.type==='range'?parseFloat(x.value):x.value;if(x.type==='range')x.previousElementSibling.textContent=x.value});
    try{$('.out',el).textContent=spec.run(v)}catch(e){$('.out',el).textContent='Check the inputs.'}}
  el.addEventListener('input',upd);upd();
}
$$('.widget[data-w]').forEach(function(el,i){el.dataset.n=i;buildWidget(el)});

/* ---------- PDF viewer ---------- */
var Viewer=(function(){
  var V=$('#viewer'),scroller=$('#vscroll'),sel=$('#vdoc'),pct=$('#vpct'),status=$('#vstatus');
  var pdfLib=null,doc=null,path=null,pages=[],scale=1,fit=ls('fit')||'width',tool='hand',color='#d32f2f';
  var strokes=[],undo=[],io=null,loadToken=0,current=null,restoredMsg='',persistAsked=false;
  function whenPdf(){return new Promise(function(res,rej){var t0=Date.now();(function poll(){
    if(window.pdfjsLib&&window.__pdfWorker){pdfLib=window.pdfjsLib;pdfLib.GlobalWorkerOptions.workerSrc=window.__pdfWorker;res(pdfLib)}
    else if(Date.now()-t0>15000)rej(new Error('PDF library did not load'));else setTimeout(poll,100)})()})}
  function msg(t){status.textContent=t}
  function key(){return PFX+'ann:'+path}
  function loadStrokes(){strokes=[];undo=[];try{var s=localStorage.getItem(key());if(s)strokes=JSON.parse(s)}catch(e){msg('Saved marks could not be read in this browser.')}}
  function saveStrokes(){
    try{if(strokes.length)localStorage.setItem(key(),JSON.stringify(strokes));else localStorage.removeItem(key());
      if(!persistAsked&&navigator.storage&&navigator.storage.persist){persistAsked=true;navigator.storage.persist().catch(function(){})}
    }catch(e){msg('Marks could not be saved: this browser is blocking storage (private window or full storage). They will be lost on reload.')}
  }
  function docsFor(tab){return (SITE.docs[tab]||[])}
  function fillSelect(list){
    var all=list.slice();if(path&&!all.some(function(d){return d.path===path})&&current)all.unshift(current);
    sel.innerHTML=all.map(function(d){return '<option value="'+d.path+'">'+d.title+' ('+d.pages+' pp)</option>'}).join('');
    if(path)sel.value=path;
  }
  function setOpen(o){V.hidden=!o;document.body.classList.toggle('vopen',o);ls('vopen',o?'1':'0');if(!o&&V.classList.contains('max'))V.classList.remove('max')}
  function open(p,page){
    var info=null;Object.keys(SITE.docs).forEach(function(t){SITE.docs[t].forEach(function(d){if(d.path===p)info=d})});
    if(!info&&SITE.extraDocs)info=SITE.extraDocs[p];
    current=info||{path:p,title:p,pages:'?'};
    setOpen(true);
    var tab=ls('tab');fillSelect(docsFor(tab).length?docsFor(tab):[current]);
    if(p===path&&doc){if(page)goPage(page);return}
    load(p,page);
  }
  function load(p,page){
    var tok=++loadToken;if(io){io.disconnect();io=null}path=p;sel.value=p;scroller.innerHTML='';pages=[];doc=null;msg('Loading '+p+' …');
    loadStrokes();var n=strokes.length;restoredMsg=n?(n+' mark'+(n>1?'s':'')+' restored'):'';
    whenPdf().then(function(lib){return lib.getDocument(p).promise}).then(function(d){
      if(tok!==loadToken)return;doc=d;var ps=[];for(var i=1;i<=d.numPages;i++)ps.push(d.getPage(i));
      return Promise.all(ps).then(function(pp){if(tok!==loadToken)return;
        pages=pp.map(function(pg,i){var vp=pg.getViewport({scale:1});return {pg:pg,w:vp.width,h:vp.height,n:i+1,el:null,cv:null,ink:null,rs:0}});
        build();applyFit();msg((restoredMsg?restoredMsg+' · ':'')+d.numPages+' pages');if(page)setTimeout(function(){goPage(page)},50);
      });
    }).catch(function(e){if(tok===loadToken)msg('Could not open this PDF here ('+e.message+'). Try Download.')});
  }
  function build(){
    if(io)io.disconnect();
    io=new IntersectionObserver(function(ents){ents.forEach(function(en){var p=pages[+en.target.dataset.n-1];if(!p||p.el!==en.target)return;p.vis=en.isIntersecting;if(en.isIntersecting)render(p);else release(p)})},{root:scroller,rootMargin:'800px 0px'});
    pages.forEach(function(p){var el=document.createElement('div');el.className='pg';el.dataset.n=p.n;
      el.innerHTML='<canvas class="pdf"></canvas><canvas class="ink"></canvas><span class="lbl">p'+p.n+'</span>';
      p.el=el;p.cv=el.firstChild;p.ink=el.children[1];scroller.appendChild(el);io.observe(el);bindInk(p)});
    setTool(tool);
  }
  function sizeAll(){pages.forEach(function(p){p.el.style.width=Math.round(p.w*scale)+'px';p.el.style.height=Math.round(p.h*scale)+'px';p.rs=0});pct.textContent=Math.round(scale*100)+'%';
    pages.forEach(function(p){if(p.vis)render(p)})}
  function render(p){
    var dpr=Math.min(window.devicePixelRatio||1,2),s=scale*dpr;if(p.rs===s)return;p.rs=s;
    var vp=p.pg.getViewport({scale:s});p.cv.width=vp.width;p.cv.height=vp.height;
    if(p.task)try{p.task.cancel()}catch(e){}
    p.task=p.pg.render({canvasContext:p.cv.getContext('2d'),viewport:vp});p.task.promise.catch(function(){});
    p.ink.width=vp.width;p.ink.height=vp.height;drawInk(p);
  }
  function release(p){if(p.rs){p.cv.width=1;p.cv.height=1;p.ink.width=1;p.ink.height=1;p.rs=0}}
  function avail(){return {w:scroller.clientWidth-26,h:scroller.clientHeight-26}}
  function curPage(){var top=scroller.scrollTop,best=pages[0];pages.forEach(function(p){if(p.el.offsetTop-20<=top)best=p});return best}
  function applyFit(){if(!pages.length)return;var a=avail(),p=curPage()||pages[0],keep=p?p.n:1;
    if(fit==='width')scale=a.w/p.w;else if(fit==='page')scale=Math.min(a.w/p.w,a.h/p.h);
    scale=Math.max(0.25,Math.min(3,scale));sizeAll();goPage(keep)}
  function zoomTo(s,keepFrac){var frac=scroller.scrollTop/(scroller.scrollHeight||1);scale=Math.max(0.25,Math.min(3,s));fit='custom';ls('fit',fit);sizeAll();scroller.scrollTop=frac*scroller.scrollHeight;markFit()}
  function goPage(n){var p=pages[n-1];if(p)scroller.scrollTop=p.el.offsetTop-8}
  function markFit(){$('#vfw').classList.toggle('on',fit==='width');$('#vfp').classList.toggle('on',fit==='page')}
  /* ink */
  function drawInk(p){var c=p.ink,ctx=c.getContext('2d');ctx.clearRect(0,0,c.width,c.height);
    strokes.forEach(function(s){if(s.p!==p.n||s.pts.length<1)return;ctx.save();ctx.lineCap='round';ctx.lineJoin='round';ctx.strokeStyle=s.c;
      ctx.globalAlpha=s.t==='hl'?0.35:1;ctx.lineWidth=s.w*c.width;ctx.beginPath();
      s.pts.forEach(function(q,i){var x=q[0]*c.width,y=q[1]*c.height;if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y)});
      if(s.pts.length===1)ctx.lineTo(s.pts[0][0]*c.width+0.1,s.pts[0][1]*c.height);ctx.stroke();ctx.restore()})}
  function rel(p,e){var r=p.ink.getBoundingClientRect();return [Math.round((e.clientX-r.left)/r.width*1e4)/1e4,Math.round((e.clientY-r.top)/r.height*1e4)/1e4]}
  function bindInk(p){var cur=null;
    p.ink.addEventListener('pointerdown',function(e){if(tool==='hand')return;e.preventDefault();p.ink.setPointerCapture(e.pointerId);
      if(tool==='eraser'){erase(p,rel(p,e));cur={erasing:true};return}
      cur={p:p.n,t:tool,c:tool==='hl'&&color!=='#f9d71c'?color:color,w:tool==='hl'?0.018:0.0028,pts:[rel(p,e)]};strokes.push(cur);drawInk(p)});
    p.ink.addEventListener('pointermove',function(e){if(!cur)return;if(cur.erasing){erase(p,rel(p,e));return}var q=rel(p,e),l=cur.pts[cur.pts.length-1];if(Math.abs(q[0]-l[0])+Math.abs(q[1]-l[1])>0.002){cur.pts.push(q);drawInk(p)}});
    function end(){if(!cur)return;if(!cur.erasing){undo.push({a:'add',s:cur});saveStrokes();msg(strokes.length+' mark'+(strokes.length===1?'':'s')+' on this PDF (saved in this browser)')}cur=null}
    p.ink.addEventListener('pointerup',end);p.ink.addEventListener('pointercancel',end);
  }
  function erase(p,q){var hit=[];strokes.forEach(function(s,i){if(s.p!==p.n)return;var tol=Math.max(0.012,s.w);for(var j=0;j<s.pts.length;j++){if(Math.abs(s.pts[j][0]-q[0])<tol&&Math.abs(s.pts[j][1]-q[1])<tol*(p.w/p.h)){hit.push(i);break}}});
    if(!hit.length)return;var removed=[];for(var k=hit.length-1;k>=0;k--){removed.push({i:hit[k],s:strokes[hit[k]]});strokes.splice(hit[k],1)}
    undo.push({a:'del',items:removed});saveStrokes();drawInk(p)}
  function redrawAll(){pages.forEach(function(p){if(p.rs)drawInk(p)})}
  function doUndo(){var u=undo.pop();if(!u){msg('Nothing to undo');return}
    if(u.a==='add'){var i=strokes.indexOf(u.s);if(i>=0)strokes.splice(i,1)}
    else if(u.a==='del'){u.items.slice().reverse().forEach(function(it){strokes.splice(it.i,0,it.s)})}
    else if(u.a==='clear'){strokes=u.prev}
    saveStrokes();redrawAll();msg('Undone')}
  function setTool(t){tool=t;$$('#vtools [data-tool]').forEach(function(b){b.classList.toggle('on',b.dataset.tool===t)});
    V.classList.toggle('drawing',t!=='hand');pages.forEach(function(p){p.ink.style.pointerEvents=t==='hand'?'none':'auto'})}
  /* controls */
  $$('#vtools [data-tool]').forEach(function(b){b.addEventListener('click',function(){setTool(b.dataset.tool)})});
  $$('#vtools .sw').forEach(function(b){b.addEventListener('click',function(){color=b.dataset.c;$$('#vtools .sw').forEach(function(x){x.classList.toggle('on',x===b)});if(tool==='hand'||tool==='eraser')setTool('pen')})});
  $('#vundo').addEventListener('click',doUndo);
  $('#vclear').addEventListener('click',function(){$('#vconfirm').hidden=false});
  $('#vcn').addEventListener('click',function(){$('#vconfirm').hidden=true});
  $('#vcy').addEventListener('click',function(){$('#vconfirm').hidden=true;undo.push({a:'clear',prev:strokes});strokes=[];saveStrokes();redrawAll();msg('All marks cleared (Undo brings them back)')});
  $('#vzi').addEventListener('click',function(){zoomTo(scale*1.2)});
  $('#vzo').addEventListener('click',function(){zoomTo(scale/1.2)});
  $('#vfw').addEventListener('click',function(){fit='width';ls('fit',fit);markFit();applyFit()});
  $('#vfp').addEventListener('click',function(){fit='page';ls('fit',fit);markFit();applyFit()});
  $('#vcl').addEventListener('click',function(){if(document.fullscreenElement)document.exitFullscreen().catch(function(){});setOpen(false)});
  $('#vdl').addEventListener('click',function(){if(path)downloadPath(path)});
  $('#vfs').addEventListener('click',function(){
    if(document.fullscreenElement||V.classList.contains('max')){if(document.fullscreenElement)document.exitFullscreen().catch(function(){});V.classList.remove('max');setTimeout(applyFitIf,120);return}
    var r=V.requestFullscreen?V.requestFullscreen():null;
    if(r&&r.then)r.then(function(){setTimeout(applyFitIf,120)}).catch(function(){V.classList.add('max');setTimeout(applyFitIf,60)});else{V.classList.add('max');setTimeout(applyFitIf,60)}});
  document.addEventListener('fullscreenchange',function(){setTimeout(applyFitIf,120)});
  sel.addEventListener('change',function(){load(sel.value)});
  function applyFitIf(){if(fit==='width'||fit==='page')applyFit()}
  var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(applyFitIf,150)});
  scroller.addEventListener('wheel',function(e){if(e.ctrlKey||e.metaKey){e.preventDefault();zoomTo(scale*Math.exp(-e.deltaY*0.0025))}},{passive:false});
  var pinch=null;
  scroller.addEventListener('touchstart',function(e){if(e.touches.length===2){pinch={d:dist(e.touches),s:scale}}},{passive:true});
  scroller.addEventListener('touchmove',function(e){if(pinch&&e.touches.length===2){e.preventDefault();var s=pinch.s*dist(e.touches)/pinch.d;scale=Math.max(0.25,Math.min(3,s));fit='custom';pages.forEach(function(p){p.el.style.width=Math.round(p.w*scale)+'px';p.el.style.height=Math.round(p.h*scale)+'px'});pct.textContent=Math.round(scale*100)+'%'}},{passive:false});
  scroller.addEventListener('touchend',function(e){if(pinch&&e.touches.length<2){pinch=null;ls('fit','custom');markFit();sizeAll()}});
  function dist(t){return Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY)}
  document.addEventListener('click',function(e){var b=e.target.closest('[data-view]');if(b){e.preventDefault();open(b.dataset.view,b.dataset.p?+b.dataset.p:0)}});
  markFit();
  return {
    open:open,
    onTab:function(tab){var list=docsFor(tab);if(V.hidden){return}
      if(list.length){if(!list.some(function(d){return d.path===path}))open(list[0].path);else fillSelect(list)}},
    restore:function(){var tab=ls('tab'),list=docsFor(tab);if(ls('vopen')==='1'&&list.length)open(list[0].path)},
    _state:function(){return {path:path,scale:scale,strokes:strokes.length,pages:pages.length,fit:fit}}
  };
})();
window.__viewer=Viewer;

/* ---------- boot ---------- */
var start=location.hash.slice(1)||ls('tab')||ids[0];
show(start,true);
Viewer.restore();
})();
