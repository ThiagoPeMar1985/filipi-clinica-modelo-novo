import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime as dt
from pathlib import Path
import sys

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from controllers.delivery_controller import DeliveryController

class StatusPedidosModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        
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
        
        # Criar o notebook para as abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Criar abas para cada status
        status_list = [
            ('em_espera', '⏳ Em Espera'),
            ('em_preparo', '👨‍🍳 Em Preparo'),
            ('pronto_entrega', '✅ Pronto para Entrega'),
            ('em_entrega', '🛵 Em Entrega'),
            ('entregue', '✔️ Entregue')
        ]
        
        for status_id, status_name in status_list:
            # Criar frame para a aba
            tab_frame = ttk.Frame(notebook)
            notebook.add(tab_frame, text=status_name)
            
            # Configurar estilo para a treeview
            style = ttk.Style()
            
            # Configurar o estilo das células
            style.configure("Treeview", 
                          background="#ffffff",
                          foreground="#000000",
                          rowheight=25,
                          fieldbackground="#ffffff",
                          borderwidth=1,
                          relief="solid")
            
            # Configurar o estilo do cabeçalho
            style.configure("Treeview.Heading", 
                          font=("Arial", 10, "bold"), 
                          background=self.cores["primaria"],
                          foreground=self.cores["texto"],
                          borderwidth=1,
                          relief="solid")
            
            # Configurar cores de seleção
            style.map("Treeview", 
                    background=[("selected", self.cores["secundaria"])],
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
                show='headings',
                selectmode='browse',
                style="Treeview"
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
    
    def _atualizar_lista_pedidos(self):
        """Atualiza a lista de pedidos em todas as abas com dados reais do banco de dados"""        
        # Mapeamento dos status da interface para os status do banco de dados
        status_mapping = {
            'em_espera': 'PENDENTE',
            'em_preparo': 'EM_PREPARO',
            'pronto_entrega': 'PRONTO_ENTREGA',
            'em_entrega': 'EM_ROTA',
            'entregue': 'ENTREGUE',
            'cancelado': 'CANCELADO'
        }
        
        # Criar instância do controlador de delivery
        delivery_controller = DeliveryController()
        
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
            pedidos = delivery_controller.listar_pedidos_por_status(db_status)
            
            # Filtrar apenas pedidos do tipo DELIVERY (segurança extra)
            pedidos = [p for p in pedidos if p.get('tipo') == 'DELIVERY']
            
            # Processar os pedidos encontrados
            
            # Adicionar os pedidos à árvore
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
    
    def _criar_menu_contexto(self):
        """Cria o menu de contexto para ações nos pedidos"""
        self.popup_menu = tk.Menu(self.frame, tearoff=0)
        
        # Adicionar opções de status
        status_options = [
            ('EM_PREPARO', '👨‍🍳 Em Preparo'),
            ('PRONTO_ENTREGA', '✅ Pronto para Entrega'),
            ('EM_ROTA', '🛵 Em Rota de Entrega'),
            ('ENTREGUE', '✔️ Entregue'),
            ('CANCELADO', '❌ Cancelado')
        ]
        
        # Submenu para alterar status
        status_menu = tk.Menu(self.popup_menu, tearoff=0)
        for status_code, status_label in status_options:
            status_menu.add_command(
                label=status_label,
                command=lambda status=status_code: self._alterar_status_pedido(status)
            )
        
        self.popup_menu.add_cascade(label="Alterar Status", menu=status_menu)
    
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
    
    def _alterar_status_pedido(self, novo_status):
        """Altera o status do pedido selecionado sem exibir alertas"""
        if not hasattr(self, 'pedido_selecionado_id') or not self.pedido_selecionado_id:
            return
        
        # Obter o ID do pedido selecionado
        pedido_id = self.pedido_selecionado_id
        
        # Criar instância do controlador de delivery
        delivery_controller = DeliveryController()
        
        # Chamar o método para atualizar o status diretamente
        sucesso, _ = delivery_controller.atualizar_status_pedido(pedido_id, novo_status)
        
        # Atualizar a lista de pedidos para refletir a mudança
        if sucesso:
            self._atualizar_lista_pedidos()
    
