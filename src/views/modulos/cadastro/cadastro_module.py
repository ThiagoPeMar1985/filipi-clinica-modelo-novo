"""
Módulo de Cadastro - Gerencia cadastros do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# Importar configurações de estilo
from config.estilos import CORES, FONTES, aplicar_estilo

# Adicione o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Importações locais
from src.controllers.cadastro_controller import CadastroController
from ..base_module import BaseModule


class CadastroModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        super().__init__(parent, controller)
        
        # Inicializa a conexão com o banco de dados
        self.db = CadastroController(db_connection) if db_connection else None
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Frame para o conteúdo
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dados em memória
        self.dados_empresa = {}
        self.lista_usuarios = []
        self.lista_medicos = []
        self.lista_clientes = []
      
        
        
        # Mapeamento de ações para as funções correspondentes
        self.acoes = {
            "inicio": self.mostrar_inicio,
            "empresa": self.mostrar_empresa,
            "usuarios": self.mostrar_usuarios,
            "medicos": self.mostrar_medicos,
            "clientes": self.mostrar_clientes,
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
            self.dados_empresa = self.db.obter_empresa() or {}
            
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
            entry_style = {'font': ('Arial', 10), 'bd': 0, 'relief': 'flat', 'bg': 'white'}
            
            # Inicializa os atributos dos campos como None
            self.empresa_nome = None
            self.empresa_razao = None
            self.empresa_cnpj = None
            self.empresa_ie = None
            self.empresa_telefone = None
            self.empresa_endereco = None
            self.empresa_cep = None
            self.empresa_bairro = None
            self.empresa_cidade = None
            self.empresa_estado = None
            self.empresa_numero = None
            
            # Dados da Empresa
            tk.Label(form_frame, text="Dados da Empresa", font=('Arial', 12, 'bold'), bg='#f0f2f5').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            
            # Nome Fantasia
            tk.Label(form_frame, text="Nome Fantasia*:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky='w')
            self.empresa_nome = tk.Entry(form_frame, **entry_style, width=50)
            self.empresa_nome.grid(row=1, column=1, padx=10, pady=5, sticky='w')
            
            # Razão Social
            tk.Label(form_frame, text="Razão Social:", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky='w')
            self.empresa_razao = tk.Entry(form_frame, **entry_style, width=50)
            self.empresa_razao.grid(row=2, column=1, padx=10, pady=5, sticky='w')
            
            # CNPJ
            tk.Label(form_frame, text="CNPJ*:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky='w')
            self.empresa_cnpj = tk.Entry(form_frame, **entry_style, width=25)
            self.empresa_cnpj.grid(row=3, column=1, padx=10, pady=5, sticky='w')
            
            # Inscrição Estadual
            tk.Label(form_frame, text="Inscrição Estadual:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky='w')
            self.empresa_ie = tk.Entry(form_frame, **entry_style, width=25)
            self.empresa_ie.grid(row=4, column=1, padx=10, pady=5, sticky='w')
            
            # Telefone
            tk.Label(form_frame, text="Telefone:", **label_style).grid(row=5, column=0, padx=10, pady=5, sticky='w')
            self.empresa_telefone = tk.Entry(form_frame, **entry_style, width=25)
            self.empresa_telefone.grid(row=5, column=1, padx=10, pady=5, sticky='w')
            
            # CEP
            tk.Label(form_frame, text="CEP:", **label_style).grid(row=6, column=0, padx=10, pady=5, sticky='w')
            self.empresa_cep = tk.Entry(form_frame, **entry_style, width=15)
            self.empresa_cep.grid(row=6, column=1, padx=10, pady=5, sticky='w')
            
            # Endereço
            tk.Label(form_frame, text="Endereço:", **label_style).grid(row=7, column=0, padx=10, pady=5, sticky='w')
            self.empresa_endereco = tk.Entry(form_frame, **entry_style, width=50)
            self.empresa_endereco.grid(row=7, column=1, padx=10, pady=5, sticky='w')
            
            # Número
            tk.Label(form_frame, text="Número:", **label_style).grid(row=8, column=0, padx=10, pady=5, sticky='w')
            self.empresa_numero = tk.Entry(form_frame, **entry_style, width=10)
            self.empresa_numero.grid(row=8, column=1, padx=10, pady=5, sticky='w')
            
            # Bairro
            tk.Label(form_frame, text="Bairro:", **label_style).grid(row=9, column=0, padx=10, pady=5, sticky='w')
            self.empresa_bairro = tk.Entry(form_frame, **entry_style, width=40)
            self.empresa_bairro.grid(row=9, column=1, padx=10, pady=5, sticky='w')
            
            # Cidade
            tk.Label(form_frame, text="Cidade:", **label_style).grid(row=10, column=0, padx=10, pady=5, sticky='w')
            self.empresa_cidade = tk.Entry(form_frame, **entry_style, width=30)
            self.empresa_cidade.grid(row=10, column=1, padx=10, pady=5, sticky='w')
            
            # Estado (UF)
            tk.Label(form_frame, text="UF:", **label_style).grid(row=11, column=0, padx=10, pady=5, sticky='w')
            self.empresa_estado = ttk.Combobox(form_frame, values=[
                'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
                'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
                'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
            ], state='readonly', font=('Arial', 10), width=5)
            self.empresa_estado.grid(row=11, column=1, padx=10, pady=5, sticky='w')
            
            # Frame para os botões (abaixo dos campos)
            btn_frame = tk.Frame(form_frame, bg='#f0f2f5')
            btn_frame.grid(row=12, column=0, columnspan=2, pady=(20, 10), sticky='w')
            
            # Botão Salvar
            btn_salvar = tk.Button(
                btn_frame,
                text="Salvar",
                font=('Arial', 10, 'bold'),
                bg='#4a6fa5',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                width=15,
                command=self.salvar_empresa
            )
            btn_salvar.pack(side='left', padx=5)
            
            # Botão Cancelar removido conforme solicitado
            
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
                foreground="#000000",
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
            ('Nível :', 'nivel', 3),
            ('Telefone:', 'telefone', 4)
        ]
        
        self.entries_usuario = {}
        
        for row, (label, field, _) in enumerate(campos):
            tk.Label(form_frame, text=label).grid(row=row, column=0, sticky='e', padx=10, pady=5)
            
            if field == 'nivel':
                # Usar ComboBox para o nível de acesso
                nivel_var = tk.StringVar()
                combo = ttk.Combobox(
                    form_frame, 
                    textvariable=nivel_var,
                    values=['básico', 'master'],
                    state='readonly',
                    width=37
                )
                combo.grid(row=row, column=1, sticky='w', padx=10, pady=5)
                self.entries_usuario[field] = combo
            else:
                # Campo de texto normal para os outros campos
                entry = tk.Entry(form_frame, width=40, show='*' if field == 'senha' else None)
                entry.grid(row=row, column=1, sticky='w', padx=10, pady=5)
                self.entries_usuario[field] = entry
        
        # Preencher campos se for edição
        if self.usuario_atual:
            for field, widget in self.entries_usuario.items():
                if field in self.usuario_atual and self.usuario_atual[field]:
                    if field == 'nivel':
                        # Definir o valor do ComboBox
                        widget.set(self.usuario_atual[field])
                    else:
                        # Para campos de texto normais
                        if isinstance(widget, tk.Entry):
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
        if not self.db:
            messagebox.showerror("Erro", "Conexão com o banco de dados não disponível")
            return
            
        try:
            # Validação de campos obrigatórios
            campos_obrigatorios = {
                'nome': 'Nome',
                'login': 'Login',
                'senha': 'Senha'
            }
            
            campos_faltando = [nome for campo, nome in campos_obrigatorios.items() 
                            if not self.entries_usuario[campo].get().strip()]
            
            if campos_faltando:
                messagebox.showwarning(
                    "Aviso", 
                    f"Preencha todos os campos obrigatórios:\n" + 
                    "\n".join(f"- {campo}" for campo in campos_faltando)
                )
                return
                
            # Validar nível de acesso
            nivel = self.entries_usuario['nivel'].get().strip()
            if nivel not in ['básico', 'master']:
                messagebox.showwarning("Aviso", "Selecione um nível de acesso válido (básico ou master)")
                return
                
            # Preparar os dados para salvar
            dados = {
                'nome': self.entries_usuario['nome'].get().strip(),
                'login': self.entries_usuario['login'].get().strip(),
                'senha': self.entries_usuario['senha'].get().strip(),
                'nivel': nivel,
                'telefone': self.entries_usuario['telefone'].get().strip() if 'telefone' in self.entries_usuario else ''
            }
            
            # Adiciona o ID se estiver editando
            if usuario_id:
                dados['id'] = usuario_id
            
            # Verificar se já existe um usuário com o mesmo login (apenas para novos usuários)
            if not usuario_id:
                cursor = self.db.db.cursor()
                cursor.execute("SELECT id FROM usuarios WHERE login = %s", (dados['login'],))
                if cursor.fetchone():
                    messagebox.showwarning(
                        "Aviso", 
                        f"Já existe um usuário com o login '{dados['login']}'"
                    )
                    return
            
            # Usa o método salvar_usuario do banco de dados
            if hasattr(self.db, 'salvar_usuario'):
                sucesso, mensagem = self.db.salvar_usuario(dados)
                if sucesso:
                    messagebox.showinfo("Sucesso", "Usuário salvo com sucesso!")
                    self.mostrar_usuarios()
                else:
                    messagebox.showerror("Erro", f"Falha ao salvar usuário: {mensagem}")
            else:
                # Fallback para métodos antigos se salvar_usuario não existir
                if usuario_id:
                    if self.db.atualizar_usuario(usuario_id, **dados):
                        messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                        self.mostrar_usuarios()
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar usuário")
                else:
                    if self.db.inserir_usuario(**dados):
                        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                        self.mostrar_usuarios()
                    else:
                        messagebox.showerror("Erro", "Falha ao cadastrar usuário")
                        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro detalhado ao salvar usuário:\n{error_details}")
            messagebox.showerror(
                "Erro", 
                f"Ocorreu um erro ao salvar o usuário:\n{str(e)}"
            )
    
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
                    self.mostrar_usuarios()
                else:
                    messagebox.showerror("Erro", "Falha ao excluir usuário")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")
    
    def mostrar_medicos(self):
        """Mostra a tela de cadastro de funcionários"""
        self.limpar_conteudo()
        
        try:
            if not self.db:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
                return
                
            # Carrega a lista de funcionários
            self.lista_funcionarios = self.db.listar_medicos()
            
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
                text="LISTA DE MÉDICOS", 
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
            cabecalho = ['ID', 'Nome', 'CRM', 'Especialidade', 'Telefone']
            
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
            self.tree_funcionarios.column('CRM', width=60, anchor='center')
            self.tree_funcionarios.column('Especialidade', width=120)
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
                        funcionario.get('crm', ''),
                        funcionario.get('especialidade', ''),
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
        """Cria formulário para cadastro/edição de médico na mesma tela"""
        self.limpar_conteudo()
        
        # Dados do médico (se edição)
        self.medico_atual = None
        if funcionario_id and self.db:
            try:
                self.medico_atual = self.db.obter_medico_por_id(funcionario_id)
                if not self.medico_atual:
                    messagebox.showerror("Erro", "Médico não encontrado")
                    self.mostrar_medicos()
                    return
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar dados do médico: {e}")
                self.mostrar_medicos()
                return
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='x')
        
        # Função para formatar telefone
        def format_telefone(event=None):
            text = entry_telefone.get().replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            if len(text) > 11:
                text = text[:11]
            if len(text) > 0:
                if len(text) <= 2:
                    text = f"({text}"
                elif len(text) <= 7:
                    text = f"({text[:2]}) {text[2:]}"
                else:
                    text = f"({text[:2]}) {text[2:7]}-{text[7:]}"
            entry_telefone.delete(0, tk.END)
            entry_telefone.insert(0, text)
        
        # Função para formatar CRM (apenas números)
        def format_crm(event=None):
            text = ''.join(filter(str.isdigit, entry_crm.get()))
            if len(text) > 15:  # Limita o tamanho do CRM
                text = text[:15]
            entry_crm.delete(0, tk.END)
            entry_crm.insert(0, text)
        
        # Campos do formulário
        # Nome
        tk.Label(form_frame, text="Nome Completo:").grid(row=0, column=0, sticky='e', padx=10, pady=5)
        entry_nome = tk.Entry(form_frame, width=40)
        entry_nome.grid(row=0, column=1, sticky='w', pady=5, padx=(0, 10))
        
        # CRM
        tk.Label(form_frame, text="CRM:").grid(row=1, column=0, sticky='e', padx=10, pady=5)
        entry_crm = tk.Entry(form_frame, width=20)
        entry_crm.grid(row=1, column=1, sticky='w', pady=5, padx=(0, 10))
        entry_crm.bind('<KeyRelease>', format_crm)
        
        # Especialidade
        tk.Label(form_frame, text="Especialidade:").grid(row=2, column=0, sticky='e', padx=10, pady=5)
        entry_especialidade = tk.Entry(form_frame, width=40)
        entry_especialidade.grid(row=2, column=1, sticky='w', pady=5, padx=(0, 10))
        
        # Telefone
        tk.Label(form_frame, text="Telefone:").grid(row=3, column=0, sticky='e', padx=10, pady=5)
        entry_telefone = tk.Entry(form_frame, width=20)
        entry_telefone.grid(row=3, column=1, sticky='w', pady=5, padx=(0, 10))
        entry_telefone.bind('<KeyRelease>', format_telefone)
        
        # E-mail
        tk.Label(form_frame, text="E-mail:").grid(row=4, column=0, sticky='e', padx=10, pady=5)
        entry_email = tk.Entry(form_frame, width=40)
        entry_email.grid(row=4, column=1, sticky='w', pady=5, padx=(0, 10))
        
        # Dicionário para acessar os campos
        self.entries = {
            'nome': entry_nome,
            'crm': entry_crm,
            'especialidade': entry_especialidade,
            'telefone': entry_telefone,
            'email': entry_email
        }
        
        # Preencher campos se for edição
        if self.medico_atual:
            entry_nome.insert(0, self.medico_atual.get('nome', ''))
            entry_crm.insert(0, self.medico_atual.get('crm', ''))
            entry_especialidade.insert(0, self.medico_atual.get('especialidade', ''))
            entry_telefone.insert(0, self.medico_atual.get('telefone', ''))
            # Garante que o email seja uma string vazia se for None
            email = self.medico_atual.get('email')
            if email is None:
                email = ''
            entry_email.insert(0, email)
        
        # Frame para os botões
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
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
            command=self.mostrar_medicos,
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            padx=15,
            pady=5,
            width=10
        )
        btn_cancelar.pack(side='left', padx=5)
        
        # Focar no primeiro campo
        entry_nome.focus_set()
    
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
        """Salva os dados do médico no banco de dados"""
        try:
            # Obtém os valores dos campos
            nome = self.entries['nome'].get().strip()
            crm = self.entries['crm'].get().strip()
            especialidade = self.entries['especialidade'].get().strip()
            telefone = self.entries['telefone'].get().strip()
            email = self.entries['email'].get().strip()
            
            # Verificação básica de campos obrigatórios
            if not nome or not crm:
                messagebox.showwarning("Atenção", "Os campos Nome e CRM são obrigatórios!")
                return
                
            # Prepara os dados para salvar
            dados = {
                'nome': nome,
                'crm': crm,
                'especialidade': especialidade,
                'telefone': telefone,
                'email': email
            }
            
            # Adiciona o ID se for uma atualização
            if funcionario_id:
                dados['id'] = funcionario_id
            
            # Salva no banco de dados
            if self.db:
                try:
                    if funcionario_id:
                        # Atualiza médico existente
                        if self.db.salvar_medico(dados):
                            messagebox.showinfo("Sucesso", "Médico atualizado com sucesso!")
                            self.mostrar_medicos()
                        else:
                            messagebox.showerror("Erro", "Não foi possível atualizar o médico.")
                    else:
                        # Insere novo médico
                        novo_id = self.db.salvar_medico(dados)
                        if novo_id:
                            messagebox.showinfo("Sucesso", "Médico cadastrado com sucesso!")
                            self.mostrar_medicos()
                        else:
                            messagebox.showerror("Erro", "Não foi possível cadastrar o médico.")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar médico: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                messagebox.showerror("Erro", "Conexão com o banco de dados não disponível.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar o formulário: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
            self.excluir_medico(funcionario_id)
    
    def excluir_medico(self, funcionario_id):
        """Exclui um funcionário do banco de dados"""
        try:
            if self.db.excluir_medico(funcionario_id):
                self.mostrar_medicos()  # Atualiza a lista
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

    
    def get_opcoes(self):
        """
        Retorna a lista de opções para a barra lateral.
        
        Returns:
            list: Lista de dicionários com as opções do menu
        """
        return [
            {"nome": "🏢 Empresa", "comando": self.mostrar_empresa},
            {"nome": "👥 Usuários", "comando": self.mostrar_usuarios},
            {"nome": "👷 Médicos", "comando": self.mostrar_medicos},
            {"nome": "👤 Clientes", "comando": self.mostrar_clientes},
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
        # Se a ação for 'mostrar_inicio', chama diretamente o método mostrar_inicio
        if acao == 'mostrar_inicio':
            self.mostrar_inicio()
            return
            
        # Para outras ações, verifica se existe no dicionário de ações
        if acao in self.acoes:
            self.acoes[acao]()
        else:
            # Se a ação não for encontrada, mostra a tela inicial
            self.mostrar_inicio()
            
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
        elif acao == 'medicos':
            self.mostrar_medicos()
        elif acao == 'clientes':
            self.mostrar_clientes()
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
                'endereco': (self.empresa_endereco, 'insert'),
                'cep': (self.empresa_cep, 'insert'),
                'bairro': (self.empresa_bairro, 'insert'),
                'cidade': (self.empresa_cidade, 'insert'),
                'estado': (self.empresa_estado, 'set'),
                'numero': (self.empresa_numero, 'insert')
            }
            
            # Preenche cada campo com o valor correspondente, se existir
            for campo, (widget, method) in campos.items():
                if campo in self.dados_empresa and self.dados_empresa[campo] is not None:
                    valor = str(self.dados_empresa[campo])
                    if method == 'insert':
                        widget.delete(0, tk.END)
                        widget.insert(0, valor)
                    elif method == 'set':
                        widget.set(valor)
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
                'endereco': self.empresa_endereco.get().strip() or None,
                'cep': self.empresa_cep.get().strip() or None,
                'bairro': self.empresa_bairro.get().strip() or None,
                'cidade': self.empresa_cidade.get().strip() or None,
                'estado': self.empresa_estado.get().strip() or None,
                'numero': self.empresa_numero.get().strip() or None
            }
            
            # Converte o número para inteiro se não for None e for um dígito
            if dados['numero'] and isinstance(dados['numero'], str) and dados['numero'].strip().isdigit():
                dados['numero'] = int(dados['numero'])
            else:
                dados['numero'] = None
            
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
                    # Removida mensagem de sucesso conforme solicitado
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")
    
    def novo_cliente(self):
        """Abre formulário para novo cliente usando a tabela clientes_delivery"""
        self._criar_formulario_cliente("Novo Cliente")
    
    def editar_cliente(self):
        """Abre formulário para editar cliente usando a tabela clientes_delivery"""
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
            
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        self._criar_formulario_cliente("Editar Cliente", cliente_id)
    
    def excluir_cliente(self):
        """Exclui cliente selecionado usando a tabela clientes_delivery"""
        selecionado = self.tree_clientes.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente")
            return
            
        cliente_id = self.tree_clientes.item(selecionado[0])['values'][0]
        nome = self.tree_clientes.item(selecionado[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir cliente {nome}?"):
            try:
                # Usar o CadastroController para excluir o cliente
                from src.controllers.cliente_controller import ClienteController
                cliente_controller = ClienteController()
                if cliente_controller.excluir_cliente(cliente_id):
                    self.tree_clientes.delete(selecionado[0])
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o cliente")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def _criar_formulario_cliente(self, titulo, cliente_id=None):
        """Cria formulário para cadastro/edição de cliente usando a tabela pacientes"""
        self.limpar_conteudo()
        
        # Dados do cliente (se edição)
        self.cliente_atual = None
        if cliente_id:
            # Usar o ClienteController para obter os dados do cliente
            from src.controllers.cliente_controller import ClienteController
            cliente_controller = ClienteController()
            sucesso, self.cliente_atual = cliente_controller.buscar_cliente_por_id(cliente_id)
            if not sucesso or not self.cliente_atual:
                messagebox.showwarning("Aviso", "Não foi possível carregar os dados do cliente.")
                self.mostrar_clientes()
                return
        
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Título
        tk.Label(main_frame, text=titulo, font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Campos do formulário - Reorganizados para colocar CEP antes do endereço
        campos = [
            ('Nome:', 'nome', 0, 0, 40),  # Adicionado o parâmetro de largura
            ('Data Nasc.:', 'data_nascimento', 0, 2, 15),
            ('Telefone:', 'telefone', 1, 0, 15),
            ('Telefone 2:', 'telefone2', 1, 2, 15),
            ('Email:', 'email', 2, 0, 40),
            ('CPF:', 'cpf', 2, 2, 15),
            ('CEP:', 'cep', 3, 0, 15),
            ('Endereço:', 'endereco', 4, 0, 40),
            ('Número:', 'numero', 4, 2, 15),
            ('Complemento:', 'complemento', 5, 0, 40),
            ('Bairro:', 'bairro', 6, 0, 20),
            ('Cidade:', 'cidade', 6, 2, 20),
            ('UF:', 'uf', 7, 0, 5),
            ('Ponto de Referência:', 'ponto_referencia', 8, 0, 40),
            ('Observações:', 'observacoes', 9, 0, 40)
        ]
        
        self.entries = {}
        for label, field, row, col, width in campos:  # Adicionado width nos parâmetros
            # Label
            tk.Label(form_frame, text=label, font=('Arial', 10)).grid(row=row, column=col, sticky='e', padx=5, pady=5)
            
            # Entry
            entry = tk.Entry(form_frame, font=('Arial', 10), width=width)
            entry.grid(row=row, column=col+1, sticky='w', padx=5, pady=5)
            self.entries[field] = entry
            
            # Preenche com dados existentes se estiver editando
            if self.cliente_atual and field in self.cliente_atual and self.cliente_atual[field] is not None:
                if field != 'observacoes':  # O campo observações é tratado separadamente
                    self.entries[field].insert(0, str(self.cliente_atual[field]))
            
            # Adiciona botão de busca ao lado do campo CEP
            if field == 'cep':
                btn_buscar_cep = tk.Button(
                    form_frame,
                    text="Buscar",
                    command=self.buscar_cep,
                    font=('Arial', 9),
                    bg='#4a6fa5',
                    fg='white',
                    padx=5,
                    pady=2
                )
                btn_buscar_cep.grid(row=row, column=col+2, padx=5, pady=5)
                
                # Adiciona evento para buscar CEP ao pressionar Enter no campo
                self.entries['cep'].bind('<Return>', lambda event: self.buscar_cep())
        
        # Campo de observações como Text (para múltiplas linhas)
        self.txt_observacoes = tk.Text(form_frame, height=5, width=40, font=('Arial', 10))
        self.txt_observacoes.grid(row=9, column=1, sticky='w', padx=5, pady=5)
        if self.cliente_atual and 'observacoes' in self.cliente_atual and self.cliente_atual['observacoes'] is not None:
            self.txt_observacoes.insert('1.0', self.cliente_atual['observacoes'])
        
        # Frame para os botões de ação (abaixo dos campos)
        botoes_frame = tk.Frame(form_frame)
        botoes_frame.grid(row=10, column=0, columnspan=4, pady=(20, 10), sticky='w')
        
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
    
    def buscar_cep(self):
        """Busca endereço pelo CEP usando a API ViaCEP"""
        cep = self.entries['cep'].get().strip().replace('-', '').replace('.', '')
        
        if not cep or len(cep) != 8:
            messagebox.showwarning("Aviso", "Digite um CEP válido com 8 dígitos")
            return
            
        try:
            # Consulta a API ViaCEP
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)
            data = response.json()
            
            if "erro" in data:
                messagebox.showwarning("Aviso", "CEP não encontrado")
                return
                
            # Preenche os campos com os dados retornados
            if 'logradouro' in data and data['logradouro']:
                self.entries['endereco'].delete(0, tk.END)
                self.entries['endereco'].insert(0, data['logradouro'])
                
            if 'bairro' in data and data['bairro']:
                self.entries['bairro'].delete(0, tk.END)
                self.entries['bairro'].insert(0, data['bairro'])
                
            if 'localidade' in data and data['localidade']:
                self.entries['cidade'].delete(0, tk.END)
                self.entries['cidade'].insert(0, data['localidade'])
                
            if 'uf' in data and data['uf']:
                self.entries['uf'].delete(0, tk.END)
                self.entries['uf'].insert(0, data['uf'])
                
            # Foca no campo de número para continuar o preenchimento
            self.entries['numero'].focus_set()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao buscar CEP: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _salvar_cliente(self, cliente_id=None):
        """Salva os dados do cliente no banco de dados usando CadastroController"""
        # Coletar todos os campos do formulário
        dados = {
            'nome': self.entries['nome'].get().strip(),
            'data_nascimento': self.entries['data_nascimento'].get().strip(),
            'telefone': self.entries['telefone'].get().strip(),
            'telefone2': self.entries['telefone2'].get().strip(),
            'email': self.entries['email'].get().strip(),
            'endereco': self.entries['endereco'].get().strip(),
            'numero': self.entries['numero'].get().strip(),
            'complemento': self.entries['complemento'].get().strip(),
            'bairro': self.entries['bairro'].get().strip(),
            'cidade': self.entries['cidade'].get().strip(),
            'uf': self.entries['uf'].get().strip().upper(),
            'cep': self.entries['cep'].get().strip(),
            'ponto_referencia': self.entries['ponto_referencia'].get().strip(),
            'observacoes': self.txt_observacoes.get('1.0', 'end-1c').strip() if hasattr(self, 'txt_observacoes') else ''
        }
        
        # Validação básica
        if not dados['nome']:
            messagebox.showwarning("Aviso", "Nome do cliente é obrigatório")
            return
            
        if not dados['telefone']:
            messagebox.showwarning("Aviso", "Telefone do cliente é obrigatório")
            return
        
        try:
            # Usar o CadastroController para salvar os dados
            from src.controllers.cliente_controller import ClienteController
            cliente_controller = ClienteController()
            
            if cliente_id:
                # Edição - Passando cliente_id e o dicionário de dados
                sucesso, mensagem = cliente_controller.atualizar_cliente(cliente_id, dados)
                if not sucesso:
                    messagebox.showerror("Erro", f"Não foi possível atualizar o cliente: {mensagem}")
                    return
            else:
                # Novo - Passando os dados como argumentos nomeados (**dados)
                if not cliente_controller.cadastrar_cliente(**dados):
                    messagebox.showerror("Erro", "Não foi possível cadastrar o cliente")
                    return
            
            self.mostrar_clientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_clientes(self):
        """Mostra a tela de clientes usando a tabela clientes_delivery"""
        self.limpar_conteudo()
        try:
            # Usar o CadastroController para obter os clientes
            from src.controllers.cliente_controller import ClienteController
            cliente_controller = ClienteController()
            self.lista_clientes = cliente_controller.listar_clientes() 
            
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
                text="LISTA DE PACIENTES", 
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
                text="Novo Paciente",
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
            
            # Cabeçalho da tabela - Apenas as colunas solicitadas
            colunas = ("ID", "Nome", "Telefone", "Endereço", "Número", "Bairro")
            
            # Criando a Treeview
            style = ttk.Style()
            style.configure("Treeview", 
                background="#ffffff",
                foreground="#000000",  # Texto preto para melhor legibilidade
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
            self.tree_clientes.column('ID', width=40, anchor='center')
            self.tree_clientes.column('Nome', width=200)
            self.tree_clientes.column('Telefone', width=120)
            self.tree_clientes.column('Endereço', width=250)
            self.tree_clientes.column('Número', width=80, anchor='center')
            self.tree_clientes.column('Bairro', width=180)
            
            # Adicionando barra de rolagem
            scrollbar = ttk.Scrollbar(tabela_frame, orient='vertical', command=self.tree_clientes.yview)
            self.tree_clientes.configure(yscrollcommand=scrollbar.set)
            
            # Posicionando os widgets
            self.tree_clientes.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            # Preenchendo a tabela com os dados
            for cliente in self.lista_clientes:
                data_formatada = cliente['data_cadastro'].strftime('%d/%m/%Y') if cliente.get('data_cadastro') else ''
                self.tree_clientes.insert(
                    '', 'end', 
                    values=(
                        cliente.get('id', ''),
                        cliente.get('nome', ''),
                        cliente.get('telefone', ''),
                        cliente.get('endereco', ''),
                        cliente.get('numero', ''),
                        cliente.get('bairro', '')
                    )
                )
            
            # Configurar evento de seleção
            self.tree_clientes.bind('<<TreeviewSelect>>', self.atualizar_botoes_clientes)
            
            # Ajustando o layout
            self.conteudo_frame.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar clientes: {str(e)}")
            import traceback
            traceback.print_exc()
