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
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
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
            "fornecedores": self.mostrar_fornecedores,
            "opcoes": self.mostrar_opcoes
        }
        
        
        # Mostra a tela inicial
        self.mostrar_inicio()
    
    def mostrar_opcoes(self):
        """Exibe o módulo de opções de produtos"""
        # Limpa o conteúdo atual
        self.limpar_conteudo()
        
        # Obtém a conexão com o banco de dados
        try:
            from src.db.database import DatabaseConnection
            db = DatabaseConnection()
            db_connection = db.get_connection()
            
            # Verifica se a conexão está ativa
            if not db_connection.is_connected():
                db_connection.reconnect()
                
            # Importa o módulo de opções
            from views.modulos.opcoes.opcoes_module import OpcoesModule
            
            # Cria a instância do módulo de opções
            self.opcoes_module = OpcoesModule(
                self.conteudo_frame, 
                self.controller,
                db_connection
            )
            
            # Configura o frame do módulo de opções
            self.opcoes_module.frame.pack(fill='both', expand=True, padx=10, pady=10)
            
        except Exception as e:
            import traceback
            error_msg = f"Erro ao conectar ao banco de dados: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Erro de Conexão", error_msg)
            print(error_msg)  # Log adicional no console para depuração
    
    def mostrar_inicio(self):
        """Mostra a tela inicial do módulo de cadastro"""
        self.limpar_conteudo()
        
        # Adiciona uma mensagem de boas-vindas
        tk.Label(
            self.conteudo_frame, 
            text="Selecione uma opção no menu lateral para começar.", 
            font=('Arial', 12),
            bg='#f0f2f5'
        ).pack(pady=20)
    
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
                fg='#000000'
            ).pack(side='left')
            
            # Frame do formulário
            form_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=20, pady=20)
            form_frame.pack(fill='both', expand=True)
            
            # Estilo dos labels e campos
            label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w'}
            entry_style = {'font': ('Arial', 10), 'bd': 0, 'relief': 'flat', 'width': 40, 'bg': 'white'}
            
            # Dados da Empresa
            tk.Label(form_frame, text="Dados da Empresa", font=('Arial', 12, 'bold'), bg='#f0f2f5').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            
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
            self.empresa_endereco = tk.Text(form_frame, width=40, height=5, font=('Arial', 10), bd=0, relief='flat', bg='white')
            self.empresa_endereco.grid(row=6, column=1, padx=10, pady=5, sticky='w')
            
            # Frame para os botões (abaixo dos campos)
            btn_frame = tk.Frame(form_frame, bg='#f0f2f5')
            btn_frame.grid(row=7, column=0, columnspan=2, pady=(20, 10), sticky='w')
            
            # Botão Salvar
            btn_salvar = tk.Button(
                btn_frame,
                text="Salvar",
                font=('Arial', 10, 'bold'),
                bg='#4a6fa5',
                fg='white',
                padx=15,
                pady=5,
                width=10,
                command=self.salvar_empresa
            )
            btn_salvar.pack(side='left', padx=5)
            
            # Botão Cancelar
            btn_cancelar = tk.Button(
                btn_frame,
                text="Cancelar",
                font=('Arial', 10, 'bold'),
                bg='#f44336',
                fg='white',
                padx=15,
                pady=5,
                width=10,
                command=self.cancelar_edicao
            )
            btn_cancelar.pack(side='left', padx=5)
            
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
                fg='#000000'
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
                foreground='#000000',
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
        """Cria formulário para cadastro/edição de usuário na mesma tela"""
        self.limpar_conteudo()
        
        # Dados do usuário (se edição)
        self.usuario_atual = None
        if usuario_id and self.db:
            self.usuario_atual = self.db.obter_usuario_por_id(usuario_id)
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='x')
        
        # Campos do formulário (específicos para usuário)
        campos = [
            ('Nome:', 'nome', 0),
            ('Login:', 'login', 1),
            ('Senha:', 'senha', 2),
            ('Nível Acesso:', 'nivel_acesso', 3),
            ('Telefone:', 'telefone', 4)
        ]
        
        self.entries_usuario = {}
        
        for row, (label, field, _) in enumerate(campos):
            tk.Label(form_frame, text=label).grid(row=row, column=0, sticky='e', padx=10, pady=5)
            
            entry = tk.Entry(form_frame, width=40, show='*' if field == 'senha' else None)
            entry.grid(row=row, column=1, sticky='w', padx=10, pady=5)
            self.entries_usuario[field] = entry
        
        # Preencher campos se for edição
        if self.usuario_atual:
            for field, widget in self.entries_usuario.items():
                if field in self.usuario_atual:
                    widget.delete(0, tk.END)
                    widget.insert(0, str(self.usuario_atual[field]))
        
        # Frame para os botões (abaixo dos campos)
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_usuario(usuario_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_usuarios,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_cancelar.pack(side='left', padx=5)

    def novo_usuario(self):
        """Abre formulário para novo usuário"""
        self._criar_formulario_usuario("Novo Usuário")

    def editar_usuario(self):
        """Abre formulário para editar usuário"""
        selecionado = self.tree_usuarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário")
            return
            
        usuario_id = self.tree_usuarios.item(selecionado[0])['values'][0]
        self._criar_formulario_usuario("Editar Usuário", usuario_id)
    
    def _salvar_usuario(self, usuario_id=None):
        """Salva os dados do usuário no banco de dados"""
        # Validação de campos obrigatórios
        if not all([self.entries_usuario['nome'].get().strip(), 
                   self.entries_usuario['login'].get().strip(), 
                   self.entries_usuario['senha'].get().strip()]):
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios (Nome, Login e Senha)")
            return
            
        # Preparar os dados para salvar
        dados = {
            'nome': self.entries_usuario['nome'].get().strip(),
            'login': self.entries_usuario['login'].get().strip(),
            'senha': self.entries_usuario['senha'].get().strip(),
            'nivel': self.entries_usuario['nivel_acesso'].get(),
            'telefone': self.entries_usuario.get('telefone', '').get().strip()  # Campo opcional
        }
        
        # Adiciona o ID se estiver editando
        if usuario_id:
            dados['id'] = usuario_id
        
        try:
            # Usa o método salvar_usuario do banco de dados
            if hasattr(self.db, 'salvar_usuario'):
                sucesso, mensagem = self.db.salvar_usuario(dados)
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    self.mostrar_usuarios()
                else:
                    messagebox.showerror("Erro", mensagem)
            else:
                # Fallback para métodos antigos se salvar_usuario não existir
                if usuario_id:
                    if self.db.atualizar_usuario(usuario_id, **dados):
                        messagebox.showinfo("Sucesso", "Usuário atualizado!")
                        self.mostrar_usuarios()
                else:
                    if self.db.inserir_usuario(**dados):
                        messagebox.showinfo("Sucesso", "Usuário cadastrado!")
                        self.mostrar_usuarios()
                        
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar usuário: {str(e)}")
            print(f"Erro ao salvar usuário: {str(e)}")
    
    def excluir_usuario(self):
        """Exclui o usuário selecionado após confirmação"""
        selecionado = self.tree_usuarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário")
            return
            
        usuario_id = self.tree_usuarios.item(selecionado[0])['values'][0]
        nome = self.tree_usuarios.item(selecionado[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir usuário {nome}?"):
            try:
                if self.db.excluir_usuario(usuario_id):
                    messagebox.showinfo("Sucesso", "Usuário excluído!")
                    self.mostrar_usuarios()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir usuário")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")
    
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
                fg='#000000'
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
                foreground='#000000',
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
        """Cria formulário para cadastro/edição de funcionário na mesma tela"""
        self.limpar_conteudo()
        
        # Dados do funcionário (se edição)
        self.funcionario_atual = None
        if funcionario_id and self.db:
            self.funcionario_atual = self.db.obter_funcionario(funcionario_id)
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='x')
        
        # Campos do formulário (específicos para funcionário)
        campos = [
            ('Nome:', 'nome', 0),
            ('Idade:', 'idade', 1),
            ('CPF:', 'cpf', 2),
            ('Cargo:', 'cargo', 3),
            ('Telefone:', 'telefone', 4),
            ('Endereço:', 'endereco', 5)
        ]
        
        self.entries = {}
        
        for row, (label, field, _) in enumerate(campos):
            # Label
            tk.Label(form_frame, text=label).grid(row=row, column=0, sticky='e', padx=10, pady=5)
            
            if field == 'endereco':
                # Text area para endereço
                text = tk.Text(form_frame, height=4, width=40)
                text.grid(row=row, column=1, sticky='w', padx=10, pady=5)
                self.entries[field] = text
            else:
                # Entry para outros campos
                entry = tk.Entry(form_frame, width=40)
                entry.grid(row=row, column=1, sticky='w', padx=10, pady=5)
                self.entries[field] = entry
        
        # Preencher campos se for edição
        if self.funcionario_atual:
            for field, widget in self.entries.items():
                if field in self.funcionario_atual:
                    if isinstance(widget, tk.Text):
                        widget.insert('1.0', str(self.funcionario_atual[field]))
                    elif isinstance(widget, tk.Entry):
                        widget.delete(0, tk.END)
                        widget.insert(0, str(self.funcionario_atual[field]))
        
        # Frame para os botões (abaixo dos campos)
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=6, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_funcionario(funcionario_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_funcionarios,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_cancelar.pack(side='left', padx=5)
    
    def novo_funcionario(self):
        """Abre formulário para novo funcionário"""
        self._criar_formulario_funcionario("Novo Funcionário")
    
    def editar_funcionario(self):
        """Abre formulário para editar funcionário"""
        selecionado = self.tree_funcionarios.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um funcionário")
            return
            
        funcionario_id = self.tree_funcionarios.item(selecionado[0])['values'][0]
        self._criar_formulario_funcionario("Editar Funcionário", funcionario_id)
    
    def _salvar_funcionario(self, funcionario_id=None):
        """Salva os dados do funcionário no banco de dados"""
        try:
            # Obtém os valores dos campos
            def get_valor(campo, padrao=''):
                widget = self.entries.get(campo)
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
                if 'nome' in self.entries:
                    self.entries['nome'].focus_set()
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
            if funcionario_id:
                # Atualiza funcionário existente
                resultado = self.db.atualizar_funcionario(funcionario_id, **dados)
                mensagem = "atualizado"
            else:
                # Cria novo funcionário
                resultado = self.db.inserir_funcionario(**dados)
                mensagem = "cadastrado"
            
            if resultado:
                messagebox.showinfo("Sucesso", f"Funcionário {mensagem} com sucesso!")
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
                    text="LISTA DE PRODUTOS", 
                    font=('Arial', 16, 'bold'),
                    bg='#f0f2f5',
                    fg='#000000'
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
                
                # Botão Novo Produto
                self.btn_novo_prod = tk.Button(
                    botoes_frame,
                    text="Novo Produto",
                    **btn_style,
                    command=self.novo_produto
                )
                self.btn_novo_prod.pack(pady=5, fill='x')
                
                # Botão Editar (inicialmente desabilitado)
                self.btn_editar_prod = tk.Button(
                    botoes_frame,
                    text="Editar",
                    **btn_style,
                    state='disabled',
                    command=self.editar_produto
                )
                self.btn_editar_prod.pack(pady=5, fill='x')
                
                # Botão Excluir (inicialmente desabilitado)
                btn_excluir_style = btn_style.copy()
                btn_excluir_style['bg'] = '#f44336'  # Cor vermelha para o botão excluir
                self.btn_excluir_prod = tk.Button(
                    botoes_frame,
                    text="Excluir",
                    **btn_excluir_style,
                    state='disabled',
                    command=self.excluir_produto
                )
                self.btn_excluir_prod.pack(pady=5, fill='x')
                
                # Frame para a tabela (lado direito)
                tabela_container = tk.Frame(main_frame, bg='#d1d8e0')
                tabela_container.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
                
                # Frame interno para a tabela
                tabela_frame = tk.Frame(tabela_container, bg='white', padx=1, pady=1)
                tabela_frame.pack(fill='both', expand=True, padx=1, pady=1)
                
                # Cabeçalho da tabela
                colunas = ("ID", "Nome", "Tipo", "Descrição", "Preço", "Unidade", "Estoque Mínimo")
                
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
                    foreground='#000000',
                    relief='flat')
                    
                style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
                
                self.tree_produtos = ttk.Treeview(
                    tabela_frame, 
                    columns=colunas, 
                    show='headings',
                    selectmode='browse',
                    style="Treeview"
                )
                
                # Configurando as colunas
                for col in colunas:
                    self.tree_produtos.heading(col, text=col)
                    self.tree_produtos.column(col, width=100, anchor='w')
                
                # Ajustando largura das colunas
                self.tree_produtos.column('ID', width=50, anchor='center')
                self.tree_produtos.column('Nome', width=200)
                self.tree_produtos.column('Tipo', width=100)
                self.tree_produtos.column('Descrição', width=250)
                self.tree_produtos.column('Preço', width=100, anchor='e')
                self.tree_produtos.column('Unidade', width=80)
                self.tree_produtos.column('Estoque Mínimo', width=100)
                
                # Adicionando barra de rolagem
                scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_produtos.yview)
                self.tree_produtos.configure(yscrollcommand=scrollbar.set)
                
                # Posicionando os widgets
                self.tree_produtos.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Preenchendo a tabela com os dados
                for produto in self.lista_produtos:
                    self.tree_produtos.insert(
                        '', 'end', 
                        values=(
                            produto.get('id', ''),
                            produto.get('nome', ''),
                            produto.get('tipo', ''),
                            produto.get('descricao', ''),
                            f"R$ {produto.get('preco_venda', 0):.2f}",
                            produto.get('unidade_medida', 'UN'),
                            produto.get('quantidade_minima', 0)
                        )
                    )
                
                # Configurar evento de seleção
                self.tree_produtos.bind('<<TreeviewSelect>>', self.atualizar_botoes_produtos)
                
                # Ajustando o layout
                self.conteudo_frame.update_idletasks()
                
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
        
        # Frame para os botões de ação (abaixo dos campos)
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=6, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_produto(produto_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_produtos,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_cancelar.pack(side='left', padx=5)
    
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
                    text="LISTA DE FORNECEDORES", 
                    font=('Arial', 16, 'bold'),
                    bg='#f0f2f5',
                    fg='#000000'
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
                
                # Botão Novo Fornecedor
                self.btn_novo_forn = tk.Button(
                    botoes_frame,
                    text="Novo Fornecedor",
                    **btn_style,
                    command=self.novo_fornecedor
                )
                self.btn_novo_forn.pack(pady=5, fill='x')
                
                # Botão Editar (inicialmente desabilitado)
                self.btn_editar_forn = tk.Button(
                    botoes_frame,
                    text="Editar",
                    **btn_style,
                    state='disabled',
                    command=self.editar_fornecedor
                )
                self.btn_editar_forn.pack(pady=5, fill='x')
                
                # Botão Excluir (inicialmente desabilitado)
                btn_excluir_style = btn_style.copy()
                btn_excluir_style['bg'] = '#f44336'  # Cor vermelha para o botão excluir
                self.btn_excluir_forn = tk.Button(
                    botoes_frame,
                    text="Excluir",
                    **btn_excluir_style,
                    state='disabled',
                    command=self.excluir_fornecedor
                )
                self.btn_excluir_forn.pack(pady=5, fill='x')
                
                # Frame para a tabela (lado direito)
                tabela_container = tk.Frame(main_frame, bg='#d1d8e0')
                tabela_container.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
                
                # Frame interno para a tabela
                tabela_frame = tk.Frame(tabela_container, bg='white', padx=1, pady=1)
                tabela_frame.pack(fill='both', expand=True, padx=1, pady=1)
                
                # Cabeçalho da tabela
                colunas = ("ID", "Empresa", "Vendedor", "Telefone", "Email")
                
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
                    foreground='#000000',
                    relief='flat')
                    
                style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
                
                self.tree_fornecedores = ttk.Treeview(
                    tabela_frame, 
                    columns=colunas, 
                    show='headings',
                    selectmode='browse',
                    style="Treeview"
                )
                
                # Configurando as colunas
                for col in colunas:
                    self.tree_fornecedores.heading(col, text=col)
                    self.tree_fornecedores.column(col, width=100, anchor='w')
                
                # Ajustando largura das colunas
                self.tree_fornecedores.column('ID', width=50, anchor='center')
                self.tree_fornecedores.column('Empresa', width=200)
                self.tree_fornecedores.column('Vendedor', width=150)
                self.tree_fornecedores.column('Telefone', width=120)
                self.tree_fornecedores.column('Email', width=180)
                
                # Adicionando barra de rolagem
                scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_fornecedores.yview)
                self.tree_fornecedores.configure(yscrollcommand=scrollbar.set)
                
                # Posicionando os widgets
                self.tree_fornecedores.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Preenchendo a tabela com os dados
                for fornecedor in self.lista_fornecedores:
                    self.tree_fornecedores.insert(
                        '', 'end', 
                        values=(
                            fornecedor['id'],
                            fornecedor['empresa'],
                            fornecedor['vendedor'],
                            fornecedor['telefone'],
                            fornecedor['email']
                        )
                    )
                
                # Configurar evento de seleção
                self.tree_fornecedores.bind('<<TreeviewSelect>>', self.atualizar_botoes_fornecedores)
                
                # Ajustando o layout
                self.conteudo_frame.update_idletasks()
                
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
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
            
        # Se houver uma view atual, limpa também
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            self.current_view = None
            
        # Garante que a cor de fundo seja mantida
        self.conteudo_frame.configure(bg='#f0f2f5')
            
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
        
        # Frame para os botões (abaixo dos campos)
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_fornecedor(fornecedor_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_fornecedores,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_cancelar.pack(side='left', padx=5)
    
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
        self._criar_formulario_cliente("Novo Cliente")
    
    def editar_cliente(self):
        """Abre formulário para editar cliente pendura"""
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
            
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        self._criar_formulario_cliente("Editar Cliente", cliente_id)
    
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
        
        # Frame para os botões de ação (abaixo dos campos)
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=lambda: self._salvar_cliente(cliente_id),
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_salvar.pack(side='left', padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=self.mostrar_clientes,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_cancelar.pack(side='left', padx=5)
    
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
    
    def mostrar_clientes(self):
        """Mostra a tela de clientes pendura"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_clientes = self.db.listar_clientes(ativo=True)
                
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
                    text="LISTA DE CLIENTES", 
                    font=('Arial', 16, 'bold'),
                    bg='#f0f2f5',
                    fg='#000000'
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
                
                # Botão Novo Cliente
                self.btn_novo_cliente = tk.Button(
                    botoes_frame,
                    text="Novo Cliente",
                    **btn_style,
                    command=self.novo_cliente
                )
                self.btn_novo_cliente.pack(pady=5, fill='x')
                
                # Botão Editar (inicialmente desabilitado)
                self.btn_editar_cliente = tk.Button(
                    botoes_frame,
                    text="Editar",
                    **btn_style,
                    state='disabled',
                    command=self.editar_cliente
                )
                self.btn_editar_cliente.pack(pady=5, fill='x')
                
                # Botão Excluir (inicialmente desabilitado)
                btn_excluir_style = btn_style.copy()
                btn_excluir_style['bg'] = '#f44336'  # Cor vermelha para o botão excluir
                self.btn_excluir_cliente = tk.Button(
                    botoes_frame,
                    text="Excluir",
                    **btn_excluir_style,
                    state='disabled',
                    command=self.excluir_cliente
                )
                self.btn_excluir_cliente.pack(pady=5, fill='x')
                
                # Frame para a tabela (lado direito)
                tabela_container = tk.Frame(main_frame, bg='#d1d8e0')
                tabela_container.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
                
                # Frame interno para a tabela
                tabela_frame = tk.Frame(tabela_container, bg='white', padx=1, pady=1)
                tabela_frame.pack(fill='both', expand=True, padx=1, pady=1)
                
                # Cabeçalho da tabela
                colunas = ("ID", "Nome", "Telefone", "CPF", "Data Cadastro")
                
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
                    foreground='#000000',
                    relief='flat')
                    
                style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
                
                self.tree_clientes = ttk.Treeview(
                    tabela_frame, 
                    columns=colunas, 
                    show='headings',
                    selectmode='browse',
                    style="Treeview"
                )
                
                # Configurando as colunas
                for col in colunas:
                    self.tree_clientes.heading(col, text=col)
                    self.tree_clientes.column(col, width=100, anchor='w')
                
                # Ajustando largura das colunas
                self.tree_clientes.column('ID', width=50, anchor='center')
                self.tree_clientes.column('Nome', width=200)
                self.tree_clientes.column('Telefone', width=120)
                self.tree_clientes.column('CPF', width=120)
                self.tree_clientes.column('Data Cadastro', width=120)
                
                # Adicionando barra de rolagem
                scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_clientes.yview)
                self.tree_clientes.configure(yscrollcommand=scrollbar.set)
                
                # Posicionando os widgets
                self.tree_clientes.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                
                # Preenchendo a tabela com os dados
                for cliente in self.lista_clientes:
                    data_formatada = cliente['data_cadastro'].strftime('%d/%m/%Y') if cliente['data_cadastro'] else ''
                    self.tree_clientes.insert(
                        '', 'end', 
                        values=(
                            cliente.get('id', ''),
                            cliente.get('nome', ''),
                            cliente.get('telefone', ''),
                            cliente.get('cpf', ''),
                            data_formatada
                        )
                    )
                
                # Configurar evento de seleção
                self.tree_clientes.bind('<<TreeviewSelect>>', self.atualizar_botoes_clientes)
                
                # Ajustando o layout
                self.conteudo_frame.update_idletasks()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {str(e)}")
