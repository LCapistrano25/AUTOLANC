from playwright.sync_api import sync_playwright

from automation.context import Context
from automation.handlers.sidebar_navigator import SidebarNavigator
from automation.handlers.module_navigator import ModuleNavigator
from automation.handlers.navigation_helper import NavigationHelper
from database.utils import update_invoice_status, update_invoice_attemps

from automation.base import Automation
from automation.helpers.update_product import UpdateProduct
from automation.validators.purchase_resale_validator import PurchaseResaleValidator

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

class PurchaseResaleManifestation:
    """
    Classe responsável por manifestar uma nota fiscal de compra e revenda.
    """
    def __init__(self, context: Context, validator: PurchaseResaleValidator):
        self.context = context
        self.page = context.get_page()
        self.toolbox = context.get_toolbox()
        self.logger = context.get_logger()
        self.data = context.get_data()
        self.db = context.get_db()
        self.parameters = context.get_parameters()
        self.validator = validator

    def manifest(self):
        """Método responsável por manifestar a nota fiscal."""
        self._update_attempts()
        self._search_invoice()

        if not self.validator.verify_parameters(self.page):
            self.logger.info("Nota fiscal não está apta para manifestação")
            return False

        if self.validator.verify_invoice(self.page):
            self.logger.info("Nota fiscal já manifestada")
            self.toolbox.click(self.page, FiscalFields.BUTTON_LAUNCH)
            return True
        
        if self._already_manifested():
            self.logger.info("Nota fiscal não está apta para manifestação")
            return False
        
        if not self._is_checked():
            self.logger.info("Erro ao tentar manifestar a nota fiscal")
            return False
        
        if not self._confirm_manifestation():
            self.logger.error("Erro ao tentar confirmar a manifestação da nota fiscal")
            return False
        
        self.toolbox.click(self.page, FiscalFields.BUTTON_LAUNCH)
        return True
    
    def _select_filters(self):
        """Método responsável por selecionar os filtros da nota fiscal."""
        self.toolbox.wait_for_timeout(self.page, 1000)
        self.toolbox.select_option(self.page, FiscalFields.DROPDOWN_SITUATION_MANIFESTED, FILTERS_SITUATION['situation_manifested'])
        self.toolbox.select_option(self.page, FiscalFields.DROPDOWN_DOCUMENT_TYPE, FILTERS_SITUATION['document_type'])
        self.toolbox.select_option(self.page, FiscalFields.DROPDOWN_SITUATION, FILTERS_SITUATION['situation'])
        self.logger.info("Filtros da nota fiscal selecionados com sucesso")

    def _search_invoice(self):
        """Método responsável por buscar uma nota fiscal."""
        self.toolbox.wait_for_timeout(self.page, 2000)
        self.toolbox.click(self.page, FiscalFields.BUTTON_CLEAN)
        self.toolbox.wait_for_timeout(self.page, 2000)
        self.toolbox.fill(self.page, FiscalFields.FIELD_KEY, self.data.key)
        self._select_filters()
        self.toolbox.click(self.page, FiscalFields.BUTTON_SEARCH)
        self.toolbox.wait_for_timeout(self.page, 2000)

    def _update_attempts(self):
        """Método responsável por atualizar as tentativas de busca da nota fiscal."""
        result = update_invoice_attemps(self.db, key=self.data.key)
        if not result:
            raise Exception("Erro ao atualizar tentativas da nota.")

    def _already_manifested(self):
        """Método responsável por verificar se a nota fiscal já foi manifestada."""
        situation = self.toolbox.inner_text(self.page, FiscalFields.TEXT_SITUATION_MANIFESTED)
        return situation.lower() not in SITUATION_APPROVED['situation_manifested_not_approved'].lower()
    
    def _is_checked(self):
        """Método responsável por verificar se a nota fiscal está selecionada."""
        self.toolbox.check(self.page, FiscalFields.CHECKBOX_SELECT_INVOICE)
        self.toolbox.wait_for_timeout(self.page, 2000)

        if not self.toolbox.is_checked(self.page, FiscalFields.CHECKBOX_SELECT_INVOICE):
            self.logger.info("Erro ao tentar manifestar a nota fiscal")
            return False
        
        self.toolbox.click(self.page, FiscalFields.BUTTON_MANIFEST)
        self.toolbox.wait_for_timeout(self.page, 2000)
        return True

    def _confirm_manifestation(self):
        """Método responsável por confirmar a manifestação da nota fiscal."""   
        iframe = self.toolbox.obtain_frame(self.page, FiscalFields.IFRAME_CONFIRM_OPERATION)
        self.toolbox.wait_for_timeout(self.page, 3000)
        self.toolbox.frame_check(iframe, FiscalFields.OPTION_CONFIRM_OPERATION, force=True)
        self.toolbox.wait_for_timeout(self.page, 2000)
        self.toolbox.frame_click(iframe, FiscalFields.BUTTON_MANIFEST_CONFIRM)
        self.toolbox.wait_for_timeout(self.page, 2000)

        try:
            self.toolbox.wait_for_timeout(self.page, 3000)
            self.toolbox.wait_for_selector(self.page, ManualSelectionPopupFields.POPUP_CONFIRM_OPERATION)
            self.toolbox.click(self.page, ManualSelectionPopupFields.BUTTON_UPDATE_SITUATION)
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.wait_for_selector(self.page, SelectEventPopupFields.POPUP_CONFIRM_EVENT)
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.select_option(self.page, SelectEventPopupFields.DROPDOWN_SITUATION, SITUATION_APPROVED['situation_manifested_approved'])
            self.toolbox.click(self.page, SelectEventPopupFields.BUTTON_CONFIRM_EVENT)
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.click(self.page, ManualSelectionPopupFields.BUTTON_CONFIRM_SITUATION)
            self.toolbox.wait_for_timeout(self.page, 5000)
            self.logger.info("Manifestação da nota fiscal confirmada com sucesso")
            return True
        except Exception as e:
            self.logger.warning(f"Popup de confirmação não encontrado: {e}")
            return False

