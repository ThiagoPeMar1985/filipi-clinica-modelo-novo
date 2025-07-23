"""
Controller para gerenciamento de impressoras - Versão padronizada
"""

class ImpressaoController:
    """
    Controller para operações de impressão seguindo padrão do sistema.
    """
    
    # Mapeamento ID->Nome igual ao usado em produtos_impressoes.py
    MAPEAMENTO_IMPRESSORAS = {
        1: "01 - CAIXA (CUPOM FISCAL)",
        2: "02 - BAR",
        3: "03 - COZINHA",
        4: "04 - AREA 1",
        5: "05 - AREA 2"
    }

    def __init__(self, db):
        """Inicializa com conexão ao banco de dados."""
        self.db = db
    
    def obter_impressora_por_produto(self, produto_id):
        """
        Obtém impressora correta para um produto seguindo padrão do sistema.
        
        Args:
            produto_id: ID do produto
            
        Returns:
            str: Nome da impressora conforme MAPEAMENTO_IMPRESSORAS
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # 1. Obter tipo do produto (igual ao padrão existente)
            cursor.execute("SELECT tipo FROM produtos WHERE id = %s", (produto_id,))
            produto = cursor.fetchone()
            
            if not produto:
                return self.MAPEAMENTO_IMPRESSORAS[1]  # Cupom fiscal como padrão
            
            # 2. Buscar impressora para o tipo (igual ao padrão existente)
            cursor.execute("""
                SELECT impressora_id 
                FROM impressoras_tipos 
                WHERE tipo_id = (SELECT id FROM tipos_produtos WHERE nome = %s LIMIT 1)
            """, (produto['tipo'],))
            
            impressora = cursor.fetchone()
            
            # 3. Retornar nome da impressora ou cupom fiscal como padrão
            return self.MAPEAMENTO_IMPRESSORAS.get(
                impressora['impressora_id'] if impressora else 1,
                self.MAPEAMENTO_IMPRESSORAS[1]
            )
            
        except Exception as e:
            print(f"[ERRO] Falha ao obter impressora: {e}")
            return self.MAPEAMENTO_IMPRESSORAS[1]
        finally:
            if cursor:
                cursor.close()
