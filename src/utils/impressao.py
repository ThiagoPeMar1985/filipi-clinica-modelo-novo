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
        
        # Mapeamento de tipos de produtos para tipos de impressoras
        self.mapeamento_tipos = {
            'Bar': 'bar',
            'Cozinha': 'cozinha',
            'Sobremesa': 'sobremesas',
            'Sobremesas': 'sobremesas',  # Mantém compatibilidade com ambos os nomes
            'Outros': 'outros',
            'Cupom': 'cupom',
            'cupom': 'cupom'  # Garante que mesmo em minúsculo funcione
        }
    
    def _carregar_configuracoes(self):
        """Carrega as configurações de impressoras do sistema."""
        print("\n=== INÍCIO DO CARREGAMENTO DAS CONFIGURAÇÕES ===")
        
        # Inicializa dicionário vazio de impressoras
        self.impressoras = {
            'cupom': '',
            'bar': '',
            'cozinha': '',
            'sobremesas': '',
            'outros': ''
        }
        
        # Verifica se temos um config_controller válido
        if not self.config_controller:
            print("AVISO: Nenhum config_controller fornecido ao GerenciadorImpressao")
        else:
            print(f"Config controller fornecido: {self.config_controller}")
            
            # Verifica se o config_controller tem o método necessário
            if not hasattr(self.config_controller, 'carregar_config_impressoras'):
                print("AVISO: config_controller não possui o método 'carregar_config_impressoras'")
            else:
                print("Tentando carregar configurações do config_controller...")
                try:
                    config = self.config_controller.carregar_config_impressoras()
                    print(f"Configurações brutas carregadas: {config}")
                    
                    if config and isinstance(config, dict):
                        # Mapeia as configurações para as chaves corretas
                        mapeamento = {
                            'cupom_fiscal': 'cupom',
                            'bar': 'bar',
                            'cozinha': 'cozinha',
                            'sobremesas': 'sobremesas',
                            'outros': 'outros'
                        }
                        
                        # Atualiza apenas as configurações que existem no mapeamento
                        for chave_config, chave_impressora in mapeamento.items():
                            if chave_config in config and config[chave_config]:
                                self.impressoras[chave_impressora] = config[chave_config]
                        
                        print(f"Configurações de impressão processadas: {self.impressoras}")
                        
                        # Verifica se a impressora de cupom está configurada
                        impressora_cupom = self.impressoras.get('cupom', '')
                        if not impressora_cupom:
                            print("AVISO: Nenhuma impressora de cupom fiscal configurada!")
                        else:
                            print(f"Impressora de cupom fiscal configurada: {impressora_cupom}")
                        
                        return
                    else:
                        print("AVISO: Nenhuma configuração de impressão válida encontrada no config_controller")
                        
                except Exception as e:
                    print(f"ERRO ao carregar configurações do config_controller: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        # Se chegou aqui, não conseguiu carregar as configurações do config_controller
        # Tenta obter a impressora padrão do sistema
        print("\nTentando obter impressora padrão do sistema...")
        try:
            impressora_padrao = win32print.GetDefaultPrinter()
            print(f"Impressora padrão do sistema: {impressora_padrao}")
            
            # Define a impressora padrão para todos os tipos
            for chave in self.impressoras:
                self.impressoras[chave] = impressora_padrao
            
            print(f"Usando impressora padrão para todas as saídas: {impressora_padrao}")
            
        except Exception as e:
            print(f"ERRO ao obter impressora padrão: {str(e)}")
            # Mantém o dicionário vazio em caso de erro
            self.impressoras = {}
        
        print("=== FIM DO CARREGAMENTO DAS CONFIGURAÇÕES ===\n")
    
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
            impressora = self.impressoras.get('cupom', '')
            if not impressora:
                print("Nenhuma impressora de cupom fiscal configurada.")
                return False
            
            # Gerar o conteúdo do cupom
            conteudo = self._gerar_conteudo_cupom(venda, itens, pagamentos)
            
            # Imprimir o conteúdo
            resultado = self._imprimir_texto(impressora, conteudo)
            
            return resultado
        except Exception as e:
            print(f"Erro ao imprimir cupom fiscal: {e}")
            return False
            
    def imprimir_comandas_por_tipo(self, venda, itens):
        """
        Imprime comandas separadas por tipo de produto nas impressoras configuradas.
        
        Args:
            venda: Dicionário com informações da venda
            itens: Lista de itens da venda
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        try:
            # Verificar se há itens para imprimir
            if not itens:
                print("Nenhum item para imprimir nas comandas.")
                return True
                
            # Agrupar itens por tipo
            itens_por_tipo = {}
            for item in itens:
                # Garantir que cada item vá para apenas um tipo de impressora
                tipo = str(item.get('tipo', 'Outros')).strip()
                
                # Padroniza o nome do tipo
                if tipo.lower() == 'sobremesa':
                    tipo = 'Sobremesas'
                
                # Se o tipo não estiver no mapeamento, define como 'Outros'
                if tipo not in self.mapeamento_tipos:
                    tipo = 'Outros'
                
                # Adiciona o item ao grupo correspondente
                if tipo not in itens_por_tipo:
                    itens_por_tipo[tipo] = []
                itens_por_tipo[tipo].append(item)
            
            # Imprimir cada grupo na impressora correspondente
            for tipo, itens_tipo in itens_por_tipo.items():
                # Obter o tipo de impressora correspondente
                tipo_impressora = self.mapeamento_tipos.get(tipo, 'cupom')
                impressora = self.impressoras.get(tipo_impressora.lower(), '')
                
                if impressora:
                    # Gerar conteúdo da comanda
                    conteudo = self._gerar_conteudo_comanda(venda, itens_tipo, tipo)
                    
                    # Imprimir na impressora correspondente
                    self._imprimir_texto(impressora, conteudo)
                else:
                    print(f"Aviso: Nenhuma impressora configurada para o tipo: {tipo}")
            
            return True
        except Exception as e:
            print(f"Erro ao imprimir comandas por tipo: {e}")
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
            conteudo.append(f"MESA {mesa_num} - {tipo_produto.upper()}".center(largura))
        conteudo.append("=" * largura)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
        # Atendente - verifica tanto atendente_nome quanto usuario_nome
        nome_atendente = venda.get('atendente_nome') or venda.get('usuario_nome')
        if nome_atendente:
            # Verifica se o nome do usuário é um dicionário (pode acontecer em alguns casos)
            if isinstance(nome_atendente, dict) and 'nome' in nome_atendente:
                nome_atendente = nome_atendente['nome']
        conteudo.append(f"Atendente: {nome_atendente}")
            
        # Se for delivery, mostra o nome do cliente
        if tipo_venda == 'delivery' and venda.get('cliente_nome'):
            conteudo.append(f"Cliente: {venda['cliente_nome']}")
        
        # Cabeçalho dos itens
        conteudo.append("-" * largura)
        conteudo.append("DESCRIÇÃO                             QTD")
        conteudo.append("-" * largura)
        
        # Itens
        for i, item in enumerate(itens, 1):
            # Tenta obter o nome do item de diferentes maneiras
            nome = item.get('nome') or item.get('produto_nome') or item.get('nome_produto') or 'Produto sem nome'
            
            # Se ainda não tiver nome, tenta buscar pelo ID do produto
            if nome == 'Produto sem nome' and 'produto_id' in item:
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
                    print(f"Erro ao buscar nome do produto: {e}")
                    nome = f"Produto ID: {item.get('produto_id', 'N/A')}"
            
            # Limita o tamanho do nome para 30 caracteres
            nome = str(nome)[:30]
            qtd = item.get('quantidade', 1)
            
            # Formata a linha do item sem numeração em fonte maior
            linha = "\x1B!\x30" + f"{nome.upper():<20} {qtd:>3}" + "\x1B!\x00" + fonte_normal
            conteudo.append(linha)
            
            # Adicionar opções ou observações do item
            # Primeiro verifica opções
            if 'opcoes' in item and item['opcoes']:
                for opcao in item['opcoes']:
                    nome_opcao = str(opcao.get('nome', 'Opção sem nome'))[:30]
                    conteudo.append(f"    → {nome_opcao}")
            
            # Depois verifica observações
            if 'observacoes' in item and item['observacoes']:
                observacoes = str(item['observacoes']).split('\n')
                for obs in observacoes:
                    if obs.strip():
                        conteudo.append(f"    → {obs[:30]}")
        
        # Linha final
        conteudo.append("=" * largura)
        
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
                    print(f"Usando impressora padrão para demonstrativo de delivery: {impressora}")
                except Exception as e:
                    print(f"Nenhuma impressora disponível para demonstrativo de delivery: {e}")
                    return False
                
            if not impressora:
                print("Nenhuma impressora configurada para demonstrativo de delivery.")
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
            # Quebra o endereço em linhas se for muito longo
            endereco = venda['endereco_entrega']
            while endereco:
                linha = endereco[:largura-2]
                conteudo.append(linha)
                endereco = endereco[largura-2:]
        else:
            # Adiciona cada parte do endereço separadamente
            if venda.get('endereco'):
                conteudo.append(f"Rua: {venda['endereco']}")
            if venda.get('numero'):
                conteudo.append(f"Número: {venda['numero']}")
            if venda.get('bairro'):
                conteudo.append(f"Bairro: {venda['bairro']}")
            if venda.get('cidade'):
                conteudo.append(f"Cidade: {venda['cidade']}")
            if venda.get('referencia'):
                conteudo.append(f"Referência: {venda['referencia']}")
        
        
        # Linha de separação
        conteudo.append("-" * largura)
        # Itens

        # Cabeçalho da tabela de itens
        cabecalho = f"{'DESCRIÇÃO':<15} {'QTD':>2} {'VALOR':>12} {'SUBTOTAL':>12}"
        conteudo.append(cabecalho)
        conteudo.append("-" * largura)
        total = 0.0
        
        for item in itens:
            # Nome do produto (limita a 15 caracteres)
            nome = item.get('nome', 'Produto sem nome')
            if len(nome) > 15:
                nome = nome[:12] + '...'
            
            # Quantidade (padrão 1 se não informado)
            qtd = int(item.get('quantidade', 1))
            
            # Preço unitário
            preco = self._obter_preco_item(item)
            
            # Calcula subtotal do item
            subtotal_item = qtd * preco
            total += subtotal_item
            
            # Formata a linha do item
            linha_item = f"{nome:<15} {qtd:>2}x {preco:>10.2f} {subtotal_item:>11.2f}"
            conteudo.append(linha_item)
            
            # Linha de separação após cada item
            conteudo.append("-" * largura)
        
        # Total
        # Formata o valor com 2 casas decimais
        valor_formatado = f"{total:7.2f}"
        # Cria a string do total alinhada à esquerda
        linha_total = f"{'TOTAL:':<38}R$ {valor_formatado}"
        conteudo.append(linha_total)
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Forma de pagamento
        if pagamentos and len(pagamentos) > 0:

            conteudo.append("FORMA DE PAGAMENTO".center(largura, ' '))
            conteudo.append("-" * largura)
            
            # Mapeamento das formas de pagamento para nomes formatados
            FORMAS_PAGAMENTO = {
                'credito': 'CARTÃO CRÉDITO',
                'debito': 'CARTÃO DÉBITO',
                'pix': 'PIX',
                'dinheiro': 'DINHEIRO',
                'cartao': 'CARTÃO',
                'vale': 'VALE'
            }
            
            for pagamento in pagamentos:
                forma = pagamento.get('forma_nome', '').lower()
                forma_formatada = FORMAS_PAGAMENTO.get(forma, forma.upper())
                valor = float(pagamento.get('valor', 0))
                troco = float(pagamento.get('troco', 0))
                
                if forma == 'dinheiro' and troco > 0:
                    conteudo.append(f"{forma_formatada:<15} R$ {valor:>9.2f}")
                    conteudo.append(f"{'TROCO:':<15} R$ {troco:>9.2f}")
                else:
                    conteudo.append(f"{forma_formatada:<15} R$ {valor:>9.2f}")
        
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
        cabecalho = f"{'DESCRIÇÃO':<15} {'QTD':>2} {'VALOR':>12} {'SUBTOTAL':>12}"
        conteudo.append(cabecalho)
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Itens
        total = 0.0
        
        for item in itens:
            # Nome do produto (limita a 15 caracteres)
            nome = item.get('nome', 'Produto sem nome')
            if len(nome) > 15:
                nome = nome[:12] + '...'
            
            # Quantidade (padrão 1 se não informado)
            qtd = int(item.get('quantidade', 1))
            
            # Preço unitário
            preco = 0.0
            for campo in ['valor_unitario', 'preco_unitario', 'preco', 'valor', 'valor_venda', 'preco_venda']:
                if campo in item and item[campo] is not None:
                    try:
                        preco = float(item[campo])
                        break
                    except (ValueError, TypeError):
                        continue
            
            # Calcula subtotal do item
            subtotal_item = qtd * preco
            total += subtotal_item
            
            # Formata a linha do item
            linha_item = f"{nome:<15} {qtd:>2}x {preco:>10.2f} {subtotal_item:>11.2f}"
            conteudo.append(linha_item)
            
            # Linha de separação após cada item
            conteudo.append("-" * largura)
        
        # Total
        # Formata o valor com 2 casas decimais
        valor_formatado = f"{total:7.2f}"
        # Cria a string do total alinhada à esquerda
        linha_total = f"{'TOTAL:':<38}R$ {valor_formatado}"
        conteudo.append(linha_total)
        
        # Linha de separação
        conteudo.append("-" * largura)
        
        # Forma de pagamento
      
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        # Processa os pagamentos
        if pagamentos and len(pagamentos) > 0:
            for pagamento in pagamentos:
                forma = pagamento.get('forma_nome', '').upper()
                valor = float(pagamento.get('valor', 0))
                troco = float(pagamento.get('troco', 0))
                
                # Formata o nome da forma de pagamento
                if forma == 'DEBITO':
                    forma_display = 'CARTÃO DÉBITO'
                elif forma == 'CREDITO':
                    forma_display = 'CARTÃO CRÉDITO'
                elif forma == 'DINHEIRO':
                    forma_display = 'DINHEIRO'
                else:
                    forma_display = forma
                
                # Adiciona a linha de pagamento
                linha_pagamento = f"{forma_display.lower():<20} {'R$':>15} {valor:>11.2f}"
                conteudo.append(linha_pagamento)
                
                # Se for dinheiro e houver troco
                if forma == 'DINHEIRO' and troco > 0:
                    linha_troco = f"{'TROCO:':<20} {'R$':>15} {troco:>11.2f}"
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
            impressora: Nome da impressora
            texto: Texto a ser impresso
            
        Returns:
            bool: True se a impressão foi bem-sucedida, False caso contrário
        """
        print(f"Tentando imprimir na impressora: {impressora}")
        print(f"Tipo da impressora: {type(impressora)}")
        
        # Listar todas as impressoras disponíveis para depuração
        try:
            impressoras_disponiveis = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            print("Impressoras disponíveis no sistema:")
            for i, (flags, desc, name, comment) in enumerate(impressoras_disponiveis):
                print(f"  {i+1}. {name} (Descrição: {desc})")
        except Exception as e:
            print(f"Erro ao listar impressoras: {e}")
            
        try:
            # Verifica se é uma impressora PDF, XPS ou virtual
            impressora_upper = impressora.upper()
            impressora_virtual = any(x in impressora_upper for x in ["TO PDF", "TO XPS", "MICROSOFT XPS", "MICROSOFT PRINT TO PDF"])
            
            print(f"Impressora selecionada: {impressora}")
            print(f"É impressora virtual? {impressora_virtual}")
            
            if impressora_virtual:
                # Método gráfico para impressoras virtuais (PDF, XPS, etc.)
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(impressora)
                
                # Configura o modo de mapeamento para TWIPS (1/1440 de polegada)
                hdc.SetMapMode(win32con.MM_TWIPS)
                
                # Configura o tamanho do papel para 80mm x 297mm (comprimento contínuo)
                # 1mm = 56.693 TWIPS
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
                hdc.StartDoc("Cupom Fiscal")
                hdc.StartPage()
                
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
                    
                    # Verifica se precisa de uma nova página (deixa 1cm de margem inferior)
                    if y_position > (PAPER_HEIGHT - int(10 * 56.693)):  # 10mm de margem inferior
                        hdc.EndPage()
                        hdc.StartPage()
                        y_position = MARGIN_TOP
                
                # Finaliza a página e o documento
                hdc.EndPage()
                hdc.EndDoc()
                hdc.DeleteDC()
                
                # Adiciona comandos para avançar e cortar o papel (para impressoras virtuais)
                # Isso é feito adicionando os comandos ao final do texto
                texto += '\n\n\n\x1DVA\x00'  # Avança 3 linhas e corta o papel
                
                return True
                
            else:
                # Método RAW para impressoras térmicas reais
                print(f"Tentando abrir a impressora: {impressora}")
                try:
                    # Tenta abrir a impressora com permissões corretas
                    try:
                        hprinter = win32print.OpenPrinter(impressora)
                        print(f"Impressora aberta com sucesso: {hprinter}")
                        
                        # Verifica se a impressora está pronta
                        try:
                            printer_info = win32print.GetPrinter(hprinter, 2)
                            print(f"Status da impressora: {printer_info.get('Status', 'Status não disponível')}")
                            
                            # Verifica se a impressora está pronta
                            if printer_info.get('Status') != 0:
                                print(f"Aviso: A impressora pode não estar pronta. Status: {printer_info.get('Status')}")
                                
                        except Exception as e:
                            print(f"Erro ao obter informações da impressora: {e}")
                            print("Continuando com a impressão...")
                            
                    except Exception as e:
                        print(f"Erro ao abrir a impressora: {e}")
                        print("Tentando abrir a impressora padrão...")
                        
                        # Tenta abrir a impressora padrão
                        try:
                            impressora_padrao = win32print.GetDefaultPrinter()
                            print(f"Usando impressora padrão: {impressora_padrao}")
                            hprinter = win32print.OpenPrinter(impressora_padrao)
                            print(f"Impressora padrão aberta com sucesso: {hprinter}")
                        except Exception as e2:
                            print(f"Erro ao abrir a impressora padrão: {e2}")
                            print("Nenhuma impressora disponível. Criando arquivo de log...")
                            
                            # Cria um arquivo de log com o conteúdo que seria impresso
                            try:
                                with open("erro_impressao.txt", "a", encoding="utf-8") as f:
                                    f.write(f"=== Erro de impressão em {datetime.datetime.now()} ===\n")
                                    f.write(f"Impressora: {impressora}\n")
                                    f.write(f"Erro: {e}\n")
                                    f.write("Conteúdo:\n")
                                    f.write(texto)
                                    f.write("\n\n")
                                print("Arquivo de log criado: erro_impressao.txt")
                            except Exception as e3:
                                print(f"Erro ao criar arquivo de log: {e3}")
                                
                            return False
                    
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
                    job = win32print.StartDocPrinter(hprinter, 1, ("Cupom Fiscal", None, "RAW"))
                    win32print.StartPagePrinter(hprinter)
                    
                    # Envia os comandos de inicialização
                    print("Enviando comandos de inicialização para a impressora...")
                    for i, cmd in enumerate(init_commands):
                        try:
                            print(f"Enviando comando {i+1}: {cmd}")
                            win32print.WritePrinter(hprinter, cmd)
                            print("Comando enviado com sucesso")
                        except Exception as e:
                            print(f"Erro ao enviar comando {i+1}: {e}")
                            print("Continuando com a impressão...")
                    
                    # Prepara o texto para impressão
                    # Remove linhas vazias extras e adiciona quebra de linha no final de cada linha
                    linhas = [linha.rstrip() for linha in texto.split('\n') if linha.strip()]
                    texto_formatado = '\n'.join(linhas) + '\n\n\n'  # Adiciona 3 linhas em branco no final
                    
                    # Adiciona comandos para avançar e cortar o papel
                    texto_formatado += '\n\n\n\x1DVA\x00'  # Avança 3 linhas e corta o papel (GS V 0)
                    
                    # Converte para bytes usando codificação cp850 (compatível com a maioria das impressoras térmicas)
                    try:
                        print("Convertendo texto para bytes...")
                        texto_bytes = texto_formatado.encode('cp850', errors='replace')
                        print(f"Texto convertido para {len(texto_bytes)} bytes")
                        
                        # Envia o texto diretamente para a impressora
                        print("Enviando texto para a impressora...")
                        win32print.WritePrinter(hprinter, texto_bytes)
                        print("Texto enviado com sucesso para a impressora")
                        
                    except Exception as e:
                        print(f"Erro ao enviar texto para a impressora: {e}")
                        print("Tentando enviar o texto em partes menores...")
                        
                        # Tenta enviar o texto em partes menores
                        try:
                            # Divide o texto em linhas e envia uma por vez
                            for i, linha in enumerate(texto_formatado.split('\n')):
                                if linha.strip():  # Ignora linhas vazias
                                    linha_bytes = (linha + '\n').encode('cp850', errors='replace')
                                    win32print.WritePrinter(hprinter, linha_bytes)
                                    print(f"Linha {i+1} enviada")
                            print("Todas as linhas foram enviadas")
                        except Exception as e2:
                            print(f"Erro ao enviar texto em partes: {e2}")
                            raise
                    
                    # Finaliza a impressão
                    try:
                        print("Finalizando página da impressora...")
                        win32print.EndPagePrinter(hprinter)
                        print("Finalizando documento...")
                        win32print.EndDocPrinter(hprinter)
                        print("Fechando impressora...")
                        win32print.ClosePrinter(hprinter)
                        print("Impressão concluída com sucesso!")
                        
                        return True
                        
                    except Exception as e:
                        print(f"Erro ao finalizar a impressão: {e}")
                        try:
                            win32print.ClosePrinter(hprinter)
                        except:
                            pass
                        return False
                    
                except Exception as e:
                    try:
                        win32print.ClosePrinter(hprinter)
                    except:
                        pass
                    print(f"Erro ao imprimir: {e}")
                    return False
                
        except Exception as e:
            print(f"Erro ao imprimir texto: {e}")
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
