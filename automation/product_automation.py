import time
from playwright.sync_api import sync_playwright
from automation.automation import Automation
from complements.fields import (
    HomeFields, 
    HomeMenuFields, 
    FiscalFields, 
    ImportXMLFields, 
    LaunchNFSe,
    FILTERS_SITUATION
)

class ProductNotesAutomation(Automation):
    def __init__(self, url, username, password, toolbox=None, data=None):
        super().__init__(url, username, password, toolbox, data)

    def get_branch_actual(self, page):
        """Método responsável por retornar o texto da filial atual."""
        text = self.toolbox.inner_text(page, HomeFields.BUTTON_SWITCH_BRANCH, timeout=5000)
        return text
    
    def validate_branch(self, page, branch_text):
        """Método responsável por validar a filial atual."""
        try:
            text = self.get_branch_actual(page).split(' | ')[-1]  # Captura a filial atual
            return branch_text.lower() == text.lower()  # Retorna True se for igual
        except Exception as e:
            self.logger.error(f"Erro na tentativa de validar a {branch_text}: {e}")
            return False  # Retorna False em caso de erro

    def validate_rotine(self, page, selector, rotine):
        """Método responsável por validar o módulo atual."""
        try:
            text = self.toolbox.inner_text(page, selector, timeout=5000).split(' - ')[-1]
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
        """Seleciona a filial desejada."""
        if self.validate_branch(page, branch_name):
            self.logger.info(f"A filial {branch_name} já está selecionada")
            return 
        
        self.logger.info(f"Selecionando a filial {branch_name}")
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
                self.toolbox.click(page, FiscalFields.SIDEBAR_FISCAL)
                self.toolbox.click(page, FiscalFields.OPTION_INVOICE)
                self.logger.info("Acesso ao módulo fiscal e opção de nota fiscal realizado com sucesso")
            else:
                self.logger.info("O módulo fiscal e a opção de nota fiscal já estão acessados")

        except Exception as e:
            self.logger.error(f"Erro ao tentar acessar módulo fiscal e opção de fatura: {e}")
            raise e
        finally:
            self.logger.info("Acesso ao módulo fiscal e opção de nota fiscal finalizado")

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
        
    def search_invoice(self, page:object, key: str):
        """Método responsável por buscar uma nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.click(page, FiscalFields.BUTTON_CLEAN)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.fill(page, FiscalFields.FIELD_KEY, key)
            self.select_filter(page, FILTERS_SITUATION)
            self.toolbox.click(page, FiscalFields.BUTTON_SEARCH)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, FiscalFields.BUTTON_LAUNCH)
            self.logger.info(f"Busca pela nota fiscal {key} realizada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar buscar a nota fiscal {key}: {e}")
            raise e
        finally:
            self.logger.info("Busca pela nota fiscal finalizada")
    
    def insert_operation(self, page: object, operation: str):
        """Método responsável por lançar uma nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.fill(page, ImportXMLFields.FIELD_OPERATION, operation)
            self.toolbox.click(page, ImportXMLFields.BUTTON_NEXT)
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, ImportXMLFields.BUTTON_CONFIRM_NEXT)
            self.logger.info(f"Operação selecionada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao selecionar a operação: {e}")
            raise e
       
    def verify_items(self, page: object) -> None:
        """Método responsável por verificar os itens da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_timeout(page, 2000)
            self.toolbox.click(page, ImportXMLFields.BUTTON_NEXT)
            self.logger.info("Itens da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os itens da nota fiscal: {e}")
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
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT)
            self.logger.info("Campos preenchidos com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao preencher os campos da nota fiscal: {e}")
            raise e
        
    def totals(self, page: object) -> None:
        """Método responsável por verificar os totais da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TAB_TOTALS)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT)
            self.logger.info("Totais da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os totais da nota fiscal: {e}")
            raise e
    
    def items(self, page: object) -> None:
        """Método responsável por verificar os itens da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TABLE_ITEMS)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT_ITEMS_TAXES)
            self.logger.info("Itens da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os itens da nota fiscal: {e}")
            raise e
        
    def taxes(self, page: object) -> None:
        """Método responsável por verificar os impostos da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TAB_TAXES)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.click(page, LaunchNFSe.BUTTON_NEXT_ITEMS_TAXES)
            self.logger.info("Impostos da nota fiscal verificados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar os impostos da nota fiscal: {e}")
            raise e
    
    def installments(self, page: object) -> None:
        """Método responsável por verificar as parcelas da nota fiscal."""
        try:
            self.toolbox.wait_for_load_state(page, 'networkidle')
            self.toolbox.wait_for_selector(page, LaunchNFSe.TABLE_INSTALLMENTS)
            self.toolbox.wait_for_timeout(page, 1000)
            self.toolbox.click(page, LaunchNFSe.BUTTON_CONFIRM)
            self.logger.info("Parcelas da nota fiscal verificadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar verificar as parcelas da nota fiscal: {e}")
            raise e
        
    def launch_invoice(self, page: object, operation: str, checker: str, vendor: str, payment_policy: str, cost_center: str):
        """Método responsável por lançar uma nota fiscal."""
        try:
            self.toolbox.wait_for_timeout(page, 2000)
            if not self.validate_rotine(page, LaunchNFSe.TITLE_LAUNCH_NFSE, LaunchNFSe.ROTINE):
                self.insert_operation(page, operation)
                self.verify_items(page)

            self.entry(page, checker, vendor, payment_policy, cost_center)
            self.totals(page)
            self.items(page)
            self.taxes(page)
            self.installments(page)

            self.logger.info("Nota fiscal lançada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao tentar lançar a nota fiscal: {e}")
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
                        self.access_module(page)
                        self.search_invoice(page, i['chave'])
                        self.launch_invoice(page, i['operacao'], i['conferente'], i['vendedor'], i['politica'], i['centro'])
                        page.wait_for_timeout(5000)

                        self.logger.info(f"Processamento da nota fiscal {i['chave']} finalizado com sucesso")
                    except Exception as e:
                        self.logger.error(f"Erro ao tentar processar a nota fiscal {i['chave']}: {e}")
                        continue

                self.logger.info("Automação finalizada com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao tentar executar a automação: {e}")
                raise e
            finally:
                self.close(browser)