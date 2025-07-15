"""
Módulo para operações de banco de dados do módulo de Cadastro.
e vai usar essas tabelas que estão no banco de dados 

Table: empresas
Columns:
id int AI PK 
nome_fantasia varchar(255) 
razao_social varchar(255) 
cnpj varchar(20) 
inscricao_estadual varchar(50) 
telefone varchar(20) 
endereco text 

Table: usuarios
Columns:
id int AI PK 
nome varchar(255) 
login varchar(50) 
senha varchar(255) 
nivel varchar(50) 
telefone varchar(20)

Table: funcionarios
Columns:
id int AI PK 
nome varchar(255) 
idade varchar(10) 
cpf varchar(14) 
cargo varchar(100) 
telefone varchar(20) 
endereco text

Table: clientes_pendura
Columns:
id int AI PK 
nome varchar(255) 
telefone varchar(20) 
cpf varchar(14) 
endereco text 
data_cadastro datetime 
ativo tinyint(1) 
observacoes text
 
Table: produtos
Columns:
id int AI PK 
nome varchar(255) 
descricao text 
tipo varchar(50) 
preco_venda decimal(10,2) 
unidade_medida varchar(10) 
quantidade_minima decimal(10,2)

Table: fornecedores
Columns:
id int AI PK 
empresa varchar(255) 
vendedor varchar(255) 
produtos text 
telefone varchar(20) 
email varchar(255)

"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class CadastroDB:
    """Classe para operações de banco de dados do módulo de Cadastro."""
    
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
    
    # Métodos para Funcionários
    def obter_funcionario_por_id(self, funcionario_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um funcionário pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM funcionarios WHERE id = %s", (funcionario_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter funcionário: {e}")
            return None
    
    def inserir_funcionario(self, **dados) -> bool:
        """Insere um novo funcionário no banco de dados."""
        try:
            cursor = self.db.cursor()
            campos = ', '.join(dados.keys())
            valores = tuple(dados.values())
            placeholders = ', '.join(['%s'] * len(dados))
            
            query = f"INSERT INTO funcionarios ({campos}) VALUES ({placeholders})"
            cursor.execute(query, valores)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir funcionário: {e}")
            self.db.rollback()
            return False
    
    def atualizar_funcionario(self, funcionario_id: int, **dados) -> bool:
        """Atualiza os dados de um funcionário existente."""
        try:
            cursor = self.db.cursor()
            sets = [f"{campo} = %s" for campo in dados.keys()]
            valores = list(dados.values())
            valores.append(funcionario_id)
            
            query = f"UPDATE funcionarios SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(query, valores)
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar funcionário: {e}")
            self.db.rollback()
            return False
    
    def excluir_funcionario(self, funcionario_id: int) -> bool:
        """Exclui um funcionário do banco de dados."""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM funcionarios WHERE id = %s", (funcionario_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir funcionário: {e}")
            self.db.rollback()
            return False
    
    # Métodos para Empresa
    def obter_empresa(self) -> Optional[Dict[str, Any]]:
        """Obtém os dados da empresa."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM empresas LIMIT 1")
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter dados da empresa: {e}")
            return None
    
    def salvar_empresa(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva ou atualiza os dados da empresa.
        Como só pode existir uma empresa no sistema, sempre faz UPDATE se existir,
        ou INSERT se for a primeira vez.
        """
        try:
            cursor = self.db.cursor()
            
            # Lista de campos na ordem correta
            campos = [
                'nome_fantasia', 'razao_social', 'cnpj',  # obrigatórios
                'inscricao_estadual', 'telefone', 'endereco',  # opcionais
                'cep', 'bairro', 'cidade', 'estado', 'numero'  # opcionais
            ]
            
            # Prepara os valores
            valores = []
            for campo in campos:
                # Para campos obrigatórios, usa string vazia como padrão
                # Para opcionais, usa None como padrão
                valor = dados.get(campo, '' if campo in ['nome_fantasia', 'razao_social', 'cnpj'] else None)
                valores.append(valor)
            
            # Verifica se já existe empresa
            cursor.execute("SELECT id FROM empresas LIMIT 1")
            empresa_existente = cursor.fetchone()
            
            if empresa_existente:
                # Atualiza empresa existente
                query = f"""
                    UPDATE empresas 
                    SET {', '.join([f"{campo} = %s" for campo in campos])}
                    LIMIT 1  # Garante que só uma linha seja afetada
                """
            else:
                # Insere nova empresa
                placeholders = ', '.join(['%s'] * len(campos))
                query = f"""
                    INSERT INTO empresas 
                    ({', '.join(campos)})
                    VALUES ({placeholders})
                """
            
            cursor.execute(query, valores)
            self.db.commit()
            return True, "Dados da empresa salvos com sucesso!"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao salvar dados da empresa: {str(e)}"
        
    # Métodos para Usuários
    def listar_usuarios(self) -> List[Dict[str, Any]]:
        """Lista todos os usuários cadastrados."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT id, nome, login, nivel, telefone FROM usuarios")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
    
    def obter_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um usuário pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter usuário: {e}")
            return None
    
    def salvar_usuario(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva ou atualiza um usuário."""
        try:
            cursor = self.db.cursor()
            
            # Se tiver ID, é atualização
            if 'id' in dados and dados['id']:
                query = """
                    UPDATE usuarios 
                    SET nome = %s, login = %s, nivel = %s, telefone = %s
                    {senha_sql}
                    WHERE id = %s
                """
                
                # Se tiver senha, atualiza a senha
                if 'senha' in dados and dados['senha']:
                    query = query.format(senha_sql=", senha = %s")
                    valores = (
                        dados['nome'],
                        dados['login'],
                        dados['nivel'],
                        dados['telefone'],
                        dados['senha'],
                        dados['id']
                    )
                else:
                    query = query.format(senha_sql="")
                    valores = (
                        dados['nome'],
                        dados['login'],
                        dados['nivel'],
                        dados['telefone'],
                        dados['id']
                    )
            else:
                # Inserção de novo usuário
                if 'senha' not in dados or not dados['senha']:
                    return False, "A senha é obrigatória para novo usuário."
                    
                query = """
                    INSERT INTO usuarios (nome, login, senha, nivel, telefone)
                    VALUES (%s, %s, %s, %s, %s)
                """
                valores = (
                    dados['nome'],
                    dados['login'],
                    dados['senha'],
                    dados['nivel'],
                    dados['telefone']
                )
            
            cursor.execute(query, valores)
            self.db.commit()
            return True, "Usuário salvo com sucesso!"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao salvar usuário: {str(e)}"
    
    def excluir_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """Exclui um usuário pelo ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
            self.db.commit()
            return True, "Usuário excluído com sucesso!"
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao excluir usuário: {str(e)}"
    
    # Métodos para Funcionários
    def listar_funcionarios(self) -> List[Dict[str, Any]]:
        """Lista todos os funcionários cadastrados."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM funcionarios")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar funcionários: {e}")
            return []
    
    def salvar_funcionario(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva ou atualiza um funcionário."""
        try:
            cursor = self.db.cursor()
            
            if 'id' in dados and dados['id']:
                # Atualização
                query = """
                    UPDATE funcionarios 
                    SET nome = %s, idade = %s, cpf = %s, 
                        cargo = %s, telefone = %s, endereco = %s
                    WHERE id = %s
                """
                valores = (
                    dados['nome'],
                    dados['idade'],
                    dados['cpf'],
                    dados['cargo'],
                    dados['telefone'],
                    dados['endereco'],
                    dados['id']
                )
            else:
                # Inserção
                query = """
                    INSERT INTO funcionarios 
                    (nome, idade, cpf, cargo, telefone, endereco)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (
                    dados['nome'],
                    dados['idade'],
                    dados['cpf'],
                    dados['cargo'],
                    dados['telefone'],
                    dados['endereco']
                )
            
            cursor.execute(query, valores)
            self.db.commit()
            return True, "Funcionário salvo com sucesso!"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao salvar funcionário: {str(e)}"
    
    def excluir_funcionario(self, funcionario_id: int) -> Tuple[bool, str]:
        """Exclui um funcionário pelo ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM funcionarios WHERE id = %s", (funcionario_id,))
            self.db.commit()
            return True, "Funcionário excluído com sucesso!"
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao excluir funcionário: {str(e)}"

    
    # Métodos para Produtos
    def listar_produtos(self) -> List[Dict[str, Any]]:
        """Lista todos os produtos cadastrados."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM produtos ORDER BY nome")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return []

    def obter_produto(self, produto_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um produto pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter produto: {e}")
            return None

    def inserir_produto(self, **dados) -> bool:
        """Insere um novo produto no banco de dados."""
        try:
            cursor = self.db.cursor()
            campos = ', '.join(dados.keys())
            valores = tuple(dados.values())
            placeholders = ', '.join(['%s'] * len(dados))
            
            query = f"INSERT INTO produtos ({campos}) VALUES ({placeholders})"
            cursor.execute(query, valores)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erro ao inserir produto: {e}")
            self.db.rollback()
            return False

    def atualizar_produto(self, produto_id: int, **dados) -> bool:
        """Atualiza um produto existente."""
        try:
            cursor = self.db.cursor()
            campos = ', '.join([f"{k} = %s" for k in dados.keys()])
            valores = tuple(dados.values()) + (produto_id,)
            
            query = f"UPDATE produtos SET {campos} WHERE id = %s"
            cursor.execute(query, valores)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            self.db.rollback()
            return False

    def excluir_produto(self, produto_id: int) -> bool:
        """Exclui um produto do banco de dados"""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir produto: {e}")
            self.db.rollback()
            return False
    
    def remover_produto(self, produto_id: int) -> bool:
        """Remove um produto do banco de dados."""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
            self.db.commit()
            return True
        except Exception as e:
            print(f"Erro ao remover produto: {e}")
            self.db.rollback()
            return False
    
    # Métodos para Fornecedores
    def listar_fornecedores(self) -> List[Dict[str, Any]]:
        """Lista todos os fornecedores cadastrados"""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM fornecedores ORDER BY empresa")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar fornecedores: {e}")
            return []
    
    def obter_fornecedor(self, fornecedor_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um fornecedor pelo ID"""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM fornecedores WHERE id = %s", (fornecedor_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter fornecedor: {e}")
            return None
    
    def inserir_fornecedor(self, **dados) -> bool:
        """Insere um novo fornecedor no banco de dados"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO fornecedores 
                (empresa, vendedor, telefone, email, produtos)
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (
                dados['empresa'],
                dados['vendedor'],
                dados['telefone'],
                dados['email'],
                dados['produtos']
            )
            cursor.execute(query, valores)
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao inserir fornecedor: {e}")
            self.db.rollback()
            return False
    
    def atualizar_fornecedor(self, fornecedor_id: int, **dados) -> bool:
        """Atualiza os dados de um fornecedor"""
        try:
            cursor = self.db.cursor()
            query = """
                UPDATE fornecedores SET
                empresa = %s,
                vendedor = %s,
                telefone = %s,
                email = %s,
                produtos = %s
                WHERE id = %s
            """
            valores = (
                dados['empresa'],
                dados['vendedor'],
                dados['telefone'],
                dados['email'],
                dados['produtos'],
                fornecedor_id
            )
            cursor.execute(query, valores)
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar fornecedor: {e}")
            self.db.rollback()
            return False
    
    def excluir_fornecedor(self, fornecedor_id: int) -> bool:
        """Exclui um fornecedor do banco de dados"""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM fornecedores WHERE id = %s", (fornecedor_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir fornecedor: {e}")
            self.db.rollback()
            return False
