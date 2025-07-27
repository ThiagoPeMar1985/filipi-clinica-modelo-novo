
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime as dt
from pathlib import Path
import sys

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.delivery_controller import DeliveryController
from controllers.entregador_controller import EntregadorController

class StatusPedidosModule:
    def __init__(self, parent, controller, db):
        """Inicializa o módulo de status de pedidos."""
        self.parent = parent
        self.controller = controller
        self.db = db
        self.frame = ttk.Frame(parent)  # Inicializa o frame principal
        self.delivery_controller = DeliveryController()
        self.entregador_controller = EntregadorController(db)
        self.pedido_selecionado_id = None
        
        # Configuração de cores
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
        
        # Dicionário para armazenar as abas
        self.tabs = {}
        
    def show(self):
        # Limpar o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Mostrar a tela de status dos pedidos
        self._show_status_pedidos()
        
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_status_pedidos(self):
        """Mostra a tela de status dos pedidos"""
        # Criar o frame principal
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            title_frame,
            text="📊 Status dos Pedidos",
            font=('Arial', 16, 'bold')
        ).pack(side='left')
        
        # Frame para os botões de ação
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        # Botão para atualizar a lista
        tk.Button(
            btn_frame,
            text="🔄 Atualizar",
            command=self._atualizar_lista_pedidos,
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        # Botão para gerenciar entregadores
        tk.Button(
            btn_frame,
            text="🚚 Entregadores",
            command=self._gerenciar_entregadores,
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        # Criar o notebook para as abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Criar abas para cada status
        self.status_list = [
            ('em_espera', '⏳ Em Espera'),
            ('em_preparo', '👨\u200d🍳 Em Preparo'),
            ('pronto_entrega', '✅ Pronto para Entrega'),
            ('em_entrega', '🛵 Em Entrega'),
            ('entregue', '✔️ Entregue')
        ]
        
        for status_id, status_name in self.status_list:
            # Criar frame para a aba
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=status_name)
            
            # Configurar estilo para a treeview
            style = ttk.Style()
            
            # Criar um estilo personalizado para esta treeview
            style_name = f"StatusPedidos.Treeview.{status_id}"
            
            # Configurar o estilo das células
            style.configure(style_name, 
                          background="#ffffff",
                          foreground="#000000",
                          rowheight=25,
                          fieldbackground="#ffffff",
                          borderwidth=1,
                          relief="solid")
            
            # Configurar o layout para o estilo personalizado
            style.layout(style_name, [('Treeview.treearea', {'sticky': 'nswe'})])
            
            # Configurar o estilo do cabeçalho
            style.configure(f"{style_name}.Heading", 
                          font=("Arial", 10, "bold"), 
                          background=self.cores["primaria"],
                          foreground=self.cores["texto"],
                          borderwidth=1,
                          relief="solid")
            
            # Configurar cores de seleção
            style.map(style_name, 
                    background=[("selected", self.cores["primaria"])],
                    foreground=[("selected", self.cores["texto_claro"])])
            
            # Criar treeview para listar os pedidos
            columns = ("ID", "Tipo", "Cliente", "Telefone", "Itens", "Valor", "Hora Pedido")
            
            # Criar um frame para conter a treeview e as scrollbars
            tree_frame = ttk.Frame(tab_frame)
            tree_frame.grid(row=0, column=0, sticky='nsew')
            
            # Configurar o grid para expandir
            tab_frame.grid_rowconfigure(0, weight=1)
            tab_frame.grid_columnconfigure(0, weight=1)
            
            # Criar a treeview
            tree = ttk.Treeview(
                tree_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
                style=style_name
            )
            
            # Configurar colunas
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor='center')
            
            # Ajustar largura das colunas
            tree.column("ID", width=50)
            tree.column("Tipo", width=80)
            tree.column("Cliente", width=150)
            tree.column("Telefone", width=100)
            tree.column("Itens", width=250)
            tree.column("Valor", width=100)
            tree.column("Hora Pedido", width=120)
            
            # Adicionar scrollbars
            vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Posicionar os widgets usando grid dentro do tree_frame
            tree.grid(row=0, column=0, sticky='nsew')
            vsb.grid(row=0, column=1, sticky='ns')
            hsb.grid(row=1, column=0, sticky='ew')
            
            # Configurar o grid para expandir
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            # Adicionar à lista de abas
            self.tabs[status_id] = tree
            
            # Configurar o evento de clique com botão direito para exibir menu de contexto
            tree.bind("<Button-3>", lambda event, tree=tree: self._mostrar_menu_contexto(event, tree))
        
        # Criar o menu de contexto (popup)
        self._criar_menu_contexto()
        
        # Carregar dados iniciais
        self._atualizar_lista_pedidos()
    
    def _gerenciar_entregadores(self):
        """Abre a janela de gerenciamento de entregadores"""
        # Criar janela de gerenciamento de entregadores
        janela = tk.Toplevel(self.frame)
        janela.title("Gerenciar Entregadores")
        janela.geometry("800x500")
        
        # Frame principal
        main_frame = ttk.Frame(janela, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        ttk.Label(
            main_frame,
            text="🚚 Gerenciamento de Entregadores",
            font=('Arial', 14, 'bold')
        ).pack(anchor='w', pady=(0, 15))
        
        # Frame para a tabela de entregadores
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill='both', expand=True)
        
        # Criar a tabela de entregadores
        colunas = ("ID", "Nome", "Telefone", "Veículo", "Placa")
        
        # Configurar estilo personalizado para a tabela de entregadores
        style = ttk.Style()
        style_name = "Entregadores.Treeview"
        
        # Configurar o estilo das células
        style.configure(style_name, 
                      background="#ffffff",
                      foreground="#000000",
                      rowheight=25,
                      fieldbackground="#ffffff",
                      borderwidth=1,
                      relief="solid")
                      
        # Configurar o layout para o estilo personalizado
        style.layout(style_name, [('Treeview.treearea', {'sticky': 'nswe'})])
        
        # Configurar o estilo do cabeçalho
        style.configure(f"{style_name}.Heading", 
                      font=("Arial", 10, "bold"), 
                      background=self.cores["primaria"],
                      foreground=self.cores["texto"],  # Alterado para texto escuro
                      borderwidth=1,
                      relief="solid")
        
        # Configurar cores de seleção
        style.map(style_name, 
                background=[("selected", self.cores["primaria"])],
                foreground=[("selected", self.cores["texto_claro"]),
                          ("!selected", "#000000")])
        
        # Criar a treeview com o estilo personalizado
        tree = ttk.Treeview(
            table_frame,
            columns=colunas,
            show='headings',
            selectmode='browse',
            style=style_name
        )
        
        # Configurar colunas
        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Ajustar largura das colunas
        tree.column("ID", width=50)
        tree.column("Nome", width=200)
        tree.column("Telefone", width=120)
        tree.column("Veículo", width=150)
        tree.column("Placa", width=100)
        
        # Adicionar scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Posicionar a tabela e as scrollbars
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configurar o grid para expandir
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para os botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(15, 0))
        
        # Botão para adicionar entregador
        tk.Button(
            btn_frame,
            text="➕ Adicionar Entregador",
            command=lambda: self._adicionar_entregador(tree),
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        # Botão para remover entregador
        tk.Button(
            btn_frame,
            text="🗑️ Remover Selecionado",
            command=lambda: self._remover_entregador(tree),
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        # Centralizar a janela
        self._centralizar_janela(janela)
        
        # Carregar dados iniciais
        self._carregar_entregadores(tree)
    
    def _adicionar_entregador(self, tree):
        """Abre o diálogo para adicionar um novo entregador"""
        # Criar janela de diálogo para adicionar entregador
        dialog = tk.Toplevel(self.parent)
        dialog.title("Adicionar Entregador")
        dialog.resizable(False, False)
        
        # Variáveis para os campos
        nome = tk.StringVar()
        telefone = tk.StringVar()
        veiculo = tk.StringVar()
        placa = tk.StringVar()
        
        # Função para salvar o entregador
        def salvar():
            if not all([nome.get(), telefone.get(), veiculo.get(), placa.get()]):
                messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.", parent=dialog)
                return
                
            dados = {
                'nome': nome.get(),
                'telefone': telefone.get(),
                'veiculo': veiculo.get(),
                'placa': placa.get()
            }
            
            sucesso, mensagem = self.entregador_controller.adicionar_entregador(dados)
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem, parent=dialog)
                self._carregar_entregadores(tree)
                dialog.destroy()
            else:
                messagebox.showerror("Erro", mensagem, parent=dialog)
        
        # Layout do formulário
        ttk.Label(dialog, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=nome, width=30).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Telefone:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=telefone, width=30).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Veículo:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        ttk.Combobox(dialog, textvariable=veiculo, values=["Moto", "Carro", "Bicicleta", "Outro"], width=27).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Placa:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        ttk.Entry(dialog, textvariable=placa, width=30).grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # Botões
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Salvar", command=salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side='left', padx=5)
        
        # Centralizar a janela
        self._centralizar_janela(dialog)
        
        # Focar no primeiro campo
        dialog.focus_set()
        dialog.grab_set()
    
    def _remover_entregador(self, tree):
        """Remove o entregador selecionado"""
        # Obter o item selecionado na árvore
        selecionado = tree.selection()
        
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um entregador para remover.")
            return
            
        # Obter o ID do entregador selecionado
        entregador_id = tree.item(selecionado[0], 'values')[0]
        
        # Confirmar a remoção
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este entregador?"):
            # Chamar o controlador para remover o entregador
            sucesso, mensagem = self.entregador_controller.remover_entregador(entregador_id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                # Atualizar a lista de entregadores
                self._carregar_entregadores(tree)
            else:
                messagebox.showerror("Erro", mensagem)
    
    def _carregar_entregadores(self, tree):
        """Carrega a lista de entregadores na tabela a partir do banco de dados"""
        try:
            # Limpar a tabela
            for item in tree.get_children():
                tree.delete(item)
            
            # Buscar entregadores no banco de dados
            entregadores = self.entregador_controller.listar_entregadores(apenas_ativos=True)
            
            if not entregadores:
                messagebox.showinfo("Informação", "Nenhum entregador cadastrado.")
                return
            
            # Preencher a tabela com os dados do banco
            for entregador in entregadores:
                tree.insert('', 'end', values=(
                    entregador['id'],
                    entregador['nome'],
                    entregador['telefone'],
                    entregador['veiculo'],
                    entregador['placa']
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar entregadores: {str(e)}")
    
    def _centralizar_janela(self, janela):
        """Centraliza a janela na tela"""
        janela.update_idletasks()
        width = janela.winfo_width()
        height = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (width // 2)
        y = (janela.winfo_screenheight() // 2) - (height // 2)
        janela.geometry(f'{width}x{height}+{x}+{y}')
    
    def _atualizar_lista_pedidos(self):
        """Atualiza a lista de pedidos em todas as abas com dados reais do banco de dados"""        
        # Mapeamento dos status da interface para os status do banco de dados
        status_mapping = {
            'em_espera': 'PENDENTE',
            'em_preparo': 'EM_PREPARO',
            'pronto_entrega': 'PRONTO_ENTREGA',
            'em_entrega': 'EM_ROTA',
            'entregue': ['ENTREGUE', 'FINALIZADO'],  # Aceita ambos os status
            'cancelado': 'CANCELADO'
        }
        
        # Verificar se o notebook foi criado
        if not hasattr(self, 'notebook') or not self.notebook.winfo_exists():
            print("ERRO: Notebook não encontrado ou não está mais ativo")
            return
            
        # Verificar se a lista de status está disponível
        if not hasattr(self, 'status_list') or not self.status_list:
            print("ERRO: Lista de status não encontrada")
            return
        
        # Criar instância do controlador de delivery
        delivery_controller = DeliveryController()
        
        # Dicionário para armazenar a contagem de pedidos por status
        contagem_por_status = {}
        
        # Para cada aba de status, buscar os pedidos correspondentes
        for status_id, tree in self.tabs.items():
            # Limpar a árvore
            for item in tree.get_children():
                tree.delete(item)
            
            # Obter o status correspondente no banco de dados
            db_status = status_mapping.get(status_id)
            if not db_status:
                continue
                
            # Buscar pedidos com o status atual e tipo DELIVERY
            if isinstance(db_status, list):
                # Se for uma lista de status (caso de 'entregue' que pode ser 'ENTREGUE' ou 'FINALIZADO')
                pedidos = []
                for status in db_status:
                    pedidos_status = delivery_controller.listar_pedidos_por_status(status)
                    pedidos.extend([p for p in pedidos_status if p.get('tipo') == 'DELIVERY'])
            else:
                # Status único
                pedidos = delivery_controller.listar_pedidos_por_status(db_status)
                pedidos = [p for p in pedidos if p.get('tipo') == 'DELIVERY']
            
            # Remover duplicatas (pode acontecer se um pedido tiver mais de um status na lista)
            # Usamos um dicionário com o ID do pedido como chave para garantir unicidade
            pedidos_unicos = {}
            for pedido in pedidos:
                pedido_id = pedido.get('id')
                if pedido_id and pedido_id not in pedidos_unicos:
                    pedidos_unicos[pedido_id] = pedido
            
            # Converter de volta para lista
            pedidos = list(pedidos_unicos.values())
            
            # Se for a aba de entregues, filtrar apenas pedidos do dia atual
            if status_id == 'entregue':
                hoje = dt.now().date()
                pedidos = [p for p in pedidos if self._is_pedido_hoje(p, hoje)]
            
            # Armazenar a contagem de pedidos
            contagem_por_status[status_id] = len(pedidos)
            
            # Processar os pedidos encontrados
            for pedido in pedidos:
                # Formatar os dados para exibição (usando get com chave em maiúsculas)
                id_pedido = pedido.get('id', 'N/A')
                cliente = pedido.get('Cliente', pedido.get('cliente_nome', 'Cliente não informado'))
                telefone = pedido.get('Telefone', pedido.get('cliente_telefone', '--/--'))
                itens = pedido.get('Itens', 'Sem itens')
                valor_total = pedido.get('total', pedido.get('valor_total', 0))
                valor = f"R$ {float(valor_total):.2f}".replace('.', ',')
                
                # Converter a data para o formato brasileiro
                data_abertura = pedido.get('DataPedido', pedido.get('data_abertura', dt.now()))
                if isinstance(data_abertura, str):
                    # Se for string, tentar converter para datetime
                    try:
                        data_abertura = dt.strptime(data_abertura, '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        pass
                
                if hasattr(data_abertura, 'strftime'):
                    hora_pedido = data_abertura.strftime('%d/%m/%Y %H:%M')
                else:
                    hora_pedido = str(data_abertura)
                
                # Obter o tipo do pedido
                tipo_pedido = pedido.get('tipo', 'DELIVERY')
                
                # Inserir na árvore
                tree.insert('', 'end', values=(
                    id_pedido,
                    tipo_pedido,
                    cliente,
                    telefone,
                    itens[:100] + '...' if itens and len(itens) > 100 else itens,
                    valor,
                    hora_pedido
                ))
                
                # Ajustar a largura das colunas para o conteúdo
                for col in tree['columns']:
                    tree.column(col, width=100)  # Reset para largura padrão
        
        # Atualizar os títulos das abas com a contagem de pedidos
        try:
            # Atualizar cada aba com a contagem
            for i, (status_id, status_name) in enumerate(self.status_list):
                if status_id in contagem_por_status:
                    contagem = contagem_por_status[status_id]
                    novo_nome = f"{status_name} ({contagem})"
                    
                    # Atualizar o texto da aba
                    self.notebook.tab(i, text=novo_nome)
                    
        except Exception:
            pass
    
    def _is_pedido_hoje(self, pedido, data_hoje=None):
        """Verifica se um pedido foi feito hoje"""
        if data_hoje is None:
            data_hoje = dt.now().date()
            
        # Tenta obter a data do pedido de diferentes campos possíveis
        data_pedido = pedido.get('DataPedido') or pedido.get('data_abertura') or pedido.get('data_finalizacao')
        
        # Se não encontrou a data, assume que não é de hoje
        if not data_pedido:
            return False
            
        # Se for string, converter para datetime
        if isinstance(data_pedido, str):
            try:
                data_pedido = dt.strptime(data_pedido, '%Y-%m-%d %H:%M:%S')
                data_pedido = data_pedido.date()
            except ValueError:
                try:
                    data_pedido = dt.strptime(data_pedido, '%Y-%m-%d').date()
                except (ValueError, AttributeError):
                    return False
        # Se for datetime, extrair apenas a data
        elif hasattr(data_pedido, 'date'):
            data_pedido = data_pedido.date()
        
        return data_pedido == data_hoje
    
   
    
    def _mostrar_menu_contexto(self, event, tree):
        """Exibe o menu de contexto ao clicar com o botão direito em um pedido"""
        # Identificar o item clicado
        item = tree.identify_row(event.y)
        if item:
            # Selecionar o item clicado
            tree.selection_set(item)
            # Armazenar o ID do pedido selecionado
            self.pedido_selecionado_id = tree.item(item, 'values')[0]
            # Exibir o menu de contexto na posição do clique
            self.popup_menu.post(event.x_root, event.y_root)

    def _criar_menu_contexto(self):
        """Cria o menu de contexto para ações nos pedidos"""
        self.popup_menu = tk.Menu(self.frame, tearoff=0)
        
        # Opção para visualizar produtos
        self.popup_menu.add_command(
            label=" Ver Produtos do Pedido",
            command=self._ver_produtos_pedido,
            compound='left',
            image=''  # Pode adicionar um ícone aqui se desejar
        )
            
        # Opção para imprimir cupom
        self.popup_menu.add_command(
            label=" Imprimir Cupom",
            command=self._imprimir_cupom
        )
            
        # Separador
        self.popup_menu.add_separator()
            
        # Opções de status disponíveis
        status_options = [
            ('EM_PREPARO', ' Em Preparo'),
            ('PRONTO_ENTREGA', ' Pronto para Entrega'),
            ('EM_ROTA', ' Em Rota de Entrega'),
            ('ENTREGUE', ' Entregue'),
            ('CANCELADO', ' Cancelado')
        ]
            
        # Submenu para alterar status
        status_menu = tk.Menu(self.popup_menu, tearoff=0)
        for status_code, status_label in status_options:
            status_menu.add_command(
                label=status_label,
                command=lambda status=status_code: self._alterar_status_pedido(status)
                )
            
        self.popup_menu.add_cascade(label="Alterar Status", menu=status_menu)
    
    def _ver_produtos_pedido(self):
        """Exibe os produtos do pedido selecionado em uma janela com Treeview."""
        if not hasattr(self, 'pedido_selecionado_id') or not self.pedido_selecionado_id:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado.")
            return
            
        pedido_id = self.pedido_selecionado_id
        
        try:
            # Criar janela
            janela_produtos = tk.Toplevel(self.frame.master)
            janela_produtos.title(f"Produtos do Pedido #{pedido_id}")
            janela_produtos.transient(self.frame.master)
            janela_produtos.grab_set()
            
            # Tamanho e posicionamento
            largura = 500
            altura = 500
            x = (self.frame.master.winfo_screenwidth() // 2) - (largura // 2)
            y = (self.frame.master.winfo_screenheight() // 2) - (altura // 2)
            janela_produtos.geometry(f'{largura}x{altura}+{x}+{y}')
            
            # Frame principal
            frame_principal = ttk.Frame(janela_produtos)
            frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Criar Treeview com 2 colunas
            tree = ttk.Treeview(
                frame_principal,
                columns=('item', 'quantidade'),
                show='headings',
                selectmode='browse'
            )
            
            # Configurar colunas
            tree.heading('item', text='Item')
            tree.heading('quantidade', text='Qtd')
            
            # Ajustar largura das colunas
            tree.column('item', width=400, anchor='w')
            tree.column('quantidade', width=50, anchor='center')
            
            # Adicionar scrollbar
            scrollbar = ttk.Scrollbar(frame_principal, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Posicionar widgets
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Conectar ao banco de dados
            delivery_controller = DeliveryController()
            cursor = delivery_controller.db.cursor(dictionary=True)
            
            try:
                # Buscar itens do pedido
                cursor.execute("""
                    SELECT 
                        ip.id,
                        p.nome as produto_nome,
                        ip.quantidade
                    FROM itens_pedido ip
                    JOIN produtos p ON ip.produto_id = p.id
                    WHERE ip.pedido_id = %s
                    ORDER BY ip.id
                """, (pedido_id,))
                
                itens = cursor.fetchall()
                
                # Adicionar itens à árvore
                for item in itens:
                    # Adicionar o item principal
                    item_id = tree.insert(
                        "", 
                        'end',
                        values=(item['produto_nome'], item['quantidade']),
                        tags=('item_principal',)
                    )
                    
                    # Buscar opções do item atual
                    cursor.execute("""
                        SELECT nome 
                        FROM itens_pedido_opcoes 
                        WHERE item_pedido_id = %s
                        ORDER BY id
                    """, (item['id'],))
                        
                    opcoes = cursor.fetchall()
                    
                    # Adicionar opções como filhos
                    for opcao in opcoes:
                        # Mostrar o nome da opção, tratando texto livre
                        nome_opcao = opcao['nome']
                        if nome_opcao.startswith('Texto: '):
                            nome_opcao = nome_opcao[7:].strip()
                        
                        tree.insert(
                            item_id,
                            'end',
                            values=(f"  • {nome_opcao}", ""),
                            tags=('opcao_item',)
                        )
                
                # Configurar tags para estilização
                tree.tag_configure('item_principal', font=('Arial', 10, 'bold'))
                tree.tag_configure('opcao_item', font=('Arial', 9))
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar itens do pedido: {str(e)}")
            finally:
                cursor.close()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exibir produtos: {str(e)}")
    
    def _imprimir_cupom(self):
        """Imprime o cupom fiscal do pedido selecionado"""
        if not hasattr(self, 'pedido_selecionado_id') or not self.pedido_selecionado_id:
            messagebox.showwarning("Aviso", "Nenhum pedido selecionado.")
            return
        
        pedido_id = self.pedido_selecionado_id
        
        try:
            # Importar o GerenciadorImpressao
            from src.utils.impressao import GerenciadorImpressao
            from src.controllers.config_controller import ConfigController
            
            # Criar instâncias dos controladores necessários
            delivery_controller = DeliveryController()
            
            # Obter o config_controller do controlador principal
            config_controller = None
            if hasattr(self.controller, 'config_controller'):
                config_controller = self.controller.config_controller
            else:
                # Se não houver config_controller no controlador principal, criar um novo
                config_controller = ConfigController()
                
            # Carregar configurações de impressão se disponível
            if hasattr(config_controller, 'carregar_config_impressoras'):
                config_controller.carregar_config_impressoras()
                
            gerenciador_impressao = GerenciadorImpressao(config_controller=config_controller)
            
            # Buscar o pedido no banco de dados
            cursor = delivery_controller.db.cursor(dictionary=True)
            
            # Buscar dados básicos do pedido
            cursor.execute("""
                SELECT p.*, 
                       c.nome as cliente_nome, 
                       c.telefone as cliente_telefone,
                       c.endereco as cliente_endereco,
                       c.numero as cliente_numero,
                       c.bairro as cliente_bairro,
                       c.cidade as cliente_cidade,
                       c.ponto_referencia as cliente_referencia,
                       c.complemento as cliente_complemento,
                       u.nome as atendente_nome
                FROM pedidos p
                LEFT JOIN clientes_delivery c ON p.cliente_id = c.id
                LEFT JOIN usuarios u ON p.usuario_id = u.id
                WHERE p.id = %s
            """, (pedido_id,))
            
            pedido = cursor.fetchone()
            
            if not pedido:
                messagebox.showerror("Erro", f"Pedido #{pedido_id} não encontrado.")
                return
            
            # Buscar itens do pedido com os nomes dos produtos
            cursor.execute("""
                SELECT 
                    ip.id,
                    ip.pedido_id,
                    ip.produto_id,
                    ip.quantidade,
                    COALESCE(ip.valor_unitario, p.preco_venda) as valor_unitario,
                    ip.subtotal,
                    ip.observacoes,
                    p.nome as produto_nome, 
                    p.preco_venda as preco_venda,
                    p.tipo as tipo_produto
                FROM itens_pedido ip
                JOIN produtos p ON ip.produto_id = p.id
                WHERE ip.pedido_id = %s
            """, (pedido_id,))
            
            itens_brutos = cursor.fetchall()
            
            # Importar o módulo decimal para lidar com valores monetários
            from decimal import Decimal
            
            # Função auxiliar para converter para Decimal com tratamento de None
            def to_decimal(value, default=Decimal('0.00')):
                try:
                    if value is None:
                        return default
                    if isinstance(value, Decimal):
                        return value
                    return Decimal(str(value))
                except (ValueError, TypeError):
                    return default
            
            # Formatar os itens para o formato esperado pelo sistema de impressão
            itens = []
            for item in itens_brutos:
                # Usa o valor_unitario se for maior que zero, senão usa o preco_venda do produto
                valor_unitario = to_decimal(item['valor_unitario'] or item['preco_venda'])
                quantidade = item['quantidade']
                subtotal = valor_unitario * quantidade
                
                itens.append({
                    'id': item['id'],
                    'produto_id': item['produto_id'],
                    'nome': item['produto_nome'],
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'subtotal': subtotal,
                    'observacoes': item.get('observacoes', ''),
                    'tipo': item.get('tipo_produto', 'Outros')
                })
            
            # Fechar o cursor
            cursor.close()
            
            # Verificar se existem itens
            if not itens:
                messagebox.showwarning("Aviso", f"Nenhum item encontrado para o pedido #{pedido_id}.")
                return
            
            # Criar estrutura de pagamento a partir dos dados do pedido
            pagamentos = [{
                'forma_nome': pedido.get('forma_pagamento', 'Não informado').title(),
                'valor': to_decimal(pedido.get('total')),
                'troco': to_decimal(pedido.get('troco_para'))
            }]
            
            # Formatar os dados para impressão no formato que o módulo espera
            dados_impressao = {
                'id': pedido.get('id'),
                'tipo': pedido.get('tipo', 'delivery'),
                'cliente_nome': pedido.get('cliente_nome', ''),
                'cliente_telefone': pedido.get('cliente_telefone', ''),
                'endereco_entrega': f"{pedido.get('cliente_endereco', '')}, {pedido.get('cliente_numero', '')}, {pedido.get('cliente_bairro', '')}",
                'usuario_nome': pedido.get('atendente_nome', 'Não identificado'),
                'itens': itens,
                'pagamentos': pagamentos,
                'valor_total': pedido.get('total', 0),
                'taxa_entrega': pedido.get('taxa_entrega', 0),
                'troco_para': pedido.get('troco_para', 0),
                'observacoes': pedido.get('observacoes', '')
            }
            
            # Determinar se é um pedido de delivery ou não
            tipo_pedido = pedido.get('tipo', '').upper()
            
            # Imprimir o cupom fiscal ou demonstrativo de entrega
            if tipo_pedido == 'DELIVERY':
                sucesso = gerenciador_impressao.imprimir_demonstrativo_delivery(dados_impressao, itens, pagamentos)
            else:
                sucesso = gerenciador_impressao.imprimir_cupom_fiscal(dados_impressao, itens, pagamentos)
            
            if not sucesso:
                messagebox.showerror("Erro", "Não foi possível enviar o cupom para impressão.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar imprimir o cupom: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _alterar_status_pedido(self, novo_status):
        """Altera o status do pedido selecionado sem exibir alertas"""
        if not hasattr(self, 'pedido_selecionado_id') or not self.pedido_selecionado_id:
            return
        
        # Obter o ID do pedido selecionado
        pedido_id = self.pedido_selecionado_id
        
        # Criar instância do controlador de delivery
        delivery_controller = DeliveryController()
        
        # Se o novo status for 'ENTREGUE', o controlador irá converter para 'FINALIZADO'
        # Chamar o método para atualizar o status
        sucesso, _ = delivery_controller.atualizar_status_pedido(pedido_id, novo_status)
        
        # Atualizar a lista de pedidos para refletir a mudança
        if sucesso:
            # Forçar uma nova busca no banco para garantir que o status esteja atualizado
            self._atualizar_lista_pedidos()
    
