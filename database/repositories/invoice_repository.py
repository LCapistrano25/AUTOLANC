
from database.consults.invoices import INVOICES, UPDATE_INVOICE, UPDATE_INVOICE_ERROR
from database.models.invoice import Invoice

class InvoiceRepository:
    def __init__(self, connection):
        self.db = connection

    def get_invoices(self, lauch_status, limit):
        cursor = self.db.get_cursor()
        cursor.execute(INVOICES, (lauch_status, limit))
        rows = cursor.fetchall()
        return [Invoice(*row) for row in rows]
    
    def update_invoice_status(self, status, key):
        try:
            cursor = self.db.get_cursor()
            try:
                cursor.execute(UPDATE_INVOICE, (status, key))
                self.db.commit()
                return True
            except Exception as e:
                return False
        except Exception as e:
            print(f"Erro ao tentar atualizar a nota fiscal: {e}")
            return False

    def update_invoice_attempts(self, key):
        cursor = self.db.get_cursor()
        try:
            cursor.execute(UPDATE_INVOICE_ERROR, (key,))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erro ao tentar atualizar a nota fiscal com erro: {e}")
            return False