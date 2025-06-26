from abc import ABC, abstractmethod

class AbstractToolbox(ABC):
    """
    Abstract class for toolbox
    This class defines the interface for toolbox operations.
    """
    @abstractmethod
    def fill(self, page: object, selector: str, text: str):
        pass

    @abstractmethod
    def click(self, page: object, selector: str, is_required: bool = True, timeout: int = 30000):
        pass

    @abstractmethod
    def inner_text(self, page: object, selector: str, timeout: int = 30000):
        pass

    @abstractmethod
    def select_option(self, page: object, selector: str, text: str):
        pass

    @abstractmethod
    def enter(self, page: object, selector: str):
        pass

    @abstractmethod
    def wait_for_selector(self, page: object, selector: str):
        pass

    @abstractmethod
    def wait_for_load_state(self, page: object, state: str):
        pass

    @abstractmethod
    def wait_for_timeout(self, page: object, time: int):
        pass

    @abstractmethod
    def obtain_frame(self, page: object, selector: str):
        pass

    @abstractmethod
    def frame_locator(self, iframe: object, selector: str, text: str):
        pass

    @abstractmethod
    def frame_click(self, iframe: object, selector: str):
        pass

    @abstractmethod
    def frame_check(self, iframe: object, selector: str, force: bool = False):
        pass

    @abstractmethod
    def check(self, page: object, selector: str):
        pass

    @abstractmethod
    def uncheck(self, page: object, selector: str):
        pass

    @abstractmethod
    def is_checked(self, page: object, selector: str):
        pass

    @abstractmethod
    def screenshot(self, page: object, path: str):
        pass
        
class Toolbox(AbstractToolbox):
    """
    Toolbox for automation operations.
    This class provides methods for interacting with web pages, such as filling forms, clicking elements,
    selecting options, and taking screenshots.
    """
    
    @staticmethod
    def fill(page: object, selector: str, text: str):
        page.wait_for_selector(selector, state='visible')
        page.fill(selector, text)

    @staticmethod
    def click(page: object, selector: str, is_required: bool = True, timeout: int = 30000):
        if is_required:
            page.wait_for_selector(selector, state='visible', timeout=timeout)
        page.click(selector)

    @staticmethod
    def inner_text(page: object, selector: str, timeout: int = 30000):
        page.wait_for_selector(selector, state='visible', timeout=timeout)
        return page.locator(selector).inner_text()
    
    @staticmethod
    def select_option(page: object, selector: str, text: str):
        page.select_option(selector, text)

    @staticmethod
    def enter(page: object, selector: str):
        page.press(selector, 'Enter')
        
    @staticmethod
    def wait_for_selector(page: object, selector: str):
        page.wait_for_selector(selector)

    @staticmethod
    def wait_for_load_state(page: object, state: str):
        page.wait_for_load_state(state)
    
    @staticmethod
    def wait_for_timeout(page: object, time: int):
        page.wait_for_timeout(time)
        
    @staticmethod
    def obtain_frame(page: object, selector: str):
        return page.frame_locator(selector)
    
    @staticmethod
    def frame_locator(iframe: object, selector: str, text: str):
        iframe.locator(selector).select_option(value=text)

    @staticmethod
    def frame_click(iframe: object, selector: str):
        iframe.locator(selector).click()
    
    @staticmethod
    def frame_check(iframe: object, selector: str, force: bool = False):
        iframe.locator(selector).check(force=force)

    @staticmethod
    def check(page: object, selector: str):
        page.check(selector)

    @staticmethod
    def uncheck(page: object, selector: str):
        page.uncheck(selector)

    @staticmethod
    def is_checked(page: object, selector: str):
        return page.locator(selector).is_checked()
    
    @staticmethod
    def screenshot(page: object, path: str):
        page.screenshot(path=path, full_page=True)