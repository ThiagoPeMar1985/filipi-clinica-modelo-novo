"""
Controlador para operações relacionadas a clientes.
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

class ClienteController:
    """Controlador para operações relacionadas a pacientes."""
    
    def __init__(self):
        """Inicializa o controlador de pacientes."""
        from src.db.database import db
        self.db = db
    
    def buscar_cliente_por_id(self, cliente_id: int) -> tuple[bool, dict]:
        """
        Busca um cliente pelo ID.
        
        Args:
            cliente_id: ID do cliente a ser buscado.
            
        Returns:
            Tupla (sucesso, dados_do_cliente).
            Se o cliente não for encontrado, retorna (False, None).
        """
        query = """
            SELECT 
                id, nome, data_nascimento, cpf, telefone, telefone2, email, 
                endereco, numero, complemento, bairro, 
                cidade, uf, cep, ponto_referencia, observacoes, regiao_entrega_id
            FROM pacientes
            WHERE id = %s
        """
        
        try:
            resultado = self.db.execute_query(query, (cliente_id,), fetch_all=False)
            
            if resultado:
                # Formatar a data para exibição (DD/MM/YYYY)
                if resultado.get('data_nascimento'):
                    # Se a data já estiver no formato DD/MM/YYYY, não tenta converter
                    if isinstance(resultado['data_nascimento'], str) and '/' in resultado['data_nascimento']:
                        pass  # Já está no formato correto
                    else:
                        # Tenta converter de YYYY-MM-DD para DD/MM/YYYY
                        try:
                            from datetime import datetime
                            if isinstance(resultado['data_nascimento'], str):
                                data_obj = datetime.strptime(resultado['data_nascimento'], '%Y-%m-%d')
                            else:
                                data_obj = resultado['data_nascimento']
                            resultado['data_nascimento'] = data_obj.strftime('%d/%m/%Y')
                        except (ValueError, TypeError) as e:
                            print(f"Erro ao formatar data: {e}")
                            resultado['data_nascimento'] = None
                
                # Formatar CPF se existir
                if resultado.get('cpf'):
                    cpf = resultado['cpf']
                    if len(cpf) == 11:  # Formatar apenas se tiver 11 dígitos
                        resultado['cpf'] = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
                
                return True, resultado
            return False, None
            
        except Exception as e:
            print(f"Erro ao buscar cliente por ID: {e}")
            return False, None
            
    def buscar_cliente_por_telefone(self, telefone: str) -> List[Dict[str, Any]]:
        """
        Busca clientes pelo telefone (busca parcial).
        
        Args:
            telefone: Número de telefone ou parte dele para busca.
            
        Returns:
            Lista de dicionários com os dados dos clientes encontrados.
        """
        query = """
            SELECT * FROM pacientes 
            WHERE telefone LIKE %s OR telefone2 LIKE %s
            ORDER BY nome
        """
        try:
            # Adiciona % para busca parcial
            termo_busca = f"{telefone}%"
            resultados = self.db.execute_query(query, (termo_busca, termo_busca))
            return resultados if resultados else []
        except Exception as e:
            print(f"Erro ao buscar cliente por telefone: {e}")
            return []
    
    def buscar_cliente_por_nome(self, nome: str) -> List[Dict[str, Any]]:
        """
        Busca clientes pelo nome (busca parcial).
        
        Args:
            nome: Nome ou parte do nome do cliente.
            
        Returns:
            Lista de dicionários com os dados dos clientes encontrados.
        """
        query = """
            SELECT * FROM pacientes
            WHERE nome LIKE %s
            ORDER BY nome
            LIMIT 10
        """
        try:
            return self.db.execute_query(query, (f"%{nome}%",))
        except Exception as e:
            print(f"Erro ao buscar cliente por nome: {e}")
            return []
    
    def cadastrar_cliente(self, **dados):
        """
        Cadastra um novo cliente no banco de dados.
        
        Args:
            **dados: Dicionário com os dados do cliente.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        try:
            # Formatar a data de nascimento se existir
            if 'data_nascimento' in dados and dados['data_nascimento']:
                try:
                    # Converter de DD/MM/YYYY para YYYY-MM-DD
                    data_obj = datetime.strptime(dados['data_nascimento'], '%d/%m/%Y')
                    dados['data_nascimento'] = data_obj.strftime('%Y-%m-%d')
                except ValueError:
                    # Se a data estiver em formato inválido, remove para não causar erro no banco
                    dados['data_nascimento'] = None
            
            # Formatar CPF (remover pontos e traço)
            if 'cpf' in dados and dados['cpf']:
                cpf = ''.join(filter(str.isdigit, dados['cpf']))
                if len(cpf) != 11:  # CPF deve ter 11 dígitos
                    return False, "CPF inválido. Deve conter 11 dígitos."
                dados['cpf'] = cpf
            
            # Garantir que campos obrigatórios existam
            campos_obrigatorios = ['nome', 'telefone']
            for campo in campos_obrigatorios:
                if campo not in dados or not dados[campo]:
                    return False, f"O campo {campo} é obrigatório."
            
            # Inserir no banco de dados
            campos = ', '.join(dados.keys())
            placeholders = ', '.join(['%s'] * len(dados))
            
            query = f"""
                INSERT INTO pacientes ({campos})
                VALUES ({placeholders})
            """
            
            self.db.execute_query(query, list(dados.values()))
            return True, "Cliente cadastrado com sucesso."
            
        except Exception as e:
            print(f"Erro ao cadastrar cliente: {e}")
            return False, f"Erro ao cadastrar cliente: {str(e)}"
    
    def atualizar_cliente(self, cliente_id: int, dados_atualizados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza os dados de um cliente existente.
        
        Args:
            cliente_id: ID do cliente a ser atualizado.
            dados_atualizados: Dicionário com os dados atualizados do cliente.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        if not dados_atualizados:
            return False, "Nenhum dado para atualizar."
        
        # Preparar os pares campo=valor para a atualização
        sets = []
        valores = []
        
        for campo, valor in dados_atualizados.items():
            if campo != 'id':  # Não atualizar o ID
                sets.append(f"{campo} = %s")
                valores.append(valor)
        
        if not sets:
            return False, "Nenhum campo válido para atualização."
        
        # Adicionar o ID aos valores para a cláusula WHERE
        valores.append(cliente_id)
        
        query = f"""
            UPDATE pacientes
            SET {', '.join(sets)}
            WHERE id = %s
        """
        
        try:
            self.db.execute_query(query, tuple(valores))
            return True, "Cliente atualizado com sucesso."
        except Exception as e:
            print(f"Erro ao atualizar cliente: {e}")
            return False, f"Erro ao atualizar cliente: {str(e)}"
    
    def listar_clientes(self, filtro: str = None) -> List[Dict[str, Any]]:
        """
        Lista todos os clientes, opcionalmente filtrando por nome ou telefone.
        
        Args:
            filtro: Texto para filtrar por nome ou telefone (opcional).
            
        Returns:
            Lista de dicionários com os dados dos clientes.
        """
        query = """
            SELECT * FROM pacientes
            WHERE 1=1
        """
        
        params = ()
        
        if filtro:
            query += " AND (nome LIKE %s OR telefone LIKE %s OR telefone2 LIKE %s)"
            filtro_like = f"%{filtro}%"
            params = (filtro_like, filtro_like, filtro_like)
        
        query += " ORDER BY nome"
        
        try:
            return self.db.execute_query(query, params)
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []
    
    def obter_cliente_por_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um cliente pelo ID.
        
        Args:
            cliente_id: ID do cliente.
            
        Returns:
            Dicionário com os dados do cliente ou None se não encontrado.
        """
        query = """
            SELECT * FROM pacientes
            WHERE id = %s 
            LIMIT 1
        """
        
        try:
            return self.db.execute_query(query, (cliente_id,), fetch_all=False)
        except Exception as e:
            print(f"Erro ao obter cliente por ID: {e}")
            return None
            
    def excluir_cliente(self, cliente_id: int) -> Tuple[bool, str]:
        """
        Exclui permanentemente um cliente do banco de dados.
        
        Args:
            cliente_id: ID do cliente a ser excluído.
            
        Returns:
            Tupla (sucesso, mensagem).
        """
        query = "DELETE FROM pacientes WHERE id = %s"
        
        try:
            # Verificar se o cliente existe
            cliente = self.obter_cliente_por_id(cliente_id)
            if not cliente:
                return False, "Cliente não encontrado."
                
            # Executar a exclusão
            self.db.execute_query(query, (cliente_id,))
            return True, "Cliente excluído permanentemente com sucesso."
            
        except Exception as e:
            print(f"Erro ao excluir cliente: {e}")
            return False, f"Erro ao excluir cliente: {str(e)}"
