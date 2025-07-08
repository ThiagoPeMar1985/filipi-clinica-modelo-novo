import tkinter as tk
from tkinter import ttk, messagebox
import sys
import datetime
from datetime import datetime as dt
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.cadastro_controller import CadastroController
from controllers.opcoes_controller import OpcoesController
from controllers.financeiro_controller import FinanceiroController
from views.modulos.pagamento.pagamento_module import PagamentoModule
from utils.impressao import GerenciadorImpressao
from views.modulos.vendas.delivery_module import DeliveryModule
from views.modulos.vendas.status_module import StatusPedidosModule

class VendasModule:
    def __init__(self, parent, controller):
        # Importar o controlador de cadastro para acessar produtos
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        
        # Inicializar o controlador de cadastro
        self.cadastro_controller = CadastroController()
        self.financeiro_controller = FinanceiroController(controller.db_connection)
        
        # Inicializar o carrinho de compras
        self.carrinho = []
        
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
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "💰 Venda Avulsa", "acao": "venda_avulsa"},
            {"nome": "🛵 Delivery", "acao": "delivery"},
            {"nome": "📊 Status Pedidos", "acao": "status_pedidos"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        # Limpar o frame principal
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Definir o current_view como None inicialmente
        self.current_view = None
            
        if acao == 'venda_avulsa':
            self._show_venda_avulsa()
        elif acao == 'delivery':
            self._show_delivery()
        elif acao == 'status_pedidos':
            self._show_status_pedidos()
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_delivery(self):
        """Mostra a tela de delivery"""
        # Limpar o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Inicializar o módulo de delivery
        try:
            delivery_module = DeliveryModule(self.frame, self.controller)
            self.current_view = delivery_module.show()
            
            # Garantir que o frame seja exibido
            self.frame.update()
           
        except Exception as e:
            print(f"Erro ao inicializar módulo de delivery: {e}")
            messagebox.showerror("Erro", f"Erro ao inicializar módulo de delivery: {e}")
    
    def _show_status_pedidos(self):
        """Mostra a tela de status dos pedidos"""
        # Limpar o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Inicializar o módulo de status de pedidos
        try:
            status_module = StatusPedidosModule(self.frame, self.controller, self.controller.db_connection)
            self.current_view = status_module.show()
            
            # Garantir que o frame seja exibido
            self.frame.update()
           
        except Exception as e:
            print(f"Erro ao inicializar módulo de status de pedidos: {e}")
            messagebox.showerror("Erro", f"Erro ao inicializar módulo de status de pedidos: {e}")
            messagebox.showerror("Erro", f"Erro ao inicializar módulo de status de pedidos: {e}")
    
    def _show_default(self):
        # Tela inicial do módulo de vendas
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção de vendas no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_venda_avulsa(self):
        # Remover a visualização atual se existir
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            
        # Criar novo frame para a visualização
        frame = ttk.Frame(self.frame, style="Card.TFrame")
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame  # Armazenar referência à visualização atual
        
        # Configurar estilo para as tabelas
        style = ttk.Style()
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
        
        # Título da página
        titulo_frame = tk.Frame(frame, bg=self.cores["fundo"])
        titulo_frame.pack(fill="x", padx=0, pady=0)
        
        titulo_label = tk.Label(
            titulo_frame, 
            text="VENDA AVULSA", 
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
        
        # Frame esquerdo - Lista de produtos
        produtos_frame = ttk.Frame(container)
        produtos_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
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
        
        busca_entry = ttk.Entry(busca_frame, width=20)
        busca_entry.pack(side="left")
        
        self.busca_entry = busca_entry
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
        colunas = ("Código", "Produto", "Preço", "Estoque")
        
        self.produtos_tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", height=20, style="Custom.Treeview")
        
        # Configurar menu de contexto para a tabela de produtos (apenas opções)
        self.menu_contexto_produto = tk.Menu(self.produtos_tree, tearoff=0)
        self.menu_contexto_produto.add_command(label="Adicionar Opções", command=self._mostrar_opcoes_produto)
        
        # Vincular evento de clique direito
        self.produtos_tree.bind("<Button-3>", self._mostrar_menu_contexto_produto)
        
        # Configurar cabeçalhos com larguras proporcionais
        larguras = {"Código": 80, "Produto": 200, "Preço": 100, "Estoque": 80}
        for col in colunas:
            self.produtos_tree.heading(col, text=col)
            self.produtos_tree.column(col, width=larguras.get(col, 100))
        
        # Carregar produtos do banco de dados
        try:
            self._carregar_produtos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {str(e)}")
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.produtos_tree.yview)
        self.produtos_tree.configure(yscroll=scrollbar.set)
        
        self.produtos_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botões de ação para produtos em um frame separado abaixo da tabela
        botoes_produtos = ttk.Frame(produtos_frame)
        botoes_produtos.pack(fill="x", pady=5)
        
        # Botão de adicionar ao carrinho com tamanho maior
        adicionar_button = tk.Button(
            botoes_produtos, 
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
        carrinho_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Cabeçalho do carrinho com título
        header_carrinho = ttk.Frame(carrinho_frame)
        header_carrinho.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            header_carrinho, 
            text="Carrinho de Compras", 
            font=('Arial', 12, 'bold')
        ).pack(side="left")
        
        # Organizar o carrinho em um frame principal
        carrinho_conteudo = ttk.Frame(carrinho_frame)
        carrinho_conteudo.pack(fill="both", expand=True)
        
        # Frame para a tabela do carrinho
        tabela_carrinho_frame = ttk.Frame(carrinho_conteudo)
        tabela_carrinho_frame.pack(fill="both", expand=True)
        
        # Tabela do carrinho com altura ajustada
        colunas_carrinho = ("Produto", "Qtd", "Preço Unit.", "Total")
        
        self.carrinho_tree = ttk.Treeview(tabela_carrinho_frame, columns=colunas_carrinho, show="headings", height=15, style="Custom.Treeview")
        
        # Configurar cabeçalhos com larguras proporcionais
        larguras_carrinho = {"Produto": 200, "Qtd": 50, "Preço Unit.": 100, "Total": 100}
        for col in colunas_carrinho:
            self.carrinho_tree.heading(col, text=col)
            self.carrinho_tree.column(col, width=larguras_carrinho.get(col, 100))
        
        # Barra de rolagem
        scrollbar_carrinho = ttk.Scrollbar(tabela_carrinho_frame, orient="vertical", command=self.carrinho_tree.yview)
        self.carrinho_tree.configure(yscroll=scrollbar_carrinho.set)
        
        self.carrinho_tree.pack(side="left", fill="both", expand=True)
        scrollbar_carrinho.pack(side="right", fill="y")
        
        # Botões de ação para o carrinho em um grid para melhor distribuição
        botoes_carrinho = ttk.Frame(carrinho_frame)
        botoes_carrinho.pack(fill="x", pady=3)
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
        resumo_frame = ttk.LabelFrame(carrinho_frame, text="Resumo da Compra")
        resumo_frame.pack(fill="x", pady=3)
        
        # Grid para organizar os campos do resumo
        resumo_grid = ttk.Frame(resumo_frame)
        resumo_grid.pack(fill="x", padx=10, pady=5)
        resumo_grid.columnconfigure(0, weight=1)  # Coluna dos rótulos
        resumo_grid.columnconfigure(1, weight=1)  # Coluna dos valores
        
        # Subtotal
        ttk.Label(resumo_grid, text="Subtotal:", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=2)
        self.subtotal_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=('Arial', 10))
        self.subtotal_valor.grid(row=0, column=1, sticky="e", pady=2)
        
        # Desconto
        ttk.Label(resumo_grid, text="Desconto (R$):", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=2)
        
        # Variável para armazenar o valor do desconto
        self.desconto_var = tk.StringVar()
        self.desconto_var.trace_add("write", self._calcular_total_com_desconto)
        
        self.desconto_entry = ttk.Entry(resumo_grid, width=10, textvariable=self.desconto_var)
        self.desconto_entry.grid(row=1, column=1, sticky="e", pady=2)
        
        # Separador antes do total
        ttk.Separator(resumo_grid, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Total com destaque
        ttk.Label(resumo_grid, text="TOTAL:", font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky="w", pady=2)
        self.total_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=('Arial', 12, 'bold'))
        self.total_valor.grid(row=3, column=1, sticky="e", pady=2)
        
        # Botão de finalizar venda com tamanho maior e mais destaque
        finalizar_button = tk.Button(
            carrinho_frame, 
            text="FINALIZAR VENDA", 
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            font=('Arial', 12, 'bold'),
            bd=0,
            padx=20,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=self._finalizar_venda
        )
        finalizar_button.pack(fill="x", pady=5)
        
        self.current_view = frame
    
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
    
    def _filtrar_produtos_por_tipo(self, tipo):
        """Filtra produtos por tipo"""
        self._carregar_produtos(tipo)
        
    def _buscar_produtos(self):
        """Busca produtos pelo termo digitado"""
        termo = self.busca_entry.get().strip().lower()
        
        if not termo:
            self._carregar_produtos()
            return
            
        # Limpar a tabela atual
        for item in self.produtos_tree.get_children():
            self.produtos_tree.delete(item)
            
        try:
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
                        produto.get('quantidade_minima', '0')
                    )
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar produtos: {str(e)}")
            
    def _mostrar_menu_contexto_produto(self, event):
        """Exibe o menu de contexto para o produto selecionado"""
        # Identificar o item clicado
        item = self.produtos_tree.identify_row(event.y)
        if item:
            # Selecionar o item clicado
            self.produtos_tree.selection_set(item)
            # Exibir o menu de contexto
            self.menu_contexto_produto.post(event.x_root, event.y_root)
    
    def _mostrar_opcoes_produto(self):
        """Exibe as opções disponíveis para o produto selecionado"""
        # Obter o item selecionado
        selecionado = self.produtos_tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para adicionar opções.")
            return
            
        # Obter os dados do produto selecionado
        item = self.produtos_tree.item(selecionado[0])
        valores = item['values']
        produto_id = valores[0]
        
        # Verificar se o produto tem opções antes de criar a janela
        try:
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
            self.janela_opcoes = tk.Toplevel(self.parent)
            self.janela_opcoes.title(f"Opções para {valores[1]}")
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
            messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
            self.janela_opcoes.destroy()
    
    def _adicionar_ao_carrinho_com_opcoes(self, produto_id, valores_produto):
        """Adiciona o produto ao carrinho com as opções selecionadas"""
        try:
            # Obter as opções selecionadas
            opcoes_selecionadas = []
            
            for grupo_id, selecao in self.selecoes_opcoes.items():
                if selecao['tipo'] == 'unico' and selecao['var'].get():
                    # Opção única selecionada
                    opcao_id = int(selecao['var'].get())
                    
                    # Buscar o nome da opção selecionada
                    nome_opcao = ""
                    preco_adicional = 0.0
                    
                    # Buscar informações da opção no banco de dados
                    try:
                        from controllers.opcoes_controller import OpcoesController
                        db_connection = getattr(self.controller, 'db_connection', None)
                        if db_connection:
                            opcoes_controller = OpcoesController(db_connection=db_connection)
                            opcao = opcoes_controller.obter_item_opcao(opcao_id)
                            if opcao:
                                nome_opcao = opcao.get('nome', '')
                                preco_adicional = opcao.get('preco_adicional', 0.0)
                    except Exception as e:
                        print(f"Erro ao buscar nome da opção: {e}")
                    
                    opcoes_selecionadas.append({
                        'grupo_id': grupo_id,
                        'opcao_id': opcao_id,
                        'nome': nome_opcao,
                        'preco_adicional': preco_adicional
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
            self.janela_opcoes.destroy()
            
            # Adicionar ao carrinho
            self._adicionar_ao_carrinho(produto_id, valores_produto, opcoes_selecionadas)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar opções: {str(e)}")
    
    def _adicionar_ao_carrinho(self, produto_id=None, valores=None, opcoes_selecionadas=None):
        """Adiciona o produto selecionado ao carrinho de compras"""
        # Se não foram fornecidos valores, obter da seleção atual
        if valores is None:
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
        for item in self.carrinho:
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
                'tipo': tipo_produto,  # Tipo do produto para impressão nas comandas
                'opcoes': opcoes_selecionadas or []  # Lista para armazenar as opções do produto
            }
            self.carrinho.append(novo_item)
            
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
        for item in self.carrinho:
            # Verificar se o item tem opções
            tem_opcoes = bool(item.get('opcoes'))
            
            # Adicionar o item principal
            item_id = self.carrinho_tree.insert(
                "", 
                tk.END, 
                values=(
                    f"{item['nome']} {'+'  if tem_opcoes else ''}",
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
        
        # Calcular o subtotal (soma de todos os itens)
        self.subtotal = sum(item['total'] for item in self.carrinho)
        
        # Atualizar os valores no resumo da compra
        if hasattr(self, 'subtotal_valor'):
            self.subtotal_valor.config(text=f"R$ {self.subtotal:.2f}".replace('.', ','))
            
        # Recalcular o total com desconto
        self._calcular_total_com_desconto()
        
        # Atualizar o total do carrinho (se houver um label para isso)
        if hasattr(self, 'total_carrinho_label'):
            self.total_carrinho_label.config(text=f"R$ {self.subtotal:.2f}".replace('.', ','))

    def _remover_do_carrinho(self):
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
        
        if 0 <= indice < len(self.carrinho):
            # Remover o item do carrinho
            self.carrinho.pop(indice)
            
            # Atualizar a exibição do carrinho
            self._atualizar_carrinho()
    
    def _limpar_carrinho(self):
        """Limpa todos os itens do carrinho"""
        if not self.carrinho:
            messagebox.showinfo("Informação", "O carrinho já está vazio.")
            return
            
        # Confirmar a ação
        resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar o carrinho?")
        
        if resposta:
            # Limpar o carrinho
            self.carrinho = []
            
            # Limpar o campo de desconto
            if hasattr(self, 'desconto_var'):
                self.desconto_var.set('')
                
            # Atualizar a exibição do carrinho
            self._atualizar_carrinho()
    
    def _calcular_total_com_desconto(self, *args):
        """Calcula o total da compra considerando o desconto"""
        if not hasattr(self, 'subtotal'):
            self.subtotal = 0
            
        # Obter o valor do desconto
        desconto = 0
        if hasattr(self, 'desconto_var') and self.desconto_var.get():
            try:
                # Substituir vírgula por ponto para conversão correta
                desconto_str = self.desconto_var.get().replace(',', '.')
                desconto = float(desconto_str)
            except ValueError:
                # Se não for um número válido, define como zero
                desconto = 0
                
        # Calcular o total (subtotal - desconto)
        total = max(0, self.subtotal - desconto)  # Garante que o total não seja negativo
        
        # Atualizar o valor do total na interface
        if hasattr(self, 'total_valor'):
            self.total_valor.config(text=f"R$ {total:.2f}".replace('.', ','))
            
    def _finalizar_venda(self):
        """Abre a tela de pagamento para finalizar a venda"""
        # Verificar se há itens no carrinho
        if not self.carrinho:
            messagebox.showinfo("Informação", "O carrinho está vazio. Adicione produtos antes de finalizar.")
            return
            
        # Obter o valor do subtotal
        subtotal = self.subtotal
        
        # Obter o valor do desconto
        desconto = 0
        if hasattr(self, 'desconto_var') and self.desconto_var.get():
            try:
                desconto_str = self.desconto_var.get().replace(',', '.')
                desconto = float(desconto_str)
            except ValueError:
                desconto = 0
        
        # Obter a conexão com o banco de dados do controlador principal
        db_connection = getattr(self.controller, 'db_connection', None)
        if not db_connection:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
            return
        
        # Criar uma janela para o módulo de pagamentos
        pagamento_window = tk.Toplevel(self.parent)
        pagamento_window.title("Pagamento")
        pagamento_window.geometry("800x600")
        pagamento_window.transient(self.parent)
        
        # Centralizar na tela
        pagamento_window.update_idletasks()
        width = pagamento_window.winfo_width()
        height = pagamento_window.winfo_height()
        x = (pagamento_window.winfo_screenwidth() // 2) - (width // 2)
        y = (pagamento_window.winfo_screenheight() // 2) - (height // 2)
        pagamento_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Inicializar o módulo de pagamentos
        pagamento_module = PagamentoModule(
            pagamento_window,
            db_connection,
            valor_total=subtotal,
            desconto=desconto,
            callback_finalizar=self._processar_venda_finalizada,
            venda_tipo='avulsa',
            itens_venda=self.carrinho
        )
        
        # Configurar evento para quando a janela for fechada
        pagamento_window.protocol("WM_DELETE_WINDOW", pagamento_window.destroy)
        
    def _processar_venda_finalizada(self, venda_dados, itens_venda, pagamentos):
        """
        Processa a venda finalizada com os pagamentos realizados
        
        Args:
            venda_dados: Dicionário com os dados da venda
            itens_venda: Lista de itens da venda
            pagamentos: Lista de dicionários com os dados dos pagamentos
        """
        # Calcular totais
        valor_total = sum(item['total'] for item in self.carrinho)
        desconto = float(self.desconto_var.get() or 0) if hasattr(self, 'desconto_var') else 0
        valor_final = valor_total - desconto
        
        # Obter informações do usuário logado
        usuario_id = getattr(self.controller, 'usuario_id', None)
        usuario_nome = getattr(self.controller, 'usuario_nome', 'Sistema')
        
        # Criar descrição dos itens da venda
        descricao_itens = ", ".join([f"{item['quantidade']}x {item['nome']}"[:50] for item in self.carrinho[:3]])
        if len(self.carrinho) > 3:
            descricao_itens += "..."
            
        descricao = f"Venda {venda_dados.get('tipo', 'avulsa')} - {descricao_itens}"
        
        cursor = None
        try:
            cursor = self.controller.db_connection.cursor()
            
            # Inserir o pedido
            cursor.execute("""
                INSERT INTO pedidos (
                    data_abertura, 
                    status, 
                    total, 
                    garcom_id, 
                    tipo, 
                    observacao, 
                    cliente_nome,
                    status_entrega,
                    processado_estoque
                )
                VALUES (
                    NOW(), 
                    'FECHADO', 
                    %s, 
                    %s, 
                    'AVULSO', 
                    %s, 
                    %s,
                    'NAO_APLICAVEL',
                    0
                )
            """, (
                valor_final,  # total
                usuario_id,   # garcom_id (usando o usuário logado)
                descricao,    # observação com os itens
                usuario_nome  # cliente_nome (usando o nome do usuário logado)
            ))
            
            pedido_id = cursor.lastrowid
            
            # Registrar cada pagamento individualmente
            entrada_ids = []
            for pagamento in pagamentos:
                try:
                    # Obter o nome da forma de pagamento
                    forma_pagamento = 'Desconhecido'
                    if 'forma_nome' in pagamento:
                        forma_pagamento = pagamento['forma_nome']
                    elif 'forma_id' in pagamento:
                        # Se tivermos o ID, podemos buscar o nome da forma de pagamento
                        try:
                            cursor_pag = self.controller.db_connection.cursor(dictionary=True)
                            cursor_pag.execute("SELECT nome FROM formas_pagamento WHERE id = %s", (pagamento['forma_id'],))
                            forma = cursor_pag.fetchone()
                            if forma:
                                forma_pagamento = forma['nome']
                            cursor_pag.close()
                        except Exception as e:
                            print(f"Erro ao buscar forma de pagamento: {e}")
                    
                    # Registrar entrada financeira para cada pagamento
                    entrada_id = self.financeiro_controller.registrar_entrada(
                        valor=pagamento['valor'],
                        descricao=f"{descricao} - {pagamento.get('observacao', '')}",
                        tipo_entrada=forma_pagamento,
                        usuario_id=usuario_id,
                        usuario_nome=usuario_nome,
                        pedido_id=pedido_id
                    )
                    entrada_ids.append(entrada_id)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Erro ao registrar pagamento: {e}")
            
            # Se não conseguiu registrar nenhum pagamento, levantar exceção
            if not entrada_ids:
                raise Exception("Não foi possível registrar os pagamentos.")
            
            # Commit das alterações
            self.controller.db_connection.commit()
            
            # Preparar dados da venda para impressão
            venda = {
                'tipo': venda_dados.get('tipo', 'avulsa'),
                'valor_total': valor_total,
                'desconto': desconto,
                'valor_final': valor_final,
                'data_venda': datetime.datetime.now(),
                'pedido_id': pedido_id,
                'entrada_id': entrada_ids[0] if entrada_ids else None
            }
            
            # Limpar o carrinho
            self.carrinho = []
            
            # Limpar o campo de desconto
            if hasattr(self, 'desconto_var'):
                self.desconto_var.set('')
                
            # Atualizar a interface
            self._atualizar_carrinho()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo(
                "Venda Finalizada", 
                f"Venda finalizada com sucesso!\nPedido #{pedido_id}"
            )
            
            # Voltar para a tela inicial de vendas
            self._show_venda_avulsa()
            
        except Exception as e:
            if self.controller.db_connection:
                self.controller.db_connection.rollback()
            print(f"Erro ao processar venda: {e}")
            messagebox.showerror(
                "Erro", 
                f"Ocorreu um erro ao processar a venda: {str(e)}"
            )
        finally:
            if cursor:
                cursor.close()
