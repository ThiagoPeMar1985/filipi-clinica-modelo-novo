"""
Controlador para operações relacionadas a clientes.
"""
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

class ClienteController:
    """Controlador para operações relacionadas a clientes."""
    
    def __init__(self):
        """Inicializa o controlador de clientes."""
        from src.db.database import db
        self.db = db
    
    def buscar_cliente_por_id(self, cliente_id: int) -> tuple[bool, dict]:
        """
        Busca um cliente pelo ID.
        
        Args:
            cliente_id: ID do cliente a ser buscado.
            
        Returns:
            Tupla (sucesso, dados_do_cliente)
            - sucesso: booleano indicando se a operação foi bem sucedida
            - dados_do_cliente: dicionário com os dados do cliente ou mensagem de erro
        """
        query = """
            SELECT 
                id, nome, telefone, telefone2, email, 
                endereco, numero, complemento, bairro, 
                cidade, uf, cep, ponto_referencia, observacoes, regiao_entrega_id
            FROM clientes_delivery 
            WHERE id = %s
        """
        try:
            resultado = self.db.execute_query(query, (cliente_id,), fetch_all=False)
            if not resultado:
                return False, "Cliente não encontrado."
                
            # Garantir que todos os campos estejam presentes no dicionário
            cliente = {
                'id': resultado.get('id'),
                'nome': resultado.get('nome', ''),
                'telefone': resultado.get('telefone', ''),
                'telefone2': resultado.get('telefone2', ''),
                'email': resultado.get('email', ''),
                'endereco': resultado.get('endereco', ''),
                'numero': resultado.get('numero', ''),
                'complemento': resultado.get('complemento', ''),
                'bairro': resultado.get('bairro', ''),
                'cidade': resultado.get('cidade', ''),
                'uf': resultado.get('uf', ''),
                'cep': resultado.get('cep', ''),
                'ponto_referencia': resultado.get('ponto_referencia', ''),
                'observacoes': resultado.get('observacoes', ''),
                'regiao_entrega_id': resultado.get('regiao_entrega_id')
            }
            
            return True, cliente
            
        except Exception as e:
            print(f"Erro ao buscar cliente por ID: {e}")
            return False, f"Erro ao buscar cliente: {str(e)}"
            
    def atualizar_cliente(self, cliente_id: int, dados_atualizados: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Atualiza os dados de um cliente existente.
        
        Args:
            cliente_id: ID do cliente a ser atualizado
            dados_atualizados: Dicionário com os campos a serem atualizados
            
        Returns:
            Tupla (sucesso, mensagem)
        """
        if not dados_atualizados:
            return False, "Nenhum dado para atualizar."
            
        # Remover campos que não devem ser atualizados
        dados_atualizados.pop('id', None)
        dados_atualizados.pop('data_cadastro', None)
        
        # Montar a query dinamicamente
        sets = []
        valores = []
        for campo, valor in dados_atualizados.items():
            if valor is not None:
                sets.append(f"{campo} = %s")
                valores.append(valor)
        
        if not sets:
            return False, "Nenhum dado válido para atualizar."
            
        # Adicionar o ID no final para a cláusula WHERE
        valores.append(cliente_id)
        
        query = f"""
            UPDATE clientes_delivery 
            SET {', '.join(sets)}
            WHERE id = %s
        """
        
        try:
            self.db.execute_query(query, tuple(valores))
            return True, "Cliente atualizado com sucesso."
        except Exception as e:
            print(f"Erro ao atualizar cliente: {e}")
            return False, f"Erro ao atualizar cliente: {str(e)}"
            
    def buscar_cliente_por_telefone(self, telefone: str) -> List[Dict[str, Any]]:
        """
        Busca clientes pelo telefone (busca parcial).
        
        Args:
            telefone: Número de telefone ou parte dele para busca.
            
        Returns:
            Lista de dicionários com os dados dos clientes encontrados.
        """
        query = """
            SELECT * FROM clientes_delivery 
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
            SELECT * FROM clientes_delivery 
            WHERE nome LIKE %s
            ORDER BY nome
            LIMIT 10
        """
        try:
            return self.db.execute_query(query, (f"%{nome}%",))
        except Exception as e:
            print(f"Erro ao buscar cliente por nome: {e}")
            return []
    
    def cadastrar_cliente(self, dados_cliente: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
        """
        Cadastra um novo cliente no banco de dados.
        
        Args:
            dados_cliente: Dicionário com os dados do cliente.
            
        Returns:
            Tupla (sucesso, id_ou_mensagem).
            - Se sucesso for True, id_ou_mensagem contém o ID do cliente cadastrado.
            - Se sucesso for False, id_ou_mensagem contém uma mensagem de erro.
        """
        # Verificar campos obrigatórios
        campos_obrigatorios = ['nome', 'telefone', 'endereco', 'numero', 'bairro', 'cidade', 'uf']
        for campo in campos_obrigatorios:
            if not dados_cliente.get(campo):
                nome_campo = campo.replace('_', ' ').title()
                return False, f"O campo {nome_campo} é obrigatório."
        
        # Verificar se já existe cliente com o mesmo telefone
        telefone = dados_cliente['telefone']
        cliente_existente = self.buscar_cliente_por_telefone(telefone)
        if cliente_existente:
            return False, f"Já existe um cliente cadastrado com este telefone: {cliente_existente.get('nome')}"
            
        # Preparar os dados para inserção
        campos = []
        valores = []
        
        # Adicionar a data de cadastro atual
        from datetime import datetime
        dados_cliente['data_cadastro'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for campo, valor in dados_cliente.items():
            if valor is not None and valor != '':
                campos.append(campo)
                valores.append(valor)
      
        # Montar a query de inserção
        placeholders = ', '.join(['%s'] * len(campos))
        campos_str = ', '.join(campos)
        
        query = f"""
            INSERT INTO clientes_delivery ({campos_str})
            VALUES ({placeholders})
        """
        
        try:
            resultado = self.db.execute_query(query, tuple(valores), fetch_all=False)
            return True, resultado['lastrowid']
        except Exception as e:
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
            UPDATE clientes_delivery 
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
            SELECT * FROM clientes_delivery 
            WHERE ativo = 1
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
            SELECT * FROM clientes_delivery 
            WHERE id = %s AND ativo = 1
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
        query = "DELETE FROM clientes_delivery WHERE id = %s"
        
        try:
            self.db.execute_query(query, (cliente_id,))
            return True, "Cliente excluído permanentemente com sucesso."
        except Exception as e:
            print(f"Erro ao excluir cliente: {e}")
            return False, f"Erro ao excluir cliente: {str(e)}"
