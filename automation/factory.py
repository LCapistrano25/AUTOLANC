from automation.routines.purchase_resale import PurchaseResaleAutomation
from automation.routines.transfer_notes import TransferNotesAutomation

class AutomationFactory:
    @staticmethod
    def create_automation(automation_type, *args, **kwargs):
        if automation_type == "product_notes":
            return PurchaseResaleAutomation(*args, **kwargs)
        elif automation_type == "transfer_notes":
            return TransferNotesAutomation(*args, **kwargs)
        else:
            raise ValueError(f"Tipo de automação desconhecido: {automation_type}")
