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
        """Método para realizar o login no sistema"""
        try:
            self.toolbox.fill(page, LoginFields.FIELD_LOGIN_USER, self.username)
            self.toolbox.fill(page, LoginFields.FIELD_LOGIN_PASSWORD, self.password)
            self.toolbox.click(page, LoginFields.BUTTON_LOGIN)
            try:
                self.toolbox.click(page, LoginFields.BUTTON_CLOSE_POPUP, is_required=False, timeout=5000)
            except Exception as ex:
                self.logger.info('Popup de confimação não encontrado')
                 
            self.logger.info("Login realizado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar realizar o login: {e}")
            raise e
        finally:
            self.logger.info("Login finalizado")

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
            self.logger.info("Filial selecionada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar selecionar a filial: {e}")
            raise e
        finally:
            self.logger.info("Seleção de filial finalizada")

    @abstractmethod
    def close(self, browser: object) -> None:
        """Método para fechar o navegador"""
        try:
            browser.close()
            self.logger.info("Navegador fechado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar fechar o navegador: {e}")
            raise e
        finally:
            self.logger.info("Fechamento do navegador finalizado")

    @abstractmethod
    def execute(self) -> None:
        """Execute the automation"""
        pass