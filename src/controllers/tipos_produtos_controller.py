"""
Controller para gerenciamento de tipos de produtos.
Permite criar, editar, excluir e listar tipos de produtos.
"""
from .base_controller import BaseController

class TiposProdutosController(BaseController):
    def __init__(self, db_connection=None):
        """
        Inicializa o controller de tipos de produtos.
        
        Args:
            db_connection: Conexão com o banco de dados
        """
        # A BaseController espera uma view, mas como não usamos, passamos None
        # Armazenamos a conexão em self.db para manter compatibilidade com o código existente
        super().__init__(None)
        self.db = db_connection
        
    def inicializar(self):
        """
        Inicializa o controlador e configura os eventos.
        Este método é necessário para atender à interface da classe base.
        """
        # Neste caso, não precisamos configurar eventos, pois a view é gerenciada externamente
        pass
    
    def verificar_tabela_tipos_produtos(self):
        """
        Verifica se a tabela tipos_produtos existe, se não, cria.
        
        Returns:
            bool: True se a tabela existe ou foi criada com sucesso, False caso contrário
        """
        try:
            cursor = self.db.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'tipos_produtos'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Criar a tabela se não existir
                cursor.execute("""
                CREATE TABLE tipos_produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(50) NOT NULL UNIQUE,
                    descricao TEXT,
                    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                self.db.commit()
                
                # Inserir os tipos padrão que já existem na tabela produtos
                cursor.execute("""
                INSERT INTO tipos_produtos (nome) 
                SELECT DISTINCT tipo FROM produtos 
                WHERE tipo IS NOT NULL AND tipo != ''
                """)
                self.db.commit()
                
                return True
            
            cursor.close()
            return True
            
        except Exception as e:
            self.log_error(f"Erro ao verificar/criar tabela de tipos: {str(e)}")
            self.db.rollback()
            return False
    
    def listar_tipos(self):
        """
        Lista todos os tipos de produtos.
        
        Returns:
            list: Lista de dicionários com os tipos de produtos
        """
        try:
            # Garantir que a tabela existe
            if not self.verificar_tabela_tipos_produtos():
                return []
                
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tipos_produtos ORDER BY nome")
            tipos = cursor.fetchall()
            cursor.close()
            return tipos
        except Exception as e:
            print(f"Erro ao listar tipos de produtos: {str(e)}")
            return []
    
    def obter_tipo(self, tipo_id):
        """
        Obtém um tipo de produto pelo ID.
        
        Args:
            tipo_id: ID do tipo de produto
            
        Returns:
            dict: Dicionário com os dados do tipo de produto ou None se não encontrado
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM tipos_produtos WHERE id = %s", (tipo_id,))
            tipo = cursor.fetchone()
            cursor.close()
            return tipo
        except Exception as e:
            print(f"Erro ao obter tipo de produto: {str(e)}")
            return None
    
    def criar_tipo(self, nome, descricao=None, cor=None):
        """
        Cria um novo tipo de produto.
        
        Args:
            nome: Nome do tipo de produto
            descricao: Descrição do tipo de produto (opcional)
            cor: Cor do tipo de produto (opcional)
            
        Returns:
            int: ID do tipo criado ou None em caso de erro
        """
        try:
            # Garantir que a tabela existe
            if not self.verificar_tabela_tipos_produtos():
                return None
                
            cursor = self.db.cursor()
            
            # Verificar se já existe um tipo com o mesmo nome
            cursor.execute("SELECT id FROM tipos_produtos WHERE nome = %s", (nome,))
            if cursor.fetchone():
                print(f"Já existe um tipo com o nome '{nome}'")
                cursor.close()
                return None
            
            # Inserir o novo tipo
            if descricao:
                cursor.execute(
                    """
                    INSERT INTO tipos_produtos (nome, descricao) 
                    VALUES (%s, %s)
                    """,
                    (nome, descricao)
                )

            else:
                cursor.execute(
                    """
                    INSERT INTO tipos_produtos (nome) 
                    VALUES (%s)
                    """,
                    (nome,)
                )
            
            self.db.commit()
            tipo_id = cursor.lastrowid
            cursor.close()
            return tipo_id
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar tipo de produto: {str(e)}")
            return None
    
    def atualizar_tipo(self, tipo_id, nome, descricao=None, cor=None):
        """
        Atualiza um tipo de produto existente.
        
        Args:
            tipo_id: ID do tipo de produto
            nome: Novo nome do tipo de produto
            descricao: Nova descrição do tipo de produto (opcional)
            cor: Nova cor do tipo de produto (opcional)
            
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        """
        try:
            cursor = self.db.cursor()
            
            # Verificar se já existe outro tipo com o mesmo nome (exceto o próprio)
            cursor.execute(
                "SELECT id FROM tipos_produtos WHERE nome = %s AND id != %s", 
                (nome, tipo_id)
            )
            if cursor.fetchone():
                print(f"Já existe um tipo com o nome '{nome}'")
                cursor.close()
                return False
            
            # Atualizar o tipo
            if descricao is not None and cor is not None:
                cursor.execute(
                    """
                    UPDATE tipos_produtos 
                    SET nome = %s, descricao = %s, cor = %s 
                    WHERE id = %s
                    """,
                    (nome, descricao, cor, tipo_id)
                )
            elif descricao is not None:
                cursor.execute(
                    """
                    UPDATE tipos_produtos 
                    SET nome = %s, descricao = %s 
                    WHERE id = %s
                    """,
                    (nome, descricao, tipo_id)
                )
            elif cor is not None:
                cursor.execute(
                    """
                    UPDATE tipos_produtos 
                    SET nome = %s, cor = %s 
                    WHERE id = %s
                    """,
                    (nome, cor, tipo_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE tipos_produtos 
                    SET nome = %s 
                    WHERE id = %s
                    """,
                    (nome, tipo_id)
                )
            
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao atualizar tipo de produto: {str(e)}")
            return False
    
    def excluir_tipo(self, tipo_id):
        """
        Exclui um tipo de produto.
        
        Args:
            tipo_id: ID do tipo de produto
            
        Returns:
            tuple: (bool, str) - (True/False, mensagem de erro se houver)
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            
            # Primeiro, obter o nome do tipo para verificar em produtos
            cursor.execute("SELECT nome FROM tipos_produtos WHERE id = %s", (tipo_id,))
            tipo = cursor.fetchone()
            
            if not tipo:
                return False, "Tipo de produto não encontrado."
                
            # Verificar se existem produtos associados a este tipo pelo nome
            cursor.execute("SELECT COUNT(*) as total FROM produtos WHERE tipo = %s", (tipo['nome'],))
            if cursor.fetchone()['total'] > 0:
                return False, "Existem produtos cadastrados com este tipo. Remova os produtos antes de excluir o tipo."
            
            # Verificar se o tipo está vinculado a alguma impressora
            cursor.execute("""
                SELECT 1 
                FROM impressoras_tipos 
                WHERE tipo_id = %s
                LIMIT 1
            """, (tipo_id,))
            
            if cursor.fetchone():
                return False, "Este tipo está vinculado a uma impressora. Desvincule o tipo da impressora antes de excluí-lo."
                
            # Excluir o tipo
            cursor.execute("DELETE FROM tipos_produtos WHERE id = %s", (tipo_id,))
            self.db.commit()
            
            resultado = cursor.rowcount > 0
            cursor.close()
            
            if resultado:
                return True, ""
            else:
                return False, "Não foi possível excluir o tipo de produto."
            
        except Exception as e:
            self.db.rollback()
            error_msg = str(e)
            print(f"Erro ao excluir tipo de produto: {error_msg}")
            
            # Verifica se o erro é de chave estrangeira
            if "foreign key constraint" in error_msg.lower() and "impressoras_tipos" in error_msg.lower():
                return False, "Este tipo está vinculado a uma configuração de impressora. Desvincule o tipo da impressora antes de excluí-lo."
                
            return False, f"Erro ao excluir tipo de produto: {error_msg}"
