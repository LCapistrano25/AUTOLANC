class ItemFourmaqConnect:
    def __init__(self, code, origin):
        self.code = str(code)
        self.origin = str(origin)

    def __repr__(self):
        return f"<ItemFourmaqConnect code={self.code} origin={self.origin}>"
