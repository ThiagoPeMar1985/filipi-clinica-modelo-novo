"""
Módulo para gerenciamento de impressão de cupons e relatórios.
"""
import win32print
import win32ui
from win32con import MM_TEXT
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
        if self.config_controller:
            config = self.config_controller.carregar_config_impressoras()
            self.impressoras = {
                'cupom': config.get('cupom', ''),     # Para cupom fiscal
                'bar': config.get('bar', ''),         # Para itens do bar
                'cozinha': config.get('cozinha', ''), # Para itens da cozinha
                'sobremesas': config.get('sobremesas', ''),  # Para sobremesas
                'outros': config.get('outros', '')    # Para itens diversos
            }
        else:
            # Se não tiver controlador, usa a impressora padrão para tudo
            try:
                impressora_padrao = win32print.GetDefaultPrinter()
                self.impressoras = {
                    'cupom': impressora_padrao,     # Para cupom fiscal
                    'bar': impressora_padrao,       # Para itens do bar
                    'cozinha': impressora_padrao,   # Para itens da cozinha
                    'sobremesas': impressora_padrao, # Para sobremesas
                    'outros': impressora_padrao      # Para itens diversos
                }
            except Exception:
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
        # Largura padrão para a comanda
        largura = 50
        
        # Cabeçalho
        conteudo = []
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
        
        # Verificar o tipo de venda
        tipo_venda = venda.get('tipo', '').lower()
        if tipo_venda == 'avulsa':
            conteudo.append("VENDA AVULSA".center(largura))
        elif tipo_venda == 'delivery':
            conteudo.append("DELIVERY".center(largura))
            if venda.get('cliente_nome'):
                conteudo.append(f"Cliente: {venda['cliente_nome']}".center(largura))
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
        
        conteudo.append("-" * largura)
        conteudo.append("ITEM  DESCRIÇÃO                             QTD")
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
            
            # Formata a linha do item
            linha = f"{i:02d}    {nome:<30} {qtd:>3}"
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
        
        # Rodápé
        conteudo.append("=" * largura)
        conteudo.append(f"Total de itens: {len(itens)}".center(largura))
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
        # Largura padrão para papel de 80mm (aproximadamente 48 caracteres)
        largura = 48
        
        # Buscar dados da empresa no banco de dados
        try:
            from src.db.cadastro_db import CadastroDB
            from src.db.config import get_db_config
            import mysql.connector
            
            db_config = get_db_config()
            conn = mysql.connector.connect(**db_config)
            cadastro_db = CadastroDB(conn)
            empresa = cadastro_db.obter_empresa()
            conn.close()
            
            # Se não encontrou a empresa, usa valores padrão
            if not empresa:
                empresa = {
                    'nome_fantasia': 'QUIOSQUE AQUARIUS',
                    'cnpj': '00.000.000/0001-00',
                    'endereco': '',
                    'cidade': '',
                    'estado': '',
                    'telefone': ''
                }
        except Exception as e:
            print(f"Erro ao buscar dados da empresa: {e}")
            empresa = {
                'nome_fantasia': 'QUIOSQUE AQUARIUS',
                'cnpj': '00.000.000/0001-00',
                'endereco': '',
                'cidade': '',
                'estado': '',
                'telefone': ''
            }
        
        # Formata o endereço completo
        endereco_completo = []
        if empresa.get('endereco'):
            endereco_completo.append(empresa['endereco'])
            if empresa.get('numero'):
                endereco_completo[-1] += f", {empresa['numero']}"
        if empresa.get('bairro'):
            endereco_completo.append(empresa['bairro'])
        if empresa.get('cidade') and empresa.get('estado'):
            endereco_completo.append(f"{empresa['cidade']}/{empresa['estado']}")
        elif empresa.get('cidade'):
            endereco_completo.append(empresa['cidade'])
        elif empresa.get('estado'):
            endereco_completo.append(empresa['estado'])
        
        endereco_formatado = " - ".join(endereco_completo)
        
        # Cabeçalho
        conteudo = []
        conteudo.append("=" * largura)
        conteudo.append(empresa['nome_fantasia'].upper().center(largura))
        conteudo.append(f"CNPJ: {empresa.get('cnpj', '00.000.000/0001-00')}".center(largura))
        if endereco_formatado:
            # Divide o endereço em duas linhas
            partes = endereco_formatado.split(" - ")
            if len(partes) >= 2:
                linha1 = partes[0] + " - " + partes[1]
                linha2 = partes[2]
                
                # Limita cada linha ao tamanho máximo
                if len(linha1) > largura:
                    linha1 = linha1[:largura-3] + '...'
                if len(linha2) > largura:
                    linha2 = linha2[:largura-3] + '...'
                
                # Adiciona as linhas centralizadas
                conteudo.append(linha1.center(largura))
                conteudo.append(linha2.center(largura))
            else:
                conteudo.append(endereco_formatado.center(largura))
        if empresa.get('telefone'):
            conteudo.append(f"Tel: {empresa['telefone']}".center(largura))
        conteudo.append("=" * largura)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
        # Tipo de venda
        tipo_venda = venda.get('tipo', 'delivery')
        tipo_display = 'DELIVERY'
        conteudo.append(f"Tipo: {tipo_display}")
        
        # Atendente
        nome_usuario = venda.get('usuario_nome', 'Não identificado')
        if isinstance(nome_usuario, dict):
            nome_usuario = nome_usuario.get('nome', 'Não identificado')
        conteudo.append(f"Atendente: {nome_usuario}")
        
        # Informações do cliente
        conteudo.append("-" * largura)
        conteudo.append("DADOS DO CLIENTE".center(largura))
        conteudo.append("-" * largura)
        
        if venda.get('cliente_nome'):
            conteudo.append(f"Nome: {venda['cliente_nome']}")
        if venda.get('cliente_telefone'):
            conteudo.append(f"Telefone: {venda['cliente_telefone']}")
            
        # Endereço de entrega
        conteudo.append("-" * largura)
        conteudo.append("ENDEREÇO DE ENTREGA".center(largura))
        conteudo.append("-" * largura)
        
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
        
        # Itens do pedido
        conteudo.append("-" * largura)
        conteudo.append("ITENS DO PEDIDO".center(largura))
        conteudo.append("-" * largura)
        conteudo.append("ITEM  DESCRIÇÃO" + " " * 20 + "QTD   VALOR")
        conteudo.append("-" * largura)
        
        # Lista de itens
        for i, item in enumerate(itens, 1):
            nome = item.get('nome', '')[:28]  # Limita a 28 caracteres
            qtd = int(item.get('quantidade', 0))
            preco = float(item.get('valor_unitario', 0))
            
            # Formata a linha do item
            linha = f"{i:02d}  {nome:<28} {qtd:>2}  R$ {preco:>7.2f}"
            conteudo.append(linha)
            
            # Adiciona opções do item, se houver
            if 'opcoes' in item and item['opcoes']:
                for opcao in item['opcoes']:
                    nome_opcao = opcao.get('nome', '')[:20]
                    preco_adicional = opcao.get('preco_adicional', 0)
                    if preco_adicional > 0:
                        conteudo.append(f"    → {nome_opcao} (+ R$ {preco_adicional:.2f})")
                    else:
                        conteudo.append(f"    → {nome_opcao}")
            
            # Adiciona observações do item, se houver
            if 'observacoes' in item and item['observacoes']:
                obs = f"    → {item['observacoes']}"
                conteudo.append(obs[:largura])  # Limita ao tamanho máximo
        
        conteudo.append("-" * largura)
        
        # Totais
        subtotal = 0.0
        for item in itens:
            qtd = int(item.get('quantidade', 0))
            preco = float(item.get('valor_unitario', 0))
            subtotal += qtd * preco
        
        taxa_entrega = float(venda.get('taxa_entrega', 0))
        total = subtotal + taxa_entrega
        
        # Formata os valores com 2 casas decimais e alinhamento correto
        conteudo.append(f"{'Subtotal:':<35} R$ {subtotal:>7.2f}")
        if taxa_entrega > 0:
            conteudo.append(f"{'Taxa de entrega:':<35} R$ {taxa_entrega:>7.2f}")
        conteudo.append("-" * largura)
        conteudo.append(f"{'TOTAL:':<35} R$ {total:>7.2f}")
        
        # Forma de pagamento
        conteudo.append("-" * largura)
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        # Mapeamento das formas de pagamento para nomes formatados
        FORMAS_PAGAMENTO = {
            'credito': 'Cartão de Crédito',
            'debito': 'Cartão de Débito',
            'pix': 'Pix',
            'dinheiro': 'Dinheiro'
        }
        
        for pagamento in pagamentos:
            forma = pagamento.get('forma_nome', '').lower()
            forma_formatada = FORMAS_PAGAMENTO.get(forma, forma)
            valor = float(pagamento.get('valor', 0))
            troco = float(pagamento.get('troco', 0))
            
            if forma == 'dinheiro' and troco > 0:
                conteudo.append(f"{forma_formatada:<35} R$ {valor:>7.2f}")
                conteudo.append(f"{'Troco:':<35} R$ {troco:>7.2f}")
            else:
                conteudo.append(f"{forma_formatada:<35} R$ {valor:>7.2f}")
        
        # Rodapé
        conteudo.append("")
        conteudo.append("=" * largura)
        conteudo.append("Obrigado pela preferência!".center(largura))
        conteudo.append("Volte sempre!".center(largura))
        conteudo.append("")
        conteudo.append(f"{datetime.datetime.now().strftime('Impresso em %d/%m/%Y %H:%M')}".center(largura))
        
        return "\n".join(conteudo)

        
    def _gerar_conteudo_cupom(self, venda, itens, pagamentos):
        """
        Gera o conteúdo do cupom fiscal.
        
        Args:
            venda: Dicionário com informações da venda
            itens: Lista de itens da venda
            pagamentos: Lista de pagamentos realizados
            
        Returns:
            str: Conteúdo formatado do cupom
        """
        # Largura padrão para papel de 80mm (aproximadamente 48 caracteres)
        largura = 48
        
        # Buscar dados da empresa no banco de dados
        try:
            from src.db.cadastro_db import CadastroDB
            from src.db.config import get_db_config
            import mysql.connector
            
            db_config = get_db_config()
            conn = mysql.connector.connect(**db_config)
            cadastro_db = CadastroDB(conn)
            empresa = cadastro_db.obter_empresa()
            conn.close()
            
            # Se não encontrou a empresa, usa valores padrão
            if not empresa:
                empresa = {
                    'nome_fantasia': 'QUIOSQUE AQUARIUS',
                    'cnpj': '00.000.000/0001-00',
                    'endereco': '',
                    'cidade': '',
                    'estado': '',
                    'telefone': ''
                }
        except Exception as e:
            print(f"Erro ao buscar dados da empresa: {e}")
            empresa = {
                'nome_fantasia': 'QUIOSQUE AQUARIUS',
                'cnpj': '00.000.000/0001-00',
                'endereco': '',
                'cidade': '',
                'estado': '',
                'telefone': ''
            }
        
        # Formata o endereço completo
        endereco_completo = []
        if empresa.get('endereco'):
            endereco_completo.append(empresa['endereco'])
            if empresa.get('numero'):
                endereco_completo[-1] += f", {empresa['numero']}"
        if empresa.get('bairro'):
            endereco_completo.append(empresa['bairro'])
        if empresa.get('cidade') and empresa.get('estado'):
            endereco_completo.append(f"{empresa['cidade']}/{empresa['estado']}")
        elif empresa.get('cidade'):
            endereco_completo.append(empresa['cidade'])
        elif empresa.get('estado'):
            endereco_completo.append(empresa['estado'])
        
        endereco_formatado = " - ".join(endereco_completo)
        
        # Cabeçalho
        conteudo = []
        conteudo.append("=" * largura)
        conteudo.append(empresa['nome_fantasia'].upper().center(largura))
        conteudo.append(f"CNPJ: {empresa.get('cnpj', '00.000.000/0001-00')}".center(largura))
        if endereco_formatado:
            # Divide o endereço em duas linhas
            partes = endereco_formatado.split(" - ")
            if len(partes) >= 2:
                linha1 = partes[0] + " - " + partes[1]
                linha2 = partes[2]
                
                # Limita cada linha ao tamanho máximo
                if len(linha1) > largura:
                    linha1 = linha1[:largura-3] + '...'
                if len(linha2) > largura:
                    linha2 = linha2[:largura-3] + '...'
                
                # Adiciona as linhas centralizadas
                conteudo.append(linha1.center(largura))
                conteudo.append(linha2.center(largura))
            else:
                conteudo.append(endereco_formatado.center(largura))
        if empresa.get('telefone'):
            conteudo.append(f"Tel: {empresa['telefone']}".center(largura))
        conteudo.append("=" * largura)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
        
        # Tipo de venda
        tipo_venda = venda.get('tipo', 'avulsa')
        # Mapeia 'avulsa' para 'BALCÃO' e mantém outros valores em maiúsculas
        tipo_display = 'BALCÃO' if tipo_venda.lower() == 'avulsa' else tipo_venda.upper()
        conteudo.append(f"Tipo: {tipo_display}")
        
        # Cliente (se houver)
        if venda.get('cliente_nome'):
            conteudo.append(f"Cliente: {venda['cliente_nome']}")
        
        conteudo.append("-" * largura)
        # Cabeçalho da tabela de itens
        conteudo.append("ITEM  DESCRIÇÃO" + " " * 20 + "QTD   VALOR")
        conteudo.append("-" * largura)
        
        # Itens
        for i, item in enumerate(itens, 1):
            # Buscar o nome do produto em diferentes campos possíveis
            nome = None
            for campo_nome in ['nome', 'nome_produto', 'produto_nome']:
                if campo_nome in item and item[campo_nome]:
                    nome = item[campo_nome]
                    break
            
            if nome is None:
                nome = 'Produto sem nome'
                
            nome = nome[:25]  # Limitar a 25 caracteres
            qtd = item.get('quantidade', 0)
            
            # Buscar o preço em diferentes campos possíveis
            preco = 0
            for campo_preco in ['valor_unitario', 'preco_unitario', 'preco', 'valor', 'valor_venda', 'preco_venda']:
                if campo_preco in item and item[campo_preco] is not None:
                    preco = float(item[campo_preco])
                    break
            
            # Formata a linha do item
            linha = f"{i:02d}  {nome:<30} {qtd:>2}  R$ {preco:>6.2f}"
            conteudo.append(linha)
            
            # Adiciona opções do item, se houver
            if 'opcoes' in item and item['opcoes']:
                for opcao in item['opcoes']:
                    nome_opcao = opcao.get('nome', '')[:20]
                    preco_adicional = opcao.get('preco_adicional', 0)
                    if preco_adicional > 0:
                        conteudo.append(f"    → {nome_opcao} (+ R$ {preco_adicional:.2f})")
                    else:
                        conteudo.append(f"    → {nome_opcao}")
            
            # Adiciona observações do item, se houver
            if 'observacoes' in item and item['observacoes']:
                obs = f"    → {item['observacoes']}"
                conteudo.append(obs[:largura])  # Limita ao tamanho máximo
        
        conteudo.append("-" * largura)
        
        # Linha em branco antes dos totais
        conteudo.append("")
        
        # Totais
        # Calcula o subtotal usando os mesmos campos de preço que usamos para exibir os itens
        subtotal = 0
        for item in itens:
            qtd = item.get('quantidade', 0)
            preco_unitario = 0
            # Busca o preço em diferentes campos possíveis
            for campo_preco in ['valor_unitario', 'preco_unitario', 'preco', 'valor', 'valor_venda', 'preco_venda']:
                if campo_preco in item and item[campo_preco] is not None:
                    preco_unitario = float(item[campo_preco])
                    break
            subtotal += qtd * preco_unitario
        
        # Inicializa variáveis
        taxa_entrega = venda.get('taxa_entrega', 0)
        
        # Calcula totais de acordo com o tipo de venda
        if tipo_venda.lower() == 'mesa':
            # Verifica se a taxa de serviço foi marcada
            taxa_servico_flag = venda.get('taxa_servico', False)
            # Converte para booleano se for string
            if isinstance(taxa_servico_flag, str):
                taxa_servico_flag = taxa_servico_flag.lower() == 'true' or taxa_servico_flag == '1'
                
            taxa_servico = subtotal * 0.1 if taxa_servico_flag else 0.0
            desconto = venda.get('desconto', 0)
            total = subtotal + taxa_servico - desconto
            
            # Exibe os totais
            conteudo.append(f"{'Subtotal:':<35} R$ {subtotal:>7.2f}")
            # Garantir que a taxa de serviço seja exibida quando aplicada
            if taxa_servico > 0:
                conteudo.append(f"{'Taxa de serviço (10%):':<35} R$ {taxa_servico:>7.2f}")
            if desconto > 0:
                conteudo.append(f"{'Desconto:':<35} R$ {desconto:>7.2f}")
                
        elif tipo_venda.lower() == 'delivery':
            # Para delivery, aplica apenas a taxa de entrega
            total = subtotal + taxa_entrega
            
            # Exibe os totais
            conteudo.append(f"{'Subtotal:':<40} R$ {subtotal:>7.2f}")
            if taxa_entrega > 0:
                conteudo.append(f"{'Taxa de entrega:':<40} R$ {taxa_entrega:>7.2f}")
        else:
            # Para vendas avulsas, não aplica nenhuma taxa
            # Buscar o desconto na venda
            desconto = venda.get('desconto', 0)
            total = subtotal - desconto
            
            # Exibe os totais
            conteudo.append(f"{'Subtotal:':<35} R$ {subtotal:>7.2f}")
            if desconto > 0:
                conteudo.append(f"{'Desconto:':<35} R$ {desconto:>7.2f}")
        
        # Exibe o total final
        conteudo.append("-" * largura)
        conteudo.append(f"{'TOTAL:':<35} R$ {total:>7.2f}")
        
        conteudo.append("-" * largura)
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        # Pagamentos
        for pagamento in pagamentos:
            forma = pagamento.get('forma_nome', '').lower()
            valor = pagamento.get('valor', 0)
            troco = pagamento.get('troco', 0)
            
            if forma == 'dinheiro' and troco > 0:
                conteudo.append(f"{forma:<35} R$ {valor:>7.2f}")
                conteudo.append(f"{'Troco:':<35} R$ {troco:>7.2f}")
            else:
                conteudo.append(f"{forma:<15} R$ {valor:>6.2f}")
        
        # Rodapé
        conteudo.append("")
        conteudo.append("=" * largura)
        conteudo.append("Obrigado pela preferência!".center(largura))
        conteudo.append("Volte sempre!".center(largura))
        conteudo.append("")
        conteudo.append(f"{datetime.datetime.now().strftime('Impresso em %d/%m/%Y %H:%M')}".center(largura))
        
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
        try:
            # Verifica se é uma impressora PDF ou virtual
            impressora_virtual = "PDF" in impressora.upper() or "XPS" in impressora.upper() or "Microsoft" in impressora
            
            if impressora_virtual:
                # Método gráfico para impressoras virtuais (PDF, XPS, etc.)
                # Cria um objeto DC para a impressora
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(impressora)
                
                # Configura o modo de mapeamento
                hdc.SetMapMode(MM_TEXT)
                
                # Cria e seleciona a fonte com tamanho muito maior para impressoras virtuais
                fonte = win32ui.CreateFont({
                    "name": "Courier New",
                    "height": -72,  # Valor negativo para altura em pontos (muito maior)
                    "weight": 700    # Negrito para melhor legibilidade
                })
                hdc.SelectObject(fonte)
                
                # Inicia o documento
                hdc.StartDoc("Cupom Fiscal")
                hdc.StartPage()
                
                # Configurações de impressão com valores muito maiores para impressoras virtuais
                line_height = 100  # Espaçamento muito maior entre linhas
                margin_left = 80   # Margem maior para acomodar a fonte grande
                y_position = 80    # Posição inicial mais abaixo
                
                # Imprime o texto linha por linha
                for linha in texto.split('\n'):
                    hdc.TextOut(margin_left, y_position, linha)
                    y_position += line_height
                    
                    # Verifica se precisa de uma nova página
                    if y_position > (hdc.GetDeviceCaps(8) - line_height):
                        hdc.EndPage()
                        hdc.StartPage()
                        y_position = 20
                
                # Finaliza a página e o documento
                hdc.EndPage()
                hdc.EndDoc()
                hdc.DeleteDC()
                
                return True
            else:
                # Método RAW para impressoras térmicas reais
                hprinter = win32print.OpenPrinter(impressora)
                try:
                    # Inicia um trabalho de impressão RAW
                    job = win32print.StartDocPrinter(hprinter, 1, ("Cupom Fiscal", None, "RAW"))
                    win32print.StartPagePrinter(hprinter)
                    
                    # Prepara o texto para impressão
                    # Converte o texto para bytes usando codificação cp850 (compatível com a maioria das impressoras térmicas)
                    texto_bytes = texto.encode('cp850', errors='replace')
                    
                    # Envia o texto diretamente para a impressora
                    win32print.WritePrinter(hprinter, texto_bytes)
                    
                    # Finaliza a impressão
                    win32print.EndPagePrinter(hprinter)
                    win32print.EndDocPrinter(hprinter)
                    win32print.ClosePrinter(hprinter)
                    
                    return True
                    
                except Exception as e:
                    win32print.ClosePrinter(hprinter)
                    raise e
                
        except Exception as e:
            print(f"Erro ao imprimir texto: {e}")
            return False
