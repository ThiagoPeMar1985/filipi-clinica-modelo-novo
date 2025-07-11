"""
Controlador para o módulo de Mesas.

Gerencia as operações relacionadas às mesas e seus pedidos.

tabelas em uso neste modulo
Table: mesas
Columns:
id int AI PK 
numero int 
status varchar(20) 
capacidade int 
pedido_atual_id int

Table: itens_pedido
Columns:
id int AI PK 
pedido_id int 
produto_id int 
quantidade int 
valor_unitario decimal(10,2) 
subtotal decimal(10,2) 
observacao text 
usuario_id int 
data_hora datetime 
valor_total decimal(10,2) 
observacoes text 
status varchar(20) 
data_hora_preparo datetime 
data_hora_pronto datetime 
data_hora_entregue datetime

Table: pedidos
Columns:
id int AI PK 
mesa_id int 
data_abertura datetime 
data_fechamento datetime 
status varchar(20) 
total decimal(10,2) 
usuario_id int 
tipo enum('MESA','AVULSO','DELIVERY') 
cliente_id int 
cliente_nome varchar(255) 
cliente_telefone varchar(20) 
cliente_endereco text 
entregador_id int 
tipo_cliente varchar(20) 
regiao_id int 
taxa_entrega decimal(10,2) 
observacao text 
previsao_entrega datetime 
data_entrega datetime 
status_entrega varchar(50) 
processado_estoque tinyint(1) 
data_atualizacao timestamp 
data_inicio_preparo datetime 
data_pronto_entrega datetime 
data_saida_entrega datetime 
data_cancelamento datetime 
forma_pagamento varchar(50) 
troco_para decimal(10,2)

Table: opcoes_itens
Columns:
id int AI PK 
grupo_id int 
nome varchar(100) 
descricao text 
preco_adicional decimal(10,2) 
ativo tinyint(1) 
data_criacao timestamp 
data_atualizacao timestamp

Table: itens_pedido_opcoes
Columns:
id int AI PK 
item_pedido_id int 
opcao_id int 
grupo_id int 
nome varchar(255) 
preco_adicional decimal(10,2) 
data_criacao timestamp




"""
import datetime
import mysql.connector
from typing import List, Dict, Any, Optional, Tuple, Union

class MesasController:
    """Controlador para operações do módulo de Mesas."""
    
    def __init__(self, view=None, db_connection=None):
        """
        Inicializa o controlador com a view opcional e conexão com o banco de dados.
        
        Args:
            view: View associada ao controlador (opcional)
            db_connection: Conexão com o banco de dados (opcional)
        """
        self.view = view
        self.db_connection = db_connection
        
        # Inicializa listas vazias para armazenar dados
        self.mesas = []
        self.pedidos = []
        self.produtos = []
        self.itens_pedido = []
        self.pedido_atual = None
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
        
    def carregar_mesas(self) -> bool:
        """
        Carrega todas as mesas do banco de dados.
        
        Returns:
            bool: True se as mesas foram carregadas com sucesso, False caso contrário.
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM mesas ORDER BY numero")
            self.mesas = cursor.fetchall()
            cursor.close()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def carregar_produtos(self) -> bool:
        """
        Carrega todos os produtos do banco de dados.
        
        Returns:
            bool: True se os produtos foram carregados com sucesso, False caso contrário.
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            # Removendo a condição ativo=1 já que a coluna não existe
            cursor.execute("SELECT * FROM produtos ORDER BY nome")
            self.produtos = cursor.fetchall()
            cursor.close()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def carregar_pedidos(self, mesa_id: int) -> bool:
        """
        Carrega os pedidos de uma mesa específica.
        
        Args:
            mesa_id: ID da mesa
            
        Returns:
            bool: True se os pedidos foram carregados com sucesso, False caso contrário.
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Carregar todos os pedidos da mesa
            cursor.execute(
                "SELECT * FROM pedidos WHERE mesa_id = %s ORDER BY data_abertura DESC",
                (mesa_id,)
            )
            self.pedidos = cursor.fetchall()
            
            # Identificar o pedido atual (em aberto)
            self.pedido_atual = None
            for pedido in self.pedidos:
                if pedido['status'] in ['ABERTO', 'EM_ANDAMENTO']:
                    self.pedido_atual = pedido
                    break
            
            # Se encontrou um pedido atual, carregar seus itens
            if self.pedido_atual:
                self.carregar_itens_pedido(self.pedido_atual['id'])
            
            cursor.close()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def carregar_itens_pedido(self, pedido_id: int) -> bool:
        """
        Carrega os itens de um pedido específico, incluindo suas opções.
        
        Args:
            pedido_id: ID do pedido
            
        Returns:
            bool: True se os itens foram carregados com sucesso, False caso contrário.
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Carregar itens do pedido
            cursor.execute(
                """
                SELECT ip.*, p.nome as nome_produto 
                FROM itens_pedido ip
                JOIN produtos p ON ip.produto_id = p.id
                WHERE ip.pedido_id = %s
                ORDER BY ip.id
                """,
                (pedido_id,)
            )
            self.itens_pedido = cursor.fetchall()
            
            # Para cada item, carregar suas opções
            for item in self.itens_pedido:
                cursor.execute(
                    """
                    SELECT * FROM itens_pedido_opcoes
                    WHERE item_pedido_id = %s
                    """,
                    (item['id'],)
                )
                opcoes = cursor.fetchall()
                item['opcoes'] = opcoes
            
            cursor.close()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def criar_novo_pedido(self, mesa_id: int, usuario_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Cria um novo pedido para a mesa especificada.
        
        Args:
            mesa_id: ID da mesa
            usuario_id: ID do usuário que está criando o pedido (opcional)
            
        Returns:
            Dict[str, Any]: Dados do pedido criado ou None se falhar
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Verificar se já existe um pedido em aberto para esta mesa
            cursor.execute(
                "SELECT * FROM pedidos WHERE mesa_id = %s AND status IN ('ABERTO', 'EM_ANDAMENTO')",
                (mesa_id,)
            )
            pedido_existente = cursor.fetchone()
            
            if pedido_existente:
                return pedido_existente
            
            # Criar novo pedido
            data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(
                """
                INSERT INTO pedidos (mesa_id, data_abertura, status, total, usuario_id, tipo)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (mesa_id, data_atual, 'ABERTO', 0.0, usuario_id, 'MESA')
            )
            
            self.db_connection.commit()
            pedido_id = cursor.lastrowid
            
            # Atualizar a mesa para apontar para o novo pedido
            cursor.execute(
                "UPDATE mesas SET status = 'OCUPADA', pedido_atual_id = %s WHERE id = %s",
                (pedido_id, mesa_id)
            )
            
            self.db_connection.commit()
            
            # Buscar o pedido completo
            cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
            novo_pedido = cursor.fetchone()
            
            cursor.close()
            
            # Atualizar o pedido atual
            self.pedido_atual = novo_pedido
            
            return novo_pedido
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def adicionar_item_mesa(self, mesa_id: int, produto: Dict[str, Any], quantidade: int, 
                           opcoes_selecionadas: Optional[List[Dict[str, Any]]] = None,
                           preco_adicional: float = 0.0,
                           usuario_id: Optional[int] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Adiciona um item ao pedido atual da mesa.
        
        Args:
            mesa_id: ID da mesa
            produto: Dados do produto
            quantidade: Quantidade do item
            opcoes_selecionadas: Lista de opções selecionadas (opcional)
            preco_adicional: Preço adicional das opções (opcional)
            usuario_id: ID do usuário que está adicionando o item (opcional)
            
        Returns:
            Tuple[bool, str, Optional[Dict[str, Any]]]: (sucesso, mensagem, pedido_atualizado)
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
            
            # Verificar se há um pedido atual
            if not self.pedido_atual:
                # Tentar criar um novo pedido
                novo_pedido = self.criar_novo_pedido(mesa_id, usuario_id)
                if not novo_pedido:
                    return False, "Não foi possível criar um novo pedido", None
                self.pedido_atual = novo_pedido
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Se não foi fornecido um preço adicional, calcular a partir das opções
            if preco_adicional == 0.0 and opcoes_selecionadas:
                for opcao in opcoes_selecionadas:
                    preco_adicional += float(opcao.get('preco_adicional', 0))
            
            # Inserir o item no pedido
            cursor.execute(
                """
                INSERT INTO itens_pedido 
                (pedido_id, produto_id, quantidade, valor_unitario, subtotal, usuario_id, data_hora)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    self.pedido_atual['id'],
                    produto['id'],
                    quantidade,
                    float(self._obter_preco_produto(produto)),
                    (float(self._obter_preco_produto(produto)) + preco_adicional) * quantidade,
                    usuario_id,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            
            item_id = cursor.lastrowid
            
            # Inserir as opções do item, se houver
            if opcoes_selecionadas:
                for opcao in opcoes_selecionadas:
                    cursor.execute(
                        """
                        INSERT INTO itens_pedido_opcoes 
                        (item_pedido_id, opcao_id, grupo_id, nome, preco_adicional)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            item_id,
                            opcao['id'],
                            opcao.get('grupo_id'),
                            opcao['nome'],
                            float(opcao['preco_adicional'])
                        )
                    )
            
            # Atualizar o total do pedido
            cursor.execute(
                """
                UPDATE pedidos SET total = (
                    SELECT SUM(subtotal) FROM itens_pedido WHERE pedido_id = %s
                ) WHERE id = %s
                """,
                (self.pedido_atual['id'], self.pedido_atual['id'])
            )
            
            # Atualizar o status do pedido para EM_ANDAMENTO se estiver ABERTO
            if self.pedido_atual['status'] == 'ABERTO':
                cursor.execute(
                    "UPDATE pedidos SET status = 'EM_ANDAMENTO' WHERE id = %s",
                    (self.pedido_atual['id'],)
                )
            
            self.db_connection.commit()
            
            # Buscar o pedido atualizado
            cursor.execute("SELECT * FROM pedidos WHERE id = %s", (self.pedido_atual['id'],))
            pedido_atualizado = cursor.fetchone()
            
            # Atualizar o pedido atual
            self.pedido_atual = pedido_atualizado
            
            # Recarregar os itens do pedido
            self.carregar_itens_pedido(self.pedido_atual['id'])
            
            cursor.close()
            
            return True, "Item adicionado com sucesso", pedido_atualizado
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Erro ao adicionar item: {str(e)}", None
    
    def remover_item_pedido(self, item_id: int) -> Tuple[bool, str]:
        """
        Remove um item do pedido atual.
        
        Args:
            item_id: ID do item a ser removido
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
            
            cursor = self.db_connection.cursor()
            
            # Remover as opções do item primeiro
            cursor.execute("DELETE FROM itens_pedido_opcoes WHERE item_pedido_id = %s", (item_id,))
            
            # Remover o item
            cursor.execute("DELETE FROM itens_pedido WHERE id = %s", (item_id,))
            
            # Atualizar o total do pedido
            if self.pedido_atual:
                cursor.execute(
                    """
                    UPDATE pedidos SET total = COALESCE((
                        SELECT SUM(subtotal) FROM itens_pedido WHERE pedido_id = %s
                    ), 0) WHERE id = %s
                    """,
                    (self.pedido_atual['id'], self.pedido_atual['id'])
                )
            
            self.db_connection.commit()
            
            # Recarregar os itens do pedido
            if self.pedido_atual:
                self.carregar_itens_pedido(self.pedido_atual['id'])
                
                # Verificar se ainda há itens no pedido
                cursor.execute("SELECT COUNT(*) FROM itens_pedido WHERE pedido_id = %s", (self.pedido_atual['id'],))
                count = cursor.fetchone()[0]
                
                # Se não houver mais itens, atualizar o status do pedido para ABERTO
                if count == 0:
                    cursor.execute(
                        "UPDATE pedidos SET status = 'ABERTO' WHERE id = %s",
                        (self.pedido_atual['id'],)
                    )
                    self.db_connection.commit()
            
            cursor.close()
            
            return True, "Item removido com sucesso"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Erro ao remover item: {str(e)}"
    
    def finalizar_pedido(self, forma_pagamento: str, valor_total: float, 
                        desconto: float = 0.0) -> Tuple[bool, str]:
        """
        Finaliza o pedido atual da mesa.
        
        Args:
            forma_pagamento: Forma de pagamento
            valor_total: Valor total do pedido
            desconto: Valor do desconto (opcional)
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
            
            if not self.pedido_atual:
                return False, "Não há pedido em andamento"
            
            cursor = self.db_connection.cursor()
            
            # Atualizar o pedido
            data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(
                """
                UPDATE pedidos 
                SET status = 'FINALIZADO', 
                    data_fechamento = %s, 
                    forma_pagamento = %s,
                    total = %s
                WHERE id = %s
                """,
                (data_atual, forma_pagamento, valor_total - desconto, self.pedido_atual['id'])
            )
            
            # Liberar a mesa
            cursor.execute(
                "UPDATE mesas SET status = 'LIVRE', pedido_atual_id = NULL WHERE id = %s",
                (self.pedido_atual['mesa_id'],)
            )
            
            self.db_connection.commit()
            
            # Limpar o pedido atual
            self.pedido_atual = None
            self.itens_pedido = []
            
            cursor.close()
            
            return True, "Pedido finalizado com sucesso"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Erro ao finalizar pedido: {str(e)}"
    
    def cancelar_pedido(self) -> Tuple[bool, str]:
        """
        Cancela o pedido atual da mesa.
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
            
            if not self.pedido_atual:
                return False, "Não há pedido em andamento"
            
            cursor = self.db_connection.cursor()
            
            # Remover todas as opções dos itens do pedido
            cursor.execute(
                """
                DELETE FROM itens_pedido_opcoes 
                WHERE item_pedido_id IN (SELECT id FROM itens_pedido WHERE pedido_id = %s)
                """,
                (self.pedido_atual['id'],)
            )
            
            # Remover todos os itens do pedido
            cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (self.pedido_atual['id'],))
            
            # Atualizar o pedido
            data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute(
                """
                UPDATE pedidos 
                SET status = 'CANCELADO', 
                    data_fechamento = %s,
                    data_cancelamento = %s,
                    total = 0
                WHERE id = %s
                """,
                (data_atual, data_atual, self.pedido_atual['id'])
            )
            
            # Liberar a mesa
            cursor.execute(
                "UPDATE mesas SET status = 'LIVRE', pedido_atual_id = NULL WHERE id = %s",
                (self.pedido_atual['mesa_id'],)
            )
            
            self.db_connection.commit()
            
            # Limpar o pedido atual
            self.pedido_atual = None
            self.itens_pedido = []
            
            cursor.close()
            
            return True, "Pedido cancelado com sucesso"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Erro ao cancelar pedido: {str(e)}"
    
    def _obter_preco_produto(self, produto: Dict[str, Any]) -> float:
        """
        Obtém o preço do produto independente do nome do campo.
        
        Args:
            produto: Dicionário com os dados do produto
            
        Returns:
            float: Preço do produto ou 0.0 se não encontrar
        """
        # Lista de possíveis nomes de campo para preço
        campos_preco = ['preco', 'valor', 'valor_unitario', 'price', 'valor_venda', 'preco_venda']
        
        # Verificar cada campo
        for campo in campos_preco:
            if campo in produto and produto[campo] is not None:
                try:
                    return float(produto[campo])
                except (ValueError, TypeError):
                    continue
        
        # Se chegou aqui, não encontrou nenhum campo válido
        print(f"Aviso: Não foi possível encontrar o preço do produto {produto.get('id', '?')} - {produto.get('nome', '?')}")
        print(f"Campos disponíveis: {list(produto.keys())}")
        return 0.0
    
    def adicionar_item_especifico(self, pedido_id: int, produto: Dict[str, Any], quantidade: int,
                                opcoes_selecionadas: Optional[List[Dict[str, Any]]] = None,
                                preco_adicional: float = 0.0) -> bool:
        """
        Adiciona um item específico a um pedido.
        
        Args:
            pedido_id: ID do pedido
            produto: Dados do produto
            quantidade: Quantidade do item
            opcoes_selecionadas: Lista de opções selecionadas (opcional)
            preco_adicional: Preço adicional das opções (opcional)
            
        Returns:
            bool: True se o item foi adicionado com sucesso, False caso contrário
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Inserir o item no pedido
            cursor.execute(
                """
                INSERT INTO itens_pedido 
                (pedido_id, produto_id, quantidade, valor_unitario, subtotal, data_hora)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    pedido_id,
                    produto['id'],
                    quantidade,
                    float(self._obter_preco_produto(produto)),
                    (float(self._obter_preco_produto(produto)) + preco_adicional) * quantidade,
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            )
            
            item_id = cursor.lastrowid
            
            # Inserir as opções do item, se houver
            if opcoes_selecionadas:
                for opcao in opcoes_selecionadas:
                    cursor.execute(
                        """
                        INSERT INTO itens_pedido_opcoes 
                        (item_pedido_id, opcao_id, grupo_id, nome, preco_adicional)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            item_id,
                            opcao['id'],
                            opcao.get('grupo_id'),
                            opcao['nome'],
                            float(opcao['preco_adicional'])
                        )
                    )
            
            # Atualizar o total do pedido
            cursor.execute(
                """
                UPDATE pedidos SET total = (
                    SELECT SUM(subtotal) FROM itens_pedido WHERE pedido_id = %s
                ) WHERE id = %s
                """,
                (pedido_id, pedido_id)
            )
            
            # Atualizar o status do pedido para EM_ANDAMENTO se estiver ABERTO
            cursor.execute(
                "UPDATE pedidos SET status = 'EM_ANDAMENTO' WHERE id = %s AND status = 'ABERTO'",
                (pedido_id,)
            )
            
            self.db_connection.commit()
            cursor.close()
            
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
