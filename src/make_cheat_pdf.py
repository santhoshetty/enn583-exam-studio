import sys,os
from playwright.sync_api import sync_playwright
EXE=os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell')
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE)
    pg=b.new_page(); pg.goto('file://'+os.path.abspath('src/cheatsheet_print.html')); pg.wait_for_timeout(1500)
    pg.pdf(path='cheatsheet.pdf',format='A4',print_background=True,prefer_css_page_size=True)
    b.close()
import pymupdf; d=pymupdf.open('cheatsheet.pdf'); print('pages',len(d)); d.set_metadata({}); d.saveIncr() if False else None
