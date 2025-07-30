import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import uuid
import json
from src.utils.produtos_utils import obter_tipos_produtos, criar_botoes_tipos_produtos
from ..base_module import BaseModule
from src.config.estilos import CORES, FONTES
from src.controllers.mesas_controller import MesasController
from src.controllers.opcoes_controller import OpcoesController
from src.controllers.tipos_produtos_controller import TiposProdutosController
from src.utils.impressao import GerenciadorImpressao
from src.controllers.config_controller import ConfigController
from .modoEdicaoMesas_module import ModoEdicaoMesas
from views.modulos.mostrar_opcoes_module import MostrarOpcoesModule

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
        self.tipos_controller = TiposProdutosController(db_connection=db_connection)
        self.opcoes_module = MostrarOpcoesModule(
        master=self.frame,  # ou self.root, dependendo da sua estrutura
        root_window=self.parent,  # janela principal
        callback_confirmar=self._processar_produto_com_opcoes,
        db_connection=db_connection
        )

        # Inicializa as listas vazias
        self.pedidos = []
        self.produtos = []
        self.itens_pedido = []
        self.pedido_atual = None
        
        # Lista de itens adicionados na sessão é gerenciada pelo ModoEdicaoMesas
        
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
        
        # Inicializa o gerenciador de modo de edição
        self.modo_edicao = ModoEdicaoMesas(self)
        
        # Referências para os botões que serão manipulados
        self.botao_voltar = None
        self.botao_finalizar = None
        self.botao_cancelar = None
        self.botao_confirmar = None
        
        # Referências para as barras de sobreposição
        self.barra_lateral_sobreposicao = None
        self.barra_superior_sobreposicao = None
        
        # Configurar a interface primeiro para mostrar algo ao usuário rapidamente
        self.setup_ui()
        
        # Carregar dados em segundo plano após a interface estar pronta
        self.parent.after(100, self.carregar_dados)

    def _processar_produto_com_opcoes(self, *args, **kwargs):
        """Processa o produto com as opções selecionadas"""
        try:
            # Extrai os parâmetros de args ou kwargs
            if len(args) >= 2:
                produto = args[0]
                opcoes = args[1]
            else:
                produto = kwargs.get('produto', {})
                opcoes = kwargs.get('opcoes_selecionadas', [])
            
            # Garante que opcoes seja uma lista
            opcoes = opcoes if isinstance(opcoes, list) else []
             
            # Chama o método para adicionar ao carrinho
            self._adicionar_item_com_opcoes(produto, 1, opcoes=opcoes)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao processar produto: {str(e)}")
            
    def _filtrar_produtos_por_tipo(self, tipo):
        """
        Filtra os produtos por tipo e atualiza a tabela de produtos.
        
        Args:
            tipo (dict): Dicionário com as informações do tipo de produto selecionado
        """
        try:
            self.tipo_selecionado = tipo if tipo else None
            
            # Limpar o campo de busca se existir
            if hasattr(self, 'busca_entry') and self.busca_entry.winfo_exists():
                self.busca_entry.delete(0, tk.END)
            
            # Se não houver produtos, não faz nada
            if not hasattr(self, 'produtos') or not self.produtos:
                print("Nenhum produto disponível para filtragem.")
                self.preencher_tabela_produtos([])
                return
            
            # Se for o botão "Todos", mostra todos os produtos
            if tipo and tipo.get('nome') == 'Todos' and tipo.get('id') is None:
                self.preencher_tabela_produtos(self.produtos)
                return
                
            # Usar o método _carregar_produtos para fazer a filtragem
            self._carregar_produtos(tipo)
            
        except Exception as e:
            print(f"Erro ao filtrar produtos por tipo: {e}")
            import traceback
            traceback.print_exc()
            
            # Em caso de erro, mostra lista vazia
            self.preencher_tabela_produtos([])
    
    def carregar_dados(self):
        """Carrega os dados essenciais para iniciar o módulo e agenda o carregamento dos dados restantes"""
        try:
            # Carregar pedidos da mesa
            self.carregar_pedidos()
            
            # Carregar produtos disponíveis
            if self.controller_mesas.carregar_produtos():
                # Garantir que self.produtos seja uma lista
                self.produtos = list(self.controller_mesas.produtos) if self.controller_mesas.produtos else []
                
                # Carregar tipos de produtos e criar botões dinâmicos
                try:
                    # Usar o controller para obter os tipos de produtos
                    tipos_produtos = self.tipos_controller.listar_tipos()
                    
                    # Garantir que tipos_produtos seja uma lista
                    if not isinstance(tipos_produtos, list):
                        tipos_produtos = []
                    
                    if tipos_produtos:  # Verifica se a lista não está vazia
                        criar_botoes_tipos_produtos(
                            self.tipos_frame, 
                            tipos_produtos, 
                            CORES, 
                            self._filtrar_produtos_por_tipo,
                            botoes_por_linha=5  # Definindo 5 botões por linha
                        )
                    else:
                        print("Nenhum tipo de produto encontrado.")
                except Exception as e:
                    print(f"Erro ao carregar tipos de produtos: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Preencher a tabela de produtos apenas se houver produtos
                if self.produtos:
                    self.preencher_tabela_produtos()
                else:
                    messagebox.showwarning("Aviso", "Nenhum produto cadastrado no sistema.")
            else:
                messagebox.showerror("Erro", "Não foi possível carregar os produtos.")
                self.produtos = []
            
            # Atualizar a interface
            self.atualizar_interface()
            
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
            return False
            
    def carregar_pedidos(self, manter_itens_sessao=False):
        """
        Carrega os pedidos da mesa atual usando o controller
        
        Args:
            manter_itens_sessao: Se True, mantém os itens adicionados na sessão
        """
        try:
            if self.mesa and self.controller_mesas.carregar_pedidos(self.mesa['id']):
                self.pedidos = self.controller_mesas.pedidos
                self.pedido_atual = self.controller_mesas.pedido_atual
                
                # Usar os itens do pedido do controller
                self.itens_pedido = self.controller_mesas.itens_pedido
                
                # Se não for para manter os itens da sessão, limpar a lista de itens adicionados
                if not manter_itens_sessao and hasattr(self, 'modo_edicao'):
                    self.modo_edicao.limpar_itens_sessao()
                
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
            command=self._voltar_para_mesas
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
            command=lambda: self.modo_edicao.cancelar_alteracoes() if hasattr(self, 'modo_edicao') else None
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
        container.columnconfigure(0, weight=1)  # Coluna da lista de produtos (menor largura)
        container.columnconfigure(1, weight=4)  # Coluna do carrinho (maior largura)
        
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
        
        # Botões para filtrar por tipo de produto em uma barra horizontal
        self.tipos_frame = ttk.Frame(produtos_frame)
        self.tipos_frame.pack(fill="x", pady=(0, 0))
        
        # Os botões de tipos de produtos serão carregados dinamicamente
        # quando os dados forem carregados
        
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
            text="CONFIRMAR", 
            bg=CORES["sucesso"],
            fg=CORES["texto_claro"],
            font=FONTES['subtitulo'],
            bd=0,
            padx=20,
            pady=12,
            relief='flat',
            cursor='hand2',
            command=lambda: self.modo_edicao.confirmar_alteracoes() if hasattr(self, 'modo_edicao') else None
        )
        # Usar pack com fill="x" para garantir que ocupe toda a largura, igual ao botão finalizar
        self.botao_confirmar.pack(fill="x", pady=5)
        self.botao_confirmar.pack_forget()  # Inicialmente oculto
    
    def criar_tabela_produtos(self, parent):
        """Cria a tabela de produtos disponíveis"""
        # Criação de um frame para conter a tabela e a barra de rolagem
        tabela_frame = ttk.Frame(parent)
        tabela_frame.pack(fill="both", expand=True)
        
        # Tabela de produtos com altura ajustada para aproveitar mais espaço
        colunas = ("Código", "Produto", "Preço", "Estoque")
        
        # Configurar estilo para a Treeview
        from src.config.estilos import configurar_estilo_tabelas
        style = configurar_estilo_tabelas()
        
        # Criar Treeview com estilo personalizado
        self.tabela_produtos = ttk.Treeview(
            tabela_frame, 
            columns=colunas, 
            show="headings", 
            height=20, 
            style="Produtos.Treeview"
        )
        
        # Configurar menu de contexto para a tabela de produtos (apenas opções)
        self.menu_contexto_produto = tk.Menu(self.tabela_produtos, tearoff=0)
        self.menu_contexto_produto.add_command(
            label="Adicionar ao Pedido", 
            command=self._mostrar_opcoes_produto
        )
        
        # Configurar cabeçalhos com larguras proporcionais
        larguras = {"Código": 80, "Produto": 200, "Preço": 100, "Estoque": 80}
        for col in colunas:
            self.tabela_produtos.heading(col, text=col)
            self.tabela_produtos.column(col, width=larguras.get(col, 100))
        
        # Carregar produtos do banco de dados
        try:
            self.preencher_tabela_produtos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {str(e)}")
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tabela_produtos.yview)
        self.tabela_produtos.configure(yscroll=scrollbar.set)
        
        # Empacotar widgets
        self.tabela_produtos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Vincular eventos
        self.tabela_produtos.bind("<Double-1>", lambda e: self._mostrar_opcoes_produto())
        self.tabela_produtos.bind("<Button-3>", self._mostrar_menu_contexto_produto)
        self.tabela_produtos.bind("<Return>", lambda e: self._mostrar_opcoes_produto())
        self.tabela_produtos.bind("<KeyPress>", self._on_key_press)
    
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
        
        # Ordenar produtos por nome
        produtos_ordenados = sorted(produtos_a_mostrar, key=lambda x: x.get('nome', '').lower())
        
        # Inserir produtos na tabela
        for produto in produtos_ordenados:
            # Obter o preço do produto
            preco = 0.0
            for campo in ['preco_venda', 'preco', 'valor', 'valor_unitario', 'price', 'valor_venda']:
                if campo in produto and produto[campo] is not None:
                    try:
                        preco = float(produto[campo])
                        break
                    except (ValueError, TypeError):
                        continue
            
            # Formatar preço
            preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
            
            # Obter quantidade em estoque
            estoque = str(produto.get('estoque_atual', produto.get('quantidade_estoque', produto.get('quantidade', '0'))))
            
            # Inserir na tabela
            self.tabela_produtos.insert("", "end", values=(
                str(produto.get('id', '')),
                produto.get('nome', 'Produto sem nome'),
                preco_formatado,
                estoque
            ))
        
        # Ajustar largura das colunas
        for col in self.tabela_produtos["columns"]:
            self.tabela_produtos.column(col, anchor="center" if col != "Produto" else "w")
    
    def _on_key_press(self, event):
        """Lida com eventos de teclado na tabela de produtos"""
        # Verificar se a tecla pressionada foi Enter
        if event.keysym == 'Return':
            self._mostrar_opcoes_produto()
            return 'break'  # Impedir o comportamento padrão
        
        # Permitir navegação com as setas
        if event.keysym in ('Up', 'Down', 'Left', 'Right'):
            return  # Deixar o comportamento padrão
            
        # Focar no campo de busca quando o usuário começar a digitar
        if event.char.isprintable() and not event.keysym.startswith('Control'):
            if hasattr(self, 'busca_entry') and self.busca_entry.winfo_exists():
                self.busca_entry.focus_set()
                # Inserir o caractere digitado no campo de busca
                self.busca_entry.insert(tk.INSERT, event.char)
                # Disparar a busca após um pequeno atraso para garantir que o caractere foi inserido
                self.after(10, self._buscar_produtos)
            return 'break'  # Impedir o comportamento padrão
    
    # O método selecionar_produto foi removido pois agora o duplo clique mostra as opções do produto
    
    def _mostrar_menu_contexto_produto(self, event):
        """Exibe o menu de contexto para o produto selecionado"""
        # Identificar o item clicado
        item = self.tabela_produtos.identify_row(event.y)
        if not item:
            return
            
        # Selecionar o item clicado
        self.tabela_produtos.selection_set(item)
        
        try:
            # Exibir o menu de contexto
            self.menu_contexto_produto.tk_popup(event.x_root, event.y_root)
        finally:
            # Garantir que o menu seja fechado
            self.menu_contexto_produto.grab_release()
        
    def _carregar_produtos(self, tipo=None):
        """
        Carrega todos os produtos ou filtra por tipo.
        
        Args:
            tipo (dict or str): Tipo de produto para filtrar. Pode ser um dicionário com 'id' e 'nome' ou uma string com o nome do tipo.
                              Se for None, mostra todos os produtos.
        """
        # Limpar a tabela atual
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)
            
        try:
            # Obter produtos do banco de dados se necessário
            if not hasattr(self, 'produtos') or not self.produtos:
                if not self.controller_mesas.carregar_produtos():
                    messagebox.showerror("Erro", "Não foi possível carregar os produtos.")
                    return
                self.produtos = list(self.controller_mesas.produtos) if self.controller_mesas.produtos else []
            
            # Se não houver tipo especificado, mostrar todos os produtos
            if not tipo:
                self.preencher_tabela_produtos(self.produtos)
                return
                
            # Inicializar lista de produtos filtrados
            produtos_filtrados = []
            
            # Se for um dicionário (do botão de filtro)
            if isinstance(tipo, dict):
                tipo_id = tipo.get('id')
                tipo_nome = tipo.get('nome', '').strip().lower()
                
                # Primeiro tenta filtrar por tipo_id se disponível
                if tipo_id is not None:
                    produtos_filtrados = [p for p in self.produtos if p.get('tipo_id') == tipo_id]
                    
                # Se não encontrou pelo ID ou não tem ID, tenta pelo nome
                if not produtos_filtrados and tipo_nome:
                    produtos_filtrados = [
                        p for p in self.produtos 
                        if str(p.get('tipo', '')).strip().lower() == tipo_nome
                    ]
                    
                # Se ainda não encontrou produtos, verifica se é o botão "Todos"
                if not produtos_filtrados and tipo_id is None and tipo_nome == 'todos':
                    produtos_filtrados = self.produtos
            # Se for uma string (filtro por nome)
            elif isinstance(tipo, str):
                tipo_nome = tipo.strip().lower()
                # Se for 'todos', mostra todos os produtos
                if tipo_nome == 'todos':
                    produtos_filtrados = self.produtos
                else:
                    produtos_filtrados = [
                        p for p in self.produtos 
                        if str(p.get('tipo', '')).strip().lower() == tipo_nome
                    ]
            
            # Mostrar apenas os produtos filtrados, mesmo que a lista esteja vazia
            self.preencher_tabela_produtos(produtos_filtrados)
            
        except Exception as e:
            print(f"Erro ao carregar produtos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Ocorreu um erro ao carregar os produtos: {str(e)}")
            # Em caso de erro, mostra todos os produtos
            self.preencher_tabela_produtos(self.produtos)
    
    def _buscar_produtos(self, event=None):
        """Busca produtos pelo termo digitado"""
        termo = self.busca_entry.get().strip().lower()
        
        if not termo:
            self._carregar_produtos(self.tipo_selecionado if hasattr(self, 'tipo_selecionado') else None)
            return
            
        # Limpar a tabela atual
        for item in self.tabela_produtos.get_children():
            self.tabela_produtos.delete(item)
            
        try:
            # Obter todos os produtos
            if not hasattr(self, 'produtos') or not self.produtos:
                if not self.controller_mesas.carregar_produtos():
                    messagebox.showerror("Erro", "Não foi possível carregar os produtos.")
                    return
                self.produtos = list(self.controller_mesas.produtos) if self.controller_mesas.produtos else []
            
            # Filtrar pelo termo de busca
            produtos_filtrados = [p for p in self.produtos if termo in p.get('nome', '').lower()]
                
            # Inserir na tabela
            for produto in produtos_filtrados:
                # Obter o preço do produto
                preco = 0.0
                for campo in ['preco_venda', 'preco', 'valor', 'valor_unitario', 'price', 'valor_venda']:
                    if campo in produto and produto[campo] is not None:
                        try:
                            preco = float(produto[campo])
                            break
                        except (ValueError, TypeError):
                            continue
                
                # Formatar preço
                preco_formatado = f"R$ {preco:.2f}".replace('.', ',')
                
                # Obter quantidade em estoque
                estoque = str(produto.get('estoque_atual', produto.get('quantidade_estoque', produto.get('quantidade', '0'))))
                
                # Inserir na tabela
                self.tabela_produtos.insert(
                    "", 
                    "end", 
                    values=(
                        str(produto.get('id', '')), 
                        produto.get('nome', ''), 
                        preco_formatado, 
                        estoque
                    )
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar produtos: {str(e)}")

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
        
        # Finalização direta sem confirmação
        try:
            # Definir como True para sempre liberar a mesa após finalizar o pedido
            liberar_mesa = hasattr(self, 'mesa') and bool(self.mesa)

            
            # Calcular o total do pedido
            total = self.atualizar_total_pedido()

            
            # Importar o módulo de pagamento
            from views.modulos.pagamento.pagamento_module import PagamentoModule
            
            # Preparar os itens para pagamento, garantindo que todos tenham o campo 'tipo'
            # Preparar os itens para pagamento, garantindo que todos tenham o campo 'tipo'
            itens_para_pagamento = []
            for item in self.itens_pedido:
                # Criar uma cópia do item para não modificar o original
                item_pagamento = item.copy()
                
                # Garantir que o item tenha um nome de produto
                if 'nome' not in item_pagamento and 'nome_produto' in item_pagamento:
                    item_pagamento['nome'] = item_pagamento['nome_produto']
                elif 'nome' not in item_pagamento:
                    item_pagamento['nome'] = 'Produto'
                
                # Garantir que o preço esteja no formato correto
                if 'preco' not in item_pagamento and 'valor_unitario' in item_pagamento:
                    item_pagamento['preco'] = float(item_pagamento['valor_unitario'])
                elif 'preco' not in item_pagamento:
                    item_pagamento['preco'] = 0.0
                
                # Adicionar opções ao item, se houver
                if 'opcoes' in item_pagamento and item_pagamento['opcoes']:
                    item_pagamento['opcoes'] = item_pagamento['opcoes']
                
                itens_para_pagamento.append(item_pagamento)
                        
            # Criar uma janela para o módulo de pagamento

            pagamento_window = tk.Toplevel(self.parent)
            pagamento_window.title("Pagamento - Mesa " + str(self.mesa.get('numero', '')))
            pagamento_window.geometry("1200x600")
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
                itens_venda=itens_para_pagamento,
                taxa_servico=self.taxa_servico_var.get()  # Passar o estado do checkbox da taxa de serviço
            )
            
            # Configurar evento para quando a janela for fechada
            def on_close():
                if messagebox.askokcancel("Fechar", "Deseja realmente cancelar o pagamento?"):
                    pagamento_window.destroy()
            
            pagamento_window.protocol("WM_DELETE_WINDOW", on_close)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao finalizar pedido: {str(e)}")
    
    def _processar_venda_finalizada(self, venda_dados, itens_venda, pagamentos, liberar_mesa=True):
        try:
            # Verificar se há pagamentos
            if not pagamentos:
                messagebox.showwarning("Aviso", "Nenhum pagamento registrado.")
                return False
                
            # Obter a forma de pagamento (usar a primeira se houver mais de uma)
            forma_pagamento = pagamentos[0].get('forma_nome', '')
            
            # Calcular o valor total dos pagamentos
            valor_total = sum(float(p.get('valor', 0)) for p in pagamentos)
            
            # Obter o desconto (se houver)
            desconto = float(venda_dados.get('desconto', 0))
            
            # Chamar o método do controller para finalizar o pedido
            sucesso, mensagem = self.controller_mesas.finalizar_pedido(
                forma_pagamento=forma_pagamento,
                valor_total=valor_total,
                desconto=desconto,
                pagamento=pagamentos[0],  # Passar o primeiro pagamento
                usuario_id=getattr(self.controller.usuario, 'id', None) if hasattr(self, 'controller') and hasattr(self.controller, 'usuario') else None,
                venda_dados=venda_dados
            )
            
            
            if not sucesso:
                messagebox.showinfo("Aviso", mensagem)
                return False
            
            # Limpar o pedido atual
            self.pedido_atual = None
            self.itens_pedido = []
            
            # Se a mesa foi liberada, voltar para a tela de mesas
            if liberar_mesa:
                self._voltar_para_mesas()
            else:
                # Recarregar pedidos para garantir que os dados estejam atualizados
                self.carregar_pedidos()
                
                # Atualizar interface
                self.atualizar_interface()
            
            return True  # Importante: retornar True para indicar sucesso
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao processar venda finalizada: {str(e)}")
            return False
    
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

        # Janela para inserir o motivo do cancelamento
        janela = tk.Toplevel(self.parent)
        janela.title("Motivo do Cancelamento")
        janela.transient(self.parent)
        janela.grab_set()
        
        # Centralizar a janela
        largura_janela = 500
        altura_janela = 250
        x = (janela.winfo_screenwidth() // 2) - (largura_janela // 2)
        y = (janela.winfo_screenheight() // 2) - (altura_janela // 2)
        janela.geometry(f'{largura_janela}x{altura_janela}+{x}+{y}')
        
        # Configuração do grid para expansão
        janela.columnconfigure(0, weight=1)
        janela.rowconfigure(1, weight=1)
        
        # Função para confirmar
        def confirmar():
            motivo = motivo_entry.get("1.0", tk.END).strip()
            if not motivo:
                messagebox.showwarning("Atenção", "Por favor, informe o motivo do cancelamento.")
                return
            if len(motivo) > 255:
                messagebox.showwarning("Atenção", "O motivo não pode ter mais de 255 caracteres.")
                return
                
            janela.destroy()
            
            try:
                # Chamar o método do controller para cancelar o pedido
                sucesso, mensagem = self.controller_mesas.cancelar_pedido(motivo)
                
                if sucesso:
                    # Atualizar estado local
                    self.pedido_atual = None
                    if hasattr(self, 'itens_pedido'):
                        self.itens_pedido = []
                    
                    # Atualizar a interface após um pequeno atraso
                    self.atualizar_apos_cancelamento()
                else:
                    # Mostrar mensagem de erro
                    messagebox.showerror("Erro", mensagem)
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao cancelar o pedido: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Label de instrução
        ttk.Label(main_frame, text="Informe o motivo do cancelamento:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Frame para o campo de texto com barra de rolagem
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Campo de texto para o motivo
        motivo_entry = tk.Text(text_frame, height=8, width=50, wrap=tk.WORD, 
                             yscrollcommand=scrollbar.set, 
                             font=('Arial', 10))
        motivo_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=motivo_entry.yview)
        
        # Frame para os botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.grid(row=2, column=0, pady=(10, 0), sticky="e")
        
        # Botão Confirmar
        btn_confirmar = tk.Button(
            botoes_frame, 
            text="Confirmar", 
            command=confirmar,
            bg=CORES['primaria'],  
            fg='white',  # Texto branco
            font=('Arial', 10, 'bold'),
            relief='flat',  # Sem borda 3D
            bd=0,  # Sem borda
            padx=15,  # Espaçamento horizontal interno
            pady=5,   # Espaçamento vertical interno
        )
        btn_confirmar.pack(side=tk.LEFT, padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=janela.destroy,
            bg=CORES['alerta'],  # Vermelho para ações de cancelamento
            fg='white',  # Texto branco
            font=('Arial', 10, 'bold'),
            relief='flat',  # Sem borda 3D
            bd=0,  # Sem borda
            padx=15,  # Espaçamento horizontal interno
            pady=5,   # Espaçamento vertical interno
            )
        btn_cancelar.pack(side=tk.LEFT, padx=5)
        
        # Focar no campo de texto
        motivo_entry.focus_set()
        
        # Configurar o redimensionamento
        janela.resizable(True, True)
        janela.minsize(500, 250)
        
        # Centralizar a janela novamente após configurar o tamanho mínimo
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() // 2) - (janela.winfo_width() // 2)
        y = (janela.winfo_screenheight() // 2) - (janela.winfo_height() // 2)
        janela.geometry(f"+{x}+{y}")
        
        # Trazer para frente
        janela.lift()
        janela.focus_force()
        
        # Vincular tecla Enter ao botão Confirmar e ESC ao botão Cancelar
        motivo_entry.bind("<Return>", lambda e: confirmar())
        janela.bind("<Escape>", lambda e: janela.destroy())
        
        # Esperar o fechamento da janela
        self.parent.wait_window(janela)

    def atualizar_apos_cancelamento(self):
        """
        Atualiza a interface após o cancelamento de um pedido.
        """
        try:
            # Limpa os dados do pedido atual
            self.pedido_atual = None
            self.itens_pedido = []
            
            # Mostra a mensagem de sucesso
            messagebox.showinfo("Sucesso", "Pedido cancelado e mesa liberada com sucesso!")
            
            # Usa a mesma lógica do _voltar_para_mesas para garantir consistência
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
                
                # Forçar atualização da interface
                self.parent.update_idletasks()
                
            except Exception as e:
                # Em caso de erro, tentar uma abordagem alternativa
                try:
                    if hasattr(self, 'modulo_anterior') and self.modulo_anterior:
                        self.modulo_anterior.frame.pack(fill="both", expand=True)
                except Exception as e2:
                    # Se nada mais funcionar, pelo menos tente atualizar a interface
                    self.parent.update()
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar após cancelamento: {str(e)}")
    
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
            # Chamar o método do controller para remover o item com motivo padrão
            sucesso, mensagem = self.controller_mesas.remover_item_pedido(
                item_id=item_id,
                motivo_remocao="Item removido pelo usuário"
            )
            
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
        """Método interno para voltar para a tela de mesas"""
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
            
            # Forçar atualização da interface
            self.parent.update_idletasks()
            
        except Exception as e:
            # Em caso de erro, tentar uma abordagem alternativa
            try:
                if hasattr(self, 'modulo_anterior') and self.modulo_anterior:
                    self.modulo_anterior.frame.pack(fill="both", expand=True)
            except Exception as e2:
                # Se nada mais funcionar, pelo menos tente atualizar a interface
                self.parent.update()

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
        Exibe as opções disponíveis para o produto selecionado usando o MostrarOpcoesModule
        
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
        
        # Verifica novamente se o produto foi encontrado
        if produto is None or not isinstance(produto, dict):
            messagebox.showerror("Erro", "Produto não encontrado ou inválido.")
            return
        
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        # Obter a conexão com o banco de dados do controlador principal
        db_connection = getattr(self.controller, 'db_connection', None)
        if not db_connection:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.")
            return

        # Função de callback que será chamada quando o usuário confirmar as opções
        def callback_confirmar(produto_selecionado, selecoes):
            # Adicionar o item com as opções selecionadas
            self._processar_produto_com_opcoes(produto, selecoes)
            
            # Fechar a janela de opções se ainda existir
            if hasattr(self, 'janela_opcoes') and hasattr(self.janela_opcoes, 'winfo_exists') and self.janela_opcoes.winfo_exists():
                self.janela_opcoes.destroy()

        # Criar e configurar o módulo de opções
        from views.modulos.mostrar_opcoes_module import MostrarOpcoesModule
        
        # Criar uma janela temporária para ser dona do diálogo
        temp_window = tk.Toplevel(self.parent)
        temp_window.withdraw()  # Esconder a janela temporária
        
        # Inicializar o módulo de opções
        opcoes_module = MostrarOpcoesModule(
            master=temp_window,
            root_window=self.parent,
            callback_confirmar=callback_confirmar,
            db_connection=db_connection
        )
        
        # Mostrar as opções do produto
        opcoes_module.mostrar_opcoes(produto)
        # Configurar a janela para ser fechada quando o diálogo for fechado
        temp_window.protocol("WM_DELETE_WINDOW", lambda: temp_window.destroy())
        
    
    def _adicionar_item_com_opcoes(self, produto, quantidade, usuario_id=None, opcoes=None):
        """
        Adiciona o produto ao pedido com as opções selecionadas
        """
        try:
            
            # Fazer uma cópia do dicionário do produto
            produto = produto.copy()
            
            # Se já tivermos as opções, adiciona ao pedido
            if opcoes is not None:
                # Processar as opções selecionadas
                opcoes_processadas = []
                preco_adicional = 0.0
                texto_livre = []
                
                for opcao in opcoes:
                    if not isinstance(opcao, dict):
                        continue
                    
                    # Se for texto livre
                    if opcao.get('tipo') == 'texto_livre':
                        # Adiciona o texto livre como uma opção processada
                        if 'valor' in opcao and opcao['valor'].strip():
                            texto_livre.append(opcao['valor'].strip())
                            opcoes_processadas.append({
                                'id': opcao.get('id'),
                                'tipo': 'texto_livre',
                                'nome': opcao.get('nome', 'Observação'),
                                'valor': opcao['valor'].strip(),
                                'preco_adicional': 0.0,
                                'grupo_id': opcao.get('grupo_id')
                            })
                    
                    # Se for opção normal
                    elif 'id' in opcao:
                        opcao_dict = {
                            'id': opcao['id'],
                            'tipo': opcao.get('tipo', 'opcao_simples'),
                            'nome': opcao.get('nome', ''),
                            'preco_adicional': float(opcao.get('preco_adicional', 0)),
                            'grupo_id': opcao.get('grupo_id')
                        }
                        # Se for uma opção do tipo 'opcao_simples', adiciona ao preço adicional
                        if opcao_dict['tipo'] == 'opcao_simples':
                            preco_adicional += opcao_dict['preco_adicional']
                        opcoes_processadas.append(opcao_dict)
                
                # Processar textos livres para adicionar ao nome do produto
                if texto_livre:
                    texto_obs = " - ".join(texto_livre)
                    produto['nome'] = f"{produto.get('nome', '')} ({texto_obs})"

                # Verificar se há um pedido atual, se não, criar um
                if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
                    sucesso = self.criar_novo_pedido(usuario_id=usuario_id)
                    if not sucesso:
                        messagebox.showerror("Erro", "Não foi possível criar um novo pedido")
                        return False

                # Obter o ID do usuário logado, se disponível
                if usuario_id is None and hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                    usuario_id = self.controller.usuario.id
                
                # Chamar o método do controller para adicionar o item
                sucesso, mensagem, pedido = self.controller_mesas.adicionar_item_mesa(
                    mesa_id=self.mesa['id'],
                    produto=produto,
                    quantidade=quantidade,
                    opcoes_selecionadas=opcoes_processadas,  # Inclui tanto opções normais quanto textos livres
                    preco_adicional=preco_adicional,
                    usuario_id=usuario_id
                )

                if sucesso:
                    # Atualizar a tabela de itens mantendo os itens da sessão
                    self.carregar_pedidos(manter_itens_sessao=True)
                    
                    # Ativar o modo de edição
                    if hasattr(self, 'modo_edicao'):
                        self.modo_edicao.entrar_modo_edicao()
                    return True
                else:
                    messagebox.showerror("Erro", mensagem or "Não foi possível adicionar o item ao pedido.")
                    return False

            # Se não tiver opções, exibir o diálogo de opções
            self._mostrar_opcoes_produto(produto, quantidade, usuario_id)
            return False

        except Exception as e:
            error_msg = f"Erro ao adicionar item com opções: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", error_msg)
            return False
        
    def adicionar_item(self, produto=None, quantidade=None, usuario_id=None, opcoes=None):
        """
        Adiciona um item ao pedido atual ou cria um novo pedido se necessário.
        
        Pode ser chamado com ou sem parâmetros:
        - Sem parâmetros: obtém os dados da interface
        - Com parâmetros: usa os valores fornecidos
        
        Args:
            produto: Dicionário com os dados do produto (opcional)
            quantidade: Quantidade do item (opcional)
            usuario_id: ID do usuário logado (opcional)
            opcoes: Lista de opções do produto (opcional)
            
        Returns:
            bool: True se o item foi adicionado com sucesso, False caso contrário
        """
        try:
            # Se não receber parâmetros, obtém da interface
            if produto is None:
                # Verificar se há um produto selecionado
                selecionado = self.tabela_produtos.selection()
                if not selecionado:
                    messagebox.showwarning("Aviso", "Selecione um produto para adicionar")
                    return False
                    
                # Obter o produto selecionado
                valores = self.tabela_produtos.item(selecionado[0])['values']
                if not valores or len(valores) < 2:
                    messagebox.showerror("Erro", "Dados do produto inválidos!")
                    return False
                    
                # Encontrar o produto na lista de produtos
                produto_id = int(valores[0])
                produto = next((p for p in self.produtos if p['id'] == produto_id), None)
                
                if not produto:
                    messagebox.showerror("Erro", "Produto não encontrado!")
                    return False
                    
                # Obter a quantidade
                try:
                    quantidade = int(self.quantidade_var.get())
                    if quantidade <= 0:
                        raise ValueError("Quantidade deve ser maior que zero")
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade inválida!")
                    return False
                    
                # Obter o ID do usuário logado, se disponível
                if hasattr(self.controller, 'usuario') and hasattr(self.controller.usuario, 'id'):
                    usuario_id = self.controller.usuario.id
                    
                # Se não tiver opções, verificar se o produto tem opções obrigatórias
                if opcoes is None:
                    grupos_opcoes = self.controller_mesas.obter_grupos_opcoes(produto['id'])
                    tem_opcoes_obrigatorias = any(
                        grupo.get('obrigatorio', False) 
                        for grupo in grupos_opcoes
                    )
                    
                    if grupos_opcoes and tem_opcoes_obrigatorias:
                        # Se tiver opções obrigatórias, mostrar a janela de opções
                        self._mostrar_opcoes_produto(produto, quantidade, usuario_id)
                        return True
                    opcoes = []  # Se não tiver opções obrigatórias, usa lista vazia
            
            # Verificar se há um pedido atual, se não, criar um
            if not hasattr(self, 'pedido_atual') or not self.pedido_atual:
                if not self.criar_novo_pedido(usuario_id=usuario_id):
                    messagebox.showerror("Erro", "Não foi possível criar um novo pedido")
                    return False
            
            # Chamar o método do controller para adicionar o item
            sucesso, mensagem, pedido = self.controller_mesas.adicionar_item_mesa(
                mesa_id=self.mesa['id'],
                produto=produto,
                quantidade=quantidade,
                opcoes_selecionadas=opcoes,  # Pode ser None ou lista vazia
                preco_adicional=0.0,  # O preço adicional é calculado nas opções
                usuario_id=usuario_id
            )
            
            if sucesso and pedido:
                # Atualizar a tabela de itens mantendo os itens da sessão
                self.carregar_pedidos(manter_itens_sessao=True)
                
                # Ativar o modo de edição
                if hasattr(self, 'modo_edicao'):
                    try:
                        self.modo_edicao.entrar_modo_edicao()
                    except Exception as e:
                        print(f"Erro ao ativar modo de edição: {e}")
                
                return True
            
            messagebox.showerror("Erro", mensagem or "Não foi possível adicionar o item ao pedido.")
            return False
                
        except Exception as e:
            error_msg = f"Erro ao adicionar item: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", error_msg)
            return False

    
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
                    if hasattr(self, 'modo_edicao') and hasattr(self.modo_edicao, '_sair_modo_edicao'):
                        self.modo_edicao._sair_modo_edicao(confirmar=True)
                    # Se não estiver em modo de edição, apenas atualiza a interface
                    elif hasattr(self, 'atualizar_interface'):
                        self.atualizar_interface()
                
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
