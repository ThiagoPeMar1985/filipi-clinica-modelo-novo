"""
Módulo para operações de banco de dados do módulo Financeiro.
"""
from typing import Dict, List, Any, Optional
import mysql.connector
from datetime import datetime

class FinanceiroDB:
    """Classe para operações de banco de dados do módulo Financeiro."""
    
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
        
    def registrar_entrada(self, valor, descricao, tipo_entrada, usuario_id=None, usuario_nome=None, pedido_id=None, garcom_id=None, garcom_nome=None):
        """
        Registra um pagamento no sistema.
        
        Args:
            valor: Valor do pagamento
            descricao: Descrição do pagamento
            tipo_entrada: Forma de pagamento (ex: 'dinheiro', 'cartao', 'pix')
            usuario_id: ID do usuário que registrou o pagamento
            usuario_nome: Nome do usuário que registrou o pagamento
            pedido_id: ID do pedido relacionado
            garcom_id: ID do garçom (opcional)
            garcom_nome: Nome do garçom (opcional)
            
        Returns:
            int: ID do pagamento registrado ou 0 em caso de erro
        """
        # Iniciando registro de pagamento
        
        if not pedido_id:
            print("[ERRO] ID do pedido não informado")
            return 0
            
        try:
            cursor = self.db.cursor()
            
            # Preparar dados para inserção
            dados = {
                'pedido_id': pedido_id,
                'forma_pagamento': tipo_entrada,
                'valor': valor,
                'data_hora': datetime.now()
            }
            
            # Construir a query dinamicamente baseada nas chaves fornecidas
            colunas = ", ".join(dados.keys())
            placeholders = ", ".join(["%s"] * len(dados))
            
            query = f"""
                INSERT INTO pagamentos ({colunas})
                VALUES ({placeholders})
            """
            
            # Executar a query
            cursor.execute(query, list(dados.values()))
            
            # Obter o ID do pagamento inserido
            pagamento_id = cursor.lastrowid
            self.db.commit()
            return pagamento_id
                
        except mysql.connector.Error as err:
            print(f"[ERRO] Erro ao registrar pagamento: {err}")
            print(f"[ERRO] SQL State: {err.sqlstate}")
            print(f"[ERRO] Código de erro: {err.errno}")
            print(f"[ERRO] Mensagem: {err.msg}")
            if 'cursor' in locals() and self.db:
                self.db.rollback()
            return 0
                
        except Exception as e:
            print(f"[ERRO CRÍTICO] Erro inesperado ao registrar pagamento: {str(e)}")
            import traceback
            traceback.print_exc()
            if 'cursor' in locals() and self.db:
                self.db.rollback()
            return 0
            
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
                pass
