import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import sys
from pathlib import Path

# Importar configurações de estilo
from config.estilos import CORES, FONTES, aplicar_estilo

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.cadastro_controller import CadastroController
from controllers.cliente_controller import ClienteController
from controllers.delivery_controller import DeliveryController
from utils.impressao import GerenciadorImpressao

class DeliveryModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = parent
        
        # Inicializar os controladores
        self.cadastro_controller = CadastroController()
        self.cliente_controller = ClienteController()
        self.delivery_controller = DeliveryController()
        
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
        
        # Labels para exibir os dados do cliente
        self.nome_cliente_label = None
        self.telefone_cliente_label = None
        self.endereco_cliente_label = None
        self.regiao_entrega_label = None
        self.taxa_entrega_label = None
        
    def formatar_moeda(self, valor):
        """Formata um valor numérico para o padrão monetário brasileiro."""
        return f"R$ {valor:,.2f}".replace('.', ',')
    
    def show(self):
        # Limpar o frame atual
        # Limpar o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Criar o frame principal com estilo Card
        frame = ttk.Frame(self.frame, style="Card.TFrame")
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Ajustar o estilo dos botões
        style = ttk.Style()
        style.configure('TButton', 
                      font=('Arial', 14),
                      padding=10)
        
        # Configurar estilo para a Treeview usando a função global
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        
        # Configuração adicional para os cabeçalhos
        style.configure("Treeview.Heading", 
                      font=("Arial", 10, "bold"), 
                      background=self.cores["primaria"],
                      foreground=self.cores["texto"])
        
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
        
        # Removido a exibição da data
        
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
        
        # Cabeçalho Nome e Telefone
        ttk.Label(
            info_cliente_frame,
            text="Nome: ",
            font=('Arial', 9, 'bold')
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.nome_cliente_label = ttk.Label(
            info_cliente_frame, 
            text="-",
            font=('Arial', 9),
            width=40
        )
        self.nome_cliente_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(
            info_cliente_frame,
            text="Telefone: ",
            font=('Arial', 9, 'bold')
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        self.telefone_cliente_label = ttk.Label(
            info_cliente_frame, 
            text="-",
            font=('Arial', 9),
            width=20
        )
        self.telefone_cliente_label.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Linha do Endereço
        ttk.Label(
            info_cliente_frame, 
            text="Endereço: ",
            font=('Arial', 9, 'bold')
        ).grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        
        self.endereco_cliente_label = ttk.Label(
            info_cliente_frame, 
            text="-",
            font=('Arial', 9),
            wraplength=400,
            justify='left'
        )
        self.endereco_cliente_label.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Taxa de entrega (invisível, apenas para cálculo)
        self.taxa_entrega_label = ttk.Label(
            info_cliente_frame,
            text="R$ 0,00",
            font=('Arial', 1)  # Fonte mínima para ficar invisível
        )
        self.taxa_entrega_label.grid_remove()  # Remove da grade de layout
        
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
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        
        # Configurações adicionais específicas para esta tabela
        style.configure("Produtos.Treeview",
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
        
        # Frame direito - Conteúdo principal
        right_frame = ttk.Frame(container)
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Frame para as informações de entrega
        entrega_frame = ttk.Frame(right_frame)
        entrega_frame.pack(fill="x", pady=(0, 5))
        
        # Cabeçalho das informações de entrega
        entrega_header = ttk.Frame(entrega_frame)
        entrega_header.pack(fill="x")
        
        ttk.Label(
            entrega_header, 
            text="Informações de Entrega", 
            font=('Arial', 12, 'bold')
        ).pack(side="left", anchor="w")
        
        # Conteúdo das informações de entrega
        entrega_content = ttk.Frame(entrega_frame)
        entrega_content.pack(fill="x", pady=5)
        
        # Botão para gerenciar regiões de entrega
        btn_gerenciar_entregas = tk.Button(
            entrega_content,
            text="Gerenciar Regiões de Entrega",
            bg=self.cores["secundaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self._gerenciar_regioes_entrega
        )
        btn_gerenciar_entregas.pack(side="left", padx=5, pady=5)
        
        # Informações da entrega
        info_frame = ttk.Frame(entrega_content)
        info_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        # Região de entrega
        ttk.Label(info_frame, text="Região:").grid(row=0, column=0, sticky="w", padx=2)
        self.regiao_entrega_label = ttk.Label(info_frame, text="Selecione um cliente", font=('Arial', 9, 'bold'))
        self.regiao_entrega_label.grid(row=0, column=1, sticky="w", padx=2)
        
        # Taxa de entrega
        ttk.Label(info_frame, text="Taxa:").grid(row=0, column=2, sticky="e", padx=2)
        self.taxa_entrega_label = ttk.Label(info_frame, text="R$ 0,00", font=('Arial', 9, 'bold'))
        self.taxa_entrega_label.grid(row=0, column=3, sticky="w", padx=2)
        
        # Frame do carrinho de compras
        carrinho_frame = ttk.Frame(right_frame)
        carrinho_frame.pack(fill="both", expand=True, pady=(10, 0))
        carrinho_frame.columnconfigure(0, weight=1)
        carrinho_frame.rowconfigure(1, weight=1)
        
        # Cabeçalho do carrinho
        carrinho_header = ttk.Frame(carrinho_frame)
        carrinho_header.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            carrinho_header, 
            text="Carrinho de Compras", 
            font=('Arial', 12, 'bold')
        ).pack(side="left", anchor="w")
        
        # Organizar o carrinho em um frame principal
        carrinho_conteudo = ttk.Frame(carrinho_frame)
        carrinho_conteudo.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para a tabela do carrinho
        tabela_carrinho_frame = ttk.Frame(carrinho_conteudo)
        tabela_carrinho_frame.pack(fill="both", expand=True)
        
        # Tabela do carrinho com altura ajustada
        colunas_carrinho = ("Produto", "Qtd", "Unit.", "Total")
        
        # Configurar estilo para a tabela do carrinho
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        
        # Configurações adicionais específicas para esta tabela
        style.configure("Carrinho.Treeview",
            borderwidth=0,
            highlightthickness=0
        )
        
        self.carrinho_tree = ttk.Treeview(
            tabela_carrinho_frame, 
            columns=colunas_carrinho, 
            show="headings", 
            height=15,
            style="Carrinho.Treeview"
        )
        
        # Configurar cabeçalhos com larguras proporcionais
        larguras_carrinho = {"Produto": 200, "Qtd": 50, "Unit.": 80, "Total": 80}
        for col in colunas_carrinho:
            self.carrinho_tree.heading(col, text=col)
            self.carrinho_tree.column(col, width=larguras_carrinho.get(col, 100), anchor="center")
        
        # Adicionar barra de rolagem
        scrollbar_carrinho = ttk.Scrollbar(tabela_carrinho_frame, orient="vertical", command=self.carrinho_tree.yview)
        self.carrinho_tree.configure(yscrollcommand=scrollbar_carrinho.set)
        
        self.carrinho_tree.pack(side="left", fill="both", expand=True)
        scrollbar_carrinho.pack(side="right", fill="y")
        
        # Botões de ação para o carrinho em um grid para melhor distribuição
        botoes_carrinho = ttk.Frame(carrinho_conteudo)
        botoes_carrinho.pack(fill="x", pady=5)
        botoes_carrinho.columnconfigure(0, weight=1)
        botoes_carrinho.columnconfigure(1, weight=1)
        
        remover_button = tk.Button(
            botoes_carrinho, 
            text="Remover Item", 
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self._remover_do_carrinho
        )
        remover_button.grid(row=0, column=0, sticky="ew", padx=2)
        
        limpar_button = tk.Button(
            botoes_carrinho, 
            text="Limpar Carrinho", 
            bg=self.cores["terciaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self._limpar_carrinho
        )
        limpar_button.grid(row=0, column=1, sticky="ew", padx=2)
        
        # Resumo da compra em um frame com estilo destacado
        resumo_frame = ttk.LabelFrame(carrinho_conteudo, text="Resumo do Pedido")
        resumo_frame.pack(fill="x", pady=5)
        
        # Grid para organizar os campos do resumo
        resumo_grid = ttk.Frame(resumo_frame)
        resumo_grid.pack(fill="x", padx=10, pady=5)
        resumo_grid.columnconfigure(0, weight=1)  # Coluna dos rótulos
        resumo_grid.columnconfigure(1, weight=1)  # Coluna dos valores
        
        # Subtotal
        ttk.Label(resumo_grid, text="Subtotal:", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.subtotal_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=('Arial', 10))
        self.subtotal_valor.grid(row=0, column=1, sticky="e", pady=2)
        
        # Taxa de entrega
        ttk.Label(resumo_grid, text="Taxa de Entrega:", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=2)
        self.taxa_entrega_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=('Arial', 10))
        self.taxa_entrega_valor.grid(row=1, column=1, sticky="e", pady=2)
        
        # Separador antes do total
        ttk.Separator(resumo_grid, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Total com destaque
        ttk.Label(resumo_grid, text="TOTAL:", font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky="w", pady=2)
        self.total_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=('Arial', 12, 'bold'))
        self.total_valor.grid(row=3, column=1, sticky="e", pady=2)
        
        # Botão de finalizar pedido com estilo 'sucesso'
        from config.estilos import aplicar_estilo
        finalizar_button = tk.Button(
            carrinho_conteudo, 
            text="FINALIZAR PEDIDO",
            command=self._finalizar_pedido
        )
        aplicar_estilo(finalizar_button, "sucesso")
        finalizar_button.pack(fill="x", pady=5)
        
        # Vincular duplo clique para abrir opções do produto
        self.carrinho_tree.bind("<Double-1>", self._abrir_opcoes_item_carrinho)
        
        # Barra inferior vazia para manter o layout
        ttk.Frame(container, height=10).grid(row=2, column=0, columnspan=2, sticky="ew")
        
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
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        
        # Configurações adicionais específicas para esta tabela
        style.configure("Clientes.Treeview",
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
                cliente.get("telefone", ""),
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
                        frame_opcao = ttk.Frame(grupo_frame)
                        frame_opcao.pack(fill="x", pady=2)
                        
                        rb = ttk.Radiobutton(
                            frame_opcao,
                            text=f"{opcao['nome']}:",
                            variable=var,
                            value=str(opcao['id'])
                        )
                        rb.pack(side="left", anchor="w")
                        
                        # Se for opção de texto livre, adicionar campo de texto
                        if opcao.get('tipo') == 'texto_livre':
                            texto_entry = ttk.Entry(frame_opcao)
                            texto_entry.pack(side="right", fill="x", expand=True, padx=5)
                            opcao['texto_entry'] = texto_entry  # Armazenar referência ao campo de texto
                else:
                    # Seleção múltipla (Checkbuttons)
                    self.selecoes_opcoes[grupo_id] = {'var': [], 'tipo': 'multiplo'}
                    
                    for opcao in grupo_info['itens']:
                        frame_opcao = ttk.Frame(grupo_frame)
                        frame_opcao.pack(fill="x", pady=2)
                        
                        var = tk.BooleanVar()
                        self.selecoes_opcoes[grupo_id]['var'].append((var, opcao))
                        
                        cb = ttk.Checkbutton(
                            frame_opcao,
                            text=f"{opcao['nome']}:",
                            variable=var
                        )
                        cb.pack(side="left", anchor="w")
                        
                        # Se for opção de texto livre, adicionar campo de texto
                        if opcao.get('tipo') == 'texto_livre':
                            texto_entry = ttk.Entry(frame_opcao)
                            texto_entry.pack(side="right", fill="x", expand=True, padx=5)
                            opcao['texto_entry'] = texto_entry  # Armazenar referência ao campo de texto
            
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
                    opcao_id = int(selecao['var'].get())
                    
                    # Buscar informações da opção para verificar se é do tipo texto_livre
                    from controllers.opcoes_controller import OpcoesController
                    db_connection = getattr(self.controller, 'db_connection', None)
                    if db_connection:
                        opcoes_controller = OpcoesController(db_connection=db_connection)
                        opcao = opcoes_controller.obter_item_opcao(opcao_id)
                        
                        if opcao and opcao.get('tipo') == 'texto_livre' and 'texto_entry' in opcao:
                            # Se for opção de texto livre, obter o texto digitado
                            texto_livre = opcao['texto_entry'].get()
                            if texto_livre:
                                opcoes_selecionadas.append({
                                    'grupo_id': grupo_id,
                                    'opcao_id': opcao_id,
                                    'nome': f"{opcao.get('nome', '')}: {texto_livre}",
                                    'preco_adicional': opcao.get('preco_adicional', 0.0),
                                    'texto_livre': texto_livre
                                })
                        else:
                            # Opção normal
                            opcoes_selecionadas.append({
                                'grupo_id': grupo_id,
                                'opcao_id': opcao_id,
                                'nome': opcao.get('nome', '') if opcao else f"Opção {opcao_id}",
                                'preco_adicional': opcao.get('preco_adicional', 0.0) if opcao else 0.0
                            })
                elif selecao['tipo'] == 'multiplo':
                    # Múltiplas opções podem ser selecionadas
                    for var, opcao in selecao['var']:
                        if var.get():
                            if opcao.get('tipo') == 'texto_livre' and 'texto_entry' in opcao:
                                # Se for opção de texto livre, obter o texto digitado
                                texto_livre = opcao['texto_entry'].get()
                                if texto_livre:
                                    opcoes_selecionadas.append({
                                        'grupo_id': grupo_id,
                                        'opcao_id': opcao['id'],
                                        'nome': f"{opcao.get('nome', '')}: {texto_livre}",
                                        'preco_adicional': opcao.get('preco_adicional', 0.0),
                                        'texto_livre': texto_livre
                                    })
                            else:
                                # Opção normal
                                opcoes_selecionadas.append({
                                    'grupo_id': grupo_id,
                                    'opcao_id': opcao['id'],
                                    'nome': opcao.get('nome', ''),
                                    'preco_adicional': opcao.get('preco_adicional', 0.0)
                                })
            
            # Fechar a janela de opções
            if hasattr(self, 'janela_opcoes') and self.janela_opcoes.winfo_exists():
                self.janela_opcoes.destroy()
            
            # Adicionar ao carrinho
            self._adicionar_ao_carrinho(produto_id, valores_produto, opcoes_selecionadas)
            
        except Exception as e:
            import traceback
            print(f"Erro ao adicionar opções: {str(e)}\n{traceback.format_exc()}")
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
    

    def _abrir_opcoes_item_carrinho(self, event=None):
        """Abre as opções do item do carrinho quando o usuário dá um duplo clique"""
        selecionado = self.carrinho_tree.selection()
        if not selecionado:
            return
            
        # Obter o ID do item selecionado
        item_id = selecionado[0]
        
        # Verificar se é um item principal ou uma opção
        item = self.carrinho_tree.item(item_id)
        
        # Se for uma opção, obter o item pai
        if self.carrinho_tree.parent(item_id):
            item_id = self.carrinho_tree.parent(item_id)
            item = self.carrinho_tree.item(item_id)
        
        # Obter os dados do item no carrinho
        for item_pedido in self.itens_pedido:
            if item_pedido.get('id_item') == item_id:
                # Encontrar o produto no banco de dados
                produto = self.cadastro_controller.obter_produto_por_id(item_pedido['produto_id'])
                if produto:
                    # Remover o item do carrinho temporariamente
                    self.itens_pedido.remove(item_pedido)
                    
                    # Abrir as opções do produto
                    self._mostrar_opcoes_produto(produto_id=produto['id'])
                return

    def _remover_do_carrinho(self, event=None):
        """Remove o item selecionado do carrinho"""
        selecionado = self.carrinho_tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
            
        # Obter o ID do item selecionado
        item_id = selecionado[0]
        
        # Verificar se é um item principal ou uma opção
        item = self.carrinho_tree.item(item_id)
        
        # Se for uma opção (filho), obter o item pai
        if self.carrinho_tree.parent(item_id):
            item_pai_id = self.carrinho_tree.parent(item_id)
            item_pai = self.carrinho_tree.item(item_pai_id)
            
            # Encontrar o item principal no carrinho
            for i, item_pedido in enumerate(self.itens_pedido):
                if item_pedido['nome'] == item_pai['values'][0].replace(' +', ''):
                    # Encontrar a opção correspondente
                    opcao_nome = item['values'][0].strip().replace('→', '').strip()
                    for j, opcao in enumerate(item_pedido.get('opcoes', [])):
                        if opcao.get('nome') == opcao_nome:
                            # Remover a opção
                            item_pedido['opcoes'].pop(j)
                            
                            # Atualizar o preço total do item
                            item_pedido['total'] -= opcao.get('preco_adicional', 0)
                            
                            # Se não houver mais opções, remover o sinal de +
                            if not item_pedido.get('opcoes'):
                                item_pedido['nome'] = item_pedido['nome'].replace(' +', '')
                            
                            # Atualizar a exibição
                            self._atualizar_carrinho()
                            return
        else:
            # Remover o item principal do carrinho
            item_nome = item['values'][0].replace(' +', '')
            for i, item_pedido in enumerate(self.itens_pedido):
                if item_pedido['nome'] == item_nome:
                    self.itens_pedido.pop(i)
                    self._atualizar_carrinho()
                    return
                    
            # Se não encontrou pelo nome, tentar pelo ID do item na árvore
            # Isso é necessário para itens que foram adicionados com o mesmo nome
            if len(self.itens_pedido) > 0:
                # Remover o último item se não encontrar correspondência
                # (isso é uma solução de fallback)
                self.itens_pedido.pop(-1)
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
                    f"R$ {item['total']:.2f}".replace('.=','.00').replace('.', ',')
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
        
        # Calcular o subtotal (soma de todos os itens)
        self.subtotal = sum(item['total'] for item in self.itens_pedido)
        
        # Atualizar os valores no resumo da compra
        if hasattr(self, 'subtotal_valor'):
            self.subtotal_valor.config(text=f"R$ {self.subtotal:.2f}".replace('.', ','))
            
        # Recalcular o total com taxa de entrega
        self._atualizar_total_pedido()
        
    def _atualizar_total_pedido(self):
        """Atualiza o valor total do pedido"""
        # Obter o subtotal (já calculado em _atualizar_carrinho)
        subtotal = getattr(self, 'subtotal', 0)
        
        # Obter a taxa de entrega
        try:
            # Extrair o valor da taxa do label (formato: "R$ X,XX")
            taxa_texto = self.taxa_entrega_label.cget("text").replace("R$", "").strip()
            taxa = float(taxa_texto.replace(".", "").replace(",", "."))
        except (ValueError, AttributeError):
            taxa = 0.0
        
        # Calcular o total
        total = subtotal + taxa
        
        # Atualizar os valores na interface
        if hasattr(self, 'taxa_entrega_valor'):
            self.taxa_entrega_valor.config(text=f"R$ {taxa:.2f}".replace(".", ","))
            
        if hasattr(self, 'total_valor'):
            self.total_valor.config(text=f"R$ {total:.2f}".replace(".", ","))
        
        return total
    
    def _finalizar_pedido(self):
        # Verificar se há itens no carrinho
        if not self.carrinho_tree.get_children():
            messagebox.showwarning("Aviso", "Não há itens no carrinho para finalizar o pedido.")
            return
        
        # Verificar se há um cliente selecionado
        if not self.cliente_atual or 'id' not in self.cliente_atual:
            messagebox.showwarning("Aviso", "Selecione um cliente antes de finalizar o pedido.")
            return
        
        # Calcular o valor total do pedido
        subtotal = 0.0
        itens_pedido = []
        
        for item in self.carrinho_tree.get_children():
            valores = self.carrinho_tree.item(item, 'values')
            # Verificar se o item tem valores e se o índice 3 (total) existe
            if valores and len(valores) > 3:
                try:
                    # O valor total está no índice 3 (quarto elemento)
                    valor_item = float(valores[3].replace('R$', '').replace('.', '').replace(',', '.'))
                    subtotal += valor_item
                    
                    # Adicionar item à lista de itens do pedido
                    itens_pedido.append({
                        'produto_id': valores[0],  # ID do produto
                        'descricao': valores[1],    # Nome do produto
                        'quantidade': 1,           # Quantidade (ajustar conforme necessário)
                        'preco_unitario': valor_item,
                        'total': valor_item
                    })
                except (ValueError, IndexError) as e:
                    print(f"Erro ao processar item do carrinho: {e}")
        
        # Adicionar taxa de entrega ao valor total
        taxa_entrega = 0.0
        if hasattr(self, 'taxa_entrega_label'):
            try:
                taxa_texto = self.taxa_entrega_label.cget("text").replace("R$", "").strip()
                taxa_entrega = float(taxa_texto.replace(".", "").replace(",", "."))
                
                # Adicionar taxa de entrega como um item do pedido
                itens_pedido.append({
                    'produto_id': 'TAXA_ENTREGA',
                    'descricao': 'Taxa de Entrega',
                    'quantidade': 1,
                    'preco_unitario': taxa_entrega,
                    'total': taxa_entrega
                })
            except (ValueError, AttributeError) as e:
                print(f"Erro ao processar taxa de entrega: {e}")
                taxa_entrega = 0.0
        
        valor_total = subtotal + taxa_entrega
        
        # Criar janela de pagamento
        pagamento_window = tk.Toplevel(self.frame)
        pagamento_window.title("Forma de Pagamento")
        pagamento_window.geometry("400x650")
        pagamento_window.transient(self.frame)
        pagamento_window.resizable(False, False)
        
        # Centralizar na tela
        pagamento_window.update_idletasks()
        width = 400
        height = 650
        x = (pagamento_window.winfo_screenwidth() // 2) - (width // 2)
        y = (pagamento_window.winfo_screenheight() // 2) - (height // 2)
        pagamento_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal com scroll
        main_frame = ttk.Frame(pagamento_window)
        main_frame.pack(fill='both', expand=True)
        
        # Canvas para rolagem
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Adicionar padding ao frame rolável
        content_frame = ttk.Frame(scrollable_frame, padding=20)
        content_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            content_frame, 
            text="Pagamento",
            font=('Arial', 16, 'bold'),
            foreground='black'
        ).pack(pady=(0, 20))
        
        # Variável para armazenar a forma de pagamento selecionada
        forma_pagamento = tk.StringVar()
        
        # Função utilitária para formatar valores monetários
        self.util = {
            'formatar_moeda': lambda valor: f"R$ {float(valor):.2f}".replace('.', ',') if valor else "R$ 0,00"
        }
        
        def calcular_troco(*args):
            if forma_pagamento.get() != 'dinheiro' or not valor_dinheiro.get() or not valor_dinheiro.get().strip():
                troco_label.config(text=self.util['formatar_moeda'](0), foreground='#2e7d32')
                return
                
            try:
                # Remove pontos de milhar e substitui vírgula por ponto
                valor_digitado = valor_dinheiro.get().replace('.', '').replace(',', '.')
                valor_pago = float(valor_digitado)
                
                if valor_pago < 0:
                    raise ValueError("Valor não pode ser negativo")
                    
                if valor_pago >= valor_total:
                    troco = valor_pago - valor_total
                    troco_label.config(
                        text=self.util['formatar_moeda'](troco),
                        foreground='#2e7d32'  # Verde escuro
                    )
                else:
                    valor_restante = valor_total - valor_pago
                    troco_label.config(
                        text=f"Faltam {self.util['formatar_moeda'](valor_restante)}",
                        foreground='#d32f2f'  # Vermelho
                    )
                
                # Mostrar os campos de dinheiro e troco
                valor_dinheiro_frame.pack(fill='x', pady=10)
                troco_frame.pack(fill='x', pady=5)
                
            except (ValueError, AttributeError) as e:
                troco_label.config(
                    text="Valor inválido!",
                    foreground='#d32f2f'  # Vermelho
                )
                valor_dinheiro_frame.pack(fill='x', pady=10)
                troco_frame.pack(fill='x', pady=5)
    
        def atualizar_visibilidade_campo_dinheiro(*args):
            """Atualiza a visibilidade do campo de valor em dinheiro com base na forma de pagamento"""
            if forma_pagamento.get() == 'dinheiro':
                valor_dinheiro_frame.pack(fill='x', pady=10)
                troco_frame.pack(fill='x', pady=5)
                valor_entry.focus_set()
                calcular_troco()
            else:
                valor_dinheiro_frame.pack_forget()
                troco_frame.pack_forget()
                troco_label.config(text=self.util['formatar_moeda'](0), foreground='#2e7d32')
        
        # Frame para o resumo da venda
        resumo_frame = ttk.LabelFrame(content_frame, text="Resumo da Venda", padding=(10, 5))
        resumo_frame.pack(fill='x', pady=(0, 15))
        total_frame = ttk.Frame(resumo_frame)
        total_frame.pack(fill='x', pady=2)
        ttk.Label(total_frame, text="TOTAL:", font=('Arial', 10, 'bold'), foreground=CORES['primaria']).pack(side=tk.LEFT)
        total_label = ttk.Label(total_frame, text=self.util['formatar_moeda'](valor_total), font=('Arial', 10, 'bold'), foreground=CORES['primaria'])
        total_label.pack(side=tk.RIGHT)
        
        # Restante
        restante_frame = ttk.Frame(resumo_frame)
        restante_frame.pack(fill='x', pady=2)
        ttk.Label(restante_frame, text="Restante:", font=('Arial', 10)).pack(side=tk.LEFT)
        ttk.Label(restante_frame, text=self.util['formatar_moeda'](valor_total), font=('Arial', 10)).pack(side=tk.RIGHT)
        
        # Frame para os botões de pagamento
        pagamento_frame = ttk.LabelFrame(content_frame, text="Formas de Pagamento", padding=(10, 5))
        pagamento_frame.pack(fill='x', pady=(0, 15))
            
        # Frame para os botões de pagamento - usando grid para melhor organização
        btn_frame = ttk.Frame(pagamento_frame, padding=5)
        btn_frame.pack(fill='both', expand=True)
        
        # Lista de formas de pagamento disponíveis
        formas_pagamento = [
            ("💳", "Cartão de Crédito", "credito", CORES['primaria']),
            ("💳", "Cartão de Débito", "debito", CORES['primaria']),
            ("💵", "Dinheiro", "dinheiro", CORES['primaria']),
            ("📱", "PIX", "pix", CORES['primaria'])
        ]
        
        # Criar botões para cada forma de pagamento em uma grade 2x2
        for i, (icone, texto, forma, cor) in enumerate(formas_pagamento):
            # Calcular posição na grade
            row = i // 2  # 2 colunas
            col = i % 2   # 2 colunas
            
            # Frame para cada botão
            btn_container = ttk.Frame(btn_frame, padding=2)
            btn_container.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Configurar peso das colunas para expansão uniforme
            btn_frame.columnconfigure(col, weight=1, uniform='btn')
            btn_frame.rowconfigure(row, weight=1)
            
            # Criar botão com estilo mais destacado
            btn = tk.Radiobutton(
                btn_container,
                text=texto,  # Remover ícone
                font=('Arial', 11, 'bold'),
                bg=cor,
                fg='white',
                selectcolor=cor,
                activebackground=self._darken_color(cor, 0.3),  # Cor mais escura para o estado ativo
                activeforeground='white',
                indicatoron=0,
                relief='flat',  # Botão plano como na imagem 1
                bd=0,
                highlightthickness=0,  # Remove a borda de foco
                padx=10,
                pady=10,
                wraplength=120,  # Aumentar espaço para texto
                justify='center',
                variable=forma_pagamento,
                value=forma,
                command=atualizar_visibilidade_campo_dinheiro
            )
            btn.pack(fill='both', expand=True, ipady=10, padx=3, pady=3)
            
            # Configurar estilo para o estado selecionado
            btn['selectcolor'] = self._darken_color(cor, 0.3)  # Cor mais clara quando selecionado
            
            # Efeito hover para os botões de pagamento
            btn.bind('<Enter>', lambda e, b=btn, c=cor: b.config(bg=self._darken_color(c, 0.1)) if forma_pagamento.get() != forma else None)
            btn.bind('<Leave>', lambda e, b=btn, c=cor: b.config(bg=c) if forma_pagamento.get() != forma else None)
            
            # Atualizar a cor quando o botão for selecionado
            def on_select(forma_btn=forma, btn_ref=btn, c=cor):
                if forma_pagamento.get() == forma_btn:
                    btn_ref.config(bg=self._darken_color(c, 0.3))  # Cor mais clara para o selecionado
                else:
                    btn_ref.config(bg=c)
            
            # Configurar o trace para atualizar a cor quando a seleção mudar
            forma_pagamento.trace_add('write', lambda *args, f=forma, b=btn, c=cor: on_select(f, b, c))
            
            # Selecionar o primeiro botão por padrão
            if i == 0:
                forma_pagamento.set(forma)
        
        # Frame para o campo de valor em dinheiro (oculto inicialmente)
        valor_dinheiro_frame = ttk.Frame(content_frame, padding=(5, 15))
        
        # Frame para a entrada de valor
        entrada_frame = ttk.Frame(valor_dinheiro_frame)
        entrada_frame.pack(fill='x')
        
        # Variável para o valor em dinheiro
        valor_dinheiro = tk.StringVar()
        

        
        # Entrada para o valor em dinheiro
        valor_entry = ttk.Entry(
            entrada_frame,
            textvariable=valor_dinheiro,
            font=('Arial', 10),
            width=15,
            justify='right'
        )
        valor_entry.pack(side=tk.LEFT)
        
        # Frame para o troco
        troco_frame = ttk.Frame(valor_dinheiro_frame)
        
        # Label para o troco
        ttk.Label(
            troco_frame,
            text="Troco:",
            font=('Arial', 11, 'bold'),
            foreground='#333333'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Label para exibir o valor do troco
        troco_label = ttk.Label(
            troco_frame,
            text="R$ 0,00",
            font=('Arial', 12, 'bold'),
            foreground='#2e7d32'  # Verde escuro
        )
        troco_label.pack(side=tk.LEFT)
        
        # Função para formatar o valor em moeda
        def formatar_valor_moeda(*args):
            """Formata o valor digitado como moeda brasileira"""
            # Remove tudo que não for dígito ou vírgula
            valor = ''.join(filter(lambda x: x.isdigit() or x == ',', valor_dinheiro.get()))
            
            # Se houver mais de uma vírgula, mantém apenas a primeira
            if valor.count(',') > 1:
                valor = valor.replace(',', '', valor.count(',') - 1)
            
            # Se houver vírgula, limita a 2 casas decimais
            if ',' in valor:
                partes = valor.split(',')
                if len(partes) > 1 and len(partes[1]) > 2:
                    valor = f"{partes[0]},{partes[1][:2]}"
            
            # Atualiza o valor formatado
            valor_dinheiro.set(valor)
            
            # Chama a função para calcular o troco
            calcular_troco()
        
        # Atualizar a visibilidade do campo de dinheiro com base na forma de pagamento selecionada
        forma_pagamento.trace('w', atualizar_visibilidade_campo_dinheiro)
        
        # Vincular a função de formatação ao evento de tecla solta
        valor_dinheiro.trace('w', formatar_valor_moeda)
        
        # Vincular a função de cálculo de troco ao evento de tecla solta
        valor_dinheiro.trace('w', calcular_troco)
        
        # Frame para os botões de confirmação
        botoes_frame = ttk.Frame(content_frame, padding=(0, 20, 0, 0))
        botoes_frame.pack(fill='x', pady=(10, 0))
        
        # Configurar peso das colunas
        botoes_frame.columnconfigure(0, weight=1)
        botoes_frame.columnconfigure(1, weight=1)
        
        # Botão de cancelar
        btn_cancelar = tk.Button(
            botoes_frame,
            text="❌ Cancelar",
            command=pagamento_window.destroy,
            bg='#f44336',  # Vermelho
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            bd=0,
            padx=5,
            pady=10
        )
        btn_cancelar.grid(row=0, column=0, padx=5, sticky='nsew')
        
        # Botão de confirmar
        btn_confirmar = tk.Button(
            botoes_frame,
            text="✅ Confirmar Pedido",
            command=lambda: self._processar_pagamento(
                forma_pagamento.get(),
                valor_dinheiro.get() if forma_pagamento.get() == 'dinheiro' else None,
                valor_total,
                pagamento_window
            ),
            bg='#4caf50',  # Verde
            fg='white',
            font=('Arial', 12, 'bold'),
            relief='flat',
            bd=0,
            padx=5,
            pady=10
        )
        btn_confirmar.grid(row=0, column=1, padx=5, sticky='nsew')
        
        # Efeito hover para os botões
        btn_confirmar.bind('<Enter>', lambda e, b=btn_confirmar: b.config(bg=self._darken_color('#4caf50')))
        btn_confirmar.bind('<Leave>', lambda e, b=btn_confirmar: b.config(bg='#4caf50'))
        
        # Configurar trace para o campo de valor em dinheiro
        valor_dinheiro.trace_add('write', lambda *args: formatar_valor_moeda())
        
        # Configurar atalhos de teclado
        pagamento_window.bind('<Return>', lambda e: btn_confirmar.invoke())
        pagamento_window.bind('<Escape>', lambda e: pagamento_window.destroy())
        
        # Focar na janela
        pagamento_window.focus_force()
        
        # Definir foco no campo de valor em dinheiro se a forma de pagamento for dinheiro
        def on_show():
            if forma_pagamento.get() == 'dinheiro':
                valor_entry.focus_set()
        
        pagamento_window.after(100, on_show)
        
        # Efeito hover para o botão de confirmar
        btn_confirmar.bind('<Enter>', lambda e, b=btn_confirmar: b.config(bg=self._darken_color(CORES['destaque'])))
        btn_confirmar.bind('<Leave>', lambda e, b=btn_confirmar: b.config(bg=CORES['destaque']))
        
    def _atualizar_dados_cliente(self, dados_atualizados=None):
        """
        Atualiza os dados do cliente na interface.
        
        Args:
            dados_atualizados (dict, optional): Dados atualizados do cliente. Se None, usa self.cliente_atual.
        """
        if dados_atualizados is not None:
            self.cliente_atual = dados_atualizados
            
        if not hasattr(self, 'cliente_atual') or not self.cliente_atual:
            # Se não houver cliente selecionado, limpa os campos
            if hasattr(self, 'nome_cliente_label') and self.nome_cliente_label:
                self.nome_cliente_label.config(text="-")
            if hasattr(self, 'telefone_cliente_label') and self.telefone_cliente_label:
                self.telefone_cliente_label.config(text="-")
            if hasattr(self, 'endereco_cliente_label') and self.endereco_cliente_label:
                self.endereco_cliente_label.config(text="-")
            if hasattr(self, 'regiao_entrega_label') and self.regiao_entrega_label:
                self.regiao_entrega_label.config(text="Selecione um cliente")
            if hasattr(self, 'taxa_entrega_label') and self.taxa_entrega_label:
                self.taxa_entrega_label.config(text="R$ 0,00")
            return
            
        # Atualizar os labels com os dados do cliente
        if hasattr(self, 'nome_cliente_label') and self.nome_cliente_label:
            self.nome_cliente_label.config(text=self.cliente_atual.get('nome', '-'))
            
        if hasattr(self, 'telefone_cliente_label') and self.telefone_cliente_label:
            self.telefone_cliente_label.config(text=self.cliente_atual.get('telefone', '-'))
            
        if hasattr(self, 'endereco_cliente_label') and self.endereco_cliente_label:
            endereco = []
            if 'endereco' in self.cliente_atual and self.cliente_atual['endereco']:
                endereco.append(self.cliente_atual['endereco'])
            if 'numero' in self.cliente_atual and self.cliente_atual['numero']:
                endereco.append(str(self.cliente_atual['numero']))
            if 'bairro' in self.cliente_atual and self.cliente_atual['bairro']:
                endereco.append(self.cliente_atual['bairro'])
                
            endereco_str = ", ".join(endereco) if endereco else "-"
            self.endereco_cliente_label.config(text=endereco_str)
            
            # Se o cliente tiver bairro, tentar obter a região de entrega
            if 'bairro' in self.cliente_atual and self.cliente_atual['bairro']:
                try:
                    regiao = self.delivery_controller.obter_regiao_por_bairro(self.cliente_atual['bairro'])
                    if regiao and 'id' in regiao:
                        if hasattr(self, 'regiao_entrega_label') and self.regiao_entrega_label:
                            self.regiao_entrega_label.config(text=regiao.get('nome', 'Região não especificada'))
                        if hasattr(self, 'taxa_entrega_label') and self.taxa_entrega_label:
                            taxa = float(regiao.get('taxa_entrega', 0))
                            self.taxa_entrega_label.config(text=f"R$ {taxa:.2f}".replace(".", ","))
                    else:
                        if hasattr(self, 'regiao_entrega_label') and self.regiao_entrega_label:
                            self.regiao_entrega_label.config(text="Região não encontrada")
                        if hasattr(self, 'taxa_entrega_label') and self.taxa_entrega_label:
                            self.taxa_entrega_label.config(text="R$ 0,00")
                except Exception as e:
                    print(f"Erro ao obter região de entrega: {e}")
                    if hasattr(self, 'regiao_entrega_label') and self.regiao_entrega_label:
                        self.regiao_entrega_label.config(text="Erro ao buscar região")
                    if hasattr(self, 'taxa_entrega_label') and self.taxa_entrega_label:
                        self.taxa_entrega_label.config(text="R$ 0,00")
            else:
                if hasattr(self, 'regiao_entrega_label') and self.regiao_entrega_label:
                    self.regiao_entrega_label.config(text="Bairro não informado")
                if hasattr(self, 'taxa_entrega_label') and self.taxa_entrega_label:
                    self.taxa_entrega_label.config(text="R$ 0,00")
        
        # Atualizar o total do pedido para incluir a taxa de entrega, se aplicável
        if hasattr(self, '_atualizar_total_pedido'):
            self._atualizar_total_pedido()
    
    def _darken_color(self, color, factor=0.2):
        """Escurece uma cor em um fator especificado"""
        try:
            # Verifica se a cor está no formato #RRGGBB
            if color.startswith('#'):
                color = color[1:]
            
            # Converte a cor para RGB
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            # Escurece a cor
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            # Formata de volta para o formato hexadecimal
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            # Em caso de erro, retorna a cor original
            return color
            
    def _processar_pagamento(self, forma_pagamento, valor_recebido, valor_total, janela):
        """
        Processa o pagamento do pedido
        
        Args:
            forma_pagamento (str): Forma de pagamento selecionada
            valor_recebido (str): Valor recebido em dinheiro (apenas para pagamento em dinheiro)
            valor_total (float): Valor total do pedido
            janela: Referência para a janela de pagamento
        """
        try:
            # Verificar se a conexão com o banco de dados está disponível
            if not hasattr(self, 'delivery_controller') or not self.delivery_controller:
                messagebox.showerror("Erro", "Conexão com o banco de dados não disponível.")
                return
            
            # Verificar se há itens no carrinho
            if not hasattr(self, 'carrinho_tree') or not self.carrinho_tree.get_children():
                messagebox.showwarning("Aviso", "Não há itens no carrinho para finalizar o pedido.")
                return
                
            # Verificar se há um cliente selecionado
            if not self.cliente_atual or 'id' not in self.cliente_atual:
                messagebox.showwarning("Aviso", "Selecione um cliente antes de finalizar o pedido.")
                return
                
            # Verificar se a forma de pagamento foi selecionada
            if not forma_pagamento or forma_pagamento not in ['dinheiro', 'credito', 'debito', 'pix', 'outros']:
                messagebox.showwarning("Aviso", "Selecione uma forma de pagamento válida.")
                return
                
            # Validar valor recebido para pagamento em dinheiro
            valor_recebido_float = 0.0
            if forma_pagamento == 'dinheiro':
                if not valor_recebido or not valor_recebido.strip():
                    messagebox.showwarning("Aviso", "Informe o valor recebido em dinheiro.")
                    return
                    
                try:
                    valor_recebido_float = float(valor_recebido.replace('.', '').replace(',', '.'))
                    if valor_recebido_float <= 0:
                        messagebox.showwarning("Aviso", "O valor recebido deve ser maior que zero.")
                        return
                        
                    if valor_recebido_float < valor_total:
                        messagebox.showwarning("Aviso", 
                            f"O valor recebido (R$ {valor_recebido_float:.2f}) "
                            f"é menor que o valor total (R$ {valor_total:.2f}).")
                        return
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido. Digite um valor numérico válido.")
                    return
            
            # Preparar os dados do pedido
            itens_pedido = []
            try:
                # Usar os dados já estruturados em self.itens_pedido em vez de ler da árvore
                for item in self.itens_pedido:
                    itens_pedido.append({
                        'produto_id': item['id'],  # Usar o ID do item diretamente
                        'quantidade': item['quantidade'],
                        'preco_unitario': item['preco'],
                        'observacoes': item.get('observacoes', ''),
                        'opcoes': item.get('opcoes', [])  # Incluir as opções do item
                    })
            except (ValueError, IndexError) as e:
                messagebox.showerror("Erro", f"Erro ao processar itens do carrinho: {str(e)}")
                return
            
            # Verificar se há itens válidos no pedido
            if not itens_pedido:
                messagebox.showwarning("Aviso", "Nenhum item válido encontrado no carrinho.")
                return
            
            # Obter observações do pedido, se disponível
            observacoes = ""
            if hasattr(self, 'observacoes_text'):
                try:
                    observacoes = self.observacoes_text.get('1.0', tk.END).strip()
                except:
                    pass
            
            # Dados do pedido
            dados_pedido = {
                'cliente_id': self.cliente_atual['id'],
                'cliente_nome': self.cliente_atual.get('nome', ''),
                'cliente_telefone': self.cliente_atual.get('telefone', ''),
                'endereco': self.cliente_atual.get('endereco', ''),
                'bairro': self.cliente_atual.get('bairro', ''),
                'cidade': self.cliente_atual.get('cidade', ''),
                'referencia': self.cliente_atual.get('referencia', ''),
                'itens': itens_pedido,
                'valor_total': valor_total,
                'forma_pagamento': forma_pagamento,
                'status': 'pendente',
                'observacoes': observacoes,
                'data_hora': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'taxa_entrega': float(self.taxa_entrega_label.cget('text').replace('R$ ', '').replace(',', '.')) if hasattr(self, 'taxa_entrega_label') else 0.0
            }
            
            # Se for pagamento em dinheiro, adicionar o valor recebido e o troco
            if forma_pagamento == 'dinheiro':
                dados_pedido['valor_recebido'] = valor_recebido_float
                dados_pedido['troco'] = valor_recebido_float - valor_total
            
            # Adicionar o ID do usuário logado aos dados do pedido
            if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                dados_pedido['usuario_id'] = self.controller.usuario.id
            else:
                # Se não houver usuário logado, usar um valor padrão (1 = admin)
                dados_pedido['usuario_id'] = 1
                
            # Registrar o pedido no banco de dados
            try:
                sucesso, mensagem, pedido_id = self.delivery_controller.registrar_pedido(dados_pedido)
                
                if sucesso:
                    # Mensagem de sucesso removida conforme solicitado
                    
                    # Imprimir o comprovante do pedido
                    try:
                        # Tentar obter o config_controller de várias maneiras diferentes
                        config_controller = None
                        
                        # 1. Tenta acessar diretamente do controlador
                        if hasattr(self.controller, 'config_controller'):
                            config_controller = self.controller.config_controller
                        
                        # 2. Tenta acessar através do sistema_controller
                        elif hasattr(self.controller, 'sistema_controller'):
                            if hasattr(self.controller.sistema_controller, 'config_controller'):
                                config_controller = self.controller.sistema_controller.config_controller
                        
                        # 3. Tenta importar diretamente
                        if not config_controller:
                            try:
                                from controllers.config_controller import ConfigController
                                config_controller = ConfigController()
                            except ImportError as e:
                                print(f"Erro ao importar ConfigController: {e}")
                        
                        # Se ainda não encontrou, usa um config_controller vazio
                        if not config_controller:
                            print("Aviso: Usando ConfigController vazio. As configurações de impressora podem não estar disponíveis.")
                            from controllers.config_controller import ConfigController
                            config_controller = ConfigController()
                            
                        # Verificar se o controller principal tem um config_controller
                        if hasattr(self.controller, 'config_controller') and self.controller.config_controller:
                            config_controller = self.controller.config_controller
                            print("Usando config_controller do controller principal")
                            
                        # Inicializar o gerenciador de impressão
                        gerenciador = GerenciadorImpressao(config_controller)
                        
                        # Preparar os dados do pedido para impressão
                        dados_venda = {
                            'id': pedido_id,
                            'data_hora': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                            'cliente_nome': self.cliente_atual.get('nome', 'Cliente não identificado'),
                            'cliente_telefone': self.cliente_atual.get('telefone', ''),
                            'valor_total': valor_total,
                            'tipo': 'DELIVERY',
                            'observacoes': observacoes,
                            'taxa_entrega': float(dados_pedido.get('taxa_entrega', 0)),
                            'forma_pagamento': dados_pedido['forma_pagamento'],
                            'usuario_id': dados_pedido.get('usuario_id', 1),
                            'usuario_nome': getattr(self.controller.usuario, 'nome', 'Operador') if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'nome') else 'Operador'
                        }
                        
                        # Adicionar endereço de entrega
                        endereco = []
                        if 'endereco' in self.cliente_atual and self.cliente_atual['endereco']:
                            endereco.append(self.cliente_atual['endereco'])
                        if 'numero' in self.cliente_atual and self.cliente_atual['numero']:
                            endereco.append(str(self.cliente_atual['numero']))
                        if 'bairro' in self.cliente_atual and self.cliente_atual['bairro']:
                            endereco.append(self.cliente_atual['bairro'])
                        
                        dados_venda['endereco_entrega'] = ", ".join(endereco) if endereco else "Endereço não informado"
                        
                        # Preparar os itens para impressão
                        itens_impressao = []
                        for item in itens_pedido:
                            # Buscar informações completas do produto, incluindo o tipo
                            produto_info = None
                            try:
                                if 'produto_id' in item and item['produto_id'] != 'TAXA_ENTREGA':
                                    produto_info = self.cadastro_controller.obter_produto(item['produto_id'])
                            except Exception as e:
                                print(f"Erro ao buscar informações do produto {item.get('produto_id')}: {e}")
                                
                            # Determinar o tipo do produto
                            tipo_produto = 'Outros'
                            if produto_info and 'tipo' in produto_info:
                                tipo_produto = produto_info['tipo']
                                
                            # Preparar item para impressão
                            # Obter o nome do produto com prioridade: produto_info > descricao > nome
                            nome_produto = 'Produto sem nome'
                            if produto_info and 'nome' in produto_info:
                                nome_produto = produto_info['nome']
                            elif 'descricao' in item and item['descricao']:
                                nome_produto = item['descricao']
                            elif 'nome' in item and item['nome']:
                                nome_produto = item['nome']
                                
                            item_impressao = {
                                'nome': nome_produto,  # Usar o nome obtido do produto
                                'quantidade': item['quantidade'],
                                'valor_unitario': item['preco_unitario'],
                                'valor_total': item['quantidade'] * item['preco_unitario'],
                                'observacoes': item.get('observacoes', ''),
                                'tipo': tipo_produto
                            }
                            
                            # Adicionar opções do item, se houver
                            if 'opcoes' in item and item['opcoes']:
                                # Processar as opções para o formato esperado pelo módulo de impressão
                                opcoes_formatadas = []
                                for opcao in item['opcoes']:
                                    # Verificar se a opção tem o formato esperado
                                    if isinstance(opcao, dict) and 'nome' in opcao:
                                        opcoes_formatadas.append(opcao)
                                    elif isinstance(opcao, dict) and 'opcao_id' in opcao:
                                        # Buscar informações da opção no banco de dados
                                        try:
                                            from controllers.opcoes_controller import OpcoesController
                                            from src.db.database import DatabaseConnection
                                            
                                            # Obter conexão com o banco de dados
                                            db_connection = DatabaseConnection().get_connection()
                                            opcoes_controller = OpcoesController(db_connection=db_connection)
                                            opcao_info = opcoes_controller.obter_item_opcao(opcao['opcao_id'])
                                            if opcao_info:
                                                opcoes_formatadas.append({
                                                    'nome': opcao_info.get('nome', 'Opção'),
                                                    'preco_adicional': opcao_info.get('preco_adicional', 0)
                                                })
                                        except Exception as e:
                                            print(f"Erro ao buscar informações da opção {opcao.get('opcao_id')}: {e}")
                                
                                item_impressao['opcoes'] = opcoes_formatadas
                                
                            itens_impressao.append(item_impressao)
                        
                        
                        # Obtém o nome formatado da forma de pagamento
                        forma_nome = forma_pagamento.lower()
                        forma_formatada = forma_pagamento
                        
                        pagamentos_impressao = [{
                            'forma_nome': forma_formatada,
                            'valor': valor_total
                        }]
                        
                        # Se for pagamento em dinheiro, adicionar o troco
                        if forma_pagamento.lower() == 'dinheiro' and 'troco' in dados_pedido:
                            pagamentos_impressao.append({
                                'forma_nome': 'TROCO',
                                'valor': dados_pedido['troco']
                            })
                        
                        # Imprimir o demonstrativo de delivery com informações do cliente e endereço
                        sucesso_cupom = gerenciador.imprimir_demonstrativo_delivery(
                            dados_venda, 
                            itens_impressao, 
                            pagamentos_impressao
                        )
                        
                        # Depois, imprimir as comandas por tipo de produto
                        # Os itens já estão no formato esperado pelo método imprimir_comandas_por_tipo
                        # com o tipo do produto incluído
                        
                        # Imprimir as comandas por tipo de produto
                        sucesso_comandas = gerenciador.imprimir_comandas_por_tipo(
                            dados_venda,
                            itens_impressao
                        )
                        
                        if not sucesso_cupom and not sucesso_comandas:
                            print("Aviso: Não foi possível imprimir o comprovante do pedido.")
                        elif not sucesso_cupom:
                            print("Aviso: Não foi possível imprimir o cupom fiscal, mas as comandas foram enviadas.")
                        elif not sucesso_comandas:
                            print("Aviso: As comandas não foram enviadas corretamente, mas o cupom fiscal foi impresso.")
                            
                    except Exception as e:
                        print(f"Erro ao tentar imprimir o comprovante do pedido: {str(e)}")
                    
                    # Limpar o carrinho e os dados do cliente
                    self._limpar_carrinho_sem_confirmacao()
                    self.cliente_atual = None
                    self._atualizar_dados_cliente()
                    
                    # Fechar a janela de pagamento
                    if janela and janela.winfo_exists():
                        janela.destroy()
                    
                    # Atualizar a lista de pedidos em espera (se existir)
                    if hasattr(self, '_atualizar_lista_pedidos'):
                        try:
                            self._atualizar_lista_pedidos()
                        except Exception as e:
                            print(f"Aviso: Não foi possível atualizar a lista de pedidos: {str(e)}")
                else:
                    messagebox.showerror("Erro", f"Não foi possível registrar o pedido: {mensagem}")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao registrar pedido no banco de dados: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado ao processar o pagamento: {str(e)}")
            import traceback
            print(f"Erro detalhado: {traceback.format_exc()}")

    def _processar_pedido_finalizado(self, pagamentos):
        """
        Processa o pedido finalizado com os pagamentos realizados
        
        Este método é mantido para compatibilidade, mas não é mais usado no fluxo principal.
        O processamento do pedido agora é feito diretamente no método confirmar_pagamento.
{{ ... }}
        """
        # Este método não faz mais nada, pois o processamento é feito em confirmar_pagamento
        # Mantido apenas para compatibilidade
        pass

    def _gerenciar_regioes_entrega(self):
        """Abre a janela para gerenciar as regiões de entrega"""
        # Criar janela de diálogo
        dialog = tk.Toplevel(self.frame)
        dialog.title("Gerenciar Regiões de Entrega")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Centralizar a janela
        largura = 800
        altura = 500
        x = (dialog.winfo_screenwidth() - largura) // 2
        y = (dialog.winfo_screenheight() - altura) // 2
        dialog.geometry(f"{largura}x{altura}+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Frame para os botões de ação
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=(0, 10))
        
        # Botão para adicionar nova região
        btn_nova = tk.Button(
            botoes_frame,
            text="Nova Região",
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=lambda: self._abrir_formulario_regiao()
        )
        btn_nova.pack(side="left", padx=5)
        
        # Botão para atualizar a lista
        btn_atualizar = tk.Button(
            botoes_frame,
            text="Atualizar",
            bg=self.cores["secundaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=lambda: self._atualizar_lista_regioes(tree)
        )
        btn_atualizar.pack(side="left", padx=5)
        
        # Criar a tabela de regiões
        colunas = ("ID", "Nome", "Taxa (R$)", "Tempo Médio (min)", "Status")
        
        # Configurar estilo para a tabela
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        
        # Configurações adicionais específicas para esta tabela
        style.configure("Regioes.Treeview",
            borderwidth=0,
            highlightthickness=0
        )
        
        # Frame para a tabela com barra de rolagem
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Adicionar barra de rolagem
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        # Criar a Treeview
        tree = ttk.Treeview(
            table_frame, 
            columns=colunas, 
            show="headings",
            style="Regioes.Treeview",
            selectmode="browse",
            yscrollcommand=scroll_y.set
        )
        
        # Configurar a barra de rolagem
        scroll_y.config(command=tree.yview)
        
        # Empacotar a treeview
        tree.pack(side="left", fill="both", expand=True)
        
        # Configurar as colunas
        larguras = {"ID": 50, "Nome": 250, "Taxa (R$)": 100, "Tempo Médio (min)": 120, "Status": 80}
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=larguras.get(col, 100), anchor="center" if col != "Nome" else "w")
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Empacotar a árvore e a barra de rolagem
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Adicionar botões de ação
        botoes_acao_frame = ttk.Frame(main_frame)
        botoes_acao_frame.pack(fill="x", pady=(10, 0))
        
        # Botão para editar
        btn_editar = tk.Button(
            botoes_acao_frame,
            text="Editar",
            bg=self.cores["secundaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=lambda: self._editar_regiao_selecionada(tree)
        )
        btn_editar.pack(side="left", padx=5)
        
        # Botão para excluir
        btn_excluir = tk.Button(
            botoes_acao_frame,
            text="Excluir",
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=lambda: self._excluir_regiao_selecionada(tree)
        )
        btn_excluir.pack(side="left", padx=5)
        
        # Frame para o botão de fechar
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        # Botão Fechar
        btn_fechar = tk.Button(
            btn_frame,
            text="Fechar",
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=dialog.destroy
        )
        btn_fechar.pack(side="right", padx=5, pady=5)
        
        # Configurar o evento de duplo clique para edição
        tree.bind("<Double-1>", lambda e: self._editar_regiao_selecionada(tree))
        
        # Carregar as regiões na tabela
        self._atualizar_lista_regioes(tree)
    
    def _abrir_formulario_regiao(self, regiao_id=None):
        """Abre o formulário para cadastrar/editar uma região de entrega."""
        from views.dialogs.regiao_entrega_dialog import RegiaoEntregaDialog
        
        regiao_data = None
        if regiao_id:
            regiao_data = self.delivery_controller.obter_regiao_por_id(regiao_id)
        
        def callback_salvar(dados):
            try:
                self.delivery_controller.salvar_regiao_entrega(dados)
                messagebox.showinfo("Sucesso", "Região salva com sucesso!", parent=dialog)
                self._atualizar_lista_regioes()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar região: {str(e)}", parent=dialog)
        
        dialog = RegiaoEntregaDialog(
            self.frame,
            self.delivery_controller,
            regiao_data=regiao_data,
            callback=callback_salvar
        )
    
    def _editar_regiao_selecionada(self, tree):
        """Abre o formulário para editar a região selecionada."""
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma região para editar.")
            return
        
        regiao_id = tree.item(selecionado[0], 'values')[0]
        self._abrir_formulario_regiao(regiao_id)
    
    def _excluir_regiao_selecionada(self, tree):
        """Exclui a região selecionada."""
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma região para excluir.")
            return
        
        regiao_id = tree.item(selecionado[0], 'values')[0]
        regiao_nome = tree.item(selecionado[0], 'values')[1]
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir a região '{regiao_nome}'?"):
            try:
                if self.delivery_controller.excluir_regiao_entrega(regiao_id):
                    messagebox.showinfo("Sucesso", "Região excluída com sucesso!")
                    self._atualizar_lista_regioes(tree)
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir a região.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir região: {str(e)}")
    
    def _atualizar_lista_regioes(self, tree=None):
        """Atualiza a lista de regiões na tabela."""
        if not tree:
            # Se não for passada uma tree, tenta encontrar a janela ativa
            for window in self.frame.winfo_children():
                if isinstance(window, tk.Toplevel) and "Gerenciar Regiões de Entrega" in window.title():
                    for widget in window.winfo_children():
                        if isinstance(widget, ttk.Frame) and hasattr(widget, 'winfo_children'):
                            for child in widget.winfo_children():
                                if isinstance(child, ttk.Treeview):
                                    tree = child
                                    break
                            if tree:
                                break
                    break
            
            if not tree:
                return
        
        # Limpar a árvore
        for item in tree.get_children():
            tree.delete(item)
        
        # Buscar as regiões no banco de dados
        regioes = self.delivery_controller.listar_regioes_entrega()
        
        # Preencher a árvore
        for regiao in regioes:
            tree.insert("", "end", values=(
                regiao['id'],
                regiao['nome'],
                f"R$ {float(regiao['taxa_entrega']):.2f}".replace('.', ','),
                regiao['tempo_medio_entrega'],
                'Ativo' if regiao['ativo'] else 'Inativo'
            ))
    
    def _limpar_carrinho(self, confirmar=True):
        """
        Limpa todos os itens do carrinho.
        
        Args:
            confirmar (bool): Se True, pede confirmação antes de limpar.
        """
        if not self.itens_pedido:
            return
            
        if confirmar and not messagebox.askyesno("Confirmar", "Deseja realmente limpar o carrinho?"):
            return
            
        self.itens_pedido = []
        self._atualizar_carrinho()
        self._atualizar_total_pedido()
    
    def _limpar_carrinho_sem_confirmacao(self):
        """Limpa todos os itens do carrinho sem pedir confirmação"""
        self._limpar_carrinho(confirmar=False)
