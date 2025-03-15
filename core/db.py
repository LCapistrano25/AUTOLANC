import sqlite3
import psycopg2
import mysql.connector

class DatabaseConnection:
    def __init__(self, db_type, db_name, user=None, password=None, host="localhost", port=None):
        self.db_type = db_type.lower()
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None
        self.cursor = None

    def connect(self):
        """Estabelece conexão com o banco de dados."""
        try:
            if self.db_type == "sqlite":
                self.conn = sqlite3.connect(self.db_name)
            elif self.db_type == "postgresql":
                self.conn = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port or "5432"
                )
            elif self.db_type == "mysql":
                self.conn = mysql.connector.connect(
                    database=self.db_name,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port or "3306"
                )
            else:
                raise ValueError("Banco de dados não suportado!")

            self.cursor = self.conn.cursor()
            print(f"Conectado ao banco de dados {self.db_name} ({self.db_type})")

        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")

    def execute_query(self, query, params=None):
        """Executa uma consulta SQL e retorna os resultados, se houver."""
        try:
            self.cursor.execute(query, params or ())
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return "Query executada com sucesso!"
        except Exception as e:
            print(f"Erro ao executar a query: {e}")
            return None

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Conexão fechada.")