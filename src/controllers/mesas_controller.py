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
            db_connection: Conexão com o banco de dados (opcional)"""
        
        self.view = view
        self.db_connection = db_connection
        
        # Inicializa listas vazias para armazenar dados
        self.mesas = []
        self.pedidos = []
        self.produtos = []
        self.itens_pedido = []
        self.pedido_atual = None
        self.itens_adicionados_na_sessao = []  # Lista para armazenar todos os itens adicionados na sessão
    
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
    
    def carregar_pedidos(self, mesa_id: int, manter_itens_sessao: bool = False) -> bool:
        """
        Carrega os pedidos de uma mesa específica.
        
        Args:
            mesa_id: ID da mesa
            manter_itens_sessao: Se True, mantém os itens adicionados na sessão
            
        Returns:
            bool: True se os pedidos foram carregados com sucesso, False caso contrário.
        """
        try:
            # Fazer backup dos itens da sessão se necessário
            itens_sessao_backup = None
            if manter_itens_sessao and hasattr(self, 'itens_adicionados_na_sessao'):
                itens_sessao_backup = self.itens_adicionados_na_sessao.copy()
            
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Carregar todos os pedidos da mesa incluindo o usuario_id
            cursor.execute(
                """
                SELECT p.*, u.nome as nome_usuario 
                FROM pedidos p
                LEFT JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.mesa_id = %s 
                ORDER BY p.data_abertura DESC
                """,
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
    
    def criar_novo_pedido(self, mesa_id: int, usuario_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
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
            
            # Verificar se a mesa existe e está disponível
            cursor.execute("SELECT * FROM mesas WHERE id = %s", (mesa_id,))
            mesa = cursor.fetchone()
            
            if not mesa:
                return None
            
            # Criar o pedido
            data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Garantir que o usuario_id seja um inteiro ou NULL
            usuario_id_final = int(usuario_id) if usuario_id is not None else None
            
            # Construir a query dinamicamente para lidar com NULL
            if usuario_id_final is not None:
                cursor.execute(
                    """
                    INSERT INTO pedidos (mesa_id, data_abertura, status, total, usuario_id, tipo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (mesa_id, data_atual, 'ABERTO', 0.0, usuario_id_final, 'MESA')
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO pedidos (mesa_id, data_abertura, status, total, tipo)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (mesa_id, data_atual, 'ABERTO', 0.0, 'MESA')
                )
            
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
            
            # Se o pedido existente não tem um usuario_id ou tem um usuario_id diferente do fornecido, atualizar o pedido
            if usuario_id is not None and self.pedido_atual.get('usuario_id') != usuario_id:
                cursor = self.db_connection.cursor(dictionary=True)
                cursor.execute(
                    "UPDATE pedidos SET usuario_id = %s WHERE id = %s",
                    (usuario_id, self.pedido_atual['id'])
                )
                self.db_connection.commit()
                cursor.close()
                
                # Atualizar o pedido_atual com o novo usuario_id
                self.pedido_atual['usuario_id'] = usuario_id
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Se não foi fornecido um preço adicional, calcular a partir das opções
            if preco_adicional == 0.0 and opcoes_selecionadas:
                for opcao in opcoes_selecionadas:
                    preco_adicional += float(opcao.get('preco_adicional', 0))
            
            # Calcular valores
            valor_unitario = float(self._obter_preco_produto(produto))
            subtotal = (valor_unitario + preco_adicional) * quantidade
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
                    valor_unitario,
                    subtotal,
                    usuario_id,  # Usar o usuario_id fornecido
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
            
            # Buscar o item recém-adicionado com suas opções
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT ip.*, p.nome as nome_produto 
                FROM itens_pedido ip
                JOIN produtos p ON ip.produto_id = p.id
                WHERE ip.id = %s
                """,
                (item_id,)
            )
            item_adicionado = cursor.fetchone()
            
            # Buscar as opções do item, se houver
            if opcoes_selecionadas:
                cursor.execute(
                    "SELECT * FROM itens_pedido_opcoes WHERE item_pedido_id = %s",
                    (item_id,)
                )
                item_adicionado['opcoes'] = cursor.fetchall()
            else:
                item_adicionado['opcoes'] = []
            
            # Inicializar a lista de itens da sessão se não existir
            if not hasattr(self, 'itens_adicionados_na_sessao'):
                self.itens_adicionados_na_sessao = []
            
            # Armazenar o item na lista de itens adicionados na sessão
            self.itens_adicionados_na_sessao.append(item_adicionado)
            
            # Armazenar o último item adicionado para referência
            self.ultimo_item_adicionado = {'id': item_id}
            
            cursor.close()
            
            return True, "Item adicionado com sucesso", pedido_atualizado
        except Exception as e:
            import traceback
            traceback.print_exc()
            

            return False, f"Erro ao adicionar item: {str(e)}", None
    
    def limpar_itens_sessao(self) -> None:
        """
        Limpa a lista de itens adicionados na sessão atual.
        """
        try:
            if hasattr(self, 'itens_adicionados_na_sessao'):
                self.itens_adicionados_na_sessao = []
            else:
                self.itens_adicionados_na_sessao = []
        except Exception as e:
            import traceback
            traceback.print_exc()
    
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
                error_msg = "Conexão com o banco de dados não disponível"
                raise ValueError(error_msg)
            
            cursor = self.db_connection.cursor()
            
            # Verificar se o item existe antes de tentar remover
            cursor.execute("SELECT id, pedido_id FROM itens_pedido WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            
            if not item:
                error_msg = f"Item com ID {item_id} não encontrado"
                return False, error_msg
                
            pedido_id = item[1]
            
            # Remover as opções do item primeiro
            cursor.execute("DELETE FROM itens_pedido_opcoes WHERE item_pedido_id = %s", (item_id,))
            
            # Remover o item
            cursor.execute("DELETE FROM itens_pedido WHERE id = %s", (item_id,))
            
            if cursor.rowcount == 0:
                error_msg = f"Nenhum item removido (ID: {item_id})"
                self.db_connection.rollback()
                return False, error_msg
                
            # Atualizar o total do pedido
            cursor.execute(
                """
                UPDATE pedidos SET total = COALESCE((
                    SELECT SUM(subtotal) FROM itens_pedido WHERE pedido_id = %s
                ), 0) WHERE id = %s
                """,
                (pedido_id, pedido_id)
            )
            
            self.db_connection.commit()
            
            # Recarregar os itens do pedido
            self.carregar_itens_pedido(pedido_id)
            
            # Verificar se ainda há itens no pedido
            cursor.execute("SELECT COUNT(*) FROM itens_pedido WHERE pedido_id = %s", (pedido_id,))
            count = cursor.fetchone()[0]
            
            # Se não houver mais itens, cancelar o pedido e liberar a mesa
            if count == 0 and self.pedido_atual and 'id' in self.pedido_atual:
                # Atualizar o status do pedido para CANCELADO
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
                    (data_atual, data_atual, pedido_id)
                )
                
                # Liberar a mesa
                cursor.execute(
                    "UPDATE mesas SET status = 'LIVRE', pedido_atual_id = NULL WHERE pedido_atual_id = %s",
                    (pedido_id,)
                )
                
                # Limpar o pedido atual
                self.pedido_atual = None
                self.itens_pedido = []
                
                self.db_connection.commit()
            
            cursor.close()
            
            success_msg = f"Item {item_id} removido com sucesso"
            return True, success_msg
            
        except Exception as e:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if self.db_connection:
                self.db_connection.rollback()
            import traceback
            error_msg = f"Erro ao remover item: {str(e)}"
            print(f"[ERRO CRÍTICO] {error_msg}")
            traceback.print_exc()
            return False, error_msg
    
    def finalizar_pedido(self, forma_pagamento: str, valor_total: float, 
                        desconto: float = 0.0, pagamento: Optional[Dict] = None) -> Tuple[bool, str]:
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
            
            # Calcular o troco se for pagamento em dinheiro
            troco = 0
            if forma_pagamento.lower() == 'dinheiro':
                troco = pagamento.get('troco', 0)  # O troco deve ser passado no dicionário de pagamento
                
            # Atualizar o pedido com troco e desconto
            cursor.execute(
                """
                UPDATE pedidos 
                SET status = 'FINALIZADO', 
                    data_fechamento = %s, 
                    forma_pagamento = %s,
                    total = %s,
                    troco_para = %s,
                    desconto = %s
                WHERE id = %s
                """,
                (data_atual, forma_pagamento, valor_total - desconto, troco, desconto, self.pedido_atual['id'])
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
    
    def atualizar_total_pedido(self, pedido_id: int) -> float:
        """
        Atualiza a taxa de serviço de um pedido.
        
        Args:
            pedido_id: ID do pedido a ser atualizado
            taxa_servico: 1 para ativar a taxa de serviço (10%), 0 para desativar
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Primeiro, obtém o total dos itens do pedido (sem a taxa de serviço)
            query_itens = """
                SELECT COALESCE(SUM(ip.quantidade * ip.valor_unitario), 0) as total_itens
                FROM itens_pedido ip
                WHERE ip.pedido_id = %s
            """
            
            cursor.execute(query_itens, (pedido_id,))
            resultado = cursor.fetchone()
            total_itens = float(resultado['total_itens'] or 0.0) if resultado else 0.0
            
            # Inicializa o total de opções como zero
            total_opcoes = 0.0
            
            # Verifica se a tabela itens_pedido_opcoes existe
            cursor.execute("""
                SELECT COUNT(*) as table_exists 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = 'itens_pedido_opcoes'
            """)
            tabela_opcoes_existe = cursor.fetchone()['table_exists'] > 0
            
            if tabela_opcoes_existe:
                # Verifica se a tabela opcoes existe
                cursor.execute("""
                    SELECT COUNT(*) as table_exists 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'opcoes'
                """)
                tabela_opcoes_existe = cursor.fetchone()['table_exists'] > 0
                
                if tabela_opcoes_existe:
                    # Se ambas as tabelas existirem, tenta obter o total das opções
                    try:
                        query_opcoes = """
                            SELECT COALESCE(SUM(ipo.quantidade * o.preco_adicional), 0) as total_opcoes
                            FROM itens_pedido_opcoes ipo
                            JOIN opcoes o ON ipo.opcao_id = o.id
                            JOIN itens_pedido ip ON ipo.item_pedido_id = ip.id
                            WHERE ip.pedido_id = %s
                        """
            
                        cursor.execute(query_opcoes, (pedido_id,))
                        resultado = cursor.fetchone()
                        total_opcoes = float(resultado['total_opcoes'] or 0.0) if resultado else 0.0
                    except Exception as e:
                        print(f"Erro ao calcular total das opções: {str(e)}")
                        total_opcoes = 0.0
            
            # Calcula o subtotal (itens + opções) - este é o valor sem a taxa de serviço
            subtotal = total_itens + total_opcoes
            
            # O total retornado é apenas o subtotal (sem a taxa de serviço)
            # A taxa de serviço será aplicada posteriormente, se necessário
            
            # Atualiza o subtotal no pedido
            update_query = """
                UPDATE pedidos 
                SET total = %s,
                    data_atualizacao = NOW()
                WHERE id = %s
            """
            cursor.execute(update_query, (subtotal, pedido_id))
            self.db_connection.commit()
            
            # Atualiza o pedido atual se for o mesmo pedido
            if self.pedido_atual and self.pedido_atual.get('id') == pedido_id:
                self.pedido_atual['total'] = subtotal
            
            return subtotal
            
        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            error_msg = f"Erro ao atualizar total do pedido: {str(e)}"
            print(f"[ERRO] {error_msg}")
            import traceback
            traceback.print_exc()
            raise
            
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

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
    
    def obter_grupos_opcoes(self, produto_id: int) -> List[Dict[str, Any]]:
        """
        Obtém os grupos de opções disponíveis para um produto.
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Lista de dicionários com os grupos de opções e seus itens
        """
        try:
            if not self.db_connection:
                raise ValueError("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Buscar os grupos de opções associados ao produto
            cursor.execute("""
                SELECT 
                    og.id, 
                    og.nome, 
                    og.descricao, 
                    po.obrigatorio,
                    og.selecao_minima,
                    og.selecao_maxima
                FROM 
                    opcoes_grupos og
                INNER JOIN 
                    produto_opcoes po ON og.id = po.grupo_id
                WHERE 
                    po.produto_id = %s
                    AND og.ativo = TRUE
                ORDER BY 
                    po.ordem, og.nome
            """, (produto_id,))
            
            grupos = cursor.fetchall()
            
            # Para cada grupo, buscar os itens de opção
            for grupo in grupos:
                cursor.execute("""
                    SELECT 
                        id, 
                        nome, 
                        descricao, 
                        preco_adicional
                    FROM 
                        opcoes_itens
                    WHERE 
                        grupo_id = %s
                        AND ativo = TRUE
                    ORDER BY 
                        nome
                """, (grupo['id'],))
                
                grupo['itens'] = cursor.fetchall()
            
            cursor.close()
            return grupos
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []