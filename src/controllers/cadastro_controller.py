"""
Controlador para o módulo de Cadastro.
"""

class CadastroController:
    """Controlador para operações do módulo de Cadastro."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Aqui você pode inicializar o DB específico do módulo
        # from src.db.cadastro_db import CadastroDB
        # self.db = CadastroDB(obter_conexao())
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
        
    def listar_produtos(self):
        """Lista todos os produtos cadastrados."""
        from src.db.cadastro_db import CadastroDB
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            db = CadastroDB(connection)
            return db.listar_produtos()
        except Exception as e:
            raise Exception(f"Erro ao listar produtos: {str(e)}")
            
    def obter_produto(self, produto_id):
        """Obtém um produto pelo ID."""
        from src.db.cadastro_db import CadastroDB
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            db = CadastroDB(connection)
            return db.obter_produto(produto_id)
        except Exception as e:
            print(f"Erro ao obter produto: {str(e)}")
            return None
