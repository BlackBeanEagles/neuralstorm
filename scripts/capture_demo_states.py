"""Capture real BinWise browser states for the animated product tour.

Requires Playwright and an installed Chrome or Edge browser. The local app is
started only for this capture; no production deployment or model scan is used.
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
URL = "http://127.0.0.1:8765"
BROWSERS = (
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
)


def capture(page, name: str, focus: str | None = None) -> None:
    if focus:
        page.locator(focus).evaluate(
            "element => window.scrollTo({top: element.getBoundingClientRect().top + "
            "window.scrollY - 16, behavior: 'instant'})"
        )
    page.wait_for_timeout(450)
    page.screenshot(path=str(MEDIA / f"demo-{name}.png"))
    print(f"Captured {name}", flush=True)


def main() -> None:
    browser_path = next((path for path in BROWSERS if path.exists()), None)
    if browser_path is None:
        raise RuntimeError("Chrome or Edge is required for browser captures")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1",
         "--port", "8765", "--log-level", "error"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(80):
            try:
                with urllib.request.urlopen(f"{URL}/api/health", timeout=1):
                    break
            except (OSError, TimeoutError):
                time.sleep(0.1)
        else:
            raise RuntimeError("Local BinWise server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=str(browser_path), headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
            page.goto(URL, wait_until="networkidle")
            page.locator("#quick-items button").first.wait_for()
            capture(page, "home")
            capture(page, "choose", "#scan")
            page.locator("#text-input").fill("plastic bottle")
            capture(page, "typed", "#text-form")
            page.locator(".text-lookup").screenshot(path=str(MEDIA / "demo-typed-panel.png"))

            dark_path = MEDIA / "demo-dark-input.png"
            Image.new("RGB", (420, 420), (8, 10, 9)).save(dark_path)
            page.locator("#file-input").set_input_files(str(dark_path))
            page.locator("#scan-button").click()
            page.locator("#result-empty h3").get_by_text("Please retake the photo").wait_for(timeout=10000)
            capture(page, "retake", "#result-card")

            page.locator("#quick-items button").filter(has_text="Plastic bottle").click()
            page.locator("#prep-box").wait_for(state="visible")
            capture(page, "prep", "#result-card")
            page.locator("#prep-box").screenshot(path=str(MEDIA / "demo-prep-panel.png"))
            page.locator('[data-prep="empty"][data-answer="yes"]').click()
            page.locator('[data-prep="clean"][data-answer="yes"]').click()
            page.locator("#bin-box").wait_for(state="visible")
            capture(page, "plastic-result", "#result-card")
            capture(page, "feedback", "#feedback-box")
            page.locator("#feedback-box").screenshot(path=str(MEDIA / "demo-feedback-panel.png"))

            page.locator("#quick-items button").filter(has_text="Food scraps").click()
            page.locator("#bin-box").wait_for(state="visible")
            capture(page, "food", "#result-card")
            page.locator("#quick-items button").filter(has_text="Battery").click()
            page.locator("#bin-box").wait_for(state="visible")
            capture(page, "battery", "#result-card")

            page.locator("#language").select_option("hi")
            capture(page, "hindi", "#result-card")
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()


if __name__ == "__main__":
    main()
