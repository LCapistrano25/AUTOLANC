class Toolbox:
    @staticmethod
    def fill(page: object, selector: str, text: str):
        page.wait_for_selector(selector, state='visible')
        page.fill(selector, text)

    @staticmethod
    def type(page: object, selector: str, text: str, delay: int = 500):
        page.wait_for_selector(selector, state='visible')
        page.type(selector, text, delay=delay)

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

    

    
    
    
