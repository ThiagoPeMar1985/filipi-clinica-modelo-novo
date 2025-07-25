"""
Módulo para gerenciamento de impressão de cupons e relatórios.
"""
import win32print
import win32ui
import win32con
import win32api
import win32gui
import datetime
import os
from pathlib import Path

class GerenciadorImpressao:
    """Classe para gerenciar a impressão de cupons e relatórios."""
    
    def __init__(self, config_controller=None):
        """
        Inicializa o gerenciador de impressão.
        
        Args:
            config_controller: Controlador de configurações para obter as impressoras configuradas
        """
        self.config_controller = config_controller
        self.impressoras = {}
        self._carregar_configuracoes()
        
        # Inicializa o mapeamento de tipos vazio - será carregado do banco
        self.mapeamento_tipos = {}
        self._carregar_mapeamento_banco()  
        
    def _carregar_mapeamento_banco(self):
        """
        Carrega o mapeamento de tipos de produtos para impressoras do banco de dados.
        
        Returns:
            bool: True se o carregamento foi bem-sucedido, False caso contrário
        """
        try:
            import mysql.connector
            from src.db.config import get_db_config
            
            db_config = get_db_config()
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Busca todos os mapeamentos de tipos para impressoras
            cursor.execute("""
                SELECT tp.nome as tipo, it.impressora_id 
                FROM impressoras_tipos it
                JOIN tipos_produtos tp ON it.tipo_id = tp.id
            """)
            
            resultados = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if resultados:
                self.mapeamento_tipos = {item['tipo']: str(item['impressora_id']) for item in resultados}
    
                return True
                
            print("[AVISO] Nenhum mapeamento encontrado no banco de dados")
            return False
            
        except Exception as e:
            print(f"[ERRO] Falha ao carregar mapeamento do banco: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _carregar_configuracoes(self):
        """Carrega as configurações de impressoras do sistema."""
        # Inicializa dicionário vazio de impressoras
        self.impressoras = {
            'impressora 1': '',  # Padrão para cupom fiscal
            'impressora 2': '',
            'impressora 3': '',
            'impressora 4': '',
            'impressora 5': '',
            'impressora 6': ''
        }
        
        # Verifica se temos um config_controller válido
        if not self.config_controller:
            # Nenhum config_controller fornecido ao GerenciadorImpressao
            pass
        else:
            # Verifica se o config_controller tem o método necessário
            if hasattr(self.config_controller, 'carregar_config_impressoras'):
                try:
                    config = self.config_controller.carregar_config_impressoras()
                    
                    if config and isinstance(config, dict):
                        # Mapeia as configurações para as chaves corretas
                        for i in range(1, 7):
                            chave = f'impressora {i}'
                            if chave in config and config[chave]:
                                self.impressoras[chave] = config[chave]
                        
                        return
                    
                except Exception as e:
                    print(f"[ERRO] Erro ao carregar configurações de impressão: {e}")
        
        # Se chegou aqui, não conseguiu carregar as configurações do config_controller
        # Tenta obter a impressora padrão do sistema
        try:
            impressora_padrao = win32print.GetDefaultPrinter()
            
            # Define a impressora padrão para todos os tipos
            for chave in self.impressoras:
                self.impressoras[chave] = impressora_padrao
            
        except Exception as e:
            # Mantém o dicionário vazio em caso de erro
            self.impressoras = {}
        
    def imprimir_cupom_fiscal(self, venda, itens, pagamentos):
        """
        Imprime um cupom fiscal para a venda finalizada.
        
        Args:
            venda: Dicionário com informações da venda (valor_total, desconto, valor_final, etc)
            itens: Lista de itens da venda (produto, quantidade, valor_unitario, valor_total)
            pagamentos: Lista de pagamentos realizados (forma_nome, valor)
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        try:
            # Sempre usa a impressora 1 para cupom fiscal
            impressora = self.impressoras.get('impressora 1', '')
            if not impressora:
                print("[ERRO] Nenhuma impressora configurada para o cupom fiscal (impressora 1)")
                return False
            
            # Gerar o conteúdo do cupom
            conteudo = self._gerar_conteudo_cupom(venda, itens, pagamentos)
            
            # Imprimir o conteúdo
            return self._imprimir_texto(impressora, conteudo)
            
        except Exception as e:
            print(f"[ERRO] Erro ao imprimir cupom fiscal: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def imprimir_comandas_por_tipo(self, venda, itens):
        """
        Imprime comandas agrupadas por impressora, juntando todos os itens da mesma impressora.
        """
        try:
            if not itens:
                return True

            
            
            # Dicionário para agrupar itens por impressora
            itens_por_impressora = {}
            
            # Agrupa os itens por impressora
            for item in itens:
                tipo = str(item.get('tipo', 'Outros')).strip()
               
                
                # Padroniza o nome do tipo
                if tipo.lower() == 'sobremesa':
                    tipo = 'Sobremesas'
                
                # Obtém o ID da impressora para este tipo
                impressora_id = self.mapeamento_tipos.get(tipo, '5')  # Default para 'Outros' se não encontrar

                if impressora_id == '6':
                    continue
                
                # Inicializa a lista de itens para esta impressora se não existir
                if impressora_id not in itens_por_impressora:
                    itens_por_impressora[impressora_id] = []
                
                # Adiciona o item à impressora correspondente
                itens_por_impressora[impressora_id].append(item)
            
            # Imprime cada grupo de itens na impressora correspondente
            for impressora_id, itens_impressora in itens_por_impressora.items():
                
                # Obtém o nome da impressora
                impressora = self.impressoras.get(f'impressora {impressora_id}')
                
                if not impressora:
                    print(f"[ERRO] Impressora {impressora_id} não configurada")
                    continue
                    
                # Gera e imprime o conteúdo com todos os itens juntos
                conteudo = self._gerar_conteudo_comanda(venda, itens_impressora, f"Impressora {impressora_id}")
                self._imprimir_texto(impressora, conteudo)
                
            return True
            
        except Exception as e:
            print(f"[ERRO] Falha ao imprimir comandas por tipo: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def _gerar_conteudo_comanda(self, venda, itens, tipo_produto):
        """
        Gera o conteúdo da comanda para um tipo específico de produto.
        
        Args:
            venda: Dicionário com informações da venda
            itens: Lista de itens da venda do tipo específico
            tipo_produto: Tipo de produto (Bar, Cozinha, Sobremesas, Outros)
            
        Returns:
            str: Conteúdo formatado da comanda
        """
        # Largura máxima para a comanda (48 caracteres para papel de 80mm)
        largura = 48
        
        # Função auxiliar para garantir que o texto não ultrapasse a largura
        def cortar_texto(texto, max_caracteres=largura):
            return str(texto)[:max_caracteres].strip()
        
        # Cabeçalho
        conteudo = []
        
        conteudo.append("QUIOSQUE AQUARIUS".center(largura))
        conteudo.append("=" * largura)
        # Garantir que o número da mesa seja exibido corretamente
        mesa_num = venda.get('mesa_numero') or venda.get('numero_mesa') or venda.get('num_mesa') or venda.get('mesa')
        if not mesa_num:
            # Se ainda não encontrou, tenta buscar pelo ID do pedido na tabela pedidos e depois na tabela mesas
            if 'id' in venda:
                try:
                    import mysql.connector
                    from src.db.config import get_db_config
                    
                    db_config = get_db_config()
                    conn = mysql.connector.connect(**db_config)
                    cursor = conn.cursor(dictionary=True)
                    
                    # Primeiro busca o ID da mesa na tabela pedidos
                    cursor.execute("SELECT mesa_id FROM pedidos WHERE id = %s", (venda['id'],))
                    pedido = cursor.fetchone()
                    
                    if pedido and pedido['mesa_id']:
                        # Agora busca o número da mesa na tabela mesas
                        cursor.execute("SELECT numero FROM mesas WHERE id = %s", (pedido['mesa_id'],))
                        mesa = cursor.fetchone()
                        if mesa:
                            mesa_num = mesa['numero']
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Erro ao buscar número da mesa: {e}")
                    mesa_num = 'X'
            else:
                mesa_num = 'X'
        
        # Comandos ESC/POS para formatação
        fonte_dupla = "\x1D\x21\x11"  # Altura e largura duplas
        fonte_normal = "\x1D\x21\x00"  # Volta ao normal
        centralizado = "\x1B\x61\x01"  # Centraliza o texto (ESC a 1)
        esquerda = "\x1B\x61\x00"      # Alinha à esquerda (ESC a 0)
        
        # Verificar o tipo de venda
        tipo_venda = venda.get('tipo', '').lower()
        if tipo_venda == 'avulsa':
            # Centraliza e usa fonte dupla para o título (Bematech MP-4200 TH)
            # Junta tudo em uma única string para evitar quebras de linha
            titulo = centralizado + fonte_dupla + "VENDA AVULSA" + fonte_normal + esquerda
            conteudo.append(titulo)
        elif tipo_venda == 'delivery':
            # Centraliza e usa fonte dupla para o título (Bematech MP-4200 TH)
            # Junta tudo em uma única string para evitar quebras de linha
            titulo = centralizado + fonte_dupla + "DELIVERY" + fonte_normal + esquerda
            conteudo.append(titulo)
        else:
            # Usa comandos ESC/POS para centralizar e aumentar a fonte
            # Mostra apenas o número da mesa, sem o tipo de produto
            titulo = centralizado + fonte_dupla + f"MESA {mesa_num}" + fonte_normal + esquerda
            conteudo.append(titulo)
        conteudo.append("=" * largura)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
        # Atendente - verifica em várias fontes possíveis
        nome_atendente = 'Sistema'  # Valor padrão
        
        # Verifica as fontes possíveis em ordem de prioridade
        fontes_nome = [
            venda.get('atendente_nome'),
            venda.get('usuario_nome'),
            venda.get('usuario', {}).get('nome') if isinstance(venda.get('usuario'), dict) else None,
            venda.get('usuario').nome if hasattr(venda.get('usuario'), 'nome') else None
        ]
        
        # Pega o primeiro valor não nulo
        for fonte in fontes_nome:
            if fonte:
                nome_atendente = fonte
                break
                
        # Se ainda for um dicionário, tenta obter o nome
        if isinstance(nome_atendente, dict) and 'nome' in nome_atendente:
            nome_atendente = nome_atendente['nome']
            
        # Garante que é uma string
        nome_atendente = str(nome_atendente).strip()
        
        # Adiciona o nome do atendente à comanda
        conteudo.append(f"Atendente: {nome_atendente}")
            
        # Se for delivery, mostra o nome do cliente
        if tipo_venda == 'delivery' and venda.get('cliente_nome'):
            conteudo.append(f"Cliente: {venda['cliente_nome']}")
        
        # Cabeçalho dos itens
        conteudo.append("-" * largura)
        conteudo.append("DESCRIÇÃO                             QTD")
        conteudo.append("-" * largura)
        
        # Agrupa itens iguais
        itens_agrupados = {}
        
        # Primeiro, processa todos os itens para agrupar
        for item in itens:
            # Tenta obter o nome do item de diferentes maneiras
            nome = item.get('nome') or item.get('produto_nome') or item.get('nome_produto')
            
            # Se ainda não tiver nome, tenta buscar pelo ID do produto
            if not nome and 'produto_id' in item:
                try:
                    import mysql.connector
                    from src.db.config import get_db_config
                    
                    db_config = get_db_config()
                    conn = mysql.connector.connect(**db_config)
                    cursor = conn.cursor(dictionary=True)
                    
                    cursor.execute("SELECT nome FROM produtos WHERE id = %s", (item['produto_id'],))
                    produto = cursor.fetchone()
                    if produto:
                        nome = produto['nome']
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    nome = f"Produto ID: {item.get('produto_id', 'N/A')}"
            
            # Se ainda não tiver nome, usa um valor padrão
            if not nome:
                nome = 'Produto sem nome'
            
            # Limita o tamanho do nome para 30 caracteres
            nome = str(nome)[:30].upper()
            qtd = int(item.get('quantidade', 1))
            
            # Cria uma chave única para o item baseada no nome e nas opções/observações
            chave_item = nome
            
            # Adiciona opções à chave do item
            opcoes = []
            if 'opcoes' in item and item['opcoes']:
                for opcao in item['opcoes']:
                    nome_opcao = str(opcao.get('nome', 'Opção sem nome')).strip()
                    if nome_opcao:
                        opcoes.append(nome_opcao)
            
            # Adiciona observações à chave do item
            observacoes = []
            if 'observacoes' in item and item['observacoes']:
                obs = str(item['observacoes']).strip()
                if obs:
                    observacoes = [o.strip() for o in obs.split('\n') if o.strip()]
            
            chave_item = f"{nome}__{'_'.join(opcoes)}__{'_'.join(observacoes)}"
            
            # Se o item já existe, incrementa a quantidade
            if chave_item in itens_agrupados:
                itens_agrupados[chave_item]['quantidade'] += qtd
            else:
                itens_agrupados[chave_item] = {
                    'nome': nome,
                    'quantidade': qtd,
                    'opcoes': opcoes,
                    'observacoes': observacoes
                }
        
        # Agora imprime os itens agrupados
        for chave, dados in itens_agrupados.items():
            nome = dados['nome']
            qtd = dados['quantidade']
            
            # Formata a linha do item sem numeração em fonte maior
            linha = "\x1B!\x30" + f"{nome.upper():<20} {qtd:>3}" + "\x1B!\x00" + fonte_normal
            conteudo.append(linha)
            
            # Adiciona as opções do item
            for opcao in dados['opcoes']:
                if opcao:
                    # Usa um hífen simples em vez de seta para melhor compatibilidade
                    conteudo.append(f"    - {opcao[:30]}")
            
            # Adiciona as observações do item
            for obs in dados['observacoes']:
                if obs:
                    # Usa um hífen simples em vez de seta para melhor compatibilidade
                    conteudo.append(f"    - {obs[:30]}")

        conteudo.append("-" * largura)            

        return "\n".join(conteudo)
    
    def imprimir_demonstrativo_delivery(self, venda, itens, pagamentos):
        """
        Imprime um demonstrativo específico para delivery com informações do cliente e endereço.
        
        Args:
            venda: Dicionário com informações da venda e do cliente
            itens: Lista de itens do pedido
            pagamentos: Lista de pagamentos realizados
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        try:
            impressora = self.impressoras.get('cupom', '')
            if not impressora:
                # Se não houver impressora de cupom configurada, tentar usar a impressora padrão
                try:
                    impressora = win32print.GetDefaultPrinter()
                    # Usando impressora padrão para demonstrativo de delivery: {impressora}
                except Exception as e:
                    # Nenhuma impressora disponível para demonstrativo de delivery: {e}
                    return False
                
            if not impressora:
                # Nenhuma impressora configurada para demonstrativo de delivery.
                return False
            
            # Gerar o conteúdo do demonstrativo de delivery
            conteudo = self._gerar_conteudo_demonstrativo_delivery(venda, itens, pagamentos)
            
            # Imprimir o conteúdo
            resultado = self._imprimir_texto(impressora, conteudo)
            
            return resultado
        except Exception as e:
            print(f"Erro ao imprimir demonstrativo de delivery: {e}")
            return False
    
    def _gerar_conteudo_demonstrativo_delivery(self, venda, itens, pagamentos):
        """
        Gera o conteúdo do demonstrativo de delivery com informações do cliente e endereço.
        
        Args:
            venda: Dicionário com informações da venda e do cliente
            itens: Lista de itens do pedido
            pagamentos: Lista de pagamentos realizados
            
        Returns:
            str: Conteúdo formatado do demonstrativo
        """
        # Largura para papel de 80mm (48 caracteres)
        largura = 48
        
        # Busca os dados da empresa usando o CadastroDB
        try:
            from src.db.database import db
            from src.db.cadastro_db import CadastroDB
            
            # Obtém a conexão do banco de dados
            conn = db.get_connection()
            
            # Cria uma instância do CadastroDB
            cadastro_db = CadastroDB(conn)
            
            # Obtém os dados da empresa
            empresa_db = cadastro_db.obter_empresa()
            
            if empresa_db:
                empresa = {
                    'nome_fantasia': empresa_db.get('nome_fantasia', 'LOJA SEM NOME').strip().upper(),
                    'cnpj': empresa_db.get('cnpj', '').strip(),
                  
                }
            else:
                empresa = {
                    'nome_fantasia': 'LOJA SEM NOME',
                    'cnpj': '00.000.000/0001-00',
                }
                 
                
        except Exception as e:
            print(f"Erro ao buscar dados da empresa: {e}")
            empresa = {
                'nome_fantasia': 'LOJA SEM NOME',
                'cnpj': '00.000.000/0001-00',
               
            }
        
        # Inicializa o conteúdo do cupom
        conteudo = []
        
        # Linha de separação superior
        conteudo.append("=" * largura)
        
        # Nome da empresa centralizado
        conteudo.append(empresa['nome_fantasia'].center(largura))
        
        # CNPJ centralizado
        if empresa['cnpj']:
            conteudo.append(empresa['cnpj'].center(largura))
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Data/hora e usuário logado
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        usuario = venda.get('usuario_nome', 'OPERADOR')
        
        # Formata a linha de data/hora e usuário
        linha_dh_usuario = f"D/H: {data_hora}          nome: {usuario.upper()}"
        conteudo.append(linha_dh_usuario)
        
        # Define o tipo de venda como DELIVERY
        conteudo.append("TIPO: DELIVERY")
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Informações do cliente

        conteudo.append("DADOS DO CLIENTE".center(largura))
        conteudo.append("-" * largura)
        
        if venda.get('cliente_nome'):
            conteudo.append(f"Nome: {venda['cliente_nome']}")
        if venda.get('cliente_telefone'):
            conteudo.append(f"Telefone: {venda['cliente_telefone']}")
        
        if venda.get('endereco_entrega'):
            # Se veio o endereço completo, adiciona como está
            conteudo.append(venda['endereco_entrega'])
            
            # Adiciona cidade e referência se existirem
            endereco_extra = []
            if venda.get('cidade'):
                endereco_extra.append(f"Cidade: {venda['cidade']}")
            if venda.get('ponto_referencia'):
                endereco_extra.append(f"Ref: {venda['ponto_referencia']}")

            if endereco_extra:
                conteudo.append(", ".join(endereco_extra))
        else:
            # Primeira linha: Rua, Número, Bairro
            endereco_parts = []
            if venda.get('endereco'):
                endereco_parts.append(f"Rua: {venda['endereco']}")
            if venda.get('numero'):
                endereco_parts.append(f"Nº: {venda['numero']}")
            if venda.get('bairro'):
                endereco_parts.append(f"Bairro: {venda['bairro']}")
            
            if endereco_parts:
                conteudo.append(", ".join(endereco_parts))
            
            # Segunda linha: Cidade e Referência
            segunda_linha_parts = []
            if venda.get('cidade'):
                segunda_linha_parts.append(f"Cidade: {venda['cidade']}")
            if venda.get('ponto_referencia'):
                segunda_linha_parts.append(f"Ref: {venda['ponto_referencia']}")
            
            if segunda_linha_parts:
                conteudo.append(", ".join(segunda_linha_parts))
        
        
        # Linha de separação
        conteudo.append("-" * largura)
        # Itens

        # Cabeçalho da tabela de itens
        cabecalho = f"{'DESCRIÇÃO':<25} {'QTD':>2} {'VALOR':>9} {'SUBTOTAL':>9}"
        conteudo.append(cabecalho)
        conteudo.append("-" * largura)
        total = 0.0
        
        for item in itens:
            # Nome do produto (limita a 25 caracteres)
            nome = item.get('nome', 'Produto sem nome')
            if len(nome) > 25:
                nome = nome[:25] + '...'
            
            # Quantidade (padrão 1 se não informado)
            qtd = int(item.get('quantidade', 1))
            
            # Preço unitário
            preco = self._obter_preco_item(item)
            
            # Calcula subtotal do item
            subtotal_item = qtd * preco
            total += subtotal_item
            
            # Formata a linha do item
            linha_item = f"{nome:<25} {qtd:>2}x {preco:>9.2f} {subtotal_item:>9.2f}"
            conteudo.append(linha_item)
            
            
        
        # Total
        # Formata o valor com 2 casas decimais
        conteudo.append("-" * largura)
        valor_formatado = f"{total:7.2f}"
        # Cria a string do total alinhada à esquerda
        linha_total = f"{'TOTAL:':<38}R$ {valor_formatado}"
        conteudo.append(linha_total)
        
        # Verifica se há taxa de entrega
        taxa_entrega = float(venda.get('taxa_entrega', 0))
        if taxa_entrega > 0:
            # Formata a taxa de entrega com 2 casas decimais
            taxa_formatada = f"{taxa_entrega:7.2f}"
            # Cria a string da taxa de entrega alinhada à esquerda
            linha_taxa = f"{'TAXA DE ENTREGA:':<38}R$ {taxa_formatada}"
            conteudo.append(linha_taxa)
            
            # Atualiza o total com a taxa de entrega
            total_com_taxa = total + taxa_entrega
            total_formatado = f"{total_com_taxa:7.2f}"
            linha_total_com_taxa = f"{'TOTAL + ENTREGA:':<38}R$ {total_formatado}"
            conteudo.append(linha_total_com_taxa)
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Forma de pagamento
        if pagamentos and len(pagamentos) > 0:

            conteudo.append("FORMA DE PAGAMENTO".center(largura, ' '))
            conteudo.append("-" * largura)
            
            # Mapeamento das formas de pagamento para nomes formatados
            FORMAS_PAGAMENTO = {
                'credito': 'Cartao de credito',
                'debito': 'Cartao de debito',
                'pix': 'Pix',
                'dinheiro': 'Dinheiro',
               
            }
            
            # Primeiro, processa os pagamentos normais
            for pagamento in pagamentos:
                forma = pagamento.get('forma_nome', '').lower()
                
                # Se for troco, pula para processar junto com o pagamento em dinheiro
                if forma == 'troco':
                    continue
                    
                # Formata a forma de pagamento
                forma_formatada = FORMAS_PAGAMENTO.get(forma, forma.capitalize())
                if forma_formatada == forma:  # Se não encontrou no mapeamento, formata manualmente
                    forma_formatada = forma.lower().replace('_', ' ').title()
                    
                valor = float(pagamento.get('valor', 0))
                
                # Se for dinheiro, verifica se tem troco
                if forma == 'dinheiro':
                    # Verifica se existe um valor de troco no dicionário da venda
                    troco = float(venda.get('troco_para', 0))
                    
                    # Verifica se há um pagamento de troco na lista de pagamentos
                    for pag in pagamentos:
                        if pag.get('forma_nome', '').lower() == 'troco':
                            troco = float(pag.get('valor', 0))
                            break
                    
                    if troco > 0:
                        valor_total_pago = valor + troco
                        conteudo.append(f"{forma_formatada.upper():<15} R$ {valor_total_pago:>9.2f}")
                        conteudo.append(f"{'Troco:':<15} R$ {troco:>9.2f}")
                    else:
                        # Se não tiver troco, mostra apenas o valor
                        conteudo.append(f"{forma_formatada.upper():<15} R$ {valor:>9.2f}")
                elif forma != 'troco':  # Ignora entradas de troco, pois já foram processadas
                    # Para outras formas de pagamento, mostra apenas o valor
                    conteudo.append(f"{forma_formatada.upper():<15} R$ {valor:>9.2f}")
        
        # Rodapé
     
        conteudo.append("-" * largura)
        conteudo.append("Obrigado pela preferência!".center(largura))
        conteudo.append("Volte sempre!".center(largura))
        conteudo.append(f"{datetime.datetime.now().strftime('Impresso em %d/%m/%Y %H:%M')}".center(largura))
        
        return "\n".join(conteudo)

        
    def _gerar_conteudo_cupom(self, venda, itens, pagamentos):
        """
        Gera o conteúdo do cupom fiscal otimizado para papel de 80mm.
        
        Args:
            venda: Dicionário com informações da venda
            itens: Lista de itens da venda
            pagamentos: Lista de pagamentos realizados
            
        Returns:
            str: Conteúdo formatado do cupom
        """
        # Mapeamento das formas de pagamento para nomes formatados
        FORMAS_PAGAMENTO = {
            'credito': 'CARTÃO CRÉDITO',
            'cartao_credito': 'CARTÃO CRÉDITO',
            'debito': 'CARTÃO DÉBITO',
            'cartao_debito': 'CARTÃO DÉBITO',
            'pix': 'PIX',
            'dinheiro': 'DINHEIRO',
            'vale_alimentacao': 'VALE ALIMENTAÇÃO',
            'vale_refeicao': 'VALE REFEIÇÃO',
            'outro': 'OUTRA FORMA',
        }
        
        # Largura para papel de 80mm (48 caracteres)
        largura = 48
        
        # Busca os dados da empresa usando o CadastroDB
        try:
            from src.db.database import db
            from src.db.cadastro_db import CadastroDB
            
            # Obtém a conexão do banco de dados
            conn = db.get_connection()
            
            # Cria uma instância do CadastroDB
            cadastro_db = CadastroDB(conn)
            
            # Obtém os dados da empresa
            empresa_db = cadastro_db.obter_empresa()
            
            if empresa_db:
                empresa = {
                    'nome_fantasia': empresa_db.get('nome_fantasia', 'LOJA SEM NOME').strip().upper(),
                    'cnpj': empresa_db.get('cnpj', '').strip()
                }
            else:
                empresa = {
                    'nome_fantasia': 'LOJA SEM NOME',
                    'cnpj': ''
                }
                
        except Exception as e:
            print(f"Erro ao buscar dados da empresa: {e}")
            empresa = {
                'nome_fantasia': 'LOJA SEM NOME',
                'cnpj': ''
            }
        
        # Inicializa o conteúdo do cupom
        conteudo = []
        
        # Linha de separação superior
        conteudo.append("=" * largura)
        
        # Nome da empresa centralizado
        conteudo.append(empresa['nome_fantasia'].center(largura))
        
        # CNPJ centralizado
        if empresa['cnpj']:
            conteudo.append(empresa['cnpj'].center(largura))
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Data/hora e usuário logado
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        usuario = venda.get('usuario_nome', 'OPERADOR')
        
        # Formata a linha de data/hora e usuário
        linha_dh_usuario = f"D/H: {data_hora}          nome: {usuario.upper()}"
        conteudo.append(linha_dh_usuario)
        
        # Define o tipo de venda baseado no tipo da venda
        tipo_venda = venda.get('tipo', 'BALCÃO').upper()
        if tipo_venda == 'AVULSA':
            tipo_venda = 'BALCÃO'
        elif tipo_venda == 'DELIVERY':
            tipo_venda = 'DELIVERY'
        elif tipo_venda == 'MESA':
            tipo_venda = 'MESA'
        
        conteudo.append(f"TIPO: {tipo_venda}")
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Cabeçalho da tabela de itens
        cabecalho = f"{'DESCRIÇÃO':<25} {'QTD':>2} {'VALOR':>9} {'SUBTOTAL':>9}"
        conteudo.append(cabecalho)
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Agrupa itens iguais
        itens_agrupados = {}
        
        for item in itens:
            # Busca o nome do produto em diferentes campos possíveis
            nome = 'Produto sem nome'
            for campo_nome in ['nome_produto', 'produto_nome', 'nome', 'descricao', 'descrição']:
                if campo_nome in item and item[campo_nome]:
                    nome = str(item[campo_nome]).strip()
                    break
            
            # Se o nome for vazio, pula para o próximo item
            if not nome:
                continue
                
            # Obtém o preço unitário
            preco = 0.0
            for campo in ['valor_unitario', 'preco_unitario', 'preco', 'valor', 'valor_venda', 'preco_venda']:
                if campo in item and item[campo] is not None:
                    try:
                        preco = float(item[campo])
                        break
                    except (ValueError, TypeError):
                        continue
            
            # Quantidade (padrão 1 se não informado)
            qtd = int(item.get('quantidade', 1))
            
            # Se o item já existe no dicionário, soma a quantidade
            if nome in itens_agrupados:
                itens_agrupados[nome]['quantidade'] += qtd
                itens_agrupados[nome]['subtotal'] += qtd * preco
            else:
                itens_agrupados[nome] = {
                    'quantidade': qtd,
                    'preco': preco,
                    'subtotal': qtd * preco
                }
        
        # Calcula o total
        total = sum(item['subtotal'] for item in itens_agrupados.values())
        
        # Adiciona os itens agrupados ao conteúdo do cupom
        for nome, dados in itens_agrupados.items():
            qtd = dados['quantidade']
            preco = dados['preco']
            subtotal_item = dados['subtotal']
            
            # Limita o tamanho do nome para 25 caracteres
            nome_exibicao = nome
            if len(nome_exibicao) > 25:
                nome_exibicao = nome_exibicao[:25] + '...'
            
            # Formata a linha do item
            linha_item = f"{nome_exibicao:<25} {qtd:>2}x {preco:>9.2f} {subtotal_item:>9.2f}"
            conteudo.append(linha_item)
        

        # Total
        # Formata o valor com 2 casas decimais
        conteudo.append("-" * largura)
        valor_formatado = f"{total:7.2f}"
        # Cria a string do total alinhada à esquerda
        linha_total = f"{'TOTAL:':<38}R$ {valor_formatado}"
        conteudo.append(linha_total)
        
        # Verifica se há taxa de entrega
        taxa_entrega = float(venda.get('taxa_entrega', 0))
        if taxa_entrega > 0:
            # Formata a taxa de entrega com 2 casas decimais
            taxa_formatada = f"{taxa_entrega:7.2f}"
            # Cria a string da taxa de entrega alinhada à esquerda
            linha_taxa = f"{'TAXA DE ENTREGA:':<38}R$ {taxa_formatada}"
            conteudo.append(linha_taxa)
            
            # Atualiza o total com a taxa de entrega
            total += taxa_entrega
            total_formatado = f"{total:7.2f}"
            linha_total_com_taxa = f"{'TOTAL + ENTREGA:':<38}R$ {total_formatado}"
            conteudo.append(linha_total_com_taxa)
        
        # Verifica se há taxa de serviço
        valor_taxa_servico = float(venda.get('taxa_servico', 0))
        if valor_taxa_servico > 0:
            # Formata a taxa de serviço com 2 casas decimais
            taxa_servico_formatada = f"{valor_taxa_servico:7.2f}"
            # Cria a string da taxa de serviço alinhada à esquerda
            linha_taxa_servico = f"{'TAXA DE SERVIÇO (10%):':<38}R$ {taxa_servico_formatada}"
            conteudo.append(linha_taxa_servico)
            
            # Atualiza o total com a taxa de serviço
            total += valor_taxa_servico
            total_formatado = f"{total:7.2f}"
            linha_total_com_taxa_servico = f"{'TOTAL + SERVIÇO:':<38}R$ {total_formatado}"
            conteudo.append(linha_total_com_taxa_servico)
        
        # Verifica se há desconto
        desconto = float(venda.get('desconto', 0))
        if desconto > 0:
            # Formata o desconto com 2 casas decimais
            desconto_formatado = f"{desconto:7.2f}"
            # Cria a string do desconto alinhada à esquerda
            linha_desconto = f"{'DESCONTO:':<38}R$ {desconto_formatado}"
            conteudo.append(linha_desconto)
            
            # Calcula e exibe o total com desconto
            total_com_desconto = total - desconto
            total_com_desconto_formatado = f"{total_com_desconto:7.2f}"
            linha_total_com_desconto = f"{'TOTAL C/ DESCONTO:':<38}R$ {total_com_desconto_formatado}"
            conteudo.append(linha_total_com_desconto)
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Forma de pagamento
      
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        # Processa os pagamentos
        if pagamentos and len(pagamentos) > 0:
            for pagamento in pagamentos:
                forma = str(pagamento.get('forma_nome', '')).lower()
                valor = float(pagamento.get('valor', 0))
                troco = float(pagamento.get('troco', 0))
                
                # Formata o nome da forma de pagamento
                forma_display = FORMAS_PAGAMENTO.get(forma, forma.capitalize())
                
                # Adiciona a linha de pagamento
                valor_pago = valor + troco if forma == 'dinheiro' and troco > 0 else valor
                linha_pagamento = f"{forma_display:<20} {'R$':>15} {valor_pago:>11.2f}"
                conteudo.append(linha_pagamento)
                    
                # Se for dinheiro e houver troco
                if forma == 'dinheiro' and troco > 0:
                    linha_troco = f"{'Troco:':<20} {'R$':>15} {troco:>11.2f}"
                    conteudo.append(linha_troco)
                        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Mensagem de agradecimento
      
        conteudo.append("OBRIGADO PELA PREFERÊNCIA".center(largura))
        conteudo.append("VOLTE SEMPRE".center(largura))
        
        # Data e hora de impressão
        data_impressao = datetime.datetime.now().strftime("IMPRESSO EM %d/%m/%Y %H:%M")
       
        conteudo.append(data_impressao.center(largura))
        
        # Adiciona linhas em branco para garantir espaço antes do corte
        conteudo.append("")
        conteudo.append("")
        
        return "\n".join(conteudo)
    
    def _imprimir_texto(self, impressora, texto):
        """
        Imprime um texto na impressora especificada.
        
        Args:
            impressora: Nome da impressora a ser usada
            texto: Texto a ser impresso
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        if not impressora or not texto:
            return False
            
        # Lista todas as impressoras disponíveis
        try:
            # Verifica se é uma impressora PDF, XPS ou virtual
            impressora_upper = impressora.upper()
            impressora_virtual = any(x in impressora_upper for x in ["TO PDF", "TO XPS", "MICROSOFT XPS", "MICROSOFT PRINT TO PDF"])
            
            if impressora_virtual:
                # Método gráfico para impressoras virtuais (PDF, XPS, etc.)
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(impressora)
                
                # Configura o modo de mapeamento para TWIPS (1/1440 de polegada)
                hdc.SetMapMode(win32con.MM_TWIPS)
                
                # Configura o tamanho do papel para 80mm x 297mm (comprimento contínuo)
                PAPER_WIDTH = int(80 * 56.693)      # Largura: 80mm
                PAPER_HEIGHT = int(297 * 56.693)    # Altura: 297mm (comprimento contínuo)
                
                # Define o tamanho do papel e as margens
                hdc.SetViewportExt((PAPER_WIDTH, PAPER_HEIGHT))
                hdc.SetWindowExt((PAPER_WIDTH, PAPER_HEIGHT))
                
                # Margens em TWIPS (1mm = 56.693 TWIPS)
                MARGIN_LEFT = int(5 * 56.693)   # 5mm
                MARGIN_TOP = int(5 * 56.693)    # 5mm
                
                # Cria e seleciona a fonte (Courier New, tamanho 9pt, não-negrito)
                fonte = win32ui.CreateFont({
                    "name": "Courier New",
                    "height": -135,  # Tamanho da fonte em TWIPS (135 = ~9.5pt)
                    "weight": 400,   # Peso normal (400 = normal, 700 = negrito)
                    "charset": 0,    # ANSI_CHARSET
                    "italic": 0,     # Não itálico
                    "underline": 0   # Sem sublinhado
                })
                hdc.SelectObject(fonte)
                
                # Inicia o documento
                try:
                    hdc.StartDoc("Cupom Fiscal")
                    hdc.StartPage()
                except Exception as e:
                    return False
                
                # Configurações de impressão
                line_height = 200  # Espaçamento entre linhas em TWIPS (~3.5mm)
                y_position = MARGIN_TOP
                
                # Imprime o texto linha por linha
                for linha in texto.split('\n'):
                    # Remove caracteres de controle que podem ativar comandos da impressora
                    linha = linha.replace('\x1B', '').replace('\x1D', '').replace('\x1C', '')
                    
                    # Se a linha estiver vazia, adiciona apenas o espaçamento
                    if not linha.strip():
                        y_position += line_height
                        continue
                        
                    # Imprime a linha (Y negativo porque o eixo Y é invertido no modo TWIPS)
                    hdc.TextOut(MARGIN_LEFT, -y_position, linha)
                    
                    # Atualiza a posição Y para a próxima linha
                    y_position += line_height
                    
                    # Verifica se precisa de uma nova página
                    if y_position > (PAPER_HEIGHT - int(10 * 56.693)):  # 10mm de margem inferior
                        hdc.EndPage()
                        hdc.StartPage()
                        y_position = MARGIN_TOP
                
                # Finaliza a página e o documento
                try:
                    hdc.EndPage()
                    hdc.EndDoc()
                    hdc.DeleteDC()
                    return True
                except Exception as e:
                    try:
                        hdc.DeleteDC()
                    except:
                        pass
                    return False
                    
            else:
                # Método RAW para impressoras térmicas reais
               
                hprinter = None
                
                try:
                    # Tenta abrir a impressora
                  
                    hprinter = win32print.OpenPrinter(impressora)
                    
                    # Verificação simplificada de status
                    try:
                        printer_info = win32print.GetPrinter(hprinter, 2)
                        status = printer_info.get('Status', 0)
                        if status != 0:
                          
                            if status & 1:  # Verifica se está sem papel

                                return False
                    except Exception as e:
                        pass
                    
                    # Comandos de inicialização para impressoras térmicas
                    init_commands = [
                        b'\x1B@',           # Inicializa a impressora (reset)
                        b'\x1B!\x00',      # Fonte padrão (normal, 12x24)
                        b'\x1B3\x18',      # Define espaçamento entre linhas (24/180 polegadas = 3.38mm)
                        b'\x1Ba\x01',      # Define o alinhamento para centralizado
                        b'\x1B!\x00',      # Fonte normal
                        b'\x0A\x0A',       # Linhas em branco
                        b'\x1Ba\x00',      # Alinhamento à esquerda
                    ]
                    
                    # Inicia um trabalho de impressão RAW
                    try:
                        job = win32print.StartDocPrinter(hprinter, 1, ("Cupom Fiscal", None, "RAW"))
                        win32print.StartPagePrinter(hprinter)

                    except Exception as e:
                        raise
                    
                    # Envia os comandos de inicialização
                    for cmd in init_commands:
                        try:
                            win32print.WritePrinter(hprinter, cmd)
                        except:
                            continue
                    
                    # Prepara o texto para impressão
                    linhas = [linha.rstrip() for linha in texto.split('\n') if linha.strip()]
                    texto_formatado = '\n'.join(linhas) + '\n\n\n'  # Adiciona 3 linhas em branco no final
                    
                    # Adiciona comandos para avançar e cortar o papel
                    texto_formatado += '\n\n\n\x1DVA\x00'  # Avança 3 linhas e corta o papel
                    
                    # Converte para bytes usando codificação cp850
                    try:
                        texto_bytes = texto_formatado.encode('cp850', errors='replace')
                        win32print.WritePrinter(hprinter, texto_bytes)
                    except Exception as e:
                        print(f"DEBUG - _imprimir_texto - Erro ao enviar texto: {str(e)}")
                        # Tenta enviar o texto em partes menores
                        for linha in texto_formatado.split('\n'):
                            if linha.strip():  # Ignora linhas vazias
                                try:
                                    linha_bytes = (linha + '\n').encode('cp850', errors='replace')
                                    win32print.WritePrinter(hprinter, linha_bytes)
                                except:
                                    continue
                    
                    # Finaliza a impressão
                   
                    try:
                        win32print.EndPagePrinter(hprinter)
                        win32print.EndDocPrinter(hprinter)
                        win32print.ClosePrinter(hprinter)
                      
                        return True
                    except Exception as e:

                        try:
                            win32print.ClosePrinter(hprinter)
                        except:
                            pass
                        return False
                    
                except Exception as e:
                    print(f"DEBUG - _imprimir_texto - Erro durante a impressão: {str(e)}")
                    try:
                        if hprinter:
                            win32print.ClosePrinter(hprinter)
                    except:
                        pass
                    return False
                
        except Exception as e:
            print(f"DEBUG - _imprimir_texto - Erro inesperado: {str(e)}")
            return False
            
    def _obter_preco_item(self, item):
        """
        Obtém o preço de um item de venda, verificando diferentes campos possíveis.
        
        Args:
            item: Dicionário com informações do item de venda
            
        Returns:
            float: Preço do item ou 0.0 se não encontrado
        """
        # Lista de campos possíveis que podem conter o preço
        campos_preco = [
            'preco', 'preco_unitario', 'valor_unitario', 
            'valor', 'valor_venda', 'preco_venda', 'valorUnitario'
        ]
        
        # Procura o preço em cada campo possível
        for campo in campos_preco:
            if campo in item and item[campo] is not None:
                try:
                    return float(item[campo])
                except (ValueError, TypeError):
                    continue
        
        # Se não encontrou em nenhum campo, retorna 0.0
        return 0.0