class PurchaseResaleLauncher:
    def __init__(self, context: Context, navigator: NavigationHelper):
        self.context = context
        self.dir_logs = context.get_dir_logs()
        self.page = context.get_page()
        self.toolbox = context.get_toolbox()
        self.logger = context.get_logger()
        self.data = context.get_data()
        self.db = context.get_db()
        self.parameters = context.get_parameters()
        self.invoice_id = context.get_data().key
        self.navigator = navigator

    def launch(self, operation: str, checker: str, vendor: str, payment_policy: str, cost_center: str):
        """Método responsável por lançar uma nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(self.page, 2000)
            result = update_invoice_status(self.db, status=self.parameters.launching, key=self.invoice_id)

            if not result:
                self.logger.error("Erro ao tentar atualizar a nota fiscal")
                update_invoice_status(self.db, status=self.parameters.not_launched, key=self.invoice_id)
                raise Exception("Erro ao tentar atualizar a nota fiscal")

            self.toolbox.wait_for_timeout(self.page, 5000)
            if not self.navigator.validate_rotine(self.page, LaunchNFSe.TITLE_LAUNCH_NFSE, LaunchNFSe.ROTINE):
                self._insert_operation(operation)
                self._verify_items()

            self._entry(checker, vendor, payment_policy, cost_center)
            self._totals()
            self._items()
            self._taxes()
            self._installments()

            result = update_invoice_status(self.db, status=self.parameters.launched, key=self.invoice_id)

            if not result:
                update_invoice_status(self.db, status=self.parameters.to_review, key=self.invoice_id)

            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/8 - nota_fiscal_lancada.png")
            self.logger.info("Nota fiscal lançada com sucesso")
        except Exception as e:
            update_invoice_status(self.db, status=self.parameters.not_launched, key=self.invoice_id)
            self.logger.error(f"Erro ao tentar lançar a nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/8888 - erro_nota_fiscal_lancada.png")
            raise e

    def _insert_operation(self, operation: str):
        """Método responsável por lançar uma nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.fill(self.page, ImportXMLFields.FIELD_OPERATION, operation)
            self.toolbox.click(self.page, ImportXMLFields.BUTTON_NEXT)
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/1 - inserindo_operacao.png")
            self.toolbox.click(self.page, ImportXMLFields.BUTTON_CONFIRM_NEXT)
            self.logger.info(f"Operação selecionada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao selecionar a operação: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/1 - erro_inserindo_operacao.png")
            raise e
       
    def _verify_items(self) -> None:
        """Método responsável por verificar os itens da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/2 - verificando_itens.png")
            self.toolbox.click(self.page, ImportXMLFields.BUTTON_NEXT)
            self.logger.info("Itens da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os itens da nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/2 - erro_verificando_itens.png")
            raise e

    def _entry(self, checker: str, vendor: str, payment_policy: str, cost_center: str):
        """Método responsável por preencher os campos da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_timeout(self.page, 5000)
            self.toolbox.fill(self.page, LaunchNFSe.FIELD_CHECKER, checker)
            self.toolbox.fill(self.page, LaunchNFSe.FIELD_VENDOR, vendor)
            self.toolbox.fill(self.page, LaunchNFSe.FIELD_PAYMENT_POLICY, payment_policy)
            self.toolbox.fill(self.page, LaunchNFSe.FIELD_COST_CENTER, cost_center)
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/3 - preenchendo_campos.png")
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.click(self.page, LaunchNFSe.BUTTON_NEXT)
            self.logger.info("Campos preenchidos com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao preencher os campos da nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/3 - erro_preenchendo_campos.png")
            raise e
        
    def _totals(self) -> None:
        """Método responsável por verificar os totais da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_selector(self.page, LaunchNFSe.TAB_TOTALS)
            self.toolbox.wait_for_timeout(self.page, 1000)
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/4 - verificando_totais.png")
            self.toolbox.click(self.page, LaunchNFSe.BUTTON_NEXT)
            self.logger.info("Totais da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os totais da nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/4 - erro_verificando_totais.png")
            raise e

    def _items(self) -> None:
        """Método responsável por verificar os itens da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_selector(self.page, LaunchNFSe.TABLE_ITEMS)
            self.toolbox.wait_for_timeout(self.page, 1000)
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/5 - verificando_itens_nota.png")
            self.toolbox.click(self.page, LaunchNFSe.BUTTON_NEXT_ITEMS_TAXES)
            self.logger.info("Itens da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os itens da nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/5 - erro_verificando_itens_nota.png")
            raise e

    def _taxes(self) -> None:
        """Método responsável por verificar os impostos da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_selector(self.page, LaunchNFSe.TAB_TAXES)
            self.toolbox.wait_for_timeout(self.page, 1000)

            if not self._verify_error(self.page):
                raise Exception("Erro encontrado na tela")

            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/6 - verificando_impostos.png")
            self.toolbox.click(self.page, LaunchNFSe.BUTTON_NEXT_ITEMS_TAXES)
            self.logger.info("Impostos da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os impostos da nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/6 - erro_verificando_impostos.png")
            raise e

    def _installments(self) -> None:
        """Método responsável por verificar as parcelas da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_selector(self.page, LaunchNFSe.TABLE_INSTALLMENTS)
            self.toolbox.wait_for_timeout(self.page, 1000)
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/7 - verificando_parcelas.png")
            self.toolbox.click(self.page, LaunchNFSe.BUTTON_CONFIRM)
            self.logger.info("Parcelas da nota fiscal verificadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar as parcelas da nota fiscal: {e}")
            self.toolbox.screenshot(self.page, f"{self.dir_logs}/{self.invoice_id}/7 - erro_verificando_parcelas.png")
            raise e

    def _verify_error(self) -> bool:
        """Método responsável por verificar se existe erro na tela."""
        try:
            self.toolbox.wait_for_load_state(self.page, 'networkidle')
            self.toolbox.wait_for_timeout(self.page, 2000)
            self.toolbox.wait_for_selector(self.page, LaunchNFSe.ERROR_TAXES)
            error_message = self.toolbox.inner_text(self.page, LaunchNFSe.ERROR_TAXES).lower()
            if error_message:
                self.logger.info(f"Erro encontrado na tela: {error_message}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar erro na tela: {e}")
            return True
        
