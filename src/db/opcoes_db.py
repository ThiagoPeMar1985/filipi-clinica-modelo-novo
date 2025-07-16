"""
Módulo para operações de banco de dados do módulo de Opções.
"""
from typing import Dict, List, Any, Optional
import mysql.connector

class OpcoesDB:
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria as tabelas necessárias para o módulo de opções."""
        try:
            cursor = self.db.cursor()
            
            # Tabela de grupos de opções
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS opcoes_grupos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                obrigatorio BOOLEAN DEFAULT FALSE,
                selecao_minima INT DEFAULT 0,
                selecao_maxima INT DEFAULT 1,
                ativo BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de opções
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS opcoes_itens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                grupo_id INT NOT NULL,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                preco_adicional DECIMAL(10,2) DEFAULT 0.00,
                ativo BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (grupo_id) REFERENCES opcoes_grupos(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # Tabela de relação entre produtos e grupos de opções
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS produto_opcoes (
                produto_id INT NOT NULL,
                grupo_id INT NOT NULL,
                ordem INT DEFAULT 0,
                obrigatorio BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (produto_id, grupo_id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE,
                FOREIGN KEY (grupo_id) REFERENCES opcoes_grupos(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            self.db.commit()
            cursor.close()
            return True
            
        except mysql.connector.Error as err:
            print(f"Erro ao criar tabelas de opções: {err}")
            return False
    
    # Métodos para Grupos de Opções
    def listar_grupos(self, ativo: bool = True) -> List[Dict[str, Any]]:
        """Lista todos os grupos de opções."""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = "SELECT * FROM opcoes_grupos"
            params = ()
            
            if ativo is not None:
                query += " WHERE ativo = %s"
                params = (ativo,)
                
            query += " ORDER BY nome"
            cursor.execute(query, params)
            
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar grupos de opções: {err}")
            return []
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
    
    def obter_grupo(self, grupo_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um grupo de opções pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM opcoes_grupos 
                WHERE id = %s
            """, (grupo_id,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Erro ao obter grupo de opções: {err}")
            return None
        finally:
            cursor.close()
    
    def salvar_grupo(self, dados: Dict[str, Any]) -> int:
        """Salva ou atualiza um grupo de opções."""
        try:
            cursor = self.db.cursor()
            
            if 'id' in dados and dados['id']:
                # Atualizar grupo existente
                cursor.execute("""
                    UPDATE opcoes_grupos 
                    SET nome = %s, 
                        descricao = %s, 
                        obrigatorio = %s,
                        selecao_minima = %s,
                        selecao_maxima = %s,
                        ativo = %s
                    WHERE id = %s
                """, (
                    dados['nome'],
                    dados.get('descricao', ''),
                    dados.get('obrigatorio', False),
                    dados.get('selecao_minima', 0),
                    dados.get('selecao_maxima', 1),
                    dados.get('ativo', True),
                    dados['id']
                ))
                grupo_id = dados['id']
            else:
                # Inserir novo grupo
                cursor.execute("""
                    INSERT INTO opcoes_grupos 
                    (nome, descricao, obrigatorio, selecao_minima, selecao_maxima, ativo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    dados['nome'],
                    dados.get('descricao', ''),
                    dados.get('obrigatorio', False),
                    dados.get('selecao_minima', 0),
                    dados.get('selecao_maxima', 1),
                    dados.get('ativo', True)
                ))
                grupo_id = cursor.lastrowid
            
            self.db.commit()
            return grupo_id
            
        except mysql.connector.Error as err:
            self.db.rollback()
            print(f"Erro ao salvar grupo de opções: {err}")
            return 0
        finally:
            cursor.close()
    
    def excluir_grupo(self, grupo_id: int) -> bool:
        """Exclui um grupo de opções (exclusão lógica)."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE opcoes_grupos 
                SET ativo = FALSE 
                WHERE id = %s
            """, (grupo_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            self.db.rollback()
            print(f"Erro ao excluir grupo de opções: {err}")
            return False
        finally:
            cursor.close()
    
    # Métodos para Itens de Opções
    def listar_itens_por_grupo(self, grupo_id: int, ativo: bool = True) -> List[Dict[str, Any]]:
        """Lista todos os itens de um grupo de opções."""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
                SELECT * FROM opcoes_itens 
                WHERE grupo_id = %s
            """
            params = [grupo_id]
            
            if ativo is not None:
                query += " AND ativo = %s"
                params.append(ativo)
                
            query += " ORDER BY nome"
            cursor.execute(query, params)
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro ao listar itens de opções: {err}")
            return []
        finally:
            cursor.close()
    
    def salvar_item(self, grupo_id: int, dados: Dict[str, Any]) -> int:
        """Salva ou atualiza um item de opção."""
        try:
            cursor = self.db.cursor()
            
            if 'id' in dados and dados['id']:
                # Atualizar item existente
                cursor.execute("""
                    UPDATE opcoes_itens 
                    SET nome = %s, 
                        descricao = %s, 
                        preco_adicional = %s,
                        tipo = %s,
                        ativo = %s
                    WHERE id = %s AND grupo_id = %s
                """, (
                    dados['nome'],
                    dados.get('descricao', ''),
                    dados.get('preco_adicional', 0.00),
                    dados.get('tipo', 'opcao_simples'),
                    dados.get('ativo', True),
                    dados['id'],
                    grupo_id
                ))
                item_id = dados['id']
            else:
                # Inserir novo item
                cursor.execute("""
                    INSERT INTO opcoes_itens 
                    (grupo_id, nome, descricao, preco_adicional, tipo, ativo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    grupo_id,
                    dados['nome'],
                    dados.get('descricao', ''),
                    dados.get('preco_adicional', 0.00),
                    dados.get('tipo', 'opcao_simples'),
                    dados.get('ativo', True)
                ))
                item_id = cursor.lastrowid
            
            self.db.commit()
            return item_id
            
        except mysql.connector.Error as err:
            self.db.rollback()
            print(f"Erro ao salvar item de opção: {err}")
            return 0
        finally:
            cursor.close()
    
    def excluir_item(self, item_id: int) -> bool:
        """Exclui um item de opção (exclusão lógica)."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE opcoes_itens 
                SET ativo = FALSE 
                WHERE id = %s
            """, (item_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            self.db.rollback()
            print(f"Erro ao excluir item de opção: {err}")
            return False
        finally:
            cursor.close()
            
    def obter_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um item de opção pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM opcoes_itens 
                WHERE id = %s
            """, (item_id,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Erro ao obter item de opção: {err}")
            return None
        finally:
            cursor.close()
    
    # Métodos para Relação entre Produtos e Opções
    def listar_grupos_por_produto(self, produto_id: int) -> List[Dict[str, Any]]:
        """Lista todos os grupos de opções de um produto."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT og.*, po.ordem, po.obrigatorio 
                FROM produto_opcoes po
                JOIN opcoes_grupos og ON po.grupo_id = og.id
                WHERE po.produto_id = %s
                ORDER BY po.ordem
            """, (produto_id,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro ao listar grupos de opções do produto: {err}")
            return []
        finally:
            cursor.close()
    
    def adicionar_grupo_ao_produto(self, produto_id: int, grupo_id: int, obrigatorio: bool = False, ordem: int = 0) -> bool:
        """Adiciona um grupo de opções a um produto."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO produto_opcoes 
                (produto_id, grupo_id, obrigatorio, ordem)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    obrigatorio = VALUES(obrigatorio),
                    ordem = VALUES(ordem)
            """, (
                produto_id,
                grupo_id,
                obrigatorio,
                ordem
            ))
            self.db.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            self.db.rollback()
            print(f"Erro ao adicionar grupo ao produto: {err}")
            return False
        finally:
            cursor.close()
    
    def remover_grupo_do_produto(self, produto_id: int, grupo_id: int) -> bool:
        """Remove um grupo de opções de um produto."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                DELETE FROM produto_opcoes 
                WHERE produto_id = %s AND grupo_id = %s
            """, (produto_id, grupo_id))
            self.db.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            self.db.rollback()
            print(f"Erro ao remover grupo do produto: {err}")
            return False
        finally:
            cursor.close()
    
    def listar_opcoes_por_produto(self, produto_id: int) -> Dict[int, List[Dict[str, Any]]]:
        """Lista todas as opções disponíveis para um produto, agrupadas por grupo."""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Primeiro, obtém os grupos associados ao produto
            grupos = self.listar_grupos_por_produto(produto_id)
            
            # Para cada grupo, obtém os itens ativos
            resultado = {}
            for grupo in grupos:
                grupo_id = grupo['id']
                itens = self.listar_itens_por_grupo(grupo_id, ativo=True)
                
                # Adiciona informações adicionais do grupo
                grupo_info = {
                    'nome': grupo['nome'],
                    'descricao': grupo.get('descricao', ''),
                    'obrigatorio': bool(grupo.get('obrigatorio', False)),
                    'selecao_minima': grupo.get('selecao_minima', 0),
                    'selecao_maxima': grupo.get('selecao_maxima', 1),
                    'ordem': grupo.get('ordem', 0),
                    'itens': itens
                }
                
                resultado[grupo_id] = grupo_info
            
            return resultado
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar opções do produto: {err}")
            return {}
        finally:
            cursor.close()
    
    def listar_opcoes_por_produto(self, produto_id: int) -> Dict[int, Dict[str, Any]]:
        """Lista todas as opções disponíveis para um produto, agrupadas por grupo."""
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Primeiro, obtemos os grupos de opções vinculados ao produto
            query_grupos = """
                SELECT g.*, po.obrigatorio, po.ordem
                FROM opcoes_grupos g
                JOIN produto_opcoes po ON g.id = po.grupo_id
                WHERE po.produto_id = %s AND g.ativo = TRUE
                ORDER BY po.ordem, g.nome
            """
            
            cursor.execute(query_grupos, (produto_id,))
            grupos = cursor.fetchall()
            
            resultado = {}
            
            # Para cada grupo, buscamos os itens ativos
            for grupo in grupos:
                grupo_id = grupo['id']
                
                query_itens = """
                    SELECT * 
                    FROM opcoes_itens 
                    WHERE grupo_id = %s AND ativo = TRUE
                    ORDER BY nome
                """
                cursor.execute(query_itens, (grupo_id,))
                itens = cursor.fetchall()
                
                # Adiciona informações adicionais do grupo
                grupo_info = {
                    'nome': grupo['nome'],
                    'descricao': grupo.get('descricao', ''),
                    'obrigatorio': bool(grupo.get('obrigatorio', False)),
                    'selecao_minima': grupo.get('selecao_minima', 0),
                    'selecao_maxima': grupo.get('selecao_maxima', 1),
                    'ordem': grupo.get('ordem', 0),
                    'itens': itens
                }
                
                resultado[grupo_id] = grupo_info
            
            return resultado
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar opções do produto: {err}")
            return {}
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
                
    def listar_produtos_por_grupo(self, grupo_id: int) -> List[Dict[str, Any]]:
        """Lista todos os produtos vinculados a um grupo de opções."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.id, p.nome, po.obrigatorio
                FROM produtos p
                JOIN produto_opcoes po ON p.id = po.produto_id
                WHERE po.grupo_id = %s
                ORDER BY p.nome
            """, (grupo_id,))
            return cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro ao listar produtos do grupo: {err}")
            return []
        finally:
            cursor.close()
            
    def listar_produtos_por_categoria(self, tipo_produto: str) -> List[Dict[str, Any]]:
        """
        Lista os produtos de uma categoria específica.
        
        Args:
            tipo_produto: Tipo do produto (Bebidas, Comida, Sobremesa, Outros)
            
        Returns:
            Lista de dicionários com os produtos da categoria
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, preco 
                FROM produtos 
                WHERE ativo = TRUE 
                AND tipo = %s
                ORDER BY nome
            """, (tipo_produto,))
            
            return cursor.fetchall()
            
        except mysql.connector.Error as err:
            print(f"Erro ao listar produtos por tipo {tipo_produto}: {err}")
            return []
        finally:
            cursor.close()
