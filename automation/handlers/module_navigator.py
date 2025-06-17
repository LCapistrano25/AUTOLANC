from typing import Any

class ModuleNavigator:
    """Responsável por navegar entre módulos de um sistema."""

    def __init__(
        self,
        menu_icon_selector: str,
        module_selector: str,
        destination_selector: str,
        toolbox: Any,
        logger: Any
    ) -> None:
        self.toolbox = toolbox
        self.logger = logger
        self.menu_icon_selector = menu_icon_selector
        self.module_selector = module_selector
        self.destination_selector = destination_selector

    def access_module(self, page: Any) -> None:
        """
        Acessa o módulo e sua respectiva funcionalidade no sistema.

        Args:
            page: Página atual da automação Playwright.
        """
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, self.menu_icon_selector)
            self.toolbox.wait_for_selector(page, self.module_selector)
            self.toolbox.click(page, self.destination_selector)
            self.logger.info("Módulo e funcionalidade acessados com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao acessar o módulo ou funcionalidade: {e}")
            raise RuntimeError("Falha ao acessar o módulo do sistema.") from e

