
from automation.product_automation import ProductNotesAutomation
from automation.service_automation import ServiceNotesAutomation

class AutomationFactory:
    @staticmethod
    def create_automation(automation_type, *args, **kwargs):
        if automation_type == "product_notes":
            return ProductNotesAutomation(*args, **kwargs)
        elif automation_type == "invoice_processing":
            return ServiceNotesAutomation(*args, **kwargs)
        else:
            raise ValueError(f"Tipo de automação desconhecido: {automation_type}")
