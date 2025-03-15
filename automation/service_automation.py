from playwright import sync_playwright
from automation.automation import Automation

class ServiceNotesAutomation(Automation):
    def __init__(self, url, username, password, toolbox=None):
        super().__init__(url, username, password, toolbox)

    def login(self, page):
        super().login(page)

    def close(self, browser):
        super().close(browser)

    def execute(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            self.login(page)
            browser.close()
    