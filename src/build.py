"""Assemble index.html from shell.html, app.js and the content modules in src/frag/."""
import json, re, os, sys, importlib.util, html
HERE = os.path.dirname(os.path.abspath(__file__)); SITE = os.path.dirname(HERE)
VIDS = json.load(open(os.path.join(HERE, 'videos_verified.json')))

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, 'frag', name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def esc(s): return html.escape(s, quote=True)
def mmss(s): return f'{s//60}:{s%60:02d}'

def slides(body, docs):
    """[[p12]] -> link into the topic's first doc; [[P:p5]] -> second doc; [[P2:p3]] third."""
    def rep(m):
        which, p = m.group(1), m.group(2); i = {'': 0, 'P:': 1, 'P2:': 2}[which or '']
        d = docs[min(i, len(docs) - 1)]
        lab = ('slides' if i == 0 else 'paper') + ' p.' + p
        return f'<a class="sl" data-view="{d["path"]}" data-p="{p}" title="Open {esc(d["title"])} at page {p}">{lab}</a>'
    return re.sub(r'\[\[(P2?:)?p(\d+)\]\]', rep, body)

def notes_box(d, label='Lecture notes'):
    return (f'<div class="box notes"><div class="meta"><b>{label}: {esc(d["title"])}</b><small>{d["pages"]} pages · PDF</small></div>'
            f'<div class="acts"><button class="btn pri" type="button" data-view="{d["path"]}">📖 View here</button>'
            f'<button class="btn" type="button" data-dl="{d["path"]}">⬇ Download PDF</button>'
            f'<a class="btn" href="{d["path"]}" target="_blank" rel="noopener">Open in new tab ↗</a></div></div>')

def video_cards(ids):
    out = []
    for v in ids:
        m = VIDS[v]; amp = '\\u0026'
        title = esc(html.unescape(m['title']).replace(amp, '&')); chan = esc(m['channel'].replace(amp, '&'))
        out.append(f'<div class="vid"><div class="t">{title}</div>'
                   f'<small>{chan} · {mmss(m["len"])}</small>'
                   f'<div class="row"><button class="btn" type="button" data-play="{v}">▶ Play here</button>'
                   f'<a class="btn" href="https://www.youtube.com/watch?v={v}" target="_blank" rel="noopener">Open on YouTube ↗</a></div></div>')
    return '<div class="vids">' + ''.join(out) + '</div><p class="note">The in-page player can be blocked inside some viewers (including the claude.ai frame). If it stays blank, use “Open on YouTube”.</p>'

def mcq(qid, stem, opts, ans, why, chips=(), num=None):
    lis = ''.join(f'<li class="{"ok" if i == ans else ""}">{o}</li>' for i, o in enumerate(opts))
    ch = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    head = f'<b>{num}</b>' if num else ''
    return (f'<div class="q" data-qid="{qid}"><div class="hd">{head}<span>{ch}</span></div><div>{stem}</div><ol class="opts">{lis}</ol>'
            f'<details class="sol"><summary>Show answer</summary><div class="in"><p><b>Answer: ({"abcd"[ans]})</b> {why}</p></div></details>'
            f'<div class="self">Self-mark: <button class="y" type="button">✓ got it</button><button class="n" type="button">✗ revisit</button></div></div>')

def openq(qid, stem, ans, chips=(), num=None):
    ch = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    head = f'<b>{num}</b>' if num else ''
    return (f'<div class="q" data-qid="{qid}"><div class="hd">{head}<span>{ch}</span></div><div>{stem}</div>'
            f'<details class="sol"><summary>Show worked answer</summary><div class="in">{ans}</div></details>'
            f'<div class="self">Self-mark: <button class="y" type="button">✓ got it</button><button class="n" type="button">✗ revisit</button></div></div>')

