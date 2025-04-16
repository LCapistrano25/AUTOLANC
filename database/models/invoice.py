class Invoice:
    def __init__(self, chave, numero_filial, nome_filial, operacao, conferente,
                 vendedor, centro, politica, tipo_lancamento, numero_nota):
        self.chave = chave
        self.numero_filial = numero_filial
        self.nome_filial = nome_filial
        self.operacao = operacao
        self.conferente = conferente
        self.vendedor = vendedor
        self.centro = centro
        self.politica = politica
        self.tipo_lancamento = tipo_lancamento
        self.numero_nota = numero_nota

    def __repr__(self):
        return f"<Invoice chave={self.chave} nota={self.numero_nota}>"
