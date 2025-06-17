from .configuracao_module import ConfiguracaoModule

def get_module():
    return {
        "id": "configuracao",
        "nome": "CONFIGURAÇÃO",
        "icone": "⚙️",
        "opcoes": [
            {"nome": "Programa", "acao": "programa"},
            {"nome": "Impressoras", "acao": "impressoras"},
            {"nome": "Banco de Dados", "acao": "banco_dados"},
            {"nome": "PDV", "acao": "pdv"},
            {"nome": "Segurança", "acao": "seguranca"},
            {"nome": "Integrações", "acao": "integracoes"},
            {"nome": "Redes", "acao": "redes"},
            {"nome": "Backup", "acao": "backup"},
            {"nome": "Sistema", "acao": "sistema"}
        ]
    }