def topic(T):
    tid = T['id']; docs = T['docs']; parts = []
    parts.append(f'<div><p class="note mono">Week {T["week"]}</p><h2>{T["title"]}</h2><p class="lead">{T["lead"]}</p></div>')
    parts.append(notes_box(docs[0]))
    if T.get('prac'):
        nb, txt = T['prac']
        parts.append(f'<div class="box prac"><span class="tag">Practical (optional)</span><p style="margin:4px 0 0"><code>{nb}</code>: {txt}</p>'
                     f'<p class="note" style="margin:4px 0 0">Practical lessons come in Phase 2. The exam does not test the code.</p></div>')
    T['eli5'] = [tuple(slides(x, docs) if x else x for x in c) for c in T['eli5']]
    cards = ''.join(f'<div class="card"><h4>{c[0]}</h4><p>{c[1]}</p>' + (f'<p class="inp"><b>In the practical:</b> {c[2]}</p>' if len(c) > 2 and c[2] else '') + '</div>' for c in T['eli5'])
    parts.append(f'<div class="eli"><h3>Explain it like I’m five</h3><div class="cards">{cards}</div>'
                 f'<figure class="diagram" style="margin:0">{T["svg"]}<figcaption>{slides(T["svgcap"], docs)}</figcaption></figure>{video_cards(T["videos"])}</div>')
    parts.append(slides(T['body'], docs))
    if T.get('paper'):
        P = T['paper']
        parts.append(f'<div class="paper"><span class="kick">Tutorial paper · in 60 seconds</span><h3>{P["title"]}</h3>{slides(P["sixty"], docs)}'
                     f'<div class="acts" style="display:flex;gap:6px;flex-wrap:wrap">' +
                     ''.join(f'<button class="btn" type="button" data-view="{d["path"]}">📖 {esc(d["title"])}</button>' for d in docs[1:]) + '</div></div>')
    if T.get('tut'):
        parts.append(f'<details class="tut"><summary>Tutorial: full discussion (optional depth)</summary><div class="in">{slides(T["tut"], docs)}</div></details>')
    if T.get('quiz'):
        qs = ''.join(mcq(f'{tid}-q{i+1}', q[0], q[1], q[2], slides(q[3], docs), ('mini-quiz', 'MCQ')) for i, q in enumerate(T['quiz']))
        parts.append(f'<div class="sub"><h3>Mini-quiz</h3>{qs}</div>')
    return f'<section data-panel="{tid}" hidden aria-label="{esc(T["title"])}">' + '\n'.join(parts) + '</section>'

def main():
    import glob
    topics = [load(f'w{i:02d}').T for i in range(1, 14)]
    plan, mock, past, qa, cheat = (load(n) for n in ('plan', 'mock', 'past', 'qa', 'cheat'))
    tabs = [('plan', 'Study plan', '')] + [(t['id'], t['tab'], f'W{t["week"]}') for t in topics] + \
           [('mock', 'Mock exam', ''), ('past', 'Practice exam solved', ''), ('qa', 'Practice Q&A', ''), ('cheat', 'Cheatsheet', '')]
    tabhtml = ''.join(f'<button type="button" role="tab" data-tab="{i}" aria-selected="false">' + (f'<span class="wk">{w}</span>' if w else '') + f'{esc(n)}</button>' for i, n, w in tabs)
    panels = [plan.render(topics)] + [topic(t) for t in topics] + [mock.render(mcq, openq), past.render(mcq, notes_box), qa.render(mcq, openq), cheat.render()]
    docs = {t['id']: t['docs'] for t in topics}
    docs['past'] = [past.DOC]
    data = {'docs': docs, 'topicNames': {**{t['id']: f'W{t["week"]} {t["tab"]}' for t in topics}, 'mock': 'Mock exam', 'past': 'Practice exam', 'qa': 'Practice Q&A'}}
    shell = open(os.path.join(HERE, 'shell.html')).read()
    out = (shell.replace('{{TABS}}', tabhtml).replace('{{PANELS}}', '\n'.join(panels))
           .replace('{{DATA}}', json.dumps(data)).replace('{{APPJS}}', open(os.path.join(HERE, 'app.js')).read()))
    open(os.path.join(SITE, 'index.html'), 'w').write(out)
    open(os.path.join(HERE, 'cheatsheet_print.html'), 'w').write(cheat.print_html())
    # Same page wrapped the way the publish skeleton wraps it (viewport meta + reset), for local tests and GitHub Pages.
    skel = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>'
            '</head><body>' + out + '</body></html>')
    open(os.path.join(SITE, 'preview.html'), 'w').write(skel)
    key = ' '.join(f'{i+1}{"abcd"[q[3]]}' for i, q in enumerate(past.Q)); print('answer key:', key)
    print('index.html', len(out) // 1024, 'KB;', len(tabs), 'tabs')

if __name__ == '__main__':
    main()
