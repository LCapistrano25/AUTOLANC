import time
from playwright.sync_api import sync_playwright
from automation.automation import Automation
from complements.fields import HomeFields, HomeMenuFields, FiscalFields

class ProductNotesAutomation(Automation):
    def __init__(self, url, username, password, toolbox=None, data=None):
        super().__init__(url, username, password, toolbox, data)

    def login(self, page):
        super().login(page)

    def close(self, browser):
        super().close(browser)
    
    def select_branch(self, page, branch):
        return super().select_branch(page, branch)
    
    def access_module(self, page: object) -> None:
        """Access the fiscal module and the invoice option."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.click(page, HomeFields.ICON_MENU)
            self.toolbox.click(page, HomeMenuFields.MODULE_FISCAL)
            self.toolbox.click(page, FiscalFields.SIDEBAR_FISCAL)
            self.toolbox.click(page, FiscalFields.OPTION_INVOICE)
            self.logger.info("Access to fiscal module and invoice option successful")
        except Exception as e:
            self.logger.error(f"Error while trying to access the fiscal module and invoice option: {e}")
            raise e
        finally:
            self.logger.info("Access process finished")

    def search_invoice(self, page:object, key: str):
        """Searching the invoice product"""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.click(page, FiscalFields.BUTTON_CLEAN)
            time.sleep(10)
            self.toolbox.fill(page, FiscalFields.FIELD_KEY, key)
            self.toolbox.click(page, FiscalFields.BUTTON_SEARCH)
        except Exception as e:
            pass
    def execute(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(self.url)
            self.login(page)
            for i in self.data:
                self.select_branch(page, i['filial'])
                self.access_module(page)
                self.search_invoice(page, i['chave'])
                time.sleep(10)
                browser.close()
    