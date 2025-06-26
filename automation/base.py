from abc import ABC, abstractmethod

from complements.fields import LoginFields, HomeFields
from automation.context import Context

class Automation(ABC):
    def __init__(self, url: str, username: str, password: str, context: Context) -> None:
        self.url = url
        self.username = username
        self.password = password
        self.context = context
        self.toolbox = context.toolbox
        self.logger = context.logger

    @abstractmethod
    def login(self, page: object) -> None:
        """Método para realizar o login no sistema"""
        try:
            self.toolbox.fill(page, LoginFields.FIELD_LOGIN_USER, self.username)
            self.toolbox.fill(page, LoginFields.FIELD_LOGIN_PASSWORD, self.password)
            self.toolbox.click(page, LoginFields.BUTTON_LOGIN)
            try:
               page.click(LoginFields.BUTTON_CLOSE_POPUP, timeout=5000)
            except Exception as ex:
                    self.logger.warning('Popup de confimação não encontrado')

            self.logger.info("OK - Login realizado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar realizar o login: {e}")
            raise e

    @abstractmethod
    def select_branch(self, page: object, branch: str) -> None:
        """Método para selecionar a filial"""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.click(page, HomeFields.BUTTON_SWITCH_BRANCH)
            self.toolbox.wait_for_selector(page, HomeFields.IFRAME_BRANCH)
            iframe = self.toolbox.obtain_frame(page, HomeFields.IFRAME_BRANCH)
            self.toolbox.frame_locator(iframe, HomeFields.DROPDOWN_BRANCH, branch)
            self.toolbox.frame_click(iframe, HomeFields.BUTTON_CONFIRM_BRANCH)
            self.logger.info("OK - Filial selecionada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar selecionar a filial: {e}")
            raise e

    @abstractmethod
    def close(self, browser: object) -> None:
        """Método para fechar o navegador"""
        try:
            browser.close()
            self.logger.info("Navegador fechado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar fechar o navegador: {e}")
            raise e

    @abstractmethod
    def execute(self) -> None:
        """Execute the automation"""
        pass