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
        try:
            self.ensure_schema()
        except Exception:
            # Evita travar inicialização caso não tenha permissão para DDL
            pass

    def ensure_schema(self):
        """Cria as tabelas de caixa se não existirem."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS caixa_sessoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    abertura_datahora DATETIME NOT NULL,
                    abertura_valor_inicial DECIMAL(10,2) NOT NULL DEFAULT 0,
                    abertura_usuario_id INT NULL,
                    fechamento_datahora DATETIME NULL,
                    fechamento_usuario_id INT NULL,
                    observacao VARCHAR(255) NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS caixa_movimentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sessao_id INT NOT NULL,
                    tipo ENUM('recebimento','pagamento') NOT NULL,
                    forma ENUM('dinheiro','cartao','pix','outro') NOT NULL DEFAULT 'dinheiro',
                    valor DECIMAL(10,2) NOT NULL,
                    descricao VARCHAR(255) NULL,
                    data_hora DATETIME NOT NULL,
                    usuario_id INT NULL,
                    CONSTRAINT fk_caixa_mov_sessao FOREIGN KEY (sessao_id) REFERENCES caixa_sessoes(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            self.db.commit()
        finally:
            cursor.close()

    def get_caixa_aberto(self) -> dict | None:
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT * FROM caixa_sessoes
                WHERE fechamento_datahora IS NULL
                ORDER BY abertura_datahora DESC
                LIMIT 1
                """
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def abrir_caixa(self, valor_inicial: float, usuario_id: int | None = None, observacao: str | None = None) -> int:
        """Abre uma nova sessão de caixa se não houver uma aberta. Retorna id da sessão."""
        existente = self.get_caixa_aberto()
        if existente:
            return existente['id']
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO caixa_sessoes (abertura_datahora, abertura_valor_inicial, abertura_usuario_id, observacao)
                VALUES (%s, %s, %s, %s)
                """,
                (datetime.now(), float(valor_inicial or 0), usuario_id, observacao)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def registrar_movimento(self, sessao_id: int, tipo: str, forma: str, valor: float, descricao: str | None, usuario_id: int | None) -> int:
        """Registra um movimento (recebimento/pagamento) na sessão."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO caixa_movimentos (sessao_id, tipo, forma, valor, descricao, data_hora, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (sessao_id, tipo, forma, float(valor or 0), descricao, datetime.now(), usuario_id)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def listar_movimentos(self, sessao_id: int) -> list[dict]:
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, tipo, forma, valor, descricao, data_hora, usuario_id
                FROM caixa_movimentos
                WHERE sessao_id = %s
                ORDER BY data_hora ASC, id ASC
                """,
                (sessao_id,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def fechar_caixa(self, sessao_id: int, usuario_id: int | None = None):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                UPDATE caixa_sessoes
                SET fechamento_datahora = %s, fechamento_usuario_id = %s
                WHERE id = %s AND fechamento_datahora IS NULL
                """,
                (datetime.now(), usuario_id, sessao_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def resumo_sessao(self, sessao_id: int) -> dict:
        """Calcula totais de entradas/saídas por forma e saldo."""
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT abertura_valor_inicial FROM caixa_sessoes WHERE id=%s", (sessao_id,))
            row = cursor.fetchone()
            valor_inicial = float(row['abertura_valor_inicial'] if row and row.get('abertura_valor_inicial') is not None else 0)

            cursor.execute(
                """
                SELECT tipo, forma, SUM(valor) AS total
                FROM caixa_movimentos
                WHERE sessao_id = %s
                GROUP BY tipo, forma
                """,
                (sessao_id,)
            )
            linhas = cursor.fetchall() or []
            entradas = {}
            saidas = {}
            total_entradas = 0.0
            total_saidas = 0.0
            for r in linhas:
                total = float(r['total'] or 0)
                if r['tipo'] == 'recebimento':
                    entradas[r['forma']] = entradas.get(r['forma'], 0.0) + total
                    total_entradas += total
                else:
                    saidas[r['forma']] = saidas.get(r['forma'], 0.0) + total
                    total_saidas += total
            saldo_final = valor_inicial + total_entradas - total_saidas
            return {
                'valor_inicial': valor_inicial,
                'entradas_por_forma': entradas,
                'saidas_por_forma': saidas,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_final': saldo_final,
            }
        finally:
            cursor.close()
        
    def registrar_entrada(self, valor, descricao, tipo_entrada, usuario_id=None, usuario_nome=None, pedido_id=None):
        """
        Registra um pagamento no sistema.
        
        Args:
            valor: Valor do pagamento
            descricao: Descrição do pagamento
            tipo_entrada: Forma de pagamento (ex: 'dinheiro', 'cartao', 'pix')
            usuario_id: ID do usuário que registrou o pagamento
            usuario_nome: Nome do usuário que registrou o pagamento
            pedido_id: ID do pedido relacionado
            
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
