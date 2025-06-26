from playwright.sync_api import Page

from complements.log import Logger
from complements.toolbox import Toolbox
from complements.fields import (
    HomeFields,
    StockRegisterFields, 
    ProductFields, 
    HomeMenuFields
)

class UpdateProduct:
    @staticmethod
    def validate_rotine(toolbox: Toolbox, page: Page, selector: str, rotine: str) -> bool:
        """Método responsável por validar o módulo atual."""
        try:
            text = toolbox.inner_text(page, selector, timeout=3000).split(' - ')[-1]
            return rotine == text
        except Exception as e:
            return False
        
    @staticmethod
    def access_stock_module(toolbox: Toolbox, logger: Logger, page: Page) -> bool:
        """Acessa o módulo de estoque."""
        try:
            logger.info("Acessando módulo de estoque...")
            toolbox.wait_for_load_state(page, 'networkidle')
            toolbox.wait_for_timeout(page, 2000)
            toolbox.click(page, HomeFields.ICON_MENU)
            toolbox.wait_for_selector(page, HomeMenuFields.MODULES)
            toolbox.wait_for_timeout(page, 2000)
            toolbox.click(page, HomeMenuFields.MODULE_STOCK)
            return True
        except Exception as e:
            logger.error(f"Erro ao acessar o módulo de estoque {e}")
            return False
        
    @staticmethod
    def access_register_product(toolbox: Toolbox, logger: Logger, page: Page) -> bool:
        """Acessa o cadastro de produtos."""
        try:
            logger.info("Acessando cadastro de produtos...")
            toolbox.wait_for_load_state(page, 'networkidle')
            toolbox.wait_for_timeout(page, 2000)
            toolbox.click(page, StockRegisterFields.SIDEBAR_STOCK)
            toolbox.wait_for_timeout(page, 1000)
            toolbox.click(page, StockRegisterFields.OPTION_PRODUCT_STOCK)
            toolbox.wait_for_timeout(page, 1000)
            toolbox.click(page, StockRegisterFields.OPTION_REGISTER_STOCK)
            return True
        except Exception as e:
            logger.error(f"Erro ao acessar o cadastro de produtos {e}")
            return False
    
    @staticmethod
    def search_product(toolbox: Toolbox, logger: Logger, page: Page, code_product: str) -> bool:
        """Busca o produto."""
        try:
            logger.info("Buscando o produto...")
            toolbox.wait_for_load_state(page, 'networkidle')
            toolbox.wait_for_timeout(page, 1500)
            toolbox.click(page, StockRegisterFields.BUTTON_CLEAN)
            toolbox.wait_for_timeout(page, 1500)
            toolbox.fill(page, StockRegisterFields.FIELD_PRODUCT, code_product)
            toolbox.wait_for_timeout(page, 1000)
            toolbox.click(page, StockRegisterFields.BUTTON_SEARCH)
            toolbox.wait_for_timeout(page, 1500)
            toolbox.click(page, StockRegisterFields.BUTTON_EDIT)
            return True
        except Exception as e:
            logger.error(f"Erro ao buscar o produto {e}")
            return False
        
    @staticmethod
    def update_product(toolbox: Toolbox, logger: Logger, page: Page, origin: str) -> bool:
        """Atualiza o produto."""
        try:
            logger.info("Atualizando o produto...")
            toolbox.wait_for_load_state(page, 'networkidle')
            toolbox.wait_for_timeout(page, 1500)
            toolbox.click(page, ProductFields.TAB_TAX)
            toolbox.wait_for_timeout(page, 500)
            toolbox.select_option(page, ProductFields.DROPDOWN_ORIGIN, origin)
            toolbox.wait_for_timeout(page, 500)
            toolbox.click(page, ProductFields.BUTTON_SAVE)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar o produto {e}")
            return False

    @staticmethod
    def process_update_product(toolbox: Toolbox, logger: Logger, page: Page, products: list) -> bool:
        """Atualiza o cadastro de produtos."""
        try:
            logger.info("Iniciando atualização do cadastro de produtos...")
            toolbox.wait_for_load_state(page, 'networkidle')
            toolbox.wait_for_timeout(page, 2000)
            
            for index, product in enumerate(products):
                logger.info(f"Processando N°{len(products) - (index)} - produto {product.code}...")
                if not UpdateProduct.validate_rotine(
                    toolbox, page, ProductFields.TITLE_PRODUCT, ProductFields.ROTINE):
                    UpdateProduct.access_stock_module(toolbox, logger, page)
                    UpdateProduct.access_register_product(toolbox,logger, page)

                UpdateProduct.search_product(toolbox, logger, page, product.code)
                UpdateProduct.update_product(toolbox, logger, page, product.origin)
            
            toolbox.wait_for_timeout(page, 2000)
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar o cadastro de produtos {e}")
            return False