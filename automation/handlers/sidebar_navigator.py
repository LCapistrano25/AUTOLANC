from typing import Any, List

class SidebarNavigator:
    """Classe responsável por navegar entre os módulos de um sistema via barra lateral."""

    def __init__(
        self,
        selectors: List[str],
        toolbox: Any,
        logger: Any
    ) -> None:
        self.toolbox = toolbox
        self.logger = logger
        self.selectors = selectors

    def standard_navigation(self, page: Any, selector: str) -> None:
        """
        Navega até um módulo específico utilizando o seletor informado.

        Args:
            page: Página atual da automação Playwright.
            selector: Seletor CSS do módulo a ser acessado.
        """
        try:
            self.toolbox.wait_for_selector(page, selector)
            self.toolbox.click(page, selector)
        except Exception as e:
            self.logger.error(f"Erro ao navegar para o seletor '{selector}': {e}")
            raise RuntimeError(f"Falha ao acessar o seletor '{selector}'.") from e

    def access_page(self, page: Any) -> None:
        """
        Acessa a página navegando sequencialmente pelos seletores definidos.

        Args:
            page: Página atual da automação Playwright.
        """
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            for selector in self.selectors:
                self.standard_navigation(page, selector)
                self.toolbox.wait_for_timeout(page, 2000)
            self.logger.info("Todos os módulos e funcionalidades foram acessados com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao acessar a sequência de módulos: {e}")
            raise RuntimeError("Falha ao acessar a página do sistema.") from e
