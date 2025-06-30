"""
Controlador para o módulo de pagamentos.
"""
from db.pagamento_db import PagamentoDB

class PagamentoController:
    def __init__(self, db_connection=None):
        """Inicializa o controlador de pagamentos."""
        self.db = PagamentoDB(db_connection) if db_connection else None
        
    def listar_formas_pagamento(self):
        """Lista todas as formas de pagamento disponíveis."""
        if not self.db:
            return []
        return self.db.listar_formas_pagamento()
        
    def registrar_pagamento(self, venda_id, forma_pagamento, valor, observacao=None):
        """Registra um pagamento para uma venda."""
        if not self.db:
            return False
        return self.db.registrar_pagamento(venda_id, forma_pagamento, valor, observacao)
        
    def registrar_venda(self, dados_venda, itens, pagamentos):
        """Registra uma venda completa com seus itens e pagamentos."""
        if not self.db:
            return False
        return self.db.registrar_venda(dados_venda, itens, pagamentos)
        
    def vincular_conta_cliente(self, venda_id, cliente_id, valor):
        """Vincula uma venda à conta de um cliente (pendura)."""
        if not self.db:
            return False
        return self.db.vincular_conta_cliente(venda_id, cliente_id, valor)
