import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
H=functools.partial(http.server.SimpleHTTPRequestHandler)
srv=socketserver.TCPServer(("127.0.0.1",8765),H); srv.allow_reuse_address=True
threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,name in [(1440,"desktop-full"),(390,"mobile-full")]:
        pg=b.new_page(viewport={"width":w,"height":900},device_scale_factor=2 if w<500 else 1)
        pg.goto("http://127.0.0.1:8765",wait_until="load",timeout=20000)
        pg.wait_for_timeout(1500)
        pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
        pg.wait_for_timeout(500)
        pg.screenshot(path=f"screenshots/{name}.png",full_page=True)
        print("shot",name); pg.close()
    b.close()
srv.shutdown()
