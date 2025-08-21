from datetime import datetime, time, timedelta

class HorarioController:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.db = db_connection  # Referência alternativa para compatibilidade

    def salvar_horario(self, medico_id, dia_semana, hora_inicio, hora_fim):
        try:
            cursor = self.db_connection.cursor()
            query = """
                INSERT INTO horarios_disponiveis 
                (medico_id, dia_semana, hora_inicio, hora_fim)
                VALUES (%s, %s, %s, %s) AS new
                ON DUPLICATE KEY UPDATE
                hora_fim = new.hora_fim
            """
            cursor.execute(query, (medico_id, dia_semana, hora_inicio, hora_fim))
            self.db_connection.commit()
            return True, "Horário salvo com sucesso!"
        except Exception as e:
            self.db_connection.rollback()
            return False, f"Erro ao salvar horário: {str(e)}"
        finally:
            cursor.close()

    def remover_horario(self, horario_id):
        """Remove um horário pelo ID"""
        try:
            cursor = self.db_connection.cursor()
            query = """
                DELETE FROM horarios_disponiveis 
                WHERE id = %s
            """
            cursor.execute(query, (horario_id,))
            self.db_connection.commit()
            return True, "Horário removido com sucesso!"
        except Exception as e:
            self.db_connection.rollback()
            return False, f"Erro ao remover horário: {str(e)}"
        finally:
            cursor.close()

    def listar_horarios_medico(self, medico_id, dia_semana=None):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT * FROM horarios_disponiveis 
                WHERE medico_id = %s 
            """
            params = [medico_id]
            
            if dia_semana is not None:
                query += " AND dia_semana = %s"
                params.append(dia_semana)
                
            query += " ORDER BY dia_semana, hora_inicio"
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Erro ao listar horários: {str(e)}")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()

    def verificar_disponibilidade(self, medico_id, data, hora_consulta, duracao_minutos):
        cursor = None
        try:
            # Converter para objeto time
            if isinstance(hora_consulta, str):
                hora_consulta = datetime.strptime(hora_consulta, '%H:%M').time()
            
            hora_fim = (datetime.combine(datetime.today(), hora_consulta) + 
                    timedelta(minutes=duracao_minutos)).time()
            
            # Obter dia da semana (0=segunda, 6=domingo)
            if isinstance(data, str):
                data = datetime.strptime(data, '%Y-%m-%d').date()
            dia_semana = data.weekday()  # 0=segunda, 6=domingo
            
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT * FROM horarios_disponiveis 
                WHERE medico_id = %s 
                AND dia_semana = %s
                AND hora_inicio <= %s
                AND hora_fim >= %s
            """
            cursor.execute(query, (medico_id, dia_semana, 
                                hora_consulta.strftime('%H:%M'),
                                hora_fim.strftime('%H:%M')))
            
            return cursor.fetchone() is not None
        except Exception as e:
            raise Exception(f"Erro ao verificar disponibilidade: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def obter_dias_atendimento(self, medico_id):
        """Retorna os dias da semana (0-6) em que o médico atende"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT DISTINCT dia_semana 
                FROM horarios_disponiveis 
                WHERE medico_id = %s
                ORDER BY dia_semana
            """, (medico_id,))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao obter dias de atendimento: {e}")
            return []
        finally:
            cursor.close()

    def obter_horarios_disponiveis(self, medico_id, dia_semana):
        """
        Retorna os horários disponíveis para um médico em um determinado dia da semana
        
        Args:
            medico_id: ID do médico
            dia_semana: Dia da semana (0=segunda, 1=terça, ..., 6=domingo)
            
        Returns:
            Lista de dicionários com os horários disponíveis, cada um contendo:
            - id: ID do horário
            - hora_inicio: Objeto time com a hora de início
            - hora_fim: Objeto time com a hora de fim
        """
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            query = """
                SELECT id, hora_inicio, hora_fim
                FROM horarios_disponiveis 
                WHERE medico_id = %s 
                AND dia_semana = %s
                ORDER BY hora_inicio
            """
            cursor.execute(query, (medico_id, dia_semana))
            
            # Converte as strings de hora para objetos time
            resultados = cursor.fetchall()
            for resultado in resultados:
                if isinstance(resultado['hora_inicio'], str):
                    resultado['hora_inicio'] = datetime.strptime(resultado['hora_inicio'], '%H:%M:%S').time()
                if isinstance(resultado['hora_fim'], str):
                    resultado['hora_fim'] = datetime.strptime(resultado['hora_fim'], '%H:%M:%S').time()
            
            return resultados
        except Exception as e:
            print(f"Erro ao obter horários disponíveis: {e}")
            return []
        finally:
            cursor.close()