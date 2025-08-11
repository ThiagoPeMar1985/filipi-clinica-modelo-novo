"""
Controlador para operações de cadastro do sistema.
Gerencia operações relacionadas a médicos, pacientes e outros cadastros.
"""
from typing import Dict, List, Optional, Tuple, Any

class CadastroController:
    """Controlador para operações de cadastro do sistema."""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
    
    def set_db_connection(self, db_connection):
        """Define a conexão com o banco de dados."""
        self.db = db_connection
    
    
    def obter_medico_por_id(self, medico_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um médico pelo ID."""
        if not self.db:
            return None
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicos WHERE id = %s", (medico_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter médico: {e}")
            return None
    
    def listar_medicos(self) -> List[Dict[str, Any]]:
        """Lista todos os médicos cadastrados."""
        if not self.db:
            return []
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicos ORDER BY nome")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar médicos: {e}")
            return []
    
    def listar_medicos_com_modelos(self) -> List[Dict[str, Any]]:
        """Lista todos os médicos, independente de terem modelos ou não."""
        if not self.db:
            return []
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
                SELECT m.* FROM medicos m
                ORDER BY m.nome
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar médicos: {e}")
            return []
    
    def salvar_medico(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva ou atualiza um médico."""
        if not self.db:
            return False, "Sem conexão com o banco de dados"
        
        try:
            cursor = self.db.cursor()
            
            # Validações
            campos_obrigatorios = ['nome', 'especialidade', 'crm', 'telefone', 'usuario_id']
            for campo in campos_obrigatorios:
                if not str(dados.get(campo, '')).strip():
                    return False, f"O campo {campo} é obrigatório"
            
            # Formatação
            nome = str(dados['nome']).strip()
            crm = ''.join(filter(str.isdigit, str(dados['crm'])))
            telefone = ''.join(filter(str.isdigit, str(dados['telefone'])))
            email = str(dados.get('email', '')).strip() or None
            try:
                usuario_id = int(dados.get('usuario_id')) if dados.get('usuario_id') is not None else None
            except Exception:
                usuario_id = None
            
            if 'id' in dados and dados['id']:
                # Atualização (sem coluna inexistente 'data_atualizacao')
                query = """
                    UPDATE medicos 
                    SET nome=%s, especialidade=%s, crm=%s, 
                        telefone=%s, email=%s, usuario_id=%s
                    WHERE id=%s
                """
                valores = (nome, dados['especialidade'], crm, telefone, email, usuario_id, dados['id'])
            else:
                # Inserção
                query = """
                    INSERT INTO medicos 
                    (nome, especialidade, crm, telefone, email, usuario_id, data_cadastro)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """
                valores = (nome, dados['especialidade'], crm, telefone, email, usuario_id)
            
            cursor.execute(query, valores)
            self.db.commit()
            
            if 'id' not in dados or not dados['id']:
                # Padroniza retorno: (ok, mensagem, lastrowid)
                return True, "Médico cadastrado com sucesso!", cursor.lastrowid
            return True, "Médico atualizado com sucesso!", None
                
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao salvar médico: {e}")
            return False, f"Erro ao salvar médico: {str(e)}", None

    def obter_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um usuário pelo ID."""
        if not self.db:
            return None
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
            return cursor.fetchone()
        except Exception as e:
            self.ultimo_erro = str(e)
            print(f"Erro ao obter usuário: {e}")
            return None
    
    def listar_usuarios(self) -> List[Dict[str, Any]]:
        """Lista todos os usuários cadastrados."""
        if not self.db:
            return []
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios ORDER BY nome")
            return cursor.fetchall()
        except Exception as e:
            self.ultimo_erro = str(e)
            print(f"Erro ao listar usuários: {e}")
            return []
    
    def salvar_usuario(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Salva ou atualiza um usuário.
        
        Args:
            dados: Dicionário com os dados do usuário
                - id (opcional): ID do usuário para atualização
                - nome: Nome completo (obrigatório)
                - login: Nome de usuário (obrigatório, único)
                - senha: Senha (obrigatória)
                - nivel: Nível de acesso (obrigatório, ex: 'admin' ou 'usuario')
                - telefone: Telefone (opcional)
                
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        if not self.db:
            return False, "Sem conexão com o banco de dados"
            
        try:
            cursor = self.db.cursor()
            
            # Validações
            campos_obrigatorios = ['nome', 'login', 'senha', 'nivel']
            for campo in campos_obrigatorios:
                if campo not in dados or not str(dados.get(campo, '')).strip():
                    return False, f"O campo {campo} é obrigatório"
            
            # Verifica se já existe usuário com o mesmo login
            if 'id' in dados and dados['id']:
                # Atualização - verifica se outro usuário tem o mesmo login
                cursor.execute(
                    "SELECT id FROM usuarios WHERE login = %s AND id != %s",
                    (dados['login'], dados['id'])
                )
            else:
                # Inserção - verifica se já existe o login
                cursor.execute(
                    "SELECT id FROM usuarios WHERE login = %s",
                    (dados['login'],)
                )
            
            if cursor.fetchone():
                return False, f"Já existe um usuário com o login '{dados['login']}'"
            
            # Prepara os dados para salvar
            nome = str(dados['nome']).strip()
            login = str(dados['login']).strip()
            senha = str(dados['senha']).strip()
            nivel = str(dados['nivel']).strip()
            telefone = str(dados.get('telefone', '')).strip() or None
            
            if 'id' in dados and dados['id']:
                # Atualização
                query = """
                    UPDATE usuarios 
                    SET nome=%s, login=%s, senha=%s, nivel=%s, telefone=%s
                    WHERE id=%s
                """
                valores = (nome, login, senha, nivel, telefone, dados['id'])
            else:
                # Inserção
                query = """
                    INSERT INTO usuarios 
                    (nome, login, senha, nivel, telefone)
                    VALUES (%s, %s, %s, %s, %s)
                """
                valores = (nome, login, senha, nivel, telefone)
            
            cursor.execute(query, valores)
            self.db.commit()
            
            if 'id' not in dados or not dados['id']:
                return True, ("Usuário cadastrado com sucesso!", cursor.lastrowid)
            return True, "Usuário atualizado com sucesso!"
                
        except Exception as e:
            self.db.rollback()
            self.ultimo_erro = str(e)
            return False, f"Erro ao salvar usuário: {str(e)}"
    
    def excluir_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """Exclui um usuário pelo ID."""
        if not self.db:
            return False, "Sem conexão com o banco de dados"
            
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
            self.db.commit()
            return True, "Usuário excluído com sucesso!"
        except Exception as e:
            self.db.rollback()
            self.ultimo_erro = str(e)
            return False, f"Erro ao excluir usuário: {str(e)}"
    
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
        """Salva ou atualiza os dados da empresa."""
        try:
            cursor = self.db.cursor()
            
            # Verifica se já existe uma empresa cadastrada
            empresa_existente = self.obter_empresa()
            
            if empresa_existente:
                # Atualização
                query = """
                    UPDATE empresas 
                    SET nome_fantasia = %s, razao_social = %s, cnpj = %s,
                        inscricao_estadual = %s, telefone = %s, endereco = %s,
                        cep = %s, bairro = %s, cidade = %s, estado = %s, numero = %s
                    WHERE id = %s
                """
                valores = (
                    dados.get('nome_fantasia', ''),
                    dados.get('razao_social', ''),
                    dados.get('cnpj', ''),
                    dados.get('inscricao_estadual', ''),
                    dados.get('telefone', ''),
                    dados.get('endereco', ''),
                    dados.get('cep', ''),
                    dados.get('bairro', ''),
                    dados.get('cidade', ''),
                    dados.get('estado', ''),
                    dados.get('numero', ''),
                    empresa_existente['id']
                )
            else:
                # Inserção
                query = """
                    INSERT INTO empresas 
                    (nome_fantasia, razao_social, cnpj, inscricao_estadual, 
                     telefone, endereco, cep, bairro, cidade, estado, numero)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    dados.get('nome_fantasia', ''),
                    dados.get('razao_social', ''),
                    dados.get('cnpj', ''),
                    dados.get('inscricao_estadual', ''),
                    dados.get('telefone', ''),
                    dados.get('endereco', ''),
                    dados.get('cep', ''),
                    dados.get('bairro', ''),
                    dados.get('cidade', ''),
                    dados.get('estado', ''),
                    dados.get('numero', '')
                )
            
            cursor.execute(query, valores)
            self.db.commit()
            return True, "Dados da empresa salvos com sucesso!"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao salvar dados da empresa: {str(e)}"

    def criar_receita(self, medico_id: int, nome: str, texto: str) -> Optional[int]:
        """Cria uma nova receita no banco de dados.
        
        Args:
            medico_id: ID do médico que está criando a receita
            nome: Nome/título da receita
            texto: Conteúdo da receita
            
        Returns:
            int: ID da receita criada ou None em caso de erro
        """
        if not self.db:
            return None
        try:
            from datetime import datetime
            
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO receitas (medico_id, nome, texto, data) VALUES (%s, %s, %s, %s)",
                (medico_id, nome, texto, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            self.db.commit()
            return cursor.lastrowid
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao criar receita: {e}")
            return None
        
    def obter_receita_por_id(self, receita_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma receita pelo ID."""
        if not self.db:
            return None
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM receitas WHERE id = %s", (receita_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter receita: {e}")
            return None

    def listar_receitas_por_medico(self, medico_id: int) -> List[Dict[str, Any]]:
        """Lista todas as receitas de um médico.
        
        Args:
            medico_id: ID do médico
            
        Returns:
            List[Dict]: Lista de dicionários com as receitas
        """
        if not self.db:
            return []
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, m.nome as nome_medico
                FROM receitas r
                LEFT JOIN medicos m ON r.medico_id = m.id
                WHERE r.medico_id = %s 
                ORDER BY r.data DESC
            """, (medico_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar receitas: {e}")
            return []

    def obter_receita_por_id(self, receita_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma receita pelo ID.
        
        Args:
            receita_id: ID da receita
            
        Returns:
            Dict: Dados da receita ou None se não encontrada
        """
        if not self.db:
            return None
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.*, m.nome as nome_medico
                FROM receitas r
                LEFT JOIN medicos m ON r.medico_id = m.id
                WHERE r.id = %s
            """, (receita_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter receita: {e}")
            return None

    def excluir_receita(self, receita_id: int) -> bool:
        """Exclui uma receita."""
        if not self.db:
            return False
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM receitas WHERE id = %s", (receita_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir receita: {e}")
            self.db.rollback()
            return False

    def listar_medicos_receitas(self):
        """Método temporário para depuração."""
        print("listar_medicos() foi chamado")
        try:
            # Tenta listar os médicos do banco
          
            self.cursor.execute("SELECT id, nome FROM medicos WHERE ORDER BY nome")
            resultado = self.cursor.fetchall()
           
            return resultado
        except Exception as e:
            print(f"Erro em listar_medicos: {str(e)}")
            return []

    def atualizar_receita(self, receita_id: int, dados: dict) -> bool:
        """Atualiza uma receita existente.
        
        Args:
            receita_id: ID da receita a ser atualizada
            dados: Dicionário com os campos a serem atualizados (nome, texto, medico_id)
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not self.db:
            return False
            
        try:
            cursor = self.db.cursor()
            
            # Monta a query dinamicamente com base nos campos fornecidos
            set_clause = ', '.join([f"{campo} = %s" for campo in dados.keys()])
            valores = list(dados.values())
            valores.append(receita_id)  # Adiciona o ID para o WHERE
            
            query = f"UPDATE receitas SET {set_clause} WHERE id = %s"
            
            cursor.execute(query, valores)
            self.db.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao atualizar receita: {e}")
            self.db.rollback()
            return False


    def criar_exame_consulta(self, medico_id: int, nome: str, tempo: int) -> Optional[int]:
        """Cria um novo exame/consulta.
        
        Args:
            medico_id: ID do médico
            nome: Nome do exame/consulta
            tempo: Tempo em minutos
            
        Returns:
            int: ID do exame/consulta criado ou None em caso de erro
        """
        if not self.db:
            return None
            
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO exames_consultas (medico_id, nome, tempo) VALUES (%s, %s, %s)",
                (medico_id, nome, tempo)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao criar exame/consulta: {e}")
            self.db.rollback()
            return None

    def listar_exames_consultas_por_medico(self, medico_id: int) -> List[Dict[str, Any]]:
        """Lista todos os exames/consultas de um médico.
        
        Args:
            medico_id: ID do médico
            
        Returns:
            List[Dict]: Lista de exames/consultas
        """
        if not self.db:
            return []
            
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, medico_id, nome, tempo 
                FROM exames_consultas 
                WHERE medico_id = %s 
                ORDER BY nome
            """, (medico_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar exames/consultas: {e}")
            return []

    def atualizar_exame_consulta(self, exame_id: int, dados: dict) -> bool:
        """Atualiza um exame/consulta existente.
        
        Args:
            exame_id: ID do exame/consulta
            dados: Dicionário com os campos a serem atualizados (nome, tempo)
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        if not self.db or not dados:
            return False
            
        try:
            cursor = self.db.cursor()
            
            # Monta a query dinamicamente
            set_clause = ', '.join([f"{campo} = %s" for campo in dados.keys()])
            valores = list(dados.values())
            valores.append(exame_id)  # Adiciona o ID para o WHERE
            
            query = f"UPDATE exames_consultas SET {set_clause} WHERE id = %s"
            
            cursor.execute(query, valores)
            self.db.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Erro ao atualizar exame/consulta: {e}")
            self.db.rollback()
            return False

    def excluir_exame_consulta(self, exame_id: int) -> bool:
        """Exclui um exame/consulta.
        
        Args:
            exame_id: ID do exame/consulta a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        if not self.db:
            return False
            
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM exames_consultas WHERE id = %s", (exame_id,))
            self.db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir exame/consulta: {e}")
            self.db.rollback()
            return False