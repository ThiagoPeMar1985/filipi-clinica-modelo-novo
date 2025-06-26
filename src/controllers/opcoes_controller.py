"""
Controlador para o módulo de Opções de Produtos.
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
        return self.db.listar_opcoes_por_produto(produto_id)
