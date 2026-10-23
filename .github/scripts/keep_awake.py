import os
from playwright.sync_api import sync_playwright

URL = os.environ["APP_URL"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(8000)

    wake = page.get_by_role("button", name="Yes, get this app back up!")
    if wake.count() > 0:
        print("App was asleep, clicking wake button")
        wake.first.click()
        page.wait_for_timeout(60000)

    page.wait_for_timeout(15000)
    print("Page title:", page.title())
    browser.close()