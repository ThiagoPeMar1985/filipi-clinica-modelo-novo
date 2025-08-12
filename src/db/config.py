"""
Configurações do banco de dados MySQL.

Este módulo contém as configurações de conexão com o banco de dados MySQL
usando MySQL Connector/Python em modo puro Python.
"""
from pathlib import Path
import json
import os

# Configurações do banco de dados
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Beer1234@',
    'database': 'clinica_filipi',
    'port': 3306,
    'raise_on_warnings': True,
    'use_pure': True,
    'autocommit': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'connection_timeout': 30
}

# Configurações adicionais para desenvolvimento
DEV_CONFIG = {
    **DB_CONFIG,
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

def _load_user_json_config():
    """Carrega o JSON de configuração do usuário se existir.
    Retorna um dicionário com possíveis chaves: host, port/porta, user/usuario, password/senha, database/nome_bd
    """
    try:
        # Prioriza nova pasta de configs (~/.clinicas), mantendo compatibilidade com a antiga (~/.pdv_aquarius)
        new_dir = Path.home() / '.clinicas'
        new_file = new_dir / 'config.json'
        cfg_file = new_file if new_file.exists() else new_file
        if not cfg_file.exists():
            return {}
        with open(cfg_file, 'r', encoding='utf-8') as f:
            data = json.load(f) or {}
        bd = data.get('banco_dados') or data  # compat: pode estar na raiz
        # normaliza chaves
        host = bd.get('host')
        port = bd.get('port') if 'port' in bd else bd.get('porta')
        user = bd.get('user') if 'user' in bd else bd.get('usuario')
        password = bd.get('password') if 'password' in bd else bd.get('senha')
        database = bd.get('database') if 'database' in bd else bd.get('nome_bd')
        out = {}
        if host:
            out['host'] = host
        if port:
            try:
                out['port'] = int(port)
            except Exception:
                pass
        if user:
            out['user'] = user
        if password is not None:
            out['password'] = password
        if database:
            out['database'] = database
        return out
    except Exception:
        return {}


def is_server_machine():
    return os.environ.get('IS_SERVER') == 'True'


def get_db_config(environment: str | None = None):
    """Retorna as configurações do banco de dados.

    Prioriza configurações salvas pelo usuário em ~/.clinicas/config.json.
    Se `environment` for 'production', retorna PROD_CONFIG. Caso contrário, retorna
    DEV_CONFIG mesclado com o JSON do usuário (se existir).
    Também respeita a variável de ambiente APP_ENV quando `environment` não é informado.
    """
    env = (environment or os.environ.get('APP_ENV') or '').lower()
    if env == 'production':
        return PROD_CONFIG

    # Ambiente de desenvolvimento/auto: aplica JSON do usuário sobre DEV_CONFIG
    cfg = {**DEV_CONFIG}
    user_overrides = _load_user_json_config()
    
    # Se o usuário já configurou o host, respeitamos essa configuração
    if 'host' in user_overrides:
        cfg.update(user_overrides)
    else:
        # Se não há configuração de host pelo usuário, usamos a detecção automática
        cfg.update(user_overrides)  # Atualiza outras configurações primeiro
        
        # Detecta automaticamente se é o servidor ou cliente
        if is_server_machine():
            cfg['host'] = '127.0.0.1'  # Host para servidor local
        else:
            # Para clientes, não definimos host padrão para forçar configuração
            if 'host' in cfg:
                del cfg['host']
    
    return cfg
