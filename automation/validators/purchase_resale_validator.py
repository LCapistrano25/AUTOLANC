# validators/purchase_resale_validator.py
from typing import Any

from complements.fields import SITUATION_APPROVED, FiscalFields

class PurchaseResaleValidator:
    """
    Responsável por validar a nota fiscal de compra e revenda.
    """
    def __init__(self, toolbox: Any, logger: Any):
        self.toolbox = toolbox
        self.logger = logger

    def _get_inner_text(self, page: Any, selector: str) -> str:
        self.toolbox.wait_for_timeout(page, 2000)
        return self.toolbox.inner_text(page, selector).lower()

    def _is_equal_to_expected(self, value: str, expected: str) -> bool:
        return value == expected.lower()

    def verify_document_type(self, page: Any) -> bool:
        """Verifica se o tipo de documento é o esperado."""
        try:
            text = self._get_inner_text(page, FiscalFields.TEXT_DOCUMENT_TYPE)
            return self._is_equal_to_expected(text, SITUATION_APPROVED['document_type_approved'])
        except Exception as e:
            self.logger.error(f"Erro ao verificar o tipo de documento: {e}")
            raise

    def verify_situation(self, page: Any) -> bool:
        """Verifica a situação da nota fiscal."""
        try:
            text = self._get_inner_text(page, FiscalFields.TEXT_SITUATION)
            return self._is_equal_to_expected(text, SITUATION_APPROVED['situation_approved'])
        except Exception as e:
            self.logger.error(f"Erro ao verificar a situação da nota fiscal: {e}")
            raise

    def verify_situation_manifested(self, page: Any) -> bool:
        """Verifica se a nota fiscal foi manifestada corretamente."""
        try:
            text = self._get_inner_text(page, FiscalFields.TEXT_SITUATION_MANIFESTED)
            return self._is_equal_to_expected(text, SITUATION_APPROVED['situation_manifested_approved'])
        except Exception as e:
            self.logger.error(f"Erro ao verificar situação manifestada: {e}")
            raise

    def verify_parameters(self, page: Any) -> bool:
        """
        Verifica os parâmetros principais da nota fiscal:
        tipo de documento e situação.
        """
        try:
            if not self.verify_document_type(page):
                self.logger.info("Nota fiscal não é do tipo esperado.")
                return False
            if not self.verify_situation(page):
                self.logger.info("Nota fiscal não está com situação autorizada.")
                return False

            self.logger.info("Parâmetros da nota fiscal verificados com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao verificar parâmetros da nota: {e}")
            raise

    def verify_invoice(self, page: Any) -> bool:
        """
        Verifica se a nota fiscal foi manifestada corretamente após carregamento.
        """
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            return self.verify_situation_manifested(page)
        except Exception as e:
            self.logger.error(f"Erro ao verificar a nota fiscal completa: {e}")
            raise
