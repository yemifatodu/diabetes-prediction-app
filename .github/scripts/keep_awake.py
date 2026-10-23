import os
from playwright.sync_api import sync_playwright

URLS = [u.strip() for u in os.environ["APP_URLS"].splitlines() if u.strip()]
failed = []

with sync_playwright() as p:
    browser = p.chromium.launch()
    for url in URLS:
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            page.wait_for_timeout(8000)

            wake = page.get_by_role("button", name="Yes, get this app back up!")
            if wake.count() > 0:
                print(f"{url}: asleep, clicking wake button")
                wake.first.click()
                page.wait_for_timeout(60000)

            page.wait_for_timeout(15000)
            print(f"{url}: Page title: {page.title()}")
            page.close()
        except Exception as e:
            print(f"{url}: FAILED - {e}")
            failed.append(url)
    browser.close()

if failed:
    raise SystemExit(f"Failed: {failed}")