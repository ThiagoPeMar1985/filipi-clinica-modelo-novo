"""
Módulo para gerenciamento de pedidos de mesas.
Permite visualizar, adicionar, editar e remover pedidos de uma mesa específica.

tabelas em uso neste modulo
Table: mesas
Columns:
id int AI PK 
numero int 
status varchar(20) 
capacidade int 
pedido_atual_id int

Table: itens_pedido
Columns:
id int AI PK 
pedido_id int 
produto_id int 
quantidade int 
valor_unitario decimal(10,2) 
subtotal decimal(10,2) 
observacao text 
usuario_id int 
data_hora datetime 
valor_total decimal(10,2) 
observacoes text 
status varchar(20) 
data_hora_preparo datetime 
data_hora_pronto datetime 
data_hora_entregue datetime

Table: pedidos
Columns:
id int AI PK 
mesa_id int 
data_abertura datetime 
data_fechamento datetime 
status varchar(20) 
total decimal(10,2) 
usuario_id int 
tipo enum('MESA','AVULSO','DELIVERY') 
cliente_id int 
cliente_nome varchar(255) 
cliente_telefone varchar(20) 
cliente_endereco text 
entregador_id int 
tipo_cliente varchar(20) 
regiao_id int 
taxa_entrega decimal(10,2) 
observacao text 
previsao_entrega datetime 
data_entrega datetime 
status_entrega varchar(50) 
processado_estoque tinyint(1) 
data_atualizacao timestamp 
data_inicio_preparo datetime 
data_pronto_entrega datetime 
data_saida_entrega datetime 
data_cancelamento datetime 
forma_pagamento varchar(50) 
troco_para decimal(10,2)

Table: opcoes_itens
Columns:
id int AI PK 
grupo_id int 
nome varchar(100) 
descricao text 
preco_adicional decimal(10,2) 
ativo tinyint(1) 
data_criacao timestamp 
data_atualizacao timestamp

Table: itens_pedido_opcoes
Columns:
id int AI PK 
item_pedido_id int 
opcao_id int 
grupo_id int 
nome varchar(255) 
preco_adicional decimal(10,2) 
data_criacao timestamp

table: produtos
Columns:
id int AI PK 
nome varchar(255) 
descricao text 
tipo varchar(50) 
preco_venda decimal(10,2) 
unidade_medida varchar(10) 
quantidade_minima decimal(10,2)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ..base_module import BaseModule
from src.config.estilos import CORES, FONTES
from src.controllers.mesas_controller import MesasController
from src.controllers.opcoes_controller import OpcoesController

class PedidosMesasModule(BaseModule):
    def __init__(self, parent, controller, mesa=None, db_connection=None, modulo_anterior=None):
        """
        Inicializa o módulo de pedidos de mesas.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
            mesa: Dados da mesa selecionada
            db_connection: Conexão com o banco de dados (opcional)
            modulo_anterior: Módulo anterior para voltar (opcional)
        """
        # Inicializa a classe base
        super().__init__(parent, controller)
        
        self.mesa = mesa
        self.db_connection = db_connection
        self.modulo_anterior = modulo_anterior
        
        # Inicializa os controllers
        self.controller_mesas = MesasController(db_connection=db_connection)
        self.opcoes_controller = OpcoesController(db_connection=db_connection)
        
        # Inicializa as listas vazias
        self.pedidos = []
        self.produtos = []
        self.itens_pedido = []
        self.pedido_atual = None
        
        # Inicializa variáveis de controle
        self.quantidade_var = tk.StringVar(value="1")
        self.desconto_var = tk.StringVar(value="0.00")
        self.selecoes_opcoes = {}
        
        # Configurar a interface primeiro para mostrar algo ao usuário rapidamente
        self.setup_ui()
        
        # Carregar dados em segundo plano após a interface estar pronta
        self.parent.after(100, self.carregar_dados)
        
    def carregar_dados(self):
        """Carrega os dados essenciais para iniciar o módulo e agenda o carregamento dos dados restantes"""
        try:
            # Primeiro, carregar os produtos
            if self.controller_mesas.carregar_produtos():
                self.produtos = self.controller_mesas.produtos
                self.preencher_tabela_produtos()
            
            # Em seguida, carregar os pedidos da mesa
            if self.mesa and self.controller_mesas.carregar_pedidos(self.mesa['id']):
                self.pedidos = self.controller_mesas.pedidos
                self.pedido_atual = self.controller_mesas.pedido_atual
                self.itens_pedido = self.controller_mesas.itens_pedido
                self.preencher_tabela_itens()
            
        except Exception as e:
            print(f"Erro ao carregar dados: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def carregar_pedidos(self):
        """Carrega os pedidos da mesa atual usando o controller"""
        try:
            if self.mesa and self.controller_mesas.carregar_pedidos(self.mesa['id']):
                self.pedidos = self.controller_mesas.pedidos
                self.pedido_atual = self.controller_mesas.pedido_atual
                self.itens_pedido = self.controller_mesas.itens_pedido
                self.preencher_tabela_itens()
                return True
            return False
        except Exception as e:
            print(f"Erro ao carregar pedidos: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    # As funções carregar_produtos e carregar_itens_pedido foram movidas para o MesasController
    # Consulte o controller para ver a implementação dessas funções
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = tk.Frame(self.frame, bg=CORES['fundo'])
        main_frame.pack(fill="both", expand=True)
        
        # Variáveis de controle já inicializadas no __init__
        
        # Título da página com botão de voltar
        titulo_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        titulo_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Botão de voltar
        voltar_button = tk.Button(
            titulo_frame,
            text="← Voltar",
            bg=CORES["primaria"],
            fg=CORES["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self.voltar_para_mesas
        )
        voltar_button.pack(side="left", padx=(0, 15))
        
        # Título com informações da mesa
        tk.Label(
            titulo_frame, 
            text=f"VENDA MESA {self.mesa['numero']}", 
            font=FONTES['titulo'],
            bg=CORES['fundo'],
            fg=CORES['texto'],
            padx=15,
            pady=10
        ).pack(side="left")
        
        # Container principal com grid para melhor divisão do espaço
        container = ttk.Frame(main_frame)
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
            font=FONTES['subtitulo']
        ).pack(side="left", anchor="w")
        
        # Campo de busca integrado ao cabeçalho
        busca_frame = ttk.Frame(header_frame)
        busca_frame.pack(side="right", fill="x")
        
        ttk.Label(busca_frame, text="Buscar:").pack(side="left", padx=(0, 5))
        
        self.busca_entry = ttk.Entry(busca_frame, width=20)
        self.busca_entry.pack(side="left")
        
        busca_button = tk.Button(
            busca_frame, 
            text="Buscar", 
            command=self._buscar_produtos,
            bg=CORES["primaria"],
            fg=CORES["texto_claro"],
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
                bg=CORES["primaria"],
                fg=CORES["texto_claro"],
                bd=0,
                padx=10,
                pady=5,
                relief='flat',
                cursor='hand2',
                command=lambda t=tipo: self._filtrar_produtos_por_tipo(t)
            )
            btn.grid(row=0, column=i, sticky="ew", padx=2)
        
        # Criar tabela de produtos
        self.criar_tabela_produtos(produtos_frame)
        
        # Botão de adicionar à mesa com tamanho maior
        adicionar_button = tk.Button(
            produtos_frame, 
            text="Adicionar à Mesa", 
            bg=CORES["destaque"],
            fg=CORES["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            font=FONTES['normal'],
            command=self.adicionar_item
        )
        adicionar_button.pack(fill="x")
        
        # Frame direito - Produtos do pedido
        carrinho_frame = ttk.Frame(container)
        carrinho_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Cabeçalho do carrinho com título
        header_carrinho = ttk.Frame(carrinho_frame)
        header_carrinho.pack(fill="x", pady=(0, 5))
        
        ttk.Label(
            header_carrinho, 
            text="Produtos do Pedido", 
            font=FONTES['subtitulo']
        ).pack(side="left")
        
        # Criar tabela de itens do pedido
        self.criar_tabela_itens(carrinho_frame)
        
        # Botões de ação para o carrinho em um grid para melhor distribuição
        botoes_carrinho = ttk.Frame(carrinho_frame)
        botoes_carrinho.pack(fill="x", pady=3)
        botoes_carrinho.columnconfigure(0, weight=1)
        botoes_carrinho.columnconfigure(1, weight=1)
        
        remover_button = tk.Button(
            botoes_carrinho, 
            text="Remover Item", 
            bg=CORES["alerta"],
            fg=CORES["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=lambda: self.remover_item_selecionado()
        )
        remover_button.grid(row=0, column=0, sticky="ew", padx=2)
        
        limpar_button = tk.Button(
            botoes_carrinho, 
            text="Cancelar Pedido", 
            bg=CORES["alerta"],
            fg=CORES["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=lambda: self.cancelar_pedido()
        )
        limpar_button.grid(row=0, column=1, sticky="ew", padx=2)
        
        # Resumo da compra em um frame com estilo destacado
        resumo_frame = ttk.LabelFrame(carrinho_frame, text="Resumo do Pedido")
        resumo_frame.pack(fill="x", pady=3)
        
        # Grid para organizar os campos do resumo
        resumo_grid = ttk.Frame(resumo_frame)
        resumo_grid.pack(fill="x", padx=10, pady=5)
        resumo_grid.columnconfigure(0, weight=1)  # Coluna dos rótulos
        resumo_grid.columnconfigure(1, weight=1)  # Coluna dos valores
        
        # Subtotal
        ttk.Label(resumo_grid, text="Subtotal:", font=FONTES['pequena']).grid(row=0, column=0, sticky="w", pady=2)
        self.subtotal_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=FONTES['pequena'])
        self.subtotal_valor.grid(row=0, column=1, sticky="e", pady=2)
        
        # Desconto
        ttk.Label(resumo_grid, text="Desconto (R$):", font=FONTES['pequena']).grid(row=1, column=0, sticky="w", pady=2)
        
        # Variável para armazenar o valor do desconto
        self.desconto_var = tk.StringVar()
        self.desconto_var.trace_add("write", self._calcular_total_com_desconto)
        
        self.desconto_entry = ttk.Entry(resumo_grid, width=10, textvariable=self.desconto_var)
        self.desconto_entry.grid(row=1, column=1, sticky="e", pady=2)
        
        # Separador antes do total
        ttk.Separator(resumo_grid, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Total com destaque
        ttk.Label(resumo_grid, text="TOTAL:", font=FONTES['subtitulo']).grid(row=3, column=0, sticky="w", pady=2)
        self.total_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=FONTES['subtitulo'])
        self.total_valor.grid(row=3, column=1, sticky="e", pady=2)
        
        # Botão de finalizar venda com tamanho maior e mais destaque
        finalizar_button = tk.Button(
            carrinho_frame, 
            text="FINALIZAR VENDA", 
            bg=CORES["destaque"],
            fg=CORES["texto_claro"],
            font=FONTES['subtitulo'],
            bd=0,
            padx=20,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=self.finalizar_pedido
        )
        finalizar_button.pack(fill="x", pady=5)
    
    def criar_tabela_produtos(self, parent):
        """Cria a tabela de produtos disponíveis"""
        # Criar frame para a tabela com scrollbar
        tabela_container = tk.Frame(parent, bg=CORES['fundo_conteudo'])
        tabela_container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabela_container)
        scrollbar.pack(side="right", fill="y")
        
        # Colunas da tabela - usar as mesmas do módulo de vendas
        colunas = ("Código", "Produto", "Preço", "Estoque")
        
        # Configurar estilo para a Treeview
        from src.config.estilos import configurar_estilo_tabelas
        configurar_estilo_tabelas()
        
        # Criar Treeview
        self.tabela_produtos = ttk.Treeview(
            tabela_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=10,
            style="Treeview"
        )
        
        # Configurar scrollbar
        self.tabela_produtos.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tabela_produtos.yview)
        
        # Configurar cabeçalhos com larguras proporcionais
        larguras = {"Código": 80, "Produto": 200, "Preço": 100, "Estoque": 80}
        self.tabela_produtos.heading("#0", text="", anchor="w")
        for col in colunas:
            self.tabela_produtos.heading(col, text=col)
            self.tabela_produtos.column(col, width=larguras.get(col, 100))
        
        # Esconder a coluna #0
        self.tabela_produtos.column("#0", width=0, stretch=tk.NO)
        
        # Preencher a tabela com os produtos
        self.preencher_tabela_produtos()
        
        # Empacotar a tabela
        self.tabela_produtos.pack(fill="both", expand=True)
        
        # Configurar menu de contexto para a tabela de produtos (opções)
        self.menu_contexto_produto = tk.Menu(self.tabela_produtos, tearoff=0)
        self.menu_contexto_produto.add_command(label="Adicionar Opções", command=self._mostrar_opcoes_produto)
        
        # Vincular evento de clique duplo para mostrar opções do produto
        self.tabela_produtos.bind("<Double-1>", lambda e: self._mostrar_opcoes_produto())
        
        # Vincular evento de clique direito
        self.tabela_produtos.bind("<Button-3>", self._mostrar_menu_contexto_produto)
    
    def preencher_tabela_produtos(self, produtos_filtrados=None):
        """Preenche a tabela de produtos com os dados carregados ou filtrados"""
        # Verificar se a tabela existe
        if not hasattr(self, 'tabela_produtos'):
            return
            
        # Limpar a tabela
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)
        
        # Usar os produtos filtrados se fornecidos, caso contrário usar todos os produtos
        produtos_a_mostrar = produtos_filtrados if produtos_filtrados is not None else self.produtos
        
        # Se não houver produtos, não há o que mostrar
        if not produtos_a_mostrar:
            return
        
        # Preparar todos os produtos antes de inserir (melhora o desempenho)
        produtos_para_inserir = []
        for produto in produtos_a_mostrar:
            # Formatar o preço - usando valor_unitario ou outro campo disponível
            # Verificar quais campos estão disponíveis no produto
            preco_campo = None
            for campo in ['preco', 'valor', 'valor_unitario', 'price', 'valor_venda', 'preco_venda']:
                if campo in produto:
                    preco_campo = campo
                    break
            
            # Se encontrou um campo de preço, usar; caso contrário, usar 0.0
            if preco_campo:
                preco = f"R$ {float(produto[preco_campo]):.2f}".replace('.', ',')
            else:
                # Imprimir as chaves disponíveis para debug
                print(f"Campos disponíveis no produto: {list(produto.keys())}")
                preco = "R$ 0,00"
            
            # Adicionar à lista de produtos para inserir (usando as mesmas colunas do módulo de vendas)
            produtos_para_inserir.append((
                produto['id'],                # Código
                produto['nome'],              # Produto
                preco,                        # Preço
                produto.get('quantidade_minima', '0')  # Estoque (usando quantidade_minima como estoque)
            ))
        
        # Inserir todos os produtos de uma vez
        for valores in produtos_para_inserir:
            self.tabela_produtos.insert("", "end", values=valores)
    
    # O método selecionar_produto foi removido pois agora o duplo clique mostra as opções do produto
    
    def adicionar_item_especifico(self, produto, quantidade, opcoes_selecionadas=None, preco_adicional=0.0):
        """
        Adiciona um item específico ao pedido com opções opcionais
        
        Args:
            produto: Dicionário com os dados do produto
            quantidade: Quantidade do item
            opcoes_selecionadas: Lista de opções selecionadas (opcional)
            preco_adicional: Valor adicional das opções (opcional)
            
        Nota: Este método não deve ser chamado diretamente sem verificar se há um pedido_atual.
              Use adicionar_item() que já faz essa verificação.
        """
        try:
            if not self.pedido_atual:
                raise ValueError("Nenhum pedido em andamento. Crie um pedido antes de adicionar itens.")
                
            # Usar o controller para adicionar o item
            self.controller_mesas.adicionar_item_especifico(
                self.pedido_atual['id'],
                produto,
                quantidade,
                opcoes_selecionadas,
                preco_adicional
            )
            
            # Recarregar dados
            self.carregar_pedidos()
            
            # Atualizar interface
            self.atualizar_interface()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_sem_pedidos(self, parent):
        """Exibe uma mensagem quando não há pedidos para a mesa"""
        # Frame para centralizar o conteúdo
        frame = tk.Frame(parent, bg=CORES['fundo'])
        frame.pack(expand=True, fill="both")
        
        # Ícone ou imagem (opcional)
        # Aqui poderia ser adicionado um ícone representativo
        
        # Mensagem principal
        tk.Label(
            frame, 
            text="Nenhum pedido encontrado para esta mesa", 
            font=FONTES['subtitulo'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(pady=(50, 10))
        
        # Mensagem secundária
        tk.Label(
            frame, 
            text="Clique no botão abaixo para criar um novo pedido", 
            font=FONTES['normal'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(pady=(0, 20))
        
        # Botão para criar novo pedido
        tk.Button(
            frame, 
            text="NOVO PEDIDO", 
            font=FONTES['normal'],
            bg=CORES['destaque'],
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=self.criar_novo_pedido
        ).pack(pady=10)
    
    # Primeira implementação de criar_tabela_itens removida - função duplicada
    
    # Primeira implementação de preencher_tabela_itens removida - função duplicada
    
    # Função confirmar_remover_item removida - substituída por editar_item_selecionado()
    
    def mostrar_pedidos(self, parent):
        """Exibe os pedidos existentes e seus itens"""
        # Frame para conteúdo com duas colunas
        conteudo_frame = tk.Frame(parent, bg=CORES['fundo'])
        conteudo_frame.pack(fill="both", expand=True)
        
        # Configuração de grid para duas colunas
        conteudo_frame.columnconfigure(0, weight=1)  # Coluna da esquerda (lista de itens)
        conteudo_frame.columnconfigure(1, weight=1)  # Coluna da direita (adicionar itens)
        
        # Frame para a lista de itens do pedido (coluna esquerda)
        itens_frame = tk.Frame(conteudo_frame, bg=CORES['fundo'])
        itens_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Título da seção de itens
        tk.Label(
            itens_frame, 
            text="ITENS DO PEDIDO", 
            font=FONTES['subtitulo'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(anchor="w", pady=(0, 10))
        
        # Informações do pedido atual
        if self.pedido_atual:
            info_pedido = tk.Frame(itens_frame, bg=CORES['fundo'])
            info_pedido.pack(fill="x", pady=(0, 10))
            
            # Data e hora formatada
            data_hora = datetime.datetime.strptime(str(self.pedido_atual['data_abertura']), '%Y-%m-%d %H:%M:%S')
            data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M')
            
            tk.Label(
                info_pedido, 
                text=f"Pedido #{self.pedido_atual['id']} - {data_hora_formatada}", 
                font=FONTES['pequena'],
                bg=CORES['fundo'],
                fg=CORES['texto']
            ).pack(anchor="w")
            
            tk.Label(
                info_pedido, 
                text=f"Status: {self.pedido_atual['status'].capitalize()}", 
                font=FONTES['pequena'],
                bg=CORES['fundo'],
                fg=CORES['texto']
            ).pack(anchor="w")
        
        # Frame para a tabela de itens
        tabela_frame = tk.Frame(itens_frame, bg=CORES['fundo_conteudo'], bd=1, relief="solid")
        tabela_frame.pack(fill="both", expand=True)
        
        # Criar tabela de itens
        self.criar_tabela_itens(tabela_frame)
        
        # Frame para o valor total
        total_frame = tk.Frame(itens_frame, bg=CORES['fundo'])
        total_frame.pack(fill="x", pady=10)
        
        # Valor total formatado
        valor_total = self.pedido_atual['total'] if self.pedido_atual else 0
        valor_formatado = f"R$ {valor_total:.2f}".replace('.', ',')
        
        tk.Label(
            total_frame, 
            text="TOTAL:", 
            font=FONTES['subtitulo'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(side="left")
        
        tk.Label(
            total_frame, 
            text=valor_formatado, 
            font=FONTES['subtitulo'],
            bg=CORES['fundo'],
            fg=CORES['destaque']
        ).pack(side="right")
        
        # Frame para adicionar novos itens (coluna direita)
        adicionar_frame = tk.Frame(conteudo_frame, bg=CORES['fundo'])
        adicionar_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Título da seção de adicionar itens
        tk.Label(
            adicionar_frame, 
            text="ADICIONAR ITEM", 
            font=FONTES['subtitulo'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(anchor="w", pady=(0, 10))
        
        # Formulário para adicionar itens
        self.criar_formulario_item(adicionar_frame)
        
        # Frame para botões de ação
        acoes_frame = tk.Frame(parent, bg=CORES['fundo'])
        acoes_frame.pack(fill="x", pady=(20, 0))
        
        # Botões de ação
        tk.Button(
            acoes_frame, 
            text="FINALIZAR PEDIDO", 
            font=FONTES['normal'],
            bg=CORES['destaque'],
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.finalizar_pedido
        ).pack(side="right", padx=5)
        
        tk.Button(
            acoes_frame, 
            text="NOVO PEDIDO", 
            font=FONTES['normal'],
            bg=CORES['primaria'],
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self.criar_novo_pedido
        ).pack(side="right", padx=5)
    
    def criar_tabela_itens(self, parent):
        """Cria a tabela de itens do pedido"""
        # Criar frame para a tabela com scrollbar
        tabela_container = tk.Frame(parent, bg=CORES['fundo_conteudo'])
        tabela_container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabela_container)
        scrollbar.pack(side="right", fill="y")
        
        # Colunas da tabela
        colunas = ("id", "produto", "quantidade", "valor_unit", "valor_total")
        
        # Configurar estilo para a Treeview
        from src.config.estilos import configurar_estilo_tabelas
        configurar_estilo_tabelas()
        
        # Criar Treeview
        self.tabela_itens = ttk.Treeview(
            tabela_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=10,
            style="Treeview"
        )
        
        # Configurar cabeçalhos
        self.tabela_itens.heading("id", text="ID")
        self.tabela_itens.heading("produto", text="Produto")
        self.tabela_itens.heading("quantidade", text="Qtd")
        self.tabela_itens.heading("valor_unit", text="Valor Unit.")
        self.tabela_itens.heading("valor_total", text="Valor Total")

        
        # Configurar larguras das colunas
        self.tabela_itens.column("id", width=50, anchor="center")
        self.tabela_itens.column("produto", width=200, anchor="w")
        self.tabela_itens.column("quantidade", width=50, anchor="center")
        self.tabela_itens.column("valor_unit", width=100, anchor="e")
        self.tabela_itens.column("valor_total", width=100, anchor="e")

        
        # Configurar tags para estilização
        self.tabela_itens.tag_configure('opcao_item', background='#f9f9f9')   # Cinza claro para opções
        self.tabela_itens.tag_configure('com_opcoes', background='#f0f8ff')  # Azul claro para itens com opções
        self.tabela_itens.tag_configure('sem_opcoes', background='#ffffff')  # Branco para itens sem opções
        
        # Configurar scrollbar
        self.tabela_itens.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tabela_itens.yview)
        
        # Configurar o evento de duplo clique para expandir/recolher as opções
        self.tabela_itens.bind("<Double-1>", self._alternar_exibicao_opcoes)
        
        # Empacotar a tabela
        self.tabela_itens.pack(fill="both", expand=True)
        
        # Preencher a tabela com os itens do pedido
        self.preencher_tabela_itens()
    
    def preencher_tabela_itens(self):
        """
        Preenche a tabela com os itens do pedido atual, incluindo opções
        """
        # Verificar se a tabela existe
        if not hasattr(self, 'tabela_itens'):
            return
        
        # Limpar a tabela
        for item in self.tabela_itens.get_children():
            self.tabela_itens.delete(item)
        
        # Se não houver pedido atual, não há itens para mostrar
        if not self.pedido_atual or not self.itens_pedido:
            return
            
        # Dicionário para armazenar os itens e suas opções
        itens_com_opcoes = {}
        
        # Primeiro, organizar os itens e suas opções
        for item in self.itens_pedido:
            item_id = str(item['id'])
            itens_com_opcoes[item_id] = {
                'dados': item,
                'opcoes': item.get('opcoes', [])
            }
        
        # Agora, percorrer os itens e adicionar à tabela
        for item_id, dados in itens_com_opcoes.items():
            item = dados['dados']
            
            # Formatar valores monetários
            valor_unitario = float(item['valor_unitario'])
            preco_adicional = float(item.get('preco_adicional', 0))
            
            # Calcular valor unitário total (incluindo opções)
            valor_unitario_total = valor_unitario + preco_adicional
            
            # Calcular subtotal
            subtotal = valor_unitario_total * int(item['quantidade'])
            
            # Formatar para exibição
            valor_unitario_fmt = f"R$ {valor_unitario_total:.2f}".replace('.', ',')
            subtotal_fmt = f"R$ {subtotal:.2f}".replace('.', ',')
            
            # Verificar se o item tem opções para adicionar o sinal de +
            # Tenta obter o nome do produto de vários campos possíveis
            nome_produto = None
            for campo in ['nome_produto', 'produto_nome', 'nome']:
                if campo in item and item[campo]:
                    nome_produto = item[campo]
                    break
            
            if not nome_produto:
                # Se não encontrou o nome, imprimir os campos disponíveis para debug
                print(f"Campos disponíveis no item: {list(item.keys())}")
                nome_produto = 'Produto sem nome'
                
            tem_opcoes = bool(dados['opcoes'])
            
            if tem_opcoes and not nome_produto.endswith(' +'):
                nome_produto = f"{nome_produto} +"
            
            # Inserir o item principal
            item_tree = self.tabela_itens.insert(
                "", 
                "end", 
                iid=item_id,
                values=(
                    item_id,
                    nome_produto,
                    item['quantidade'],
                    valor_unitario_fmt,
                    subtotal_fmt
                ),
                tags=('com_opcoes' if tem_opcoes else 'sem_opcoes',)
            )
            
            # Adicionar as opções como itens filhos, se houver
            if tem_opcoes:
                for opcao in dados['opcoes']:
                    # Obter o nome da opção
                    nome_opcao = opcao.get('nome', '')
                    
                    # Se não tiver nome, tentar obter do banco de dados
                    if not nome_opcao and 'id' in opcao:
                        try:
                            from src.controllers.opcoes_controller import OpcoesController
                            from src.db.database import DatabaseConnection
                            
                            # Criar conexão com o banco e controller
                            db_connection = DatabaseConnection().get_connection()
                            opcoes_controller = OpcoesController(db_connection=db_connection)
                            
                            # Buscar a opção completa
                            opcao_completa = opcoes_controller.obter_item_opcao(opcao['id'])
                            
                            # Se encontrou, usar o nome
                            if opcao_completa and 'nome' in opcao_completa:
                                nome_opcao = opcao_completa['nome']
                        except Exception as e:
                            print(f"Erro ao buscar nome da opção: {e}")
                    
                    # Se ainda não tiver nome, usar o nome padrão
                    if not nome_opcao:
                        nome_opcao = "arroz"
                    
                    self.tabela_itens.insert(
                        item_id, 
                        "end", 
                        values=(
                            "",  # ID vazio para opções
                            f"  → {nome_opcao}",
                            "",  # Quantidade vazia
                            f"+R$ {float(opcao.get('preco_adicional', 0)):.2f}".replace('.', ','),
                            ""   # Subtotal vazio
                        ),
                        tags=('opcao_item',)
                    )
                
                # Inicialmente, as opções estarão recolhidas
                self.tabela_itens.item(item_id, open=False)
        
        # O evento de duplo clique já está configurado no método criar_tabela_itens
    
    def _alternar_exibicao_opcoes(self, event):
        """Alterna a exibição das opções de um item ao clicar duas vezes"""
        # Identificar o item clicado
        item = self.tabela_itens.identify_row(event.y)
        if not item:
            return
            
        # Verificar se é um item que tem opções
        if 'tem_opcoes' in self.tabela_itens.item(item, 'tags'):
            # Alternar entre aberto e fechado
            aberto = self.tabela_itens.item(item, 'open')
            self.tabela_itens.item(item, open=not aberto)
            
            # Se estiver abrindo, garantir que as opções estão visíveis
            if not aberto:
                # Rolar até o item para garantir que está visível
                self.tabela_itens.see(item)
    
    def criar_formulario_item(self, parent):
        """Cria o formulário para adicionar novos itens ao pedido"""
        # Frame para o formulário
        form_frame = tk.Frame(parent, bg=CORES['fundo_conteudo'], bd=1, relief="solid")
        form_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Frame interno com padding
        interno_frame = tk.Frame(form_frame, bg=CORES['fundo_conteudo'], padx=20, pady=20)
        interno_frame.pack(fill="both", expand=True)
        
        # Produto
        tk.Label(
            interno_frame, 
            text="Produto:", 
            font=FONTES['normal'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).pack(anchor="w", pady=(0, 5))
        
        # Combobox para seleção de produto
        self.produto_var = tk.StringVar()
        self.combo_produtos = ttk.Combobox(
            interno_frame, 
            textvariable=self.produto_var,
            state="readonly",
            font=FONTES['normal'],
            height=10
        )
        
        # Preencher opções de produtos
        produtos_opcoes = [f"{p['nome']} - R$ {p['preco']:.2f}" for p in self.produtos]
        self.combo_produtos['values'] = produtos_opcoes
        
        if produtos_opcoes:
            self.combo_produtos.current(0)
            
        self.combo_produtos.pack(fill="x", pady=(0, 15))
        
        # Quantidade
        tk.Label(
            interno_frame, 
            text="Quantidade:", 
            font=FONTES['normal'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).pack(anchor="w", pady=(0, 5))
        
        # Frame para quantidade com botões + e -
        qtd_frame = tk.Frame(interno_frame, bg=CORES['fundo_conteudo'])
        qtd_frame.pack(fill="x", pady=(0, 15))
        
        # Botão -
        tk.Button(
            qtd_frame, 
            text="-", 
            font=FONTES['subtitulo'],
            bg=CORES['primaria'],
            fg=CORES['texto_claro'],
            bd=0,
            width=3,
            relief='flat',
            cursor='hand2',
            command=lambda: self.alterar_quantidade(-1)
        ).pack(side="left")
        
        # Campo de quantidade
        self.quantidade_var = tk.StringVar(value="1")
        self.quantidade_entry = ttk.Entry(
            qtd_frame, 
            textvariable=self.quantidade_var,
            font=FONTES['normal'],
            width=5,
            justify="center"
        )
        self.quantidade_entry.pack(side="left", padx=10)
        
        # Botão +
        tk.Button(
            qtd_frame, 
            text="+", 
            font=FONTES['subtitulo'],
            bg=CORES['primaria'],
            fg=CORES['texto_claro'],
            bd=0,
            width=3,
            relief='flat',
            cursor='hand2',
            command=lambda: self.alterar_quantidade(1)
        ).pack(side="left")
        
        # Observações
        tk.Label(
            interno_frame, 
            text="Observações:", 
            font=FONTES['normal'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).pack(anchor="w", pady=(0, 5))
        
        # Campo de observações
        self.observacoes_var = tk.StringVar()
        self.observacoes_entry = ttk.Entry(
            interno_frame, 
            textvariable=self.observacoes_var,
            font=FONTES['normal']
        )
        self.observacoes_entry.pack(fill="x", pady=(0, 20))
        
        # Botão para adicionar item
        tk.Button(
            interno_frame, 
            text="ADICIONAR ITEM", 
            font=FONTES['normal'],
            bg=CORES['destaque'],
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2',
            command=self.adicionar_item
        ).pack(fill="x")
    
    def alterar_quantidade(self, delta):
        """Altera a quantidade no campo de quantidade"""
        try:
            # Obter valor atual
            valor_atual = int(self.quantidade_var.get())
            
            # Calcular novo valor (mínimo 1)
            novo_valor = max(1, valor_atual + delta)
            
            # Atualizar campo
            self.quantidade_var.set(str(novo_valor))
        except ValueError:
            # Se não for um número válido, definir como 1
            self.quantidade_var.set("1")
            return
                
        # Obter os dados do produto selecionado
            valores = self.tabela_produtos.item(item_selecionado[0], 'values')
            if not valores or len(valores) < 2:  # Verifica se há valores suficientes
                messagebox.showerror("Erro", "Dados do produto inválidos!")
                return
                
            # Encontrar o produto completo na lista de produtos
            produto_id = int(valores[0])  # Assumindo que o ID está na primeira coluna
            produto = None
            
            for p in self.produtos:
                if p['id'] == produto_id:
                    produto = p
                    break
                    
            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado!")
                return
            
            # Obter a quantidade
            try:
                if not hasattr(self, 'quantidade_var'):
                    self.quantidade_var = tk.StringVar(value="1")
                    
                quantidade = int(self.quantidade_var.get())
                if quantidade <= 0:
                    raise ValueError("Quantidade deve ser maior que zero")
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida!")
                return
            
            # Obter o ID do usuário logado, se disponível
            usuario_id = None
            if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                usuario_id = self.controller.usuario.id
            
            # Verificar se o produto tem opções
            if hasattr(produto, 'opcoes') and produto.opcoes:
                # Se o produto tiver opções, mostrar a janela de opções
                self._mostrar_opcoes_produto(produto, quantidade, usuario_id)
            else:
                # Se não tiver opções, adicionar diretamente
                self._adicionar_item_sem_opcoes(produto, quantidade, usuario_id)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")
            import traceback
            traceback.print_exc()

    def criar_novo_pedido(self):
        """Cria um novo pedido para a mesa atual usando o controller"""
        try:
            if not hasattr(self, 'mesa') or not self.mesa:
                messagebox.showerror("Erro", "Nenhuma mesa selecionada!")
                return False
                
            # O controlador já atualiza o status da mesa automaticamente ao criar o pedido
            
            # Obter o ID do usuário logado, se disponível
            usuario_id = None
            if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                usuario_id = self.controller.usuario.id
            
            # Chamar o método do controller para criar o pedido
            pedido = self.controller_mesas.criar_novo_pedido(self.mesa['id'], usuario_id)
            
            if not pedido:
                messagebox.showerror("Erro", "Não foi possível criar o pedido.")
                return False
            
            # Atualizar o pedido atual com os dados retornados pelo controller
            self.pedido_atual = pedido
            
            # Recarregar pedidos
            self.carregar_pedidos()
            
            # Atualizar a interface
            self.atualizar_interface()
            
            return True
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar novo pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def formatar_data(self, data):
        """Formata uma data para exibição"""
        if not data:
            return ""
        
        # Se for uma string, converter para datetime
        if isinstance(data, str):
            try:
                # Tentar diferentes formatos de data
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                    try:
                        data = datetime.datetime.strptime(data, fmt)
                        break
                    except ValueError:
                        continue
            except Exception:
                return data  # Retornar a string original se não conseguir converter
        
        # Formatar a data
        try:
            return data.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return str(data)
    
    def finalizar_pedido(self):
        """
        Finaliza o pedido atual, mantendo o histórico de itens e opções
        """
        if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
            messagebox.showinfo("Aviso", "Não há pedido aberto para finalizar!")
            return
        
        # Verificar se existem itens no pedido
        if not hasattr(self, 'itens_pedido') or not self.itens_pedido:
            messagebox.showinfo("Aviso", "Adicione itens ao pedido antes de finalizar!")
            return
        
        # Confirmar finalização
        if not messagebox.askyesno("Confirmar", "Deseja finalizar esta venda?"):
            return
        
        try:
            # Verificar se deve liberar a mesa
            liberar_mesa = False
            if hasattr(self, 'mesa') and self.mesa:
                liberar_mesa = messagebox.askyesno(
                    "Liberar Mesa", 
                    f"Deseja liberar a mesa {self.mesa.get('numero', '')} após finalizar o pedido?"
                )
            
            # Chamar o método do controller para finalizar o pedido
            pedido_atualizado = self.controller_mesas.finalizar_pedido(
                pedido_id=self.pedido_atual['id'],
                mesa_id=self.pedido_atual.get('mesa_id'),
                liberar_mesa=liberar_mesa
            )
            
            if not pedido_atualizado:
                messagebox.showinfo("Aviso", "Este pedido já foi finalizado anteriormente.")
                return
            
            # Atualizar o pedido atual com os dados retornados pelo controller
            self.pedido_atual = pedido_atualizado
            
            # Recarregar pedidos para garantir que os dados estejam atualizados
            self.carregar_pedidos()
            
            # Atualizar interface
            self.atualizar_interface()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", "Pedido finalizado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def editar_item_selecionado(self, event):
        """Seleciona o item na tabela e exibe as opções para edição"""
        # Obter o item clicado
        item = self.tabela_itens.identify_row(event.y)
        if not item:
            return
            
        # Obter o item pai (se for uma opção, o pai é o item principal)
        parent = self.tabela_itens.parent(item)
        
        # Se não for um item raiz (é uma opção), usar o pai
        if parent:
            item = parent
            
        # Obter os dados do item selecionado
        item_data = self.tabela_itens.item(item, 'values')
        if not item_data or len(item_data) < 1:
            return
            
        # Encontrar o item correspondente na lista de itens do pedido
        item_id = int(item_data[0])  # O ID está na primeira coluna
        
        # Procurar o item na lista de itens do pedido
        for item_pedido in self.itens_pedido:
            if item_pedido.get('id') == item_id:
                # Chamar o método para mostrar as opções do item
                self._mostrar_opcoes_item(item_pedido)
                return
                
        # Se chegou aqui, não encontrou o item
        messagebox.showinfo("Aviso", "Item não encontrado no pedido atual.")
            
    def remover_item_selecionado(self):
        """Remove o item selecionado da tabela"""
        # Obter o item selecionado
        selecao = self.tabela_itens.selection()
        if not selecao:
            messagebox.showinfo("Aviso", "Selecione um item para remover")
            return
            
        # Obter os dados do item selecionado
        item_id = self.tabela_itens.item(selecao)['values'][0]
        
        # Perguntar se deseja remover o item
        resposta = messagebox.askyesno(
            "Confirmar", 
            "Deseja remover este item do pedido?"
        )
        
        if resposta:
            self.remover_item(item_id)
            
    def cancelar_pedido(self):
        """
        Cancela o pedido atual, marcando-o como CANCELADO no banco de dados e liberando a mesa
        """
        # Verificações iniciais
        if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
            messagebox.showinfo("Aviso", "Não há pedido aberto para cancelar")
            return
            
        if not hasattr(self, 'mesa') or not self.mesa:
            messagebox.showerror("Erro", "Mesa não identificada")
            return
            
        # Mensagem de confirmação
        mensagem = "Deseja cancelar este pedido e liberar a mesa?"
        if hasattr(self, 'itens_pedido') and self.itens_pedido:
            mensagem = "O pedido contém itens. " + mensagem
            
        if not messagebox.askyesno("Confirmar Cancelamento", mensagem):
            return
            
        try:
            # Chamar o método do controller para cancelar o pedido
            # O controller já tem acesso ao pedido atual e à mesa
            sucesso, mensagem = self.controller_mesas.cancelar_pedido()
            
            if sucesso:
                # Atualizar estado local
                self.pedido_atual = None
                if hasattr(self, 'itens_pedido'):
                    self.itens_pedido = []
                
                # Mostrar mensagem de sucesso
                messagebox.showinfo("Sucesso", mensagem)
                
                # Atualizar a interface após um pequeno atraso
                self.parent.after(1000, self.atualizar_apos_cancelamento)
            else:
                # Mostrar mensagem de erro
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar o pedido: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def atualizar_apos_cancelamento(self):
        """Atualiza a interface após o cancelamento do pedido e retorna para a tela de mesas"""
        try:
            # Recarregar os dados
            self.carregar_pedidos()
            self.atualizar_interface()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", "Pedido cancelado e mesa liberada com sucesso!")
            
            # Voltar para a tela de mesas após um pequeno atraso para garantir que a mensagem seja exibida
            self.parent.after(500, self.voltar_para_mesas)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar a interface: {str(e)}")
            # Mesmo em caso de erro, tente voltar para a tela de mesas
            self.parent.after(500, self.voltar_para_mesas)
    
    def remover_item(self, item_id):
        """
        Remove um item do pedido, incluindo suas opções associadas
        
        Args:
            item_id: ID do item a ser removido
        """
        if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
            messagebox.showinfo("Aviso", "Nenhum pedido em andamento")
            return
            
        try:
            # Chamar o método do controller para remover o item
            sucesso = self.controller_mesas.remover_item_do_pedido(
                item_id=item_id,
                pedido_id=self.pedido_atual['id']
            )
            
            if sucesso:
                # Recarregar dados
                self.carregar_pedidos()
                
                # Atualizar interface
                self.atualizar_interface()
                
                # Mensagem de sucesso
                messagebox.showinfo("Sucesso", "Item removido com sucesso!")
            else:
                messagebox.showerror("Erro", "Item não encontrado no pedido")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover item: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def atualizar_interface(self):
        """Atualiza a interface após mudanças nos dados"""
        # Atualizar tabela de itens
        self.preencher_tabela_itens()
        
        # Atualizar informações do pedido
        if hasattr(self, 'total_label') and self.pedido_atual:
            self.total_label.config(text=f"R$ {self.pedido_atual['total']:.2f}".replace('.', ','))
    
    
    def voltar_para_mesas(self):
        """Volta para a visualização de mesas"""
        # Ocultar este módulo
        self.frame.pack_forget()
        
        # Destruir este frame para liberar memória
        self.frame.destroy()
        
        # Importar o módulo de visualização de mesas
        from src.views.modulos.mesas.visualizar_module import VisualizarMesasModule
        
        # Criar uma nova instância do módulo de visualização de mesas
        visualizar_module = VisualizarMesasModule(self.parent, self.controller, self.db_connection)
        
        # Mostrar o módulo de visualização de mesas
        visualizar_module.frame.pack(fill="both", expand=True)
    
    def show(self):
        """Mostra o módulo"""
        self.frame.pack(fill="both", expand=True)
        
    # As funções _remover_do_carrinho e _limpar_carrinho foram substituídas por remover_item_selecionado e limpar_pedido_atual
            
    def _buscar_produtos(self):
        """Busca produtos pelo texto digitado"""
        try:
            termo = self.busca_entry.get().strip()
            
            # Usar o controller para buscar os produtos
            produtos = self.controller_mesas.buscar_produtos(termo)
            
            # Atualizar a tabela com os produtos encontrados
            self.preencher_tabela_produtos(produtos)
            
        except Exception as e:
            print(f"Erro ao buscar produtos: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao buscar produtos: {str(e)}")
    
    def _filtrar_produtos_por_tipo(self, tipo):
        """Filtra produtos por tipo"""
        # Se não houver produtos carregados, não fazer nada
        if not hasattr(self, 'produtos') or not self.produtos:
            return
            
        # Converter para minúsculas para comparação case-insensitive
        tipo_busca = tipo.lower()
        
        # Filtrar produtos pelo tipo
        produtos_filtrados = [p for p in self.produtos 
                            if p.get('tipo', '').lower() == tipo_busca]
        
        # Atualizar a tabela com os produtos filtrados
        self.preencher_tabela_produtos(produtos_filtrados)
            

    def _mostrar_menu_contexto_produto(self, event):
        """Exibe o menu de contexto para o produto selecionado"""
        # Identificar o item clicado
        item = self.tabela_produtos.identify_row(event.y)
        if item:
            # Selecionar o item clicado
            self.tabela_produtos.selection_set(item)
            # Exibir o menu de contexto
            self.menu_contexto_produto.post(event.x_root, event.y_root)
    
    def _mostrar_opcoes_item(self, item_pedido):
        """Exibe as opções de um item do pedido
        
        Args:
            item_pedido (dict): Dicionário com as informações do item do pedido
        """
        # Verificar se o item tem opções antes de criar a janela
        try:
            from controllers.opcoes_controller import OpcoesController
            
            # Obter o ID do produto a partir do item do pedido
            produto_id = item_pedido['produto_id']
            
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
                
            # Inicializar a lista de opções
            opcoes = []
            
            # Verificar se o item tem opções
            try:
                grupos_opcoes = opcoes_controller.listar_opcoes_por_produto(produto_id)
                
                if not grupos_opcoes:
                    messagebox.showinfo("Informação", "Este item não possui opções disponíveis.")
                    return
                    
                # Extrair todas as opções de todos os grupos
                for grupo_id, grupo_info in grupos_opcoes.items():
                    if 'itens' in grupo_info and grupo_info['itens']:
                        for item in grupo_info['itens']:
                            # Criar uma cópia do item para não modificar o original
                            item_copy = item.copy()
                            # Adicionar informações do grupo ao item
                            item_copy['grupo_nome'] = grupo_info.get('nome', 'Sem Grupo')
                            item_copy['grupo_obrigatorio'] = grupo_info.get('obrigatorio', False)
                            opcoes.append(item_copy)
                
                if not opcoes:
                    messagebox.showinfo("Informação", "Nenhuma opção disponível para este item.")
                    return
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
                print(f"Erro ao carregar opções: {str(e)}")
                import traceback
                traceback.print_exc()
                return
                
            # Criar uma janela para exibir as opções
            janela_opcoes = tk.Toplevel(self.parent)  # Usar self.parent em vez de self.window
            janela_opcoes.title(f"Opções do Item #{item_pedido.get('id', '')}")
            janela_opcoes.geometry("500x400")
            janela_opcoes.resizable(False, False)
            
            # Centralizar a janela
            largura_janela = 500
            altura_janela = 400
            largura_tela = janela_opcoes.winfo_screenwidth()
            altura_tela = janela_opcoes.winfo_screenheight()
            pos_x = (largura_tela // 2) - (largura_janela // 2)
            pos_y = (altura_tela // 2) - (altura_janela // 2)
            janela_opcoes.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
            
            # Frame principal
            main_frame = tk.Frame(janela_opcoes, bg=CORES['fundo'], padx=20, pady=20)
            main_frame.pack(fill="both", expand=True)
            
            # Título
            tk.Label(
                main_frame,
                text=f"Opções do Item: {item_pedido.get('nome_produto', 'Item')}",
                font=FONTES['subtitulo'],
                bg=CORES['fundo'],
                fg=CORES['texto']
            ).pack(anchor="w", pady=(0, 20))
            
            # Lista de opções
            opcoes_frame = tk.Frame(main_frame, bg=CORES['fundo'])
            opcoes_frame.pack(fill="both", expand=True)
            
            # Adicionar opções existentes já selecionadas
            opcoes_selecionadas = {}
            
            if 'opcoes' in item_pedido and item_pedido['opcoes']:
                for opcao in item_pedido['opcoes']:
                    if isinstance(opcao, dict) and 'id' in opcao:
                        opcoes_selecionadas[opcao['id']] = opcao
            
            # Criar checkboxes para cada opção
            for opcao in opcoes:
                opcao_id = opcao.get('id')
                if not opcao_id:
                    continue
                    
                var = tk.BooleanVar(value=opcao_id in opcoes_selecionadas)
                
                frame_opcao = tk.Frame(opcoes_frame, bg=CORES['fundo'], pady=5)
                frame_opcao.pack(fill="x", pady=2)
                
                # Nome do grupo como título (se for diferente do anterior)
                if 'grupo_nome' in opcao and (not hasattr(self, '_ultimo_grupo') or self._ultimo_grupo != opcao['grupo_nome']):
                    lbl_grupo = tk.Label(
                        opcoes_frame,
                        text=opcao['grupo_nome'],
                        font=FONTES['subtitulo'],
                        bg=CORES['fundo'],
                        fg=CORES['texto'],
                        anchor="w"
                    )
                    lbl_grupo.pack(fill="x", pady=(10, 5))
                    self._ultimo_grupo = opcao['grupo_nome']
                
                # Checkbox
                cb = tk.Checkbutton(
                    frame_opcao,
                    text=f"{opcao.get('nome', 'Opção')} (+R$ {float(opcao.get('preco_adicional', 0)):.2f})",
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    bg=CORES['fundo'],
                    fg=CORES['texto'],
                    selectcolor=CORES['fundo'],
                    activebackground=CORES['fundo'],
                    activeforeground=CORES['texto'],
                    command=lambda o=opcao, v=var: self._atualizar_opcao_item(item_pedido, o, v)
                )
                cb.pack(anchor="w")
                
                # Descrição da opção (se houver)
                descricao = opcao.get('descricao')
                if descricao:
                    tk.Label(
                        frame_opcao,
                        text=f"    {descricao}",
                        font=FONTES['pequena'],
                        bg=CORES['fundo'],
                        fg=CORES['texto_secundario'],
                        wraplength=400,
                        justify="left"
                    ).pack(anchor="w", padx=20)
            
            # Botão de fechar
            btn_frame = tk.Frame(main_frame, bg=CORES['fundo'], pady=10)
            btn_frame.pack(fill="x", side="bottom")
            
            tk.Button(
                btn_frame,
                text="Fechar",
                command=janela_opcoes.destroy,
                bg=CORES['primaria'],
                fg=CORES['texto_claro'],
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2'
            ).pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
            print(f"Erro ao carregar opções: {str(e)}")
    
    def atualizar_total_pedido(self):
        """Atualiza o valor total do pedido com base nos itens e opções"""
        if not hasattr(self, 'pedido_atual') or not self.pedido_atual or 'id' not in self.pedido_atual:
            return 0.0
            
        try:
            # Usar o controller para atualizar o total do pedido
            total = self.controller_mesas.atualizar_total_pedido(self.pedido_atual['id'])
            
            # Atualizar o total no pedido atual
            if self.pedido_atual:
                self.pedido_atual['total'] = total
            
            # Atualizar a interface
            if hasattr(self, 'total_valor'):
                self.total_valor.config(text=f"R$ {total:.2f}".replace('.', ','))
            
            return float(total) if total is not None else 0.0
            
        except Exception as e:
            print(f"Erro ao atualizar total do pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0.0
            
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def _atualizar_opcao_item(self, item_pedido, opcao, var):
        """Atualiza as opções de um item do pedido
        
        Args:
            item_pedido (dict): Dicionário com as informações do item do pedido
            opcao (dict): Dicionário com as informações da opção
            var (BooleanVar): Variável de controle do checkbox
        """
        try:
            # Usar o controller para atualizar a opção do item
            self.controller_mesas.atualizar_opcao_item(
                item_pedido_id=item_pedido['id'],
                opcao=opcao,
                selecionado=var.get()
            )
            
            # Atualizar a lista de itens do pedido
            self.carregar_itens_pedido(self.pedido_atual['id'])
            
            # Atualizar a tabela de itens
            self.preencher_tabela_itens()
            
            # Atualizar o total do pedido
            self.atualizar_total_pedido()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar opção: {str(e)}")
            print(f"Erro ao atualizar opção: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _mostrar_opcoes_produto(self, produto=None, quantidade=1, usuario_id=None):
        """
        Exibe as opções disponíveis para o produto selecionado
        
        Args:
            produto: Dicionário com os dados do produto
            quantidade: Quantidade do item
            usuario_id: ID do usuário logado (opcional)
        """
        if produto is None:
            # Obter o item selecionado se o produto não foi passado
            selecionado = self.tabela_produtos.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um produto para adicionar opções.")
                return
                
            # Obter os dados do produto selecionado
            item = self.tabela_produtos.item(selecionado[0])
            valores = item['values']
            produto_id = valores[0]
            
            # Encontrar o produto na lista
            produto = None
            for p in self.produtos:
                if str(p['id']) == str(produto_id):
                    produto = p
                    break
        
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return
            
        produto_id = produto['id']
        
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
            grupos_opcoes = opcoes_controller.listar_grupos_por_produto(produto_id)
            
            if not grupos_opcoes:
                messagebox.showinfo("Informação", "Este produto não possui opções configuradas.")
                return
                
            # Para cada grupo, buscar os itens de opção
            for grupo in grupos_opcoes:
                grupo['itens'] = opcoes_controller.listar_itens_por_grupo(grupo['id'], ativo=True)
            
            # Criar janela de opções
            self.janela_opcoes = tk.Toplevel(self.parent)
            self.janela_opcoes.title(f"Opções para {produto['nome']}")
            self.janela_opcoes.geometry("400x500")
            
            # Frame principal
            frame_principal = ttk.Frame(self.janela_opcoes, padding="10")
            frame_principal.pack(fill="both", expand=True)
                
            # Dicionário para armazenar as seleções do usuário
            self.selecoes_opcoes = {}
            
            # Para cada grupo de opções
            for grupo in grupos_opcoes:
                grupo_frame = ttk.LabelFrame(frame_principal, text=grupo['nome'], padding="5")
                grupo_frame.pack(fill="x", pady=5)
                
                # Verificar se é seleção única ou múltipla
                if grupo['selecao_maxima'] == 1:
                    # Seleção única (Radiobuttons)
                    var = tk.StringVar()
                    self.selecoes_opcoes[grupo['id']] = {'var': var, 'tipo': 'unico', 'itens': grupo['itens']}
                    
                    # Se houver apenas uma opção, pré-selecionar automaticamente
                    if len(grupo['itens']) == 1:
                        var.set(str(grupo['itens'][0]['id']))
                     
                    
                    for opcao in grupo['itens']:
                        rb = ttk.Radiobutton(
                            grupo_frame,
                            text=f"{opcao['nome']} (+R$ {float(opcao['preco_adicional']):.2f})",
                            variable=var,
                            value=str(opcao['id'])
                        )
                        rb.pack(anchor="w")
                        
                        # Adicionar evento para seleção
                        def on_select(event=None, opcao_id=opcao['id'], grupo_id=grupo['id']):
                            pass
                        
                        rb.bind("<Button-1>", on_select)
                    
                    # Debug: mostrar opções disponíveis
                    # Opções disponíveis para este grupo
                else:
                    # Seleção múltipla (Checkbuttons)
                    self.selecoes_opcoes[grupo['id']] = {'var': [], 'tipo': 'multiplo', 'itens': grupo['itens']}
                    
                    for opcao in grupo['itens']:
                        var = tk.BooleanVar()
                        self.selecoes_opcoes[grupo['id']]['var'].append((var, opcao))
                        
                        cb = ttk.Checkbutton(
                            grupo_frame,
                            text=f"{opcao['nome']} (+R$ {float(opcao['preco_adicional']):.2f})",
                            variable=var
                        )
                        cb.pack(anchor="w")
                    
                    # Opções disponíveis para checkbox
            
            # Botão para confirmar as opções
            btn_confirmar = tk.Button(
                frame_principal,
                text="Confirmar Opções",
                bg=CORES['destaque'],
                fg=CORES['texto_claro'],
                padx=10,
                pady=5,
                command=lambda p=produto, q=quantidade, u=usuario_id: self._adicionar_item_com_opcoes(p, q, u)
            )
            btn_confirmar.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
            if hasattr(self, 'janela_opcoes'):
                self.janela_opcoes.destroy()
    
    def _adicionar_item_sem_opcoes(self, produto, quantidade, usuario_id=None):
        """
        Adiciona um produto sem opções ao pedido
        
        Args:
            produto: Dicionário com os dados do produto
            quantidade: Quantidade do item
            usuario_id: ID do usuário logado (opcional)
        
        Returns:
            bool: True se o item foi adicionado com sucesso, False caso contrário
        """
        try:
            # Verificar se há um pedido atual, se não, criar um
            if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
                sucesso = self.criar_novo_pedido()
                if not sucesso:
                    messagebox.showerror("Erro", "Não foi possível criar um novo pedido")
                    return False
            
            # Chamar o método do controller para adicionar o item
            sucesso, mensagem, item = self.controller_mesas.adicionar_item_mesa(
                self.mesa['id'],
                produto,
                quantidade,
                opcoes_selecionadas=None,  # Sem opções
                preco_adicional=0.0,  # Sem preço adicional
                usuario_id=usuario_id
            )
            
            if sucesso:
                # Atualizar a tabela de itens
                self.carregar_pedidos()
                return True
            else:
                messagebox.showerror("Erro", mensagem)
                return False
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _adicionar_item_com_opcoes(self, produto, quantidade, usuario_id=None):
        """
        Adiciona o produto ao pedido com as opções selecionadas
        
        Args:
            produto: Dicionário com os dados do produto
            quantidade: Quantidade do item
            usuario_id: ID do usuário logado (opcional)
        """
        opcoes_selecionadas = []
        preco_adicional = 0
        
        # Processando opções para o produto
        
        try:
            # Verificar se existem seleções feitas
            if not hasattr(self, 'selecoes_opcoes') or not self.selecoes_opcoes:
                messagebox.showwarning("Aviso", "Nenhuma opção foi selecionada.")
                return False
                
            # Processar cada grupo de opções
            for grupo_id, dados in self.selecoes_opcoes.items():
                if dados['tipo'] == 'unico':
                    # Opção única (radiobutton)
                    opcao_id = dados['var'].get()
                    # Processando seleção do radiobutton
                    
                    # Se não houver seleção e o grupo tiver apenas uma opção, selecionar automaticamente
                    if not opcao_id and 'itens' in dados and len(dados['itens']) == 1:
                        opcao_id = str(dados['itens'][0]['id'])
                        # Selecionando automaticamente a única opção disponível
                    
                    if not opcao_id:
                        # Nenhuma opção selecionada para este grupo
                        continue
                    
                    # Buscar a opção nos itens do grupo
                    encontrou = False
                    for opcao in dados.get('itens', []):
                        # Converter para string para garantir comparação correta
                        if str(opcao.get('id')) == str(opcao_id):
                            # Opção encontrada
                            opcoes_selecionadas.append({
                                'id': opcao['id'],
                                'nome': opcao.get('nome', 'Opção'),
                                'preco_adicional': float(opcao.get('preco_adicional', 0)),
                                'grupo_id': grupo_id
                            })
                            preco_adicional += float(opcao.get('preco_adicional', 0))
                            encontrou = True
                            break
                    
                    if not encontrou:
                        print(f"ERRO: Não encontrou opção com ID {opcao_id} no grupo {grupo_id}")
                        print(f"Itens disponíveis: {[{i['id']: i['nome']} for i in dados.get('itens', [])]}")
                        # Tentar novamente com uma abordagem diferente
                        for opcao in dados.get('itens', []):
                            print(f"Comparando: '{opcao_id}' com '{opcao['id']}' (tipos: {type(opcao_id)} e {type(opcao['id'])})")
                        
                        # Se não encontrou, mas temos apenas uma opção, usar essa opção
                        if len(dados.get('itens', [])) == 1:
                            opcao = dados['itens'][0]
                            print(f"Usando a única opção disponível: {opcao['nome']} (ID: {opcao['id']})")
                            opcoes_selecionadas.append({
                                'id': opcao['id'],
                                'nome': opcao.get('nome', 'Opção'),
                                'preco_adicional': float(opcao.get('preco_adicional', 0)),
                                'grupo_id': grupo_id
                            })
                            preco_adicional += float(opcao.get('preco_adicional', 0))
                        else:
                            messagebox.showwarning("Aviso", f"Não foi possível encontrar a opção selecionada no grupo {grupo_id}.")
                            return False
                            
                elif dados['tipo'] == 'multiplo':
                    # Verificar se é uma lista de tuplas (var, opcao) ou um dicionário
                    if isinstance(dados['var'], list):
                        for var, opcao in dados['var']:
                            if var.get():
                                opcoes_selecionadas.append({
                                    'id': opcao['id'],
                                    'nome': opcao.get('nome', 'Opção'),
                                    'preco_adicional': float(opcao.get('preco_adicional', 0)),
                                    'grupo_id': grupo_id
                                })
                                preco_adicional += float(opcao.get('preco_adicional', 0))
                    else:
                        # Tratar como um dicionário de opções
                        for opcao_id, var in dados['var'].items():
                            if var.get():
                                opcao = next((op for op in dados.get('itens', []) 
                                            if str(op['id']) == str(opcao_id)), None)
                                if opcao:
                                    opcoes_selecionadas.append({
                                        'id': opcao['id'],
                                        'nome': opcao.get('nome', 'Opção'),
                                        'preco_adicional': float(opcao.get('preco_adicional', 0)),
                                        'grupo_id': grupo_id
                                    })
                                    preco_adicional += float(opcao.get('preco_adicional', 0))
            
            # Usar a função do controlador para adicionar o item
            sucesso, mensagem, pedido = self.controller_mesas.adicionar_item_mesa(
                mesa_id=self.mesa['id'],
                produto=produto,
                quantidade=quantidade,
                opcoes_selecionadas=opcoes_selecionadas,
                preco_adicional=preco_adicional,
                usuario_id=usuario_id
            )
            
            if sucesso and pedido:
                # Fechar a janela de opções
                if hasattr(self, 'janela_opcoes'):
                    self.janela_opcoes.destroy()
                
                # Atualizar o pedido atual
                self.pedido_atual = pedido
                
                # Recarregar itens do pedido
                self.carregar_pedidos()
                
                # Atualizar a interface
                self.atualizar_interface()
                
                # Limpar campos do formulário
                if hasattr(self, 'quantidade_var'):
                    self.quantidade_var.set("1")
                if hasattr(self, 'observacoes_var'):
                    self.observacoes_var.set("")
                
                # Mensagem de sucesso
                messagebox.showinfo("Sucesso", mensagem or "Item adicionado com sucesso!")
                return True
            else:
                messagebox.showerror("Erro", mensagem or "Não foi possível adicionar o item ao pedido.")
                return False
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item com opções: {str(e)}")
            return False
    
    def _obter_todas_opcoes(self):
        """Obtém todas as opções disponíveis"""
        try:
            from controllers.opcoes_controller import OpcoesController
            
            # Obter a conexão com o banco de dados do controlador principal
            db_connection = getattr(self.controller, 'db_connection', None)
            if not db_connection:
                return []
                
            # Criar o controlador de opções com a conexão
            opcoes_controller = OpcoesController(db_connection=db_connection)
            
            # Obter todos os grupos de opções
            grupos = opcoes_controller.listar_grupos()
            
            # Coletar todas as opções
            todas_opcoes = []
            for grupo in grupos:
                opcoes = opcoes_controller.listar_itens_por_grupo(grupo['id'])
                todas_opcoes.extend(opcoes)
                
            return todas_opcoes
            
        except Exception as e:
            print(f"Erro ao obter opções: {str(e)}")
            return []
    
    def adicionar_item(self):
        """
        Adiciona um item ao pedido atual ou cria um novo pedido se necessário.
        
        Este método é chamado quando o usuário clica no botão de adicionar item.
        """
        try:
            # Verificar se há um produto selecionado
            selecionado = self.tabela_produtos.selection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um produto para adicionar")
                return
                
            # Obter o produto selecionado
            valores = self.tabela_produtos.item(selecionado[0])['values']
            if not valores or len(valores) < 2:  # Verifica se há valores suficientes
                messagebox.showerror("Erro", "Dados do produto inválidos!")
                return
                
            # Encontrar o produto na lista de produtos
            produto_id = int(valores[0])
            produto = None
            
            for p in self.produtos:
                if p['id'] == produto_id:
                    produto = p
                    break
                    
            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado!")
                return
            
            # Obter a quantidade
            try:
                quantidade = int(self.quantidade_var.get())
                if quantidade <= 0:
                    raise ValueError("Quantidade deve ser maior que zero")
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida!")
                return
            
            # Obter o ID do usuário logado, se disponível
            usuario_id = None
            if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                usuario_id = self.controller.usuario.id
            
            # Verificar se o produto tem opções usando o controller de opções
            grupos_opcoes = self.opcoes_controller.listar_grupos_por_produto(produto['id'])
            
            # Verificar se há grupos de opções obrigatórios
            tem_opcoes_obrigatorias = False
            for grupo in grupos_opcoes:
                if grupo.get('obrigatorio', False):
                    tem_opcoes_obrigatorias = True
                    break
            
            if grupos_opcoes and len(grupos_opcoes) > 0 and tem_opcoes_obrigatorias:
                # Se o produto tiver opções obrigatórias, mostrar a janela de opções
                self._mostrar_opcoes_produto(produto, quantidade, usuario_id)
                return True
            else:
                # Se não tiver opções ou não tiver opções obrigatórias, adicionar diretamente
                return self._adicionar_item_sem_opcoes(produto, quantidade, usuario_id)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _calcular_total_com_desconto(self, *args):
        """Calcula o total com desconto quando o valor do desconto é alterado"""
        if not hasattr(self, 'pedido_atual') or not self.pedido_atual or 'id' not in self.pedido_atual:
            return
            
        try:
            # Obter o valor do desconto (converter vírgula para ponto)
            desconto_texto = self.desconto_var.get().replace(',', '.')
            valor_desconto = float(desconto_texto) if desconto_texto else 0
            
            # Usar o controlador para calcular o desconto e obter os valores atualizados
            subtotal, total = self.controller_mesas.calcular_desconto(
                self.pedido_atual['id'],
                valor_desconto
            )
            
            # Atualizar os labels com os valores formatados
            self.subtotal_valor.config(text=f"R$ {subtotal:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
            self.total_valor.config(text=f"R$ {total:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
            
            # Forçar atualização da interface
            self.update_idletasks()
            
        except ValueError:
            # Se o valor do desconto não for um número válido, não faz nada
            pass
        except Exception as e:
            print(f"Erro ao calcular desconto: {str(e)}")
            import traceback
            traceback.print_exc()
            
    # Função calcular_total removida - não estava sendo utilizada
