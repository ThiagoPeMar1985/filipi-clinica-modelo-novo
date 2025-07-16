"""
Controlador para o módulo de Opções de Produtos.

Table: opcoes_grupos
Columns:
id int AI PK 
nome varchar(100) 
descricao text 
obrigatorio tinyint(1) 
selecao_minima int 
selecao_maxima int 
ativo tinyint(1) 
data_criacao timestamp 
data_atualizacao timestamp

Table: opcoes_itens
Columns:
id int AI PK 
grupo_id int 
nome varchar(100) 
descricao text 
preco_adicional decimal(10,2) 
ativo tinyint(1) 
data_criacao timestamp 
data_atualizacao timestamp


"""

class OpcoesController:
    """Controlador para operações do módulo de Opções."""
    
    def __init__(self, view=None, db_connection=None):
        """Inicializa o controlador com a view e conexão com o banco de dados."""
        self.view = view
        self.db = None
        
        if db_connection:
            from src.db.opcoes_db import OpcoesDB
            self.db = OpcoesDB(db_connection)
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
    
    # Métodos para Grupos de Opções
    def listar_grupos(self, ativo=True):
        """Lista todos os grupos de opções."""
        if not self.db:
            return []
        return self.db.listar_grupos(ativo)
    
    def obter_grupo(self, grupo_id):
        """Obtém um grupo de opções pelo ID."""
        if not self.db:
            return None
        return self.db.obter_grupo(grupo_id)
    
    def salvar_grupo(self, dados_grupo):
        """Salva ou atualiza um grupo de opções."""
        if not self.db:
            return 0
        return self.db.salvar_grupo(dados_grupo)
    
    def excluir_grupo(self, grupo_id):
        """Exclui um grupo de opções (exclusão lógica)."""
        if not self.db:
            return False
        return self.db.excluir_grupo(grupo_id)
    
    # Métodos para Itens de Opções
    def listar_itens_por_grupo(self, grupo_id, ativo=True):
        """Lista todos os itens de um grupo de opções."""
        if not self.db:
            return []
        return self.db.listar_itens_por_grupo(grupo_id, ativo)
    
    def salvar_item(self, grupo_id, dados_item):
        """Salva ou atualiza um item de opção."""
        if not self.db:
            return 0
        return self.db.salvar_item(grupo_id, dados_item)
    
    def excluir_item(self, item_id):
        """Exclui um item de opção (exclusão lógica)."""
        if not self.db:
            return False
        return self.db.excluir_item(item_id)
        
    def obter_item_opcao(self, item_id):
        """Obtém um item de opção pelo ID."""
        if not self.db:
            return None
        return self.db.obter_item(item_id)
        
    def criar_opcao_texto_livre(self, grupo_id, nome, descricao="", preco_adicional=0.0):
        """
        Cria uma opção de texto livre em um grupo de opções.
        
        Args:
            grupo_id: ID do grupo de opções
            nome: Nome da opção de texto livre
            descricao: Descrição da opção (opcional)
            preco_adicional: Preço adicional para esta opção (padrão: 0.0)
            
        Returns:
            int: ID do item criado ou 0 em caso de erro
        """
        if not self.db:
            return 0
            
        dados_item = {
            'nome': nome,
            'descricao': descricao,
            'preco_adicional': preco_adicional,
            'tipo': 'texto_livre',
            'ativo': True
        }
        
        return self.db.salvar_item(grupo_id, dados_item)
    
    # Métodos para Relação entre Produtos e Opções
    def listar_grupos_por_produto(self, produto_id):
        """Lista todos os grupos de opções de um produto."""
        if not self.db:
            return []
        return self.db.listar_grupos_por_produto(produto_id)
    
    def adicionar_grupo_ao_produto(self, produto_id, grupo_id, obrigatorio=False, ordem=0):
        """Adiciona um grupo de opções a um produto."""
        if not self.db:
            return False
        return self.db.adicionar_grupo_ao_produto(produto_id, grupo_id, obrigatorio, ordem)
    
    def remover_grupo_do_produto(self, produto_id, grupo_id):
        """Remove um grupo de opções de um produto."""
        if not self.db:
            return False
        return self.db.remover_grupo_do_produto(produto_id, grupo_id)
    
    def listar_opcoes_por_produto(self, produto_id):
        """Lista todas as opções disponíveis para um produto, agrupadas por grupo."""
        if not self.db:
            return {}
            
        opcoes = self.db.listar_opcoes_por_produto(produto_id)
        return opcoes
        
    def listar_produtos_para_vinculo(self):
        """Lista todos os produtos que podem ter opções vinculadas."""
        if not self.db:
            return []
            
        try:
            cursor = self.db.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome, tipo 
                FROM produtos 
                WHERE ativo = TRUE 
                ORDER BY nome
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar produtos para vínculo: {e}")
            return []
            
    def listar_produtos_por_categoria(self, categoria):
        """
        Lista os produtos de uma categoria específica.
        
        Args:
            categoria: Nome da categoria (bar, cozinha, sobremesa, outros)
            
        Returns:
            Lista de dicionários com os produtos da categoria
        """
        if not self.db:
            return []
            
        try:
            cursor = self.db.db.cursor(dictionary=True)
            
            # Mapeia o nome da categoria para o valor no banco de dados
            categoria_map = {
                'bar': 'Bar',
                'cozinha': 'Cozinha',
                'sobremesa': 'Sobremesas',
                'outros': 'Outros'
            }
            
            tipo_produto = categoria_map.get(categoria.lower(), 'Outros')
            
            cursor.execute("""
                SELECT id, nome, preco_venda as preco 
                FROM produtos 
                WHERE tipo = %s
                ORDER BY nome
            """, (tipo_produto,))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Erro ao listar produtos por categoria {categoria}: {e}")
            return []
            
    def listar_grupos_para_vinculo(self):
        """Lista todos os grupos de opções disponíveis para vínculo."""
        if not self.db:
            return []
            
        try:
            cursor = self.db.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nome 
                FROM opcoes_grupos 
                WHERE ativo = TRUE 
                ORDER BY nome
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar grupos para vínculo: {e}")
            return []
            
    def listar_produtos_por_grupo(self, grupo_id):
        """
        Lista todos os produtos vinculados a um grupo de opções.
        
        Args:
            grupo_id: ID do grupo de opções
            
        Returns:
            Lista de dicionários com informações dos produtos
        """
        if not self.db:
            return []
            
        try:
            return self.db.listar_produtos_por_grupo(grupo_id)
        except Exception as e:
            print(f"Erro ao listar produtos do grupo: {e}")
            return []
    
    def atualizar_status_vinculo(self, produto_id, grupo_id, obrigatorio):
        """
        Atualiza o status de obrigatório de um vínculo entre produto e grupo.
        
        Args:
            produto_id: ID do produto
            grupo_id: ID do grupo de opções
            obrigatorio: Novo status de obrigatório (True/False)
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not self.db:
            return False
            
        try:
            cursor = self.db.db.cursor()
            cursor.execute("""
                UPDATE produto_opcoes 
                SET obrigatorio = %s 
                WHERE produto_id = %s AND grupo_id = %s
            """, (obrigatorio, produto_id, grupo_id))
            
            if cursor.rowcount > 0:
                self.db.db.commit()
                return True
            return False
            
        except Exception as e:
            print(f"Erro ao atualizar status do vínculo: {e}")
            self.db.db.rollback()
            return False
    
    def salvar_vinculos_produto(self, produto_id, vinculos):
        """
        Salva os vínculos entre um produto e os grupos de opções.
        
        Args:
            produto_id: ID do produto
            vinculos: Lista de dicionários com as chaves 'grupo_id' e 'obrigatorio'
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.db:
            return False
            
        try:
            cursor = self.db.db.cursor()
            
            # Remove todos os vínculos existentes para o produto
            cursor.execute("""
                DELETE FROM produto_opcoes 
                WHERE produto_id = %s
            """, (produto_id,))
            
            # Adiciona os novos vínculos
            for vinculo in vinculos:
                cursor.execute("""
                    INSERT INTO produto_opcoes 
                    (produto_id, grupo_id, obrigatorio) 
                    VALUES (%s, %s, %s)
                """, (
                    produto_id,
                    vinculo['grupo_id'],
                    vinculo['obrigatorio']
                ))
            
            self.db.db.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar vínculos do produto: {e}")
            self.db.db.rollback()
            return False
            
    def salvar_vinculos_grupo(self, grupo_id, vinculos):
        """
        Salva os vínculos entre um grupo de opções e produtos.
        
        Args:
            grupo_id: ID do grupo de opções
            vinculos: Lista de dicionários com as chaves 'produto_id' e 'obrigatorio'
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.db:
            return False
            
        try:
            cursor = self.db.db.cursor()
            
            # Remove todos os vínculos existentes para o grupo
            cursor.execute("""
                DELETE FROM produto_opcoes 
                WHERE grupo_id = %s
            """, (grupo_id,))
            
            # Adiciona os novos vínculos
            for vinculo in vinculos:
                cursor.execute("""
                    INSERT INTO produto_opcoes 
                    (produto_id, grupo_id, obrigatorio) 
                    VALUES (%s, %s, %s)
                """, (
                    vinculo['produto_id'],
                    grupo_id,
                    vinculo['obrigatorio']
                ))
            
            self.db.db.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar vínculos do grupo: {e}")
            self.db.db.rollback()
            return False
            
    def salvar_vinculo_grupo(self, produto_id, grupo_id, obrigatorio=False):
        """
        Salva um único vínculo entre produto e grupo.
        
        Args:
            produto_id: ID do produto
            grupo_id: ID do grupo de opções
            obrigatorio: Se o grupo é obrigatório para o produto
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        if not self.db:
            return False
            
        try:
            cursor = self.db.db.cursor()
            
            # Verifica se o vínculo já existe
            cursor.execute("""
                SELECT COUNT(*) FROM produto_opcoes 
                WHERE produto_id = %s AND grupo_id = %s
            """, (produto_id, grupo_id))
            
            if cursor.fetchone()[0] > 0:
                # Atualiza o vínculo existente
                cursor.execute("""
                    UPDATE produto_opcoes 
                    SET obrigatorio = %s 
                    WHERE produto_id = %s AND grupo_id = %s
                """, (obrigatorio, produto_id, grupo_id))
            else:
                # Cria um novo vínculo
                cursor.execute("""
                    INSERT INTO produto_opcoes 
                    (produto_id, grupo_id, obrigatorio) 
                    VALUES (%s, %s, %s)
                """, (produto_id, grupo_id, obrigatorio))
            
            self.db.db.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar vínculo: {e}")
            self.db.db.rollback()
            return False
