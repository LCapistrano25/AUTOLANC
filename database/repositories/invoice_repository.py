
from database.consults.invoices import INVOICES, UPDATE_INVOICE, UPDATE_INVOICE_ERROR
from database.models.invoice import Invoice

class InvoiceRepository:
    def __init__(self, connection):
        self.conn = connection

    def get_invoices(self, lauch_status, limit):
        cursor = self.conn.cursor
        cursor.execute(INVOICES, (lauch_status, limit))
        rows = cursor.fetchall()
        return [Invoice(*row) for row in rows]

    def update_invoice_status(self, status, key):
        cursor = self.conn.cursor
        cursor.execute(UPDATE_INVOICE, (status, key))
        self.conn.commit()
    
    def update_invoice_error(self, key):
        cursor = self.conn.cursor
        cursor.execute(UPDATE_INVOICE_ERROR, (key,))
        self.conn.commit()
        
    def to_dict(self, invoice):
        return {
            'chave': invoice.chave,
            'numero_filial': invoice.numero_filial,
            'nome_filial': invoice.nome_filial,
            'operacao': invoice.operacao,
            'conferente': invoice.conferente,
            'vendedor': invoice.vendedor,
            'centro': invoice.centro,
            'politica': invoice.politica,
            'tipo_lancamento': invoice.tipo_lancamento,
            'numero_nota': invoice.numero_nota
        }