class Invoice:
    def __init__(self, key, branch_number, branch_name, operation, checker,
                 seller, center, policy, entry_type, invoice_number, products=None):
        self.key = str(key)
        self.branch_number = str(branch_number)
        self.branch_name = str(branch_name)
        self.operation = str(operation)
        self.checker = str(checker)
        self.seller = str(seller)
        self.center = str(center)
        self.policy = str(policy)
        self.entry_type = str(entry_type)
        self.invoice_number = str(invoice_number)
        self.products = products if products else []

    def set_products(self, products):
        """Seta os produtos da nota fiscal."""
        self.products = products
        
    def __repr__(self):
        return f"<Invoice key={self.key} invoice={self.invoice_number}>"
