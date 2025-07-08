"""
Controlador para gerenciamento de entregadores.
"""
from typing import List, Dict, Any, Optional, Tuple
from mysql.connector import Error

class EntregadorController:
    """Controlador para operações relacionadas a entregadores."""
    
    def __init__(self, db_connection):
        """
        Inicializa o controlador com uma conexão de banco de dados.
        
        Args:
            db_connection: Conexão ativa com o banco de dados MySQL.
        """
        self.db = db_connection
    
    def listar_entregadores(self, apenas_ativos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista todos os entregadores cadastrados.
        
        Args:
            apenas_ativos: Se True, retorna apenas entregadores ativos.
            
        Returns:
            Lista de dicionários contendo os dados dos entregadores.
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            
            query = "SELECT * FROM entregadores"
            params = ()
            
            if apenas_ativos:
                query += " WHERE ativo = %s"
                params = (1,)
                
            query += " ORDER BY nome"
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Error as e:
            print(f"Erro ao listar entregadores: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def buscar_entregador_por_id(self, entregador_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca um entregador pelo ID.
        
        Args:
            entregador_id: ID do entregador a ser buscado.
            
        Returns:
            Dicionário com os dados do entregador ou None se não encontrado.
        """
        try:
            cursor = self.db.cursor(dictionary=True)
            query = "SELECT * FROM entregadores WHERE id = %s"
            cursor.execute(query, (entregador_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Erro ao buscar entregador: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def adicionar_entregador(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Adiciona um novo entregador.
        
        Args:
            dados: Dicionário com os dados do entregador (nome, telefone, veiculo, placa).
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        try:
            cursor = self.db.cursor()
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['nome', 'telefone', 'veiculo', 'placa']
            for campo in campos_obrigatorios:
                if not dados.get(campo):
                    return False, f"O campo {campo} é obrigatório."
            
            # Inserir novo entregador
            query = """
                INSERT INTO entregadores (nome, telefone, veiculo, placa, ativo)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            valores = (
                dados['nome'],
                dados['telefone'],
                dados['veiculo'],
                dados['placa'],
                1  # Por padrão, novo entregador é ativado
            )
            
            cursor.execute(query, valores)
            self.db.commit()
            
            return True, "Entregador cadastrado com sucesso!"
            
        except Error as e:
            self.db.rollback()
            return False, f"Erro ao cadastrar entregador: {e}"
        finally:
            if cursor:
                cursor.close()
    
    def atualizar_entregador(self, entregador_id: int, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza os dados de um entregador existente.
        
        Args:
            entregador_id: ID do entregador a ser atualizado.
            dados: Dicionário com os dados a serem atualizados.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        try:
            cursor = self.db.cursor()
            
            # Verificar se o entregador existe
            if not self.buscar_entregador_por_id(entregador_id):
                return False, "Entregador não encontrado."
            
            # Construir a query de atualização dinamicamente
            campos = []
            valores = []
            
            for campo, valor in dados.items():
                if campo in ['nome', 'telefone', 'veiculo', 'placa', 'ativo']:
                    campos.append(f"{campo} = %s")
                    valores.append(valor)
            
            if not campos:
                return False, "Nenhum dado válido para atualização."
            
            # Adicionar o ID no final para a cláusula WHERE
            valores.append(entregador_id)
            
            query = f"""
                UPDATE entregadores
                SET {', '.join(campos)}
                WHERE id = %s
            """
            
            cursor.execute(query, valores)
            self.db.commit()
            
            return True, "Entregador atualizado com sucesso!"
            
        except Error as e:
            self.db.rollback()
            return False, f"Erro ao atualizar entregador: {e}"
        finally:
            if cursor:
                cursor.close()
    
    def remover_entregador(self, entregador_id: int) -> Tuple[bool, str]:
        """
        Remove um entregador do sistema (remoção lógica).
        
        Args:
            entregador_id: ID do entregador a ser removido.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        try:
            cursor = self.db.cursor()
            
            # Verificar se o entregador existe
            if not self.buscar_entregador_por_id(entregador_id):
                return False, "Entregador não encontrado."
            
            # Verificar se o entregador está associado a algum pedido
            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE entregador_id = %s", (entregador_id,))
            if cursor.fetchone()[0] > 0:
                # Em vez de remover, desativa o entregador
                query = "UPDATE entregadores SET ativo = 0 WHERE id = %s"
                cursor.execute(query, (entregador_id,))
                self.db.commit()
                return True, "Entregador desativado com sucesso, pois possui pedidos associados."
            
            # Se não houver pedidos associados, remove fisicamente
            query = "DELETE FROM entregadores WHERE id = %s"
            cursor.execute(query, (entregador_id,))
            self.db.commit()
            
            return True, "Entregador removido com sucesso!"
            
        except Error as e:
            self.db.rollback()
            return False, f"Erro ao remover entregador: {e}"
        finally:
            if cursor:
                cursor.close()
