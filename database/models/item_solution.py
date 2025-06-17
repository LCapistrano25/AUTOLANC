class ItemSolution:
    def __init__(self, product_code, origin):
        self.product_code = str(product_code)
        self.origin = str(origin)

    def __repr__(self):
        return f"<ItemSolution code={self.product_code.strip()} origin={self.origin}>"
