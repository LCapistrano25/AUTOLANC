from database.consults.items import ITEMS_FOURMAQCONNECT
from database.models.item_fourmaq import ItemFourmaqConnect

class ItemFourmaqRepository:
    def __init__(self, connection):
        self.db = connection

    def get_item_fourmaq(self, access_key):
        cursor = self.db.get_cursor()
        cursor.execute(ITEMS_FOURMAQCONNECT, (access_key,))
        rows = cursor.fetchall()
        return [ItemFourmaqConnect(*row) for row in rows]