import asyncio, sys, subprocess, time, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8765"], cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
PS = [float(x) for x in sys.argv[1].split(",")]
W, H = (int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "1440x900").split("x"))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        logs = []
        pg.on("console", lambda m: logs.append(m.text))
        await pg.goto("http://localhost:8765/index.html")
        await pg.wait_for_selector("#loader.done", timeout=60000)
        for v in PS:
            await pg.evaluate(f"window.scrollTo(0,(document.documentElement.scrollHeight-innerHeight)*{v})")
            await pg.wait_for_timeout(1800)
            await pg.screenshot(path=os.path.join(HERE, "shots", f"p{int(v*1000):04d}_{W}.png"))
        print("console:", logs[:5])
        await b.close()
os.makedirs(os.path.join(HERE, "shots"), exist_ok=True)
try:
    asyncio.run(main())
finally:
    srv.terminate()
