"""
Módulo de Cadastro - Gerencia cadastros do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Adicione o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Importações locais
from src.db.cadastro_db import CadastroDB
from ..base_module import BaseModule

class CadastroModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        super().__init__(parent, controller)
        
        # Inicializa a conexão com o banco de dados
        self.db = CadastroDB(db_connection) if db_connection else None
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Frame para o conteúdo
        self.conteudo_frame = tk.Frame(self.frame)
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Dados em memória
        self.dados_empresa = {}
        self.lista_usuarios = []
        self.lista_funcionarios = []
        self.lista_clientes = []
        self.lista_produtos = []
        self.lista_fornecedores = []
        
        # Mapeamento de ações para as funções correspondentes
        self.acoes = {
            "empresa": self.mostrar_empresa,
            "usuarios": self.mostrar_usuarios,
            "funcionarios": self.mostrar_funcionarios,
            "clientes": self.mostrar_clientes,
            "produtos": self.mostrar_produtos,
            "fornecedores": self.mostrar_fornecedores
        }
        
        
        # Mostra a tela inicial
        self.mostrar_inicio()
    
    def mostrar_inicio(self):
        """Mostra a tela inicial do módulo de cadastro"""
        self.limpar_conteudo()
        
        # Adiciona uma mensagem de boas-vindas
        tk.Label(
            self.conteudo_frame,
            text="Selecione uma opção no menu lateral para começar.",
            font=('Arial', 12)
        ).pack(pady=50)
    
    def mostrar_empresa(self):
        """Mostra a tela de cadastro da empresa"""
        self.limpar_conteudo()
        
        try:
            if not self.db:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
                return
                
            # Carrega os dados da empresa
            self.dados_empresa = self.db.obter_empresa()
            
            # Frame principal
            main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Título
            title_frame = tk.Frame(main_frame, bg='#f0f2f5')
            title_frame.pack(fill='x', pady=(0, 20))
            
            tk.Label(
                title_frame, 
                text="CADASTRO DA EMPRESA", 
                font=('Arial', 16, 'bold'),
                bg='#f0f2f5',
                fg='#333333'
            ).pack(side='left')
            
            # Frame do formulário
            form_frame = tk.Frame(main_frame, bg='white', padx=20, pady=20, bd=1, relief='groove')
            form_frame.pack(fill='both', expand=True)
            
            # Estilo dos labels e campos
            label_style = {'font': ('Arial', 10, 'bold'), 'bg': 'white', 'anchor': 'w'}
            entry_style = {'font': ('Arial', 10), 'bd': 1, 'relief': 'solid', 'width': 40}
            
            # Dados da Empresa
            tk.Label(form_frame, text="Dados da Empresa", font=('Arial', 12, 'bold'), bg='white').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            
            # Nome Fantasia (obrigatório)
            tk.Label(form_frame, text="Nome Fantasia*:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky='w')
            self.empresa_nome = tk.Entry(form_frame, **entry_style)
            self.empresa_nome.grid(row=1, column=1, padx=10, pady=5, sticky='w')
            
            # Razão Social
            tk.Label(form_frame, text="Razão Social:", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky='w')
            self.empresa_razao = tk.Entry(form_frame, **entry_style)
            self.empresa_razao.grid(row=2, column=1, padx=10, pady=5, sticky='w')
            
            # CNPJ (obrigatório)
            tk.Label(form_frame, text="CNPJ*:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky='w')
            self.empresa_cnpj = tk.Entry(form_frame, **entry_style)
            self.empresa_cnpj.grid(row=3, column=1, padx=10, pady=5, sticky='w')
            
            # Inscrição Estadual
            tk.Label(form_frame, text="Inscrição Estadual:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky='w')
            self.empresa_ie = tk.Entry(form_frame, **entry_style)
            self.empresa_ie.grid(row=4, column=1, padx=10, pady=5, sticky='w')
            
            # Telefone
            tk.Label(form_frame, text="Telefone:", **label_style).grid(row=5, column=0, padx=10, pady=5, sticky='w')
            self.empresa_telefone = tk.Entry(form_frame, **entry_style)
            self.empresa_telefone.grid(row=5, column=1, padx=10, pady=5, sticky='w')
            
            # Endereço (texto livre)
            tk.Label(form_frame, text="Endereço Completo:", **label_style).grid(row=6, column=0, padx=10, pady=5, sticky='nw')
            self.empresa_endereco = tk.Text(form_frame, width=40, height=5, font=('Arial', 10), bd=1, relief='solid')
            self.empresa_endereco.grid(row=6, column=1, padx=10, pady=5, sticky='w')
            
            # Frame para os botões
            btn_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=20)
            btn_frame.pack(fill='x')
            
            # Botão Salvar
            btn_salvar = tk.Button(
                btn_frame,
                text="Salvar",
                font=('Arial', 10, 'bold'),
                bg='#4CAF50',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=self.salvar_empresa
            )
            btn_salvar.pack(side='right', padx=10)
            
            # Botão Cancelar
            btn_cancelar = tk.Button(
                btn_frame,
                text="Cancelar",
                font=('Arial', 10, 'bold'),
                bg='#f44336',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=self.cancelar_edicao
            )
            btn_cancelar.pack(side='right')
            
            # Ajusta o grid para expandir corretamente
            form_frame.columnconfigure(1, weight=1)
            
            # Preenche os campos se existirem dados
            self.preencher_campos_empresa()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar os dados da empresa: {str(e)}")
    
    def mostrar_usuarios(self):
        """Mostra a tela de cadastro de usuários"""
        self.limpar_conteudo()
        
        try:
            if not self.db:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
                return
            
            # Carrega a lista de usuários
            self.lista_usuarios = self.db.listar_usuarios()
            
            # Frame principal com grid
            main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(1, weight=1)
            
            # Frame do título
            title_frame = tk.Frame(main_frame, bg='#f0f2f5')
            title_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
            
            tk.Label(
                title_frame, 
                text="LISTA DE USUÁRIOS", 
                font=('Arial', 16, 'bold'),
                bg='#f0f2f5',
                fg='#333333'
            ).pack(side='left')
            
            # Frame para os botões (lado esquerdo)
            botoes_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=10, pady=10)
            botoes_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
            botoes_frame.columnconfigure(0, weight=1)
            
            # Configurando o estilo dos botões
            btn_style = {
                'font': ('Arial', 10, 'bold'),
                'bg': '#4a6fa5',
                'fg': 'white',
                'bd': 0,
                'padx': 20,
                'pady': 8,
                'relief': 'flat',
                'cursor': 'hand2',
                'width': 15
            }
            
            # Botão Novo Usuário
            btn_novo = tk.Button(
                botoes_frame,
                text="Novo Usuário",
                **btn_style,
                command=self.novo_usuario
            )
            btn_novo.pack(pady=5, fill='x')
            
            # Botão Editar (inicialmente desabilitado)
            self.btn_editar = tk.Button(
                botoes_frame,
                text="Editar",
                **btn_style,
                state='disabled',
                command=self.editar_usuario
            )
            self.btn_editar.pack(pady=5, fill='x')
            
            # Botão Excluir (inicialmente desabilitado)
            btn_excluir_style = btn_style.copy()
            btn_excluir_style['bg'] = '#f44336'  # Cor vermelha para o botão excluir
            self.btn_excluir = tk.Button(
                botoes_frame,
                text="Excluir",
                **btn_excluir_style,
                state='disabled',
                command=self.excluir_usuario
            )
            self.btn_excluir.pack(pady=5, fill='x')
            
            # Frame para a tabela (lado direito)
            tabela_container = tk.Frame(main_frame, bg='#d1d8e0')
            tabela_container.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
            
            # Frame interno para a tabela
            tabela_frame = tk.Frame(tabela_container, bg='white', padx=1, pady=1)
            tabela_frame.pack(fill='both', expand=True, padx=1, pady=1)
            
            # Cabeçalho da tabela (sem a coluna de ações)
            cabecalho = ['ID', 'Nome', 'Login', 'Nível', 'Telefone']
            
            # Criando a Treeview
            style = ttk.Style()
            style.configure("Treeview", 
                background="#ffffff",
                foreground="#333333",
                rowheight=30,
                fieldbackground="#ffffff",
                borderwidth=0)
                
            style.map('Treeview', 
                background=[('selected', '#4a6fa5')],
                foreground=[('selected', 'white')])
            
            style.configure("Treeview.Heading", 
                font=('Arial', 10, 'bold'),
                background='#4a6fa5',
                foreground='black',
                relief='flat')
                
            style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
            
            self.tree_usuarios = ttk.Treeview(
                tabela_frame, 
                columns=cabecalho, 
                show='headings',
                selectmode='browse',
                style="Treeview"
            )
            
            # Configurando as colunas
            for col in cabecalho:
                self.tree_usuarios.heading(col, text=col)
                self.tree_usuarios.column(col, width=100, anchor='w')
            
            # Ajustando largura das colunas
            self.tree_usuarios.column('ID', width=50, anchor='center')
            self.tree_usuarios.column('Nome', width=200)
            self.tree_usuarios.column('Login', width=150)
            self.tree_usuarios.column('Nível', width=100, anchor='center')
            self.tree_usuarios.column('Telefone', width=150)
            
            # Adicionando barra de rolagem
            scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_usuarios.yview)
            self.tree_usuarios.configure(yscrollcommand=scrollbar.set)
            
            # Posicionando os widgets
            self.tree_usuarios.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Preenchendo a tabela com os dados (sem a coluna de ações)
            for usuario in self.lista_usuarios:
                self.tree_usuarios.insert(
                    '', 'end', 
                    values=(
                        usuario.get('id', ''),
                        usuario.get('nome', ''),
                        usuario.get('login', ''),
                        usuario.get('nivel', ''),
                        usuario.get('telefone', '')
                    )
                )
            
            # Configurar evento de seleção
            self.tree_usuarios.bind('<<TreeviewSelect>>', self.atualizar_botoes)
            
            # Ajustando o layout
            self.conteudo_frame.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {str(e)}")
    
    def atualizar_botoes(self, event=None):
        """Atualiza o estado dos botões com base na seleção"""
        selecionado = bool(self.tree_usuarios.selection())
        state = 'normal' if selecionado else 'disabled'
        self.btn_editar.config(state=state)
        self.btn_excluir.config(state=state)
    
    def _criar_formulario_usuario(self, titulo, usuario_id=None):
        """Cria o formulário de usuário (usado para novo e edição)"""
        # Cria uma janela modal
        self.janela_form_usuario = tk.Toplevel(self.frame)
        self.janela_form_usuario.title(titulo)
        self.janela_form_usuario.transient(self.frame)
        self.janela_form_usuario.resizable(False, False)
        
        # Armazena o ID do usuário em edição (None para novo usuário)
        self.usuario_editando_id = usuario_id
        
        # Centraliza a janela
        largura_janela = 400
        altura_janela = 400
        largura_tela = self.janela_form_usuario.winfo_screenwidth()
        altura_tela = self.janela_form_usuario.winfo_screenheight()
        posx = (largura_tela // 2) - (largura_janela // 2)
        posy = (altura_tela // 2) - (altura_janela // 2)
        self.janela_form_usuario.geometry(f'{largura_janela}x{altura_janela}+{posx}+{posy}')
        
        # Frame principal
        main_frame = tk.Frame(self.janela_form_usuario, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        tk.Label(
            main_frame,
            text=titulo.upper(),
            font=('Arial', 14, 'bold'),
            pady=10
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Dicionário para armazenar as variáveis dos campos
        self.campos_usuario = {}
        
        # Se estiver editando, carrega os dados do usuário
        dados_usuario = None
        if usuario_id is not None:
            dados_usuario = self.db.obter_usuario_por_id(usuario_id)
        
        # Campos do formulário
        campos = [
            ("Nome:", 'entry', True, {'value': dados_usuario['nome'] if dados_usuario else ''}),
            ("Login:", 'entry', True, {'value': dados_usuario['login'] if dados_usuario else ''}),
            ("Senha:", 'entry', usuario_id is None, {'show': '*', 'value': ''}),
            ("Confirmar Senha:", 'entry', usuario_id is None, {'show': '*', 'value': ''}),
            ("Nível:", 'combobox', True, {
                'values': ['Administrador', 'Gerente', 'Operador'],
                'state': 'readonly',
                'width': 20,
                'value': dados_usuario['nivel'].capitalize() if dados_usuario else 'Operador'
            }),
            ("Telefone:", 'entry', False, {'value': dados_usuario.get('telefone', '') if dados_usuario else ''})
        ]
        
        # Cria os campos do formulário
        for i, (rotulo, tipo, obrigatorio, *args) in enumerate(campos, 1):
            # Adiciona o rótulo
            texto_rotulo = f"{rotulo} {'*' if obrigatorio else ''}"
            tk.Label(
                main_frame,
                text=texto_rotulo,
                font=('Arial', 10),
                fg='red' if obrigatorio else 'black'
            ).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            
            # Adiciona o campo
            if tipo == 'entry':
                kwargs = args[0] if args else {}
                # Se tiver valor padrão, remove do kwargs e usa no insert
                valor = kwargs.pop('value', '')
                entry = tk.Entry(
                    main_frame,
                    font=('Arial', 10),
                    width=30,
                    **kwargs
                )
                if valor:
                    entry.insert(0, valor)
                entry.grid(row=i, column=1, sticky='w', pady=5)
                self.campos_usuario[rotulo.lower().replace(' ', '_').replace(':', '')] = entry
                
            elif tipo == 'combobox':
                kwargs = args[0] if args else {}
                # Se tiver valor padrão, remove do kwargs e usa no set
                valor = kwargs.pop('value', None)
                combo = ttk.Combobox(
                    main_frame,
                    font=('Arial', 10),
                    **kwargs
                )
                combo.grid(row=i, column=1, sticky='w', pady=5)
                if valor and valor in (kwargs.get('values') or []):
                    combo.set(valor)
                else:
                    combo.set(kwargs.get('values', [''])[0] if 'values' in kwargs else '')
                self.campos_usuario[rotulo.lower().replace(' ', '_').replace(':', '')] = combo
        
        # Frame para os botões
        botoes_frame = tk.Frame(main_frame)
        botoes_frame.grid(row=len(campos)+2, column=0, columnspan=2, pady=(20, 0))
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame,
            text="Salvar",
            command=self.salvar_usuario,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            bd=0
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame,
            text="Cancelar",
            command=self.janela_form_usuario.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5,
            bd=0
        )
        btn_cancelar.pack(side='left', padx=5)
        
        # Focar no primeiro campo
        self.janela_form_usuario.after(100, lambda: self.campos_usuario['nome'].focus())
        
        # Configurar o fechamento da janela
        self.janela_form_usuario.protocol("WM_DELETE_WINDOW", self.janela_form_usuario.destroy)
        
        # Trava a janela principal
        self.janela_form_usuario.grab_set()
    
    def novo_usuario(self):
        """Abre o formulário para criar um novo usuário"""
        self._criar_formulario_usuario("Novo Usuário")
        
        # Configurar o comando do botão Salvar
        for widget in self.janela_form_usuario.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == 'Salvar':
                widget.config(command=self.salvar_usuario)
                break
    
    def salvar_usuario(self):
        """Salva um usuário no banco de dados (cria novo ou atualiza existente)"""
        try:
            # Obtém os valores dos campos
            nome = self.campos_usuario['nome'].get().strip()
            login = self.campos_usuario['login'].get().strip()
            senha = self.campos_usuario['senha'].get()
            confirmar_senha = self.campos_usuario['confirmar_senha'].get()
            nivel = self.campos_usuario['nível'].get().lower()
            telefone = self.campos_usuario['telefone'].get().strip()
            
            # Validações
            if not nome or not login or not senha or not confirmar_senha or not nivel:
                messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                return
                
            if senha != confirmar_senha:
                messagebox.showwarning("Atenção", "As senhas não conferem!")
                self.campos_usuario['senha'].delete(0, 'end')
                self.campos_usuario['confirmar_senha'].delete(0, 'end')
                self.campos_usuario['senha'].focus()
                return
            
            # Prepara os dados para salvar
            dados_usuario = {
                'nome': nome,
                'login': login,
                'nivel': nivel,
                'telefone': telefone if telefone else None
            }
            
            # Se estiver editando, adiciona o ID
            if hasattr(self, 'usuario_editando_id') and self.usuario_editando_id is not None:
                dados_usuario['id'] = self.usuario_editando_id
            
            # Se for novo usuário ou se a senha foi alterada
            if senha:
                dados_usuario['senha'] = senha  # Em produção, criptografe a senha antes de salvar
            
            # Salva no banco de dados
            sucesso, mensagem = self.db.salvar_usuario(dados_usuario)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                # Atualiza a lista de usuários
                self.mostrar_usuarios()
                # Fecha o formulário
                if hasattr(self, 'janela_form_usuario'):
                    self.janela_form_usuario.destroy()
                # Limpa a referência
                if hasattr(self, 'usuario_editando_id'):
                    del self.usuario_editando_id
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def editar_usuario(self):
        """Abre o formulário para editar o usuário selecionado"""
        selecionado = self.tree_usuarios.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para editar.")
            return
            
        item = self.tree_usuarios.item(selecionado[0])
        usuario_id = item['values'][0]
        
        # Abre o formulário de edição
        self._criar_formulario_usuario("Editar Usuário", usuario_id)
        
        # Configura o comando do botão Salvar
        for widget in self.janela_form_usuario.winfo_children():
            if isinstance(widget, tk.Button) and widget['text'] == 'Salvar':
                widget.config(command=self.salvar_usuario)
                break
    
    def excluir_usuario(self):
        """Exclui o usuário selecionado após confirmação"""
        try:
            selecionado = self.tree_usuarios.selection()
            if not selecionado:
                return
                
            item = self.tree_usuarios.item(selecionado[0])
            usuario_id = item['values'][0]
            nome = item['values'][1]
            
            if messagebox.askyesno("Confirmar Exclusão", 
                                 f"Tem certeza que deseja excluir o usuário '{nome}'?"):
                sucesso, mensagem = self.db.excluir_usuario(usuario_id)
                if sucesso:
                    self.tree_usuarios.delete(selecionado[0])
                    messagebox.showinfo("Sucesso", mensagem)
                else:
                    messagebox.showerror("Erro", mensagem)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_funcionarios(self):
        """Mostra a tela de cadastro de funcionários"""
        self.limpar_conteudo()
        
        try:
            if not self.db:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
                return
                
            # Carrega a lista de funcionários
            self.lista_funcionarios = self.db.listar_funcionarios()
            
            # Frame principal com grid
            main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(1, weight=1)
            
            # Frame do título
            title_frame = tk.Frame(main_frame, bg='#f0f2f5')
            title_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
            
            tk.Label(
                title_frame, 
                text="LISTA DE FUNCIONÁRIOS", 
                font=('Arial', 16, 'bold'),
                bg='#f0f2f5',
                fg='#333333'
            ).pack(side='left')
            
            # Frame para os botões (lado esquerdo)
            botoes_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=10, pady=10)
            botoes_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
            botoes_frame.columnconfigure(0, weight=1)
            
            # Configurando o estilo dos botões
            btn_style = {
                'font': ('Arial', 10, 'bold'),
                'bg': '#4a6fa5',
                'fg': 'white',
                'bd': 0,
                'padx': 20,
                'pady': 8,
                'relief': 'flat',
                'cursor': 'hand2',
                'width': 15
            }
            
            # Botão Novo Funcionário
            btn_novo = tk.Button(
                botoes_frame,
                text="Novo Funcionário",
                **btn_style,
                command=self.novo_funcionario
            )
            btn_novo.pack(pady=5, fill='x')
            
            # Botão Editar (inicialmente desabilitado)
            self.btn_editar_func = tk.Button(
                botoes_frame,
                text="Editar",
                **btn_style,
                state='disabled',
                command=self.editar_funcionario
            )
            self.btn_editar_func.pack(pady=5, fill='x')
            
            # Botão Excluir (inicialmente desabilitado)
            btn_excluir_style = btn_style.copy()
            btn_excluir_style['bg'] = '#f44336'  # Cor vermelha para o botão excluir
            self.btn_excluir_func = tk.Button(
                botoes_frame,
                text="Excluir",
                **btn_excluir_style,
                state='disabled',
                command=self.confirmar_exclusao_funcionario
            )
            self.btn_excluir_func.pack(pady=5, fill='x')
            
            # Frame para a tabela (lado direito)
            tabela_container = tk.Frame(main_frame, bg='#d1d8e0')
            tabela_container.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
            
            # Frame interno para a tabela
            tabela_frame = tk.Frame(tabela_container, bg='white', padx=1, pady=1)
            tabela_frame.pack(fill='both', expand=True, padx=1, pady=1)
            
            # Cabeçalho da tabela
            cabecalho = ['ID', 'Nome', 'Idade', 'CPF', 'Cargo', 'Telefone']
            
            # Criando a Treeview
            style = ttk.Style()
            style.configure("Treeview", 
                background="#ffffff",
                foreground="#333333",
                rowheight=30,
                fieldbackground="#ffffff",
                borderwidth=0)
                
            style.map('Treeview', 
                background=[('selected', '#4a6fa5')],
                foreground=[('selected', 'white')])
            
            style.configure("Treeview.Heading", 
                font=('Arial', 10, 'bold'),
                background='#4a6fa5',
                foreground='black',
                relief='flat')
                
            style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
            
            self.tree_funcionarios = ttk.Treeview(
                tabela_frame, 
                columns=cabecalho, 
                show='headings',
                selectmode='browse',
                style="Treeview"
            )
            
            # Configurando as colunas
            for col in cabecalho:
                self.tree_funcionarios.heading(col, text=col)
                self.tree_funcionarios.column(col, width=100, anchor='w')
            
            # Ajustando largura das colunas
            self.tree_funcionarios.column('ID', width=50, anchor='center')
            self.tree_funcionarios.column('Nome', width=200)
            self.tree_funcionarios.column('Idade', width=60, anchor='center')
            self.tree_funcionarios.column('CPF', width=120)
            self.tree_funcionarios.column('Cargo', width=150)
            self.tree_funcionarios.column('Telefone', width=120)
            
            # Adicionando barra de rolagem
            scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_funcionarios.yview)
            self.tree_funcionarios.configure(yscrollcommand=scrollbar.set)
            
            # Posicionando os widgets
            self.tree_funcionarios.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Preenchendo a tabela com os dados
            for funcionario in self.lista_funcionarios:
                self.tree_funcionarios.insert(
                    '', 'end', 
                    values=(
                        funcionario.get('id', ''),
                        funcionario.get('nome', ''),
                        funcionario.get('idade', ''),
                        funcionario.get('cpf', ''),
                        funcionario.get('cargo', ''),
                        funcionario.get('telefone', '')
                    )
                )
            
            # Configurar evento de seleção
            self.tree_funcionarios.bind('<<TreeviewSelect>>', self.atualizar_botoes_funcionarios)
            
            # Ajustando o layout
            self.conteudo_frame.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar funcionários: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def atualizar_botoes_funcionarios(self, event=None):
        """Atualiza o estado dos botões com base na seleção"""
        selecionado = bool(self.tree_funcionarios.selection())
        state = 'normal' if selecionado else 'disabled'
        self.btn_editar_func.config(state=state)
        self.btn_excluir_func.config(state=state)
    
    def _criar_formulario_funcionario(self, titulo, funcionario_id=None):
        """Cria o formulário de cadastro/edição de funcionário"""
        # Janela de formulário
        self.janela_form_funcionario = tk.Toplevel(self.frame)
        self.janela_form_funcionario.title(titulo)
        self.janela_form_funcionario.resizable(False, False)
        
        # Armazena o ID do funcionário em edição (None para novo funcionário)
        self.funcionario_editando_id = funcionario_id
        
        # Centraliza a janela
        largura_janela = 450
        altura_janela = 500
        largura_tela = self.janela_form_funcionario.winfo_screenwidth()
        altura_tela = self.janela_form_funcionario.winfo_screenheight()
        posx = (largura_tela // 2) - (largura_janela // 2)
        posy = (altura_tela // 2) - (altura_janela // 2)
        self.janela_form_funcionario.geometry(f'{largura_janela}x{altura_janela}+{posx}+{posy}')
        
        # Frame principal
        main_frame = tk.Frame(self.janela_form_funcionario, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        tk.Label(
            main_frame,
            text=titulo.upper(),
            font=('Arial', 14, 'bold'),
            pady=10
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Dicionário para armazenar as variáveis dos campos
        self.campos_funcionario = {}
        
        # Se estiver editando, carrega os dados do funcionário
        dados_funcionario = None
        if funcionario_id is not None:
            # Busca o funcionário pelo ID na lista
            for func in self.lista_funcionarios:
                if func['id'] == funcionario_id:
                    dados_funcionario = func
                    break
        
        # Lista de cargos pré-definidos
        cargos = [
            "Bartender", "Caixa", "Gerente", "Garçom",
            "Auxiliar", "Segurança", "Cozinheiro",
            "Gerente"
        ]
        
        # Campos do formulário
        campos = [
            ("Nome*:", 'entry', True, {'value': dados_funcionario['nome'] if dados_funcionario else ''}),
            ("Idade:", 'entry', False, {'value': str(dados_funcionario.get('idade', '')) if dados_funcionario and dados_funcionario.get('idade') else ''}),
            ("CPF:", 'entry', False, {'value': dados_funcionario.get('cpf', '') if dados_funcionario else ''}),
            ("Cargo:", 'combobox', False, {
                'values': cargos,
                'value': dados_funcionario.get('cargo', '') if dados_funcionario else '',
                'state': 'readonly',
                'width': 37
            }),
            ("Telefone:", 'entry', False, {'value': dados_funcionario.get('telefone', '') if dados_funcionario else ''}),
            ("Endereço:", 'text', False, {'value': dados_funcionario.get('endereco', '') if dados_funcionario else ''})
        ]
        
        # Cria os campos do formulário
        for i, (label_text, field_type, required, kwargs) in enumerate(campos, 1):
            # Label
            label = tk.Label(main_frame, text=label_text, font=('Arial', 10), anchor='w')
            label.grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            # Campo
            if field_type == 'entry':
                var = tk.StringVar(value=kwargs.get('value', ''))
                entry = tk.Entry(
                    main_frame, 
                    textvariable=var,
                    font=('Arial', 10),
                    width=40
                )
                entry.grid(row=i, column=1, sticky='w', padx=5, pady=5)
                self.campos_funcionario[label_text.replace('*', '').replace(':', '').lower()] = entry
            elif field_type == 'combobox':
                var = tk.StringVar()
                combo = ttk.Combobox(
                    main_frame,
                    textvariable=var,
                    font=('Arial', 10),
                    **{k: v for k, v in kwargs.items() if k != 'value'}
                )
                if 'value' in kwargs:
                    var.set(kwargs['value'])
                combo.grid(row=i, column=1, sticky='w', padx=5, pady=5)
                self.campos_funcionario[label_text.replace('*', '').replace(':', '').lower()] = combo
            elif field_type == 'text':
                text = tk.Text(
                    main_frame,
                    font=('Arial', 10),
                    width=40,
                    height=5,
                    wrap='word'
                )
                text.grid(row=i, column=1, sticky='w', padx=5, pady=5)
                if 'value' in kwargs and kwargs['value'] is not None:
                    text.insert('1.0', str(kwargs['value']))
                self.campos_funcionario['endereco'] = text
        
        # Frame dos botões
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=len(campos) + 1, column=0, columnspan=2, pady=(20, 0))
        
        # Botão Salvar
        btn_salvar = tk.Button(
            btn_frame,
            text="Salvar",
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self.salvar_funcionario
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            btn_frame,
            text="Cancelar",
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            bd=0,
            padx=20,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self.janela_form_funcionario.destroy
        )
        btn_cancelar.pack(side='left', padx=5)
        
        # Centraliza os botões
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        # Configura o grid para expandir corretamente
        main_frame.grid_rowconfigure(len(campos) + 1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
    
    def novo_funcionario(self):
        """Abre o formulário para criar um novo funcionário"""
        self._criar_formulario_funcionario("Novo Funcionário")
    
    def editar_funcionario(self):
        """Abre o formulário para editar o funcionário selecionado"""
        selecionado = self.tree_funcionarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um funcionário para editar")
            return
            
        # Obtém o ID do funcionário selecionado
        item = self.tree_funcionarios.item(selecionado[0])
        funcionario_id = item['values'][0]
        
        # Abre o formulário de edição
        self._criar_formulario_funcionario("Editar Funcionário", funcionario_id)
    
    def salvar_funcionario(self):
        """Salva um funcionário no banco de dados (cria novo ou atualiza existente)"""
        try:
            # Obtém os valores dos campos
            def get_valor(campo, padrao=''):
                widget = self.campos_funcionario.get(campo)
                if isinstance(widget, (tk.Entry, ttk.Combobox)):
                    return widget.get().strip()
                elif isinstance(widget, tk.Text):
                    return widget.get('1.0', 'end-1c').strip()
                return padrao
            
            nome = get_valor('nome')
            idade = get_valor('idade')
            cpf = get_valor('cpf')
            cargo = get_valor('cargo')
            telefone = get_valor('telefone')
            endereco = get_valor('endereco')
            
            # Validação dos campos obrigatórios
            if not nome:
                messagebox.showwarning("Aviso", "O campo Nome é obrigatório")
                if 'nome' in self.campos_funcionario:
                    self.campos_funcionario['nome'].focus()
                return
            
            # Prepara os dados para salvar
            try:
                idade_int = int(idade) if idade and idade.isdigit() else None
            except (ValueError, AttributeError):
                idade_int = None
                
            dados = {
                'nome': nome,
                'idade': idade_int,
                'cpf': cpf or None,
                'cargo': cargo or None,
                'telefone': telefone or None,
                'endereco': endereco or None
            }
            
            # Salva no banco de dados
            if self.funcionario_editando_id is not None:
                # Atualiza funcionário existente
                resultado = self.db.atualizar_funcionario(self.funcionario_editando_id, **dados)
                mensagem = "atualizado"
            else:
                # Cria novo funcionário
                resultado = self.db.inserir_funcionario(**dados)
                mensagem = "cadastrado"
            
            if resultado:
                messagebox.showinfo("Sucesso", f"Funcionário {mensagem} com sucesso!")
                self.janela_form_funcionario.destroy()
                self.mostrar_funcionarios()  # Atualiza a lista
            else:
                messagebox.showerror("Erro", f"Erro ao salvar funcionário: {self.db.ultimo_erro}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar funcionário: {str(e)}")
    
    def confirmar_exclusao_funcionario(self):
        """Confirma a exclusão de um funcionário"""
        selecionado = self.tree_funcionarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um funcionário para excluir")
            return
            
        # Obtém o ID do funcionário selecionado
        item = self.tree_funcionarios.item(selecionado[0])
        funcionario_id = item['values'][0]
        
        # Confirma a exclusão
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o funcionário {item['values'][1]}?"):
            self.excluir_funcionario(funcionario_id)
    
    def excluir_funcionario(self, funcionario_id):
        """Exclui um funcionário do banco de dados"""
        try:
            if self.db.excluir_funcionario(funcionario_id):
                messagebox.showinfo("Sucesso", "Funcionário excluído com sucesso!")
                self.mostrar_funcionarios()  # Atualiza a lista
            else:
                messagebox.showerror("Erro", f"Erro ao excluir funcionário: {self.db.ultimo_erro}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir funcionário: {str(e)}")
    
    def mostrar_clientes(self):
        """Mostra a tela de clientes pendura"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_clientes = self.db.listar_clientes(ativo=True)
                
                # Frame principal
                main_frame = tk.Frame(self.conteudo_frame)
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Título
                tk.Label(main_frame, text="CLIENTES PENDURA", font=('Arial', 14, 'bold'), pady=10).pack()
                
                # Frame para conteúdo (botões + tabela)
                conteudo_frame = tk.Frame(main_frame)
                conteudo_frame.pack(fill='both', expand=True)
                
                # Frame para botões (lado esquerdo)
                botoes_frame = tk.Frame(conteudo_frame, width=150)
                botoes_frame.pack(side='left', fill='y', padx=(0, 10), pady=(0, 10))
                botoes_frame.pack_propagate(False)
                
                # Botão Novo Cliente
                self.btn_novo_cliente = tk.Button(
                    botoes_frame,
                    text="Novo Cliente",
                    font=('Arial', 10, 'bold'),
                    bg='#4a6fa5',
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    command=self.novo_cliente
                )
                self.btn_novo_cliente.pack(pady=2, fill='x')
                
                # Botão Editar
                self.btn_editar_cliente = tk.Button(
                    botoes_frame,
                    text="Editar",
                    font=('Arial', 10, 'bold'),
                    bg='#4a6fa5',
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    state='disabled',
                    command=self.editar_cliente
                )
                self.btn_editar_cliente.pack(pady=2, fill='x')
                
                # Botão Excluir
                self.btn_excluir_cliente = tk.Button(
                    botoes_frame,
                    text="Excluir",
                    font=('Arial', 10, 'bold'),
                    bg='#f44336',
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    state='disabled',
                    command=self.excluir_cliente
                )
                self.btn_excluir_cliente.pack(pady=2, fill='x')
                
                # Frame da tabela (lado direito)
                tabela_frame = tk.Frame(conteudo_frame, bg='white')
                tabela_frame.pack(side='left', fill='both', expand=True)
                
                # Cria a Treeview
                colunas = ("ID", "Nome", "Telefone", "CPF", "Data Cadastro")
                self.tree_clientes = ttk.Treeview(
                    tabela_frame,
                    columns=colunas,
                    show='headings',
                    selectmode='browse'
                )
                
                # Configura as colunas
                for col in colunas:
                    self.tree_clientes.heading(col, text=col)
                    self.tree_clientes.column(col, width=100, anchor='w')
                
                # Ajusta largura das colunas
                self.tree_clientes.column('ID', width=50, anchor='center')
                self.tree_clientes.column('Nome', width=200)
                self.tree_clientes.column('Telefone', width=120)
                
                # Barra de rolagem
                scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_clientes.yview)
                self.tree_clientes.configure(yscrollcommand=scrollbar.set)
                
                # Posiciona os widgets
                self.tree_clientes.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Preenche a tabela com dados
                for cliente in self.lista_clientes:
                    data_formatada = cliente['data_cadastro'].strftime('%d/%m/%Y') if cliente['data_cadastro'] else ''
                    self.tree_clientes.insert('', 'end', values=(
                        cliente['id'],
                        cliente['nome'],
                        cliente['telefone'],
                        cliente['cpf'],
                        data_formatada
                    ))
                
                # Evento de seleção na tabela
                self.tree_clientes.bind('<<TreeviewSelect>>', self.atualizar_botoes_clientes)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {str(e)}")

    def atualizar_botoes_clientes(self, event=None):
        """Atualiza o estado dos botões com base na seleção"""
        selecionado = bool(self.tree_clientes.selection())
        state = 'normal' if selecionado else 'disabled'
        self.btn_editar_cliente.config(state=state)
        self.btn_excluir_cliente.config(state=state)
    
    def mostrar_produtos(self):
        """Mostra a tela de cadastro de produtos"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_produtos = self.db.listar_produtos()
                
                # Frame principal
                main_frame = tk.Frame(self.conteudo_frame)
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Título
                tk.Label(main_frame,text="LISTA DE PRODUTOS",font=('Arial', 14, 'bold'),pady=10).pack()
                
                # Frame para conteúdo (botões + tabela) em linha horizontal
                conteudo_frame = tk.Frame(main_frame)
                conteudo_frame.pack(fill='both', expand=True)
                
                # Frame para botões (lado esquerdo)
                botoes_frame = tk.Frame(conteudo_frame, width=150)
                botoes_frame.pack(side='left', fill='y', padx=(0, 10), pady=(0, 10))
                botoes_frame.pack_propagate(False)  # Mantém a largura definida
                
                # Botão Novo Produto
                self.btn_novo_prod = tk.Button(
                    botoes_frame,
                    text="Novo Produto",
                    font=('Arial', 10, 'bold'),  # Com negrito
                    bg='#4a6fa5',  # Azul escuro
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    command=self.novo_produto
                )
                self.btn_novo_prod.pack(pady=2, fill='x')
                
                # Botão Editar
                self.btn_editar_prod = tk.Button(
                    botoes_frame,
                    text="Editar",
                    font=('Arial', 10, 'bold'),  # Com negrito
                    bg='#4a6fa5',  # Azul escuro
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    state='disabled',
                    command=self.editar_produto
                )
                self.btn_editar_prod.pack(pady=2, fill='x')
                
                # Botão Excluir
                self.btn_excluir_prod = tk.Button(
                    botoes_frame,
                    text="Excluir",
                    font=('Arial', 10, 'bold'),  # Com negrito
                    bg='#f44336',  # Vermelho
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    state='disabled',
                    command=self.excluir_produto
                )
                self.btn_excluir_prod.pack(pady=2, fill='x')
                
                # Frame da tabela (lado direito)
                tabela_frame = tk.Frame(conteudo_frame, bg='white')
                tabela_frame.pack(side='left', fill='both', expand=True)
                
                # Cria a Treeview
                colunas = ("ID", "Nome", "Tipo", "Descrição", "Preço", "Unidade", "Estoque Mínimo")
                self.tree_produtos = ttk.Treeview(
                    tabela_frame,
                    columns=colunas,
                    show='headings',
                    selectmode='browse'
                )
                
                # Configura as colunas
                for col in colunas:
                    self.tree_produtos.heading(col, text=col)
                    self.tree_produtos.column(col, width=100, anchor='w')
                
                # Ajusta largura das colunas
                self.tree_produtos.column('ID', width=50, anchor='center')
                self.tree_produtos.column('Nome', width=200)
                self.tree_produtos.column('Tipo', width=100)
                self.tree_produtos.column('Descrição', width=250)
                self.tree_produtos.column('Preço', width=100, anchor='e')
                
                # Barra de rolagem
                scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_produtos.yview)
                self.tree_produtos.configure(yscrollcommand=scrollbar.set)
                
                # Posiciona os widgets
                self.tree_produtos.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Preenche a tabela
                for produto in self.lista_produtos:
                    self.tree_produtos.insert('', 'end', values=(
                        produto.get('id', ''),
                        produto.get('nome', ''),
                        produto.get('tipo', ''),
                        produto.get('descricao', ''),
                        f"R$ {produto.get('preco_venda', 0):.2f}",
                        produto.get('unidade_medida', 'UN'),
                        produto.get('quantidade_minima', 0)
                    ))
                
                # Configura evento de seleção
                self.tree_produtos.bind('<<TreeviewSelect>>', self.atualizar_botoes_produtos)
                
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar produtos: {str(e)}")
    
    def atualizar_botoes_produtos(self, event=None):
        """Atualiza o estado dos botões com base na seleção"""
        selecionado = bool(self.tree_produtos.selection())
        state = 'normal' if selecionado else 'disabled'
        self.btn_editar_prod.config(state=state)
        self.btn_excluir_prod.config(state=state)
    
    def novo_produto(self):
        """Abre formulário para cadastrar novo produto"""
        self._criar_formulario_produto("Novo Produto")
    
    def _criar_formulario_produto(self, titulo, produto_id=None):
        """Cria formulário para cadastro/edição de produto"""
        self.limpar_conteudo()
        
        # Dados do produto (se edição)
        self.produto_atual = None
        if produto_id and self.db:
            self.produto_atual = self.db.obter_produto(produto_id)
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Tipos de produtos
        tipos_produtos = ['Cozinha', 'Bar', 'Sobremesas', 'Outros']
        
        # Campos do formulário
        campos = [
            ('Nome:', 'nome', 0),
            ('Tipo:', 'tipo', 1),
            ('Descrição:', 'descricao', 2),
            ('Preço Venda:', 'preco_venda', 3),
            ('Unidade Medida:', 'unidade_medida', 4),
            ('Quantidade Mínima:', 'quantidade_minima', 5)
        ]
        
        self.entries = {}
        for label, field, row in campos:
            # Label
            tk.Label(form_frame, text=label, font=('Arial', 10)).grid(row=row, column=0, sticky='e', padx=5, pady=5)
            
            # Field
            if field == 'tipo':
                # Combobox para tipo de produto
                tipo_var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=tipo_var, values=tipos_produtos, state='readonly', width=37)
                combo.grid(row=row, column=1, sticky='w', padx=5, pady=5)
                self.entries[field] = combo
            elif field == 'descricao':
                # Text widget para descrição
                descricao = tk.Text(form_frame, font=('Arial', 10), width=40, height=4)
                descricao.grid(row=row, column=1, sticky='w', padx=5, pady=5)
                self.entries[field] = descricao
            else:
                # Entry padrão
                entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
                entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
                self.entries[field] = entry
            
            # Preenche com dados existentes se estiver editando
            if self.produto_atual and field in self.produto_atual:
                if field == 'tipo':
                    self.entries[field].set(self.produto_atual[field])
                elif field == 'descricao':
                    self.entries[field].insert('1.0', self.produto_atual[field])
                else:
                    self.entries[field].insert(0, str(self.produto_atual[field]))
        
        # Botões de ação
        botoes_frame = tk.Frame(main_frame)
        botoes_frame.pack(fill='x', pady=10)
        
        tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_produto(produto_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
        
        tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_produtos,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
    
    def _salvar_produto(self, produto_id=None):
        """Salva os dados do produto com tratamento completo de erros"""
        try:
            # Validação do nome
            nome = self.entries['nome'].get()
            if not nome or not nome.strip():
                messagebox.showwarning("Aviso", "Nome do produto é obrigatório")
                self.entries['nome'].focus_set()
                return

            # Validação do preço
            preco_texto = self.entries['preco_venda'].get()
            if not preco_texto or not preco_texto.strip():
                messagebox.showwarning("Aviso", "Preço de venda é obrigatório")
                self.entries['preco_venda'].focus_set()
                return
                
            try:
                preco = float(preco_texto.replace(',', '.'))
                if preco <= 0:
                    raise ValueError("Preço deve ser maior que zero")
            except ValueError:
                messagebox.showwarning("Aviso", "Preço inválido. Use números (ex: 12.99 ou 12,99)")
                self.entries['preco_venda'].focus_set()
                return

            # Obter descrição corretamente
            descricao = ''
            if hasattr(self.entries['descricao'], 'get'):
                if hasattr(self.entries['descricao'].get, '__code__') and self.entries['descricao'].get.__code__.co_argcount > 1:
                    descricao = self.entries['descricao'].get('1.0', 'end-1c')
                else:
                    descricao = self.entries['descricao'].get()
            
            dados = {
                'nome': nome.strip(),
                'tipo': self.entries['tipo'].get().strip(),
                'descricao': descricao.strip(),
                'preco_venda': preco,
                'unidade_medida': self.entries['unidade_medida'].get().strip(),
                'quantidade_minima': float(self.entries['quantidade_minima'].get() or 0)
            }

            # Operação no banco
            if produto_id:
                resultado = self.db.atualizar_produto(produto_id, **dados)
                msg = "atualizado"
            else:
                resultado = self.db.inserir_produto(**dados)
                msg = "cadastrado"

            if resultado:
                messagebox.showinfo("Sucesso", f"Produto {msg} com sucesso!")
                self.mostrar_produtos()
            else:
                messagebox.showerror("Erro", f"Falha ao {msg} produto")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar produto: {str(e)}")
    
    def editar_produto(self):
        """Abre formulário para editar produto selecionado"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto")
            return
            
        produto_id = self.tree_produtos.item(selecionado[0])['values'][0]
        self._criar_formulario_produto("Editar Produto", produto_id)
    
    def excluir_produto(self):
        """Exclui produto selecionado"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            return
            
        produto_id = self.tree_produtos.item(selecionado[0])['values'][0]
        nome = self.tree_produtos.item(selecionado[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir {nome}?"):
            try:
                if self.db.excluir_produto(produto_id):
                    self.tree_produtos.delete(selecionado[0])
                    messagebox.showinfo("Sucesso", "Produto excluído")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")
    
    def mostrar_fornecedores(self):
        """Mostra a tela de cadastro de fornecedores"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_fornecedores = self.db.listar_fornecedores()
                
                # Frame principal
                main_frame = tk.Frame(self.conteudo_frame)
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Título
                tk.Label(main_frame, text="FORNECEDORES", font=('Arial', 14, 'bold'), pady=10).pack()
                
                # Frame para conteúdo (botões + tabela)
                conteudo_frame = tk.Frame(main_frame)
                conteudo_frame.pack(fill='both', expand=True)
                
                # Frame para botões (lado esquerdo)
                botoes_frame = tk.Frame(conteudo_frame, width=150)
                botoes_frame.pack(side='left', fill='y', padx=(0, 10), pady=(0, 10))
                botoes_frame.pack_propagate(False)
                
                # Botão Novo Fornecedor
                self.btn_novo_forn = tk.Button(
                    botoes_frame,
                    text="Novo Fornecedor",
                    font=('Arial', 10, 'bold'),
                    bg='#4a6fa5',
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    command=self.novo_fornecedor
                )
                self.btn_novo_forn.pack(pady=2, fill='x')
                
                # Botão Editar
                self.btn_editar_forn = tk.Button(
                    botoes_frame,
                    text="Editar",
                    font=('Arial', 10, 'bold'),
                    bg='#4a6fa5',
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    state='disabled',
                    command=self.editar_fornecedor
                )
                self.btn_editar_forn.pack(pady=2, fill='x')
                
                # Botão Excluir
                self.btn_excluir_forn = tk.Button(
                    botoes_frame,
                    text="Excluir",
                    font=('Arial', 10, 'bold'),
                    bg='#f44336',
                    fg='white',
                    bd=0,
                    padx=10,
                    pady=5,
                    state='disabled',
                    command=self.excluir_fornecedor
                )
                self.btn_excluir_forn.pack(pady=2, fill='x')
                
                # Frame da tabela (lado direito)
                tabela_frame = tk.Frame(conteudo_frame, bg='white')
                tabela_frame.pack(side='left', fill='both', expand=True)
                
                # Cria a Treeview com as colunas solicitadas
                colunas = ("ID", "Empresa", "Vendedor", "Telefone", "Email")
                self.tree_fornecedores = ttk.Treeview(
                    tabela_frame,
                    columns=colunas,
                    show='headings',
                    selectmode='browse'
                )
                
                # Configura as colunas
                for col in colunas:
                    self.tree_fornecedores.heading(col, text=col)
                    self.tree_fornecedores.column(col, width=100, anchor='w')
                
                # Ajusta largura das colunas
                self.tree_fornecedores.column('ID', width=50, anchor='center')
                self.tree_fornecedores.column('Empresa', width=200)
                self.tree_fornecedores.column('Vendedor', width=150)
                self.tree_fornecedores.column('Telefone', width=120)
                
                # Barra de rolagem
                scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_fornecedores.yview)
                self.tree_fornecedores.configure(yscrollcommand=scrollbar.set)
                
                # Posiciona os widgets
                self.tree_fornecedores.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Preenche a tabela com dados
                for fornecedor in self.lista_fornecedores:
                    self.tree_fornecedores.insert('', 'end', values=(
                        fornecedor['id'],
                        fornecedor['empresa'],
                        fornecedor['vendedor'],
                        fornecedor['telefone'],
                        fornecedor['email']
                    ))
                
                # Evento de seleção na tabela
                self.tree_fornecedores.bind('<<TreeviewSelect>>', self.atualizar_botoes_fornecedores)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar fornecedores: {str(e)}")

    def atualizar_botoes_fornecedores(self, event=None):
        """Atualiza o estado dos botões com base na seleção"""
        selecionado = bool(self.tree_fornecedores.selection())
        state = 'normal' if selecionado else 'disabled'
        self.btn_editar_forn.config(state=state)
        self.btn_excluir_forn.config(state=state)
    
    def get_opcoes(self):
        """
        Retorna a lista de opções para a barra lateral.
        
        Returns:
            list: Lista de dicionários com as opções do menu
        """
        return [
            {"nome": "🏢 Empresa", "comando": self.mostrar_empresa},
            {"nome": "👥 Usuários", "comando": self.mostrar_usuarios},
            {"nome": "👷 Funcionários", "comando": self.mostrar_funcionarios},
            {"nome": "👤 Clientes", "comando": self.mostrar_clientes},
            {"nome": "📦 Produtos", "comando": self.mostrar_produtos},
            {"nome": "🏭 Fornecedores", "comando": self.mostrar_fornecedores}
        ]
    
    def limpar_conteudo(self):
        """Limpa o conteúdo da área de exibição"""
        # Destroi todos os widgets dentro do frame de conteúdo
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
            
        # Garante que o frame de conteúdo está visível e configurado corretamente
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Se houver uma view atual, limpa também
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            self.current_view = None
            
    def executar_acao(self, acao):
        """Executa a ação correspondente ao botão clicado na barra lateral"""
        if acao in self.acoes:
            self.acoes[acao]()
        else:
            messagebox.showwarning("Aviso", f"Ação '{acao}' não encontrada")


        
    def mostrar_tela(self, acao=None):
        """Mostra a tela correspondente à ação especificada"""
        # Limpa a view atual
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            
        # Cria a view solicitada ou a view padrão
        if acao == 'empresa':
            self.mostrar_empresa()
        elif acao == 'usuarios':
            self.mostrar_usuarios()
        elif acao == 'funcionarios':
            self.mostrar_funcionarios()
        elif acao == 'clientes':
            self.mostrar_clientes()
        elif acao == 'produtos':
            self.mostrar_produtos()
        elif acao == 'fornecedores':
            self.mostrar_fornecedores()
        else:
            self.mostrar_inicio()
            
        return self.frame
    
    def carregar_dados(self):
        """Carrega os dados iniciais do banco de dados"""
        # Este método não carrega mais dados na inicialização
        # Os dados serão carregados sob demanda quando cada aba for acessada
        pass
    
    def preencher_campos_empresa(self):
        """Preenche os campos do formulário com os dados da empresa"""
        if not self.dados_empresa:
            return
            
        try:
            # Mapeia os campos do formulário para as chaves do dicionário de dados
            campos = {
                'nome_fantasia': (self.empresa_nome, 'insert'),
                'razao_social': (self.empresa_razao, 'insert'),
                'cnpj': (self.empresa_cnpj, 'insert'),
                'inscricao_estadual': (self.empresa_ie, 'insert'),
                'telefone': (self.empresa_telefone, 'insert'),
                'endereco': (self.empresa_endereco, 'insert_text')
            }
            
            # Preenche cada campo com o valor correspondente, se existir
            for campo, (widget, method) in campos.items():
                if campo in self.dados_empresa and self.dados_empresa[campo] is not None:
                    valor = str(self.dados_empresa[campo])
                    if method == 'insert':
                        widget.delete(0, tk.END)
                        widget.insert(0, valor)
                    elif method == 'insert_text':
                        widget.delete('1.0', tk.END)
                        widget.insert('1.0', valor)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao preencher os dados da empresa: {str(e)}")
    
    def salvar_empresa(self):
        """Salva os dados da empresa"""
        try:
            # Coleta os dados dos campos
            dados = {
                'nome_fantasia': self.empresa_nome.get().strip(),
                'razao_social': self.empresa_razao.get().strip(),
                'cnpj': self.empresa_cnpj.get().strip(),
                'inscricao_estadual': self.empresa_ie.get().strip() or None,
                'telefone': self.empresa_telefone.get().strip() or None,
                'endereco': self.empresa_endereco.get('1.0', 'end-1c').strip() or None
            }
            
            # Validação do campo obrigatório
            if not dados['nome_fantasia']:
                messagebox.showwarning("Aviso", "O campo Nome Fantasia é obrigatório.")
                self.empresa_nome.focus_set()
                return
                
            # Formata o CNPJ se preenchido
            if dados['cnpj']:
                # Remove caracteres não numéricos do CNPJ
                cnpj_limpo = ''.join(filter(str.isdigit, dados['cnpj']))
                if len(cnpj_limpo) != 14:
                    messagebox.showwarning("Aviso", "CNPJ inválido. Deve conter 14 dígitos.")
                    self.empresa_cnpj.focus_set()
                    return
                # Formata o CNPJ
                dados['cnpj'] = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
            else:
                dados['cnpj'] = None
            
            # Salva os dados no banco
            sucesso, mensagem = self.db.salvar_empresa(dados)
            
            if sucesso:
                # Atualiza os dados em memória
                self.dados_empresa = self.db.obter_empresa() or {}
                messagebox.showinfo("Sucesso", "Dados da empresa salvos com sucesso!")
            else:
                messagebox.showerror("Erro", f"Não foi possível salvar os dados: {mensagem}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar os dados da empresa: {str(e)}")
    
    def cancelar_edicao(self):
        """Cancela a edição e volta para a tela inicial do módulo"""
        self.mostrar_inicio()

    def novo_fornecedor(self):
        """Abre formulário para novo fornecedor"""
        self._criar_formulario_fornecedor("Novo Fornecedor")
    
    def editar_fornecedor(self):
        """Abre formulário para editar fornecedor"""
        selecionado = self.tree_fornecedores.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um fornecedor")
            return
            
        fornecedor_id = self.tree_fornecedores.item(selecionado[0])['values'][0]
        self._criar_formulario_fornecedor("Editar Fornecedor", fornecedor_id)
    
    def excluir_fornecedor(self):
        """Exclui fornecedor selecionado"""
        selecionado = self.tree_fornecedores.selection()
        if not selecionado:
            return
            
        fornecedor_id = self.tree_fornecedores.item(selecionado[0])['values'][0]
        nome = self.tree_fornecedores.item(selecionado[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir {nome}?"):
            try:
                if self.db.excluir_fornecedor(fornecedor_id):
                    self.tree_fornecedores.delete(selecionado[0])
                    messagebox.showinfo("Sucesso", "Fornecedor excluído")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")
    
    def _criar_formulario_fornecedor(self, titulo, fornecedor_id=None):
        """Cria formulário completo para cadastro/edição de fornecedor"""
        self.limpar_conteudo()
        
        # Dados do fornecedor (se edição)
        self.fornecedor_atual = None
        if fornecedor_id and self.db:
            self.fornecedor_atual = self.db.obter_fornecedor(fornecedor_id)
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Campos do formulário
        campos = [
            ('Empresa:', 'empresa', 0),
            ('Vendedor:', 'vendedor', 1),
            ('Telefone:', 'telefone', 2),
            ('Email:', 'email', 3),
            ('Produtos:', 'produtos', 4)
        ]
        
        self.entries = {}
        for label, field, row in campos:
            # Label
            tk.Label(form_frame, text=label, font=('Arial', 10)).grid(row=row, column=0, sticky='e', padx=5, pady=5)
            
            # Entry
            entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            
            # Preenche com dados existentes se estiver editando
            if self.fornecedor_atual and field in self.fornecedor_atual:
                entry.insert(0, self.fornecedor_atual[field])
            
            self.entries[field] = entry
        
        # Campo de produtos como Text (para múltiplas linhas)
        self.txt_produtos = tk.Text(form_frame, height=5, width=40, font=('Arial', 10))
        self.txt_produtos.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        if self.fornecedor_atual and 'produtos' in self.fornecedor_atual:
            self.txt_produtos.insert('1.0', self.fornecedor_atual['produtos'])
        
        # Botões de ação
        botoes_frame = tk.Frame(main_frame)
        botoes_frame.pack(fill='x', pady=10)
        
        tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_fornecedor(fornecedor_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
        
        tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_fornecedores,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
    
    def _salvar_fornecedor(self, fornecedor_id=None):
        """Salva os dados do fornecedor no banco de dados"""
        dados = {
            'empresa': self.entries['empresa'].get(),
            'vendedor': self.entries['vendedor'].get(),
            'telefone': self.entries['telefone'].get(),
            'email': self.entries['email'].get(),
            'produtos': self.txt_produtos.get('1.0', 'end-1c')
        }
        
        try:
            if fornecedor_id:
                # Edição
                if self.db.atualizar_fornecedor(fornecedor_id, **dados):
                    messagebox.showinfo("Sucesso", "Fornecedor atualizado!")
            else:
                # Novo
                if self.db.inserir_fornecedor(**dados):
                    messagebox.showinfo("Sucesso", "Fornecedor cadastrado!")
            
            self.mostrar_fornecedores()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {str(e)}")

    def novo_cliente(self):
        """Abre formulário para novo cliente pendura"""
        self._criar_formulario_cliente("Novo Cliente Pendura")
    
    def editar_cliente(self):
        """Abre formulário para editar cliente pendura"""
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
            
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        self._criar_formulario_cliente("Editar Cliente Pendura", cliente_id)
    
    def excluir_cliente(self):
        """Exclui cliente pendura selecionado"""
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
            
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        nome = self.tree_clientes.item(selecionado[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir cliente {nome}?"):
            try:
                if self.db.excluir_cliente(cliente_id):
                    self.tree_clientes.delete(selecionado[0])
                    messagebox.showinfo("Sucesso", "Cliente excluído")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")
    
    def _criar_formulario_cliente(self, titulo, cliente_id=None):
        """Cria formulário para cadastro/edição de cliente pendura"""
        self.limpar_conteudo()
        
        # Dados do cliente (se edição)
        self.cliente_atual = None
        if cliente_id and self.db:
            self.cliente_atual = self.db.obter_cliente(cliente_id)
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Campos do formulário
        campos = [
            ('Nome:', 'nome', 0),
            ('Telefone:', 'telefone', 1),
            ('CPF:', 'cpf', 2),
            ('Endereço:', 'endereco', 3),
            ('Observações:', 'observacoes', 4)
        ]
        
        self.entries = {}
        for label, field, row in campos:
            # Label
            tk.Label(form_frame, text=label, font=('Arial', 10)).grid(row=row, column=0, sticky='e', padx=5, pady=5)
            
            # Entry
            entry = tk.Entry(form_frame, font=('Arial', 10), width=40)
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=5)
            
            # Preenche com dados existentes se estiver editando
            if self.cliente_atual and field in self.cliente_atual:
                entry.insert(0, self.cliente_atual[field])
            
            self.entries[field] = entry
        
        # Campo de observações como Text (para múltiplas linhas)
        self.txt_observacoes = tk.Text(form_frame, height=5, width=40, font=('Arial', 10))
        self.txt_observacoes.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        if self.cliente_atual and 'observacoes' in self.cliente_atual:
            self.txt_observacoes.insert('1.0', self.cliente_atual['observacoes'])
        
        # Botões de ação
        botoes_frame = tk.Frame(main_frame)
        botoes_frame.pack(fill='x', pady=10)
        
        tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_cliente(cliente_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
        
        tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_clientes,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5
        ).pack(side='left', padx=10)
    
    def _salvar_cliente(self, cliente_id=None):
        """Salva os dados do cliente no banco de dados"""
        dados = {
            'nome': self.entries['nome'].get(),
            'telefone': self.entries['telefone'].get(),
            'cpf': self.entries['cpf'].get(),
            'endereco': self.entries['endereco'].get(),
            'observacoes': self.txt_observacoes.get('1.0', 'end-1c')
        }
        
        try:
            if cliente_id:
                # Edição
                if self.db.atualizar_cliente(cliente_id, **dados):
                    messagebox.showinfo("Sucesso", "Cliente atualizado!")
            else:
                # Novo
                if self.db.inserir_cliente(**dados):
                    messagebox.showinfo("Sucesso", "Cliente cadastrado!")
            
            self.mostrar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {str(e)}")
