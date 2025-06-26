from abc import ABC, abstractmethod

from playwright.sync_api import Page
from complements.log import AbstractLogger
from complements.toolbox import AbstractToolbox

class Context(ABC):
    def __init__(self, toolbox: AbstractToolbox, logger: AbstractLogger, db, data, parameters, dir_logs=None):
        """Initialize the automation context."""
        self.page = None
        self.toolbox = toolbox
        self.logger = logger
        self.data = data
        self.db = db
        self.parameters = parameters
        self.dir_logs = dir_logs

    @abstractmethod
    def set_page(self, page: Page):
        """Set the page for the automation context."""
        self.page = page

    @abstractmethod
    def get_toolbox(self) -> AbstractToolbox:
        """Get the toolbox for the automation context."""
        return self.toolbox
    
    @abstractmethod
    def get_logger(self) -> AbstractLogger:
        """Get the logger for the automation context."""
        return self.logger
    
    @abstractmethod
    def get_page(self) -> Page:
        """Get the page for the automation context."""
        return self.page
    
    @abstractmethod
    def get_data(self):
        """Get the data for the automation context."""
        return self.data
    
    @abstractmethod
    def get_db(self):
        """Get the database connection for the automation context."""
        return self.db
    
    @abstractmethod
    def get_parameters(self):
        """Get the parameters for the automation context."""
        return self.parameters
    
    @abstractmethod
    def get_dir_logs(self):
        """Get the directory for logs."""
        return self.dir_logs if self.dir_logs else "logs"
    

class AutomationContext(Context):
    def __init__(self, toolbox: AbstractToolbox, logger: AbstractLogger, db, data, parameters, dir_logs=None):
        """Initialize the automation context."""
        super().__init__(toolbox, logger, db, data, parameters, dir_logs)

    def set_page(self, page: Page):
        """Set the page for the automation context."""
        super().set_page(page)

    def get_toolbox(self) -> AbstractToolbox:
        """Get the toolbox for the automation context."""
        return super().get_toolbox()
    
    def get_logger(self) -> AbstractLogger:
        """Get the logger for the automation context."""
        return super().get_logger()
    
    def get_page(self) -> Page:
        """Get the page for the automation context."""
        return super().get_page()
    
    def get_data(self):
        """Get the data for the automation context."""
        return super().get_data()
    
    def get_db(self):
        """Get the database connection for the automation context."""
        return super().get_db()
    
    def get_parameters(self):
        """Get the parameters for the automation context."""
        return super().get_parameters()
    
    def get_dir_logs(self):
        """Get the directory for logs."""
        return super().get_dir_logs()