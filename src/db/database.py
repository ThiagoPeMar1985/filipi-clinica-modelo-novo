"""
Módulo de conexão com o banco de dados MySQL.

Este módulo fornece uma classe para gerenciar conexões com o banco de dados MySQL
usando MySQL Connector/Python em modo puro Python.
"""
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any, Union, List, Tuple

from .config import get_db_config

class DatabaseConnection:
    """Classe para gerenciar conexões com o banco de dados MySQL."""
    
    _instance = None
    _connection = None
    
    def __new__(cls, environment: str = 'development'):
        """Implementa o padrão Singleton para garantir apenas uma instância da conexão."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._initialize_connection(environment)
        return cls._instance
    
    @classmethod
    def _initialize_connection(cls, environment: str):
        """Inicializa a conexão com o banco de dados."""
        try:
            db_config = get_db_config(environment)
            # Remove configurações específicas do pool
            for key in ['pool_name', 'pool_size', 'pool_reset_session']:
                db_config.pop(key, None)
                
            cls._connection = mysql.connector.connect(
                **db_config
            )
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise
    
    def get_connection(self):
        """Obtém a conexão com o banco de dados."""
        if self._connection is None or not self._connection.is_connected():
            self._reconnect()
        return self._connection
        
    def _reconnect(self):
        """Reconecta ao banco de dados."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            
        db_config = get_db_config()
        # Remove configurações específicas do pool
        for key in ['pool_name', 'pool_size', 'pool_reset_session']:
            db_config.pop(key, None)
            
        self._connection = mysql.connector.connect(
            use_pure=True,
            **db_config
        )
    
    def execute_query(self, query: str, params: Optional[tuple] = None, 
                      fetch_all: bool = True) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        """Executa uma consulta SQL e retorna os resultados.
        
        Args:
            query: Consulta SQL a ser executada
            params: Parâmetros para a consulta (opcional)
            fetch_all: Se True, retorna todos os resultados; caso contrário, retorna apenas o primeiro
            
        Returns:
            Lista de dicionários com os resultados ou um único dicionário se fetch_all=False
        """
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE')):
                result = cursor.fetchall() if fetch_all else cursor.fetchone()
                return result
            else:
                connection.commit()
                return {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}
                
        except Error as e:
            if self._connection and self._connection.is_connected():
                self._connection.rollback()
            print(f"Erro ao executar consulta: {e}")
            print(f"SQL: {query}")
            print(f"Parâmetros: {params}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_many(self, query: str, params_list: List[tuple]) -> Dict[str, Any]:
        """Executa uma consulta SQL várias vezes com diferentes parâmetros.
        
        Args:
            query: Consulta SQL a ser executada
            params_list: Lista de tuplas de parâmetros
            
        Returns:
            Dicionário com informações sobre a execução
        """
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.executemany(query, params_list)
            connection.commit()
            
            return {"rowcount": cursor.rowcount, "lastrowid": cursor.lastrowid}
                
        except Error as e:
            if self._connection and self._connection.is_connected():
                self._connection.rollback()
            print(f"Erro ao executar consulta em lote: {e}")
            print(f"SQL: {query}")
            print(f"Número de parâmetros: {len(params_list) if params_list else 0}")
            if params_list and len(params_list) > 0:
                print(f"Primeiro conjunto de parâmetros: {params_list[0]}")
            raise
        finally:
            if cursor:
                cursor.close()

# Criar uma instância global para uso em todo o sistema
db = DatabaseConnection()

def get_db() -> DatabaseConnection:
    """Retorna a instância do gerenciador de banco de dados."""
    return db
