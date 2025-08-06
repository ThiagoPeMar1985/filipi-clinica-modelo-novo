from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class CadastroDB:
    """Classe para operações de banco de dados do módulo de Cadastro."""
    
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
    
    # ===== MÉTODOS PARA MÉDICOS =====
    def obter_medico_por_id(self, medico_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um médico pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicos WHERE id = %s", (medico_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter médico: {e}")
            return None
    
    def listar_medicos(self) -> List[Dict[str, Any]]:
        """Lista todos os médicos cadastrados."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicos ORDER BY nome")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar médicos: {e}")
            return []
    
    def salvar_medico(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Salva ou atualiza um médico.
        
        Args:
            dados: Dicionário com os dados do médico
                - id (opcional): ID do médico para atualização
                - nome: Nome completo do médico (obrigatório)
                - especialidade: Especialidade médica (obrigatório)
                - crm: Número do CRM (obrigatório, apenas números)
                - telefone: Telefone do médico (obrigatório)
                - email: E-mail do médico (opcional)
                
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            cursor = self.db.cursor()
            
            # Validações
            campos_obrigatorios = ['nome', 'especialidade', 'crm', 'telefone']
            for campo in campos_obrigatorios:
                if campo not in dados or not str(dados[campo]).strip():
                    return False, f"O campo {campo} é obrigatório"
            
            # Formatação dos dados
            nome = str(dados['nome']).strip()
            especialidade = str(dados['especialidade']).strip()
            crm = ''.join(filter(str.isdigit, str(dados['crm'])))
            telefone = ''.join(filter(str.isdigit, str(dados['telefone'])))
            email = str(dados.get('email', '')).strip() or None
            
            # Validação do CRM (apenas números, mínimo 4 dígitos)
            if not crm or len(crm) < 4:
                return False, "CRM inválido. Deve conter no mínimo 4 dígitos."
                
            # Validação do telefone (apenas números, mínimo 10 dígitos)
            if len(telefone) < 10:
                return False, "Telefone inválido. Deve conter DDD + número."
            
            # Validação de e-mail se fornecido
            if email and '@' not in email:
                return False, "E-mail inválido"
            
            if 'id' in dados and dados['id']:
                # Atualização
                query = """
                    UPDATE medicos 
                    SET nome = %s, especialidade = %s, crm = %s, 
                        telefone = %s, email = %s
                    WHERE id = %s
                """
                valores = (
                    nome,
                    especialidade,
                    crm,
                    telefone,
                    email,
                    int(dados['id'])
                )
                acao = "atualizado"
            else:
                # Inserção
                query = """
                    INSERT INTO medicos 
                    (nome, especialidade, crm, telefone, email, data_cadastro)
                    VALUES (%s, %s, %s, %s, %s, CURDATE())
                """
                valores = (
                    nome,
                    especialidade,
                    crm,
                    telefone,
                    email
                )
                acao = "cadastrado"
            
            cursor.execute(query, valores)
            self.db.commit()
            return True, f"Médico {acao} com sucesso!"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao salvar médico: {str(e)}"
    
    def excluir_medico(self, medico_id: int) -> Tuple[bool, str]:
        """Exclui um médico pelo ID."""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM medicos WHERE id = %s", (medico_id,))
            self.db.commit()
            return True, "Médico excluído com sucesso!"
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao excluir médico: {str(e)}"


    # ===== MÉTODOS PARA USUÁRIOS =====
    def obter_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um usuário pelo ID."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter usuário: {e}")
            return None
    
    def listar_usuarios(self) -> List[Dict[str, Any]]:
        """Lista todos os usuários cadastrados."""
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios ORDER BY nome")
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
    
    def salvar_usuario(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva ou atualiza um usuário."""
        try:
            cursor = self.db.cursor()
            
            campos_obrigatorios = ['nome', 'login', 'senha', 'nivel']
            for campo in campos_obrigatorios:
                if campo not in dados or not dados[campo]:
                    return False, f"O campo {campo} é obrigatório"
            
            if 'id' in dados and dados['id']:
                # Atualização
                query = """
                    UPDATE usuarios 
                    SET nome = %s, login = %s, senha = %s, 
                        nivel = %s, telefone = %s
                    WHERE id = %s
                """
                valores = (
                    dados['nome'],
                    dados['login'],
                    dados['senha'],
                    dados['nivel'],
                    dados['telefone'],
                    dados['id']
                )
            else:
                # Inserção
                query = """
                    INSERT INTO usuarios 
                    (nome, login, senha, nivel, telefone)
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

    # ===== MÉTODOS PARA EMPRESA =====
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
