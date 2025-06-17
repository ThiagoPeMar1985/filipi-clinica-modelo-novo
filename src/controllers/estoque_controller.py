"""
Controlador para o módulo de Estoque.
"""

class EstoqueController:
    """Controlador para operações do módulo de Estoque."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Aqui você pode inicializar o DB específico do módulo
        # from src.db.estoque_db import EstoqueDB
        # self.db = EstoqueDB(obter_conexao())
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
