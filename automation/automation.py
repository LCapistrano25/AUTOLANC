from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright

from complements.toolbox import Toolbox
from complements.fields import LoginFields, HomeFields
from complements.utils import Logger

class Automation(ABC):
    def __init__(self, url: str, username: str, password: str, toolbox: object = None, data: list[dict] = None) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.toolbox = toolbox or Toolbox()
        self.logger = Logger(__name__)
        self.data = data or []
        
    @abstractmethod
    def login(self, page: object) -> None:
        """Login to the system"""
        try:
            self.toolbox.fill(page, LoginFields.FIELD_LOGIN_USER, self.username)
            self.toolbox.fill(page, LoginFields.FIELD_LOGIN_PASSWORD, self.password)
            self.toolbox.click(page, LoginFields.BUTTON_LOGIN)
            self.toolbox.click(page, LoginFields.BUTTON_CLOSE_POPUP, is_required=False)
            self.logger.info("Login successful")
        except Exception as e:
            self.logger.error(f"Error while trying to login: {e}")
            raise e
        finally:
            self.logger.info("Login process finished")

    @abstractmethod
    def select_branch(self, page: object, branch: str) -> None:
        """Select a branch to the system"""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.click(page, HomeFields.BUTTON_SWITCH_BRANCH)
            self.toolbox.wait_for_selector(page, HomeFields.IFRAME_BRANCH)
            iframe = self.toolbox.obtain_frame(page, HomeFields.IFRAME_BRANCH)
            self.toolbox.frame_locator(iframe, HomeFields.DROPDOWN_BRANCH, branch)
            self.toolbox.frame_click(iframe, HomeFields.BUTTON_CONFIRM_BRANCH)
        except Exception as e:
            self.logger.error(f"Error while trying select to branch: {e}")
            raise e
        finally:
            self.logger.info("Select Branch finished")

    @abstractmethod
    def close(self, browser: object) -> None:
        """Close the browser"""
        try:
            browser.close()
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Error while trying to close the browser: {e}")
            raise e
        finally:
            self.logger.info("Close process finished")

    @abstractmethod
    def execute(self) -> None:
        """Execute the automation"""
        pass