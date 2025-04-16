class ItemSolution:
    def __init__(self, codigo_produto, origem):
        self.codigo_produto = codigo_produto
        self.origem = origem

    def __repr__(self):
        return f"<ItemSolution codigo={self.codigo_produto} origem={self.origem}>"
