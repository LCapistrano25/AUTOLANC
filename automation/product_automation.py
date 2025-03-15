from playwright.sync_api import sync_playwright

from core.utils import update_invoice, update_invoice_error
from automation.automation import Automation
from automation.update_product import UpdateProduct
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

class ProductNotesAutomation(Automation):
    def __init__(self, url, username, password, toolbox=None, data=None, dir_logs='logs', db=None, parameters=None):
        self.db = db
        self.parameters = parameters
        self.invoice_id = data[0]['chave']
        self.dir_logs = dir_logs
        self.logger = Logger(self.invoice_id, log_file=f'{self.dir_logs}/{self.invoice_id}/{self.invoice_id}.log', invoice_id=self.invoice_id)
        super().__init__(url, username, password, toolbox, data, self.logger)

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
            return rotine == text
        except Exception as e:
            self.logger.error(f"Erro ao validar a rotina {rotine}: {e}")
            return False
    
    def login(self, page):
        """Método responsável por realizar o login no sistema."""
        super().login(page)

    def close(self, browser):
        """Método responsável por fechar o navegador."""
        super().close(browser)

    def select_branch(self, page: object, branch_id: str, branch_name: str = None):
        """Método responsável por seleciona a filial desejada."""
        if self.validate_branch(page, branch_name):
            self.logger.info(f"OK - Filial selecionada {branch_name}")
            return 
        return super().select_branch(page, branch_id)
    
    def access_module(self, page: object) -> None:
        """Método responsável por acessar o módulo fiscal e a opção de nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            if not self.validate_rotine(page, FiscalFields.TITLE_FISCAL, FiscalFields.ROTINE):
                self.toolbox.wait_for_timeout(page, 2000)
                self.toolbox.click(page, HomeFields.ICON_MENU)
                self.toolbox.wait_for_selector(page, HomeMenuFields.MODULES)
                self.toolbox.click(page, HomeMenuFields.MODULE_FISCAL)
                self.toolbox.wait_for_selector(page, FiscalFields.SIDEBAR_FISCAL)
                self.toolbox.wait_for_timeout(page, 2000)
                self.toolbox.click(page, FiscalFields.SIDEBAR_FISCAL)
                self.toolbox.wait_for_timeout(page, 2000)
                self.toolbox.wait_for_selector(page, FiscalFields.OPTION_INVOICE)
                self.toolbox.click(page, FiscalFields.OPTION_INVOICE)
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
                
            self.logger.info("Nota fiscal manifestada com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao tentar manifestar a nota fiscal: {e}")
            raise e
        
    def search_invoice(self, page:object, key: str):
        """Método responsável por buscar uma nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            result = update_invoice_error(self.db, key)
            print(result)
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
                update_invoice(self.db, self.parameters['nao_lancado'], key)
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
            result = update_invoice(self.db, self.parameters['em_lancamento'], self.invoice_id)

            if not result:
                self.logger.error("Erro ao tentar atualizar a nota fiscal")
                update_invoice(self.db, self.parameters['nao_lancado'], self.invoice_id)
                raise Exception("Erro ao tentar atualizar a nota fiscal")
            
            if not self.validate_rotine(page, LaunchNFSe.TITLE_LAUNCH_NFSE, LaunchNFSe.ROTINE):
                self.insert_operation(page, operation)
                self.verify_items(page)

            self.entry(page, checker, vendor, payment_policy, cost_center)
            self.totals(page)
            self.items(page)
            self.taxes(page)
            self.installments(page)

            result = update_invoice(self.db, self.parameters['lancado'], self.invoice_id)

            if not result:
                update_invoice(self.db, self.parameters['a_conferir'], self.invoice_id)

            self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/8 - nota_fiscal_lancada.png")
            self.logger.info("Nota fiscal lançada com sucesso")
        except Exception as e:
            update_invoice(self.db, self.parameters['nao_lancado'], self.invoice_id)
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

                for i in self.data:
                    try:
                        self.logger.info(f"Processando a nota fiscal {i['chave']}")

                        self.select_branch(page, i['filial'], i['filial_name'])

                        updated_product = UpdateProduct.process_update_product(self.toolbox, self.logger, page, i['produtos'])
                        if not updated_product:
                            self.logger.error(f"Erro ao tentar atualizar o cadastro de produtos")
                            continue

                        self.access_module(page)
                        self.search_invoice(page, i['chave'])
                        self.launch_invoice(page, i['operacao'], i['conferente'], i['vendedor'], i['politica'], i['centro'])
                        page.wait_for_timeout(5000)

                        self.logger.info(f"Processamento da nota fiscal {i['chave']} finalizado com sucesso")
                    except Exception as e:
                        self.logger.error(f"Erro ao tentar processar a nota fiscal {i['chave']}: {e}")
                        self.toolbox.screenshot(page, f"{self.dir_logs}/{self.invoice_id}/9999 - processamento_nota_fiscal.png")
                        continue

                self.logger.info("Automação finalizada com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao tentar executar a automação: {e}")
                self.close(browser)
            finally:
                self.close(browser)