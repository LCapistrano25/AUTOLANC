from playwright.sync_api import sync_playwright

from automation.handlers.sidebar_navigator import SidebarNavigator
from automation.handlers.module_navigator import ModuleNavigator
from automation.helpers.navigation_helper import NavigationHelper
from database.utils import update_invoice_status, update_invoice_attemps

from automation.base import Automation
from automation.routines.update_product import UpdateProduct

from complements.fields import (
    HomeFields, 
    HomeMenuFields, 
    FiscalFields, 
    ManualSelectionPopupFields,
    SelectEventPopupFields,
    ImportXMLFields, 
    LaunchNFSe,
    FILTERS_SITUATION,
    SITUATION_APPROVED
)
from complements.log import Logger

    
class PurchaseResaleAutomation(Automation): # Classe Controle
    def __init__(self, url, username, password, toolbox=None, data=None, dir_logs='logs', db=None, parameters=None):
        self.db = db
        self.parameters = parameters
        self.invoice_id = data.key
        self.dir_logs = dir_logs
        self.logger = Logger(self.invoice_id, log_file=f'{self.dir_logs}/{self.invoice_id}/{self.invoice_id}.log', invoice_id=self.invoice_id)

        super().__init__(url, username, password, toolbox, data, self.logger)

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
    
    def verify_error(self, page: object) -> bool:
        """Método responsável por verificar se existe erro na tela."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.wait_for_selector(page, LaunchNFSe.ERROR_TAXES)
            error_message = self.toolbox.inner_text(page, LaunchNFSe.ERROR_TAXES).lower()
            if error_message:
                self.logger.info(f"Erro encontrado na tela: {error_message}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar erro na tela: {e}")
            return False
          
    def access_module(self, page: object) -> None:
        """Método responsável por acessar o módulo fiscal e a opção de nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            if not self.navigator.validate_rotine(page, FiscalFields.TITLE_FISCAL, FiscalFields.ROTINE):

                self.module_navigator = ModuleNavigator(
                    menu_icon_selector=HomeFields.ICON_MENU,
                    module_selector=HomeMenuFields.MODULES,
                    destination_selector=HomeMenuFields.MODULE_FISCAL,
                    toolbox=self.toolbox,
                    logger=self.logger
                )

                self.module_navigator.access_module(page)

                self.sidebar_navigator = SidebarNavigator(
                    selectors=[FiscalFields.SIDEBAR_FISCAL, FiscalFields.OPTION_INVOICE], toolbox=self.toolbox, logger=self.logger)
                self.sidebar_navigator.access_page(page)

                self.logger.info("Acesso ao módulo fiscal e opção de nota fiscal realizado com sucesso")
            else:
                self.logger.info("O módulo fiscal e a opção de nota fiscal já estão acessados")

        except Exception as e:
            self.logger.error(f"Erro ao tentar acessar módulo fiscal e opção de fatura: {e}")
            raise e
     
    def select_filter(self, page: object, filters: dict) -> None:
        """Método responsável por selecionar os filtros da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.select_option(page, FiscalFields.DROPDOWN_SITUATION_MANIFESTED, FILTERS_SITUATION['situation_manifested'])
            self.toolbox.select_option(page, FiscalFields.DROPDOWN_DOCUMENT_TYPE, FILTERS_SITUATION['document_type'])
            self.toolbox.select_option(page, FiscalFields.DROPDOWN_SITUATION, FILTERS_SITUATION['situation'])
            self.logger.info("Filtros da nota fiscal selecionados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar selecionar os filtros da nota fiscal: {e}")
            raise e
    
    def verify_document_type(self, page: object) -> bool:
        """Método responsável por verificar o tipo de documento da nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            return self.toolbox.inner_text(page, FiscalFields.TEXT_DOCUMENT_TYPE).lower() == SITUATION_APPROVED['document_type_approved'].lower()
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar o tipo de documento da nota fiscal: {e}")
            raise e

    def verify_situation(self, page: object) -> bool:
        """Método responsável por verificar a situação da nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            return self.toolbox.inner_text(page, FiscalFields.TEXT_SITUATION).lower() == SITUATION_APPROVED['situation_approved'].lower()
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar a situação da nota fiscal: {e}")
            raise e
    
    def verify_situation_manifested(self, page: object) -> bool:
        """Método responsável por verificar a situação manifestada da nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            return self.toolbox.inner_text(page, FiscalFields.TEXT_SITUATION_MANIFESTED).lower() == SITUATION_APPROVED['situation_manifested_approved'].lower()
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar a situação manifestada da nota fiscal: {e}")
            raise e
        
    def verify_parameters(self, page: object) -> bool:
        """Método responsável por verificar os parâmetros da nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
        
            if not self.verify_document_type(page):
                self.logger.info("Nota fiscal não é do tipo 'Nota Fiscal'")
                return False
            
            if not self.verify_situation(page):
                self.logger.info("Nota fiscal não está com a situação 'Uso Autorizado no Momento da Consulta'")
                return False
            
            self.logger.info("Parâmetros da nota fiscal verificados com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os parâmetros da nota fiscal: {e}")
            raise e
        
    def verify_invoice(self, page: object) -> bool:
        """Método responsável por verificar a nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            return self.toolbox.inner_text(page, FiscalFields.TEXT_SITUATION_MANIFESTED).lower() == SITUATION_APPROVED['situation_manifested_approved'].lower()
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar a nota fiscal: {e}")
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
            return False

    def manifest_invoice(self, page: object) -> bool:
        """Método responsável por manifestar a nota fiscal."""	
        try:
            if not self.verify_parameters(page):
                self.logger.info("Nota fiscal não está apta para manifestação")
                return False
            
            if self.verify_invoice(page):  
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
            
            if not self.verify_situation_manifested(page):
                self.logger.info("Nota fiscal não está com a situação manifestada 'Confirmada Operação'")
                return False
            
            self.logger.info("Nota fiscal manifestada com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao tentar manifestar a nota fiscal: {e}")
            raise e
        
    def search_invoice(self, page:object, key: str):
        """Método responsável por buscar uma nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            result = update_invoice_attemps(self.db, key=key)
            if not result:
                raise Exception("Erro ao tentar atualizar a nota fiscal")
            
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, FiscalFields.BUTTON_CLEAN)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.fill(page, FiscalFields.FIELD_KEY, key)
            self.select_filter(page, FILTERS_SITUATION)
            self.toolbox.click(page, FiscalFields.BUTTON_SEARCH)
            self.toolbox.wait_for_timeout(page, 2000)

            self.toolbox.wait_for_selector(page, FiscalFields.BUTTON_LAUNCH)
            if not self.manifest_invoice(page):
                update_invoice_status(self.db, status=self.parameters.not_launched, key=key)
                self.logger.error(f"Erro ao tentar manifestar a nota fiscal {key}")
                raise Exception(f"Erro ao tentar manifestar a nota fiscal {key}")
            
            self.toolbox.click(page, FiscalFields.BUTTON_LAUNCH)
            self.logger.info(f"Busca pela nota fiscal {key} realizada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar buscar a nota fiscal {key}: {e}")
            raise e
        
    def insert_operation(self, page: object, operation: str):
        """Método responsável por lançar uma nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.fill(page, ImportXMLFields.FIELD_OPERATION, operation)
            self.toolbox.click(page, ImportXMLFields.BUTTON_NEXT)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/1 - inserindo_operacao.png")
            self.toolbox.click(page, ImportXMLFields.BUTTON_CONFIRM_NEXT)
            self.logger.info(f"Operação selecionada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao selecionar a operação: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/1 - erro_inserindo_operacao.png")
            raise e
       
    def verify_items(self, page: object) -> None:
        """Método responsável por verificar os itens da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/2 - verificando_itens.png")
            self.toolbox.click(page, ImportXMLFields.BUTTON_NEXT)
            self.logger.info("Itens da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os itens da nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/2 - erro_verificando_itens.png")
            raise e

    def entry(self, page: object, checker: str, vendor: str, payment_policy: str, cost_center: str):
        """Método responsável por preencher os campos da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 5000)
            self.toolbox.fill(page, LaunchNFSe.FIELD_CHECKER, checker)
            self.toolbox.fill(page, LaunchNFSe.FIELD_VENDOR, vendor)
            self.toolbox.fill(page, LaunchNFSe.FIELD_PAYMENT_POLICY, payment_policy)
            self.toolbox.fill(page, LaunchNFSe.FIELD_COST_CENTER, cost_center)
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/3 - preenchendo_campos.png")
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT)
            self.logger.info("Campos preenchidos com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao preencher os campos da nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/3 - erro_preenchendo_campos.png")
            raise e
        
    def totals(self, page: object) -> None:
        """Método responsável por verificar os totais da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TAB_TOTALS)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/4 - verificando_totais.png")
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT)
            self.logger.info("Totais da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os totais da nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/4 - erro_verificando_totais.png")
            raise e
    
    def items(self, page: object) -> None:
        """Método responsável por verificar os itens da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TABLE_ITEMS)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/5 - verificando_itens_nota.png")
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT_ITEMS_TAXES)
            self.logger.info("Itens da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os itens da nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/5 - erro_verificando_itens_nota.png")
            raise e
        
    def taxes(self, page: object) -> None:
        """Método responsável por verificar os impostos da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TAB_TAXES)
            self.toolbox.wait_for_timeout(page, 1000)

            if not self.verify_error(page):
                raise Exception("Erro encontrado na tela")
            
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/6 - verificando_impostos.png")
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT_ITEMS_TAXES)
            self.logger.info("Impostos da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os impostos da nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/6 - erro_verificando_impostos.png")
            raise e
    
    def installments(self, page: object) -> None:
        """Método responsável por verificar as parcelas da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TABLE_INSTALLMENTS)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/7 - verificando_parcelas.png")
            self.toolbox.click(page, LaunchNFSe.BUTTON_CONFIRM)
            self.logger.info("Parcelas da nota fiscal verificadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar as parcelas da nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/7 - erro_verificando_parcelas.png")
            raise e
        
    def launch_invoice(self, page: object, operation: str, checker: str, vendor: str, payment_policy: str, cost_center: str):
        """Método responsável por lançar uma nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            result = update_invoice_status(self.db, status=self.parameters.launching, key=self.invoice_id)

            if not result:
                self.logger.error("Erro ao tentar atualizar a nota fiscal")
                update_invoice_status(self.db, status=self.parameters.not_launched, key=self.invoice_id)
                raise Exception("Erro ao tentar atualizar a nota fiscal")
            
            self.toolbox.wait_for_timeout(page, 5000)
            if not self.navigator.validate_rotine(page, LaunchNFSe.TITLE_LAUNCH_NFSE, LaunchNFSe.ROTINE):
                self.insert_operation(page, operation)
                self.verify_items(page)

            self.entry(page, checker, vendor, payment_policy, cost_center)
            self.totals(page)
            self.items(page)
            self.taxes(page)
            self.installments(page)

            result = update_invoice_status(self.db, status=self.parameters.launched, key=self.invoice_id)

            if not result:
                update_invoice_status(self.db, status=self.parameters.to_review, key=self.invoice_id)

            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/8 - nota_fiscal_lancada.png")
            self.logger.info("Nota fiscal lançada com sucesso")
        except Exception as e:
            update_invoice_status(self.db, status=self.parameters.not_launched, key=self.invoice_id)
            self.logger.error(f"Erro ao tentar lançar a nota fiscal: {e}")
            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/8888 - erro_nota_fiscal_lancada.png")
            raise e
        
    def execute(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                page.goto(self.url)
                self.login(page)

                try:
                    key = self.data.key
                    branch_number = self.data.branch_number
                    branch_name = self.data.branch_name
                    operation = self.data.operation
                    checker = self.data.checker
                    vendor = self.data.seller
                    cost_center = self.data.center
                    payment_policy = self.data.policy
                    products = self.data.products if self.data.products else []

                    self.logger.info(f"Processando a nota fiscal {key}")

                    self.select_branch(page, branch_number, branch_name)

                    updated_product = UpdateProduct.process_update_product(self.toolbox, self.logger, page, products)
                    if not updated_product:
                        self.logger.error(f"Erro ao tentar atualizar o cadastro de produtos")
                        self.close(browser)

                    self.access_module(page)
                    self.search_invoice(page, key)
                    self.launch_invoice(page, operation, checker, vendor, payment_policy, cost_center)
                    page.wait_for_timeout(5000)

                    self.logger.info(f"Processamento da nota fiscal {key} finalizado com sucesso")
                except Exception as e:
                    self.logger.error(f"Erro ao tentar processar a nota fiscal {key}: {e}")
                    self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/9999 - processamento_nota_fiscal.png")
                    self.close(browser)

                self.logger.info("Automação finalizada com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao tentar executar a automação: {e}")
                self.close(browser)
            finally:
                self.close(browser)
    
    def __str__(self):
        return f"""
        URL: {self.url}
        Chave: {self.invoice_id}
        Filial: {self.data.branch_name}
        Operação: {self.data.operation}
        Checagem: {self.data.checker}
        Vendedor: {self.data.seller}
        Centro de Custo: {self.data.center}
        Política de Pagamento: {self.data.policy}
        Produtos para atualização: {len(self.data.products)}
        """