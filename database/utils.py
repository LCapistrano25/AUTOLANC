import os
import sys
from decouple import config

from database.db import DatabaseConnection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "repositories")))

from database.repositories.invoice_repository import InvoiceRepository
from database.repositories.parameters_repository import ParametersRepository
from database.repositories.item_fourmaq_repository import ItemFourmaqRepository
from database.repositories.item_solution_repository import ItemSolutionRepository

TYPE_LAUNCH = {
    'Nota de Produto/Transferência entre Filiais': 'transfer_notes',
    'Notas de Produtos/Compra para Revenda': 'product_notes',
}

def get_invoices(db, **kwargs):
    """Responsável por buscar as notas fiscais no banco de dados."""
    try:
        return InvoiceRepository(db).get_invoices(
            lauch_status=kwargs.get("lauch_status"), 
            limit=kwargs.get("limit")
        )
    except Exception as e:
        print(f"Erro ao tentar buscar as notas fiscais: {e}")
        return []
    
def get_parameters(db):
    """Responsável por buscar os parâmetros no banco de dados."""
    try:
        return ParametersRepository(db).get_parameters()
    except Exception as e:
        print(f"Erro ao tentar buscar os parâmetros: {e}")
        return []

def get_items_solution(db, *args, **kwargs):
    """Responsável por buscar os itens da solução."""
    try:
        return ItemSolutionRepository(db).get_item_solution(code_product=kwargs.get("code_product"))
    except Exception as e:
        print(f"Erro ao tentar buscar os itens da solução: {e}")
        return []
    
def get_items_fourmaqconnect(db, *args, **kwargs):
    """Responsável por buscar os itens da FourmaqConnect."""
    try:
        return ItemFourmaqRepository(db).get_item_fourmaq(access_key=kwargs.get("access_key"))
    except Exception as e:
        print(f"Erro ao tentar buscar os itens da FourmaqConnect: {e}")
        return []

def get_type_launch(entry_type):
    """Responsável por buscar o tipo de lançamento."""
    try:
        return TYPE_LAUNCH.get(entry_type, None)
    except Exception as e:
        print(f"Erro ao tentar buscar o tipo de lançamento: {e}")
        return None

def update_invoice_status(db, *args, **kwargs):
    """Responsável por atualizar a nota fiscal."""
    try:
       return InvoiceRepository(db).update_invoice_status(status=kwargs.get("status"), key=kwargs.get("key"))
    except Exception as e:
        print(f"Erro ao tentar atualizar a nota fiscal: {e}")
        return False

def update_invoice_attemps(db, *args, **kwargs):
    """Responsável por atualizar a nota fiscal com erro."""
    try:
        return InvoiceRepository(db).update_invoice_attempts(key=kwargs.get("key"))
    except Exception as e:
        print(f"Erro ao tentar atualizar a nota fiscal com erro: {e}")
        return False

def origin_diverget(db, access_key):
    """Responsável por verificar a divergência de origem."""
    try:
        items_fourmaqconnect = get_items_fourmaqconnect(db, access_key=access_key)
        
        db_solution = connect_to_database_solution()
        divergent = []
        for item in items_fourmaqconnect:
            code = item.code
            origin = item.origin

            items_solution = get_items_solution(db_solution, code_product=code)
            
            if not items_solution:
                continue
            
            if origin != items_solution.origin:
                divergent.append(item)

        return divergent
    except Exception as e:
        print(f"Erro ao tentar verificar a divergência de origem: {e}")
        return []

def connect_to_database_fourmaqconnect():
    """Responsável por conectar ao banco de dados."""
    try:
        db = DatabaseConnection(
            db_type=config("DB_TYPE_DEFAULT"),
            db_name=config("DB_NAME_DEFAULT"),
            user=config("DB_USER_DEFAULT"),
            password=config("DB_PASSWORD_DEFAULT"),
            host=config("DB_HOST_DEFAULT"),
            port=config("DB_PORT_DEFAULT")
        )

        db.connect()
        return db
    except Exception as e:
        print(f"Erro ao tentar conectar ao banco de dados: {e}")
        return None

def connect_to_database_solution():
    """Responsável por conectar ao banco de dados da solução."""
    try:
        db = DatabaseConnection(
            db_type=config("DB_TYPE_SOLUTION"),
            db_name=config("DB_NAME_SOLUTION"),
            user=config("DB_USER_SOLUTION"),
            password=config("DB_PASSWORD_SOLUTION"),
            host=config("DB_HOST_SOLUTION"),
            port=config("DB_PORT_SOLUTION")
        )
        db.connect()
        return db
    except Exception as e:
        print(f"Erro ao tentar conectar ao banco de dados da solução: {e}")
        return None
    