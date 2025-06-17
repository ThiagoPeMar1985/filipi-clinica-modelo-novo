"""
Controlador para o módulo de Delivery.
"""

class DeliveryController:
    """Controlador para operações do módulo de Delivery."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Aqui você pode inicializar o DB específico do módulo
        # from src.db.delivery_db import DeliveryDB
        # self.db = DeliveryDB(obter_conexao())
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
