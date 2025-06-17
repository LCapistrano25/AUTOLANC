from database.consults.items_solution import ITEMS_SOLUTION
from database.models.item_solution import ItemSolution

class ItemSolutionRepository:
    def __init__(self, connection):
        self.db = connection

    def get_item_solution(self, code_product):
        cursor = self.db.get_cursor()
        cursor.execute(ITEMS_SOLUTION, (code_product,))
        row = cursor.fetchone()
        return ItemSolution(*row) if row else None