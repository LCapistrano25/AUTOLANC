from decouple import config
from core.db import DatabaseConnection
from core.consults import (
    INVOICES, 
    PARAMETERS, 
    UPDATE_INVOICE, 
    UPDATE_INVOICE_ERROR, 
    ITEMS_SOLUTION, 
    ITEMS_FOURMAQCONNECT
)

TYPE_LAUNCH = {
    'Nota de Produto/Transferência entre Filiais': 'transfer_notes',
    'Notas de Produtos/Compra para Revenda': 'product_notes',
}

class FactoryDatabaseConnection:
    @staticmethod
    def select_connection(db_name):
        """Responsável por selecionar a conexão com o banco de dados."""
        if db_name == "fourmaqconnect":
            return connect_to_database_fourmaqconnect()
        elif db_name == "solution":
            return connect_to_database_solution()
        else:
            raise ValueError("Banco de dados não suportado!")
        
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
    
def get_invoices(db, *args, **kwargs):
    """Responsável por buscar as notas fiscais no banco de dados."""
    try:
        invoices = db.execute_query(INVOICES, params=args)
        return invoices
    except Exception as e:
        print(f"Erro ao tentar buscar as notas fiscais: {e}")
        return []

def get_parameters(db):
    """Responsável por buscar os parâmetros no banco de dados."""
    try:
        parameters = db.execute_query(PARAMETERS)
        return parameters
    except Exception as e:
        print(f"Erro ao tentar buscar os parâmetros: {e}")
        return []

def format_products_update(db, access_key):
    """Responsável por formatar os produtos para atualização."""
    data = []
    products = get_items_fourmaqconnect(db, access_key)
    for product in products:
        data.append(
            {
                'codigo_produto': str(product[0]),
                'origem': str(product[1])
            }
        )
    return data

def format_invoices(db, invoices):
    """Responsável por formatar o dicionário de entrada""" 
    data = []
    for invoice in invoices:
        access_key = str(invoice[0])
        products = origin_diverget(db, access_key)
        data.append(
            {
                'chave': access_key,
                'filial': str(invoice[1]), 
                'filial_name': str(invoice[2]), 
                'operacao': str(invoice[3]), 
                'conferente': str(invoice[4]), 
                'vendedor': str(invoice[5]), 
                'centro': str(invoice[6]), 
                'politica': str(invoice[7]),
                'tipo_lancamento': str(invoice[8]),
                'numero_nota': str(invoice[9]),
                'produtos': products
            }
        )
    return data

def format_parameters(parameters):
    """Responsável por formatar o dicionário de entrada"""
    data = {}
    for parameter in parameters:
        data = {
            'nao_lancado': parameter[0],
            'em_lancamento': parameter[1],
            'lancado': parameter[2],
            'a_conferir': parameter[3]
        }
    return data

def process_invoices(db, *args, **kwargs):
    """Responsável por processar as notas fiscais."""
    invoices = get_invoices(db, *args, **kwargs)
    data = format_invoices(db, invoices)
    return data

def process_parameters(db):
    """Responsável por processar os parâmetros."""
    parameters = get_parameters(db)
    data = format_parameters(parameters)
    return data

def validate_parameters(parameters):
    """Responsável por validar os parâmetros."""
    if not parameters:
        print("Não foi possível buscar os parâmetros no banco de dados.")
        return False
    return True

def update_invoice(db, *args, **kwargs):
    """Responsável por atualizar a nota fiscal."""
    try:
        result = db.execute_query(UPDATE_INVOICE, params=args)
        return True if result else False
    except Exception as e:
        print(f"Erro ao tentar atualizar a nota fiscal: {e}")
        return False

def update_invoice_error(db, *args, **kwargs):
    """Responsável por atualizar a nota fiscal com erro."""
    try:
        result = db.execute_query(UPDATE_INVOICE_ERROR, params=args)
        return True if result else False
    except Exception as e:
        print(f"Erro ao tentar atualizar a nota fiscal com erro: {e}")
        return False

def consult_invoices():
    """Responsável por consultar as notas fiscais."""
    db = connect_to_database_fourmaqconnect()
    if not db:
        return
    
    parameters = process_parameters(db)
    if not validate_parameters(parameters):
        return
    
    data = process_invoices(db, parameters['nao_lancado'], config("LIMIT"))
    
    if not data:
        print("Nenhuma nota fiscal encontrada.")
        return
    
    return data

def get_items_solution(db, *args, **kwargs):
    """Responsável por buscar os itens da solução."""
    try:
        items = db.execute_query(ITEMS_SOLUTION, params=args)
        return items
    except Exception as e:
        print(f"Erro ao tentar buscar os itens da solução: {e}")
        return []
    
def get_items_fourmaqconnect(db, *args, **kwargs):
    """Responsável por buscar os itens da FourmaqConnect."""
    try:
        items = db.execute_query(ITEMS_FOURMAQCONNECT, params=args)
        return items
    except Exception as e:
        print(f"Erro ao tentar buscar os itens da FourmaqConnect: {e}")
        return []
    
def origin_diverget(db, access_key):
    """Responsável por verificar a divergência de origem."""
    items_fourmaqconnect = get_items_fourmaqconnect(db, access_key)
    
    db_solution = connect_to_database_solution()
    divergent = []
    for item in items_fourmaqconnect:
        code = item[0]
        origin = item[1]
        items_solution = get_items_solution(db_solution, code)

        if not items_solution:
            continue
        
        if origin != items_solution[0][1]:
            divergent.append(
                {
                    'codigo_produto': code,
                    'origem': origin,
                }
            )

    return divergent