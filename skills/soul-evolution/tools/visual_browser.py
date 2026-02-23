import sys
import json
import asyncio
import os
import subprocess
from datetime import datetime

# Auto-install dependencies if missing
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Installing playwright...", file=sys.stderr)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.async_api import async_playwright

STORAGE_STATE = os.path.abspath("memory/reality/browser_session.json")

async def browse(action: str, query: str, duration: int = 5):
    """
    Opens a visible browser, performs action, saves session, and closes.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        # Load existing session if available
        context_args = {}
        if os.path.exists(STORAGE_STATE):
            context_args["storage_state"] = STORAGE_STATE
            
        context = await browser.new_context(viewport={"width": 1280, "height": 720}, **context_args)
        page = await context.new_page()

        try:
            if action == "browse":
                url = query
                if not url.startswith("http"):
                    url = "https://www.google.com/search?q=" + url.replace(" ", "+")
                
                print(f"Navigating to {url}...")
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                
                # Slow scroll
                for _ in range(3):
                    await page.mouse.wheel(0, 500)
                    await asyncio.sleep(1)
            
            elif action == "click":
                # query is selector
                await page.click(query)
                await asyncio.sleep(2)
                
            elif action == "type":
                # query format: "selector|text"
                if "|" in query:
                    selector, text = query.split("|", 1)
                    await page.fill(selector, text)
                    await asyncio.sleep(1)
                else:
                    await page.keyboard.type(query)

            # Final state capture
            title = await page.title()
            content = await page.inner_text("body")
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = os.path.abspath(f"memory/reality/browser_snapshots/snap_{timestamp}.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await page.screenshot(path=screenshot_path)
            
            # Save session state (cookies, etc.)
            await context.storage_state(path=STORAGE_STATE)

            result = {
                "title": title,
                "url": page.url,
                "summary": content[:2000] + "..." if len(content) > 2000 else content,
                "screenshot": screenshot_path,
                "session_saved": True
            }
            print(json.dumps(result))

        except Exception as e:
            print(json.dumps({"error": str(e)}))
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Compatibility with old call style
        action = "browse"
        query = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    else:
        action = sys.argv[1]
        query = sys.argv[2]
        
    asyncio.run(browse(action, query))
