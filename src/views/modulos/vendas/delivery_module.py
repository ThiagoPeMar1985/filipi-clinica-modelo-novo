import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.cadastro_controller import CadastroController
from controllers.cliente_controller import ClienteController

class DeliveryModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = parent
        
        # Inicializar os controladores
        self.cadastro_controller = CadastroController()
        self.cliente_controller = ClienteController()
        
        # Cores do tema
        self.cores = {
            "primaria": "#4a6fa5",
            "secundaria": "#4a6fa5",
            "terciaria": "#333f50",
            "fundo": "#f0f2f5",
            "texto": "#000000",
            "texto_claro": "#ffffff",
            "destaque": "#4caf50",
            "alerta": "#f44336"
        }
        
        # Inicializar o carrinho de delivery
        self.itens_pedido = []
        
        # Dados do cliente selecionado
        self.cliente_atual = None
        
    def show(self):
        # Limpar o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Criar o frame principal com estilo Card
        frame = ttk.Frame(self.frame, style="Card.TFrame")
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configurar estilo para as tabelas
        style = ttk.Style()
        style.configure("Treeview", 
                      background="white",
                      foreground="black",  
                      rowheight=25,
                      fieldbackground="white")
        style.configure("Treeview.Heading", 
                      font=("Arial", 10, "bold"), 
                      background=self.cores["primaria"],
                      foreground=self.cores["texto"])
        style.map("Treeview", 
                background=[("selected", "#4a6fa5")],
                foreground=[("selected", "#ffffff")])
        
        # Título da página
        titulo_frame = tk.Frame(frame, bg=self.cores["fundo"])
        titulo_frame.pack(fill="x", padx=0, pady=0)
        
        titulo_label = tk.Label(
            titulo_frame, 
            text="DELIVERY", 
            font=('Arial', 16, 'bold'),
            bg=self.cores["fundo"],
            fg=self.cores["texto"],
            padx=15,
            pady=10
        )
        titulo_label.pack(side="left")
        
        # Data e hora atual
        data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        data_label = tk.Label(
            titulo_frame,
            text=data_atual,
            font=('Arial', 12),
            bg=self.cores["fundo"],
            fg=self.cores["texto"],
            padx=15
        )
        data_label.pack(side="right", padx=15)
        
        # Container principal com grid para melhor divisão do espaço
        container = ttk.Frame(frame)
        container.pack(fill="both", expand=True, padx=15, pady=5)
        container.columnconfigure(0, weight=3)  # Coluna da lista de produtos (mais larga)
        container.columnconfigure(1, weight=2)  # Coluna do carrinho
        
        # Área de busca de cliente (entre o título e a lista de produtos)
        cliente_frame = ttk.Frame(container)
        cliente_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Título da área de cliente
        cliente_header = ttk.Frame(cliente_frame)
        cliente_header.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            cliente_header, 
            text="Cliente Delivery", 
            font=('Arial', 12, 'bold')
        ).pack(side="left", anchor="w")
        
        # Área de dados do cliente
        dados_cliente_frame = ttk.Frame(cliente_frame)
        dados_cliente_frame.pack(fill="x", pady=5)
        
        # Primeira linha: Busca por telefone ou nome
        busca_frame = ttk.Frame(dados_cliente_frame)
        busca_frame.pack(fill="x", pady=5)
        
        # Opção de busca
        ttk.Label(busca_frame, text="Buscar por:").pack(side="left", padx=(0, 5))
        
        # Variável para controlar o tipo de busca
        self.tipo_busca = tk.StringVar(value="telefone")
        
        # Radio buttons para selecionar o tipo de busca
        ttk.Radiobutton(busca_frame, text="Telefone", variable=self.tipo_busca, value="telefone").pack(side="left", padx=5)
        ttk.Radiobutton(busca_frame, text="Nome", variable=self.tipo_busca, value="nome").pack(side="left", padx=5)
        
        # Campo de busca
        ttk.Label(busca_frame, text="Valor:").pack(side="left", padx=(15, 5))
        self.busca_cliente_entry = ttk.Entry(busca_frame, width=25)
        self.busca_cliente_entry.pack(side="left", padx=5)
        
        # Botão de busca
        busca_button = tk.Button(
            busca_frame, 
            text="Buscar Cliente", 
            command=self._buscar_cliente,
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2'
        )
        busca_button.pack(side="left", padx=5)
        
        # Botão de editar cliente
        self.editar_button = tk.Button(
            busca_frame, 
            text="Editar Clientes", 
            command=self._editar_cliente,
            bg=self.cores["secundaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2'
        )
        self.editar_button.pack(side="left", padx=5)
        
        # Segunda linha: Informações do cliente
        info_cliente_frame = ttk.Frame(dados_cliente_frame)
        info_cliente_frame.pack(fill="x", pady=5)
        
        # Nome do cliente
        self.nome_cliente_label = ttk.Label(
            info_cliente_frame, 
            text="Nenhum cliente selecionado",
            font=('Arial', 9, 'bold'),
            width=40
        )
        self.nome_cliente_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Telefone do cliente
        self.telefone_cliente_label = ttk.Label(
            info_cliente_frame, 
            text="-",
            font=('Arial', 9, 'bold'),
            width=25
        )
        self.telefone_cliente_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Label de endereço (oculto, mantido para compatibilidade)
        self.endereco_cliente_label = ttk.Label(info_cliente_frame, text="")
        self.endereco_cliente_label.grid_remove()
        
        # Frame esquerdo - Lista de produtos
        produtos_frame = ttk.Frame(container)
        produtos_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Cabeçalho da lista de produtos com título e busca na mesma linha
        header_frame = ttk.Frame(produtos_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Título da lista de produtos
        ttk.Label(
            header_frame, 
            text="Lista de Produtos", 
            font=('Arial', 12, 'bold')
        ).pack(side="left", anchor="w")
        
        # Campo de busca integrado ao cabeçalho
        busca_frame = ttk.Frame(header_frame)
        busca_frame.pack(side="right", fill="x")
        
        ttk.Label(busca_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        
        self.busca_produto_entry = ttk.Entry(busca_frame, width=20)
        self.busca_produto_entry.pack(side="left")
        
        busca_button = tk.Button(
            busca_frame, 
            text="Buscar", 
            command=self._buscar_produtos,
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2'
        )
        busca_button.pack(side="left", padx=(5, 0))
        
        # Botões para filtrar por tipo de produto em uma barra horizontal
        tipos_frame = ttk.Frame(produtos_frame)
        tipos_frame.pack(fill="x", pady=(0, 10))
        
        # Definir os tipos de produtos
        tipos_produtos = ["Bar", "Cozinha", "Sobremesas", "Outros"]
        
        # Criar botões para cada tipo com distribuição uniforme
        for i, tipo in enumerate(tipos_produtos):
            tipos_frame.columnconfigure(i, weight=1)  # Distribuição uniforme
            btn = tk.Button(
                tipos_frame,
                text=tipo,
                bg=self.cores["primaria"],
                fg=self.cores["texto_claro"],
                bd=0,
                padx=10,
                pady=5,
                relief='flat',
                cursor='hand2',
                command=lambda t=tipo: self._filtrar_produtos_por_tipo(t)
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
        
        # Criação de um frame para conter a tabela e a barra de rolagem
        tabela_frame = ttk.Frame(produtos_frame)
        tabela_frame.pack(fill="both", expand=True)
        
        # Tabela de produtos com altura ajustada para aproveitar mais espaço
        colunas_produtos = ("Código", "Produto", "Preço", "Estoque")
        
        # Configurar estilo para a tabela de produtos
        style = ttk.Style()
        style.configure("Produtos.Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            highlightthickness=0
        )
        style.configure("Produtos.Treeview.Heading",
            borderwidth=0,
            relief="flat"
        )
        style.layout("Produtos.Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        self.produtos_tree = ttk.Treeview(
            tabela_frame, 
            columns=colunas_produtos, 
            show="headings", 
            height=15,
            style="Produtos.Treeview"
        )
        
        # Configurar menu de contexto para a tabela de produtos (apenas opções)
        self.menu_contexto_produto = tk.Menu(self.produtos_tree, tearoff=0)
        self.menu_contexto_produto.add_command(label="Adicionar Opções", command=self._mostrar_opcoes_produto)
        
        # Vincular evento de clique direito
        self.produtos_tree.bind("<Button-3>", self._mostrar_menu_contexto_produto)
        
        # Configurar cabeçalhos com larguras proporcionais
        larguras = {"Código": 80, "Produto": 200, "Preço": 100, "Estoque": 80}
        for col in colunas_produtos:
            self.produtos_tree.heading(col, text=col)
            self.produtos_tree.column(col, width=larguras.get(col, 100))
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.produtos_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.produtos_tree.configure(yscrollcommand=scrollbar.set)
        self.produtos_tree.pack(fill="both", expand=True)
        
        # Botão de adicionar ao carrinho
        botoes_frame = ttk.Frame(produtos_frame)
        botoes_frame.pack(fill="x", pady=5)
        
        adicionar_button = tk.Button(
            botoes_frame, 
            text="Adicionar ao Carrinho", 
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold'),
            command=self._adicionar_ao_carrinho
        )
        adicionar_button.pack(fill="x")
        
        # Frame direito - Carrinho de compras
        carrinho_frame = ttk.Frame(container)
        carrinho_frame.grid(row=1, column=1, sticky="nsew")
        
        # Cabeçalho do carrinho
        carrinho_header = ttk.Frame(carrinho_frame)
        carrinho_header.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            carrinho_header, 
            text="Carrinho de Compras", 
            font=('Arial', 12, 'bold')
        ).pack(side="left", anchor="w")
        
        # Botão para limpar carrinho
        limpar_button = tk.Button(
            carrinho_header,
            text="Limpar",
            command=self._limpar_carrinho,
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2'
        )
        limpar_button.pack(side="right")
        
        # Tabela do carrinho
        carrinho_tabela_frame = ttk.Frame(carrinho_frame)
        carrinho_tabela_frame.pack(fill="both", expand=True)
        
        # Colunas da tabela do carrinho
        colunas_carrinho = ("Código", "Produto", "Qtd", "Unit.", "Total")
        
        # Configurar estilo para remover as bordas
        style = ttk.Style()
        style.configure("Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            highlightthickness=0
        )
        style.configure("Treeview.Heading",
            borderwidth=0,
            relief="flat"
        )
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        self.carrinho_tree = ttk.Treeview(
            carrinho_tabela_frame, 
            columns=colunas_carrinho, 
            show="headings", 
            height=15,
            style="Treeview"
        )
        
        # Configurar cabeçalhos
        larguras_carrinho = {"Código": 60, "Produto": 150, "Qtd": 50, "Unit.": 80, "Total": 80}
        for col in colunas_carrinho:
            self.carrinho_tree.heading(col, text=col)
            self.carrinho_tree.column(col, width=larguras_carrinho.get(col, 80))
        
        # Adicionar barra de rolagem
        scrollbar_carrinho = ttk.Scrollbar(carrinho_tabela_frame, orient="vertical", command=self.carrinho_tree.yview)
        scrollbar_carrinho.pack(side="right", fill="y")
        self.carrinho_tree.configure(yscrollcommand=scrollbar_carrinho.set)
        self.carrinho_tree.pack(fill="both", expand=True)
        
        # Vincular duplo clique para remover do carrinho
        self.carrinho_tree.bind("<Double-1>", self._remover_do_carrinho)
        
        # Área de informações de entrega
        entrega_frame = ttk.LabelFrame(carrinho_frame, text="Informações de Entrega")
        entrega_frame.pack(fill="x", pady=10)
        
        # Observações
        ttk.Label(entrega_frame, text="Observações:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.observacoes_entry = ttk.Entry(entrega_frame, width=30)
        self.observacoes_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Taxa de entrega
        ttk.Label(entrega_frame, text="Taxa de Entrega:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.taxa_entry = ttk.Entry(entrega_frame, width=10)
        self.taxa_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.taxa_entry.insert(0, "0.00")
        
        # Barra inferior com total e finalização
        barra_inferior = ttk.Frame(container)
        barra_inferior.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Total
        total_frame = ttk.Frame(barra_inferior)
        total_frame.pack(side="left")
        
        ttk.Label(total_frame, text="Total do Pedido:", font=("Arial", 12, "bold")).pack(side="left")
        self.total_label = ttk.Label(total_frame, text="R$ 0,00", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=5)
        
        # Botão de finalizar pedido
        self.btn_finalizar = ttk.Button(
            barra_inferior,
            text="Finalizar Pedido",
            style="Accent.TButton",
            command=self._finalizar_pedido
        )
        self.btn_finalizar.pack(side="right")
        
        # Carregar produtos do banco de dados
        self._carregar_produtos()
        
        # Garantir que o frame seja exibido
        self.frame.update()
        return frame
    
    def _buscar_cliente(self):
        valor_busca = self.busca_cliente_entry.get().strip()
        tipo_busca = self.tipo_busca.get()
        
        if not valor_busca:
            messagebox.showwarning("Aviso", f"Digite o {tipo_busca} do cliente para buscar.")
            return
        
        try:
            if tipo_busca == "telefone":
                # Buscar por telefone (pode retornar múltiplos clientes)
                clientes = self.cliente_controller.buscar_cliente_por_telefone(valor_busca)
                if clientes:
                    if len(clientes) == 1:
                        # Apenas um cliente encontrado, seleciona automaticamente
                        self.cliente_atual = clientes[0]
                        self._atualizar_dados_cliente()
                    else:
                        # Mostra diálogo de seleção para múltiplos clientes
                        self._mostrar_selecao_clientes(clientes)
                else:
                    if messagebox.askyesno("Cliente não encontrado", "Cliente não encontrado. Deseja cadastrar um novo cliente?"):
                        # Abre o formulário em branco para cadastrar novo cliente
                        self._abrir_formulario_novo_cliente(None, [])
            else:
                # Buscar por nome (pode retornar múltiplos clientes)
                clientes = self.cliente_controller.buscar_cliente_por_nome(valor_busca)
                if clientes:
                    if len(clientes) == 1:
                        # Apenas um cliente encontrado, seleciona automaticamente
                        self.cliente_atual = clientes[0]
                        self._atualizar_dados_cliente()
                        messagebox.showinfo("Sucesso", "Cliente encontrado!")
                    else:
                        # Múltiplos clientes, mostrar diálogo de seleção
                        self._mostrar_selecao_clientes(clientes)
                else:
                    if messagebox.askyesno("Cliente não encontrado", "Cliente não encontrado. Deseja cadastrar um novo cliente?"):
                        # Abre o formulário em branco para cadastrar novo cliente
                        self._abrir_formulario_novo_cliente(None, [])
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao buscar o cliente: {str(e)}")
            print(f"Erro ao buscar cliente: {e}")
    
    def _mostrar_selecao_clientes(self, clientes):
        """
        Mostra um diálogo para selecionar entre múltiplos clientes encontrados.
        
        Args:
            clientes: Lista de dicionários contendo os dados dos clientes
        """
        dialog = tk.Toplevel(self.frame)
        dialog.title("Selecione um cliente")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Centralizar o diálogo
        largura = 700
        altura = 500
        x = (self.frame.winfo_screenwidth() - largura) // 2
        y = (self.frame.winfo_screenheight() - altura) // 2
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        dialog.configure(bg=self.cores["fundo"])
        
        # Frame principal com borda e sombra
        main_frame = tk.Frame(dialog, bg=self.cores["fundo"], padx=10, pady=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título com fundo cinza
        titulo_frame = tk.Frame(main_frame, bg=self.cores["fundo"])
        titulo_frame.pack(fill="x", pady=(0, 10))
        
        titulo_label = tk.Label(
            titulo_frame, 
            text="SELECIONE O CLIENTE", 
            font=('Arial', 14, 'bold'),
            bg=self.cores["fundo"],
            fg=self.cores["texto"],
            padx=10,
            pady=8
        )
        titulo_label.pack()
        
        # Frame para a tabela com fundo branco sem borda
        tabela_frame = tk.Frame(main_frame, bg='white')
        tabela_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Tabela de clientes
        columns = ("ID", "Nome", "Telefone", "Endereço")
        
        # Configurar estilo para a tabela de clientes
        style = ttk.Style()
        style.configure("Clientes.Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            rowheight=30
        )
        style.configure("Clientes.Treeview.Heading",
            borderwidth=0,
            relief="flat"
        )
        style.layout("Clientes.Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        tree = ttk.Treeview(
            tabela_frame, 
            columns=columns, 
            show="headings", 
            selectmode="browse",
            style="Clientes.Treeview"
        )
        
        # Configurar colunas
        tree.column("ID", width=50, anchor="center")
        tree.column("Nome", width=200, anchor="w")
        tree.column("Telefone", width=120, anchor="center")
        tree.column("Endereço", width=280, anchor="w")
        
        # Cabeçalhos
        for col in columns:
            tree.heading(col, text=col)
        
        # Adicionar clientes à tabela
        for cliente in clientes:
            tree.insert("", "end", values=(
                cliente.get("id", ""),
                cliente.get("nome", ""),
                cliente.get("telefone_principal", ""),
                f"{cliente.get('endereco', '')}, {cliente.get('numero', '')} - {cliente.get('bairro', '')}"
            ))
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout da tabela
        tree.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        scrollbar.pack(side="right", fill="y")
        
        # Frame dos botões com fundo claro
        btn_frame = tk.Frame(main_frame, bg=self.cores["fundo"])
        btn_frame.pack(fill="x", pady=(5, 0))
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            btn_frame,
            text="CANCELAR",
            font=('Arial', 10, 'bold'),
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=dialog.destroy
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Botão Novo Cliente
        btn_novo_cliente = tk.Button(
            btn_frame, 
            text="NOVO CLIENTE",
            font=('Arial', 10, 'bold'),
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=lambda: self._abrir_formulario_novo_cliente(dialog, clientes)
        )
        btn_novo_cliente.pack(side="right", padx=5)
        
        # Botão Selecionar
        btn_selecionar = tk.Button(
            btn_frame, 
            text="SELECIONAR",
            font=('Arial', 10, 'bold'),
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=lambda: self._selecionar_cliente_dialogo(dialog, tree, clientes)
        )
        btn_selecionar.pack(side="right", padx=5)
        
        # Configurar duplo clique para selecionar
        tree.bind("<Double-1>", lambda e: self._selecionar_cliente_dialogo(dialog, tree, clientes))
    
    def _selecionar_cliente_dialogo(self, dialog, tree, clientes):
        """Seleciona o cliente da tabela e fecha o diálogo."""
        selected = tree.selection()
        if not selected:
            return
            
        item = tree.item(selected[0])
        cliente_id = item['values'][0]
        
        # Encontrar o cliente selecionado
        for cliente in clientes:
            if cliente.get('id') == cliente_id:
                self.cliente_atual = cliente
                self._atualizar_dados_cliente()
                dialog.destroy()
                break
    
    def _abrir_formulario_novo_cliente(self, dialog, clientes_lista, nome="", telefone=""):
        """Abre o formulário para cadastrar um novo cliente.
        
        Args:
            dialog: Referência ao diálogo de seleção de clientes
            clientes_lista: Lista de clientes existente
            nome: Nome do cliente para pré-preenchimento (opcional)
            telefone: Telefone do cliente para pré-preenchimento (opcional)
        """
        def callback_cliente_salvo(novo_cliente):
            try:
                # Salva o cliente no banco de dados
                sucesso, resultado = self.cliente_controller.cadastrar_cliente(novo_cliente)
                
                if sucesso:
                    # Atualiza o ID do cliente com o retorno do banco de dados
                    novo_cliente['id'] = resultado
                    
                    # Adiciona o novo cliente à lista de clientes existente
                    if clientes_lista is not None:
                        clientes_lista.append(novo_cliente)
                    
                    # Atualiza o cliente atual
                    self.cliente_atual = novo_cliente
                    self._atualizar_dados_cliente()
                    
                    messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
                else:
                    messagebox.showerror("Erro", f"Não foi possível cadastrar o cliente: {resultado}")
                    return
                
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o cliente: {str(e)}")
                print(f"Erro ao salvar cliente: {e}")
                return
            finally:
                # Fecha o diálogo de seleção de clientes se existir
                if dialog and dialog.winfo_exists():
                    dialog.destroy()
        
        # Importa o diálogo de cliente aqui para evitar importação circular
        from src.views.dialogs.cliente_dialog import ClienteDialog
        
        # Cria e exibe o diálogo de cliente com os dados fornecidos
        cliente_data = {
            'nome': nome,
            'telefone': telefone
        }
        cliente_dialog = ClienteDialog(
            parent=self.frame,
            controller=self.controller,
            cliente_data=cliente_data,
            callback=callback_cliente_salvo
        )
        cliente_dialog.center()
        cliente_dialog.grab_set()
    
    def _editar_cliente(self):
        """Abre uma janela com a lista de clientes para edição"""
        # Criar janela de lista de clientes
        janela = tk.Toplevel(self.frame)
        janela.title("Lista de Clientes")
        janela.geometry("800x500")
        
        # Frame para a lista de clientes
        frame_lista = ttk.Frame(janela)
        frame_lista.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        # Criar a Treeview para exibir os clientes
        colunas = ('id', 'nome', 'telefone', 'endereco')
        tree = ttk.Treeview(
            frame_lista,
            columns=colunas,
            show='headings',
            yscrollcommand=scrollbar.set
        )
        
        # Configurar as colunas
        tree.heading('id', text='ID')
        tree.heading('nome', text='Nome')
        tree.heading('telefone', text='Telefone')
        tree.heading('endereco', text='Endereço')
        
        tree.column('id', width=50, anchor='center')
        tree.column('nome', width=200)
        tree.column('telefone', width=150, anchor='center')
        tree.column('endereco', width=350)
        
        # Adicionar a treeview e a scrollbar
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=tree.yview)
        
        # Frame para os botões
        frame_botoes = ttk.Frame(janela)
        frame_botoes.pack(fill='x', padx=10, pady=5)
        
        # Frame para os botões de ação
        frame_acoes = ttk.Frame(frame_botoes)
        frame_acoes.pack(side='right')
        
        # Botão Excluir Cliente
        btn_excluir = tk.Button(
            frame_acoes,
            text="Excluir Cliente",
            command=lambda: self._excluir_cliente_selecionado(tree, janela),
            bg="#d32f2f",  # Vermelho mais escuro
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 9, 'bold')
        )
        btn_excluir.pack(side='right', padx=5)
        
        # Botão Editar Cliente
        btn_editar = tk.Button(
            frame_acoes,
            text="Editar Cliente",
            command=lambda: self._editar_cliente_selecionado(tree, janela),
            bg=self.cores["secundaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 9, 'bold')
        )
        btn_editar.pack(side='right', padx=5)
        
        # Botão Fechar
        btn_fechar = tk.Button(
            frame_botoes,
            text="Fechar",
            command=janela.destroy,
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 9, 'bold')
        )
        btn_fechar.pack(side='left', padx=5)
        
        # Carregar clientes na tabela
        self._carregar_clientes_na_tabela(tree)
        
        # Centralizar a janela
        self._centralizar_janela(janela)
    
    def _excluir_cliente_selecionado(self, tree, janela):
        """Exclui o cliente selecionado da tabela"""
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return
            
        # Obter o ID e nome do cliente selecionado
        item = tree.item(selecionado[0])
        cliente_id = item['values'][0]
        cliente_nome = item['values'][1]
        
        # Obter o telefone do cliente
        telefone = item['values'][2] if len(item['values']) > 2 else ""
        
        # Confirmar a exclusão
        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir permanentemente o cliente:\n\n"
            f"Nome: {cliente_nome}\n"
            f"Telefone: {telefone}\n\n"
            "Esta ação não pode ser desfeita!",
            icon='warning'
        ):
            # Excluir o cliente do banco de dados
            sucesso, mensagem = self.cliente_controller.excluir_cliente(cliente_id)
            
            if sucesso:
                # Remover o item da tabela
                tree.delete(selecionado[0])
                messagebox.showinfo("Sucesso", mensagem)
            else:
                messagebox.showerror("Erro", f"Falha ao excluir cliente: {mensagem}")
    
    def _editar_cliente_selecionado(self, tree, janela):
        """Abre o diálogo para editar o cliente selecionado na tabela"""
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar.")
            return
            
        # Obter o ID do cliente selecionado
        item = tree.item(selecionado[0])
        cliente_id = item['values'][0]  # ID está na primeira coluna
        
        # Buscar os dados completos do cliente
        sucesso, cliente = self.cliente_controller.buscar_cliente_por_id(cliente_id)
        if not sucesso or not isinstance(cliente, dict):
            messagebox.showerror("Erro", "Não foi possível carregar os dados do cliente.")
            return
            
        # Abrir o diálogo de edição
        from views.dialogs.cliente_dialog import ClienteDialog
        
        def callback_atualizacao(dados_atualizados):
            if dados_atualizados:
                # Atualizar o cliente no banco de dados
                sucesso, mensagem = self.cliente_controller.atualizar_cliente(cliente_id, dados_atualizados)
                if sucesso:
                    # Atualizar a lista de clientes
                    self._carregar_clientes_na_tabela(tree)
                    messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
                else:
                    messagebox.showerror("Erro", f"Falha ao atualizar cliente: {mensagem}")
        
        # Criar uma cópia do dicionário de cliente para evitar modificar o original
        dados_cliente = cliente.copy()
        
        # Garantir que todos os campos esperados existam no dicionário
        campos_obrigatorios = {
            'nome': '', 'telefone': '', 'telefone2': '', 'email': '', 
            'endereco': '', 'numero': '', 'complemento': '', 'bairro': '', 
            'cidade': '', 'uf': '', 'cep': '', 'ponto_referencia': '', 
            'observacoes': '', 'regiao_entrega_id': None
        }
        
        for campo, valor_padrao in campos_obrigatorios.items():
            if campo not in dados_cliente:
                dados_cliente[campo] = valor_padrao
        
        # Criar o diálogo com os dados formatados
        dialog = ClienteDialog(
            parent=janela,
            controller=self.controller,
            cliente_data=dados_cliente,
            callback=callback_atualizacao
        )
        dialog.grab_set()
    
    def _carregar_clientes_na_tabela(self, tree):
        """Carrega a lista de clientes na tabela"""
        # Limpar a tabela
        for item in tree.get_children():
            tree.delete(item)
            
        try:
            # Buscar clientes usando um termo vazio para trazer todos
            clientes = self.cliente_controller.buscar_cliente_por_nome("")
            
            # Adicionar clientes à tabela
            for cliente in clientes:
                endereco = f"{cliente.get('endereco', '')}, {cliente.get('numero', '')} - {cliente.get('bairro', '')}"
                tree.insert('', 'end', values=(
                    cliente.get('id', ''),
                    cliente.get('nome', ''),
                    cliente.get('telefone', ''),
                    endereco
                ))
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            messagebox.showerror("Erro", f"Não foi possível carregar a lista de clientes: {str(e)}")
    
    def _centralizar_janela(self, janela):
        """Centraliza a janela na tela"""
        janela.update_idletasks()
        width = janela.winfo_width()
        height = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (width // 2)
        y = (janela.winfo_screenheight() // 2) - (height // 2)
        janela.geometry(f'{width}x{height}+{x}+{y}')
        
    def _atualizar_dados_cliente(self, dados_atualizados=None):
        if dados_atualizados:
            self.cliente_atual = dados_atualizados
        if self.cliente_atual:
            # Atualizar o rótulo do nome em negrito
            self.nome_cliente_label.config(
                text=f"Nome: {self.cliente_atual['nome']}",
                font=('Arial', 9, 'bold')
            )
            
            # Atualizar o rótulo do telefone em negrito
            self.telefone_cliente_label.config(
                text=f"Telefone: {self.cliente_atual.get('telefone_principal', self.cliente_atual.get('telefone', '-'))}",
                font=('Arial', 9, 'bold')
            )
            
            # Esconder o campo de endereço
            self.endereco_cliente_label.grid_remove()
    def _carregar_produtos(self, tipo=None):
        """Carrega todos os produtos ou filtra por tipo"""
        # Limpar a tabela atual
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
            
        try:
            # Obter produtos do banco de dados
            produtos = self.cadastro_controller.listar_produtos()
            
            # Filtrar por tipo se especificado
            if tipo:
                produtos = [p for p in produtos if p.get('tipo') == tipo]
                
            # Inserir na tabela
            for produto in produtos:
                self.produtos_tree.insert(
                    "", 
                    tk.END, 
                    values=(
                        produto.get('id', ''), 
                        produto.get('nome', ''), 
                        f"R$ {float(produto.get('preco_venda', 0)):.2f}".replace('.', ','), 
                        produto.get('quantidade_minima', '0')
                    )
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {str(e)}")
    
    def _buscar_produtos(self):
        termo = self.busca_produto_entry.get().strip().lower()
        
        if not termo:
            # Se o campo de busca estiver vazio, recarregar todos os produtos
            self._carregar_produtos()
            return
            
        # Limpar a tabela atual
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
            
        # Obter todos os produtos
        produtos = self.cadastro_controller.listar_produtos()
        
        # Filtrar pelo termo de busca
        produtos_filtrados = [p for p in produtos if termo in p.get('nome', '').lower()]
            
        # Inserir na tabela
        for produto in produtos_filtrados:
            self.produtos_tree.insert(
                "", 
                tk.END, 
                values=(
                    produto.get('id', ''), 
                    produto.get('nome', ''), 
                    f"R$ {float(produto.get('preco_venda', 0)):.2f}".replace('.', ','), 
                    produto.get('quantidade_estoque', '0')
                )
            )
    
    def _filtrar_produtos_por_tipo(self, tipo):
        """Filtra produtos por tipo"""
        self._carregar_produtos(tipo)
        
    def _mostrar_menu_contexto_produto(self, event):
        """Exibe o menu de contexto para o produto selecionado"""
        try:
            # Identificar o item clicado
            if hasattr(event, 'y'):
                item = self.produtos_tree.identify_row(event.y)
                if item:
                    # Selecionar o item clicado
                    self.produtos_tree.selection_set(item)
                    # Exibir o menu de contexto
                    if hasattr(event, 'x_root') and hasattr(event, 'y_root'):
                        self.menu_contexto_produto.post(event.x_root, event.y_root)
                    else:
                        # Se não tiver as coordenadas, mostrar próximo ao mouse
                        self.menu_contexto_produto.post(event.x, event.y)
        except Exception as e:
            print(f"Erro ao exibir menu de contexto: {e}")
    
    def _mostrar_opcoes_produto(self, event=None):
        """Exibe as opções disponíveis para o produto selecionado"""
        try:
            # Verificar se um cliente foi selecionado
            if not self.cliente_atual:
                messagebox.showwarning("Aviso", "Selecione um cliente antes de adicionar produtos ao carrinho.")
                return
                
            # Obter o item selecionado na tabela de produtos
            selecionado = self.produtos_tree.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um produto para adicionar opções.")
                return
                
            # Obter os dados do produto selecionado
            item = self.produtos_tree.item(selecionado[0])
            valores = item['values']
            
            # Verificar se o item tem valores
            if not valores or len(valores) < 2:  # Pelo menos ID e nome
                messagebox.showwarning("Aviso", "Não foi possível obter os dados do produto selecionado.")
                return
                
            produto_id = valores[0]
            produto_nome = valores[1] if len(valores) > 1 else "Produto"  # Nome padrão se não houver
        
            # Verificar se o produto tem opções antes de criar a janela
            from controllers.opcoes_controller import OpcoesController
            
            # Obter a conexão com o banco de dados do controlador principal
            db_connection = getattr(self.controller, 'db_connection', None)
            if not db_connection:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
                return
                
            # Criar o controlador de opções com a conexão
            opcoes_controller = OpcoesController(db_connection=db_connection)
            
            # Verificar se o controlador foi criado corretamente
            if not hasattr(opcoes_controller, 'db') or opcoes_controller.db is None:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados de opções.")
                return
                
            # Verificar se o produto tem opções antes de criar a janela
            grupos_opcoes = opcoes_controller.listar_opcoes_por_produto(produto_id)
            
            if not grupos_opcoes:
                messagebox.showinfo("Informação", "Este produto não possui opções configuradas.")
                return
                
            # Só cria a janela se o produto tiver opções
            self.janela_opcoes = tk.Toplevel(self.frame)
            self.janela_opcoes.title(f"Opções para {produto_nome}")
            self.janela_opcoes.geometry("400x500")
            
            # Frame principal
            frame_principal = ttk.Frame(self.janela_opcoes, padding="10")
            frame_principal.pack(fill="both", expand=True)
                
            # Dicionário para armazenar as seleções do usuário
            self.selecoes_opcoes = {}
            
            # Para cada grupo de opções
            for grupo_id, grupo_info in grupos_opcoes.items():
                grupo_frame = ttk.LabelFrame(frame_principal, text=grupo_info['nome'], padding="5")
                grupo_frame.pack(fill="x", pady=5)
                
                # Verificar se é seleção única ou múltipla
                if grupo_info['selecao_maxima'] == 1:
                    # Seleção única (Radiobuttons)
                    var = tk.StringVar()
                    self.selecoes_opcoes[grupo_id] = {'var': var, 'tipo': 'unico'}
                    
                    for opcao in grupo_info['itens']:
                        rb = ttk.Radiobutton(
                            grupo_frame,
                            text=f"{opcao['nome']} (+R$ {opcao['preco_adicional']:.2f})",
                            variable=var,
                            value=str(opcao['id'])
                        )
                        rb.pack(anchor="w")
                else:
                    # Seleção múltipla (Checkbuttons)
                    self.selecoes_opcoes[grupo_id] = {'var': [], 'tipo': 'multiplo'}
                    
                    for opcao in grupo_info['itens']:
                        var = tk.BooleanVar()
                        self.selecoes_opcoes[grupo_id]['var'].append((var, opcao))
                        
                        cb = ttk.Checkbutton(
                            grupo_frame,
                            text=f"{opcao['nome']} (+R$ {opcao['preco_adicional']:.2f})",
                            variable=var
                        )
                        cb.pack(anchor="w")
            
            # Botão para confirmar as opções
            btn_confirmar = tk.Button(
                frame_principal,
                text="Confirmar Opções",
                bg=self.cores["destaque"],
                fg=self.cores["texto_claro"],
                padx=10,
                pady=5,
                command=lambda: self._adicionar_ao_carrinho_com_opcoes(produto_id, valores)
            )
            btn_confirmar.pack(pady=10)
            
        except Exception as e:
            error_msg = f"Erro ao carregar opções: {str(e)}"
            print(error_msg)  # Log para debug
            messagebox.showerror("Erro", error_msg)
            if hasattr(self, 'janela_opcoes') and self.janela_opcoes and self.janela_opcoes.winfo_exists():
                try:
                    self.janela_opcoes.destroy()
                except:
                    pass
    
    def _adicionar_ao_carrinho_com_opcoes(self, produto_id, valores_produto):
        """Adiciona o produto ao carrinho com as opções selecionadas"""
        try:
            # Obter as opções selecionadas
            opcoes_selecionadas = []
            
            for grupo_id, selecao in self.selecoes_opcoes.items():
                if selecao['tipo'] == 'unico' and selecao['var'].get():
                    # Opção única selecionada
                    opcoes_selecionadas.append({
                        'grupo_id': grupo_id,
                        'opcao_id': int(selecao['var'].get())
                    })
                elif selecao['tipo'] == 'multiplo':
                    # Múltiplas opções podem ser selecionadas
                    for var, opcao in selecao['var']:
                        if var.get():
                            opcoes_selecionadas.append({
                                'grupo_id': grupo_id,
                                'opcao_id': opcao['id'],
                                'nome': opcao['nome'],
                                'preco_adicional': opcao.get('preco_adicional', 0.0)
                            })
            
            # Fechar a janela de opções
            if hasattr(self, 'janela_opcoes') and self.janela_opcoes.winfo_exists():
                self.janela_opcoes.destroy()
            
            # Adicionar ao carrinho
            self._adicionar_ao_carrinho(produto_id, valores_produto, opcoes_selecionadas)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar opções: {str(e)}")
    
    def _adicionar_ao_carrinho(self, produto_id=None, valores=None, opcoes_selecionadas=None, event=None):
        """Adiciona o produto selecionado ao carrinho de compras"""
        # Verificar se um cliente foi selecionado
        if not self.cliente_atual:
            messagebox.showwarning("Aviso", "Selecione um cliente antes de adicionar produtos ao carrinho.")
            return
            
        # Se o método foi chamado por um evento de clique na tabela
        if event:
            # Obter o item clicado
            item_id = self.produtos_tree.identify_row(event.y)
            if not item_id:
                return
            item = self.produtos_tree.item(item_id)
            valores = item["values"]
            produto_id = valores[0]
        # Se não foram fornecidos valores, obter da seleção atual
        elif valores is None:
            # Obter o item selecionado na tabela de produtos
            selecionado = self.produtos_tree.selection()
            
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um produto para adicionar ao carrinho.")
                return
                
            # Obter os dados do produto selecionado
            item = self.produtos_tree.item(selecionado[0])
            valores = item['values']
            produto_id = valores[0]
        
        # Extrair os dados do produto
        nome = valores[1]
        preco_str = valores[2].replace('R$', '').replace(',', '.').strip()
        preco = float(preco_str)
        
        # Obter o tipo do produto do banco de dados
        tipo_produto = 'Outros'  # Valor padrão
        try:
            produto = self.cadastro_controller.obter_produto(produto_id)
            if produto and 'tipo' in produto:
                tipo_produto = produto['tipo']
        except Exception as e:
            print(f"Erro ao obter tipo do produto: {e}")
        
        # Verificar se o produto já está no carrinho
        item_existente = None
        for item in self.itens_pedido:
            if item['id'] == produto_id and item['opcoes'] == (opcoes_selecionadas or []):
                item_existente = item
                break
                
        if item_existente:
            # Se o produto já está no carrinho, apenas incrementa a quantidade
            item_existente['quantidade'] += 1
            item_existente['total'] = item_existente['quantidade'] * preco
        else:
            # Se não está no carrinho, adiciona como novo item
            novo_item = {
                'id': produto_id,
                'nome': nome,
                'preco': preco,
                'quantidade': 1,
                'total': preco,
                'tipo': tipo_produto,
                'opcoes': opcoes_selecionadas or []  # Lista para armazenar as opções do produto
            }
            self.itens_pedido.append(novo_item)
            
        # Atualizar a exibição do carrinho
        self._atualizar_carrinho()
        self._atualizar_total_pedido()
    

    def _remover_do_carrinho(self, event=None):
        """Remove o item selecionado do carrinho"""
        # Obter o item selecionado na tabela do carrinho
        selecionado = self.carrinho_tree.selection()
        
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para remover do carrinho.")
            return
            
        # Verificar se o item selecionado é um item principal ou uma opção
        parent = self.carrinho_tree.parent(selecionado[0])
        
        if parent:  # Se tem parent, é uma opção, então seleciona o item principal
            messagebox.showinfo("Informação", "Para remover um item com opções, selecione o produto principal, não a opção.")
            return
        
        # Obter o índice do item no carrinho
        indice = self.carrinho_tree.index(selecionado[0])
        
        if 0 <= indice < len(self.itens_pedido):
            # Remover o item do carrinho
            self.itens_pedido.pop(indice)
            
            # Atualizar a exibição do carrinho
            self._atualizar_carrinho()
    
    
    def _atualizar_carrinho(self):
        """Atualiza a exibição do carrinho de compras"""
        # Limpar a tabela do carrinho
        for item in self.carrinho_tree.get_children():
            self.carrinho_tree.delete(item)
            
        # Configurar tags para estilização
        self.carrinho_tree.tag_configure('com_opcoes', background='#f0f8ff')  # Azul claro para itens com opções
        self.carrinho_tree.tag_configure('sem_opcoes', background='#ffffff')  # Branco para itens sem opções
        self.carrinho_tree.tag_configure('opcao_item', background='#f9f9f9')   # Cinza claro para opções
            
        # Adicionar os itens do carrinho à tabela
        for item in self.itens_pedido:
            # Verificar se o item tem opções
            tem_opcoes = bool(item.get('opcoes'))
            
            # Adicionar o item principal
            item_id = self.carrinho_tree.insert(
                "", 
                tk.END, 
                values=(
                    f"{item['nome']} {'+' if tem_opcoes else ''}",
                    item['quantidade'],
                    f"R$ {item['preco']:.2f}".replace('.', ','),
                    f"R$ {item['total']:.2f}".replace('.', ',')
                ),
                tags=('com_opcoes' if tem_opcoes else 'sem_opcoes',)
            )
            
            # Se o item tiver opções, adicionar como itens filhos
            if tem_opcoes:
                for opcao in item['opcoes']:
                    self.carrinho_tree.insert(
                        item_id,
                        tk.END,
                        values=(
                            f"  → {opcao.get('nome', 'Opção')}",
                            "",
                            f"+R$ {opcao.get('preco_adicional', 0):.2f}".replace('.', ','),
                            ""
                        ),
                        tags=('opcao_item',)
                    )
        
        # Atualizar o total do pedido
        self._atualizar_total_pedido()
        
    def _atualizar_total_pedido(self):
        """Atualiza o valor total do pedido"""
        total = 0.0
        
        # Somar todos os itens do carrinho
        for item in self.itens_pedido:
            total += item['total']
        
        # Adicionar taxa de entrega, se houver
        try:
            taxa = float(self.taxa_entry.get().replace(",", "."))
            total += taxa
        except ValueError:
            pass
        
        # Atualizar o label de total
        self.total_label.config(text=f"R$ {total:.2f}".replace(".", ","))
        
        return total
    
    def _finalizar_pedido(self):
        # Verificar se há cliente selecionado
        if not self.cliente_atual:
            messagebox.showwarning("Aviso", "Selecione um cliente antes de finalizar o pedido.")
            return
        
        # Verificar se há itens no carrinho
        if not self.carrinho_tree.get_children():
            messagebox.showwarning("Aviso", "Não há itens no carrinho para finalizar o pedido.")
            return
        
        # Confirmar finalização
        if messagebox.askyesno("Confirmação", "Deseja finalizar o pedido de delivery?"):
            # Aqui seria feita a finalização do pedido no banco de dados
            messagebox.showinfo("Sucesso", "Pedido finalizado com sucesso!")
            
            # Limpar os dados
            self._limpar_carrinho()
            self.busca_cliente_entry.delete(0, tk.END)
            self.observacoes_entry.delete(0, tk.END)
            self.taxa_entry.delete(0, tk.END)
            self.taxa_entry.insert(0, "0.00")
            
            # Limpar dados do cliente
            self.cliente_atual = None
            self.nome_cliente_label.config(text="Nenhum cliente selecionado")
            self.telefone_cliente_label.config(text="-")
            self.endereco_cliente_label.config(text="-")

    def _limpar_carrinho(self):
        """Limpa todos os itens do carrinho"""
        for item in self.carrinho_tree.get_children():
            self.carrinho_tree.delete(item)
        self.itens_pedido = []
        self._atualizar_total_pedido()
