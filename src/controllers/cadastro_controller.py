"""
Controlador para o módulo de Cadastro.
"""
from typing import Dict, List, Optional, Tuple, Any

class CadastroController:
    """Controlador para operações do módulo de Cadastro."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        self._cliente_controller = None
        # Aqui você pode inicializar o DB específico do módulo
        # from src.db.cadastro_db import CadastroDB
        # self.db = CadastroDB(obter_conexao())
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
    
    @property
    def cliente_controller(self):
        """Obtém uma instância do ClienteController sob demanda."""
        if self._cliente_controller is None:
            from src.controllers.cliente_controller import ClienteController
            self._cliente_controller = ClienteController()
        return self._cliente_controller
        
    def listar_produtos(self):
        """Lista todos os produtos cadastrados."""
        from src.db.cadastro_db import CadastroDB
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            db = CadastroDB(connection)
            return db.listar_produtos()
        except Exception as e:
            raise Exception(f"Erro ao listar produtos: {str(e)}")
            
    def obter_produto_por_id(self, produto_id):
        """
        Obtém um produto pelo seu ID.
        
        Args:
            produto_id: ID do produto a ser buscado
            
        Returns:
            dict: Dicionário com os dados do produto ou None se não encontrado
        """
        from src.db.cadastro_db import CadastroDB
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            db = CadastroDB(connection)
            
            # Usar o método existente obter_produto
            return db.obter_produto(produto_id)
        except Exception as e:
            print(f"Erro ao obter produto por ID: {str(e)}")
            return None
            
    def obter_produto(self, produto_id):
        """Obtém um produto pelo ID."""
        from src.db.cadastro_db import CadastroDB
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            db = CadastroDB(connection)
            return db.obter_produto(produto_id)
        except Exception as e:
            print(f"Erro ao obter produto: {str(e)}")
            return None
            
    def excluir_produto(self, produto_id):
        """
        Exclui um produto do banco de dados.
        
        Args:
            produto_id: ID do produto a ser excluído
            
        Returns:
            tuple: (sucesso, mensagem) onde sucesso é booleano e mensagem é string
        """
        from src.db.cadastro_db import CadastroDB
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            db = CadastroDB(connection)
            
            # Verificar se o produto existe antes de tentar excluir
            produto = db.obter_produto(produto_id)
            if not produto:
                return False, "Produto não encontrado"
                
            # Tentar excluir o produto
            sucesso = db.excluir_produto(produto_id)
            if sucesso:
                return True, "Produto excluído com sucesso"
            else:
                return False, "Não foi possível excluir o produto"
                
        except Exception as e:
            return False, f"Erro ao excluir produto: {str(e)}"
            
    # Métodos para gerenciar clientes usando ClienteController e a tabela clientes_delivery
    def listar_clientes(self, filtro: str = None) -> List[Dict[str, Any]]:
        """
        Lista todos os clientes, opcionalmente filtrando por nome ou telefone.
        
        Args:
            filtro: Texto para filtrar por nome ou telefone (opcional).
            
        Returns:
            Lista de dicionários com os dados dos clientes.
        """
        return self.cliente_controller.listar_clientes(filtro)
    
    def obter_cliente(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um cliente pelo ID.
        
        Args:
            cliente_id: ID do cliente.
            
        Returns:
            Dicionário com os dados do cliente ou None se não encontrado.
        """
        return self.cliente_controller.obter_cliente_por_id(cliente_id)
    
    def inserir_cliente(self, **dados_cliente) -> bool:
        """
        Insere um novo cliente no banco de dados.
        
        Args:
            **dados_cliente: Dados do cliente a serem inseridos.
            
        Returns:
            True se o cliente foi inserido com sucesso, False caso contrário.
        """
        sucesso, resultado = self.cliente_controller.cadastrar_cliente(dados_cliente)
        if sucesso:
            return True
        else:
            raise Exception(resultado)  # Lança exceção com a mensagem de erro
    
    def atualizar_cliente(self, cliente_id: int, **dados_atualizados) -> bool:
        """
        Atualiza os dados de um cliente existente.
        
        Args:
            cliente_id: ID do cliente a ser atualizado.
            **dados_atualizados: Dados atualizados do cliente.
            
        Returns:
            True se o cliente foi atualizado com sucesso, False caso contrário.
        """
        sucesso, mensagem = self.cliente_controller.atualizar_cliente(cliente_id, dados_atualizados)
        if sucesso:
            return True
        else:
            raise Exception(mensagem)  # Lança exceção com a mensagem de erro
