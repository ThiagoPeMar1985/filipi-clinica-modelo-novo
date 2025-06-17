"""
Controlador para o módulo Financeiro.
"""

class FinanceiroController:
    """Controlador para operações do módulo Financeiro."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Aqui você pode inicializar o DB específico do módulo
        # from src.db.financeiro_db import FinanceiroDB
        # self.db = FinanceiroDB(obter_conexao())
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
