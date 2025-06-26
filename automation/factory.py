from automation.routines.purchase_resale import PurchaseResaleAutomation
from automation.routines.transfer_notes import TransferNotesAutomation
from automation.context import AutomationContext
from complements.toolbox import Toolbox
from complements.log import Logger
class AutomationFactory:
    @staticmethod
    def create_automation(automation_type, *args, **kwargs):
        if automation_type == "product_notes":
            return AutomationFactory._create_product_notes_automation(kwargs)
        elif automation_type == "transfer_notes":
            return TransferNotesAutomation(*args, **kwargs)
        else:
            raise ValueError(f"Tipo de automação desconhecido: {automation_type}")

    @staticmethod
    def _create_product_notes_automation(kwargs):
        required = ("url", "username", "password", "data", "parameters", "db")
        for param in required:
            if not kwargs.get(param):
                raise ValueError(f"Parâmetro obrigatório ausente: {param}")

        data = kwargs["data"]
        key = data.key
        if not key:
            raise ValueError("Chave da nota (key) ausente em data")

        dir_logs = kwargs.get("dir_logs", "logs")

        logger = Logger(
            name=key,
            log_file=f"{dir_logs}/{key}/{key}.log",
            invoice_id=key
        )
        toolbox = Toolbox()

        context = AutomationContext(
            toolbox=toolbox,
            logger=logger,
            db=kwargs["db"],
            data=data,
            parameters=kwargs["parameters"],
            dir_logs=dir_logs
        )

        return PurchaseResaleAutomation(
            url=kwargs["url"],
            username=kwargs["username"],
            password=kwargs["password"],
            context=context
        )
