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
                    print(f"Enviando para impressora {tipo_impressora} ({impressora}): {len(itens_tipo)} itens do tipo {tipo}")
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
        # Cabeçalho
        conteudo = []
        conteudo.append("=" * 40)
        conteudo.append(f"COMANDA - {tipo_produto.upper()}".center(40))
        conteudo.append("=" * 40)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
        # Tipo de venda
        tipo_venda = venda.get('tipo', 'avulsa').upper()
        conteudo.append(f"Venda: {tipo_venda}")
        
        # Referência (mesa, delivery, etc)
        if venda.get('referencia'):
            conteudo.append(f"Ref: {venda['referencia']}")
            
        # Cliente (se houver)
        if venda.get('cliente_nome'):
            conteudo.append(f"Cliente: {venda['cliente_nome']}")
        
        conteudo.append("-" * 40)
        conteudo.append("ITEM  DESCRIÇÃO                  QTD")
        conteudo.append("-" * 40)
        
        # Itens
        for i, item in enumerate(itens, 1):
            nome = item.get('nome', '')[:25]  # Limita o tamanho do nome
            qtd = item.get('quantidade', 0)
            
            # Formata a linha do item
            linha = f"{i:02d}    {nome:<25} {qtd:>5}"
            conteudo.append(linha)
            
            # Adicionar opções do item, se houver
            if 'opcoes' in item and item['opcoes']:
                for opcao in item['opcoes']:
                    nome_opcao = opcao.get('nome', '')[:20]
                    conteudo.append(f"      → {nome_opcao}")
        
        # Rodápé
        conteudo.append("=" * 40)
        conteudo.append(f"Total de itens: {len(itens)}".center(40))
        conteudo.append("=" * 40)
        
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
        
        # Cabeçalho
        conteudo = []
        conteudo.append("=" * largura)
        conteudo.append("QUIOSQUE AQUARIUS".center(largura))
        conteudo.append("CNPJ: 00.000.000/0001-00".center(largura))
        conteudo.append("=" * largura)
        conteudo.append("DEMONSTRATIVO DE DELIVERY".center(largura))
        conteudo.append("=" * largura)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
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
        conteudo.append("ITEM  DESCRIÇÃO" + " " * 25 + "QTD   VALOR")
        conteudo.append("-" * largura)
        
        # Lista de itens
        for i, item in enumerate(itens, 1):
            nome = item.get('nome', '')[:25]  # Limita a 25 caracteres
            qtd = item.get('quantidade', 0)
            preco = item.get('valor_unitario', 0)
            valor_total = qtd * preco
            
            # Formata a linha do item
            linha = f"{i:02d}  {nome:<25} {qtd:>2}  R$ {preco:>6.2f}"
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
        subtotal = sum(item.get('quantidade', 0) * item.get('valor_unitario', 0) for item in itens)
        taxa_entrega = venda.get('taxa_entrega', 0)
        total = subtotal + taxa_entrega
        
        # Formata os totais alinhados à direita
        conteudo.append(f"{'Subtotal:':<40} R$ {subtotal:>7.2f}")
        if taxa_entrega > 0:
            conteudo.append(f"{'Taxa de entrega:':<40} R$ {taxa_entrega:>7.2f}")
        conteudo.append("-" * largura)
        conteudo.append(f"{'TOTAL:':<40} R$ {total:>7.2f}")
        
        # Forma de pagamento
        conteudo.append("-" * largura)
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        for pagamento in pagamentos:
            forma = pagamento.get('forma_nome', '')[:15]
            valor = pagamento.get('valor', 0)
            conteudo.append(f"{forma:<15} R$ {valor:>6.2f}")
        
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
        
        # Cabeçalho
        conteudo = []
        conteudo.append("=" * largura)
        conteudo.append("QUIOSQUE AQUARIUS".center(largura))
        conteudo.append("CNPJ: 00.000.000/0001-00".center(largura))
        conteudo.append("=" * largura)
        
        # Data e hora
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        conteudo.append(f"Data/Hora: {data_hora}")
        
        # Tipo de venda
        tipo_venda = venda.get('tipo', 'avulsa').upper()
        conteudo.append(f"Tipo: {tipo_venda}")
        
        # Cliente (se houver)
        if venda.get('cliente_nome'):
            conteudo.append(f"Cliente: {venda['cliente_nome']}")
        
        conteudo.append("-" * largura)
        # Cabeçalho da tabela de itens
        conteudo.append("ITEM  DESCRIÇÃO" + " " * 25 + "QTD   VALOR")
        conteudo.append("-" * largura)
        
        # Itens
        for i, item in enumerate(itens, 1):
            nome = item.get('nome', '')[:25]  # Aumentado para 25 caracteres
            qtd = item.get('quantidade', 0)
            preco = item.get('preco', 0)
            
            # Formata a linha do item
            linha = f"{i:02d}  {nome:<25} {qtd:>2}  R$ {preco:>6.2f}"
            conteudo.append(linha)
            
            # Adiciona observações do item, se houver
            if 'observacoes' in item and item['observacoes']:
                obs = f"    → {item['observacoes']}"
                conteudo.append(obs[:largura])  # Limita ao tamanho máximo
        
        conteudo.append("-" * largura)
        
        # Linha em branco antes dos totais
        conteudo.append("")
        
        # Totais
        subtotal = sum(item.get('total', 0) for item in itens)
        desconto = venda.get('desconto', 0)
        total = venda.get('valor_final', subtotal - desconto)
        
        # Formata os totais alinhados à direita
        conteudo.append(f"{'Subtotal:':<40} R$ {subtotal:>7.2f}")
        if desconto > 0:
            conteudo.append(f"{'Desconto:':<40} R$ {desconto:>7.2f}")
        conteudo.append("-" * largura)
        conteudo.append(f"{'TOTAL:':<40} R$ {total:>7.2f}")
        
        conteudo.append("-" * largura)
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        # Pagamentos
        for pagamento in pagamentos:
            forma = pagamento.get('forma_nome', '')[:15]
            valor = pagamento.get('valor', 0)
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
