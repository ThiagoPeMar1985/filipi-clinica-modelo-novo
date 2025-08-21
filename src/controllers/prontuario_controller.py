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
    
    def _execute_query(self, query: str, params=(), fetch_all: bool = True):
        """Executa query com wrapper (execute_query) ou conexão nativa (cursor dictionary=True).
        SELECT retorna lista de dicts (fetch_all=True) ou um dict (fetch_all=False).
        INSERT/UPDATE/DELETE com conexão nativa fazem commit e retornam lastrowid/True.
        """
        if not self.db:
            return [] if fetch_all else None
        if hasattr(self.db, 'execute_query') and callable(getattr(self.db, 'execute_query')):
            return self.db.execute_query(query, params, fetch_all=fetch_all)
        cursor = None
        try:
            cursor = self.db.cursor(dictionary=True)
            cursor.execute(query, params or ())
            lower = query.strip().lower()
            is_select = lower.startswith('select')
            if is_select:
                return cursor.fetchall() if fetch_all else cursor.fetchone()
            self.db.commit()
            try:
                return cursor.lastrowid if hasattr(cursor, 'lastrowid') else True
            except Exception:
                return True
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass
    
    def buscar_prontuarios_paciente(self, paciente_id: int) -> List[Dict[str, Any]]:
        """
        Busca todos os prontuários de um paciente.
        
        Args:
            paciente_id: ID do paciente.
            
        Returns:
            Lista de prontuários do paciente.
        """
        query = """
            SELECT 
                p.id,
                p.paciente_id,
                p.consulta_id,
                p.titulo,
                p.conteudo,
                p.data,
                p.usuario_id,
                pa.nome AS nome,                 -- nome do paciente
                u.nome AS nome_medico,           -- nome do médico (do usuário)
                p.data AS data_criacao,          -- data do exame
                p.paciente_id AS data_atualizacao -- substitui por paciente_id conforme solicitado
            FROM prontuarios p
            LEFT JOIN usuarios u ON u.id = p.usuario_id
            LEFT JOIN pacientes pa ON p.paciente_id = pa.id
            WHERE p.paciente_id = %s
            ORDER BY p.data DESC
        """
        try:
            return self._execute_query(query, (paciente_id,)) or []
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
            SELECT 
                p.id,
                p.paciente_id,
                p.consulta_id,
                p.titulo,
                p.conteudo,
                p.data,
                p.usuario_id,
                pa.nome AS nome,                 -- nome do paciente
                u.nome AS nome_medico,           -- nome do médico (do usuário)
                p.data AS data_criacao,          -- data do exame
                p.paciente_id AS data_atualizacao -- substitui por paciente_id conforme solicitado
            FROM prontuarios p
            LEFT JOIN usuarios u ON u.id = p.usuario_id
            LEFT JOIN pacientes pa ON p.paciente_id = pa.id
            WHERE p.id = %s
        """
        try:
            return self._execute_query(query, (prontuario_id,), fetch_all=False)
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
        # Verificar campos obrigatórios (agora usando usuario_id do médico)
        campos_obrigatorios = ['paciente_id', 'usuario_id', 'conteudo']
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return False, f"O campo {campo} é obrigatório."
        
        # Adicionar data (somente data, conforme schema) se não existir
        if 'data' not in dados:
            dados['data'] = datetime.now().strftime('%Y-%m-%d')
        
        # Inserir no banco de dados
        campos = ', '.join(dados.keys())
        placeholders = ', '.join(['%s'] * len(dados))
        
        query = f"""
            INSERT INTO prontuarios ({campos})
            VALUES ({placeholders})
        """
        
        try:
            resultado = self._execute_query(query, list(dados.values()))
            # Se conexão nativa, resultado é lastrowid (int/bool). Se wrapper, pode ser dict
            if isinstance(resultado, dict):
                return True, resultado.get('lastrowid', 0)
            return True, (int(resultado) if isinstance(resultado, (int,)) else 0)
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
            self._execute_query(query, tuple(valores))
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
            self._execute_query(query, (prontuario_id,))
            return True, "Prontuário excluído com sucesso."
        except Exception as e:
            print(f"Erro ao excluir prontuário: {e}")
            return False, f"Erro ao excluir prontuário: {str(e)}"
    
    # Métodos para gerenciamento de modelos de texto
    
    def listar_modelos_texto(self, usuario_id: int) -> List[Dict[str, Any]]:
        """
        Lista todos os modelos de texto de um usuário (médico) pelo usuario_id.
        """
        query = """
            SELECT id, nome, conteudo, data_criacao, data_atualizacao
            FROM modelos_texto
            WHERE usuario_id = %s
            ORDER BY nome
        """
        try:
            if hasattr(self.db, 'cursor'):
                cursor = self.db.cursor(dictionary=True)
                cursor.execute(query, (usuario_id,))
                return cursor.fetchall()
            # Fallback API
            return self.db.execute_query(query, (usuario_id,))
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
            SELECT id, nome, conteudo, data_criacao, data_atualizacao, usuario_id
            FROM modelos_texto
            WHERE id = %s
        """
        try:
            if hasattr(self.db, 'cursor'):
                cursor = self.db.cursor(dictionary=True)
                cursor.execute(query, (modelo_id,))
                resultado = cursor.fetchone()
                cursor.close()
                return resultado
            # Fallback API
            return self.db.execute_query(query, (modelo_id,), fetch_all=False)
        except Exception as e:
            print(f"Erro ao buscar modelo de texto: {e}")
            if 'cursor' in locals():
                cursor.close()
            return None

    def criar_modelo_texto(self, dados: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """
        Cria um novo modelo de texto.
        Exclusivamente com usuario_id (sem compatibilidade com medico_id).
        """
        campos_obrigatorios = ['nome', 'conteudo', 'usuario_id']
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
            if hasattr(self.db, 'cursor'):
                cursor = self.db.cursor()
                cursor.execute(query, valores)
                modelo_id = cursor.lastrowid
                self.db.commit()
                cursor.close()
                return True, modelo_id
            # Fallback API
            resultado = self.db.execute_query(query, valores)
            return True, (resultado.get('lastrowid', 0) if isinstance(resultado, dict) else 0)
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
            if hasattr(self.db, 'cursor'):
                cursor = self.db.cursor()
                cursor.execute(query, tuple(valores))
                self.db.commit()
                cursor.close()
                return True, "Modelo atualizado com sucesso"
            # Fallback API
            self.db.execute_query(query, tuple(valores))
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
            if hasattr(self.db, 'cursor'):
                cursor = self.db.cursor()
                cursor.execute(query, (modelo_id,))
                self.db.commit()
                cursor.close()
                return True, "Modelo excluído com sucesso"
            # Fallback API
            self.db.execute_query(query, (modelo_id,))
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
        # Alguns bancos não possuem coluna usuario_id em medicos.
        # Passamos a listar pelos usuários que possuem modelos (criadores dos modelos),
        # mantendo a ideia de "médicos com modelos".
        query = """
            SELECT DISTINCT u.id AS usuario_id, u.nome AS nome
            FROM usuarios u
            INNER JOIN modelos_texto mt ON u.id = mt.usuario_id
            ORDER BY u.nome
        """
        try:
            return self._execute_query(query) or []
        except Exception as e:
            print(f"Erro ao listar médicos com modelos: {e}")
            return []
