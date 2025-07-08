"""
Módulo para operações de banco de dados do módulo de Pagamentos.
"""
from typing import Dict, List, Any, Optional
import mysql.connector
import datetime

class PagamentoDB:
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        """Cria as tabelas necessárias para o módulo de pagamentos."""
        try:
            cursor = self.db.cursor()
            
            # Tabela de formas de pagamento
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS formas_pagamento (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                taxa DECIMAL(5,2) DEFAULT 0.00,
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de vendas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo VARCHAR(20) NOT NULL,  -- 'avulsa', 'delivery', 'mesa'
                referencia VARCHAR(50),     -- número da mesa, id do delivery, etc.
                cliente_id INT,
                valor_total DECIMAL(10,2) NOT NULL,
                desconto DECIMAL(10,2) DEFAULT 0.00,
                valor_final DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pendente',  -- 'pendente', 'pago', 'cancelado'
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                observacao TEXT,
                usuario_id INT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de itens da venda
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS venda_itens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venda_id INT NOT NULL,
                produto_id INT NOT NULL,
                quantidade INT NOT NULL,
                preco_unitario DECIMAL(10,2) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                observacao TEXT,
                FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de opções dos itens da venda
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS venda_item_opcoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venda_item_id INT NOT NULL,
                opcao_id INT NOT NULL,
                grupo_id INT NOT NULL,
                preco_adicional DECIMAL(10,2) DEFAULT 0.00,
                FOREIGN KEY (venda_item_id) REFERENCES venda_itens(id) ON DELETE CASCADE,
                FOREIGN KEY (opcao_id) REFERENCES opcoes_itens(id) ON DELETE RESTRICT,
                FOREIGN KEY (grupo_id) REFERENCES opcoes_grupos(id) ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de pagamentos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagamentos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venda_id INT NOT NULL,
                forma_pagamento_id INT NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacao TEXT,
                FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE,
                FOREIGN KEY (forma_pagamento_id) REFERENCES formas_pagamento(id) ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de contas de clientes (pendura)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas_clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT NOT NULL,
                venda_id INT NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                data_lancamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_pagamento TIMESTAMP NULL,
                status VARCHAR(20) DEFAULT 'pendente',  -- 'pendente', 'pago', 'cancelado'
                observacao TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (venda_id) REFERENCES vendas(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Inserir formas de pagamento padrão se não existirem
            cursor.execute("SELECT COUNT(*) FROM formas_pagamento")
            count = cursor.fetchone()[0]
            
            if count == 0:
                formas_pagamento = [
                    ('Dinheiro', 'Pagamento em espécie', 0.00),
                    ('Cartão de Débito', 'Pagamento com cartão de débito', 0.00),
                    ('Cartão de Crédito', 'Pagamento com cartão de crédito', 0.00),
                    ('PIX', 'Pagamento via PIX', 0.00),
                    ('Conta Cliente', 'Vincular à conta do cliente (pendura)', 0.00)
                ]
                
                cursor.executemany("""
                INSERT INTO formas_pagamento (nome, descricao, taxa)
                VALUES (%s, %s, %s)
                """, formas_pagamento)
                
                self.db.commit()
                
        except mysql.connector.Error as err:
            self.db.rollback()
            
        finally:
            cursor.close()
    
    def listar_formas_pagamento(self):
        """Lista todas as formas de pagamento ativas."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, descricao, taxa
                FROM formas_pagamento
                WHERE ativo = TRUE
                ORDER BY nome
            """)
            return cursor.fetchall()
        except mysql.connector.Error:
            return []
        finally:
            cursor.close()
    
    def registrar_pagamento(self, venda_id, forma_pagamento_id, valor, observacao=None):
        """Registra um pagamento para uma venda."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO pagamentos (venda_id, forma_pagamento_id, valor, observacao)
                VALUES (%s, %s, %s, %s)
            """, (venda_id, forma_pagamento_id, valor, observacao))
            
            pagamento_id = cursor.lastrowid
            
            # Atualizar o status da venda se necessário
            cursor.execute("""
                SELECT SUM(valor) as total_pago
                FROM pagamentos
                WHERE venda_id = %s
            """, (venda_id,))
            
            total_pago = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT valor_final
                FROM vendas
                WHERE id = %s
            """, (venda_id,))
            
            valor_final = cursor.fetchone()[0]
            
            # Se o valor pago for igual ou maior que o valor final, marcar como pago
            if total_pago >= valor_final:
                cursor.execute("""
                    UPDATE vendas
                    SET status = 'pago'
                    WHERE id = %s
                """, (venda_id,))
            
            self.db.commit()
            return pagamento_id
            
        except mysql.connector.Error:
            self.db.rollback()
            return 0
        finally:
            cursor.close()
    
    def registrar_venda(self, dados_venda, itens, pagamentos):
        """Registra uma venda completa com seus itens e pagamentos."""
        try:
            cursor = self.db.cursor()
            
            # Inserir a venda
            cursor.execute("""
                INSERT INTO vendas (
                    tipo, referencia, cliente_id, valor_total, 
                    desconto, valor_final, status, observacao, usuario_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados_venda.get('tipo', 'avulsa'),
                dados_venda.get('referencia'),
                dados_venda.get('cliente_id'),
                dados_venda.get('valor_total', 0),
                dados_venda.get('desconto', 0),
                dados_venda.get('valor_final', 0),
                dados_venda.get('status', 'pendente'),
                dados_venda.get('observacao'),
                dados_venda.get('usuario_id')
            ))
            
            venda_id = cursor.lastrowid
            
            # Inserir os itens da venda
            for item in itens:
                cursor.execute("""
                    INSERT INTO venda_itens (
                        venda_id, produto_id, quantidade, 
                        preco_unitario, total, observacao
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    venda_id,
                    item.get('produto_id'),
                    item.get('quantidade', 1),
                    item.get('preco_unitario', 0),
                    item.get('total', 0),
                    item.get('observacao')
                ))
                
                item_id = cursor.lastrowid
                
                # Inserir as opções do item, se houver
                opcoes = item.get('opcoes', [])
                for opcao in opcoes:
                    # Obter o nome da opção em um cursor separado
                    opcao_cursor = self.db.cursor(dictionary=True)
                    try:
                        opcao_cursor.execute("SELECT nome FROM opcoes_itens WHERE id = %s", (opcao.get('opcao_id'),))
                        resultado = opcao_cursor.fetchone()
                        opcao_nome = resultado['nome'] if resultado else "Opção Desconhecida"
                    except Exception as e:
                        print(f"Erro ao obter nome da opção: {e}")
                        opcao_nome = "Opção Desconhecida"
                    finally:
                        opcao_cursor.close()
                    
                    # Inserir a opção do item
                    cursor.execute("""
                        INSERT INTO itens_pedido_opcoes (
                            item_pedido_id, opcao_id, grupo_id, nome, preco_adicional
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        item_id,
                        opcao.get('opcao_id'),
                        opcao.get('grupo_id'),
                        opcao_nome,
                        opcao.get('preco_adicional', 0)
                    ))
                    
                    # Garantir que o resultado foi consumido
                    while cursor.nextset():
                        pass
            
            # Registrar os pagamentos
            for pagamento in pagamentos:
                self.registrar_pagamento(
                    venda_id,
                    pagamento.get('forma_pagamento_id'),
                    pagamento.get('valor', 0),
                    pagamento.get('observacao')
                )
            
            self.db.commit()
            return venda_id
            
        except mysql.connector.Error:
            self.db.rollback()
            return 0
        finally:
            cursor.close()
    
    def vincular_conta_cliente(self, venda_id, cliente_id, valor):
        """Vincula uma venda à conta de um cliente (pendura)."""
        try:
            cursor = self.db.cursor()
            
            # Inserir na tabela de contas de clientes
            cursor.execute("""
                INSERT INTO contas_clientes (
                    cliente_id, venda_id, valor, status
                )
                VALUES (%s, %s, %s, %s)
            """, (cliente_id, venda_id, valor, 'pendente'))
            
            conta_id = cursor.lastrowid
            
            # Atualizar o status da venda para pago
            cursor.execute("""
                UPDATE vendas
                SET status = 'pago'
                WHERE id = %s
            """, (venda_id,))
            
            self.db.commit()
            return conta_id
            
        except mysql.connector.Error:
            self.db.rollback()
            return 0
        finally:
            cursor.close()