class PurchaseResaleAutomation(Automation):
    """Classe responsável por automatizar o processo de compra e revenda de notas fiscais."""
    def __init__(self, url, username, password, context: Context):
        self.context = context
        self.db = context.get_db()
        self.parameters = context.get_parameters()
        self.invoice_id = context.get_data().key
        self.dir_logs = context.get_dir_logs()
        self.logger = context.get_logger()
        self.data = context.get_data()

        super().__init__(url, username, password, context)

        self.navigator = NavigationHelper(toolbox=self.toolbox, logger=self.logger)
        self.validator = PurchaseResaleValidator(toolbox=self.toolbox, logger=self.logger)

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
    
    def _update_products(self, page: object, products: list) -> bool:
        """Método responsável por atualizar os produtos."""
        try:
            updated_product = UpdateProduct.process_update_product(self.toolbox, self.logger, page, products)
            if not updated_product:
                self.logger.error("Erro ao tentar atualizar o cadastro de produtos")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Erro ao tentar atualizar os produtos: {e}")
            return False
        
    def _access_module(self, page: object) -> None:
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
    
    def _execute_manifestation(self):
        """Método responsável por executar a manifestação da nota fiscal."""
        try:
            manifestor = PurchaseResaleManifestation(
                context=self.context, 
                validator=self.validator
            )
            manifestor.manifest()
        except Exception as e:
            self.logger.error(f"Erro ao tentar manifestar a nota fiscal: {e}")
            raise e
        
    def _execute_launcher(self, operation: str, checker: str, vendor: str, payment_policy: str, cost_center: str):
        """Método responsável por executar o lançamento da nota fiscal."""
        try:
            launcher = PurchaseResaleLauncher(
                context=self.context,
                navigator=self.navigator
            )
            launcher.launch(
                operation=operation, 
                checker=checker, 
                vendor=vendor, 
                payment_policy=payment_policy, 
                cost_center=cost_center
            )
        except Exception as e:
            self.logger.error(f"Erro ao tentar lançar a nota fiscal: {e}")
            raise e
        
    def execute(self):
        """Método responsável por executar a automação de compra e revenda de notas fiscais."""
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

                    if not self._update_products(page, products):
                        raise Exception("Erro ao tentar atualizar os produtos")

                    self._access_module(page)
                    
                    self.context.set_page(page)

                    self._execute_manifestation()

                    self._execute_launcher(
                        operation=operation, 
                        checker=checker, 
                        vendor=vendor, 
                        payment_policy=payment_policy, 
                        cost_center=cost_center
                    )
                
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
