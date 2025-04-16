class ItemFourmaqConnect:
    def __init__(self, codigo, origem):
        self.codigo = codigo
        self.origem = origem

    def __repr__(self):
        return f"<ItemFourmaqConnect codigo={self.codigo} origem={self.origem}>"
