"""
Controlador para o módulo de Delivery.
"""
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys
import datetime

# Adiciona o diretório raiz ao path para importações
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

class DeliveryController:
    """Controlador para operações do módulo de Delivery."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Inicializar o banco de dados
        from src.db.database import DatabaseConnection
        self.db = DatabaseConnection().get_connection()
        
        # Criar as tabelas necessárias se não existirem
        self._criar_tabela_regioes_entrega()
        self._criar_tabela_itens_pedido_opcoes()
        self._criar_tabela_historico_status_pedido()
        
    def _criar_tabela_itens_pedido_opcoes(self):
        """Cria a tabela de opções dos itens do pedido se não existir."""
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido_opcoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_pedido_id INT NOT NULL,
                opcao_id INT NOT NULL,
                grupo_id INT NOT NULL,
                nome VARCHAR(255) NOT NULL,
                preco_adicional DECIMAL(10,2) DEFAULT 0.00,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_pedido_id) REFERENCES itens_pedido(id) ON DELETE CASCADE,
                FOREIGN KEY (opcao_id) REFERENCES opcoes_itens(id) ON DELETE RESTRICT,
                FOREIGN KEY (grupo_id) REFERENCES opcoes_grupos(id) ON DELETE RESTRICT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            self.db.commit()
            cursor.close()
        except Exception as e:
            print(f"Erro ao criar tabela de opções dos itens do pedido: {e}")
            if cursor:
                cursor.close()
    
    def _registrar_historico_status(self, pedido_id, status, observacao=None, usuario_id=1):
        """Registra uma alteração de status no histórico do pedido.
        
        Args:
            pedido_id (int): ID do pedido
            status (str): Novo status do pedido
            observacao (str, optional): Observação sobre a alteração de status
            usuario_id (int, optional): ID do usuário que realizou a alteração. Default: 1 (admin)
            
        Returns:
            bool: True se o registro foi feito com sucesso, False caso contrário
        """
        cursor = None
        try:
            cursor = self.db.cursor()
            
            # Verificar se o pedido existe
            cursor.execute("SELECT id FROM pedidos WHERE id = %s", (pedido_id,))
            if not cursor.fetchone():
                print(f"Pedido {pedido_id} não encontrado para registrar histórico de status.")
                return False
            
            # Inserir o registro de histórico
            query = """
            INSERT INTO historico_status_pedido 
            (pedido_id, status, data_alteracao, usuario_id, observacao)
            VALUES (%s, %s, NOW(), %s, %s)
            """
            
            cursor.execute(query, (pedido_id, status, usuario_id, observacao))
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao registrar histórico de status para o pedido {pedido_id}: {e}")
            self.db.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def _criar_tabela_historico_status_pedido(self):
        """Cria a tabela de histórico de status dos pedidos se não existir."""
        cursor = None
        try:
            # Verificar e adicionar colunas necessárias na tabela pedidos
            cursor = self.db.cursor()
            
            # Lista de colunas que precisam ser verificadas/criadas
            colunas_necessarias = [
                ('data_atualizacao', "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                ('data_inicio_preparo', 'DATETIME'),
                ('data_pronto_entrega', 'DATETIME'),
                ('data_saida_entrega', 'DATETIME'),
                ('data_entrega', 'DATETIME'),
                ('data_cancelamento', 'DATETIME')
            ]
            
            for coluna, tipo in colunas_necessarias:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'pedidos' 
                    AND COLUMN_NAME = %s
                """, (coluna,))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute(f"""
                        ALTER TABLE pedidos 
                        ADD COLUMN {coluna} {tipo}
                    """)
            
            # Verificar se a tabela de histórico de status já existe
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'historico_status_pedido'
            """)
            
            if cursor.fetchone()[0] == 0:
                # Criar a tabela de histórico de status
                query = """
                CREATE TABLE historico_status_pedido (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    pedido_id INT NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario_id INT,
                    observacao TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
                cursor.execute(query)
            self.db.commit()
        except Exception as e:
            print(f"Erro ao criar tabela de histórico de status de pedidos: {e}")
            if cursor:
                cursor.close()
        finally:
            if cursor:
                cursor.close()
                
    def _criar_tabela_regioes_entrega(self):
        """Cria a tabela de regiões de entrega se não existir."""
        cursor = None
        try:
            query = """
            CREATE TABLE IF NOT EXISTS regioes_entrega (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                taxa_entrega DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                tempo_medio_entrega INT NOT NULL DEFAULT 30,
                ativo TINYINT(1) NOT NULL DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor = self.db.cursor()
            cursor.execute(query)
            self.db.commit()
        except Exception as e:
            print(f"Erro ao criar tabela de regiões de entrega: {e}")
            if cursor:
                cursor.close()
        finally:
            if cursor:
                cursor.close()
                

    
    def listar_regioes_entrega(self, ativo=None):
        """Lista todas as regiões de entrega.
        
        Args:
            ativo (bool, optional): Filtrar por status ativo/inativo. Defaults to None.
            
        Returns:
            list: Lista de dicionários com as regiões de entrega
        """
        cursor = self.db.cursor(dictionary=True)
        try:
            query = "SELECT * FROM regioes_entrega"
            params = []
            
            if ativo is not None:
                query += " WHERE ativo = %s"
                params.append(1 if ativo else 0)
                
            query += " ORDER BY nome"
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar regiões de entrega: {e}")
            return []
        finally:
            cursor.close()
    
    def atualizar_status_pedido(self, pedido_id, novo_status):
        """Atualiza o status de um pedido de entrega.
        
        Args:
            pedido_id (int): ID do pedido a ser atualizado
            novo_status (str): Novo status do pedido (ex: 'EM_PREPARO', 'EM_ROTA', 'ENTREGUE', 'CANCELADO')
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        cursor = self.db.cursor()
        try:
            # Verificar se o pedido existe
            cursor.execute("SELECT id, status FROM pedidos WHERE id = %s AND tipo = 'DELIVERY'", (pedido_id,))
            pedido = cursor.fetchone()
            
            if not pedido:
                return False, f"Pedido de entrega {pedido_id} não encontrado."
            
            status_atual = pedido[1]
            
            # Validar transição de status
            if status_atual == 'CANCELADO':
                return False, "Não é possível alterar o status de um pedido cancelado."
                
            if status_atual == 'ENTREGUE' and novo_status != 'ENTREGUE':
                return False, "Não é possível alterar o status de um pedido já entregue."
            
            # Atualizar o status do pedido
            campos_atualizar = ["status = %s", "status_entrega = %s", "data_atualizacao = NOW()"]
            params = [novo_status, novo_status, pedido_id]
            
            # Registrar eventos específicos baseados no novo status
            if novo_status == 'EM_PREPARO':
                campos_atualizar.append("data_inicio_preparo = NOW()")
            elif novo_status == 'PRONTO_ENTREGA':
                campos_atualizar.append("data_pronto_entrega = NOW()")
            elif novo_status == 'EM_ROTA':
                campos_atualizar.append("data_saida_entrega = NOW()")
            elif novo_status == 'ENTREGUE':
                campos_atualizar.append("data_entrega = NOW()")
                self._registrar_pagamento_entrega(pedido_id)
            elif novo_status == 'CANCELADO':
                campos_atualizar.append("data_cancelamento = NOW()")
            
            # Atualizar o status na tabela de pedidos
            query = f"UPDATE pedidos SET {', '.join(campos_atualizar)} WHERE id = %s"
            cursor.execute(query, params)
            
            # Registrar o histórico de alteração de status
            self._registrar_historico_status(pedido_id, novo_status, 
                                          observacao=f"Status alterado de {status_atual} para {novo_status}",
                                          usuario_id=1)  # TODO: Substituir pelo ID do usuário logado
            
            self.db.commit()
            return True, f"Status do pedido {pedido_id} atualizado para {novo_status} com sucesso!"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Erro ao atualizar status do pedido: {str(e)}"
        finally:
            cursor.close()
    
    
    def _registrar_pagamento_entrega(self, pedido_id):
        """Registra o pagamento quando o pedido é entregue.
        
        Args:
            pedido_id (int): ID do pedido entregue
        """
        cursor = self.db.cursor(dictionary=True)
        try:
            # Buscar informações do pedido
            cursor.execute("""
                SELECT p.total, p.forma_pagamento, p.data_abertura, p.cliente_id, p.cliente_nome
                FROM pedidos p 
                WHERE p.id = %s
            """, (pedido_id,))
            
            pedido = cursor.fetchone()
            if not pedido:
                print(f"Pedido {pedido_id} não encontrado para registrar pagamento")
                return
                
            valor = pedido['total']
            forma_pagamento = pedido['forma_pagamento']
            
            # Verificar se já existe pagamento para este pedido
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM pagamentos 
                WHERE pedido_id = %s
            """, (pedido_id,))
            
            if cursor.fetchone()['total'] > 0:
                print(f"Já existe pagamento registrado para o pedido {pedido_id}")
                return
                
            # Inserir o pagamento na tabela pagamentos
            cursor.execute("""
                INSERT INTO pagamentos 
                (pedido_id, forma_pagamento, valor, data_hora, tipo_venda) 
                VALUES (%s, %s, %s, NOW(), 'delivery')
            """, (
                pedido_id, 
                forma_pagamento, 
                valor
            ))
            
            # Atualizar o status do pedido para CONCLUIDO
            cursor.execute("""
                UPDATE pedidos 
                SET status = 'CONCLUIDO', 
                    data_fechamento = NOW()
                WHERE id = %s
            """, (pedido_id,))
            
            self.db.commit()
            print(f"Pagamento registrado com sucesso para o pedido {pedido_id} como tipo 'delivery'")
            
        except Exception as e:
            self.db.rollback()
            print(f"Erro ao registrar pagamento para o pedido {pedido_id}: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            cursor.close()
    
    def listar_pedidos_por_status(self, status=None):
        """Lista os pedidos de entrega filtrados por status.
        
        Args:
            status (str, optional): Status para filtrar os pedidos. Se None, retorna todos os pedidos.
            
        Returns:
            list: Lista de dicionários com os pedidos encontrados
        """
        cursor = self.db.cursor(dictionary=True)
        try:
            query = """
            SELECT 
                p.id,
                p.tipo,
                p.cliente_nome AS Cliente,
                p.cliente_telefone AS Telefone,
                p.data_abertura AS DataPedido,
                p.status,
                p.status_entrega,
                p.total,
                p.taxa_entrega,
                p.observacao,
                p.cliente_endereco AS Endereco,
                re.nome AS regiao_entrega,
                (
                    SELECT GROUP_CONCAT(
                        CONCAT(ip.quantidade, 'x ', pr.nome) 
                        SEPARATOR ', '
                    )
                    FROM itens_pedido ip
                    JOIN produtos pr ON ip.produto_id = pr.id
                    WHERE ip.pedido_id = p.id
                ) AS Itens
            FROM pedidos p
            LEFT JOIN regioes_entrega re ON p.regiao_id = re.id
            WHERE p.tipo = 'DELIVERY'
            """
            
            params = []
            if status:
                query += " AND p.status = %s"
                params.append(status)
            
            query += " ORDER BY p.data_abertura DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Erro ao listar pedidos por status: {e}")
            return []
        finally:
            cursor.close()
    
    def obter_regiao_por_id(self, regiao_id):
        """Obtém uma região de entrega pelo ID.
        
        Args:
            regiao_id (int): ID da região de entrega
            
        Returns:
            dict or None: Dados da região ou None se não encontrada
        """
        query = "SELECT * FROM regioes_entrega WHERE id = %s"
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(query, (regiao_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def salvar_regiao_entrega(self, dados):
        """Salva uma nova região de entrega ou atualiza uma existente.
        
        Args:
            dados (dict): Dados da região de entrega
            
        Returns:
            int: ID da região salva
        """
        if 'id' in dados and dados['id']:
            # Atualizar região existente
            query = """
            UPDATE regioes_entrega 
            SET nome = %s, 
                taxa_entrega = %s, 
                tempo_medio_entrega = %s, 
                ativo = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            params = (
                dados['nome'],
                float(dados['taxa_entrega']),
                int(dados['tempo_medio_entrega']),
                1 if dados.get('ativo', True) else 0,
                dados['id']
            )
            cursor = self.db.cursor()
            cursor.execute(query, params)
            self.db.commit()
            cursor.close()
            return dados['id']
        else:
            # Inserir nova região
            query = """
            INSERT INTO regioes_entrega (nome, taxa_entrega, tempo_medio_entrega, ativo)
            VALUES (%s, %s, %s, %s)
            """
            params = (
                dados['nome'],
                float(dados['taxa_entrega']),
                int(dados['tempo_medio_entrega']),
                1 if dados.get('ativo', True) else 0
            )
            cursor = self.db.cursor()
            cursor.execute(query, params)
            self.db.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
    
    def excluir_regiao_entrega(self, regiao_id):
        """Exclui uma região de entrega.
        
        Args:
            regiao_id (int): ID da região a ser excluída
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            query = "DELETE FROM regioes_entrega WHERE id = %s"
            cursor = self.db.cursor()
            cursor.execute(query, (regiao_id,))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao excluir região de entrega: {e}")
            return False
    
    def obter_regiao_por_bairro(self, bairro):
        """Obtém a região de entrega com base no bairro.
        
        Args:
            bairro (str): Nome do bairro
            
        Returns:
            dict or None: Dados da região ou None se não encontrada
        """
        if not bairro:
            return None
            
        try:
            # Retorna a primeira região ativa
            cursor = self.db.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM regioes_entrega 
                WHERE ativo = 1 
                ORDER BY id ASC 
                LIMIT 1
            """)
            
            return cursor.fetchone()
            
        except Exception as e:
            print(f"Erro ao buscar região para o bairro {bairro}: {e}")
            # Em caso de erro, retorna a primeira região ativa como fallback
            regioes = self.listar_regioes_entrega(ativo=True)
            return regioes[0] if regioes else None
            
        finally:
            if cursor:
                cursor.close()
                

                

    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
        
    def registrar_pedido(self, dados_pedido):
        """
        Registra um novo pedido de delivery no banco de dados.
        
        Args:
            dados_pedido (dict): Dicionário com os dados do pedido contendo:
                - cliente_id (int): ID do cliente
                - itens (list): Lista de itens do pedido
                - endereco (str): Endereço de entrega
                - bairro (str): Bairro de entrega
                - cidade (str): Cidade de entrega
                - referencia (str, optional): Ponto de referência
                - observacoes (str, optional): Observações do pedido
                - taxa_entrega (float): Valor da taxa de entrega
                - subtotal (float): Valor subtotal dos itens
                - desconto (float): Valor do desconto
                - valor_total (float): Valor total do pedido
                - forma_pagamento (str): Forma de pagamento
                - troco_para (float, optional): Valor para troco (se pagamento em dinheiro)
                
        Returns:
            tuple: (bool, str, int) Sucesso, mensagem de retorno e ID do pedido
        """
        try:
            # Usar a conexão já existente em self.db
            # Inserir o pedido na tabela pedidos
            query_pedido = """
            INSERT INTO pedidos (
                tipo, status, cliente_id, cliente_nome, cliente_telefone,
                cliente_endereco, taxa_entrega, total, data_abertura,
                tipo_cliente, observacao, status_entrega, regiao_id,
                previsao_entrega, entregador_id, forma_pagamento, troco_para
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Obter dados do cliente (assumindo que estão disponíveis em dados_pedido)
            cliente_id = dados_pedido.get('cliente_id')
            cliente_nome = dados_pedido.get('cliente_nome', '')
            cliente_telefone = dados_pedido.get('cliente_telefone', '')
            
            # Obter dados do endereço
            endereco = dados_pedido.get('endereco', '')
            bairro = dados_pedido.get('bairro', '')
            cidade = dados_pedido.get('cidade', '')
            referencia = dados_pedido.get('referencia', '')
            
            # Construir endereço completo
            endereco_completo = f"{endereco}, {bairro}, {cidade}"
            if referencia:
                endereco_completo += f" - {referencia}"
            
            # Obter a região de entrega com base no bairro
            regiao = self.obter_regiao_por_bairro(bairro)
            regiao_id = regiao['id'] if regiao else None
            
            # Calcular previsão de entrega (30 minutos por padrão, ou o tempo da região)
            tempo_entrega = regiao['tempo_medio_entrega'] if regiao and 'tempo_medio_entrega' in regiao else 30
            previsao_entrega = (datetime.datetime.now() + datetime.timedelta(minutes=tempo_entrega)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Obter dados do pagamento
            forma_pagamento = dados_pedido.get('forma_pagamento', 'dinheiro')
            # Usar o valor do troco passado em dados_pedido, ou calcular com base no valor recebido
            if 'troco' in dados_pedido and dados_pedido['troco'] is not None:
                troco_para = float(dados_pedido['troco'])
            elif 'valor_recebido' in dados_pedido and dados_pedido['valor_recebido'] is not None:
                troco_para = float(dados_pedido['valor_recebido']) - float(dados_pedido.get('valor_total', 0))
            else:
                troco_para = 0.0
            
            # Definir status do pedido como PENDENTE por padrão
            # O status será atualizado posteriormente quando o pagamento for confirmado
            status_pedido = 'PENDENTE'
            
            # Preparar os parâmetros para a inserção do pedido
            params_pedido = (
                'DELIVERY',  # tipo
                status_pedido,  # status (PENDENTE ou PAGO)
                cliente_id,
                cliente_nome,
                cliente_telefone,
                endereco_completo,  # endereco
                float(dados_pedido.get('taxa_entrega', 0)),  # taxa_entrega
                float(dados_pedido.get('valor_total', 0)),  # total
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # data_abertura
                'PESSOA_FISICA',  # tipo_cliente
                dados_pedido.get('observacoes', ''),  # observacao
                'AGUARDANDO_CONFIRMACAO',  # status_entrega (AGUARDANDO_CONFIRMACAO, EM_PREPARO, EM_ROTA, ENTREGUE, CANCELADO)
                regiao_id,  # regiao_id
                previsao_entrega,  # previsao_entrega
                None,  # entregador_id (pode ser definido posteriormente)
                forma_pagamento,  # forma_pagamento
                troco_para  # troco_para
            )
            
            # Executar a inserção do pedido
            cursor = self.db.cursor()
            try:
                cursor.execute(query_pedido, params_pedido)
                pedido_id = cursor.lastrowid
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise Exception(f"Erro ao registrar pedido: {str(e)}")
            finally:
                cursor.close()
            
            # Inserir os itens do pedido na tabela itens_pedido
            query_itens = """
            INSERT INTO itens_pedido (
                pedido_id, produto_id, quantidade, valor_unitario, 
                subtotal, observacoes, garcom_id, data_hora,
                valor_total, status
            ) VALUES (%s, %s, %s, %s, %s, %s, NULL, %s, %s, %s)
            """
            
            # Preparar os parâmetros dos itens e opções
            itens_params = []
            opcoes_params = []
            data_hora_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Primeiro, inserir todos os itens para obter seus IDs
            for item in dados_pedido['itens']:
                quantidade = float(item.get('quantidade', 1))
                valor_unitario = float(item.get('valor_unitario', 0))
                subtotal = quantidade * valor_unitario
                valor_total = subtotal  # Pode ser ajustado se houver descontos/acréscimos
                
                # Extrair o ID do produto do formato 'nome/id' se necessário
                produto_id = item.get('produto_id', '0')
                if '/' in str(produto_id):
                    produto_id = str(produto_id).split('/')[-1]
                
                # Converter para inteiro e validar o ID do produto
                try:
                    produto_id_int = int(produto_id) if str(produto_id).isdigit() else 0
                    
                    # Verificar se o produto_id é válido (não zero)
                    if produto_id_int <= 0:
                        raise ValueError(f"ID de produto inválido: {produto_id}")
                        
                    # Inserir o item e obter o ID
                    item_params = (
                        int(pedido_id),  # pedido_id
                        produto_id_int,  # produto_id
                        quantidade,  # quantidade
                        valor_unitario,  # valor_unitario
                        subtotal,  # subtotal
                        str(item.get('observacoes', '')),  # observacoes
                        # garcom_id é NULL para pedidos de delivery
                        data_hora_atual,  # data_hora
                        valor_total,  # valor_total
                        'PENDENTE'  # status
                    )
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar produto_id {produto_id}: {e}")
                    # Pular itens com ID de produto inválido
                    continue
                
                # Executar a inserção do item para obter o ID
                cursor = self.db.cursor()
                try:
                    cursor.execute(query_itens, item_params)
                    venda_item_id = cursor.lastrowid
                    self.db.commit()
                    
                    # Se o item tiver opções, preparar para inserir na tabela venda_item_opcoes
                    if 'opcoes' in item and item['opcoes'] and venda_item_id:
                        for opcao in item['opcoes']:
                            opcoes_params.append((
                                venda_item_id,
                                int(opcao.get('opcao_id', 0)),
                                int(opcao.get('grupo_id', 0)),
                                float(opcao.get('preco_adicional', 0.0))
                            ))
                except Exception as e:
                    self.db.rollback()
                    print(f"Erro ao inserir item do pedido: {e}")
                    raise
                finally:
                    cursor.close()
            
            # Inserir as opções dos itens, se houver
            if opcoes_params:
                query_opcoes = """
                INSERT INTO itens_pedido_opcoes 
                (item_pedido_id, opcao_id, grupo_id, nome, preco_adicional)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                # Obter os nomes das opções e grupos para inserção
                opcoes_com_nomes = []
                for opcao in opcoes_params:
                    item_id, opcao_id, grupo_id, preco_adicional = opcao
                    
                    # Obter o nome da opção
                    try:
                        cursor = self.db.cursor(dictionary=True)
                        cursor.execute("SELECT nome FROM opcoes_itens WHERE id = %s", (opcao_id,))
                        resultado = cursor.fetchone()
                        opcao_nome = resultado['nome'] if resultado else "Opção Desconhecida"
                    except Exception as e:
                        print(f"Erro ao obter nome da opção {opcao_id}: {e}")
                        opcao_nome = "Opção Desconhecida"
                    finally:
                        if cursor:
                            cursor.close()
                    
                    # Adicionar a opção com o nome obtido
                    opcoes_com_nomes.append((
                        item_id,
                        opcao_id,
                        grupo_id,
                        opcao_nome,
                        preco_adicional
                    ))
                
                # Executar a inserção em lote
                cursor = self.db.cursor()
                try:
                    cursor.executemany(query_opcoes, opcoes_com_nomes)
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    print(f"Erro ao inserir opções do pedido: {e}")
                    raise
                finally:
                    cursor.close()
            
            # Registrar o histórico de status inicial do pedido
            status_inicial = 'AGUARDANDO_CONFIRMACAO'
            self._registrar_historico_status(
                pedido_id=pedido_id,
                status=status_inicial,
                observacao=f"Pedido de entrega criado. Previsão de entrega: {previsao_entrega}",
                usuario_id=dados_pedido.get('usuario_id', 1)  # ID do usuário que criou o pedido
            )
            
            # Se o pagamento for aprovado, registrar também o status de pagamento
            if status_pedido == 'PAGO':
                self._registrar_historico_status(
                    pedido_id=pedido_id,
                    status='PAGO',
                    observacao=f"Pagamento aprovado via {forma_pagamento}",
                    usuario_id=dados_pedido.get('usuario_id', 1)
                )
            
            # Retornar sucesso e o ID do pedido
            return True, f"Pedido registrado com sucesso! Nº {pedido_id}", pedido_id
            
        except Exception as e:
            print(f"Erro ao registrar pedido: {e}")
            return False, f"Erro ao registrar pedido: {str(e)}", None
