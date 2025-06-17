
from complements.fields import HomeFields

class NavigationHelper:
    def __init__(self, toolbox, logger):
        self.toolbox = toolbox
        self.logger = logger

    def get_branch_actual(self, page):
        """Método responsável por retornar o texto da filial atual."""
        text = self.toolbox.inner_text(page, HomeFields.BUTTON_SWITCH_BRANCH, timeout=5000)
        return text
    
    def validate_branch(self, page, branch_text):
        """Método responsável por validar a filial atual."""
        try:
            text = self.get_branch_actual(page).split(' | ')[-1]
            return branch_text.lower() == text.lower()
        except Exception as e:
            self.logger.error(f"Erro na tentativa de validar a {branch_text}: {e}")
            return False 

    def validate_rotine(self, page, selector, rotine):
        """Método responsável por validar o módulo atual."""
        try:
            text = self.toolbox.inner_text(page, selector, timeout=3000).split(' - ')[-1]
            self.logger.info(f"Da {text} para {rotine}")
            return rotine == text
        except Exception as e:
            self.logger.error(f"Erro ao validar a rotina {rotine}: {e}")
            return False
        
