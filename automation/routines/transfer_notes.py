from playwright.sync_api import sync_playwright
from decouple import config
from automation.context import Context
from automation.handlers.navigation_helper import NavigationHelper
from database.utils import update_invoice_status, update_invoice_attemps
from automation.base import Automation
from automation.helpers.update_product import UpdateProduct
from complements.fields import (
    HomeFields,
    HomeMenuFields, 
    StockInvoiceFields,
)
from complements.log import Logger

class TransferNotesAutomation(Automation):
    def __init__(self, url, username, password, context: Context):
        self.context = context
        self.db = context.db
        self.data = context.data
        self.parameters = context.parameters
        self.invoice_id = context.data.key
        self.dir_logs = context.dir_logs
        self.logger = Logger(self.invoice_id, log_file=f'{self.dir_logs}/{self.invoice_id}/{self.invoice_id}.log', invoice_id=self.invoice_id)

        super().__init__(url, username, password, self.context)

        self.navigator = NavigationHelper(toolbox=self.toolbox, logger=self.logger)

    def login(self, page):
        """Método responsável por realizar o login no sistema."""
        super().login(page)

    def close(self, browser):
        """Método responsável por fechar o navegador."""
        super().close(browser)

    def select_branch(self, page: object, branch_id: str, branch_name: str = None):
        """Método responsável por seleciona a filial desejada."""
        if self.navigator.validate_branch(page, branch_name):
            self.logger.info(f"OK - Filial selecionada {branch_name}")
            return 
        return super().select_branch(page, branch_id)
    
    def _open_modules(self, page: object) -> None:
        """Método responsável por abrir o menu de módulos."""
        self.toolbox.wait_for_timeout(page, 2000)
        self.toolbox.click(page, HomeFields.ICON_MENU)
        self.toolbox.wait_for_selector(page, HomeMenuFields.MODULES)
        self.toolbox.click(page, HomeMenuFields.MODULE_STOCK)
        self.logger.info("OK - Menu de módulos aberto com sucesso")

    def _open_sidebar_invoices(self, page: object) -> None:
        """Método responsável por abrir o menu lateral de estoque."""	
        self.toolbox.wait_for_selector(page, StockInvoiceFields.SIDEBAR_STOCK)
        self.toolbox.wait_for_timeout(page, 2000)
        self.toolbox.click(page, StockInvoiceFields.SIDEBAR_STOCK)
    
    def _select_option_import_invoice(self, page: object) -> None:
        self.toolbox.wait_for_timeout(page, 2000)
        self.toolbox.wait_for_selector(page, StockInvoiceFields.OPTION_IMPORT_INVOICE_BRANCH)
        self.toolbox.click(page, StockInvoiceFields.OPTION_IMPORT_INVOICE_BRANCH)
        self.logger.info("Acesso ao módulo de importação de notas e opção de nota fiscal realizado com sucesso")

    def access_module(self, page: object) -> None:
        """Método responsável por acessar o módulo fiscal e a opção de nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            if not self.navigator.validate_rotine(page, StockInvoiceFields.TITLE_IMPORT_INVOICE, StockInvoiceFields.ROTINE):
                self._open_modules(page)
                self._open_sidebar_invoices(page)
                self._select_option_import_invoice(page)
            else:
                self.logger.info("O módulo fiscal e a opção de nota fiscal já estão acessados")

        except Exception as e:
            self.logger.error(f"Erro ao tentar acessar módulo fiscal e opção de fatura: {e}")
            raise e
    
    def search_invoice(self, page: object, number_invoice: str) -> None:
        """Método responsável por buscar a nota fiscal."""
        try:
            result = update_invoice_attemps(self.db, key=self.invoice_id)

            if not result:
                raise Exception("Erro ao tentar atualizar a nota fiscal")
            
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.select_option(page, StockInvoiceFields.DROPDOWN_ORIGIN, '0')
            self.toolbox.select_option(page, StockInvoiceFields.DROPDOWN_DESTINATION, '0')
            self.toolbox.fill(page, StockInvoiceFields.FIELD_INVOICE, number_invoice)
            self.toolbox.click(page, StockInvoiceFields.BUTTON_SEARCH)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.wait_for_selector(page, StockInvoiceFields.OPTION_INVOICE)
            self.toolbox.click(page, StockInvoiceFields.OPTION_INVOICE)
            self.logger.info(f"Nota fiscal {number_invoice} buscada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar buscar a nota fiscal: {e}")
            raise e
    
    def launch_invoice(self, page: object) -> None:
        """Método responsável por lançar a nota fiscal."""
        try:
            result = update_invoice_status(self.db, status=self.parameters.launching, key=self.invoice_id)
            
            if not result:
                self.logger.info(f"Nota fiscal {self.invoice_id} já lançada")
                return

            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, StockInvoiceFields.BUTTON_NEXT)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, StockInvoiceFields.BUTTON_IMPORT)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, StockInvoiceFields.BUTTON_FINISH)
            self.logger.info("Nota fiscal lançada com sucesso")

            result = update_invoice_status(self.db, status=self.parameters.launched, key=self.invoice_id)

            if not result:
                update_invoice_status(self.db, status=self.parameters.to_review, key=self.invoice_id)
                raise Exception("Erro ao tentar atualizar a nota fiscal")
            
        except Exception as e:
            self.logger.error(f"Erro ao tentar lançar a nota fiscal: {e}")
            raise e
        
    def execute(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=config('HEADLESS', default=True , cast=bool))
            page = browser.new_page()
            
            try:
                page.goto(self.url)
                self.login(page)

                try:
                    key = self.data.key
                    branch_number = self.data.branch_number
                    branch_name = self.data.branch_name
                    invoice_number = self.data.invoice_number
                    
                    self.logger.info(f"Processando a nota fiscal {key}")

                    self.select_branch(page, branch_number, branch_name)
                    self.access_module(page)
                    self.search_invoice(page, invoice_number)
                    self.launch_invoice(page)
                    page.wait_for_timeout(5000)

                    self.logger.info(f"Processamento da nota fiscal {key} finalizado com sucesso")
                except Exception as e:
                    self.logger.error(f"Erro ao tentar processar a nota fiscal {key}: {e}")
                    self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/9999 - processamento_nota_fiscal.png")
                    return

                self.logger.info("Automação finalizada com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao tentar executar a automação: {e}")
                self.close(browser)
            finally:
                self.close(browser)

    def __str__(self):
        line_sep = '-' * (len(self.url) // 2)
        return f"""
        {line_sep} Transfer Notes Automation {line_sep}
        | URL: {self.url}
        | Chave: {self.invoice_id}
        | Filial: {self.data.branch_name}
        | Operação: {self.data.operation}
        | Checagem: {self.data.checker}
        | Vendedor: {self.data.seller}
        | Centro de Custo: {self.data.center}
        | Política de Pagamento: {self.data.policy}
        | Produtos para atualização: {len(self.data.products)}
        {line_sep} End Transfer Notes Automation {line_sep}
        """