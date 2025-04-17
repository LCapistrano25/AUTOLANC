import os
import sys
import threading
import time
from decouple import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from automation.factory import AutomationFactory
from core.utils import (
    connect_to_database_fourmaqconnect, 
    process_invoices, 
    process_parameters,
    TYPE_LAUNCH
)

class BrowserAutomationThread(threading.Thread):
    """Thread para execução de automação de notas fiscais."""
    def __init__(self, automation):
        super().__init__()
        self.automation = automation

    def run(self):
        self.automation.execute()

def start_browser_automation():
    """Inicia a automação de notas fiscais."""
    db = connect_to_database_fourmaqconnect()
    parameters = process_parameters(db)  
    data = process_invoices(db, parameters['nao_lancado'], config("LIMIT"))

    if not data:
        print("Nenhuma nota fiscal encontrada.")
        return
    
    threads = []

    for invoice in data:
        try:
            automation=AutomationFactory.create_automation(
                TYPE_LAUNCH[invoice['tipo_lancamento']],
                url=config("URL"),
                username=config("USERNAMES"),
                password=config("PASSWORD"),
                data=[invoice],
                dir_logs=config("DIR_LOGS"),
                db=db,
                parameters=parameters
            )

            thread = BrowserAutomationThread(automation)
            threads.append(thread)
            thread.start()
        except Exception as e:
            print(f"Erro ao iniciar automação para a nota {invoice['chave']}: {e}")

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    while True:
        start_browser_automation()
        time.sleep(30)
