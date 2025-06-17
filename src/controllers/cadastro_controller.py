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
