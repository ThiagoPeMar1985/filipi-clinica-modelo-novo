"""
Controlador para operações relacionadas a prontuários e modelos de texto.
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

class ProntuarioController:
    """Controlador para operações relacionadas a prontuários e modelos de texto."""
    
    def __init__(self):
        """Inicializa o controlador de prontuários."""
        from src.db.database import db
        self.db = db

    def set_db_connection(self, db_connection):
        """
        Define a conexão com o banco de dados.
        
        Args:
            db_connection: Conexão com o banco de dados.
        """
        self.db = db_connection
    
    def buscar_prontuarios_paciente(self, paciente_id: int) -> List[Dict[str, Any]]:
        """
        Busca todos os prontuários de um paciente.
        
        Args:
            paciente_id: ID do paciente.
            
        Returns:
            Lista de prontuários do paciente.
        """
        query = """
            SELECT p.*, m.nome as nome_medico
            FROM prontuarios p
            LEFT JOIN medicos m ON p.medico_id = m.id
            WHERE p.paciente_id = %s
            ORDER BY p.data DESC
        """
        try:
            return self.db.execute_query(query, (paciente_id,))
        except Exception as e:
            print(f"Erro ao buscar prontuários do paciente: {e}")
            return []
    
    def buscar_prontuario_por_id(self, prontuario_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um prontuário pelo ID.
        
        Args:
            prontuario_id: ID do prontuário.
            
        Returns:
            Dicionário com os dados do prontuário ou None se não encontrado.
        """
        query = """
            SELECT p.*, m.nome as nome_medico, pa.nome as nome_paciente
            FROM prontuarios p
            LEFT JOIN medicos m ON p.medico_id = m.id
            LEFT JOIN pacientes pa ON p.paciente_id = pa.id
            WHERE p.id = %s
        """
        try:
            return self.db.execute_query(query, (prontuario_id,), fetch_all=False)
        except Exception as e:
            print(f"Erro ao buscar prontuário por ID: {e}")
            return None
    
    def criar_prontuario(self, dados: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """
        Cria um novo prontuário.
        
        Args:
            dados: Dicionário com os dados do prontuário.
            
        Returns:
            Tupla (sucesso, id_prontuario ou mensagem de erro).
        """
        # Verificar campos obrigatórios
        campos_obrigatorios = ['paciente_id', 'medico_id', 'conteudo']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return False, f"O campo {campo} é obrigatório."
        
        # Adicionar data de criação se não existir
        if 'data' not in dados:
            dados['data'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Inserir no banco de dados
        campos = ', '.join(dados.keys())
        placeholders = ', '.join(['%s'] * len(dados))
        
        query = f"""
            INSERT INTO prontuarios ({campos})
            VALUES ({placeholders})
        """
        
        try:
            resultado = self.db.execute_query(query, list(dados.values()))
            return True, resultado.get('lastrowid', 0)
        except Exception as e:
            print(f"Erro ao criar prontuário: {e}")
            return False, f"Erro ao criar prontuário: {str(e)}"
    
    def atualizar_prontuario(self, prontuario_id: int, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza um prontuário existente.
        
        Args:
            prontuario_id: ID do prontuário a ser atualizado.
            dados: Dicionário com os dados atualizados.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        if not dados:
            return False, "Nenhum dado para atualizar."
        
        # Adicionar data de atualização
        dados['data_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Preparar os pares campo=valor para a atualização
        sets = []
        valores = []
        
        for campo, valor in dados.items():
            if campo != 'id':  # Não atualizar o ID
                sets.append(f"{campo} = %s")
                valores.append(valor)
        
        if not sets:
            return False, "Nenhum campo válido para atualização."
        
        # Adicionar o ID aos valores para a cláusula WHERE
        valores.append(prontuario_id)
        
        query = f"""
            UPDATE prontuarios
            SET {', '.join(sets)}
            WHERE id = %s
        """
        
        try:
            self.db.execute_query(query, tuple(valores))
            return True, "Prontuário atualizado com sucesso."
        except Exception as e:
            print(f"Erro ao atualizar prontuário: {e}")
            return False, f"Erro ao atualizar prontuário: {str(e)}"
    
    def excluir_prontuario(self, prontuario_id: int) -> Tuple[bool, str]:
        """
        Exclui um prontuário.
        
        Args:
            prontuario_id: ID do prontuário a ser excluído.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        query = "DELETE FROM prontuarios WHERE id = %s"
        
        try:
            self.db.execute_query(query, (prontuario_id,))
            return True, "Prontuário excluído com sucesso."
        except Exception as e:
            print(f"Erro ao excluir prontuário: {e}")
            return False, f"Erro ao excluir prontuário: {str(e)}"
    
    # Métodos para gerenciamento de modelos de texto
    
    def listar_modelos_texto(self, medico_id: int) -> List[Dict[str, Any]]:
        """
        Lista todos os modelos de texto de um médico.
        
        Args:
            medico_id: ID do médico.
            
        Returns:
            Lista de dicionários com os modelos de texto do médico.
        """
        query = """
            SELECT id, nome, conteudo, data_criacao, data_atualizacao
            FROM modelos_texto
            WHERE medico_id = %s
            ORDER BY nome
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute(query, (medico_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar modelos de texto: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    def buscar_modelo_por_id(self, modelo_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um modelo de texto pelo ID.
        
        Args:
            modelo_id: ID do modelo.
            
        Returns:
            Dicionário com os dados do modelo ou None se não encontrado.
        """
        query = """
            SELECT id, nome, conteudo, data_criacao, data_atualizacao, medico_id
            FROM modelos_texto
            WHERE id = %s
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute(query, (modelo_id,))
            resultado = cursor.fetchone()
            cursor.close()
            return resultado
        except Exception as e:
            print(f"Erro ao buscar modelo de texto: {e}")
            if 'cursor' in locals():
                cursor.close()
            return None

    def criar_modelo_texto(self, dados: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """
        Cria um novo modelo de texto.
        
        Args:
            dados: Dicionário com os dados do modelo.
                Deve conter: nome, conteudo, medico_id
                
        Returns:
            Tupla (sucesso, resultado) onde resultado é o ID do modelo ou mensagem de erro.
        """
        campos_obrigatorios = ['nome', 'conteudo', 'medico_id']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return False, f"O campo {campo} é obrigatório."
        
        # Adiciona a data de criação se não existir
        if 'data_criacao' not in dados:
            dados['data_criacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Prepara a query de inserção
        campos = ', '.join(dados.keys())
        placeholders = ', '.join(['%s'] * len(dados))
        valores = tuple(dados.values())
        
        query = f"""
            INSERT INTO modelos_texto ({campos})
            VALUES ({placeholders})
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, valores)
            modelo_id = cursor.lastrowid  # Obtém o ID do registro inserido
            self.db.commit()  # Confirma a transação
            cursor.close()
            return True, modelo_id
        except Exception as e:
            print(f"Erro ao criar modelo de texto: {e}")
            if 'cursor' in locals():
                cursor.close()
            return False, str(e)

    def atualizar_modelo_texto(self, modelo_id: int, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza um modelo de texto existente.
        
        Args:
            modelo_id: ID do modelo a ser atualizado.
            dados: Dicionário com os campos a serem atualizados.
                Pode conter: nome, conteudo
                
        Returns:
            Tupla (sucesso, mensagem)
        """
        if not dados:
            return False, "Nenhum dado para atualizar"
            
        # Adiciona a data de atualização
        dados['data_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Prepara a query de atualização
        sets = [f"{campo} = %s" for campo in dados.keys()]
        valores = list(dados.values())
        valores.append(modelo_id)
        
        query = f"""
            UPDATE modelos_texto
            SET {', '.join(sets)}
            WHERE id = %s
        """
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, tuple(valores))
            self.db.commit()  # Confirma a transação
            cursor.close()
            return True, "Modelo atualizado com sucesso"
        except Exception as e:
            print(f"Erro ao atualizar modelo de texto: {e}")
            if 'cursor' in locals():
                cursor.close()
            return False, str(e)

    def excluir_modelo_texto(self, modelo_id: int) -> Tuple[bool, str]:
        """
        Exclui um modelo de texto.
        
        Args:
            modelo_id: ID do modelo a ser excluído.
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        query = "DELETE FROM modelos_texto WHERE id = %s"
        
        try:
            cursor = self.db.cursor()
            cursor.execute(query, (modelo_id,))
            self.db.commit()  # Confirma a transação
            cursor.close()
            return True, "Modelo excluído com sucesso"
        except Exception as e:
            print(f"Erro ao excluir modelo de texto: {e}")
            if 'cursor' in locals():
                cursor.close()
            return False, str(e)

    def listar_medicos_com_modelos(self) -> List[Dict[str, Any]]:
        """
        Lista todos os médicos que possuem modelos de texto cadastrados.
        
        Returns:
            Lista de dicionários com os dados dos médicos.
        """
        query = """
            SELECT DISTINCT m.id, m.nome, m.crm, m.especialidade
            FROM medicos m
            INNER JOIN modelos_texto mt ON m.id = mt.medico_id
            ORDER BY m.nome
        """
        try:
            return self.db.execute_query(query)
        except Exception as e:
            print(f"Erro ao listar médicos com modelos: {e}")
            return []
