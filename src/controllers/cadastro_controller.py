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
            
    # Métodos para gerenciar configurações de impressoras
    def verificar_tabela_impressoras_tipos(self):
        """
        Verifica se a tabela impressoras_tipos existe, se não, cria
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        from src.db.database import DatabaseConnection
        
        try:
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            cursor = connection.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("SHOW TABLES LIKE 'impressoras_tipos'")
            if not cursor.fetchone():
                # Criar tabela se não existir
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS impressoras_tipos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    impressora_id INT NOT NULL,
                    tipo_id INT NOT NULL,
                    FOREIGN KEY (tipo_id) REFERENCES tipos_produtos(id),
                    UNIQUE(impressora_id, tipo_id)
                );
                """)
                connection.commit()
                print("Tabela impressoras_tipos criada com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao verificar/criar tabela impressoras_tipos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def salvar_config_impressoras(self, config_impressoras):
        """
        Salva a configuração de impressoras por tipo de produto no banco de dados
        
        Args:
            config_impressoras (dict): Dicionário com as configurações de impressoras
                                      {impressora_id: [nome_tipo1, nome_tipo2, ...]}
        
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        from src.db.database import DatabaseConnection
        from src.db.cadastro_db import CadastroDB
        
        try:
            # Verificar se a tabela existe
            if not self.verificar_tabela_impressoras_tipos():
                return False
                
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            cursor = connection.cursor()
            db = CadastroDB(connection)
            
            # Limpar configurações anteriores
            cursor.execute("DELETE FROM impressoras_tipos")
            
            # Inserir novas configurações
            for impressora_id, tipos in config_impressoras.items():
                for tipo_nome in tipos:
                    # Obter o ID do tipo pelo nome
                    cursor.execute("SELECT id FROM tipos_produtos WHERE nome = %s", (tipo_nome,))
                    resultado = cursor.fetchone()
                    if resultado:
                        tipo_id = resultado[0]
                        # Inserir na tabela de configuração
                        cursor.execute("""
                        INSERT INTO impressoras_tipos (impressora_id, tipo_id)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE impressora_id = VALUES(impressora_id)
                        """, (int(impressora_id), tipo_id))
            
            # Confirmar as alterações
            connection.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações de impressoras: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # Mapeamento explícito entre IDs numéricos e nomes de impressoras
    # Este mapeamento deve ser usado em todo o sistema para garantir consistência
    MAPEAMENTO_IMPRESSORAS = {
        # ID numérico -> nome interno -> nome de exibição
        "1": {"nome_interno": "impressora 1", "nome_exibicao": "impressora 1"},
        "2": {"nome_interno": "impressora 2", "nome_exibicao": "impressora 2"},
        "3": {"nome_interno": "impressora 3", "nome_exibicao": "impressora 3"},
        "4": {"nome_interno": "impressora 4", "nome_exibicao": "impressora 4"},
        "5": {"nome_interno": "impressora 5", "nome_exibicao": "impressora 5"}
    }
    
    def carregar_config_impressoras(self):
        """
        Carrega as configurações de impressoras salvas do banco de dados
        
        Returns:
            dict: Dicionário com as configurações de impressoras
                 {impressora_id: [nome_tipo1, nome_tipo2, ...]}
        """
        from src.db.database import DatabaseConnection
        
        # Configuração padrão (vazia)
        config = {
            "1": [],  # Cupom Fiscal
            "2": [],  # Cozinha
            "3": [],  # Bar
            "4": [],  # Sobremesas
            "5": []   # Outros
        }
        
        try:
            # Verificar se a tabela existe
            if not self.verificar_tabela_impressoras_tipos():
                return config
                
            # Obter conexão usando a classe DatabaseConnection
            connection = DatabaseConnection().get_connection()
            cursor = connection.cursor()
            
            # Carregar configurações do banco de dados
            query = """
            SELECT it.impressora_id, tp.nome
            FROM impressoras_tipos it
            JOIN tipos_produtos tp ON it.tipo_id = tp.id
            ORDER BY it.impressora_id, tp.nome
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            # Preencher a configuração com os resultados do banco
            for impressora_id, nome_tipo in resultados:
                config[str(impressora_id)].append(nome_tipo)
                
            return config
        except Exception as e:
            print(f"Erro ao carregar configurações de impressoras: {str(e)}")
            import traceback
            traceback.print_exc()
            return config
    
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
            
    def excluir_cliente(self, cliente_id: int) -> bool:
        """
        Exclui permanentemente um cliente do banco de dados.
        
        Args:
            cliente_id: ID do cliente a ser excluído.
            
        Returns:
            bool: True se o cliente foi excluído com sucesso, False caso contrário.
            
        Raises:
            Exception: Se ocorrer um erro durante a exclusão.
        """
        sucesso, mensagem = self.cliente_controller.excluir_cliente(cliente_id)
        if sucesso:
            return True
        else:
            raise Exception(mensagem)  # Lança exceção com a mensagem de erro
