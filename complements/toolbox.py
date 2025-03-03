class Toolbox:
    @staticmethod
    def fill(page: object, selector: str, text: str):
        page.wait_for_selector(selector, state='visible')
        page.fill(selector, text)

    @staticmethod
    def click(page: object, selector: str, is_required: bool = True):
        if is_required:
            page.wait_for_selector(selector, state='visible')
        page.click(selector)

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
    def obtain_frame(page: object, selector: str):
        return page.frame_locator(selector)
    
    @staticmethod
    def frame_locator(iframe: object, selector: str, text: str):
        iframe.locator(selector).select_option(value=text)

    @staticmethod
    def frame_click(iframe: object, selector: str):
        iframe.locator(selector).click()

    

    
    
    
