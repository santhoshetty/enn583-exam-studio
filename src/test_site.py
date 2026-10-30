"""Headless Chromium checks for the study site (served over http://localhost)."""
import os, json, subprocess, time, sys
from playwright.sync_api import sync_playwright
EXE=os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
srv=subprocess.Popen([sys.executable,'-m','http.server','8765'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
URL='http://localhost:8765/preview.html'; R=[]
def ok(name,cond,extra=''): R.append((name,bool(cond),extra)); print(('PASS ' if cond else 'FAIL ')+name,extra)
try:
  with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE)
    ctx=b.new_context(viewport={'width':1400,'height':900},accept_downloads=True); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(2500)
    tabs=pg.eval_on_selector_all('nav.tabs button[data-tab]','bs=>bs.map(b=>b.dataset.tab)')
    bad=[]
    for t in tabs:
        pg.click(f'nav.tabs button[data-tab="{t}"]'); pg.wait_for_timeout(120)
        vis=pg.eval_on_selector_all('section[data-panel]','ss=>ss.filter(s=>s.offsetParent!==null||getComputedStyle(s).display!="none").map(s=>s.dataset.panel)')
        if vis!=[t]: bad.append((t,vis))
    ok(f'{len(tabs)} tabs each show only their panel',not bad,str(bad[:2]))
    pg.click('nav.tabs button[data-tab="w03"]'); pg.wait_for_timeout(3000)
    ok('MathJax typeset W3',pg.eval_on_selector_all('section[data-panel="w03"] mjx-container','x=>x.length')>5)
    ok('widgets render output',pg.eval_on_selector_all('.widget .out','o=>o.filter(x=>x.textContent.length>10).length')>=20)
    # viewer
    pg.click('section[data-panel="w03"] button[data-view]'); pg.wait_for_function('document.querySelectorAll("#vscroll .pg").length>50',timeout=30000)
    pg.wait_for_timeout(2500)
    w1=pg.eval_on_selector('#vscroll .pg','e=>e.getBoundingClientRect().width')
    drawn=pg.evaluate('(()=>{const c=document.querySelector("#vscroll .pg canvas.pdf");return c.width>10})()')
    ok('notes render (107-page W3 lecture)',drawn,f'pages={pg.eval_on_selector_all("#vscroll .pg","x=>x.length")}')
    pg.click('#vzi'); pg.wait_for_timeout(500); w2=pg.eval_on_selector('#vscroll .pg','e=>e.getBoundingClientRect().width')
    ok('zoom in widens page',w2>w1*1.1,f'{w1:.0f}->{w2:.0f}')
    pg.click('#vfp'); pg.wait_for_timeout(500); h=pg.eval_on_selector('#vscroll .pg','e=>e.getBoundingClientRect().height'); sh=pg.eval_on_selector('#vscroll','e=>e.clientHeight')
    ok('fit page fits height',h<=sh,f'{h:.0f}<= {sh}')
    ok('viewer docked right on desktop',pg.evaluate('document.body.classList.contains("vopen")') and pg.eval_on_selector('#viewer','e=>Math.round(e.getBoundingClientRect().width)')<760)
    # pen stroke
    pg.click('#vtools [data-tool="pen"]'); pg.evaluate('document.querySelector("#vscroll").scrollTop=0'); pg.wait_for_timeout(400)
    box=pg.eval_on_selector('#vscroll .pg .ink','e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]}')
    x,y=box[0]+box[2]*0.3,box[1]+box[3]*0.3
    pg.mouse.move(x,y); pg.mouse.down(); pg.mouse.move(x+80,y+30,steps=8); pg.mouse.up(); pg.wait_for_timeout(300)
    key=pg.evaluate('Object.keys(localStorage).filter(k=>k.startsWith("enn583ann:"))')
    ok('pen stroke saved per-PDF key',key==['enn583ann:notes/Week03.pdf'],str(key))
    # slide link + doc select
    pg.click('section[data-panel="w03"] a.sl[data-p="63"]'); pg.wait_for_timeout(1500)
    ok('slide link jumps to page',pg.eval_on_selector('#vscroll','e=>e.scrollTop')>1000)
    pg.click('nav.tabs button[data-tab="w04"]'); pg.wait_for_timeout(1500)
    ok('viewer follows tab (W4 notes)',pg.eval_on_selector('#vdoc','s=>s.value')=='notes/Week04.pdf')
    pg.select_option('#vdoc','notes/papers/VO_Part_I.pdf'); pg.wait_for_function('document.querySelectorAll("#vscroll .pg").length==13',timeout=20000)
    ok('document picker switches to paper',True)
    # self-marks
    pg.click('nav.tabs button[data-tab="past"]'); pg.wait_for_timeout(300)
    pg.click('section[data-panel="past"] .q .self .n'); pg.wait_for_timeout(100)
    # reload persistence
    pg.reload(); pg.wait_for_timeout(2500)
    ok('viewer reopens after reload (remembered open)',pg.evaluate('!document.querySelector("#viewer").hidden'))
    ok('self-mark persists',pg.eval_on_selector('section[data-panel="past"] .q .self .n','e=>e.classList.contains("on")'))
    pg.click('nav.tabs button[data-tab="w03"]'); pg.wait_for_function('document.querySelector("#vdoc").value=="notes/Week03.pdf"&&document.querySelectorAll("#vscroll .pg").length>50',timeout=30000); pg.wait_for_timeout(1500)
    st=pg.inner_text('#vstatus'); ok('pen stroke survives reload',('1 mark restored' in st),st)
    pg.click('nav.tabs button[data-tab="plan"]'); pg.wait_for_timeout(300)
    ok('weak-topic table shows self-mark',pg.inner_text('#weakList').find('✗')>=0 or 'revisit' in pg.inner_text('#weakList'))
    # downloads (fallback path outside claude.ai)
    with pg.expect_download(timeout=15000) as dl: pg.click('nav.tabs button[data-tab="cheat"]'); pg.click('section[data-panel="cheat"] button[data-dl]')
    ok('cheatsheet download fires',dl.value.suggested_filename=='cheatsheet.pdf')
    with pg.expect_download(timeout=20000) as dl2: pg.click('#vdl')
    ok('viewer PDF download fires',dl2.value.suggested_filename.endswith('.pdf'),dl2.value.suggested_filename)
    # video
    pg.click('nav.tabs button[data-tab="w04"]'); pg.click('section[data-panel="w04"] [data-play]'); ok('play injects nocookie iframe',pg.eval_on_selector_all('section[data-panel="w04"] iframe','f=>f.length==1&&f[0].src.includes("youtube-nocookie")'))
    ok('no page errors',not errs,str(errs[:3]))
    ctx.close()
    # fresh browser = no marks
    c2=b.new_context(viewport={'width':1400,'height':900}); p2=c2.new_page(); p2.goto(URL+'#w03'); p2.wait_for_timeout(1500)
    p2.click('section[data-panel="w03"] button[data-view]'); p2.wait_for_function('document.querySelectorAll("#vscroll .pg").length>50',timeout=30000); p2.wait_for_timeout(800)
    ok('fresh visitor sees no marks',p2.evaluate('Object.keys(localStorage).filter(k=>k.startsWith("enn583ann:")).length')==0 and 'restored' not in p2.inner_text('#vstatus'))
    c2.close()
    # phone width: no horizontal scroll, viewer full screen
    c3=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True); p3=c3.new_page(); p3.goto(URL); p3.wait_for_timeout(2000); wide=[]
    for t in tabs:
        p3.evaluate(f'location.hash="{t}"'); p3.wait_for_timeout(150)
        sw=p3.evaluate('document.documentElement.scrollWidth')
        if sw>392: wide.append((t,sw))
    ok('390px: no horizontal page scroll on any tab',not wide,str(wide))
    ok('390px: tab bar not sticky',p3.eval_on_selector('header.top','e=>getComputedStyle(e).position')!='sticky')
    p3.evaluate('location.hash="w05"'); p3.wait_for_timeout(300); p3.click('section[data-panel="w05"] button[data-view]'); p3.wait_for_timeout(2500)
    ok('390px: viewer covers full width',p3.eval_on_selector('#viewer','e=>Math.round(e.getBoundingClientRect().width)')>=388)
    c3.close(); b.close()
finally:
    srv.terminate()
print(f'\n{sum(r[1] for r in R)}/{len(R)} passed')
