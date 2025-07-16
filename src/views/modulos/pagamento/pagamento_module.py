"""
Módulo de Pagamentos para o sistema PDV Aquarius.
Permite processar pagamentos para vendas avulsas, delivery e mesas.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import datetime
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.pagamento_controller import PagamentoController
from controllers.cadastro_controller import CadastroController
from utils.impressao import GerenciadorImpressao

class PagamentoModule:
    def __init__(self, master, db_connection, valor_total=0.0, desconto=0.0, 
                 callback_finalizar=None, venda_tipo='avulsa', referencia=None, itens_venda=None, controller=None, taxa_servico=False):
        """
        Inicializa o módulo de pagamentos.
        
        Args:
            master: Widget pai onde o módulo será exibido
            db_connection: Conexão com o banco de dados
            valor_total: Valor total da venda
            desconto: Valor do desconto aplicado
            callback_finalizar: Função a ser chamada quando o pagamento for finalizado
            venda_tipo: Tipo da venda ('avulsa', 'delivery', 'mesa')
            referencia: Referência da venda (número da mesa, id do delivery, etc)
            controller: Referência ao controlador principal da aplicação
        """
        self.master = master
        self.db_connection = db_connection
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
        coluna_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
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
        ttk.Label(subtotal_frame, text=f"R$ {self.valor_total:.2f}".replace('.', ','), style="Info.TLabel").pack(side="right")
        
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
        
        # Separador
        ttk.Separator(resumo_frame, orient="horizontal").pack(fill="x", padx=10, pady=5)
        
        # Total
        total_frame = ttk.Frame(resumo_frame, style="Custom.TFrame")
        total_frame.pack(fill="x", pady=8, padx=10)
        ttk.Label(total_frame, text="TOTAL:", style="Total.TLabel").pack(side="left")
        self.total_label = ttk.Label(total_frame, text=f"R$ {self.valor_final:.2f}".replace('.', ','), style="Total.TLabel")
        self.total_label.pack(side="right")
        
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
        
        ttk.Label(valor_frame, text="Valor a pagar:", style="Valor.TLabel").pack(side="left")
        
        self.valor_pagamento_var = tk.StringVar()
        self.valor_pagamento_entry = ttk.Entry(
            valor_frame, 
            textvariable=self.valor_pagamento_var, 
            font=("Arial", 12), 
            width=15,
            justify="right"
        )
        self.valor_pagamento_entry.pack(side="right")
        
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
                {'id': 4, 'nome': 'PIX'},
                {'id': 5, 'nome': 'Conta Cliente'}
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
        
        # Coluna da direita - Pagamentos realizados
        coluna_direita = ttk.Frame(container)
        coluna_direita.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Lista de pagamentos realizados
        pagamentos_frame = ttk.LabelFrame(coluna_direita, text="Pagamentos Realizados", style="Resumo.TLabelframe")
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
        
        # Botão de finalizar venda
        finalizar_frame = ttk.Frame(coluna_direita)
        finalizar_frame.pack(fill="x", pady=10)
        
        self.finalizar_btn = tk.Button(
            finalizar_frame,
            text="FINALIZAR VENDA",
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            font=("Arial", 12, "bold"),
            padx=15,
            pady=12,
            relief="flat",
            cursor="hand2",
            state="disabled",
            command=self._finalizar_venda
        )
        self.finalizar_btn.pack(fill="x")
        
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
                
            # Se for pagamento em dinheiro e o valor for maior que o restante, perguntar se deseja dar troco
            if forma['nome'].lower() == 'dinheiro' and valor > valor_restante:
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
                valor_efetivo = valor_restante
                troco_valor = troco
            else:
                valor_efetivo = valor
                troco_valor = 0
            
            # Se for Conta Cliente, abrir diálogo para selecionar o cliente
            if forma['nome'] == 'Conta Cliente':
                self._selecionar_cliente_pendura(forma, valor_efetivo)
                return
            
            # Adicionar o pagamento à lista
            pagamento = {
                'forma_id': forma['id'],
                'forma_nome': forma['nome'],
                'valor': valor_efetivo,
                'troco': troco_valor
            }
            
            self.pagamentos.append(pagamento)
            
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
        
    def _selecionar_cliente_pendura(self, forma, valor):
        """Exibe diálogo para selecionar o cliente para vincular o pagamento à conta."""
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.master)
        dialog.title("Selecionar Cliente")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.configure(bg=self.cores["fundo"])
        
        # Centralizar na tela
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(
            frame, 
            text="Selecionar Cliente para Conta", 
            font=("Arial", 14, "bold"),
            foreground=self.cores["texto"],
            background=self.cores["fundo"]
        ).pack(pady=(0, 20))
        
        # Valor a ser vinculado
        ttk.Label(
            frame, 
            text=f"Valor a vincular: R$ {valor:.2f}".replace('.', ','),
            font=("Arial", 12),
            foreground=self.cores["primaria"],
            background=self.cores["fundo"]
        ).pack(pady=(0, 20))
        
        # Campo de busca
        busca_frame = ttk.Frame(frame, style="Custom.TFrame")
        busca_frame.pack(fill="x", pady=10)
        
        ttk.Label(
            busca_frame, 
            text="Buscar cliente:", 
            font=("Arial", 10, "bold"),
            foreground=self.cores["texto"],
            background=self.cores["fundo"]
        ).pack(side="left")
        
        busca_var = tk.StringVar()
        busca_entry = ttk.Entry(busca_frame, textvariable=busca_var, font=("Arial", 10), width=30)
        busca_entry.pack(side="right")
        busca_entry.focus()
        
        # Lista de clientes
        clientes_frame = ttk.Frame(frame)
        clientes_frame.pack(fill="both", expand=True, pady=10)
        
        # Treeview para clientes
        colunas = ('id', 'nome', 'telefone')
        clientes_tree = ttk.Treeview(clientes_frame, columns=colunas, show='headings', height=8)
        
        # Configurar colunas
        clientes_tree.heading('id', text='ID')
        clientes_tree.heading('nome', text='Nome')
        clientes_tree.heading('telefone', text='Telefone')
        
        clientes_tree.column('id', width=50)
        clientes_tree.column('nome', width=250)
        clientes_tree.column('telefone', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(clientes_frame, orient="vertical", command=clientes_tree.yview)
        clientes_tree.configure(yscrollcommand=scrollbar.set)
        
        clientes_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Carregar clientes
        try:
            clientes = self.cadastro_controller.listar_clientes()
            for cliente in clientes:
                clientes_tree.insert('', 'end', values=(cliente['id'], cliente['nome'], cliente.get('telefone', '')))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {str(e)}")
        
        # Função para filtrar clientes
        def filtrar_clientes(*args):
            busca = busca_var.get().lower()
            clientes_tree.delete(*clientes_tree.get_children())
            
            try:
                clientes = self.cadastro_controller.listar_clientes()
                for cliente in clientes:
                    if busca in cliente['nome'].lower() or (cliente.get('telefone') and busca in cliente['telefone']):
                        clientes_tree.insert('', 'end', values=(cliente['id'], cliente['nome'], cliente.get('telefone', '')))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao filtrar clientes: {str(e)}")
        
        # Vincular evento de busca
        busca_var.trace_add("write", filtrar_clientes)
        
        # Botões
        botoes_frame = ttk.Frame(frame)
        botoes_frame.pack(fill="x", pady=(20, 0))
        
        ttk.Button(
            botoes_frame,
            text="Cancelar",
            command=dialog.destroy
        ).pack(side="left", padx=(0, 10))
        
        def confirmar_cliente():
            selecionado = clientes_tree.selection()
            if not selecionado:
                messagebox.showinfo("Aviso", "Selecione um cliente.")
                return
                
            cliente_values = clientes_tree.item(selecionado[0], 'values')
            cliente_id = cliente_values[0]
            cliente_nome = cliente_values[1]
            
            # Adicionar o pagamento à lista
            pagamento = {
                'forma_id': forma['id'],
                'forma_nome': f"{forma['nome']} - {cliente_nome}",
                'valor': valor,
                'cliente_id': cliente_id
            }
            
            self.pagamentos.append(pagamento)
            
            # Atualizar a interface
            self._atualizar_pagamentos()
            
            # Atualizar o valor no campo de entrada para o valor restante
            novo_valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
            if novo_valor_restante > 0:
                self.valor_pagamento_var.set(f"{novo_valor_restante:.2f}".replace('.', ','))
            else:
                self.valor_pagamento_var.set("0,00")
            
            # Fechar o diálogo
            dialog.destroy()
        
        tk.Button(
            botoes_frame,
            text="CONFIRMAR",
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=confirmar_cliente
        ).pack(side="right")
        
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
    
    def _mostrar_selecao_cliente(self, forma):
        """Exibe diálogo para selecionar o cliente para vincular à conta."""
        # Obter lista de clientes
        clientes = self.cadastro_controller.listar_clientes()
        
        if not clientes:
            messagebox.showerror("Erro", "Não há clientes cadastrados.")
            return
        
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.master)
        dialog.title("Selecionar Cliente")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Centralizar na tela
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(
            frame, 
            text="Selecione o Cliente", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))
        
        # Campo de pesquisa
        pesquisa_frame = ttk.Frame(frame)
        pesquisa_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(pesquisa_frame, text="Pesquisar:").pack(side="left")
        
        pesquisa_var = tk.StringVar()
        pesquisa_var.trace_add("write", lambda *args: self._filtrar_clientes(pesquisa_var.get(), clientes_tree, clientes))
        
        pesquisa_entry = ttk.Entry(pesquisa_frame, textvariable=pesquisa_var, width=30)
        pesquisa_entry.pack(side="left", padx=5)
        pesquisa_entry.focus()
        
        # Lista de clientes
        clientes_frame = ttk.Frame(frame)
        clientes_frame.pack(fill="both", expand=True, pady=10)
        
        # Treeview para clientes
        colunas = ('id', 'nome', 'telefone')
        clientes_tree = ttk.Treeview(clientes_frame, columns=colunas, show='headings', height=10)
        
        # Configurar colunas
        clientes_tree.heading('id', text='ID')
        clientes_tree.heading('nome', text='Nome')
        clientes_tree.heading('telefone', text='Telefone')
        
        clientes_tree.column('id', width=50)
        clientes_tree.column('nome', width=250)
        clientes_tree.column('telefone', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(clientes_frame, orient="vertical", command=clientes_tree.yview)
        clientes_tree.configure(yscrollcommand=scrollbar.set)
        
        clientes_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Preencher a lista de clientes
        for cliente in clientes:
            clientes_tree.insert(
                "", 
                "end", 
                values=(
                    cliente['id'],
                    cliente['nome'],
                    cliente.get('telefone', '')
                )
            )
        
        # Botões
        botoes_frame = ttk.Frame(frame)
        botoes_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(
            botoes_frame,
            text="CANCELAR",
            bg=self.cores["terciaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=dialog.destroy
        ).pack(side="left")
        
        tk.Button(
            botoes_frame,
            text="SELECIONAR",
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=lambda: self._selecionar_cliente(clientes_tree, forma, dialog)
        ).pack(side="right")
        
    def _filtrar_clientes(self, termo, tree, clientes):
        """Filtra a lista de clientes pelo termo de pesquisa."""
        # Limpar a árvore
        for item in tree.get_children():
            tree.delete(item)
            
        # Filtrar clientes
        termo = termo.lower()
        for cliente in clientes:
            if (termo in str(cliente['id']).lower() or 
                termo in cliente['nome'].lower() or 
                termo in str(cliente.get('telefone', '')).lower()):
                
                tree.insert(
                    "", 
                    "end", 
                    values=(
                        cliente['id'],
                        cliente['nome'],
                        cliente.get('telefone', '')
                    )
                )
    
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
        else:
            self.finalizar_btn.config(state="disabled")
    
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
    
    def _selecionar_cliente(self, tree, forma, dialog):
        """Seleciona o cliente e solicita o valor a ser vinculado à conta."""
        # Obter o item selecionado
        selection = tree.selection()
        
        if not selection:
            messagebox.showerror("Erro", "Selecione um cliente.")
            return
            
        # Obter os dados do cliente
        cliente_id = tree.item(selection[0], 'values')[0]
        cliente_nome = tree.item(selection[0], 'values')[1]
        
        # Fechar o diálogo de seleção de cliente
        dialog.destroy()
        
        # Calcular valor restante
        valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
        
        # Criar janela de diálogo para o valor
        dialog_valor = tk.Toplevel(self.master)
        dialog_valor.title(f"Vincular à Conta - {cliente_nome}")
        dialog_valor.geometry("400x250")
        dialog_valor.resizable(False, False)
        dialog_valor.transient(self.master)
        dialog_valor.grab_set()
        
        # Centralizar na tela
        dialog_valor.update_idletasks()
        width = dialog_valor.winfo_width()
        height = dialog_valor.winfo_height()
        x = (dialog_valor.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog_valor.winfo_screenheight() // 2) - (height // 2)
        dialog_valor.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(dialog_valor, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Título
        ttk.Label(
            frame, 
            text=f"Vincular à Conta de {cliente_nome}", 
            font=("Arial", 14, "bold")
        ).pack(pady=(0, 20))
        
        # Valor restante
        ttk.Label(
            frame, 
            text=f"Valor restante: R$ {valor_restante:.2f}".replace('.', ','),
            font=("Arial", 12)
        ).pack(pady=(0, 20))
        
        # Entrada de valor
        valor_frame = ttk.Frame(frame)
        valor_frame.pack(fill="x", pady=10)
        
        ttk.Label(valor_frame, text="Valor:", font=("Arial", 12)).pack(side="left")
        
        valor_var = tk.StringVar(value=f"{valor_restante:.2f}".replace('.', ','))
        valor_entry = ttk.Entry(valor_frame, textvariable=valor_var, font=("Arial", 12), width=15)
        valor_entry.pack(side="right")
        valor_entry.select_range(0, 'end')
        valor_entry.focus()
        
        # Botões
        botoes_frame = ttk.Frame(frame)
        botoes_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(
            botoes_frame,
            text="CANCELAR",
            bg=self.cores["terciaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=dialog_valor.destroy
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            botoes_frame,
            text="CONFIRMAR",
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5,
            relief="flat",
            cursor="hand2",
            command=lambda: self._confirmar_conta_cliente(forma, cliente_id, cliente_nome, valor_var.get(), dialog_valor)
        ).pack(side="right")

    def _confirmar_conta_cliente(self, forma, cliente_id, cliente_nome, valor_str, dialog):
        """Confirma a vinculação à conta do cliente."""
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
                
            # Verificar se o valor é maior que o restante
            valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
            if valor > valor_restante:
                valor = valor_restante
            
            # Adicionar o pagamento à lista
            pagamento = {
                'forma_id': forma['id'],
                'forma_nome': f"{forma['nome']} - {cliente_nome}",
                'valor': valor,
                'cliente_id': cliente_id
            }
            
            self.pagamentos.append(pagamento)
            
            # Atualizar a interface
            self._atualizar_pagamentos()
            
            # Fechar o diálogo
            dialog.destroy()
            
            # Atualizar o valor no campo de entrada para o valor restante
            novo_valor_restante = self.valor_final - sum(p['valor'] for p in self.pagamentos)
            if novo_valor_restante > 0:
                self.valor_pagamento_var.set(f"{novo_valor_restante:.2f}".replace('.', ','))
            else:
                self.valor_pagamento_var.set("0,00")
                
        except ValueError:
            messagebox.showerror("Erro", "Por favor, informe um valor válido.")
    
    def _finalizar_venda(self):
        """Finaliza a venda com os pagamentos realizados."""
        # Verificar se o valor pago é suficiente
        # Usar round para evitar problemas de arredondamento com ponto flutuante
        valor_pago = sum(p['valor'] for p in self.pagamentos)
        if round(valor_pago, 2) < round(self.valor_final, 2):
            messagebox.showerror(
                "Erro de Pagamento", 
                f"O valor pago (R$ {valor_pago:.2f}) é menor que o valor final " + 
                f"(R$ {self.valor_final:.2f}).",
                icon="error"
            )
            return
            
        # Finalizar a venda sem confirmação
        
        # Obter o nome do usuário logado, se disponível
        nome_usuario = 'Não identificado'
        if hasattr(self, 'controller') and hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'nome'):
            nome_usuario = self.controller.usuario.nome
        
        # Preparar dados da venda para o callback
        venda_dados = {
            'valor_total': self.valor_total,
            'desconto': self.desconto,
            'valor_final': self.valor_total - self.desconto,
            'data_hora': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'tipo': self.venda_tipo.upper(),
            'observacoes': '',
            'taxa_servico': self.taxa_servico
        }
        
        # Preparar os pagamentos no formato esperado
        pagamentos_formatados = []
        for pagamento in self.pagamentos:
            pagamento_formatado = {
                'forma_id': pagamento['forma_id'],
                'forma_nome': pagamento['forma_nome'],
                'valor': pagamento['valor'],
                'troco': pagamento.get('troco', 0)
            }
            
            # Adicionar informações adicionais, se disponíveis
            if 'cliente_id' in pagamento:
                pagamento_formatado['cliente_id'] = pagamento['cliente_id']
                if 'cliente_nome' in pagamento:
                    pagamento_formatado['cliente_nome'] = pagamento['cliente_nome']
                
                # Adicionar observação para pagamentos vinculados a cliente
                pagamento_formatado['observacao'] = f"{pagamento['forma_nome']} - Cliente: {pagamento.get('cliente_nome', '')}"
            else:
                pagamento_formatado['observacao'] = pagamento['forma_nome']
                
            pagamentos_formatados.append(pagamento_formatado)
            
        # Chamar o callback de finalização, se existir
        if self.callback_finalizar:
            self.callback_finalizar(venda_dados, self.itens_venda, pagamentos_formatados)
        
        # Imprimir o cupom fiscal
        self._imprimir_cupom_fiscal(venda_dados)
        
        # Destruir a janela de pagamento
        if isinstance(self.master, tk.Toplevel):
            self.master.destroy()
        else:
            # Destruir o frame
            if self.frame:
                self.frame.destroy()
    


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
            
            # Verificar estrutura e valores dos itens
            # (Debug prints removidos)
            
            # Obter o controlador de configurações
            config_controller = None
            if hasattr(self, 'config_controller'):
                config_controller = self.config_controller
                
            # Inicializar o gerenciador de impressão
            gerenciador = GerenciadorImpressao(config_controller)
            
            # Imprimir o cupom fiscal
            sucesso_cupom = gerenciador.imprimir_cupom_fiscal(venda_dados, itens, self.pagamentos)
            
            # Verificar o tipo de venda
            tipo_venda = venda_dados.get('tipo', '').lower()
            
            # Imprimir as comandas por tipo de produto separadamente APENAS se NÃO for um pedido de mesa
            # No caso de mesas, os pedidos já foram impressos quando foram adicionados
            sucesso_comandas = True
            if tipo_venda != 'mesa':
                sucesso_comandas = gerenciador.imprimir_comandas_por_tipo(venda_dados, itens)
            else:
                # Para vendas do tipo mesa, as comandas já foram impressas quando os itens foram adicionados
                pass
            
            if not sucesso_cupom:
                messagebox.showerror("Erro", "Não foi possível imprimir o cupom fiscal.")
            if not sucesso_cupom and tipo_venda != 'mesa' and not sucesso_comandas:
                messagebox.showerror("Erro", "Não foi possível imprimir as comandas.")
        except Exception as e:
            print(f"Erro ao imprimir cupom fiscal: {e}")
            
    def _obter_itens_venda(self):
        """Obtém os itens da venda para impressão do cupom fiscal"""
        return self.itens_venda
