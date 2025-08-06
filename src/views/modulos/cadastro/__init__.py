from .cadastro_module import CadastroModule

def get_module():
    return {
        "id": "cadastro",
        "nome": "CADASTRO",
        "icone": "📋",
        "opcoes": [
            {"nome": "Empresa", "acao": "empresa"},
            {"nome": "Usuários", "acao": "usuarios"},
            {"nome": "Medicos", "acao": "medicos"},
            {"nome": "clientes", "acao": "clientes"}
        ]
    }
