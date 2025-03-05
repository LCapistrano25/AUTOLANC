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
        db_type='sqlite',
        db_name='db.sqlite3',
    )

    db.connect()
    return db

def start_thread(automation):
    automation_thread = BrowserAutomationThread(automation)
    automation_thread.start()
    automation_thread.join()

def start_browser_automation():

    db = connect_to_database()

    invoices = db.execute_query('''SELECT data_emissao as EMISSAO, numero_nota AS NUMERO, chave_acesso AS CHAVE
                                FROM tb_notas_fiscais''')
    
    print(invoices)
    
    automation = ProductNotesAutomation(
        url=config("URL"),
        username="SUPERVISOR",
        password=config("PASSWORD"),
        data=[
            {
                'chave': '35241255962369000924550840002911321000650030',
                'filial': '1', 
                'filial_name': 'PALMAS', 
                'operacao': '1', 
                'conferente': 'EUROBO', 
                'vendedor': '83', 
                'centro': '1', 
                'politica': '9999'
            },

            {
                'chave': '17241101581193000265550010001321901809799238',
                'filial': '2', 
                'filial_name': 'GURUPI', 
                'operacao': '1', 
                'conferente': 'EUROBO', 
                'vendedor': '83', 
                'centro': '1', 
                'politica': '9999'
            },

            {
                'chave': '35241255962369000924550840002927151000650037',
                'filial': '2', 
                'filial_name': 'GURUPI', 
                'operacao': '1', 
                'conferente': 'EUROBO', 
                'vendedor': '83', 
                'centro': '1', 
                'politica': '9999'
            },

            {
                'chave': '35241255962369000924550840002897901000650030',
                'filial': '2', 
                'filial_name': 'GURUPI', 
                'operacao': '1', 
                'conferente': 'EUROBO', 
                'vendedor': '83', 
                'centro': '1', 
                'politica': '9999'
            },
            
            ]
    )
        
    start_thread(automation)


if __name__ == "__main__":
    start_browser_automation()
