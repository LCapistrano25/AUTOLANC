from typing import Any

from complements.fields import HomeFields

class BranchSelector:
    """
    Auxilia na navegação e validação de informações na interface,
    como a filial atual.
    """

    def __init__(self, toolbox: Any, logger: Any):
        self.toolbox = toolbox
        self.logger = logger

    def get_branch(self, page: Any) -> str:
        """
        Retorna o nome da filial atual exibida na interface.

        Args:
            page: Página atual da automação Playwright.

        Returns:
            Texto da filial atual.
        """
        try:
            return self.toolbox.inner_text(
                page,
                HomeFields.BUTTON_SWITCH_BRANCH,
                timeout=5000
            ).strip()
        except Exception as e:
            self.logger.error(f"Erro ao obter filial atual: {e}")
            raise RuntimeError("Não foi possível obter a filial atual.") from e

    def validate_branch(self, page: Any, expected_branch: str) -> bool:
        """
        Valida se a filial atual corresponde à esperada.

        Args:
            page: Página atual da automação Playwright.
            expected_branch: Texto esperado da filial.

        Returns:
            True se a filial for correspondente, False caso contrário.
        """
        try:
            current_branch = self.get_branch(page).split(' | ')[-1]
            is_valid = expected_branch.strip().lower() == current_branch.strip().lower()

            if is_valid:
                self.logger.info(f"Filial validada com sucesso: {current_branch}")
            else:
                self.logger.warning(f"Filial divergente: esperada='{expected_branch}', atual='{current_branch}'")
            
            return is_valid

        except Exception as e:
            self.logger.error(f"Erro na tentativa de validar a filial '{expected_branch}': {e}")
            return False
        
    def open_branch_selector(self, page: Any) -> None:
        """
        Abre o seletor de filiais na interface.

        Args:
            page: Página atual da automação Playwright.
        """
        try:
            self.toolbox.click(page, HomeFields.BUTTON_SWITCH_BRANCH)
            self.toolbox.wait_for_selector(page, HomeFields.IFRAME_BRANCH)
            self.logger.info("Seletor de filiais aberto com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao abrir o seletor de filiais: {e}")
            raise RuntimeError("Não foi possível abrir o seletor de filiais.") from e
        
    def update_branch(self, page: object, branch_id: str) -> None:
        """Método para selecionar a filial"""
        try:
            iframe = self.toolbox.obtain_frame(page, HomeFields.IFRAME_BRANCH)
            self.toolbox.frame_locator(iframe, HomeFields.DROPDOWN_BRANCH, branch_id)
            self.toolbox.frame_click(iframe, HomeFields.BUTTON_CONFIRM_BRANCH)
            self.logger.info("OK - Filial selecionada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar selecionar a filial: {e}")
            raise e
        
    def select_branch(self, page: Any, branch_name: str, branch_id: str) -> None:
        """
        Seleciona uma filial específica na interface.

        Args:
            page: Página atual da automação Playwright.
            branch: Nome da filial a ser selecionada.
        """
        try:
            if self.navigator.validate_branch(page, branch_name):
                self.logger.info(f"Filial selecionada {branch_name}")
                return 
            
            self.open_branch_selector(page)
            self.update_branch(page, branch_id)
        except Exception as e:
            self.logger.error(f"Erro ao tentar selecionar a filial '{branch_name}': {e}")
            raise RuntimeError("Não foi possível selecionar a filial.") from e
    

    
