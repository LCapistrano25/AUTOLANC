import logging
import os
from rich.logging import RichHandler

class Logger:
    _loggers = {} 

    def __init__(self, name, log_file=None, invoice_id=None):
        """Cria um logger separado para cada processo"""
        if name in Logger._loggers:
            self.logger = Logger._loggers[name]
            return

        formatter = logging.Formatter(f'%(asctime)s - [NF-{invoice_id}] - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        console_handler = RichHandler(show_time=False, show_level=True, rich_tracebacks=True)
        if not self.logger.handlers: 
            self.logger.addHandler(console_handler)
            self.logger.propagate = False
        console_handler.setFormatter(formatter)

        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Cria a pasta de logs se não existir
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Armazena o logger para reutilização
        Logger._loggers[name] = self.logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
