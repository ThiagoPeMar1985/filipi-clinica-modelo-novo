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
from src.utils.impressao import GerenciadorImpressao
from src.controllers.config_controller import ConfigController

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
        
        # Lista para armazenar itens adicionados na sessão atual
        self.itens_adicionados_na_sessao = []
        # Backup dos itens originais para possível cancelamento
        self.itens_originais = []
        
        # Checkbox para ativar/desativar a taxa de serviço
        # Verificar se o pedido atual tem informação sobre a taxa de serviço
        taxa_ativada = True  # Valor padrão é ativada
        if self.pedido_atual and 'taxa_servico' in self.pedido_atual:
            # Converter para booleano (0 = False, qualquer outro valor = True)
            taxa_ativada = bool(self.pedido_atual.get('taxa_servico', 1))
        
        self.taxa_servico_var = tk.BooleanVar(value=taxa_ativada)
        
        # Inicializa variáveis de controle
        self.quantidade_var = tk.StringVar(value="1")
        self.desconto_var = tk.StringVar(value="0.00")
        self.selecoes_opcoes = {}
        
        # Referências para os botões que serão manipulados
        self.botao_voltar = None
        self.botao_finalizar = None
        self.botao_cancelar = None
        self.botao_confirmar = None
        
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
    
    def carregar_pedidos(self, manter_itens_sessao=False):
        """
        Carrega os pedidos da mesa atual usando o controller
        
        Args:
            manter_itens_sessao: Se True, mantém os itens adicionados na sessão
        """
        try:
            # Se precisar manter os itens da sessão, fazer backup
            itens_sessao_backup = None
            if manter_itens_sessao and hasattr(self, 'itens_adicionados_na_sessao'):
                itens_sessao_backup = self.itens_adicionados_na_sessao.copy()

            if self.mesa and self.controller_mesas.carregar_pedidos(self.mesa['id']):
                self.pedidos = self.controller_mesas.pedidos
                self.pedido_atual = self.controller_mesas.pedido_atual
                
                # Fazer backup dos itens originais se for a primeira vez
                if not manter_itens_sessao:
                    self.itens_originais = self.controller_mesas.itens_pedido.copy()
                
                # Restaurar o backup dos itens da sessão, se existir
                if manter_itens_sessao and itens_sessao_backup:
                    self.itens_adicionados_na_sessao = itens_sessao_backup
                    
                    # Atualizar também no controller para garantir consistência
                    if hasattr(self.controller_mesas, 'itens_adicionados_na_sessao'):
                        self.controller_mesas.itens_adicionados_na_sessao = itens_sessao_backup.copy()
                
                # Usar os itens do pedido do controller
                self.itens_pedido = self.controller_mesas.itens_pedido
                
                # Preencher tabela de itens e atualizar total
                self.preencher_tabela_itens()
                self.atualizar_total_pedido()
                return True
            return False
        except Exception as e:
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
        
        # Frame para agrupar os botões de navegação
        botoes_frame = tk.Frame(titulo_frame, bg=CORES['fundo'])
        botoes_frame.pack(side="left", padx=(0, 15))
        
        # Botão de voltar
        self.botao_voltar = tk.Button(
            botoes_frame,
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
        self.botao_voltar.pack(side="left")
        
        # Botão de cancelar alteração (inicialmente oculto)
        self.botao_cancelar = tk.Button(
            botoes_frame,
            text="✕ Cancelar Alteração",
            bg=CORES["alerta"],
            fg=CORES["texto_claro"],
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self.cancelar_alteracoes
        )
        self.botao_cancelar.pack(side="left")
        self.botao_cancelar.pack_forget()  # Inicialmente oculto
        
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
            bg=CORES["terciaria"],
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
        
        # Taxa de Serviço (10%)
        taxa_frame = ttk.Frame(resumo_grid)
        taxa_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        
        # Checkbox para ativar/desativar a taxa de serviço
        self.taxa_check = ttk.Checkbutton(
            taxa_frame, 
            text="Taxa de Serviço (10%)", 
            variable=self.taxa_servico_var,
            command=self._atualizar_taxa_servico
        )
        self.taxa_check.pack(side="left")
        
        # Label para exibir o valor da taxa de serviço
        self.taxa_valor = ttk.Label(taxa_frame, text="R$ 0,00", font=FONTES['pequena'])
        self.taxa_valor.pack(side="right")
        
        # Separador antes do total
        ttk.Separator(resumo_grid, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Total com destaque
        ttk.Label(resumo_grid, text="TOTAL:", font=FONTES['subtitulo']).grid(row=3, column=0, sticky="w", pady=2)
        self.total_valor = ttk.Label(resumo_grid, text="R$ 0,00", font=FONTES['subtitulo'])
        self.total_valor.grid(row=3, column=1, sticky="e", pady=2)
        
        # Frame para agrupar os botões de ação
        botoes_acao_frame = tk.Frame(carrinho_frame, bg=CORES['fundo'])
        botoes_acao_frame.pack(fill="x", pady=5)
        
        # Botão de finalizar venda com tamanho maior e mais destaque
        self.botao_finalizar = tk.Button(
            botoes_acao_frame, 
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
        self.botao_finalizar.pack(fill="x", pady=5)
        
        # Botão de confirmar (inicialmente oculto) - mesmo estilo do finalizar venda
        self.botao_confirmar = tk.Button(
            botoes_acao_frame, 
            text="✓ CONFIRMAR", 
            bg=CORES["sucesso"],
            fg=CORES["texto_claro"],
            font=FONTES['subtitulo'],
            bd=0,
            padx=20,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=self.confirmar_alteracoes
        )
        # Usar pack com fill="x" para garantir que ocupe toda a largura, igual ao botão finalizar
        self.botao_confirmar.pack(fill="x", pady=5)
        self.botao_confirmar.pack_forget()  # Inicialmente oculto
    
    def criar_tabela_produtos(self, parent):
        """Cria a tabela de produtos disponíveis"""
        # Criar frame para a tabela com scrollbar - sem bordas
        tabela_container = tk.Frame(parent, bg=CORES['fundo_conteudo'], bd=0, highlightthickness=0)
        tabela_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabela_container)
        scrollbar.pack(side="right", fill="y")
        
        # Colunas da tabela - usar as mesmas do módulo de vendas
        colunas = ("Código", "Produto", "Preço", "Estoque")
        
        # Configurar estilo para a Treeview
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        style.configure("Treeview", borderwidth=0, relief="flat")
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe", "border": "0"})])
        
        # Criar Treeview
        self.tabela_produtos = ttk.Treeview(
            tabela_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=10,
            style="Treeview",
            padding=0
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
        # Criar frame para a tabela com scrollbar - sem bordas
        tabela_container = tk.Frame(parent, bg=CORES['fundo_conteudo'], bd=0, highlightthickness=0)
        tabela_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabela_container)
        scrollbar.pack(side="right", fill="y")
        
        # Colunas da tabela
        colunas = ("id", "produto", "quantidade", "valor_unit", "valor_total", "hora")
        
        # Configurar estilo para a Treeview
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        style.configure("Treeview", borderwidth=0, relief="flat")
        style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe", "border": "0"})])
        
        # Criar Treeview
        self.tabela_itens = ttk.Treeview(
            tabela_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=10,
            style="Treeview",
            padding=0
        )
        
        # Configurar cabeçalhos
        self.tabela_itens.heading("id", text="ID")
        self.tabela_itens.heading("produto", text="Produto")
        self.tabela_itens.heading("quantidade", text="Qtd")
        self.tabela_itens.heading("valor_unit", text="Valor Unit.")
        self.tabela_itens.heading("valor_total", text="Valor Total")
        self.tabela_itens.heading("hora", text="Hora")

        
        # Configurar larguras das colunas
        self.tabela_itens.column("id", width=50, anchor="center")
        self.tabela_itens.column("produto", width=190, anchor="w")
        self.tabela_itens.column("quantidade", width=50, anchor="center")
        self.tabela_itens.column("valor_unit", width=90, anchor="e")
        self.tabela_itens.column("valor_total", width=90, anchor="e")
        self.tabela_itens.column("hora", width=60, anchor="center")

        
        # Configurar tags para estilização
        try:
            self.tabela_itens.tag_configure('opcao_item', background='#f9f9f9')   # Cinza claro para opções
            self.tabela_itens.tag_configure('com_opcoes', background='#f0f8ff')  # Azul claro para itens com opções
            self.tabela_itens.tag_configure('sem_opcoes', background='#ffffff')  # Branco para itens sem opções
        except Exception:
            pass
        
        # Configurar scrollbar
        self.tabela_itens.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tabela_itens.yview)
        
        # Configurar os eventos de clique simples e duplo
        self.tabela_itens.bind("<Button-1>", self._on_item_click)  # Clique simples
        self.tabela_itens.bind("<Double-1>", self._alternar_exibicao_opcoes)  # Duplo clique
        
        # Empacotar a tabela
        self.tabela_itens.pack(fill="both", expand=True)
        
        # Preencher a tabela com os itens do pedido
        self.preencher_tabela_itens()
    
    def preencher_tabela_itens(self):
        """
        Preenche a tabela com os itens do pedido atual, incluindo opções
        """
        # Método para preencher a tabela de itens
        # Verificar se a tabela existe
        if not hasattr(self, 'tabela_itens'):
            # Tabela de itens não existe, retornando
            return
        
        # Limpar a tabela
        # Limpar tabela de itens
        for item in self.tabela_itens.get_children():
            self.tabela_itens.delete(item)
        
        # Se não houver pedido atual, não há itens para mostrar
        if not self.pedido_atual or not self.itens_pedido:
            # Sem pedido atual ou itens, retornando
            return
            
        # Processando itens do pedido
        self.recalcular_total = True  # Flag to indicate total should be recalculated

            
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
            # Calculando valor unitário com adicionais
            
            # Calcular valor unitário total (incluindo opções)
            valor_unitario_total = valor_unitario + preco_adicional
            # Valor unitário total calculado
            
            # Calcular subtotal
            subtotal = valor_unitario_total * int(item['quantidade'])
            # Calculando subtotal do item

            
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
                # Se não encontrou o nome, usar um nome padrão
                nome_produto = 'Produto sem nome'
                
            tem_opcoes = bool(dados['opcoes'])
            
            if tem_opcoes and not nome_produto.endswith(' +'):
                nome_produto = f"{nome_produto} +"
            
            # Formatar a hora do item
            hora_item = ''
            if 'data_hora' in item and item['data_hora']:
                try:
                    # Converter para objeto datetime se for string
                    if isinstance(item['data_hora'], str):
                        from datetime import datetime
                        data_hora = datetime.strptime(item['data_hora'], '%Y-%m-%d %H:%M:%S')
                    else:
                        data_hora = item['data_hora']
                    
                    # Formatar apenas a hora:minuto
                    hora_item = data_hora.strftime('%H:%M')
                except Exception:
                    # Silently handle date formatting errors
                    pass
            
            # Definir tags do item
            tags = ['com_opcoes' if tem_opcoes else 'sem_opcoes']
            if tem_opcoes:
                tags.append('tem_opcoes')
                
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
                    subtotal_fmt,
                    hora_item
                ),
                tags=tuple(tags)
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
                        except Exception:
                            # Silently handle option name fetch errors
                            pass
                    
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
                            "",  # Subtotal vazio
                            ""   # Hora vazia para opções
                        ),
                        tags=('opcao_item',)
                    )
                
                # Inicialmente, as opções estarão recolhidas
                self.tabela_itens.item(item_id, open=False)
        
        # O evento de duplo clique já está configurado no método criar_tabela_itens
        
        # Atualizar o total do pedido se necessário
        if hasattr(self, 'recalcular_total') and self.recalcular_total:
            self.atualizar_total_pedido()
            self.recalcular_total = False
    
    def _on_item_click(self, event):
        """Trata o evento de clique simples em um item da tabela"""
        # Identificar o item clicado
        item = self.tabela_itens.identify_row(event.y)
        if not item:
            return
            
        # Verificar se é uma opção de item (filho)
        tags = self.tabela_itens.item(item, 'tags')
        if 'opcao_item' in tags:
            # Se for uma opção, não faz nada no clique simples
            return 'break'  # Interrompe a propagação do evento
            
        # Para itens principais (com ou sem opções), permite a seleção normal
    
    def _alternar_exibicao_opcoes(self, event):
        """Alterna a exibição das opções de um item ao clicar duas vezes"""
        # Identificar o item clicado
        item = self.tabela_itens.identify_row(event.y)
        if not item:
            return 'break'
            
        # Obter informações completas do item
        item_info = self.tabela_itens.item(item)
        
        # Verificar tags do item
        tags = self.tabela_itens.item(item, 'tags')
        
        # Verificar se é um item que tem opções
        if 'tem_opcoes' in tags:
            # Verificar estado atual (aberto/fechado)
            aberto = self.tabela_itens.item(item, 'open')
            
            # Se estiver fechando, apenas alterar o estado
            if aberto:
                self.tabela_itens.item(item, open=False)
                self.tabela_itens.update_idletasks()
                return 'break'  # Interrompe a propagação do evento
                
            # Se estiver abrindo, carregar as opções
            # Remover qualquer filho existente primeiro
            for filho in self.tabela_itens.get_children(item):
                self.tabela_itens.delete(filho)
            
            # Obter o ID do item
            item_id = item_info['values'][0] if 'values' in item_info and item_info['values'] else None
            if not item_id:
                return 'break'
            
            # Procurar o item na lista de itens do pedido
            item_pedido = next((ip for ip in self.itens_pedido if str(ip.get('id')) == str(item_id)), None)
            if not item_pedido:
                return 'break'
                
            opcoes = item_pedido.get('opcoes', [])
            
            # Marcar o item como aberto
            self.tabela_itens.item(item, open=True)
            
            if opcoes:
                # Adicionar cada opção como filho do item
                for opcao in opcoes:
                    nome_opcao = opcao.get('nome', 'Opção')
                    preco_adicional = float(opcao.get('preco_adicional', 0))
                    
                    try:
                        # Inserir a opção como filho do item
                        self.tabela_itens.insert(
                            item, 
                            "end", 
                            values=(
                                "",  # ID vazio para opções
                                f"  → {nome_opcao}",
                                "",  # Quantidade vazia
                                f"+R$ {preco_adicional:.2f}",
                                "",  # Subtotal vazio
                                ""   # Hora vazia para opções
                            ),
                            tags=('opcao_item',)  # Tag para estilização
                        )
                    except Exception:
                        # Silently handle insertion errors
                        pass
            else:
                # Adicionar uma mensagem indicando que não há opções
                self.tabela_itens.insert(
                    item,
                    'end',
                    values=(
                        '',
                        "  (Nenhuma opção selecionada)",
                        '', '', '', ''
                    ),
                    tags=('opcao_item',)
                )
            
            # Atualizar a interface
            self.tabela_itens.update_idletasks()
            self.tabela_itens.see(item)
            self.tabela_itens.update()
            
            return 'break'  # Interrompe a propagação do evento
            
        return 'break'  # Interrompe a propagação do evento
    
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

    def criar_novo_pedido(self, usuario_id=None):
        """
        Cria um novo pedido para a mesa atual usando o controller
        
        Args:
            usuario_id: ID do usuário que está criando o pedido (opcional). 
                      Se não informado, tenta obter do controller.
        """
        try:
            if not hasattr(self, 'mesa') or not self.mesa:
                messagebox.showerror("Erro", "Nenhuma mesa selecionada!")
                return False
            
            # O controlador já atualiza o status da mesa automaticamente ao criar o pedido
            
            # Verificar se o usuário está logado
            if usuario_id is None and hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                usuario_id = self.controller.usuario.id

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
            # Definir como True para sempre liberar a mesa após finalizar o pedido
            liberar_mesa = hasattr(self, 'mesa') and bool(self.mesa)
            
            # Calcular o total do pedido
            total = self.atualizar_total_pedido()
            
            # Importar o módulo de pagamento
            from views.modulos.pagamento.pagamento_module import PagamentoModule
            
            # Preparar os itens para pagamento, garantindo que todos tenham o campo 'tipo'
            itens_para_pagamento = []
            for item in self.itens_pedido:
                # Criar uma cópia do item para não modificar o original
                item_pagamento = item.copy()
                
                # Verificar se o item já tem o campo 'tipo'
                if 'tipo' not in item_pagamento or not item_pagamento['tipo']:
                    # Tentar obter o tipo do produto do banco de dados
                    produto_id = item_pagamento.get('produto_id')
                    if produto_id:
                        try:
                            cursor = self.db_connection.cursor(dictionary=True)
                            cursor.execute("SELECT tipo FROM produtos WHERE id = %s", (produto_id,))
                            produto = cursor.fetchone()
                            cursor.close()
                            
                            if produto and produto.get('tipo'):
                                item_pagamento['tipo'] = produto['tipo']
                            else:
                                # Tipo padrão se não encontrar
                                item_pagamento['tipo'] = 'Outros'
                        except Exception as e:
                            print(f"Erro ao obter tipo do produto: {e}")
                            item_pagamento['tipo'] = 'Outros'
                    else:
                        item_pagamento['tipo'] = 'Outros'
                
                # Garantir que o tipo seja um dos tipos padrão do sistema
                # No cadastro de produtos, os tipos já são definidos como: Cozinha, Bar, Sobremesas, Outros
                if item_pagamento['tipo'] not in ["Cozinha", "Bar", "Sobremesas", "Outros"]:
                    # Se por algum motivo o tipo não for um dos padrões, usar 'Outros'
                    print(f"Tipo de produto não reconhecido: {item_pagamento['tipo']}. Usando 'Outros' como padrão.")
                    item_pagamento['tipo'] = 'Outros'
                
                itens_para_pagamento.append(item_pagamento)
            
            # Itens preparados para pagamento
            
            # Criar uma janela para o módulo de pagamento
            pagamento_window = tk.Toplevel(self.parent)
            pagamento_window.title("Pagamento - Mesa " + str(self.mesa.get('numero', '')))
            pagamento_window.geometry("800x600")
            pagamento_window.transient(self.parent)
            pagamento_window.focus_set()
            pagamento_window.grab_set()
            
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
                self.db_connection,
                valor_total=total,
                desconto=0.0,  # Sem desconto por padrão
                callback_finalizar=lambda venda_dados, itens_venda, pagamentos: self._processar_venda_finalizada(venda_dados, itens_venda, pagamentos, liberar_mesa),
                venda_tipo='mesa',
                referencia=self.mesa.get('numero', ''),
                itens_venda=itens_para_pagamento
            )
            
            # Configurar evento para quando a janela for fechada
            pagamento_window.protocol("WM_DELETE_WINDOW", pagamento_window.destroy)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _processar_venda_finalizada(self, venda_dados, itens_venda, pagamentos, liberar_mesa):
        """
        Processa a venda finalizada com os pagamentos realizados
        
        Args:
            venda_dados: Dicionário com os dados da venda
            itens_venda: Lista de itens da venda
            pagamentos: Lista de dicionários com os dados dos pagamentos
            liberar_mesa: Se True, libera a mesa após finalizar o pedido
        """
        try:
            # Verificar estrutura e valores dos itens
            for i, item in enumerate(itens_venda):
                pass  # Processamento silencioso dos itens
            
            # Verificar pagamentos

            # Processar pagamentos (código removido para limpeza)
            # Verificar se há pagamentos
            if not pagamentos:
                messagebox.showinfo("Aviso", "Nenhum pagamento registrado!")
                return
            
            # Obter a forma de pagamento principal (a primeira da lista)
            forma_pagamento = pagamentos[0].get('forma_nome', '')
            
            # Calcular o valor total dos pagamentos
            valor_total = sum(float(p.get('valor', 0)) for p in pagamentos)
            
            # Obter o desconto (se houver)
            desconto = float(venda_dados.get('desconto', 0))
            
            # Chamar o método do controller para finalizar o pedido com os parâmetros corretos
            sucesso, mensagem = self.controller_mesas.finalizar_pedido(
                forma_pagamento=forma_pagamento,
                valor_total=valor_total,
                desconto=desconto
            )
            
            if not sucesso:
                messagebox.showinfo("Aviso", mensagem)
                return
            
            # Registrar os pagamentos usando o PagamentoController
            from controllers.pagamento_controller import PagamentoController
            pagamento_controller = PagamentoController(self.db_connection)
            
            # Registrar cada pagamento
            for pagamento in pagamentos:
                pagamento_controller.registrar_pagamento(
                    venda_id=self.pedido_atual['id'],
                    forma_pagamento=pagamento.get('forma_nome'),  # Usar forma_nome em vez de forma_pagamento
                    valor=pagamento.get('valor'),
                    observacao=pagamento.get('observacao', '')
                )
            
            # Limpar o pedido atual conforme feito no controller
            self.pedido_atual = None
            self.itens_pedido = []
            
            # Se a mesa foi liberada, voltar para a tela de mesas
            if liberar_mesa:
                # Usar o método _voltar_para_mesas em vez de voltar()
                self._voltar_para_mesas()
            else:
                # Recarregar pedidos para garantir que os dados estejam atualizados
                self.carregar_pedidos()
                
                # Atualizar interface
                self.atualizar_interface()
            

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar venda finalizada: {str(e)}")
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
            
        # Primeira mensagem de confirmação
        mensagem = "Deseja cancelar este pedido e liberar a mesa?"
        if hasattr(self, 'itens_pedido') and self.itens_pedido:
            mensagem = "O pedido contém itens. " + mensagem
            
        if not messagebox.askyesno("Confirmar Cancelamento", mensagem):
            return
        
        # Segunda mensagem de confirmação
        if not messagebox.askyesno("Confirmação Final", 
                                 "ATENÇÃO: Esta ação irá apagar TODOS os itens do pedido e liberar a mesa.\n\n"
                                 "Deseja realmente prosseguir com o cancelamento?"):
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
            
            # Voltar para a tela de mesas
            self.voltar_para_mesas()
            
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
            
        # Verificar se o item está na lista de itens adicionados na sessão
        item_na_sessao = None
        if hasattr(self, 'itens_adicionados_na_sessao'):
            for i, item in enumerate(self.itens_adicionados_na_sessao):
                if str(item.get('id')) == str(item_id):
                    item_na_sessao = self.itens_adicionados_na_sessao.pop(i)
                    break
            
        try:
            # Chamar o método do controller para remover o item
            sucesso, mensagem = self.controller_mesas.remover_item_pedido(item_id=item_id)
            
            if sucesso:
                # Se o item estava na sessão e foi removido, atualizar a lista de itens originais
                if item_na_sessao:
                    # Atualizar a lista de itens originais para refletir a remoção
                    if hasattr(self, 'itens_originais'):
                        self.itens_originais = [item for item in self.itens_originais 
                                             if str(item.get('id')) != str(item_id)]
                
                # Recarregar dados
                self.carregar_pedidos()
                
                # Atualizar interface
                self.atualizar_interface()
                
                # Verificar se ainda há itens no pedido
                if not hasattr(self, 'itens_pedido') or not self.itens_pedido:
                    self._sair_modo_edicao(confirmar=True)
            else:
                messagebox.showerror("Erro", mensagem or "Não foi possível remover o item")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover item: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def atualizar_interface(self):
        """Atualiza a interface após mudanças nos dados"""
        # Atualizar tabela de itens
        self.preencher_tabela_itens()
        
        # Atualizar informações do pedido (subtotal, taxa e total)
        self.atualizar_total_pedido()
        
        # Atualizar o total_label se existir (para compatibilidade)
        if hasattr(self, 'total_label') and self.pedido_atual:
            self.total_label.config(text=f"R$ {self.pedido_atual['total']:.2f}".replace('.', ','))
    
    
    def _voltar_para_mesas(self):
        """Método interno para voltar para a tela de mesas após finalizar pedido"""
        try:
            # Usar o método existente para voltar para a tela de mesas
            self.voltar_para_mesas()
        except Exception as e:
            print(f"[ERRO] Erro ao voltar para tela de mesas: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar uma abordagem alternativa se o método voltar_para_mesas falhar
            try:
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
            except Exception as e2:
                print(f"[ERRO] Falha na tentativa alternativa de voltar para tela de mesas: {e2}")
                messagebox.showerror("Erro", "Não foi possível voltar para a tela de mesas. Feche e abra o sistema novamente.")
    
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
                
            # Verificar se o item tem opções antes de criar a janela
            grupos_opcoes = opcoes_controller.listar_opcoes_por_produto(produto_id)
            
            if not grupos_opcoes:
                messagebox.showinfo("Informação", "Este item não possui opções disponíveis.")
                return
                
            # Para cada grupo, buscar os itens de opção
            for grupo in grupos_opcoes:
                grupo['itens'] = opcoes_controller.listar_itens_por_grupo(grupo['id'], ativo=True)
            
            # Criar janela de opções
            self.janela_opcoes = tk.Toplevel(self.parent)
            self.janela_opcoes.title(f"Opções para {item_pedido['nome_produto']}")
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
                command=lambda p=item_pedido: self._atualizar_opcao_item(p)
            )
            btn_confirmar.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
            if hasattr(self, 'janela_opcoes'):
                self.janela_opcoes.destroy()
    
    def _atualizar_opcao_item(self, item_pedido):
        """Atualiza as opções de um item do pedido
        
        Args:
            item_pedido (dict): Dicionário com as informações do item do pedido
        """
        try:
            # Usar o controller para atualizar a opção do item
            self.controller_mesas.atualizar_opcao_item(
                item_pedido_id=item_pedido['id'],
                opcao=None,
                selecionado=None
            )
            
            # Atualizar a lista de itens do pedido
            self.carregar_itens_pedido(self.pedido_atual['id'])
            
            # Atualizar a tabela de itens
            self.preencher_tabela_itens()
            
            # Atualizar o total do pedido
            self.atualizar_total_pedido()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar opção: {str(e)}")
    
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

            # Obter o ID do usuário logado, se disponível
            if usuario_id is None and hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                usuario_id = self.controller.usuario.id

            

            
            # Verificar se há um pedido atual, se não, criar um
            if not hasattr(self, 'pedido_atual') or not self.pedido_atual:

                sucesso = self.criar_novo_pedido(usuario_id=usuario_id)
                if not sucesso:
                    messagebox.showerror("Erro", "Não foi possível criar um novo pedido")
                    return False
                
            # Chamar o método do controller para adicionar o item
            sucesso, mensagem, pedido = self.controller_mesas.adicionar_item_mesa(
                mesa_id=self.mesa['id'],
                produto=produto,
                quantidade=quantidade,
                opcoes_selecionadas=None,  # Sem opções
                preco_adicional=0.0,  # Sem preço adicional
                usuario_id=usuario_id  # Garante que o usuario_id seja sempre passado
            )
            
            if sucesso and pedido:
                # Adicionar à lista de itens da sessão
                if not hasattr(self, 'itens_adicionados_na_sessao'):
                    self.itens_adicionados_na_sessao = []
                    print("[DEBUG] Lista itens_adicionados_na_sessao inicializada")
                
                # Obter o ID do item recém-adicionado diretamente do retorno do controlador
                if hasattr(self.controller_mesas, 'ultimo_item_adicionado'):

                    item_id = self.controller_mesas.ultimo_item_adicionado.get('id')
                    if item_id:
                        # Inicializar a lista se não existir
                        if not hasattr(self.controller_mesas, 'itens_adicionados_na_sessao'):
                            self.controller_mesas.itens_adicionados_na_sessao = []

                            
                        # Adicionar à lista local
                        self.itens_adicionados_na_sessao.append({'id': item_id})

                      
                        
                        # Garantir que o controller também tenha a lista atualizada
                        if hasattr(self.controller_mesas, 'itens_adicionados_na_sessao'):
                            if item_id not in [item.get('id') for item in self.controller_mesas.itens_adicionados_na_sessao if 'id' in item]:
                                self.controller_mesas.itens_adicionados_na_sessao.append({'id': item_id})
                                print(f"[DEBUG] Item também adicionado à sessão do controller")
                    else:
                        print("[ERRO] Não foi possível obter o ID do item recém-adicionado")
                else:
                    print("[ERRO] Controller não tem atributo ultimo_item_adicionado")
                
                # Atualizar a tabela de itens

                self.carregar_pedidos(manter_itens_sessao=True)
                
                # Verificar se os itens da sessão foram mantidos
                if hasattr(self, 'itens_adicionados_na_sessao'):
                    for i, item in enumerate(self.itens_adicionados_na_sessao):
                        pass  # Código para processar cada item, se necessário
                
                # Ativar o modo de edição
                self._entrar_modo_edicao()
                
                return True
            else:
                messagebox.showerror("Erro", mensagem or "Não foi possível adicionar o item ao pedido.")
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
            
            # Verificar se há um pedido atual, se não, criar um
            if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
        
                sucesso = self.criar_novo_pedido(usuario_id=usuario_id)
                if not sucesso:
                    messagebox.showerror("Erro", "Não foi possível criar um novo pedido")
                    return False
                
            
        
            
            sucesso, mensagem, pedido = self.controller_mesas.adicionar_item_mesa(
                mesa_id=self.mesa['id'],
                produto=produto,
                quantidade=quantidade,
                opcoes_selecionadas=opcoes_selecionadas,
                preco_adicional=preco_adicional,
                usuario_id=usuario_id  # Garantir que o usuario_id seja sempre passado
            )
            
            # Se o item foi adicionado com sucesso, adicionar à lista de itens da sessão
            if sucesso and pedido:
                if not hasattr(self, 'itens_adicionados_na_sessao'):
                    self.itens_adicionados_na_sessao = []
                
                # Obter o ID do item recém-adicionado diretamente do retorno do controlador
                if hasattr(self.controller_mesas, 'ultimo_item_adicionado'):
                    item_id = self.controller_mesas.ultimo_item_adicionado.get('id')
                    if item_id:
                        # Adicionar à lista local
                        self.itens_adicionados_na_sessao.append({'id': item_id})
                        print(f"[DEBUG] Item adicionado à sessão (com opções) - ID: {item_id}")
                        print(f"[DEBUG] Total de itens na sessão agora: {len(self.itens_adicionados_na_sessao)}")
                        
                        # Garantir que o controller também tenha a lista atualizada
                        if hasattr(self.controller_mesas, 'itens_adicionados_na_sessao'):
                            if item_id not in [item.get('id') for item in self.controller_mesas.itens_adicionados_na_sessao if 'id' in item]:
                                self.controller_mesas.itens_adicionados_na_sessao.append({'id': item_id})
                                print(f"[DEBUG] Item também adicionado à sessão do controller")
                    else:
                        print("[ERRO] Não foi possível obter o ID do item recém-adicionado")
            
            if sucesso and pedido:
                # Fechar a janela de opções
                if hasattr(self, 'janela_opcoes'):
                    self.janela_opcoes.destroy()
                
                # Atualizar a tabela de itens
                print("[DEBUG] Chamando carregar_pedidos após adicionar item com opções")
                self.carregar_pedidos(manter_itens_sessao=True)
                
                # Atualizar o pedido atual
                self.pedido_atual = pedido
                
                # Recarregar itens do pedido
                print("[DEBUG] Chamando carregar_pedidos após adicionar item com opções")
                self.carregar_pedidos(manter_itens_sessao=True)
                
                # Verificar se os itens da sessão foram mantidos
                if hasattr(self, 'itens_adicionados_na_sessao'):
                    pass
                
                # Atualizar a interface
                self.atualizar_interface()
                
                # Ativar o modo de edição após adicionar um item com opções
                self._entrar_modo_edicao()
                
                # Limpar campos do formulário
                if hasattr(self, 'quantidade_var'):
                    self.quantidade_var.set("1")
                if hasattr(self, 'observacoes_var'):
                    self.observacoes_var.set("")
                
                # Retornar sucesso sem mostrar mensagem
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
            
        except Exception:
            # Silently handle errors when fetching options
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
                
            # Verificar se o produto tem opções
            grupos_opcoes = self.controller_mesas.obter_grupos_opcoes(produto['id'])
            
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
                sucesso = self._adicionar_item_sem_opcoes(produto, quantidade, usuario_id)
                if sucesso:
                    # Ativar o modo de edição após adicionar um item
                    self._entrar_modo_edicao()
                return sucesso
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _entrar_modo_edicao(self):
        """Ativa o modo de edição, mostrando os botões de cancelar e confirmar"""
        # Só entra no modo de edição se ainda não estiver nele
        if not hasattr(self, '_em_modo_edicao') or not self._em_modo_edicao:
            self._em_modo_edicao = True
            self.botao_voltar.pack_forget()
            self.botao_finalizar.pack_forget()
            self.botao_cancelar.pack(side="left")
            # Usar os mesmos parâmetros de pack que o botão finalizar para manter o mesmo tamanho
            self.botao_confirmar.pack(fill="x", pady=5)
    
    def _sair_modo_edicao(self, confirmar=False):
        """
        Desativa o modo de edição, mostrando os botões originais
        
        Args:
            confirmar: Se True, mantém as alterações. Se False, descarta as alterações.
        """
        if hasattr(self, '_em_modo_edicao') and self._em_modo_edicao:
            self._em_modo_edicao = False
            self.botao_cancelar.pack_forget()
            self.botao_confirmar.pack_forget()
            self.botao_voltar.pack(side="left")
            self.botao_finalizar.pack(fill="x", pady=5)
            
            # Se for para confirmar as alterações, limpa a lista de itens da sessão
            if confirmar:
                self.itens_adicionados_na_sessao = []
                self.itens_originais = self.itens_pedido.copy()
    
    def cancelar_alteracoes(self):
        """Cancela as alterações e volta para o estado anterior"""
        try:
            # Obter a lista de itens adicionados na sessão do controlador
            itens_para_remover = self.controller_mesas.itens_adicionados_na_sessao
            
            if not itens_para_remover:
                # Se não houver itens adicionados na sessão, apenas sai do modo de edição
                self._sair_modo_edicao()
                return
                
            # Obter detalhes dos itens a serem removidos
            itens_detalhes = []
            for item in itens_para_remover:
                if 'id' in item:
                    # Buscar detalhes do item na tabela de itens
                    for child in self.tabela_itens.get_children():
                        valores = self.tabela_itens.item(child, 'values')
                        if valores and str(valores[0]) == str(item['id']):
                            nome_item = valores[1]
                            quantidade = valores[2]
                            itens_detalhes.append(f"- {quantidade}x {nome_item}")
                            break
            
            # Criar mensagem com detalhes dos itens
            mensagem = "Tem certeza que deseja cancelar as alterações?\n\n"
            mensagem += f"Os seguintes {len(itens_para_remover)} itens serão removidos:\n"
            
            # Adicionar detalhes dos itens à mensagem
            if itens_detalhes:
                mensagem += "\n".join(itens_detalhes)
            else:
                mensagem += f"- {len(itens_para_remover)} itens sem detalhes disponíveis"
            
            # Perguntar confirmação
            if not messagebox.askyesno(
                "Cancelar Alterações",
                mensagem
            ):
                return
                
            # Remover itens adicionados na sessão
            if self.pedido_atual and 'id' in self.pedido_atual:
                itens_removidos = 0
                erros = []
                
                # Para cada item adicionado na sessão, removê-lo do pedido
                for item in itens_para_remover:
                    if 'id' in item:
                        try:
                            # Remover o item do banco de dados
                            sucesso, mensagem = self.controller_mesas.remover_item_pedido(item_id=item['id'])
                            if sucesso:
                                itens_removidos += 1
                            else:
                                erros.append(f"Falha ao remover item {item['id']}: {mensagem}")
                        except Exception as e:
                            erro_msg = f"Erro ao remover item {item['id']}: {str(e)}"
                            erros.append(erro_msg)
                
                # Limpar a lista de itens adicionados na sessão no controlador
                self.controller_mesas.limpar_itens_sessao()
                
                # Recarregar os itens do pedido do banco de dados
                self.carregar_pedidos(manter_itens_sessao=False)
                
                # Atualizar a interface
                self.atualizar_interface()
                
                # Sair do modo de edição
                self._sair_modo_edicao(confirmar=False)
                
                # Mostrar mensagem apenas em caso de erro
                if erros:
                    messagebox.showwarning(
                        "Aviso", 
                        f"{itens_removidos} itens removidos com sucesso.\n"
                        f"{len(erros)} itens não puderam ser removidos.\n\n"
                        f"Erros encontrados:\n" + "\n".join(erros[:5])
                    )
                
                # Voltar para a tela de visualizar mesas
                self.voltar_para_mesas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar alterações: {str(e)}")
    
    def confirmar_alteracoes(self):
        """Confirma as alterações e volta para o estado normal e imprime apenas os itens adicionados na sessão"""
        try:

            
            # Verificar se há itens adicionados na sessão para imprimir
            if not hasattr(self, 'itens_adicionados_na_sessao') or not self.itens_adicionados_na_sessao:
                
                messagebox.showinfo("Aviso", "Não há novos itens para imprimir.")
                self._sair_modo_edicao(confirmar=True)
                return
                
            if not hasattr(self, 'pedido_atual') or not self.pedido_atual:

                messagebox.showerror("Erro", "Não há pedido atual para confirmar alterações.")
                return
                
            for i, item in enumerate(self.itens_adicionados_na_sessao):
                pass
                
            # Inicializar o gerenciador de impressão
            config_controller = ConfigController()
            gerenciador_impressao = GerenciadorImpressao(config_controller=config_controller)
            
            # Lista para armazenar os itens que serão impressos
            itens_para_imprimir = []
            
                
            # Verificar se temos conexão com o banco de dados
            if not hasattr(self, 'db_connection') or not self.db_connection:
           
                messagebox.showerror("Erro", "Sem conexão com o banco de dados.")
                return
                
            # Buscar os detalhes completos dos itens adicionados na sessão
            cursor = self.db_connection.cursor(dictionary=True)
                
            for item_sessao in self.itens_adicionados_na_sessao:
                if 'id' in item_sessao and item_sessao['id']:
                    # Buscar o item completo no banco de dados
                    cursor.execute("""
                        SELECT ip.*, p.nome as nome_produto, p.tipo 
                        FROM itens_pedido ip
                        JOIN produtos p ON ip.produto_id = p.id
                        WHERE ip.id = %s
                    """, (item_sessao['id'],))
                        
                    item_completo = cursor.fetchone()
                    
                    if item_completo:
                        # Buscar as opções do item, se houver
                        cursor.execute("""
                            SELECT * FROM itens_pedido_opcoes 
                            WHERE item_pedido_id = %s
                        """, (item_sessao['id'],))
                        
                        opcoes = cursor.fetchall()
                        item_completo['opcoes'] = opcoes
                        
                        # Garantir que o tipo seja um dos tipos padrão
                        if item_completo.get('tipo') not in ["Cozinha", "Bar", "Sobremesas", "Outros"]:
                            item_completo['tipo'] = 'Outros'
                        
                        # Renomear o campo valor_unitario para preco_unitario se necessário
                        if 'valor_unitario' in item_completo and ('preco_unitario' not in item_completo or item_completo['preco_unitario'] is None):
                            item_completo['preco_unitario'] = item_completo['valor_unitario']
                        
                        # Garantir que todos os campos necessários existam
                        campos_necessarios = {
                            'nome': item_completo.get('nome_produto', 'Produto sem nome'),
                            'quantidade': item_completo.get('quantidade', 1),
                            'tipo': item_completo.get('tipo', 'Outros')
                        }
                        
                        # Adicionar os campos necessários ao item
                        for campo, valor in campos_necessarios.items():
                            if campo not in item_completo or item_completo[campo] is None:
                                item_completo[campo] = valor
                            
                        itens_para_imprimir.append(item_completo)
                
            cursor.close()
            
            # Se encontrou itens para imprimir
            if itens_para_imprimir:
                # Obter o nome do usuário atual, se disponível
                nome_usuario = 'Não identificado'
                if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'nome'):
                    nome_usuario = self.controller.usuario.nome
                
                # Informações do pedido para o cabeçalho da impressão
                info_pedido = {
                    'id': self.pedido_atual['id'],
                    'mesa': self.mesa['numero'],
                    'data_hora': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                    'tipo': 'ADICIONAL MESA',  # Indica que são itens adicionais
                    'tipo_venda': 'mesa',
                    'referencia': f"Mesa {self.mesa['numero']} - Pedido #{self.pedido_atual['id']} (Adicionais)",
                    'usuario_nome': nome_usuario  # Adiciona o nome do usuário
                }
                
                # Criar uma cópia dos itens para evitar modificar a lista original
                itens_para_impressao = itens_para_imprimir.copy()
                
                # Verificar e corrigir campos antes de enviar para impressão
                try:
                    for item in itens_para_impressao:
                        # Garantir que o campo nome exista (necessário para impressão)
                        if 'nome' not in item:
                            item['nome'] = item.get('nome_produto', 'Produto sem nome')

                        
                        # Garantir que o campo produto_id exista
                        if 'produto_id' not in item and 'id_produto' in item:
                            item['produto_id'] = item['id_produto']

                            

                    gerenciador_impressao.imprimir_comandas_por_tipo(info_pedido, itens_para_imprimir)
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao preparar itens para impressão: {str(e)}")
                    import traceback
                    messagebox.showerror("Erro", f"Erro ao imprimir itens: {str(e)}")
                    traceback.print_exc()

            
            # Limpar os itens da sessão no controlador e localmente

            
            # Verificar e limpar no controller
            if hasattr(self.controller_mesas, 'limpar_itens_sessao'):
                self.controller_mesas.limpar_itens_sessao()

            elif hasattr(self.controller_mesas, 'itens_adicionados_na_sessao'):
                self.controller_mesas.itens_adicionados_na_sessao = []

            
            # Limpar a lista local
            if hasattr(self, 'itens_adicionados_na_sessao'):
                qtd_antes = len(self.itens_adicionados_na_sessao)
                self.itens_adicionados_na_sessao = []

                
            # Verificar se a limpeza foi bem-sucedida
            if hasattr(self, 'itens_adicionados_na_sessao') and self.itens_adicionados_na_sessao:

                self.itens_adicionados_na_sessao = []
            
            # Sair do modo de edição
            self._sair_modo_edicao(confirmar=True)
            

            # Recarregar os itens do pedido para garantir que tudo está sincronizado

            self.carregar_pedidos()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao confirmar alterações: {str(e)}")

    
    def remover_item_selecionado(self):
        """Remove o item selecionado da tabela de itens do pedido"""
        try:
            # Verificar se há um item selecionado na tabela
            selecionado = self.tabela_itens.selection()
            if not selecionado:
                messagebox.showinfo("Aviso", "Selecione um item para remover")
                return
                
            # Obter o ID do item selecionado
            item_id = self.tabela_itens.item(selecionado[0], 'values')[0]
            
            # Verificar se o item é uma opção (verifica se o ID está vazio ou se é um item filho)
            item_values = self.tabela_itens.item(selecionado[0], 'values')
            if not item_values[0]:  # Se o ID estiver vazio, é uma opção
                messagebox.showinfo("Aviso", "Para remover este item, remova o item principal que o contém")
                return
                
            # Se chegou aqui, é um item principal (pode ter ou não opções)
            # Se estiver no modo de edição, remover o item da lista de itens adicionados
            if hasattr(self, '_em_modo_edicao') and self._em_modo_edicao:
                for i, item in enumerate(self.itens_adicionados_na_sessao):
                    if str(item.get('id')) == str(item_id):
                        self.itens_adicionados_na_sessao.pop(i)
                        break
            
            # Remover o item do banco de dados
            sucesso, mensagem = self.controller_mesas.remover_item_pedido(item_id=item_id)
            
            if sucesso:
                # Recarregar os itens do pedido
                self.carregar_pedidos(manter_itens_sessao=hasattr(self, '_em_modo_edicao') and self._em_modo_edicao)
                self.atualizar_interface()
                
                # Se não houver mais itens, sair do modo de edição
                if not hasattr(self, 'itens_pedido') or not self.itens_pedido:
                    self._sair_modo_edicao(confirmar=True)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover item: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _atualizar_taxa_servico(self):
        """Atualiza o valor da taxa de serviço e recalcula o total"""
        if not hasattr(self, 'pedido_atual') or not self.pedido_atual or 'id' not in self.pedido_atual:
            return
            
        try:
            # Obter o valor do subtotal atual
            subtotal_texto = self.subtotal_valor.cget("text").replace("R$", "").strip().replace(".", "").replace(",", ".")
            subtotal = float(subtotal_texto) if subtotal_texto else 0.0
            # Subtotal atual obtido do label
            
            # Calcular a taxa de serviço (10% do subtotal)
            taxa = subtotal * 0.1 if self.taxa_servico_var.get() else 0.0
            # Calcular taxa de serviço
            
            # Atualizar o label da taxa de serviço
            self.taxa_valor.config(text=f"R$ {taxa:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
            
            # Calcular o total (subtotal + taxa)
            total = subtotal + taxa
            # Calcular o total (subtotal + taxa)
            
            # Atualizar o label do total
            self.total_valor.config(text=f"R$ {total:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
            
            # Atualizar o total no pedido atual
            if self.pedido_atual:
                self.pedido_atual['total'] = total
                # Atualizar o total no pedido atual
                
                # Atualizar a taxa de serviço no banco de dados
                # Atualizar a taxa de serviço no banco de dados
                self.controller_mesas.atualizar_taxa_servico(
                    pedido_id=self.pedido_atual['id'],
                    taxa_servico=1 if self.taxa_servico_var.get() else 0
                )
            
            # Forçar atualização da interface
            self.update_idletasks()
            # _atualizar_taxa_servico concluído
            
        except Exception as e:
            # Silently handle the error without printing to console
            pass
    
    def atualizar_total_pedido(self):
        """Atualiza o total do pedido atual"""
        try:
            if not hasattr(self, 'pedido_atual') or not self.pedido_atual or 'id' not in self.pedido_atual:
                return 0.0
            
            # Obter o total bruto (subtotal) do controller
            subtotal = self.controller_mesas.atualizar_total_pedido(self.pedido_atual['id'])
            
            # Calcular taxa de serviço se estiver marcada
            taxa = subtotal * 0.1 if self.taxa_servico_var.get() else 0.0
            
            # Calcular o total final
            total = subtotal + taxa
            
            # Atualizar o pedido atual
            if self.pedido_atual:
                self.pedido_atual['total'] = total
            
            # Atualizar a interface
            if hasattr(self, 'total_valor'):
                # Formatar os valores para exibição
                self.subtotal_valor.config(text=f"R$ {subtotal:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
                self.taxa_valor.config(text=f"R$ {taxa:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
                self.total_valor.config(text=f"R$ {total:,.2f}".replace('.', '|').replace(',', '.').replace('|', ','))
            return float(total) if total is not None else 0.0
        except Exception as e:
            # Tratar erro silenciosamente
            return 0.0
            
        finally:
            if 'cursor' in locals():
                cursor.close()
