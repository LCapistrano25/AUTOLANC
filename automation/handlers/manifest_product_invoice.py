
from complements.fields import SITUATION_APPROVED, FiscalFields, ManualSelectionPopupFields, SelectEventPopupFields

from automation.validators.purchase_resale_validator import PurchaseResaleValidator

class ManifestProductInvoice:
    """
    Classe responsável por manifestar a nota fiscal de produtos
    """

    def __init__(self, toolbox, logger, validator):
        self.toolbox = toolbox
        self.logger = logger
        self.validator = validator or  PurchaseResaleValidator(toolbox, logger)

    def _validate_situation_invoice(self, page: object) -> bool:
        """Verifica se a nota fiscal já foi manifestada."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            situacao = self.toolbox.inner_text(page, FiscalFields.TEXT_SITUATION_MANIFESTED)
            return situacao not in SITUATION_APPROVED['situation_manifested_not_approved']
        except Exception as e:
            self.logger.error(f"Erro ao verificar a situação da nota fiscal: {e}")
            raise e
        
    def _is_checked(self, page: object) -> bool:
        """Verifica se a nota fiscal está marcada."""
        try:
            return self.toolbox.is_checked(page, FiscalFields.CHECKBOX_SELECT_INVOICE)
        except Exception as e:
            self.logger.error(f"Erro ao verificar se a nota fiscal está marcada: {e}")
            raise e
        
    def manifest_invoice(self, page: object) -> bool:
        """Método responsável por manifestar a nota fiscal."""	
        try:
            if not self.validator.verify_parameters(page):
                self.logger.info("Nota fiscal não está apta para manifestação")
                return False
            
            if self.validator.verify_invoice(page):  
                self.logger.info("Nota fiscal já manifestada")
                return True
            
            situacao = self.toolbox.inner_text(page, FiscalFields.TEXT_SITUATION_MANIFESTED)

            if situacao not in SITUATION_APPROVED['situation_manifested_not_approved']:
                self.logger.info("Nota fiscal não está apta para manifestação")
                return False

            self.toolbox.check(page, FiscalFields.CHECKBOX_SELECT_INVOICE)
            self.toolbox.wait_for_timeout(page, 2000)

            if not self.toolbox.is_checked(page, FiscalFields.CHECKBOX_SELECT_INVOICE):
                self.logger.info("Erro ao tentar manifestar a nota fiscal")
                return False

            self.toolbox.click(page, FiscalFields.BUTTON_MANIFEST)
            iframe = self.toolbox.obtain_frame(page, FiscalFields.IFRAME_CONFIRM_OPERATION)

            self.toolbox.wait_for_timeout(page, 3000)
            self.toolbox.frame_check(iframe, FiscalFields.OPTION_CONFIRM_OPERATION, force=True)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.frame_click(iframe, FiscalFields.BUTTON_MANIFEST_CONFIRM)
            self.toolbox.wait_for_timeout(page, 2000)

            try:
                self.toolbox.wait_for_timeout(page, 3000)
                self.toolbox.wait_for_selector(page, ManualSelectionPopupFields.POPUP_CONFIRM_OPERATION)

                if not self.confirm_manifestation_invoice(page):
                    self.logger.error("Erro ao tentar confirmar a manifestação da nota fiscal")
                    return False
                
            except Exception as e:
                self.logger.error(f"Não identificado POPUP de confirmação: {e}")
            
            if not self.validator.verify_situation_manifested(page):
                self.logger.info("Nota fiscal não está com a situação manifestada 'Confirmada Operação'")
                return False
            
            self.logger.info("Nota fiscal manifestada com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao tentar manifestar a nota fiscal: {e}")
            raise e

    def confirm_manifestation_invoice(self, page: object) -> bool:
        """Método responsável por confirmar a manifestação da nota fiscal."""
        try:
            self.toolbox.wait_for_selector(page, ManualSelectionPopupFields.POPUP_CONFIRM_OPERATION)
            self.toolbox.click(page, ManualSelectionPopupFields.BUTTON_UPDATE_SITUATION)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.wait_for_selector(page, SelectEventPopupFields.POPUP_CONFIRM_EVENT)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.select_option(page, SelectEventPopupFields.DROPDOWN_SITUATION, SITUATION_APPROVED['situation_manifested_approved'])
            self.toolbox.click(page, SelectEventPopupFields.BUTTON_CONFIRM_EVENT)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, ManualSelectionPopupFields.BUTTON_CONFIRM_SITUATION)
            self.toolbox.wait_for_timeout(page, 5000)
            self.logger.info("Manifestação da nota fiscal confirmada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao tentar confirmar a manifestação da nota fiscal: {e}")
            return True