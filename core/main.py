import os
import sys
import threading
from decouple import config

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from automation.product_automation import ProductNotesAutomation
from core.db import DatabaseConnection

class BrowserAutomationThread(threading.Thread):
    def __init__(self, automation):
        super().__init__()
        self.automation = automation

    def run(self):
        self.automation.execute()

def connect_to_database():
    db = DatabaseConnection(
        db_type=config("DB_TYPE_DEVELOPMENT"),
        db_name=config("DB_NAME_DEVELOPMENT"),
        user=config("DB_USER_DEVELOPMENT"),
        password=config("DB_PASSWORD_DEVELOPMENT"),
        host=config("DB_HOST_DEVELOPMENT"),
        port=config("DB_PORT_DEVELOPMENT")
    )

    db.connect()
    return db

def start_thread(automation):
    automation_thread = BrowserAutomationThread(automation)
    automation_thread.start()
    automation_thread.join()

def start_browser_automation():

    db = connect_to_database()

    invoices = db.execute_query('''SELECT data_emissao as EMISSAO, nome_fornecedor AS FORNECEDOR, chave AS CHAVE
                                FROM tb_notas_produtos 
                                WHERE id_status_nota_produto = %s''', (4,))
    
    automation = ProductNotesAutomation(
        url=config("URL"),
        username="SUPERVISOR",
        password=config("PASSWORD"),
        data=[{'chave': invoices[0][2],'filial': '1'}]
    )
        
    start_thread(automation)


if __name__ == "__main__":
    start_browser_automation()
