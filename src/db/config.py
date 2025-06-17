"""
Configurações do banco de dados MySQL.

Este módulo contém as configurações de conexão com o banco de dados MySQL
usando MySQL Connector/Python em modo puro Python.
"""

# Configurações do banco de dados
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',         # Usuário do MySQL
    'password': 'Beer1234@', # Senha do MySQL
    'database': 'pdv_bar',  # Nome do banco de dados
    'port': 3306,           # Porta padrão do MySQL
    'raise_on_warnings': True,
    'use_pure': True,      # Força o uso da implementação pura em Python
    'autocommit': True,    # Habilita autocommit por padrão
    'charset': 'utf8mb4',  # Suporte a caracteres especiais e emojis
    'collation': 'utf8mb4_unicode_ci',  # Collation para suporte a caracteres especiais
    'connection_timeout': 30  # Timeout de conexão em segundos
}

# Configurações adicionais para desenvolvimento
DEV_CONFIG = {
    **DB_CONFIG,
    'host': '127.0.0.1',
    'connect_timeout': 30
}

# Configurações para produção (substitua com suas credenciais reais)
PROD_CONFIG = {
    **DB_CONFIG,
    'host': 'seu-servidor-producao',
    'user': 'usuario_producao',
    'password': 'senha_segura',
    'pool_size': 10
}

def get_db_config(environment='development'):
    """Retorna as configurações do banco de dados com base no ambiente.
    
    Args:
        environment (str): Ambiente de execução ('development' ou 'production')
        
    Returns:
        dict: Configurações de conexão com o banco de dados
    """
    if environment.lower() == 'production':
        return PROD_CONFIG
    return DEV_CONFIG
