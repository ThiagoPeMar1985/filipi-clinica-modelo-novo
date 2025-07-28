"""
Módulo de Pagamentos para o sistema PDV Aquarius.
Permite processar pagamentos para vendas avulsas, delivery e mesas.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from datetime import datetime
from pathlib import Path


# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.pagamento_controller import PagamentoController
from controllers.cadastro_controller import CadastroController
from utils.impressao import GerenciadorImpressao

class PagamentoModule:
    def __init__(self, master, db_connection, valor_total=0.0, desconto=0.0, 
                 callback_finalizar=None, venda_tipo='avulsa', referencia=None, itens_venda=None, controller=None, taxa_servico=False, config_controller=None):
        """
        Inicializa o módulo de pagamentos.
        
        Args:
            master: Widget pai onde o módulo será exibido
            db_connection: Conexão com o banco de dados
            valor_total: Valor total da venda
            desconto: Valor do desconto aplicado
            callback_finalizar: Função a ser chamada quando o pagamento for finalizado
            venda_tipo: Tipo de venda ('avulsa', 'delivery', 'mesa')
            referencia: Número da mesa ou referência do pedido
            itens_venda: Lista de itens da venda
            controller: Controlador principal
            taxa_servico: Indica se há taxa de serviço (para mesas)
            config_controller: Controlador de configurações
        """
        self.master = master
        self.db_connection = db_connection
        self.config_controller = config_controller
        self.controller = controller  # Armazena a referência ao controlador principal
        self.pagamento_controller = PagamentoController(db_connection)
        self.cadastro_controller = CadastroController(db_connection)
        
        self.valor_total = float(valor_total)
        self.desconto = float(desconto)
        self.valor_final = self.valor_total - self.desconto
        
        self.callback_finalizar = callback_finalizar
        self.venda_tipo = venda_tipo
        self.referencia = referencia
        
        # Lista para armazenar os pagamentos realizados
        self.pagamentos = []
        
        # Itens da venda (produtos)
        self.itens_venda = itens_venda or []
        
        # Taxa de serviço (para vendas de mesa)
        self.taxa_servico = taxa_servico
        
        # Cores do tema
        self.cores = {
            "primaria": "#4a6fa5",
            "secundaria": "#28b5f4",
            "terciaria": "#333f50",
            "fundo": "#f0f2f5",
            "texto": "#000000",
            "texto_claro": "#ffffff",
            "destaque": "#4caf50",
            "alerta": "#f44336"
        }
        
        self.frame = None
        self._criar_interface()

    def _calcular_troco(self, *args):
        try:
            # Pega o valor pago
            valor_pago_str = self.valor_pagamento_var.get().replace('.', '').replace(',', '.')
            valor_pago = float(valor_pago_str) if valor_pago_str else 0.0
            
            # Calcula o valor restante a pagar
            valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
            
            # Calcula o troco (só mostra se for positivo)
            troco = valor_pago - valor_restante
            if troco > 0:
                self.troco_label.config(text=f"R$ {troco:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
            else:
                self.troco_label.config(text="R$ 0,00")
                
        except (ValueError, AttributeError):
            self.troco_label.config(text="R$ 0,00")   

    def _atualizar_previa_cupom(self):
        """Atualiza a prévia do cupom fiscal."""
        try:
            # Cria um dicionário com os dados da venda para o cupom
            venda_dados = {
                'itens': self.itens_venda,
                'pagamentos': [{
                    'forma': p['forma_nome'],
                    'valor': p['valor'],
                    'troco': p.get('troco',0)
                } for p in self.pagamentos],
                'total': self.valor_final,
                'desconto': self.desconto,
                'taxa_servico': self.taxa_servico if hasattr(self, 'taxa_servico') else 0
            }
            
            # Gera o conteúdo do cupom
            conteudo_cupom = self._gerar_conteudo_cupom(venda_dados)
            
            # Atualiza o widget de texto
            self.cupom_texto.config(state="normal")
            self.cupom_texto.delete(1.0, tk.END)
            self.cupom_texto.insert(tk.END, conteudo_cupom)
            self.cupom_texto.config(state="disabled")
            
        except Exception as e:
            print(f"Erro ao atualizar prévia do cupom: {e}")
            self.cupom_texto.config(state="normal")
            self.cupom_texto.delete(1.0, tk.END)
            self.cupom_texto.insert(tk.END, "Erro ao gerar prévia do cupom.")
            self.cupom_texto.config(state="disabled")

    def _gerar_conteudo_cupom(self, venda_dados):
        """Gera o conteúdo formatado do cupom fiscal."""
        # Largura do cupom (48 caracteres para papel de 80mm)
        largura = 40
        
        # Função auxiliar para centralizar texto
        def centralizar(texto, largura=largura):
            return texto.center(largura)
        
        # Função para formatar valores monetários
        def formatar_valor(valor):
            return f"R$ {float(valor):9.2f}".replace('.', ',')
        
        linhas = []
        
        # Cabeçalho
        
        linhas.append(centralizar("CUPOM FISCAL"))
        linhas.append("=" * largura)
        
        # Data/Hora
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        linhas.append(f"Data: {data_hora}")
        
        # Número da venda
        if 'id' in venda_dados:
            linhas.append(f"Venda: #{venda_dados['id']}")
        
        # Linha separadora
        linhas.append("-" * largura)
        
        # Cabeçalho dos itens
        linhas.append("DESCRIÇÃO                   QTD   VALOR")
        linhas.append("-" * largura)
        
        # Itens
        for item in venda_dados['itens']:
            # Obtém o nome do item
            nome = item.get('nome') or item.get('produto_nome', 'Produto')
            quantidade = item.get('quantidade', 1)
            preco = item.get('preco') or item.get('valor_unitario', 0)
            total = quantidade * preco
            
            # Formata a linha do item
            nome_linha = f"{quantidade}x {nome[:20]}"
            linha = f"{nome_linha.ljust(25)} {quantidade:>2} {formatar_valor(total)}"
            linhas.append(linha)
        
        # Totais
        linhas.append("-" * largura)
        linhas.append(f"{'Subtotal:':<25}{formatar_valor(self.valor_total)}")
        
        if venda_dados.get('desconto', 0) > 0:
            linhas.append(f"{'Desconto:':<25}{formatar_valor(venda_dados['desconto'])}")
        
        if venda_dados.get('taxa_servico', 0) > 0:
            linhas.append(f"{'Taxa Serviço:':<25}{formatar_valor(venda_dados['taxa_servico'])}")
        
        linhas.append("-" * largura)
        linhas.append(f"{'TOTAL:':<25}{formatar_valor(venda_dados['total'])}")
        
        # Pagamentos
        if 'pagamentos' in venda_dados and venda_dados['pagamentos']:
            linhas.append("-" * largura)
            linhas.append(centralizar("FORMA DE PAGAMENTO"))
            linhas.append("-" * largura)
            
            for pagamento in venda_dados['pagamentos']:
                forma = pagamento.get('forma', '')
                valor = pagamento.get('valor', 0)
                troco = pagamento.get('troco', 0)
                
                if forma.lower() == 'dinheiro' and troco > 0:
                    linhas.append(f"{'Dinheiro:':<15}{formatar_valor(valor + troco)}")
                    linhas.append(f"{'Troco:':<15}{formatar_valor(troco)}")
                else:
                    linhas.append(f"{forma.capitalize() + ':':<15}{formatar_valor(valor)}")
        
        return "\n".join(linhas)
        
    def _criar_interface(self):
        """Cria a interface do módulo de pagamentos."""
        # Remover frame anterior se existir
        if self.frame:
            self.frame.destroy()
            
        self.frame = ttk.Frame(self.master)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configurar o frame principal com a cor de fundo
        self.frame.configure(style="Custom.TFrame")
        style = ttk.Style()
        style.configure("Custom.TFrame", background=self.cores["fundo"])
        
        # Título
        titulo_frame = ttk.Frame(self.frame, style="Custom.TFrame")
        titulo_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(
            titulo_frame, 
            text="Pagamento", 
            font=("Arial", 18, "bold"),
            foreground=self.cores["texto"],
            background=self.cores["fundo"]
        ).pack(side="left", padx=(0, 20))
        
        # Botão de voltar
        voltar_btn = tk.Button(
            titulo_frame,
            text="VOLTAR",
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief="flat",
            command=self._voltar
        )
        voltar_btn.pack(side="right")
        
        # Container principal
        container = ttk.Frame(self.frame)
        container.pack(fill="both", expand=True)
        
        # Coluna da esquerda - Resumo e formas de pagamento
        coluna_esquerda = ttk.Frame(container)
        coluna_esquerda.pack(side="left", fill="both", expand=True, padx=5)

        # Coluna do meio - Pagamentos realizados
        coluna_meio = ttk.Frame(container)
        coluna_meio.pack(side="left", fill="both", expand=True, padx=5)
    
        # Coluna da direita - Visualização do cupom fiscal
        coluna_direita = ttk.Frame(container)  # Largura fixa para o cupom
        coluna_direita.pack(side="right", fill="both", padx=5)
        

       # Frame do cupom fiscal
        cupom_frame = ttk.LabelFrame(
           coluna_direita,
           text="Pré-visualização do Cupom",
           style="Resumo.TLabelframe"
        )
        cupom_frame.pack(fill="both", expand=True, pady=(0, 10), padx=5)

        # Área de visualização do cupom (com rolagem)
        cupom_container = ttk.Frame(cupom_frame)
        cupom_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Adiciona barra de rolagem
        scrollbar = ttk.Scrollbar(cupom_container)
        scrollbar.pack(side="right", fill="y")

        # Widget de texto para exibir o cupom
        self.cupom_texto = tk.Text(
            cupom_container,
            wrap="word",
            font=("Courier New", 10),  # Fonte monoespaçada para alinhamento correto
            height=30,
            bg="white",
            fg="black",
            padx=10,
            pady=10,
            state="disabled",
            yscrollcommand=scrollbar.set
        )
        self.cupom_texto.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.cupom_texto.yview)
        
        # Estilo para os frames e labels
        style.configure("Resumo.TLabelframe", background=self.cores["fundo"])
        style.configure("Resumo.TLabelframe.Label", background=self.cores["fundo"], foreground=self.cores["texto"], font=("Arial", 11, "bold"))
        style.configure("Info.TLabel", background=self.cores["fundo"], foreground=self.cores["texto"], font=("Arial", 10))
        style.configure("InfoBold.TLabel", background=self.cores["fundo"], foreground=self.cores["texto"], font=("Arial", 10, "bold"))
        style.configure("Total.TLabel", background=self.cores["fundo"], foreground=self.cores["primaria"], font=("Arial", 12, "bold"))
        
        # Resumo da venda
        resumo_frame = ttk.LabelFrame(coluna_esquerda, text="Resumo da Venda", style="Resumo.TLabelframe")
        resumo_frame.pack(fill="x", pady=(0, 20), padx=5)
        
        # Subtotal
        subtotal_frame = ttk.Frame(resumo_frame, style="Custom.TFrame")
        subtotal_frame.pack(fill="x", pady=8, padx=10)
        ttk.Label(subtotal_frame, text="Subtotal:", style="InfoBold.TLabel").pack(side="left")
        self.subtotal_label = ttk.Label(subtotal_frame, text=f"R$ {self.valor_total:.2f}".replace('.', ','), style="Info.TLabel")
        self.subtotal_label.pack(side="right")
        
        # Desconto
        desconto_frame = ttk.Frame(resumo_frame, style="Custom.TFrame")
        desconto_frame.pack(fill="x", pady=8, padx=10)
        
        # Label do desconto
        ttk.Label(desconto_frame, text="Desconto:", style="InfoBold.TLabel").pack(side="left")
        
        # Frame para o valor do desconto
        desconto_valor_frame = ttk.Frame(desconto_frame, style="Custom.TFrame")
        desconto_valor_frame.pack(side="right")
        
        # Campo de entrada para o desconto
        self.desconto_var = tk.StringVar(value=f"{self.desconto:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
        self.desconto_var.trace_add('write', self._atualizar_desconto)
        self.desconto_entry = ttk.Entry(
            desconto_valor_frame,
            textvariable=self.desconto_var,
            font=("Arial", 10),
            width=10,
            justify="right",
            validate="key"
        )
        self.desconto_entry.pack(side="right")
        
        # Taxa de serviço (se houver)
        self.valor_taxa_servico = 0.0
        self.valor_itens = self.valor_total  # Inicializa com o valor total
        
        if self.taxa_servico:
            if self.venda_tipo == 'mesa':
                # Para mesas, o valor_total já inclui a taxa de serviço
                # Vamos calcular o valor dos itens (sem a taxa) para depois calcular os 10%
                self.valor_itens = round(self.valor_total / 1.1, 2)  # Remove a taxa de 10% do total
                self.valor_taxa_servico = round(self.valor_itens * 0.1, 2)  # 10% do valor dos itens
                
                # Atualizar o subtotal para mostrar apenas o valor dos itens
                self.subtotal_label.config(text=f"R$ {self.valor_itens:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
                
                # Atualizar o valor final (já inclui a taxa)
                self.valor_final = self.valor_total - self.desconto
            else:
                # Para outros tipos de venda, calcular a taxa normalmente (10% sobre o total)
                self.valor_taxa_servico = round(self.valor_total * 0.1, 2)
                # Atualizar o valor final com a taxa de serviço
                self.valor_final = (self.valor_total + self.valor_taxa_servico) - self.desconto
            
            # Exibir a taxa de serviço na interface
            self.taxa_frame = ttk.Frame(resumo_frame, style="Custom.TFrame")
            self.taxa_frame.pack(fill="x", pady=8, padx=10)
            
            # Label da taxa de serviço
            ttk.Label(self.taxa_frame, text="Taxa de Serviço (10%):", style="InfoBold.TLabel").pack(side="left")
            
            # Valor da taxa de serviço
            self.taxa_label = ttk.Label(self.taxa_frame, text=f"R$ {self.valor_taxa_servico:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','), style="Info.TLabel")
            self.taxa_label.pack(side="right")
        
        # Total
        total_frame = ttk.Frame(resumo_frame, style="Custom.TFrame")
        total_frame.pack(fill="x", pady=8, padx=10)
        ttk.Label(total_frame, text="TOTAL:", style="Total.TLabel").pack(side="left")
        self.total_label = ttk.Label(total_frame, text=f"R$ {self.valor_final:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','), style="Total.TLabel")
        self.total_label.pack(side="right")
        
        # Separador
        ttk.Separator(resumo_frame, orient="horizontal").pack(fill="x", padx=10, pady=5)
        
        # Valor restante
        restante_frame = ttk.Frame(resumo_frame, style="Custom.TFrame")
        restante_frame.pack(fill="x", pady=8, padx=10)
        ttk.Label(restante_frame, text="Restante:", style="InfoBold.TLabel").pack(side="left")
        self.restante_label = ttk.Label(restante_frame, text=f"R$ {self.valor_final:.2f}".replace('.', ','), style="InfoBold.TLabel")
        self.restante_label.pack(side="right")
        
        # Formas de pagamento
        formas_frame = ttk.LabelFrame(coluna_esquerda, text="Formas de Pagamento", style="Resumo.TLabelframe")
        formas_frame.pack(fill="both", expand=True, padx=5)
        
        # Campo para entrada do valor de pagamento
        valor_frame = ttk.Frame(formas_frame, style="Custom.TFrame")
        valor_frame.pack(fill="x", pady=15, padx=10)
        
        # Estilo para o campo de entrada
        style.configure("Valor.TLabel", background=self.cores["fundo"], foreground=self.cores["texto"], font=("Arial", 12, "bold"))
        
        ttk.Label(valor_frame, text="Valor Recebido:", style="Valor.TLabel").pack(side="left")

        # Frame para exibir o troco
        troco_frame = ttk.Frame(formas_frame, style="Custom.TFrame")
        troco_frame.pack(fill="x", pady=(0, 15), padx=10)

        # Label "Troco:"
        ttk.Label(troco_frame, text="Troco:", style="Valor.TLabel").pack(side="left")

        # Label que vai exibir o valor do troco
        self.troco_label = ttk.Label(
            troco_frame, 
            text="R$ 0,00", 
            style="Valor.TLabel",
            foreground="green"  # Opcional: deixa o valor em verde
        )
        self.troco_label.pack(side="right")
        
        self.valor_pagamento_var = tk.StringVar()
        self.valor_pagamento_entry = ttk.Entry(
            valor_frame, 
            textvariable=self.valor_pagamento_var, 
            font=("Arial", 12), 
            width=15,
            justify="right"
        )
        self.valor_pagamento_entry.pack(side="right")

        self.valor_pagamento_var.trace_add("write", self._calcular_troco)
        
        # Definir valor padrão como o valor restante
        valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
        self.valor_pagamento_var.set(f"{valor_restante:.2f}".replace('.', ','))
        
        # Botões para formas de pagamento
        self.formas_pagamento = self.pagamento_controller.listar_formas_pagamento()
        
        # Se não houver formas de pagamento no banco, usar as padrão
        if not self.formas_pagamento:
            self.formas_pagamento = [
                {'id': 1, 'nome': 'Dinheiro'},
                {'id': 2, 'nome': 'Cartão de Crédito'},
                {'id': 3, 'nome': 'Cartão de Débito'},
                {'id': 4, 'nome': 'Pix'},
            ]
        
        # Frame para os botões de forma de pagamento
        botoes_frame = ttk.Frame(formas_frame)
        botoes_frame.pack(fill="both", expand=True, pady=10)
        
        # Criar grid para os botões (2 colunas)
        row, col = 0, 0
        max_cols = 2
        
        for forma in self.formas_pagamento:
            btn = tk.Button(
                botoes_frame,
                text=forma['nome'],
                bg=self.cores["primaria"],
                fg=self.cores["texto_claro"],
                font=("Arial", 10, "bold"),
                padx=15,
                pady=10,
                relief="flat",
                cursor="hand2",
                command=lambda f=forma: self._selecionar_forma_pagamento(f)
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Atualizar posição na grid
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        # Configurar pesos das colunas para centralizar
        for i in range(max_cols):
            botoes_frame.columnconfigure(i, weight=1)
        
        # Lista de pagamentos realizados
        pagamentos_frame = ttk.LabelFrame(coluna_meio, text="Pagamentos Realizados", style="Resumo.TLabelframe")
        pagamentos_frame.pack(fill="both", expand=True, padx=5)
        
        # Estilo para o Treeview
        style.configure("Treeview", 
                      background="white",
                      foreground=self.cores["texto"],
                      rowheight=25,
                      fieldbackground="white")
        style.configure("Treeview.Heading", 
                      font=("Arial", 10, "bold"), 
                      background=self.cores["primaria"],
                      foreground=self.cores["texto"])
        style.map("Treeview", 
                background=[("selected", "#4a6fa5")],
                foreground=[("selected", "#ffffff")])
        
        # Frame para o Treeview e scrollbar
        tree_frame = ttk.Frame(pagamentos_frame, style="Custom.TFrame")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview para pagamentos
        colunas = ('forma', 'valor')
        self.pagamentos_tree = ttk.Treeview(
            tree_frame, 
            columns=colunas, 
            show='headings', 
            height=10,
            yscrollcommand=scrollbar.set
        )
        
        # Configurar colunas
        self.pagamentos_tree.heading('forma', text='Forma de Pagamento')
        self.pagamentos_tree.heading('valor', text='Valor')
        
        self.pagamentos_tree.column('forma', width=200)
        self.pagamentos_tree.column('valor', width=150, anchor="e")
        
        # Configurar scrollbar
        scrollbar.config(command=self.pagamentos_tree.yview)
        
        self.pagamentos_tree.pack(side="left", fill="both", expand=True)
        
        # Criar menu de contexto para remoção de pagamento
        self.context_menu = tk.Menu(self.pagamentos_tree, tearoff=0)
        self.context_menu.add_command(
            label="Remover Pagamento",
            command=self._remover_pagamento_selecionado
        )
        
        # Vincular evento de clique direito
        self.pagamentos_tree.bind("<Button-3>", self._mostrar_menu_contexto)
        
          # Frame para os botões de finalização
        botoes_frame = ttk.Frame(coluna_meio)
        botoes_frame.pack(fill="x", pady=10, expand=True)
        
        # Botão Finalizar sem Imprimir
        self.finalizar_sem_imprimir_btn = tk.Button(
            botoes_frame,
            text="FINALIZAR SEM IMPRIMIR",
            bg=self.cores["secundaria"],  # Cor azul claro do tema
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=5,
            pady=10,
            relief="flat",
            cursor="hand2",
            state="disabled",
            command=lambda: self._finalizar_venda(imprimir_cupom=False)  # Adicione este parâmetro ao método _finalizar_venda
        )
        self.finalizar_sem_imprimir_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Botão Finalizar Venda
        self.finalizar_btn = tk.Button(
            botoes_frame,
            text="FINALIZAR VENDA",
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=5,
            pady=10,
            relief="flat",
            cursor="hand2",
            state="disabled",
            command=lambda: self._finalizar_venda(imprimir_cupom=True) if hasattr(self, '_finalizar_venda') else None
        )
        self.finalizar_btn.pack(side="right", fill="x", expand=True)
        self._atualizar_previa_cupom() 
        
    def _validar_desconto(self):
        """Valida se o desconto é válido."""
        if self.desconto < 0:
            messagebox.showerror("Erro", "O valor do desconto não pode ser negativo.")
            return False
            
        if self.desconto > self.valor_total:
            messagebox.showerror("Erro", f"O desconto (R$ {self.desconto:,.2f}) não pode ser maior que o valor total (R$ {self.valor_total:,.2f}).")
            return False
            
        return True
        
    def _selecionar_forma_pagamento(self, forma):
        """Adiciona um pagamento com a forma selecionada usando o valor informado no campo."""
        # Validar o desconto antes de prosseguir
        if not self._validar_desconto():
            return
            
        # Obter o valor do campo
        valor_str = self.valor_pagamento_var.get()
        
        # Verificar se o valor é válido
        try:
            valor = float(valor_str.replace(',', '.'))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, informe um valor válido.")
            return
            
        # Calcular o valor restante
        valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
        
        # Se não houver valor restante, não permitir mais pagamentos
        if valor_restante <= 0:
            messagebox.showinfo("Informação", "O valor total já foi pago.")
            return
        
        try:
            # Converter o valor (substituindo vírgula por ponto)
            valor = float(valor_str.replace(',', '.'))
            
            # Validar o valor
            if valor <= 0:
                messagebox.showerror(
                    "Erro de Valor", 
                    "O valor deve ser maior que zero.",
                    icon="error"
                )
                return
                
            # Se não for pagamento em dinheiro e o valor for maior que o restante
            if forma['nome'].lower() != 'dinheiro' and valor > valor_restante:
                messagebox.showerror(
                    "Erro de Valor", 
                    f"O valor do pagamento ({forma['nome']}) não pode ser maior que o restante.\n\n"
                    f"Valor informado: R$ {valor:.2f}\n"
                    f"Valor restante: R$ {valor_restante:.2f}"
                )
                return
                
            # Se for pagamento em dinheiro e o valor for maior que o restante, calcular o troco automaticamente
            if forma['nome'].lower() == 'dinheiro' and valor > valor_restante:
                troco = valor - valor_restante
                # Salvar o troco no pagamento
                valor_efetivo = valor_restante
                troco_valor = troco
            else:
                valor_efetivo = valor
                troco_valor = 0
            

            # Adicionar o pagamento à lista
            pagamento = {
                'forma_id': forma['id'],
                'forma_nome': forma['nome'],
                'valor': valor_efetivo,
                'troco': troco_valor
            }
            
            self.pagamentos.append(pagamento)
            self._atualizar_previa_cupom()

            # Atualizar a interface
            self._atualizar_pagamentos()
            
            # Atualizar o valor no campo de entrada para o valor restante
            novo_valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
            if novo_valor_restante > 0:
                self.valor_pagamento_var.set(f"{novo_valor_restante:.2f}".replace('.', ','))
            else:
                self.valor_pagamento_var.set("0,00")
                
        except ValueError:
            messagebox.showerror("Erro", "Por favor, informe um valor válido.")
        
    def _confirmar_pagamento(self, forma, valor_str, dialog):
        """Confirma o pagamento com a forma selecionada."""
        try:
            # Converter o valor (substituindo vírgula por ponto)
            valor = float(valor_str.replace(',', '.'))
            
            # Validar o valor
            if valor <= 0:
                messagebox.showerror(
                    "Erro de Valor", 
                    "O valor deve ser maior que zero.",
                    icon="error"
                )
                return
                
            valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
            
            # Se o valor for maior que o restante, perguntar se deseja dar troco
            if valor > valor_restante:
                troco = valor - valor_restante
                resposta = messagebox.askyesno(
                    "Troco", 
                    f"O valor informado é maior que o restante.\n\n"
                    f"Valor informado: R$ {valor:.2f}\n"
                    f"Valor restante: R$ {valor_restante:.2f}\n"
                    f"Troco: R$ {troco:.2f}\n\n"
                    f"Deseja continuar e calcular o troco?"
                )
                
                if not resposta:
                    return
                    
                # Salvar o troco no pagamento
                pagamento = {
                    'forma_id': forma['id'],
                    'forma_nome': forma['nome'],
                    'valor': valor_restante,
                    'troco': troco
                }
            else:
                # Pagamento normal sem troco
                pagamento = {
                    'forma_id': forma['id'],
                    'forma_nome': forma['nome'],
                    'valor': valor,
                    'troco': 0
                }
            
            self.pagamentos.append(pagamento)
            
            # Atualizar a interface
            self._atualizar_pagamentos()
            
            # Fechar o diálogo
            dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Informe um número válido.")
    
    def _atualizar_pagamentos(self):
        """Atualiza a lista de pagamentos na interface."""
        # Limpar a tabela
        for item in self.pagamentos_tree.get_children():
            self.pagamentos_tree.delete(item)
            
        # Adicionar os pagamentos à tabela
        for i, pagamento in enumerate(self.pagamentos):
            item_id = f"item_{i}"
            self.pagamentos_tree.insert(
                "", 
                "end", 
                iid=item_id,
                values=(
                    pagamento['forma_nome'],
                    f"R$ {pagamento['valor']:.2f}".replace('.', ',')
                )
            )
            
        # Calcular valor restante
        valor_pago = sum(p['valor'] for p in self.pagamentos)
        valor_restante = max(0, self.valor_final - valor_pago)
        
        # Atualizar label de valor restante
        self.restante_label.config(text=f"R$ {valor_restante:.2f}".replace('.', ','))
        
        # Habilitar botão de finalizar se o valor pago for maior ou igual ao valor final
        # Usar round para evitar problemas de arredondamento com ponto flutuante
        if round(sum(p['valor'] for p in self.pagamentos), 2) >= round(self.valor_final, 2):
            self.finalizar_btn.config(state="normal")
            self.finalizar_sem_imprimir_btn.config(state="normal") 
        else:
            self.finalizar_btn.config(state="disabled")
            self.finalizar_sem_imprimir_btn.config(state="disabled") 
    
    def _mostrar_menu_contexto(self, event):
        """Exibe o menu de contexto ao clicar com o botão direito."""
        # Identificar o item clicado
        item_id = self.pagamentos_tree.identify_row(event.y)
        if not item_id:
            return
            
        # Selecionar o item clicado
        self.pagamentos_tree.selection_set(item_id)
        
        # Exibir o menu de contexto
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _remover_pagamento_selecionado(self):
        """Remove o pagamento atualmente selecionado na tabela."""
        # Obter o item selecionado
        selecionados = self.pagamentos_tree.selection()
        if not selecionados:
            return
            
        item_id = selecionados[0]
        
        # Obter o índice do pagamento
        try:
            indice = int(item_id.split('_')[1])
            self._remover_pagamento(indice)
        except (ValueError, IndexError):
            pass
    
    def _remover_pagamento(self, indice):
        """Remove um pagamento da lista."""
        # Confirmar a remoção
        pagamento = self.pagamentos[indice]
        resposta = messagebox.askyesno(
            "Remover Pagamento", 
            f"Deseja remover o pagamento de {pagamento['forma_nome']} "
            f"no valor de R$ {pagamento['valor']:.2f}?",
            icon="question"
        )
        
        if not resposta:
            return
            
        # Remover o pagamento
        self.pagamentos.pop(indice)
        
        # Atualizar a interface
        self._atualizar_pagamentos()
        
        # Dar foco ao campo de valor
        self.valor_pagamento_entry.focus()
        
    def _atualizar_desconto(self, *args):
        """Atualiza o desconto automaticamente quando o valor é alterado."""
        try:
            # Obtém o valor atual do campo e a posição do cursor
            valor_atual = self.desconto_var.get()
            
            # Se o campo estiver vazio, define como zero
            if not valor_atual:
                self.desconto_var.set("0,00")
                self.desconto = 0.0
                self.valor_final = self.valor_total
                self._atualizar_valores()
                return
                
            # Tenta converter o valor para float
            try:
                # Remove formatação e converte para float
                valor_limpo = valor_atual.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                
                # Se o valor for vazio após limpeza, define como zero
                if not valor_limpo:
                    self.desconto = 0.0
                    self.desconto_var.set("0,00")
                else:
                    self.desconto = float(valor_limpo)
                    # Formata o valor para exibição
                    valor_formatado = f"{self.desconto:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
                    self.desconto_var.set(valor_formatado)
                
                # Atualiza o valor final e a interface
                self.valor_final = max(0, self.valor_total - self.desconto)
                self._atualizar_valores()
                
            except ValueError:
                # Se o valor não for numérico, restaura o valor anterior
                self.desconto_var.set(f"{self.desconto:.2f}".replace('.', ','))
                
        except Exception as e:
            print(f"Erro ao atualizar desconto: {e}")
            # Em caso de erro, mantém o valor anterior
            self.desconto_var.set(f"{self.desconto:.2f}".replace('.', ','))
    
    def _atualizar_valores(self):
        """Atualiza os valores totais e restantes na interface."""
        # Atualiza o valor total na interface
        self.total_label.config(text=f"R$ {self.valor_final:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
        
        # Atualiza o valor restante a pagar
        valor_pago = sum(p['valor'] for p in self.pagamentos)
        valor_restante = max(0, round(self.valor_final - valor_pago, 2))
        self.restante_label.config(text=f"R$ {valor_restante:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
        
        # Atualiza o valor no campo de pagamento
        if valor_restante > 0:
            self.valor_pagamento_var.set(f"{valor_restante:.2f}".replace('.', ','))
        else:
            self.valor_pagamento_var.set("0,00")
    
    def _finalizar_venda(self, imprimir_cupom=True):
        """Finaliza a venda com os pagamentos realizados."""
        try:
            # Verificar se o valor pago é suficiente
            valor_pago = sum(p['valor'] for p in self.pagamentos)
            
            if round(valor_pago, 2) < round(self.valor_final, 2):
                messagebox.showerror(
                    "Erro de Pagamento", 
                    f"O valor pago (R$ {valor_pago:.2f}) é menor que o valor final (R$ {self.valor_final:.2f}).",
                    icon="error"
                )
                return 
            
            # Verificar se callback existe
            if not hasattr(self, 'callback_finalizar') or not callable(self.callback_finalizar):
                messagebox.showerror("Erro", "Configuração incompleta - função de finalização não disponível")
                return False
                
            
            # Obter o nome do usuário logado, se disponível
            nome_usuario = 'Não identificado'
            if hasattr(self, 'controller') and hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'nome'):
                nome_usuario = self.controller.usuario.nome
            
            # Processar dados da venda
            if self.venda_tipo == 'mesa' and self.taxa_servico:
                valor_itens = self.valor_total / 1.1
                valor_taxa_servico = round(valor_itens * 0.1, 2)
                valor_final = self.valor_total - self.desconto
            else:
                valor_taxa_servico = getattr(self, 'valor_taxa_servico', 0.0)
                valor_com_taxa = self.valor_total + valor_taxa_servico
                valor_final = valor_com_taxa - self.desconto
            
            # Preparar dados da venda
            venda_dados = {
                'valor_total': self.valor_total,
                'desconto': self.desconto,
                'valor_final': round(valor_final, 2),
                'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'tipo': self.venda_tipo.upper(),
                'observacoes': '',
                'taxa_servico': valor_taxa_servico,
                'usuario_nome': nome_usuario  
            }
            
            # Preparar pagamentos
            pagamentos_formatados = []
            for i, pagamento in enumerate(self.pagamentos, 1):
                pagamento_formatado = {
                    'forma_id': pagamento['forma_id'],
                    'forma_nome': pagamento['forma_nome'],
                    'valor': pagamento['valor'],
                    'troco': pagamento.get('troco', 0)
                }

                if 'cliente_id' in pagamento:
                    pagamento_formatado['cliente_id'] = pagamento['cliente_id']
                    if 'cliente_nome' in pagamento:
                        pagamento_formatado['cliente_nome'] = pagamento['cliente_nome']
                    pagamento_formatado['observacao'] = f"{pagamento['forma_nome']} - Cliente: {pagamento.get('cliente_nome', '')}"
                else:
                    pagamento_formatado['observacao'] = pagamento['forma_nome']
                    
                pagamentos_formatados.append(pagamento_formatado)
            
            # Chamar o callback de finalização
            if self.callback_finalizar:
                try:
                    resultado = self.callback_finalizar(venda_dados, self.itens_venda, pagamentos_formatados)
                    if not resultado:  
                        return False
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return False
            
            # Imprimir cupom se necessário
            if imprimir_cupom:
                try:
                    self._imprimir_cupom_fiscal(venda_dados)
                except Exception as e:
                    print(f"ERRO ao imprimir cupom: {str(e)}")
                    # Continua mesmo com erro de impressão
            
            # Fechar a janela

            try:
                if hasattr(self, 'master') and self.master:
                    if isinstance(self.master, tk.Toplevel):
                        self.master.destroy()
                    elif hasattr(self, 'frame') and self.frame:
                        self.frame.destroy()
            except Exception as e:
                import traceback
                traceback.print_exc()
            
            return True  # Indica sucesso
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("===================================\n")
            
            messagebox.showerror(
                "Erro ao Finalizar Venda", 
                f"Ocorreu um erro ao finalizar a venda: {str(e)}",
                icon="error"
            )
            return False


    def _voltar(self):
        """Volta para a tela anterior."""
        # Confirmar se deseja voltar
        if self.pagamentos:
            resposta = messagebox.askyesno(
                "Confirmar Retorno", 
                "Há pagamentos registrados. Deseja realmente voltar?",
                icon="question"
            )
            
            if not resposta:
                return
                
        # Destruir a janela de pagamento
        if isinstance(self.master, tk.Toplevel):
            self.master.destroy()
        else:
            # Destruir o frame
            if self.frame:
                self.frame.destroy()
                self.frame = None
                
    def _imprimir_cupom_fiscal(self, venda_dados):
      
        """Imprime o cupom fiscal da venda finalizada"""
        try:
            # Obter os itens da venda (produtos)
            itens = self._obter_itens_venda()
            
            # Obter o controlador de configurações
            config_controller = None
            if hasattr(self, 'config_controller'):
                config_controller = self.config_controller

            elif hasattr(self, 'controller') and hasattr(self.controller, 'config_controller'):
                config_controller = self.controller.config_controller
            elif hasattr(self, 'controller') and hasattr(self.controller, 'controller') and hasattr(self.controller.controller, 'config_controller'):
                config_controller = self.controller.controller.config_controller
                
            # Carregar configurações de impressão se disponível
            if config_controller and hasattr(config_controller, 'carregar_config_impressoras'):
                try:
                    config_controller.carregar_config_impressoras()
                except Exception:
                    pass
            
            # Inicializar o gerenciador de impressão
            
            # Garantir que temos um config_controller válido
            if not config_controller and hasattr(self, 'config_controller'):
                config_controller = self.config_controller

            
            # Se ainda não tivermos um config_controller, tentar obter do controller principal
            if not config_controller and hasattr(self, 'controller') and hasattr(self.controller, 'config_controller'):
                config_controller = self.controller.config_controller
            
            # Se ainda não tivermos um config_controller, tentar obter do controller principal do controller
            if not config_controller and hasattr(self, 'controller') and hasattr(self.controller, 'controller') and hasattr(self.controller.controller, 'config_controller'):
                config_controller = self.controller.controller.config_controller
            
            # Inicializar o gerenciador com o config_controller
            gerenciador = GerenciadorImpressao(config_controller)
            
            # Imprimir o cupom fiscal
            sucesso_cupom = gerenciador.imprimir_cupom_fiscal(venda_dados, itens, self.pagamentos)
            
            # Verificar o tipo de venda
            tipo_venda = venda_dados.get('tipo', '').lower()
            
            # Definir sucesso_comandas como True por padrão
            # Para pedidos de mesa, as comandas já foram impressas quando os itens foram adicionados
            # Para outros tipos de venda, não imprimimos comandas no momento do pagamento
            sucesso_comandas = True
            
            if not sucesso_cupom:
                messagebox.showerror("Erro", "Não foi possível imprimir o cupom fiscal.")
            if not sucesso_cupom and tipo_venda != 'mesa' and not sucesso_comandas:
                messagebox.showerror("Erro", "Não foi possível imprimir as comandas.")
        except Exception as e:
            print(f"Erro ao imprimir cupom fiscal: {e}")
            
    def _obter_itens_venda(self):
        """Obtém os itens da venda para impressão do cupom fiscal"""
        return self.itens_venda
