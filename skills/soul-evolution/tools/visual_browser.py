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

async def browse(url: str, duration: int = 15):
    """
    Opens a visible browser, navigates to the URL, reads content, and closes.
    """
    async with async_playwright() as p:
        # Launch visible browser (headless=False is KEY)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        print(f"Navigating to {url}...")
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("domcontentloaded")
            
            # Simulate reading behavior (scroll down slowly)
            for i in range(5):
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(1)
            
            # Extract content
            title = await page.title()
            content = await page.inner_text("body")
            
            # Take a "memory" screenshot
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            screenshot_path = os.path.abspath(f"memory/reality/browser_snapshots/snap_{timestamp}.png")
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            await page.screenshot(path=screenshot_path)
            
            # Keep open for a moment so the user sees it
            await asyncio.sleep(2)

            result = {
                "title": title,
                "url": url,
                "summary": content[:2000] + "..." if len(content) > 2000 else content,
                "screenshot": screenshot_path
            }
            print(json.dumps(result))

        except Exception as e:
            print(json.dumps({"error": str(e)}))
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "URL required"}))
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://www.google.com/search?q=" + url.replace(" ", "+")
        
    asyncio.run(browse(url))
