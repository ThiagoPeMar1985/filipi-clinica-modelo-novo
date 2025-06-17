"""
Controlador para o módulo de Mesas.
"""

class MesasController:
    """Controlador para operações do módulo de Mesas."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Aqui você pode inicializar o DB específico do módulo
        # from src.db.mesas_db import MesasDB
        # self.db = MesasDB(obter_conexao())
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
