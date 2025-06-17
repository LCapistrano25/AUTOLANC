from database.consults.parameters import PARAMETERS
from database.models.parameters import StatusParameters

class ParametersRepository:
    def __init__(self, connection):
        self.db = connection

    def get_parameters(self):
        cursor = self.db.get_cursor()
        cursor.execute(PARAMETERS)
        row = cursor.fetchone()
        return StatusParameters(*row)
    