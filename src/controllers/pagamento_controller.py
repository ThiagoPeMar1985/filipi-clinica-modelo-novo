"""
Controlador para o módulo de pagamentos.
"""
class PagamentoController:
    def __init__(self, db_connection=None):
        """Inicializa o controlador de pagamentos."""
        self.db_connection = db_connection
        
    def listar_formas_pagamento(self):
        """Lista todas as formas de pagamento disponíveis."""
        if not self.db_connection:
            return []
        
        cursor = self.db_connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nome, descricao, taxa 
            FROM formas_pagamento 
            WHERE ativo = TRUE 
            ORDER BY nome
        """)
        return cursor.fetchall()
        
    def registrar_pagamento(self, pedido_id, forma_pagamento, valor, observacao=None):
        """Registra um pagamento para um pedido."""
        if not self.db_connection:
            return False
            
        cursor = self.db_connection.cursor()
        cursor.execute("""
            INSERT INTO pagamentos (
                pedido_id, forma_pagamento_id, valor, observacao
            )
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, forma_pagamento, valor, observacao))
        
        pagamento_id = cursor.lastrowid
        self.db_connection.commit()
        return pagamento_id
        
    def registrar_venda(self, dados_venda, itens, pagamentos):
        """Registra uma venda completa com seus itens e pagamentos."""
        return False  # Esta função não é mais utilizada
        
    def vincular_conta_cliente(self, pedido_id, cliente_id, valor):
        """Vincula um pedido à conta de um cliente (pendura)."""
        if not self.db_connection:
            return False
            
        cursor = self.db_connection.cursor()
        cursor.execute("""
            INSERT INTO contas_clientes (
                cliente_id, pedido_id, valor, status
            )
            VALUES (%s, %s, %s, %s)
        """, (cliente_id, pedido_id, valor, 'pendente'))
        
        conta_id = cursor.lastrowid
        self.db_connection.commit()
        return conta_id
