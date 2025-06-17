"""
Módulo para operações de banco de dados do módulo de Delivery.
"""
from typing import Dict, List, Any, Optional

class DeliveryDB:
    """Classe para operações de banco de dados do módulo de Delivery."""
    
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
