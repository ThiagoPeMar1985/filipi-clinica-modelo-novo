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
            'Sobremesas': 'sobremesas',
            'Outros': 'cupom'  # Itens do tipo 'Outros' vão para a impressora de cupom
        }
    
    def _carregar_configuracoes(self):
        """Carrega as configurações de impressoras do sistema."""
        if self.config_controller:
            config = self.config_controller.carregar_config_impressoras()
            self.impressoras = {
                'cupom': config.get('cupom', ''),
                'cozinha': config.get('cozinha', ''),
                'bar': config.get('bar', ''),
                'sobremesas': config.get('sobremesas', ''),
                'delivery': config.get('delivery', '')
            }
        else:
            # Se não tiver controlador, usa a impressora padrão para tudo
            try:
                impressora_padrao = win32print.GetDefaultPrinter()
                self.impressoras = {
                    'cupom': impressora_padrao,
                    'cozinha': impressora_padrao,
                    'bar': impressora_padrao,
                    'sobremesas': impressora_padrao,
                    'delivery': impressora_padrao
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
                tipo = item.get('tipo', 'Outros')
                
                # Verificar se o tipo é válido e está no mapeamento
                if tipo in self.mapeamento_tipos:
                    if tipo not in itens_por_tipo:
                        itens_por_tipo[tipo] = []
                    itens_por_tipo[tipo].append(item)
                else:
                    # Se não for um tipo válido, coloca em 'Outros'
                    if 'Outros' not in itens_por_tipo:
                        itens_por_tipo['Outros'] = []
                    itens_por_tipo['Outros'].append(item)
            
            # Imprimir cada grupo na impressora correspondente
            impressoras_usadas = set()  # Controlar impressoras já usadas
            
            for tipo, itens_tipo in itens_por_tipo.items():
                # Obter o tipo de impressora correspondente
                tipo_impressora = self.mapeamento_tipos.get(tipo, 'cupom')
                impressora = self.impressoras.get(tipo_impressora.lower(), '')
                
                # Verificar se a impressora já foi usada para evitar duplicação
                if impressora and impressora not in impressoras_usadas:
                    # Gerar conteúdo da comanda
                    conteudo = self._gerar_conteudo_comanda(venda, itens_tipo, tipo)
                    
                    # Imprimir na impressora correspondente
                    self._imprimir_texto(impressora, conteudo)
                    
                    # Marcar impressora como usada
                    impressoras_usadas.add(impressora)
                elif not impressora:
                    print(f"Nenhuma impressora configurada para o tipo: {tipo}")
            
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
        # Largura padrão para papel térmico
        largura = 30
        
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
        conteudo.append("ITEM DESCRICAO  QTD   VALOR")
        conteudo.append("-" * largura)
        
        # Itens
        for i, item in enumerate(itens, 1):
            nome = item.get('nome', '')[:15]  # Limita o tamanho do nome
            qtd = item.get('quantidade', 0)
            preco = item.get('preco', 0)
            
            # Formata a linha do item
            linha = f"{i:02d} {nome:<15} {qtd:>2} R${preco:>6.2f}"
            conteudo.append(linha)
        
        conteudo.append("-" * largura)
        
        # Totais
        subtotal = sum(item.get('total', 0) for item in itens)
        desconto = venda.get('desconto', 0)
        total = venda.get('valor_final', subtotal - desconto)
        
        conteudo.append(f"Subtotal: R$ {subtotal:.2f}")
        if desconto > 0:
            conteudo.append(f"Desconto: R$ {desconto:.2f}")
        conteudo.append(f"TOTAL:    R$ {total:.2f}")
        
        conteudo.append("-" * largura)
        conteudo.append("FORMA DE PAGAMENTO".center(largura))
        conteudo.append("-" * largura)
        
        # Pagamentos
        for pagamento in pagamentos:
            forma = pagamento.get('forma_nome', '')[:15]
            valor = pagamento.get('valor', 0)
            conteudo.append(f"{forma:<15} R$ {valor:>6.2f}")
        
        # Rodapé
        conteudo.append("=" * largura)
        conteudo.append("Obrigado pela preferencia!".center(largura))
        conteudo.append("Volte sempre!".center(largura))
        conteudo.append("=" * largura)
        
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
            # Configura a impressora
            hprinter = win32print.OpenPrinter(impressora)
            
            # Cria um objeto DC para a impressora
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(impressora)
            
            # Inicia o documento
            hdc.StartDoc("Cupom Fiscal")
            hdc.StartPage()
            
            # Configura o modo de mapeamento
            hdc.SetMapMode(MM_TEXT)
            
            # Define a fonte para impressora térmica (tamanho maior)
            font = win32ui.CreateFont({
                "name": "Courier New",
                "height": 30,  # Aumentado para melhor legibilidade
                "weight": 700,  # Negrito para melhor legibilidade
                "width": 12     # Largura do caractere
            })
            hdc.SelectObject(font)
            
            # Imprime o texto linha por linha
            y = 200  # Posição inicial Y aumentada
            x = 300  # Posição inicial X aumentada
            for linha in texto.split('\n'):
                hdc.TextOut(x, y, linha)
                y += 40  # Espaçamento entre linhas aumentado
            
            # Finaliza a página e o documento
            hdc.EndPage()
            hdc.EndDoc()
            
            # Fecha o objeto DC e a impressora
            hdc.DeleteDC()
            win32print.ClosePrinter(hprinter)
            
            return True
        except Exception as e:
            print(f"Erro ao imprimir texto: {e}")
            return False
