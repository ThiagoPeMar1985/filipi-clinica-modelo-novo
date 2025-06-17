from .cadastro_module import CadastroModule

def get_module():
    return {
        "id": "cadastro",
        "nome": "CADASTRO",
        "icone": "📋",
        "opcoes": [
            {"nome": "Empresa", "acao": "empresa"},
            {"nome": "Usuários", "acao": "usuarios"},
            {"nome": "Funcionários", "acao": "funcionarios"},
            {"nome": "Clientes", "acao": "clientes"},
            {"nome": "Produtos", "acao": "produtos"},
            {"nome": "Fornecedores", "acao": "fornecedores"}
        ]
    }
