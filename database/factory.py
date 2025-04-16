
class FactoryDatabaseConnection:
    @staticmethod
    def select_connection(db_name):
        """Responsável por selecionar a conexão com o banco de dados."""
        if db_name == "fourmaqconnect":
            return connect_to_database_fourmaqconnect()
        elif db_name == "solution":
            return connect_to_database_solution()
        else:
            raise ValueError("Banco de dados não suportado!")
    