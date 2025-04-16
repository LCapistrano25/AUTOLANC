class StatusParameters:
    def __init__(self, nao_lancado, em_lancamento, lancado, a_conferir):
        self.nao_lancado = nao_lancado
        self.em_lancamento = em_lancamento
        self.lancado = lancado
        self.a_conferir = a_conferir

    def __repr__(self):
        return f"<StatusParameters NL={self.nao_lancado} EL={self.em_lancamento} L={self.lancado}>"
