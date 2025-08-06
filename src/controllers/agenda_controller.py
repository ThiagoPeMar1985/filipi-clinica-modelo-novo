"""
Controlador para operações relacionadas à agenda de consultas.
"""
from typing import List, Dict, Optional, Tuple, Any

class AgendaController:
    """Controlador para operações da agenda de consultas."""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
    
    def buscar_consultas(self, filtro_medico: Optional[str] = None, 
                        data_inicio: Optional[str] = None, 
                        data_fim: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca consultas com filtros opcionais."""
        try:
            if not self.db_connection:
                raise Exception("Sem conexão com o banco de dados")
                
            cursor = self.db_connection.cursor()
            
            query = """
                SELECT c.id, c.data as data_consulta, c.hora as hora_consulta, 
                       p.nome as paciente_nome, m.nome as medico_nome,
                       c.status
                FROM consultas c
                INNER JOIN pacientes p ON c.paciente_id = p.id
                INNER JOIN medicos m ON c.medico_id = m.id
                WHERE 1=1
            """
            params = []
            
            if filtro_medico and filtro_medico != "Todos":
                query += " AND m.nome = %s"
                params.append(filtro_medico)
                
            if data_inicio:
                query += " AND c.data >= %s"
                params.append(data_inicio)
                
            if data_fim:
                query += " AND c.data <= %s"
                params.append(data_fim)
                
            query += " ORDER BY c.data, c.hora"
            
            cursor.execute(query, tuple(params))
            
            colunas = [column[0] for column in cursor.description]
            return [dict(zip(colunas, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            raise Exception(f"Erro ao buscar consultas: {str(e)}")
            
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def buscar_medicos(self) -> List[Dict[str, Any]]:
        """Busca todos os médicos."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT id, nome, crm, especialidade FROM medicos ORDER BY nome")
            return [dict(zip(['id', 'nome', 'crm', 'especialidade'], row)) 
                   for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Erro ao buscar médicos: {str(e)}")
        finally:
            cursor.close() if 'cursor' in locals() else None
    
    def salvar_consulta(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Salva ou atualiza uma consulta."""
        try:
            cursor = self.db_connection.cursor()
            
            if dados.get('id'):
                # Atualizar
                query = """
                    UPDATE consultas 
                    SET paciente_id = %s, medico_id = %s, 
                        data = %s, hora = %s, status = %s, 
                        observacoes = %s
                    WHERE id = %s
                """
                params = (
                    dados['paciente_id'], dados['medico_id'],
                    dados['data'], dados['hora'],
                    dados.get('status', 'Agendado'),
                    dados.get('observacoes', ''),
                    dados['id']
                )
            else:
                # Inserir
                query = """
                    INSERT INTO consultas 
                    (paciente_id, medico_id, data, hora, status, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (
                    dados['paciente_id'], dados['medico_id'],
                    dados['data'], dados['hora'],
                    dados.get('status', 'Agendado'),
                    dados.get('observacoes', '')
                )
            
            cursor.execute(query, params)
            self.db_connection.commit()
            return True, "Consulta salva com sucesso!"
            
        except Exception as e:
            self.db_connection.rollback()
            return False, f"Erro ao salvar consulta: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def atualizar_consulta(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza uma consulta existente.
        
        Args:
            dados: Dicionário com os dados da consulta a ser atualizada.
                Deve conter: id, paciente_id, medico_id, data, hora, status, observacoes
        
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            if not self.db_connection:
                raise Exception("Sem conexão com o banco de dados")
            
            cursor = self.db_connection.cursor()
            
            # Verificar se a consulta existe
            cursor.execute("SELECT id FROM consultas WHERE id = %s", (dados['id'],))
            if not cursor.fetchone():
                return False, "Consulta não encontrada"
            
            # Atualizar a consulta
            query = """
                UPDATE consultas 
                SET paciente_id = %s, 
                    medico_id = %s, 
                    data = %s, 
                    hora = %s, 
                    status = %s, 
                    observacoes = %s
                WHERE id = %s
            """
            params = (
                dados['paciente_id'],
                dados['medico_id'],
                dados['data'],
                dados['hora'],
                dados['status'],
                dados.get('observacoes', ''),
                dados['id']
            )
            
            cursor.execute(query, params)
            self.db_connection.commit()
            return True, "Consulta atualizada com sucesso!"
            
        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Erro ao atualizar consulta: {str(e)}"
            
        finally:
            if 'cursor' in locals():
                cursor.close()
                
    def excluir_consulta(self, consulta_id):
        """Exclui uma consulta pelo ID"""
        try:
            if not self.db_connection:
                return False, "Sem conexão com o banco de dados"
            
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM consultas WHERE id = %s", (consulta_id,))
            self.db_connection.commit()
            return True, "Consulta excluída com sucesso"
        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            return False, f"Erro ao excluir consulta: {str(e)}"
        finally:
            if 'cursor' in locals():
                cursor.close()