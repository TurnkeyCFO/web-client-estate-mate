import http.server, socketserver, threading, os, functools
from playwright.sync_api import sync_playwright
os.chdir(os.path.dirname(os.path.abspath(__file__)))
srv=socketserver.TCPServer(("127.0.0.1",8767),functools.partial(http.server.SimpleHTTPRequestHandler)); srv.allow_reuse_address=True
threading.Thread(target=srv.serve_forever,daemon=True).start()
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,name in [(1440,"desktop-full"),(390,"mobile-full")]:
        pg=b.new_page(viewport={"width":w,"height":900},device_scale_factor=2 if w<500 else 1)
        pg.on("console",lambda m:(errs.append(m.text) if m.type=="error" else None))
        pg.on("pageerror",lambda e:errs.append("PAGEERROR:"+str(e)))
        pg.goto("http://127.0.0.1:8767",wait_until="networkidle",timeout=30000)
        pg.wait_for_timeout(1500)
        pg.evaluate("document.querySelectorAll('.rv').forEach(e=>{e.style.opacity=1;e.style.transform='none'})")
        pg.wait_for_timeout(400)
        broken=pg.evaluate("Array.from(document.images).filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.currentSrc||i.src)")
        print(name,"broken_images:",broken)
        pg.screenshot(path=f"screenshots/{name}.png",full_page=True)
        pg.close()
    b.close()
srv.shutdown()
print("CONSOLE_ERRORS:",errs[:10])
