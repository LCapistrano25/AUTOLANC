from database.consults.parameters import PARAMETERS
from models.parameters import StatusParameters

class ParametersRepository:
    def __init__(self, connection):
        self.conn = connection

    def get_parameters(self):
        cursor = self.conn.cursor
        cursor.execute(PARAMETERS)
        row = cursor.fetchone()
        return StatusParameters(*row)

    def to_dict(self, parameters):
        return {
            'nao_lancado': parameters.nao_lancado,
            'em_lancamento': parameters.em_lancamento,
            'lancado': parameters.lancado,
            'a_conferir': parameters.a_conferir
        }
    