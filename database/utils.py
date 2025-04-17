import os
import sys
from decouple import config

from database.db import DatabaseConnection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "repositories")))

from database.repositories.invoice_repository import InvoiceRepository
from database.repositories.parameters_repository import ParametersRepository

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
    