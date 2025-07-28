"""
Módulo de Opções - Gerencia as opções personalizáveis dos produtos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os
import sys
from datetime import datetime

# Adicione o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Importações locais
from src.controllers.opcoes_controller import OpcoesController
from src.views.modulos.base_module import BaseModule
from src.config.estilos import CORES, FONTES

class OpcoesModule(BaseModule):
    # Dicionário para rastrear estilos já criados
    _estilos_criados = {}
    
    @classmethod
    def _criar_estilo_treeview(cls, nome_estilo):
        """Cria um estilo único para TreeView se ainda não existir."""
        if nome_estilo in cls._estilos_criados:
            return
            
        style = ttk.Style()
        
        # Cria o elemento de borda personalizado
        element_name = f'{nome_estilo}.Treeview.border'
        if not style.element_names() or element_name not in style.element_names():
            style.element_create(element_name, 'from', 'clam')
        
        # Configura o layout
        style.layout(f'{nome_estilo}.Treeview', [
            (f'{nome_estilo}.Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Configura as cores e aparência
        style.configure(f'{nome_estilo}.Treeview',
                      background='white',
                      foreground='black',
                      fieldbackground='white',
                      borderwidth=0,
                      relief='flat',
                      padding=0)
        
        # Configura as cores para o estado selecionado
        style.map(f'{nome_estilo}.Treeview',
                background=[('selected', CORES['primaria'])],
                foreground=[('selected', CORES['texto_claro'])])
        
        style.configure(f'{nome_estilo}.Treeview.Heading',
                      background='#f0f0f0',
                      foreground='black',
                      font=('Arial', 9, 'bold'),
                      borderwidth=0,
                      relief='flat')
        


        cls._estilos_criados[nome_estilo] = True
    
    def __init__(self, parent, controller, db_connection=None):
        super().__init__(parent, controller)
        
        # Inicializa o controlador
        self.controller = OpcoesController(self, db_connection)
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Frame para o conteúdo
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Variáveis de controle
        self.grupo_selecionado = None
        self.item_selecionado = None
        
        # Inicializa a interface
        self._inicializar_interface()
    
    def _inicializar_interface(self):
        """Inicializa a interface do módulo de opções."""
        # Limpa o frame de conteúdo
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        # Frame superior para os botões de ação
        frame_superior = tk.Frame(self.conteudo_frame, bg='#f0f2f5', padx=10, pady=10)
        frame_superior.pack(fill=tk.X)
        
        # Botões de ação
        btn_grupos = tk.Button(
            frame_superior,
            text="Gerenciar Grupos",
            command=self._mostrar_gerenciador_grupos,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white'
        )
        btn_grupos.pack(side=tk.LEFT, padx=5)
        
        btn_vincular = tk.Button(
            frame_superior,
            text="Vincular a Produtos",
            command=self._mostrar_vinculacao_opcoes,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white'
        )
        btn_vincular.pack(side=tk.LEFT, padx=5)
        
        # Frame principal para o conteúdo dinâmico
        self.frame_principal = tk.Frame(self.conteudo_frame, bg='#f0f2f5', padx=10, pady=10)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Mostra a tela inicial
        self._mostrar_tela_inicial()
    
    def _mostrar_tela_inicial(self):
        """Mostra a tela inicial do módulo de opções."""
        # Limpa o frame principal
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        # Título
        lbl_titulo = ttk.Label(
            self.frame_principal,
            text="Gerenciamento de Opções de Produtos",
            font=('Arial', 14, 'bold'),
            background='#f0f2f5'
        )
        lbl_titulo.pack(pady=20)
        
        # Instruções
        lbl_instrucoes = ttk.Label(
            self.frame_principal,
            text="Selecione uma das opções acima para começar.",
            font=('Arial', 10),
            background='#f0f2f5'
        )
        lbl_instrucoes.pack(pady=10)
        
        # Estatísticas (opcional)
        frame_estatisticas = tk.Frame(self.frame_principal, bg='#e9ecef', padx=20, pady=20)
        frame_estatisticas.pack(pady=20, fill=tk.X)
        
        # Aqui você pode adicionar estatísticas como:
        # - Total de grupos de opções
        # - Total de itens de opções
        # - Produtos com opções cadastradas
        # etc.
    
    def _mostrar_vinculacao_opcoes(self):
        """Mostra a tela de vinculação de opções a produtos."""
        # Inicializa o grupo selecionado como None
        self.grupo_selecionado = None
        # Limpa o conteúdo atual
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        # Título da tela
        titulo_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        titulo_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            titulo_frame, 
            text="Vincular Produtos a Grupos de Opções", 
            font=('Arial', 14, 'bold'),
            bg='#f0f2f5',
            fg='black'
        ).pack(anchor='w')
        
        # Instruções
        tk.Label(
            titulo_frame,
            text="Selecione um grupo na lista à esquerda para ver os produtos vinculados.",
            font=('Arial', 10),
            bg='#f0f2f5',
            fg='#666666'
        ).pack(anchor='w', pady=(5, 0))
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5', padx=20, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Frame para seleção de categoria
        categoria_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=5)
        categoria_frame.pack(fill='x')
        
        tk.Label(
            categoria_frame, 
            text="Selecione a Categoria:", 
            font=('Arial', 10, 'bold'),
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Variável para armazenar a categoria selecionada
        self.categoria_selecionada = tk.StringVar()

        # Busca os tipos de produtos do banco de dados
        tipos_produtos = self.controller.listar_tipos_produtos()
        
        # Verifica se encontrou tipos no banco
        if not tipos_produtos:
            messagebox.showerror(
                "Erro", 
                "Não foram encontrados tipos de produtos no banco de dados.\n"
                "Por favor, cadastre os tipos de produtos primeiro."
            )
            return
            
        # Extrai apenas os nomes dos tipos de produtos
        categorias = [tipo['nome'] for tipo in tipos_produtos if tipo.get('nome')]
        
        if not categorias:
            messagebox.showerror(
                "Erro", 
                "Nenhum tipo de produto válido encontrado.\n"
                "Verifique se os tipos de produtos estão corretamente cadastrados."
            )
            return
        
        # Combobox para selecionar a categoria
        categoria_cb = ttk.Combobox(
            categoria_frame,
            textvariable=self.categoria_selecionada,
            values=categorias,
            state='readonly',
            width=30
        )
        categoria_cb.pack(side='left', padx=5)
        
        # Define o primeiro item como selecionado por padrão, se existir
        if categorias:
            categoria_cb.set(categorias[0])
            
        # Atualiza a lista de produtos quando a categoria for alterada
        categoria_cb.bind('<<ComboboxSelected>>', lambda e: self._carregar_produtos_por_categoria())
        
        # Frame para seleção de produto
        produto_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=5)
        produto_frame.pack(fill='x')
        
        tk.Label(
            produto_frame, 
            text="Selecione o Produto:", 
            font=('Arial', 10, 'bold'),
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        ).pack(side='left', padx=5)
        
        # Variável para armazenar o produto selecionado
        self.produto_selecionado = tk.StringVar()
        
        # Combobox para selecionar o produto (será preenchido após selecionar a categoria)
        self.produtos_cb = ttk.Combobox(
            produto_frame,
            textvariable=self.produto_selecionado,
            state="readonly",
            width=60,
            font=('Arial', 10)
        )
        self.produtos_cb.pack(side='left', padx=5)
        
        # Estilo para a combobox
        style = ttk.Style()
        style.configure('TCombobox', padding=5, relief='flat', font=('Arial', 10))
        
        # Container principal para as tabelas
        container = tk.Frame(main_frame, bg='#f0f2f5')
        container.pack(fill='both', expand=True, pady=(10, 0))
        
        # Frame para a tabela de grupos disponíveis (lado esquerdo)
        disponiveis_frame = tk.Frame(container, bg='#f0f2f5', padx=10, pady=10, width=300)
        disponiveis_frame.pack(side='left', fill='y', expand=False, padx=(0, 5))
        disponiveis_frame.pack_propagate(False)  # Impede que o frame redimensione automaticamente
        
        # Título da tabela de grupos disponíveis
        tk.Label(
            disponiveis_frame, 
            text="Grupos",
            font=('Arial', 10, 'bold'),
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        ).pack(fill='x', pady=(0, 5))
        
        # Frame para a tabela e barra de rolagem
        tabela_container = tk.Frame(disponiveis_frame, bg='#f0f2f5')
        tabela_container.pack(fill='both', expand=True)
        
        # Configura os estilos para a tela de vinculação
        style = ttk.Style()
        
        # Cria estilos únicos para as Treeviews
        self._criar_estilo_treeview('VinculacaoGrupo')
        self._criar_estilo_treeview('VinculacaoGrupoVinculados')
        
        # Inicializa a lista de grupos disponíveis
        colunas_grupos_disponiveis = ('id', 'nome')
        self.lista_grupos_disponiveis = ttk.Treeview(
            tabela_container,
            columns=colunas_grupos_disponiveis,
            show='headings',
            selectmode='extended',
            style='VinculacaoGrupo.Treeview',
            height=15
        )
        
        # Configura as colunas
        self.lista_grupos_disponiveis.heading('id', text='ID')
        self.lista_grupos_disponiveis.heading('nome', text='Nome do Grupo')
        
        # Configura a largura das colunas
        self.lista_grupos_disponiveis.column('id', width=50, anchor='center')
        self.lista_grupos_disponiveis.column('nome', width=300, anchor='w')
        
        # Adiciona a barra de rolagem
        scrollbar_disponiveis = ttk.Scrollbar(tabela_container, orient='vertical', command=self.lista_grupos_disponiveis.yview)
        self.lista_grupos_disponiveis.configure(yscrollcommand=scrollbar_disponiveis.set)
        
        # Empacota a tabela e a barra de rolagem
        self.lista_grupos_disponiveis.pack(side='left', fill='both', expand=True)
        scrollbar_disponiveis.pack(side='right', fill='y')
        
        # Frame para os botões de ação
        botoes_disponiveis_frame = tk.Frame(disponiveis_frame, bg='#f0f2f5', pady=5)
        botoes_disponiveis_frame.pack(fill='x')
        
        # Botão para adicionar grupos
        btn_adicionar = tk.Button(
            botoes_disponiveis_frame,
            text="Adicionar Selecionados",
            command=self._vincular_produto_ao_grupo,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white',
            width=20
        )
        btn_adicionar.pack(side='left', padx=5)
        
        # Frame para a tabela de grupos vinculados (lado direito)
        vinculados_frame = tk.Frame(container, bg='#f0f2f5', padx=10, pady=10)
        vinculados_frame.pack(side='right', fill='both', expand=True)
        
        # Título da tabela de grupos vinculados
        tk.Label(
            vinculados_frame, 
            text="Produtos Vinculados ao Grupo",
            font=('Arial', 10, 'bold'),
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        ).pack(fill='x', pady=(0, 5))
        
        # Frame para a tabela e barra de rolagem
        tabela_vinculados_container = tk.Frame(vinculados_frame, bg='#f0f2f5')
        tabela_vinculados_container.pack(fill='both', expand=True)
        
        # Inicializa a lista de grupos vinculados
        colunas_vinculados = ('id', 'nome', 'obrigatorio')
        self.lista_grupos_vinculados = ttk.Treeview(
            tabela_vinculados_container,
            columns=colunas_vinculados,
            show='headings',
            selectmode='extended',
            style='VinculacaoGrupo.Treeview',
            height=15
        )
        
        # Configura as colunas
        self.lista_grupos_vinculados.heading('id', text='ID')
        self.lista_grupos_vinculados.heading('nome', text='Nome do Produto')
        self.lista_grupos_vinculados.heading('obrigatorio', text='Obrigatório')
        
        # Configura a largura das colunas
        self.lista_grupos_vinculados.column('id', width=50, anchor='center')
        self.lista_grupos_vinculados.column('nome', width=250, anchor='w')
        self.lista_grupos_vinculados.column('obrigatorio', width=80, anchor='center')
        
        # Adiciona a barra de rolagem
        scrollbar_vinculados = ttk.Scrollbar(
            tabela_vinculados_container, 
            orient='vertical', 
            command=self.lista_grupos_vinculados.yview
        )
        self.lista_grupos_vinculados.configure(yscrollcommand=scrollbar_vinculados.set)
        
        # Empacota a tabela e a barra de rolagem
        self.lista_grupos_vinculados.pack(side='left', fill='both', expand=True)
        scrollbar_vinculados.pack(side='right', fill='y')
        
        # Frame para os botões de ação dos grupos vinculados
        botoes_vinculados_frame = tk.Frame(vinculados_frame, bg='#f0f2f5', pady=5)
        botoes_vinculados_frame.pack(fill='x')
        
        # Botão para alternar status de obrigatório
        btn_alternar_obrigatorio = tk.Button(
            botoes_vinculados_frame,
            text="Alternar Obrigatório",
            command=self._alternar_obrigatorio,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white',
            width=15
        )
        btn_alternar_obrigatorio.pack(side='left', padx=5)
        
        # Botão para remover grupos
        btn_remover_grupo = tk.Button(
            botoes_vinculados_frame,
            text="Remover Selecionado",
            command=self._remover_vinculo_produto,
            bg='#F44336',
            fg='white',
            font=('Arial', 9, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#D32F2F',
            activeforeground='white',
            width=15
        )
        btn_remover_grupo.pack(side='left', padx=5)
        
        # Carrega os produtos da categoria selecionada
        self._carregar_produtos_por_categoria()
        
        # Carrega os grupos disponíveis
        self._carregar_grupos_disponiveis()
        
        # Frame para os botões de ação principais
        botoes_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=20)
        botoes_frame.pack(fill='x')
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame,
            text="Salvar Alterações",
            command=self._salvar_vinculos_grupo_produto,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#43A047',
            activeforeground='white',
            width=20
        )
        btn_salvar.pack(side='right', padx=10)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame,
            text="Cancelar",
            command=self._mostrar_tela_inicial,
            bg='#F44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#D32F2F',
            activeforeground='white',
            width=20
        )
        btn_cancelar.pack(side='right')
        
        # Inicializa as variáveis
        self.grupos_disponiveis = []
        self.grupos_vinculados = []
    
    def _mostrar_gerenciador_grupos(self):
        """Mostra o gerenciador de grupos de opções."""
        # Limpa o frame principal
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        # Frame principal com grid para dividir a tela em 2 colunas iguais
        frame_principal = tk.Frame(self.frame_principal, bg='#f0f2f5')
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar o grid para ter 2 colunas com pesos iguais
        frame_principal.columnconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.rowconfigure(0, weight=1)
        
        # Frame para os grupos (lado esquerdo)
        frame_grupos = tk.Frame(frame_principal, bg='#f0f2f5', padx=5, pady=5, bd=0, relief='flat')
        frame_grupos.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Configurar o grid para o frame de grupos
        frame_grupos.columnconfigure(0, weight=1)
        frame_grupos.rowconfigure(1, weight=1)
        
        # Título dos grupos
        ttk.Label(
            frame_grupos,
            text="Grupos de Opções",
            font=('Arial', 10, 'bold'),
            background='#f0f2f5'
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Frame para a árvore e barra de rolagem dos grupos
        tree_frame_grupos = tk.Frame(frame_grupos, bg='#f0f2f5')
        tree_frame_grupos.grid(row=1, column=0, sticky='nsew')
        tree_frame_grupos.columnconfigure(0, weight=1)
        tree_frame_grupos.rowconfigure(0, weight=1)
        
        # Cria estilos únicos para as Treeviews de gerenciamento
        self._criar_estilo_treeview('GerenciamentoGrupo')
        self._criar_estilo_treeview('GerenciamentoItens')
        
        # Lista de grupos
        self.lista_grupos = ttk.Treeview(
            tree_frame_grupos,
            columns=('id', 'nome'),
            show='headings',
            selectmode='browse',
            height=15,
            style='GerenciamentoGrupo.Treeview'  # Estilo específico para grupos
        )
        
        self.lista_grupos.heading('id', text='ID')
        self.lista_grupos.heading('nome', text='Nome')
        self.lista_grupos.column('id', width=40, anchor=tk.CENTER)
        self.lista_grupos.column('nome', width=200, anchor=tk.W)
        self.lista_grupos.grid(row=0, column=0, sticky='nsew')
        
        # Configura o evento de seleção
        self.lista_grupos.bind('<<TreeviewSelect>>', self._carregar_itens_do_grupo)
        
        # Barra de rolagem vertical
        scrollbar_y = ttk.Scrollbar(
            tree_frame_grupos,
            orient='vertical',
            command=self.lista_grupos.yview
        )
        self.lista_grupos.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        
        # Barra de rolagem horizontal
        scrollbar_x = ttk.Scrollbar(
            tree_frame_grupos,
            orient='horizontal',
            command=self.lista_grupos.xview
        )
        self.lista_grupos.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        # Botões de ação para grupos
        frame_botoes_grupo = tk.Frame(frame_grupos, bg='#f0f2f5', pady=5)
        frame_botoes_grupo.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        btn_novo_grupo = tk.Button(
            frame_botoes_grupo,
            text="Novo Grupo",
            command=self._criar_novo_grupo,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#43a047',
            activeforeground='white',
            width=15
        )
        btn_novo_grupo.pack(side=tk.LEFT, padx=5)
        
        btn_editar_grupo = tk.Button(
            frame_botoes_grupo,
            text="Editar",
            command=self._editar_grupo,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white',
            width=10
        )
        btn_editar_grupo.pack(side=tk.LEFT, padx=5)
        
        btn_excluir_grupo = tk.Button(
            frame_botoes_grupo,
            text="Excluir",
            command=self._excluir_grupo,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#d32f2f',
            activeforeground='white',
            width=10
        )
        btn_excluir_grupo.pack(side=tk.LEFT, padx=5)
        
        # Frame para os itens (lado direito)
        frame_itens = tk.Frame(frame_principal, bg='#f0f2f5', padx=5, pady=5, bd=0, relief='flat')
        frame_itens.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Configurar o grid para o frame de itens
        frame_itens.columnconfigure(0, weight=1)
        frame_itens.rowconfigure(1, weight=1)
        
        # Título dos itens
        ttk.Label(
            frame_itens,
            text="Itens do Grupo",
            font=('Arial', 10, 'bold'),
            background='#f0f2f5'
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Frame para a árvore e barra de rolagem dos itens
        tree_frame_itens = tk.Frame(frame_itens, bg='#f0f2f5')
        tree_frame_itens.grid(row=1, column=0, sticky='nsew')
        tree_frame_itens.columnconfigure(0, weight=1)
        tree_frame_itens.rowconfigure(0, weight=1)
        
        # Lista de itens com estilo personalizado
        self.lista_itens = ttk.Treeview(
            tree_frame_itens,
            columns=('id', 'nome', 'preco'),
            show='headings',
            selectmode='browse',
            height=15,
            style='GerenciamentoItens.Treeview'  # Estilo específico para itens
        )
        self.lista_itens.heading('id', text='ID')
        self.lista_itens.heading('nome', text='Nome')
        self.lista_itens.heading('preco', text='Preço Adicional')
        self.lista_itens.column('id', width=40, anchor=tk.CENTER)
        self.lista_itens.column('nome', width=200, anchor=tk.W)
        self.lista_itens.column('preco', width=100, anchor=tk.E)
        self.lista_itens.grid(row=0, column=0, sticky='nsew')
        
        # Configura o evento de seleção para atualizar o item selecionado
        def _atualizar_item_selecionado(event):
            selecionado = self.lista_itens.selection()
            if selecionado:
                item = self.lista_itens.item(selecionado[0])
                self.item_selecionado = item['values'][0]
            else:
                self.item_selecionado = None
                
        self.lista_itens.bind('<<TreeviewSelect>>', _atualizar_item_selecionado)
        
        # Barra de rolagem vertical
        scrollbar_y = ttk.Scrollbar(
            tree_frame_itens,
            orient='vertical',
            command=self.lista_itens.yview
        )
        self.lista_itens.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        
        # Barra de rolagem horizontal
        scrollbar_x = ttk.Scrollbar(
            tree_frame_itens,
            orient='horizontal',
            command=self.lista_itens.xview
        )
        self.lista_itens.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        # Botões de ação para itens
        frame_botoes_item = tk.Frame(frame_itens, bg='#f0f2f5', pady=5)
        frame_botoes_item.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        btn_novo_item = tk.Button(
            frame_botoes_item,
            text="Novo Item",
            command=self._criar_novo_item,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#43a047',
            activeforeground='white',
            width=15
        )
        btn_novo_item.pack(side=tk.LEFT, padx=5)
        
        btn_editar_item = tk.Button(
            frame_botoes_item,
            text="Editar",
            command=self._editar_item,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white',
            width=10
        )
        btn_editar_item.pack(side=tk.LEFT, padx=5)
        
        btn_excluir_item = tk.Button(
            frame_botoes_item,
            text="Excluir",
            command=self._excluir_item,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            activebackground='#d32f2f',
            activeforeground='white',
            width=10
        )
        btn_excluir_item.pack(side=tk.LEFT, padx=5)
        
        # Carrega os grupos
        self._carregar_grupos()
    
    def _carregar_grupos(self):
        """Carrega a lista de grupos do controlador e exibe na lista de grupos."""
        # Limpa a lista de grupos
        for item in self.lista_grupos.get_children():
            self.lista_grupos.delete(item)
        
        # Obtém os grupos do controlador
        grupos = self.controller.listar_grupos()
        
        # Adiciona cada grupo à lista
        for grupo in grupos:
            self.lista_grupos.insert('', 'end', values=(
                grupo['id'],
                grupo['nome']
            ))
    
    def _carregar_itens_do_grupo(self, event=None):
        """Carrega os itens do grupo selecionado para edição.
        
        Args:
            event: Evento de seleção da TreeView (opcional)
        """
        # Obtém o item selecionado
        selecionado = self.lista_grupos.selection()
        
        if not selecionado:
            self.grupo_selecionado = None
            self._limpar_lista_itens()
            return
        
        # Obtém os dados do grupo
        item = self.lista_grupos.item(selecionado[0])
        grupo_id = item['values'][0]
        self.grupo_selecionado = grupo_id
        
        # Limpa a lista de itens
        self._limpar_lista_itens()
        
        # Busca os itens do grupo no banco de dados
        itens = self.controller.listar_itens_por_grupo(grupo_id)
        
        # Preenche a lista de itens
        for item in itens:
            # Define o tipo de opção para exibição
            tipo = item.get('tipo', 'opcao_simples')
            tipo_exibicao = 'Texto Livre' if tipo == 'texto_livre' else 'Opção Simples'
            
            self.lista_itens.insert('', 'end', values=(
                item['id'],
                f"{item['nome']} ({tipo_exibicao})",
                f"R$ {item['preco_adicional']:.2f}" if item['preco_adicional'] and item['preco_adicional'] > 0 else ""
            ))

    def _limpar_lista_itens(self):
        """Limpa a lista de itens."""
        for item in self.lista_itens.get_children():
            self.lista_itens.delete(item)
    
    def _criar_novo_grupo(self):
        """Abre o formulário para criar um novo grupo de opções."""
        self._abrir_formulario_grupo()
    
    def _editar_grupo(self):
        """Abre o formulário para editar o grupo selecionado."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para editar.")
            return
            
        self._abrir_formulario_grupo(self.grupo_selecionado)
    
    def _excluir_grupo(self):
        """Exclui o grupo selecionado."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para excluir.")
            return
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este grupo?"):
            return
        
        # Exclui o grupo
        if self.controller.excluir_grupo(self.grupo_selecionado):
            messagebox.showinfo("Sucesso", "Grupo excluído com sucesso!")
            self._carregar_grupos()
        else:
            messagebox.showerror("Erro", "Não foi possível excluir o grupo.")
    
    def _criar_novo_item(self):
        """Abre o formulário para criar um novo item."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para adicionar itens.")
            return
        
        # Abre o formulário de item em uma janela modal
        self._abrir_formulario_item()
    
    def _editar_item(self):
        """Abre o formulário para editar o item selecionado."""
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para editar.")
            return
        
        self._abrir_formulario_item(self.item_selecionado)
    
    def _excluir_item(self):
        """Exclui o item selecionado."""
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para excluir.")
            return
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este item?"):
            return
        
        # Exclui o item
        if self.controller.excluir_item(self.item_selecionado):
            messagebox.showinfo("Sucesso", "Item excluído com sucesso!")
            self._carregar_itens_do_grupo()
        else:
            messagebox.showerror("Erro", "Não foi possível excluir o item.")
    
    def _abrir_formulario_grupo(self, grupo_id=None):
        """Abre o formulário de grupo."""
        # Cria a janela de diálogo
        dialog = tk.Toplevel(self.frame, bg='#f0f2f5')
        dialog.title("Novo Grupo de Opções" if grupo_id is None else "Editar Grupo de Opções")
        dialog.transient(self.frame)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Define o tamanho da janela
        largura = 500
        altura = 600
        x = (dialog.winfo_screenwidth() // 2) - (largura // 2)
        y = (dialog.winfo_screenheight() // 2) - (altura // 2)
        dialog.geometry(f'{largura}x{altura}+{x}+{y}')
        
        # Cria um canvas com barra de rolagem
        canvas = tk.Canvas(dialog, bg='#f0f2f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f2f5')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empacota o canvas e a barra de rolagem
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal dentro do canvas
        main_frame = tk.Frame(scrollable_frame, bg='#f0f2f5', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título do formulário
        titulo = "Novo Grupo de Opções" if grupo_id is None else "Editar Grupo de Opções"
        lbl_titulo = tk.Label(
            main_frame, 
            text=titulo, 
            font=('Arial', 14, 'bold'), 
            bg='#f0f2f5',
            fg='black'
        )
        lbl_titulo.pack(anchor='w', pady=(0, 20))
        
        # Dados do formulário
        dados = {}
        
        # Se for edição, carrega os dados do grupo
        if grupo_id:
            grupo = self.controller.obter_grupo(grupo_id)
            if grupo:
                dados = grupo
        
        # Frame para os campos do formulário
        campos_frame = tk.Frame(main_frame, bg='#f0f2f5')
        campos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campo Nome do Grupo
        lbl_nome = tk.Label(
            campos_frame, 
            text="Nome do Grupo:", 
            font=('Arial', 10), 
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        )
        lbl_nome.pack(fill=tk.X, pady=(0, 5))
        
        nome_var = tk.StringVar(value=dados.get('nome', ''))
        entry_nome = tk.Entry(
            campos_frame, 
            textvariable=nome_var, 
            font=('Arial', 10),
            bd=0,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#cccccc',
            highlightcolor='#4a6fa5',
            width=40
        )
        entry_nome.pack(fill=tk.X, pady=(0, 15))
        
        # Campo Descrição
        lbl_descricao = tk.Label(
            campos_frame, 
            text="Descrição:", 
            font=('Arial', 10), 
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        )
        lbl_descricao.pack(fill=tk.X, pady=(0, 5))
        
        descricao_text = tk.Text(
            campos_frame, 
            width=40, 
            height=5,
            font=('Arial', 10),
            bd=0,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#cccccc',
            highlightcolor='#4a6fa5',
            wrap=tk.WORD
        )
        descricao_text.insert('1.0', dados.get('descricao', ''))
        descricao_text.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para as opções
        frame_opcoes = tk.LabelFrame(
            campos_frame, 
            text="Configurações", 
            font=('Arial', 10, 'bold'),
            bg='#f0f2f5',
            fg='black',
            bd=0,
            relief='solid',
            padx=10,
            pady=10
        )
        frame_opcoes.pack(fill=tk.X, pady=(0, 15))
        
        # Checkbox para obrigatório
        obrigatorio_var = tk.BooleanVar(value=dados.get('obrigatorio', False))
        check_obrigatorio = tk.Checkbutton(
            frame_opcoes, 
            text="Obrigatório", 
            variable=obrigatorio_var,
            font=('Arial', 10),
            bg='#f0f2f5',
            activebackground='#f0f2f5',
            selectcolor='#f0f2f5'
        )
        check_obrigatorio.pack(anchor='w', pady=(0, 10))
        
        # Frame para seleção mínima
        frame_selecao_min = tk.Frame(frame_opcoes, bg='#f0f2f5')
        frame_selecao_min.pack(fill=tk.X, pady=(0, 5))
        
        lbl_selecao_min = tk.Label(
            frame_selecao_min,
            text="Seleção Mínima:",
            font=('Arial', 10),
            bg='#f0f2f5',
            fg='black',
            anchor='w',
            width=15
        )
        lbl_selecao_min.pack(side=tk.LEFT)
        
        selecao_min_var = tk.IntVar(value=dados.get('selecao_minima', 0))
        spin_selecao_min = ttk.Spinbox(
            frame_selecao_min,
            from_=0,
            to=10,
            width=5,
            textvariable=selecao_min_var,
            font=('Arial', 10)
        )
        spin_selecao_min.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para seleção máxima
        frame_selecao_max = tk.Frame(frame_opcoes, bg='#f0f2f5')
        frame_selecao_max.pack(fill=tk.X, pady=(0, 5))
        
        lbl_selecao_max = tk.Label(
            frame_selecao_max,
            text="Seleção Máxima:",
            font=('Arial', 10),
            bg='#f0f2f5',
            fg='black',
            anchor='w',
            width=15
        )
        lbl_selecao_max.pack(side=tk.LEFT)
        
        selecao_max_var = tk.IntVar(value=dados.get('selecao_maxima', 1))
        spin_selecao_max = ttk.Spinbox(
            frame_selecao_max,
            from_=1,
            to=10,
            width=5,
            textvariable=selecao_max_var,
            font=('Arial', 10)
        )
        spin_selecao_max.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para os botões
        botoes_frame = tk.Frame(main_frame, bg='#f0f2f5')
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
       
    
        
       
        # Função para salvar o grupo
        def _salvar_grupo():
            dados_grupo = {
                'id': grupo_id,
                'nome': nome_var.get().strip(),
                'descricao': descricao_text.get('1.0', tk.END).strip(),
                'obrigatorio': obrigatorio_var.get(),
                'selecao_minima': selecao_min_var.get(),
                'selecao_maxima': max(selecao_max_var.get(), selecao_min_var.get())
            }
            
            if not dados_grupo['nome']:
                messagebox.showwarning("Atenção", "O nome do grupo é obrigatório.")
                return
                
            if self.controller.salvar_grupo(dados_grupo):
                messagebox.showinfo("Sucesso", "Grupo salvo com sucesso!")
                dialog.destroy()
                self._carregar_grupos()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o grupo.")
            
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: _salvar_grupo(),
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#43a047',
            activeforeground='white',
            width=15
        )
        btn_salvar.pack(side=tk.RIGHT, padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=dialog.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#d32f2f',
            activeforeground='white',
            width=15
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)

    def _abrir_formulario_item(self, item_id=None):
        """Abre o formulário de item de opção."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para adicionar itens.")
            return
            
        # Cria a janela de diálogo
        dialog = tk.Toplevel(self.frame, bg='#f0f2f5')
        dialog.title("Novo Item de Opção" if item_id is None else "Editar Item de Opção")
        dialog.transient(self.frame)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Define o tamanho da janela
        largura = 600
        altura = 450
        x = (dialog.winfo_screenwidth() // 2) - (largura // 2)
        y = (dialog.winfo_screenheight() // 2) - (altura // 2)
        dialog.geometry(f'{largura}x{altura}+{x}+{y}')
        
        # Cria um canvas com barra de rolagem
        canvas = tk.Canvas(dialog, bg='#f0f2f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f2f5')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empacota o canvas e a barra de rolagem
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal dentro do canvas
        main_frame = tk.Frame(scrollable_frame, bg='#f0f2f5', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título do formulário
        titulo = "Novo Item de Opção" if item_id is None else "Editar Item de Opção"
        lbl_titulo = tk.Label(
            main_frame, 
            text=titulo, 
            font=('Arial', 14, 'bold'), 
            bg='#f0f2f5',
            fg='black'
        )
        lbl_titulo.pack(anchor='w', pady=(0, 20))
        
        # Dados do formulário
        dados = {}
        
        # Se for edição, carrega os dados do item
        if item_id:
            itens = self.controller.listar_itens_por_grupo(self.grupo_selecionado)
            for item in itens:
                if item['id'] == item_id:
                    dados = item
                    break
        
        # Frame para os campos do formulário
        campos_frame = tk.Frame(main_frame, bg='#f0f2f5')
        campos_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campo Nome do Item
        lbl_nome = tk.Label(
            campos_frame, 
            text="Nome do Item:", 
            font=('Arial', 10, 'bold'), 
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        )
        lbl_nome.pack(anchor='w', pady=(0, 5))
        
        nome_var = tk.StringVar(value=dados.get('nome', ''))
        entry_nome = tk.Entry(
            campos_frame, 
            textvariable=nome_var, 
            font=('Arial', 10),
            bd=0,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#cccccc',
            highlightcolor='#4a6fa5',
            width=50
        )
        entry_nome.pack(fill=tk.X, pady=(0, 15))
        
        # Campo Descrição
        lbl_descricao = tk.Label(
            campos_frame, 
            text="Descrição:", 
            font=('Arial', 10, 'bold'), 
            bg='#f0f2f5',
            fg='black',
            anchor='w'
        )
        lbl_descricao.pack(anchor='w', pady=(0, 5))
        
        descricao_text = tk.Text(
            campos_frame, 
            width=50, 
            height=5,
            font=('Arial', 10),
            bd=0,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#cccccc',
            highlightcolor='#4a6fa5',
            wrap=tk.WORD
        )
        descricao_text.insert('1.0', dados.get('descricao', ''))
        descricao_text.pack(fill=tk.X, pady=(0, 15))
        
        # Frame para preço
        frame_preco = tk.Frame(campos_frame, bg='#f0f2f5')
        frame_preco.pack(fill=tk.X, pady=(0, 15))
            
        # Rótulo do preço
        lbl_preco = tk.Label(
            frame_preco, 
            text="Preço Adicional:", 
            font=('Arial', 10, 'bold'), 
            bg='#f0f2f5',
            fg='black',
            width=15,
            anchor='w'
        )
        lbl_preco.pack(side=tk.LEFT)
            
        # Símbolo de moeda
        lbl_rs = tk.Label(
            frame_preco, 
            text="R$", 
            font=('Arial', 10), 
            bg='#f0f2f5',
            fg='black',
            width=3,
            anchor='e'
        )
        lbl_rs.pack(side=tk.LEFT, padx=(0, 5))
            
        # Campo de entrada do preço
        preco_var = tk.DoubleVar(value=float(dados.get('preco_adicional', 0)))
        entry_preco = tk.Entry(
            frame_preco,
            textvariable=preco_var,
            font=('Arial', 10),
            bd=0,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#cccccc',
            highlightcolor='#4a6fa5',
            width=15,
            justify='right'
        )
        entry_preco.pack(side=tk.LEFT)
            
        # Frame para o tipo de opção
        frame_tipo = tk.Frame(main_frame, bg='#f0f2f5')
        frame_tipo.pack(fill=tk.X, pady=(0, 15))
        
        # Variável para o tipo de opção
        tipo_var = tk.StringVar(value=dados.get('tipo', 'opcao_simples'))
        
        # Rótulo do tipo de opção
        lbl_tipo = tk.Label(
            frame_tipo, 
            text="Tipo de Opção:", 
            font=('Arial', 10, 'bold'), 
            bg='#f0f2f5',
            fg='black',
            width=15,
            anchor='w'
        )
        lbl_tipo.pack(side=tk.LEFT)
        
        # Opção Simples
        rb_opcao_simples = tk.Radiobutton(
            frame_tipo,
            text="Opção Simples",
            variable=tipo_var,
            value='opcao_simples',
            bg='#f0f2f5',
            activebackground='#f0f2f5',
            selectcolor='#f0f2f5'
        )
        rb_opcao_simples.pack(side=tk.LEFT, padx=(0, 20))
        
        # Texto Livre
        rb_texto_livre = tk.Radiobutton(
            frame_tipo,
            text="Texto Livre",
            variable=tipo_var,
            value='texto_livre',
            bg='#f0f2f5',
            activebackground='#f0f2f5',
            selectcolor='#f0f2f5'
        )
        rb_texto_livre.pack(side=tk.LEFT)
        
        # Frame para os botões
        botoes_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=20)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Função para salvar
        def salvar():
            try:
                preco = float(preco_var.get())
                if preco < 0:
                    raise ValueError("O preço não pode ser negativo.")
                    
                dados_item = {
                    'id': item_id,
                    'grupo_id': self.grupo_selecionado,
                    'nome': nome_var.get().strip(),
                    'tipo': tipo_var.get(),
                    'descricao': descricao_text.get('1.0', tk.END).strip(),
                    'preco_adicional': preco
                }
                
                if not dados_item['nome']:
                    messagebox.showwarning("Atenção", "O nome do item é obrigatório.")
                    return
                    
                if self.controller.salvar_item(self.grupo_selecionado, dados_item):
                    messagebox.showinfo("Sucesso", "Item salvo com sucesso!")
                    dialog.destroy()
                    # Recarrega os itens do grupo selecionado
                    if hasattr(self, 'lista_itens'):
                        self._limpar_lista_itens()
                        itens = self.controller.listar_itens_por_grupo(self.grupo_selecionado)
                        for item in itens:
                            # Define o tipo de opção para exibição
                            tipo = item.get('tipo', 'opcao_simples')
                            tipo_exibicao = 'Texto Livre' if tipo == 'texto_livre' else 'Opção Simples'
                            
                            self.lista_itens.insert('', 'end', values=(
                                item['id'],
                                f"{item['nome']} ({tipo_exibicao})",
                                f"R$ {item['preco_adicional']:.2f}" if item['preco_adicional'] and item['preco_adicional'] > 0 else ""
                            ))
                else:
                    messagebox.showerror("Erro", "Não foi possível salvar o item.")
                    
            except ValueError as e:
                messagebox.showwarning("Atenção", str(e) if str(e) else "Informe um preço válido (apenas números).")
        
        # Frame para os botões de ação
        botoes_acao_frame = tk.Frame(botoes_frame, bg='#f0f2f5')
        botoes_acao_frame.pack(side=tk.RIGHT)
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_acao_frame, 
            text="Salvar", 
            command=salvar,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#43a047',
            activeforeground='white',
            width=15
        )
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_acao_frame, 
            text="Cancelar", 
            command=dialog.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#d32f2f',
            activeforeground='white',
            width=15
        )
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _carregar_grupos_disponiveis(self):
        """Carrega a lista de grupos de opções disponíveis."""
        # Limpa a lista atual
        for item in self.lista_grupos_disponiveis.get_children():
            self.lista_grupos_disponiveis.delete(item)
        
        try:
            # Busca os grupos disponíveis no banco de dados
            grupos = self.controller.listar_grupos_para_vinculo()
            
            # Preenche a lista de grupos disponíveis
            for grupo in grupos:
                self.lista_grupos_disponiveis.insert('', 'end', values=(
                    grupo['id'],
                    grupo['nome']
                ), tags=(str(grupo['id']),))
            
            # Configura o evento de seleção
            self.lista_grupos_disponiveis.bind('<<TreeviewSelect>>', self._ao_selecionar_grupo)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os grupos de opções: {str(e)}")
    
    def _ao_selecionar_grupo(self, event):
        """Manipulador de evento para quando um grupo é selecionado."""
        # Obtém o item selecionado
        item_selecionado = self.lista_grupos_disponiveis.selection()
        if not item_selecionado:
            return
            
        # Obtém os valores do item selecionado
        valores = self.lista_grupos_disponiveis.item(item_selecionado[0], 'values')
        if not valores:
            return
            
        grupo_id = valores[0]
        
        # Armazena o grupo selecionado
        self.grupo_selecionado = grupo_id
        
        # Carrega os produtos vinculados ao grupo
        self._carregar_produtos_vinculados_ao_grupo(grupo_id)
    
    def _carregar_produtos_vinculados_ao_grupo(self, grupo_id):
        """Carrega os produtos vinculados ao grupo selecionado."""
        # Limpa a lista de produtos vinculados
        for item in self.lista_grupos_vinculados.get_children():
            self.lista_grupos_vinculados.delete(item)
        
        try:
            # Busca os produtos vinculados ao grupo
            produtos = self.controller.listar_produtos_por_grupo(grupo_id)
            
            # Preenche a lista de produtos vinculados
            for produto in produtos:
                self.lista_grupos_vinculados.insert('', 'end', values=(
                    produto['id'],
                    produto['nome'],
                    'Sim' if produto.get('obrigatorio', False) else 'Não'
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os produtos do grupo: {str(e)}")
    
    def _carregar_produtos_por_categoria(self):
        """Carrega os produtos da categoria selecionada."""
        categoria = self.categoria_selecionada.get()
        if not categoria:
            return
            
        try:
            # Busca a lista de produtos da categoria selecionada
            self.produtos = self.controller.listar_produtos_por_categoria(categoria)
            
            # Atualiza a combobox de produtos
            produtos_lista = [f"{p['id']} - {p['nome']}" for p in self.produtos]
            if hasattr(self, 'produto_item_cb'):
                self.produto_item_cb['values'] = produtos_lista
            if hasattr(self, 'produtos_cb'):
                self.produtos_cb['values'] = produtos_lista
            
            # Limpa a seleção anterior
            self.produto_selecionado.set('')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os produtos: {str(e)}")
    
    def _selecionar_produto_novo(self, event=None):
        """Método vazio para evitar erros ao selecionar produto no formulário de item"""
        pass
    
    def _selecionar_grupo(self, grupo_id):
        """Atualiza o grupo selecionado e sua aparência visual."""
        # Remove a seleção de todos os itens
        for item in self.lista_grupos_disponiveis.selection():
            self.lista_grupos_disponiveis.selection_remove(item)
        
        # Encontra e seleciona o item correspondente ao grupo_id
        for item in self.lista_grupos_disponiveis.get_children():
            valores = self.lista_grupos_disponiveis.item(item, 'values')
            if valores and int(valores[0]) == grupo_id:
                self.lista_grupos_disponiveis.selection_add(item)
                self.lista_grupos_disponiveis.focus(item)
                self.lista_grupos_disponiveis.see(item)
                break
        
        # Armazena o grupo selecionado
        self.grupo_selecionado = grupo_id
    
    def _salvar_vinculos_grupo_produto(self):
        """Salva as alterações nos vínculos do grupo com os produtos."""
        # Verifica se há um grupo selecionado
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo primeiro.")
            return
        
        # Obtém os produtos atualmente vinculados ao grupo
        produtos_vinculados = self.controller.listar_produtos_por_grupo(self.grupo_selecionado)
        
        # Prepara a lista de vínculos para salvar
        vinculos = []
        
        # Obtém os vínculos atuais da interface
        for item in self.lista_grupos_vinculados.get_children():
            valores = self.lista_grupos_vinculados.item(item, 'values')
            if valores:
                vinculos.append({
                    'produto_id': int(valores[0]),
                    'obrigatorio': valores[2] == 'Sim'
                })
        
        try:
            # Salva os vínculos no banco de dados
            if self.controller.salvar_vinculos_grupo(self.grupo_selecionado, vinculos):
                messagebox.showinfo("Sucesso", "Vínculos salvos com sucesso!")
                # Recarrega os produtos vinculados
                self._carregar_produtos_vinculados_ao_grupo(self.grupo_selecionado)
            else:
                messagebox.showerror("Erro", "Não foi possível salvar os vínculos.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar os vínculos: {str(e)}")
    
    def _atualizar_grupos_disponiveis(self):
        """Atualiza a lista de grupos disponíveis, removendo os já vinculados."""
        # Obtém os IDs dos grupos já vinculados
        grupos_vinculados = set()
        for item in self.lista_grupos_vinculados.get_children():
            valores = self.lista_grupos_vinculados.item(item, 'values')
            if valores:
                grupos_vinculados.add(int(valores[0]))
        
        # Atualiza a lista de grupos disponíveis
        for item in self.lista_grupos_disponiveis.get_children():
            valores = self.lista_grupos_disponiveis.item(item, 'values')
            if valores and int(valores[0]) in grupos_vinculados:
                # Se o grupo já está vinculado, remove da lista de disponíveis
                self.lista_grupos_disponiveis.detach(item)
            else:
                # Se não está vinculado, garante que está visível
                self.lista_grupos_disponiveis.reattach(item, '', 'end')
    
    def _vincular_produto_ao_grupo(self):
        """Vincula o produto selecionado ao grupo atualmente selecionado."""
        # Verifica se há um grupo selecionado
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo primeiro.")
            return
            
        # Verifica se há um produto selecionado
        produto_selecionado = self.produto_selecionado.get()
        if not produto_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para vincular.")
            return
            
        try:
            # Extrai o ID do produto da string de exibição
            produto_id = int(produto_selecionado.split(' - ')[0])
            
            # Verifica se o produto já está vinculado ao grupo
            for item in self.lista_grupos_vinculados.get_children():
                valores = self.lista_grupos_vinculados.item(item, 'values')
                if valores and int(valores[0]) == produto_id:
                    messagebox.showinfo("Aviso", "Este produto já está vinculado ao grupo.")
                    return
            
            # Adiciona o produto ao grupo (não obrigatório por padrão)
            if self.controller.adicionar_grupo_ao_produto(produto_id, self.grupo_selecionado, obrigatorio=False):
                # Atualiza a lista de produtos vinculados
                self._carregar_produtos_vinculados_ao_grupo(self.grupo_selecionado)
                messagebox.showinfo("Sucesso", "Produto vinculado ao grupo com sucesso!")
            else:
                messagebox.showerror("Erro", "Não foi possível vincular o produto ao grupo.")
                
        except (ValueError, IndexError):
            messagebox.showerror("Erro", "Selecione um produto válido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao vincular o produto: {str(e)}")
    
    def _remover_vinculo_produto(self):
        """Remove o vínculo do produto selecionado com o grupo."""
        # Verifica se há um grupo selecionado
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo primeiro.")
            return
            
        # Obtém os itens selecionados na lista de produtos vinculados
        itens_selecionados = self.lista_grupos_vinculados.selection()
        
        if not itens_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um produto para remover o vínculo.")
            return
        
        try:
            for item in itens_selecionados:
                valores = self.lista_grupos_vinculados.item(item, 'values')
                if valores:
                    produto_id = int(valores[0])
                    # Remove o vínculo
                    if self.controller.remover_grupo_do_produto(produto_id, self.grupo_selecionado):
                        # Remove da lista de vinculados
                        self.lista_grupos_vinculados.delete(item)
                        messagebox.showinfo("Sucesso", "Vínculo removido com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Não foi possível remover o vínculo.")
                        
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao remover o vínculo: {str(e)}")
    
    def _alternar_obrigatorio(self):
        """Alterna o status de obrigatório para os produtos selecionados."""
        # Verifica se há um grupo selecionado
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo primeiro.")
            return
            
        # Obtém os itens selecionados na lista de produtos vinculados
        itens_selecionados = self.lista_grupos_vinculados.selection()
        
        if not itens_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um produto para alterar o status.")
            return
        
        try:
            for item in itens_selecionados:
                valores = list(self.lista_grupos_vinculados.item(item, 'values'))
                if valores:
                    produto_id = int(valores[0])
                    novo_status = valores[2] == 'Não'  # Inverte o status atual
                    
                    # Atualiza o status no banco de dados
                    if self.controller.atualizar_status_vinculo(produto_id, self.grupo_selecionado, novo_status):
                        # Atualiza a exibição
                        valores[2] = 'Sim' if novo_status else 'Não'
                        self.lista_grupos_vinculados.item(item, values=valores)
                    else:
                        messagebox.showerror("Erro", "Não foi possível atualizar o status do produto.")
                            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar o status: {str(e)}")
    

if __name__ == "__main__":
    root = tk.Tk()
    app = OpcoesModule(root, None)
    root.mainloop()
