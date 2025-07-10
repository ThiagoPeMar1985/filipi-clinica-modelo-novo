"""
Módulo para gerenciamento de pedidos de mesas.
Permite visualizar, adicionar, editar e remover pedidos de uma mesa específica.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ..base_module import BaseModule
from src.config.estilos import CORES, FONTES

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
        self.pedidos = []
        self.produtos = []
        self.itens_pedido = []
        self.pedido_atual = None
        
        # Configurar a interface primeiro para mostrar algo ao usuário rapidamente
        self.setup_ui()
        
        # Carregar dados em segundo plano após a interface estar pronta
        self.parent.after(100, self.carregar_dados)
        
    def carregar_dados(self):
        """Carrega os dados essenciais para iniciar o módulo e agenda o carregamento dos dados restantes"""
        try:
            # Primeiro, carregar apenas os pedidos da mesa (essencial)
            self.carregar_pedidos()
            
            # Preencher a tabela de itens do pedido atual (se houver)
            self.preencher_tabela_itens()
            
            # Carregar produtos
            self.carregar_produtos()
            
            # Preencher tabela de produtos
            self.preencher_tabela_produtos()
        except Exception as e:
            print(f"Erro ao carregar produtos: {str(e)}")
            # Não exibir mensagem de erro para o usuário para não interromper o fluxo
    
    def carregar_produtos(self):
        """Carrega a lista de produtos do banco de dados"""
        if not self.db_connection:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
            return
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Consulta para buscar todos os produtos ordenados por tipo e nome
            query = """
            SELECT id, nome, preco_venda as preco, tipo, quantidade_minima
            FROM produtos 
            ORDER BY tipo, nome 
            """
            cursor.execute(query)
            self.produtos = cursor.fetchall()
            cursor.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {str(e)}")
            self.produtos = []
    
    def carregar_pedidos(self):
        """Carrega os pedidos da mesa selecionada"""
        if not self.db_connection or not self.mesa:
            return
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Consulta otimizada para buscar apenas o pedido aberto mais recente

            query = """
            SELECT p.id, p.data_abertura, p.status, p.total, p.observacao
            FROM pedidos p
            WHERE p.mesa_id = %s AND p.status = 'ABERTO'
            ORDER BY p.data_abertura DESC
            """
            
            cursor.execute(query, (self.mesa['id'],))
            resultado = cursor.fetchone()
            
            # Se houver um pedido aberto, usá-lo como pedido atual
            if resultado:
                self.pedidos = [resultado]
                self.pedido_atual = resultado
                self.carregar_itens_pedido(self.pedido_atual['id'])
            else:
                self.pedidos = []
                self.pedido_atual = None
            
            cursor.close()
        except Exception as e:
            print(f"Erro ao carregar pedidos: {str(e)}")
            self.pedidos = []
            self.pedido_atual = None
    
    def carregar_itens_pedido(self, pedido_id):
        """
        Carrega os itens de um pedido específico, incluindo suas opções
        
        Args:
            pedido_id: ID do pedido para carregar os itens
        """
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Consulta otimizada para buscar itens do pedido com informações do produto
            query = """
            SELECT i.id, i.produto_id, p.nome as nome_produto, 
                   i.quantidade, i.valor_unitario, i.subtotal, i.observacao
            FROM itens_pedido i
            JOIN produtos p ON i.produto_id = p.id
            WHERE i.pedido_id = %s
            ORDER BY i.id
            """
            
            cursor.execute(query, (pedido_id,))
            itens = cursor.fetchall()
            
            # Para cada item, buscar suas opções
            for item in itens:
                # Inicializar lista de opções vazia para o item
                item['opcoes'] = []
                
                # Buscar opções do item
                query_opcoes = """
                SELECT opcao_id as id, nome, preco_adicional
                FROM itens_pedido_opcoes
                WHERE item_pedido_id = %s
                """
                cursor.execute(query_opcoes, (item['id'],))
                item['opcoes'] = cursor.fetchall()
            
            self.itens_pedido = itens
            cursor.close()
            
        except Exception as e:
            print(f"Erro ao carregar itens do pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            self.itens_pedido = []
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = tk.Frame(self.frame, bg=CORES['fundo'])
        main_frame.pack(fill="both", expand=True)
        
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
            command=lambda: self.limpar_pedido_atual()
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
            # Formatar o preço
            preco = f"R$ {float(produto['preco']):.2f}".replace('.', ',')
            
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
        """
        # Verificar se há um pedido atual
        if not self.pedido_atual:
            # Criar novo pedido e depois adicionar o item
            self.criar_novo_pedido()
            # Após criar o pedido, chamar esta função novamente
            self.frame.after(500, lambda: self.adicionar_item_especifico(produto, quantidade, opcoes_selecionadas, preco_adicional))
            return
        
        try:
            # Calcular valores
            valor_unitario = float(produto['preco'])
            valor_total = (valor_unitario + preco_adicional) * quantidade
            
            # Inserir item no banco de dados
            cursor = self.db_connection.cursor()
            
            # Obter a data e hora atual
            data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Criar observação com as opções selecionadas
            observacao = ""
            if opcoes_selecionadas:
                nomes_opcoes = [opcao['nome'] for opcao in opcoes_selecionadas]
                observacao = "Com: " + ", ".join(nomes_opcoes)
            
            # Inserir o item principal
            query = """
            INSERT INTO itens_pedido 
            (pedido_id, produto_id, quantidade, valor_unitario, subtotal, observacao, data_hora, valor_total, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(
                query, 
                (self.pedido_atual['id'], produto['id'], quantidade, valor_unitario, 
                 valor_total, observacao, data_hora_atual, valor_total, 'pendente')
            )
            
            # Obter o ID do item inserido
            item_id = cursor.lastrowid
            
            # Inserir as opções selecionadas, se houver
            if opcoes_selecionadas:
                for opcao in opcoes_selecionadas:
                    # Obter o grupo_id da opção
                    cursor.execute("SELECT grupo_id FROM opcoes_itens WHERE id = %s", (opcao['id'],))
                    resultado = cursor.fetchone()
                    if not resultado:
                        raise ValueError(f"Opção com ID {opcao['id']} não encontrada")
                    grupo_id = resultado[0]
                    
                    query_opcao = """
                    INSERT INTO itens_pedido_opcoes 
                    (item_pedido_id, opcao_id, grupo_id, nome, preco_adicional, data_criacao) 
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    """
                    cursor.execute(
                        query_opcao,
                        (item_id, opcao['id'], grupo_id, opcao['nome'], opcao['preco_adicional'])
                    )
            
            # Atualizar valor total do pedido
            query_update = """
            UPDATE pedidos 
            SET total = total + %s 
            WHERE id = %s
            """
            
            cursor.execute(query_update, (valor_total, self.pedido_atual['id']))
            
            # Commit das alterações
            self.db_connection.commit()
            cursor.close()
            
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
        colunas = ("id", "produto", "quantidade", "valor_unit", "valor_total", "acoes")
        
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
        self.tabela_itens.heading("acoes", text="Ações")
        
        # Configurar larguras das colunas
        self.tabela_itens.column("id", width=50, anchor="center")
        self.tabela_itens.column("produto", width=200, anchor="w")
        self.tabela_itens.column("quantidade", width=50, anchor="center")
        self.tabela_itens.column("valor_unit", width=100, anchor="e")
        self.tabela_itens.column("valor_total", width=100, anchor="e")
        self.tabela_itens.column("acoes", width=100, anchor="center")
        
        # Configurar tags para estilização
        self.tabela_itens.tag_configure('opcao', background='#f5f5f5')  # Fundo mais claro para opções
        
        # Configurar scrollbar
        self.tabela_itens.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tabela_itens.yview)
        
        # Empacotar a tabela
        self.tabela_itens.pack(fill="both", expand=True)
        
        # Removido o evento de duplo clique conforme solicitado
        
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
            
        # Preparar todos os itens antes de inserir (melhora o desempenho)
        itens_para_inserir = []
        for item in self.itens_pedido:
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
            nome_produto = item['nome_produto']
            if 'opcoes' in item and item['opcoes'] and not nome_produto.endswith(' +'):
                nome_produto = f"{nome_produto} +"
            
            # Adicionar à lista de itens para inserir
            itens_para_inserir.append((
                item['id'],
                nome_produto,  # Usar a variável nome_produto que já tem o sinal de + se necessário
                item['quantidade'],
                valor_unitario_fmt,
                subtotal_fmt
            ))
        
        # Inserir todos os itens de uma vez
        for valores in itens_para_inserir:
            item_id = valores[0]
            
            # Inserir o item principal
            item = self.tabela_itens.insert("", "end", values=valores)
            
            # Verificar se o item tem opções
            for pedido_item in self.itens_pedido:
                if str(pedido_item['id']) == str(item_id) and 'opcoes' in pedido_item and pedido_item['opcoes']:
                    # Adicionar as opções como itens filhos
                    for opcao in pedido_item['opcoes']:
                        self.tabela_itens.insert(
                            item, 
                            "end", 
                            values=(
                                "",  # ID vazio para opções
                                f"  → {opcao['nome']}",  # Indentação para mostrar que é uma opção
                                "",  # Quantidade vazia
                                f"+R$ {float(opcao['preco_adicional']):.2f}".replace('.', ','),  # Preço adicional
                                ""   # Subtotal vazio
                            ),
                            tags=('opcao',)  # Tag para estilização
                        )
                    
                    # Expandir o item para mostrar as opções
                    self.tabela_itens.item(item, open=True)
                    break
    
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
    
    def adicionar_item(self):
        """Adiciona um item ao pedido atual"""
        # Obter item selecionado na tabela de produtos
        if not hasattr(self, 'tabela_produtos'):
            messagebox.showerror("Erro", "Tabela de produtos não encontrada!")
            return
            
        selecionado = self.tabela_produtos.selection()
        if not selecionado:
            messagebox.showinfo("Aviso", "Selecione um produto da lista para adicionar à mesa.")
            return
            
        # Obter valores do item selecionado
        item_values = self.tabela_produtos.item(selecionado[0], 'values')
        produto_id = item_values[0]
        
        # Encontrar o produto na lista
        produto_selecionado = None
        for produto in self.produtos:
            if str(produto['id']) == str(produto_id):
                produto_selecionado = produto
                break
                
        if not produto_selecionado:
            messagebox.showerror("Erro", "Produto não encontrado!")
            return
            
        # Adicionar o produto ao pedido
        self.adicionar_item_especifico(produto_selecionado, 1)
        
        # Verificar se há um pedido atual
        if not self.pedido_atual:
            self.criar_novo_pedido(adicionar_item=True)
            return
        
        try:
            # Obter índice do produto selecionado
            indice_produto = self.combo_produtos.current()
            if indice_produto < 0:
                messagebox.showerror("Erro", "Selecione um produto!")
                return
            
            # Obter produto selecionado
            produto = self.produtos[indice_produto]
            
            # Obter quantidade
            try:
                quantidade = int(self.quantidade_var.get())
                if quantidade <= 0:
                    raise ValueError("Quantidade deve ser maior que zero")
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida!")
                return
            
            # Obter observações
            observacoes = self.observacoes_var.get()
            
            # Calcular valores
            valor_unitario = float(produto['preco'])
            valor_total = valor_unitario * quantidade
            
            # Inserir item no banco de dados
            cursor = self.db_connection.cursor()
            
            # Obter a data e hora atual
            data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            query = """
            INSERT INTO itens_pedido 
            (pedido_id, produto_id, quantidade, valor_unitario, subtotal, observacao, data_hora, valor_total, status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(
                query, 
                (self.pedido_atual['id'], produto['id'], quantidade, valor_unitario, 
                 valor_total, observacoes, data_hora_atual, valor_total, 'pendente')
            )
            
            # Atualizar valor total do pedido
            query_update = """
            UPDATE pedidos 
            SET total = total + %s 
            WHERE id = %s
            """
            
            cursor.execute(query_update, (valor_total, self.pedido_atual['id']))
            
            # Commit das alterações
            self.db_connection.commit()
            cursor.close()
            
            # Recarregar dados
            self.carregar_pedidos()
            
            # Limpar campos do formulário
            self.quantidade_var.set("1")
            self.observacoes_var.set("")
            
            # Atualizar interface
            self.atualizar_interface()
            
            # Mensagem de sucesso
            messagebox.showinfo("Sucesso", "Item adicionado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")

    def criar_novo_pedido(self, adicionar_item=False):
        """Cria um novo pedido para a mesa atual"""
        if not self.db_connection or not self.mesa:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados ou nenhuma mesa selecionada!")
            return
        
        try:
            # Verificar se a mesa está ocupada
            if self.mesa['status'].lower() != "ocupada":
                # Perguntar se deseja ocupar a mesa
                resposta = messagebox.askyesno(
                    "Mesa não ocupada", 
                    f"A mesa {self.mesa['numero']} não está ocupada. Deseja ocupá-la e criar um novo pedido?"
                )
                
                if not resposta:
                    return
                
                # Atualizar status da mesa para ocupada
                cursor = self.db_connection.cursor()
                cursor.execute("UPDATE mesas SET status = 'OCUPADA' WHERE id = %s", (self.mesa['id'],))
                self.db_connection.commit()
                cursor.close()
                
                # Atualizar status da mesa no objeto
                self.mesa['status'] = "OCUPADA"
            
            # Criar novo pedido
            cursor = self.db_connection.cursor()
            
            # Data e hora atual
            data_abertura = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Obter o ID do usuário logado, se disponível
            usuario_id = None
            if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                usuario_id = self.controller.usuario.id
            
            # Inserir novo pedido
            query = """
            INSERT INTO pedidos 
            (mesa_id, data_abertura, status, total, observacao, tipo, usuario_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(
                query, 
                (self.mesa['id'], data_abertura, "ABERTO", 0.0, "", "MESA", usuario_id)
            )
            
            # Obter ID do pedido inserido
            pedido_id = cursor.lastrowid
            
            # Atualizar o pedido_atual_id na tabela mesas
            cursor.execute("""
                UPDATE mesas 
                SET pedido_atual_id = %s 
                WHERE id = %s
            """, (pedido_id, self.mesa['id']))
            
            # Commit das alterações
            self.db_connection.commit()
            
            # Fechar cursor
            cursor.close()
            
            # Atualizar o objeto mesa localmente
            self.mesa['pedido_atual_id'] = pedido_id
            
            # Recarregar pedidos
            self.carregar_pedidos()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", "Novo pedido criado com sucesso!")
            
            # Se for para adicionar item, continuar
            if adicionar_item:
                self.adicionar_item()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar novo pedido: {str(e)}")
    
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
        if not self.pedido_atual:
            messagebox.showinfo("Aviso", "Não há pedido aberto para finalizar!")
            return
        
        # Verificar se existem itens no pedido
        if not self.itens_pedido:
            messagebox.showinfo("Aviso", "Adicione itens ao pedido antes de finalizar!")
            return
        
        # Confirmar finalização
        if not messagebox.askyesno("Confirmar", "Deseja finalizar esta venda?"):
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            try:
                # Verificar se o pedido já não foi finalizado
                cursor.execute("SELECT status FROM pedidos WHERE id = %s", (self.pedido_atual['id'],))
                pedido = cursor.fetchone()
                
                if not pedido:
                    messagebox.showerror("Erro", "Pedido não encontrado!")
                    return
                    
                if pedido['status'] == 'FINALIZADO':
                    messagebox.showinfo("Aviso", "Este pedido já foi finalizado anteriormente.")
                    return
                
                # Data e hora atual
                data_fechamento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Atualizar status do pedido
                query = """
                UPDATE pedidos 
                SET status = 'FINALIZADO', data_fechamento = %s 
                WHERE id = %s
                """
                
                cursor.execute(query, (data_fechamento, self.pedido_atual['id']))
                
                # Verificar se há outros pedidos abertos para esta mesa
                cursor.execute(
                    "SELECT COUNT(*) as total FROM pedidos WHERE mesa_id = %s AND status = 'ABERTO' AND id != %s", 
                    (self.mesa['id'], self.pedido_atual['id'])
                )
                
                resultado = cursor.fetchone()
                outros_pedidos_abertos = resultado['total'] if resultado else 0
                
                # Se não houver outros pedidos abertos, perguntar se deseja liberar a mesa
                if outros_pedidos_abertos == 0:
                    resposta_liberar = messagebox.askyesno(
                        "Liberar Mesa", 
                        f"Não há mais pedidos abertos para a mesa {self.mesa['numero']}. Deseja liberá-la?"
                    )
                    
                    if resposta_liberar:
                        # Atualizar status da mesa para livre e limpar pedido_atual_id
                        cursor.execute("""
                            UPDATE mesas 
                            SET status = 'LIVRE', 
                                pedido_atual_id = NULL 
                            WHERE id = %s
                        """, (self.mesa['id'],))
                        self.mesa['status'] = "LIVRE"
                        self.mesa['pedido_atual_id'] = None
                
                # Commit das alterações
                self.db_connection.commit()
                
                # Atualizar o pedido atual
                self.pedido_atual['status'] = 'FINALIZADO'
                self.pedido_atual['data_fechamento'] = data_fechamento
                
                # Recarregar pedidos para garantir que os dados estejam atualizados
                self.carregar_pedidos()
                
                # Atualizar interface
                self.atualizar_interface()
                
                # Mostrar mensagem de sucesso
                messagebox.showinfo("Sucesso", "Pedido finalizado com sucesso!")
                
            except Exception as e:
                self.db_connection.rollback()
                raise e
                
            finally:
                cursor.close()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao finalizar pedido: {str(e)}")
            print(f"Erro ao finalizar pedido: {str(e)}")
    
    def editar_item_selecionado(self, event):
        """Seleciona o item na tabela sem exibir mensagens"""
        # Apenas seleciona o item, sem exibir mensagens
        selecao = self.tabela_itens.selection()
        if not selecao:
            return
            
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
            
    def limpar_pedido_atual(self):
        """
        Remove todos os itens do pedido atual e, se estiver vazio, pergunta se deseja cancelar o pedido
        """
        if not self.pedido_atual:
            messagebox.showinfo("Aviso", "Não há pedido aberto")
            return
            
        # Verificar se o pedido já está vazio
        if not self.itens_pedido or len(self.itens_pedido) == 0:
            # Se não houver itens, perguntar se deseja cancelar o pedido
            if messagebox.askyesno("Cancelar Pedido", "O pedido está vazio. Deseja cancelar este pedido e liberar a mesa?"):
                self.cancelar_pedido()
            return
            
        # Se houver itens, perguntar se deseja remover todos os itens
        if messagebox.askyesno("Confirmar", "Deseja remover TODOS os itens deste pedido?"):
            try:
                # Remover todos os itens do pedido no banco de dados
                if self.db_connection:
                    cursor = self.db_connection.cursor()
                    
                    try:
                        # Primeiro, remover todas as opções dos itens do pedido
                        cursor.execute(
                            """
                            DELETE ipo FROM itens_pedido_opcoes ipo
                            INNER JOIN itens_pedido ip ON ipo.item_pedido_id = ip.id
                            WHERE ip.pedido_id = %s
                            """,
                            (self.pedido_atual['id'],)
                        )
                        
                        # Depois, remover todos os itens do pedido
                        query = "DELETE FROM itens_pedido WHERE pedido_id = %s"
                        cursor.execute(query, (self.pedido_atual['id'],))
                        
                        # Atualizar o total do pedido para zero
                        query = "UPDATE pedidos SET total = 0 WHERE id = %s"
                        cursor.execute(query, (self.pedido_atual['id'],))
                        
                        self.db_connection.commit()
                        
                        # Atualizar o pedido atual
                        self.pedido_atual['total'] = 0
                        self.itens_pedido = []
                        
                        # Perguntar se deseja cancelar o pedido vazio
                        if messagebox.askyesno("Pedido Vazio", "O pedido está vazio. Deseja cancelar este pedido e liberar a mesa?"):
                            self.cancelar_pedido()
                        else:
                            # Atualizar a interface
                            self.preencher_tabela_itens()
                            self.atualizar_interface()
                            messagebox.showinfo("Sucesso", "Todos os itens foram removidos do pedido")
                        
                    except Exception as e:
                        self.db_connection.rollback()
                        raise e
                        
                    finally:
                        cursor.close()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar o pedido: {str(e)}")
                print(f"Erro ao limpar pedido: {str(e)}")
    
    def cancelar_pedido(self):
        """
        Cancela o pedido atual e libera a mesa
        """
        if not self.pedido_atual:
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            try:
                # Remover todas as opções dos itens do pedido
                cursor.execute(
                    """
                    DELETE ipo FROM itens_pedido_opcoes ipo
                    INNER JOIN itens_pedido ip ON ipo.item_pedido_id = ip.id
                    WHERE ip.pedido_id = %s
                    """,
                    (self.pedido_atual['id'],)
                )
                
                # Remover todos os itens do pedido
                cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = %s", (self.pedido_atual['id'],))
                
                # Remover o pedido
                cursor.execute("DELETE FROM pedidos WHERE id = %s", (self.pedido_atual['id'],))
                
                # Atualizar a mesa para LIVRE e limpar pedido_atual_id
                cursor.execute("""
                    UPDATE mesas 
                    SET status = 'LIVRE', 
                        pedido_atual_id = NULL 
                    WHERE id = %s
                """, (self.mesa['id'],))
                
                self.db_connection.commit()
                
                # Atualizar o estado local
                self.mesa['status'] = 'LIVRE'
                self.mesa['pedido_atual_id'] = None
                self.pedido_atual = None
                self.itens_pedido = []
                
                # Atualizar a interface
                self.carregar_pedidos()
                self.atualizar_interface()
                
                messagebox.showinfo("Sucesso", "Pedido cancelado e mesa liberada com sucesso!")
                
            except Exception as e:
                self.db_connection.rollback()
                raise e
                
            finally:
                cursor.close()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar o pedido: {str(e)}")
            print(f"Erro ao cancelar pedido: {str(e)}")
    
    def remover_item(self, item_id):
        """
        Remove um item do pedido, incluindo suas opções associadas
        
        Args:
            item_id: ID do item a ser removido
        """
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Obter valor total do item para subtrair do pedido
            cursor.execute("SELECT subtotal FROM itens_pedido WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            
            if not item:
                messagebox.showerror("Erro", "Item não encontrado!")
                return
            
            valor_item = item['subtotal']
            
            try:
                # Remover as opções associadas ao item primeiro (se houver)
                cursor.execute("DELETE FROM itens_pedido_opcoes WHERE item_pedido_id = %s", (item_id,))
                
                # Remover o item principal
                cursor.execute("DELETE FROM itens_pedido WHERE id = %s", (item_id,))
                
                # Atualizar valor total do pedido
                cursor.execute(
                    "UPDATE pedidos SET total = GREATEST(0, total - %s) WHERE id = %s", 
                    (valor_item, self.pedido_atual['id'])
                )
                
                # Commit das alterações
                self.db_connection.commit()
                
            except Exception as e:
                # Em caso de erro, fazer rollback
                self.db_connection.rollback()
                raise e
                
            finally:
                cursor.close()
            
            # Recarregar dados
            self.carregar_pedidos()
            
            # Atualizar interface
            self.atualizar_interface()
            
            # Mensagem de sucesso
            messagebox.showinfo("Sucesso", "Item removido com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover item: {str(e)}")
    
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
        termo = self.busca_entry.get().strip().lower()
        
        if not termo:
            # Se não houver termo de busca, mostrar todos os produtos
            self.preencher_tabela_produtos()
            return
        
        try:
            # Buscar diretamente no banco de dados para melhor desempenho
            cursor = self.db_connection.cursor(dictionary=True)
            
            query = """
            SELECT id, nome, preco_venda as preco, tipo, quantidade_minima
            FROM produtos 
            WHERE LOWER(nome) LIKE %s OR LOWER(tipo) LIKE %s
            ORDER BY nome
            """
            
            termo_busca = f"%{termo}%"
            cursor.execute(query, (termo_busca, termo_busca))
            produtos_filtrados = cursor.fetchall()
            cursor.close()
            
            # Atualizar a tabela com os produtos filtrados
            self.preencher_tabela_produtos(produtos_filtrados)
            
        except Exception as e:
            print(f"Erro ao buscar produtos: {str(e)}")
            # Em caso de erro, fazer a busca em memória
            produtos_filtrados = []
            for produto in self.produtos:
                # Buscar no nome e no tipo do produto
                if termo in produto['nome'].lower() or \
                   (produto.get('tipo', '') and termo in produto.get('tipo', '').lower()):
                    produtos_filtrados.append(produto)
            
            # Atualizar a tabela com os produtos filtrados
            self.preencher_tabela_produtos(produtos_filtrados)
    
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
                
            # Verificar se o produto tem opções
            opcoes = opcoes_controller.listar_opcoes_por_produto(produto_id)
            
            if not opcoes:
                messagebox.showinfo("Informação", "Este item não possui opções disponíveis.")
                return
                
            # Criar uma janela para exibir as opções
            janela_opcoes = tk.Toplevel(self.window)
            janela_opcoes.title(f"Opções do Item #{item_pedido['id']}")
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
            
            # Adicionar opções existentes
            opcoes_selecionadas = {}
            
            if 'opcoes' in item_pedido and item_pedido['opcoes']:
                for opcao in item_pedido['opcoes']:
                    opcoes_selecionadas[opcao['id']] = opcao
            
            # Criar checkboxes para cada opção
            for opcao in opcoes:
                var = tk.BooleanVar(value=opcao['id'] in opcoes_selecionadas)
                
                frame_opcao = tk.Frame(opcoes_frame, bg=CORES['fundo'], pady=5)
                frame_opcao.pack(fill="x", pady=2)
                
                # Checkbox
                cb = tk.Checkbutton(
                    frame_opcao,
                    text=f"{opcao['nome']} (+R$ {opcao['preco_adicional']:.2f})",
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
                if opcao.get('descricao'):
                    tk.Label(
                        frame_opcao,
                        text=f"    {opcao['descricao']}",
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
        if not self.pedido_atual:
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Calcular o total do pedido somando os subtotais dos itens
            query = """
            SELECT COALESCE(SUM(ip.subtotal), 0) as total
            FROM itens_pedido ip
            WHERE ip.pedido_id = %s
            """
            cursor.execute(query, (self.pedido_atual['id'],))
            resultado = cursor.fetchone()
            
            if resultado:
                total = float(resultado['total'])
                
                # Atualizar o total no banco de dados
                update_query = "UPDATE pedidos SET total = %s WHERE id = %s"
                cursor.execute(update_query, (total, self.pedido_atual['id']))
                self.db_connection.commit()
                
                # Atualizar o objeto do pedido atual
                self.pedido_atual['total'] = total
                
                # Atualizar a interface
                if hasattr(self, 'total_valor'):
                    self.total_valor.config(text=f"R$ {total:.2f}".replace('.', ','))
                
                return total
                
        except Exception as e:
            self.db_connection.rollback()
            print(f"Erro ao atualizar total do pedido: {str(e)}")
            return 0
            
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
            if not self.db_connection:
                messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
                return
                
            cursor = self.db_connection.cursor()
            
            if var.get():  # Se a opção foi marcada
                # Verificar se a opção já está associada ao item
                cursor.execute(
                    "SELECT id FROM itens_pedido_opcoes WHERE item_pedido_id = %s AND opcao_id = %s",
                    (item_pedido['id'], opcao['id'])
                )
                
                if not cursor.fetchone():  # Se a opção ainda não estiver associada
                    # Inserir a nova opção
                    cursor.execute(
                        """
                        INSERT INTO itens_pedido_opcoes (item_pedido_id, opcao_id, nome, preco_adicional)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (item_pedido['id'], opcao['id'], opcao['nome'], opcao['preco_adicional'])
                    )
            else:  # Se a opção foi desmarcada
                # Remover a opção
                cursor.execute(
                    "DELETE FROM itens_pedido_opcoes WHERE item_pedido_id = %s AND opcao_id = %s",
                    (item_pedido['id'], opcao['id'])
                )
            
            # Recalcular o subtotal do item
            cursor.execute(
                """
                UPDATE itens_pedido ip
                SET subtotal = (
                    SELECT (ip.quantidade * ip.valor_unitario) + COALESCE(SUM(ipo.preco_adicional), 0)
                    FROM itens_pedido ip2
                    LEFT JOIN itens_pedido_opcoes ipo ON ip2.id = ipo.item_pedido_id
                    WHERE ip2.id = ip.id
                    GROUP BY ip2.id
                )
                WHERE ip.id = %s
                """,
                (item_pedido['id'],)
            )
            
            self.db_connection.commit()
            
            # Atualizar a lista de itens do pedido
            self.carregar_itens_pedido(self.pedido_atual['id'])
            
            # Atualizar a tabela de itens
            self.preencher_tabela_itens()
            
            # Atualizar o total do pedido
            self.atualizar_total_pedido()
            
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Erro", f"Erro ao atualizar opção: {str(e)}")
            print(f"Erro ao atualizar opção: {str(e)}")
            
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def _mostrar_opcoes_produto(self):
        """Exibe as opções disponíveis para o produto selecionado"""
        # Obter o item selecionado
        selecionado = self.tabela_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para adicionar opções.")
            return
            
        # Obter os dados do produto selecionado
        item = self.tabela_produtos.item(selecionado[0])
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
            grupos_opcoes = opcoes_controller.listar_grupos_por_produto(produto_id)
            
            if not grupos_opcoes:
                messagebox.showinfo("Informação", "Este produto não possui opções configuradas.")
                return
                
            # Para cada grupo, buscar os itens de opção
            for grupo in grupos_opcoes:
                grupo['itens'] = opcoes_controller.listar_itens_por_grupo(grupo['id'], ativo=True)
                
            # Encontrar o produto na lista
            produto = None
            for p in self.produtos:
                if str(p['id']) == str(produto_id):
                    produto = p
                    break
            
            if not produto:
                messagebox.showerror("Erro", "Produto não encontrado.")
                return
            
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
                    self.selecoes_opcoes[grupo['id']] = {'var': var, 'tipo': 'unico'}
                    
                    for opcao in grupo['itens']:
                        rb = ttk.Radiobutton(
                            grupo_frame,
                            text=f"{opcao['nome']} (+R$ {float(opcao['preco_adicional']):.2f})",
                            variable=var,
                            value=str(opcao['id'])
                        )
                        rb.pack(anchor="w")
                else:
                    # Seleção múltipla (Checkbuttons)
                    self.selecoes_opcoes[grupo['id']] = {'var': [], 'tipo': 'multiplo'}
                    
                    for opcao in grupo['itens']:
                        var = tk.BooleanVar()
                        self.selecoes_opcoes[grupo['id']]['var'].append((var, opcao))
                        
                        cb = ttk.Checkbutton(
                            grupo_frame,
                            text=f"{opcao['nome']} (+R$ {float(opcao['preco_adicional']):.2f})",
                            variable=var
                        )
                        cb.pack(anchor="w")
            
            # Botão para confirmar as opções
            btn_confirmar = tk.Button(
                frame_principal,
                text="Confirmar Opções",
                bg=CORES['destaque'],
                fg=CORES['texto_claro'],
                padx=10,
                pady=5,
                command=lambda: self._adicionar_item_com_opcoes(produto, 1)  # Quantidade padrão 1
            )
            btn_confirmar.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
            if hasattr(self, 'janela_opcoes'):
                self.janela_opcoes.destroy()
    
    def _adicionar_item_com_opcoes(self, produto, quantidade):
        """Adiciona o produto ao pedido com as opções selecionadas"""
        try:
            # Obter as opções selecionadas
            opcoes_selecionadas = []
            preco_adicional = 0.0
            
            # Verificar se há seleções de opções
            if not hasattr(self, 'selecoes_opcoes') or not self.selecoes_opcoes:
                # Se não houver opções selecionadas, adicionar o item sem opções
                self.adicionar_item_especifico(produto, quantidade, [], 0.0)
                return
                
            for grupo_id, selecao in self.selecoes_opcoes.items():
                if selecao['tipo'] == 'unico' and selecao['var'].get():
                    # Opção única selecionada
                    opcao_id = int(selecao['var'].get())
                    # Encontrar a opção para obter o preço adicional
                    for opcao in self._obter_todas_opcoes():
                        if opcao['id'] == opcao_id:
                            opcoes_selecionadas.append({
                                'id': opcao_id,
                                'nome': opcao['nome'],
                                'preco_adicional': float(opcao['preco_adicional'])
                            })
                            preco_adicional += float(opcao['preco_adicional'])
                            break
                elif selecao['tipo'] == 'multiplo':
                    # Opções múltiplas selecionadas
                    for var_opcao in selecao['var']:
                        var, opcao = var_opcao
                        if var.get():
                            opcoes_selecionadas.append({
                                'id': opcao['id'],
                                'nome': opcao['nome'],
                                'preco_adicional': float(opcao['preco_adicional'])
                            })
                            preco_adicional += float(opcao['preco_adicional'])
            
            # Fechar a janela de opções
            if hasattr(self, 'janela_opcoes'):
                self.janela_opcoes.destroy()
            
            # Adicionar o item ao pedido com as opções
            self.adicionar_item_especifico(produto, quantidade, opcoes_selecionadas, preco_adicional)
            
            # Limpar as seleções após adicionar o item
            self.selecoes_opcoes = {}
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar item com opções: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
                opcoes = opcoes_controller.listar_opcoes_por_grupo(grupo['id'])
                todas_opcoes.extend(opcoes)
                
            return todas_opcoes
            
        except Exception as e:
            print(f"Erro ao obter opções: {str(e)}")
            return []
    
    def _calcular_total_com_desconto(self, *args):
        """Calcula o total com desconto quando o valor do desconto é alterado"""
        try:
            # Obter o valor do desconto (converter vírgula para ponto)
            desconto_texto = self.desconto_var.get().replace(',', '.')
            desconto = float(desconto_texto) if desconto_texto else 0
            
            # Calcular o subtotal (soma dos valores dos itens)
            subtotal = 0
            for item_id in self.tabela_itens.get_children():
                valores = self.tabela_itens.item(item_id, 'values')
                if len(valores) >= 4:  # Garantir que há valores suficientes
                    # O valor total está na quarta coluna (índice 3)
                    valor_texto = valores[3].replace('R$ ', '').replace('.', '').replace(',', '.')
                    subtotal += float(valor_texto)
            
            # Calcular o total (subtotal - desconto)
            total = max(0, subtotal - desconto)  # Garantir que o total não seja negativo
            
            # Atualizar os labels
            self.subtotal_valor.config(text=f"R$ {subtotal:.2f}".replace('.', ','))
            self.total_valor.config(text=f"R$ {total:.2f}".replace('.', ','))
            
        except ValueError:
            # Se o valor do desconto não for um número válido
            pass
            
    # Função calcular_total removida - não estava sendo utilizada
