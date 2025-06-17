import sqlite3
import psycopg2
import mysql.connector

class DatabaseConnection:
    def __init__(self, db_type: str, db_name: str, user: str=None, password: str=None, host: str="localhost", port: str=None):
        self.db_type = db_type.lower()
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self._conn = None
        self._cursor = None

    def connect(self) -> None:
        """Estabelece conexão com o banco de dados."""
        try:
            if self.db_type == "sqlite":
                self._conn = sqlite3.connect(self.db_name)
            elif self.db_type == "postgresql":
                self._conn = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port or "5432"
                )
            elif self.db_type == "mysql":
                self._conn = mysql.connector.connect(
                    database=self.db_name,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port or "3306"
                )
            else:
                raise ValueError("Banco de dados não suportado!")

            self._cursor = self._conn.cursor()
            print(f"Conectado ao banco de dados {self.db_name} ({self.db_type})")

        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")

    def execute_query(self, query, params=None) -> any:
        """Executa uma consulta SQL e retorna os resultados, se houver."""
        try:
            self._cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                return self._cursor.fetchall()
            else:
                self._conn.commit()
                return "Query executada com sucesso!"
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            return None

    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            print("Conexão fechada.")

    def get_cursor(self):
        if self._conn:
            return self._conn.cursor()
        raise RuntimeError("Conexão não iniciada.")
    
    def commit(self):
        if self._conn:
            self._conn.commit()
        else:
            raise RuntimeError("Conexão não inicializada.")