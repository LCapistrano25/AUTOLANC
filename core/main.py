import os
import sys
import time
import threading
from decouple import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from automation.factory import AutomationFactory
from core.utils import verify_directory_exists
from database.utils import (
    get_parameters, 
    get_invoices,
    get_type_launch, 
    origin_diverget,
)

from database.factory import FactoryDatabaseConnection

class BrowserAutomationThread(threading.Thread):
    """Thread para execução de automação de notas fiscais."""
    def __init__(self, automation):
        super().__init__()
        self.automation = automation

    def run(self):
        self.automation.execute()

def start_browser_automation():
    """Inicia a automação de notas fiscais."""
    db = FactoryDatabaseConnection.select_connection(db_name='fourmaqconnect')
    parameters = get_parameters(db)
    invoices = get_invoices(db, lauch_status=parameters.not_launched, limit=config("LIMIT"))

    if not invoices:
        print("Nenhuma nota fiscal encontrada.")
        return
    
    if not verify_directory_exists(config("DIR_LOGS")):
        print(f"Diretório de logs não encontrado: {config('DIR_LOGS')}")
        return
    
    threads = []
    
    for invoice in invoices:
        try:
            type_launch = get_type_launch(invoice.entry_type)

            if not type_launch:
                print(f"Tipo de lançamento inválido para a nota {invoice.key}.")
                continue
            
            products = origin_diverget(db, invoice.key)
            if products:
                invoice.set_products(products)

            automation=AutomationFactory.create_automation(
                type_launch,
                url=config("URL"),
                username=config("USERNAMES"),
                password=config("NEW_PASSWORD"),
                data=invoice,
                dir_logs=config("DIR_LOGS"),
                db=db,
                parameters=parameters
            )

            print(automation)

            thread = BrowserAutomationThread(automation)
            threads.append(thread)
            thread.start()
        except Exception as e:
            print(f"Erro ao iniciar automação para a nota {invoice.key}: {e}")

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    while True:
        start_browser_automation()
        time.sleep(15)
