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
from src.views.modulos.cadastro.horario_disponivel_module import HorarioDisponivelModule

# Importar configurações de estilo
from config.estilos import CORES, FONTES, aplicar_estilo

# Adicione o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Importações locais
from src.controllers.cadastro_controller import CadastroController
from ..base_module import BaseModule
from src.views.modulos.cadastro.modelo_prontuario_module import ModeloProntuarioModule



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
            "pacientes": self.mostrar_pacientes,
            "modelos": self.mostrar_tela_modelo,
            "receitas": self.mostrar_tela_receitas,
            "exames_consultas": self.mostrar_tela_exames_consultas,
            "horario_medico": self.horario_medico,
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

        # Badge de status do caixa abaixo da frase
        try:
            self.create_caixa_status_badge(self.conteudo_frame, pady=(0, 0))
        except Exception:
            pass
    
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
                    values=['medico', 'funcionario'],
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
            if nivel not in ['funcionario', 'medico']:
                messagebox.showwarning("Aviso", "Selecione um nível de acesso válido (funcionario ou medico)")
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
        entry_nome.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        self.entries = {'nome': entry_nome}
        
        # CRM
        tk.Label(form_frame, text="CRM:").grid(row=1, column=0, sticky='e', padx=10, pady=5)
        entry_crm = tk.Entry(form_frame, width=20)
        entry_crm.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        entry_crm.bind('<KeyRelease>', format_crm)
        self.entries['crm'] = entry_crm
        
        # Especialidade
        tk.Label(form_frame, text="Especialidade:").grid(row=2, column=0, sticky='e', padx=10, pady=5)
        entry_especialidade = tk.Entry(form_frame, width=40)
        entry_especialidade.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        self.entries['especialidade'] = entry_especialidade
        
        # Telefone
        tk.Label(form_frame, text="Telefone:").grid(row=3, column=0, sticky='e', padx=10, pady=5)
        entry_telefone = tk.Entry(form_frame, width=20)
        entry_telefone.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        entry_telefone.bind('<KeyRelease>', format_telefone)
        self.entries['telefone'] = entry_telefone
        
        # E-mail
        tk.Label(form_frame, text="E-mail:").grid(row=4, column=0, sticky='e', padx=10, pady=5)
        entry_email = tk.Entry(form_frame, width=40)
        entry_email.grid(row=4, column=1, sticky='w', padx=10, pady=5)
        self.entries['email'] = entry_email

        # Usuário (dono do CRM)
        try:
            from tkinter import ttk
        except Exception:
            ttk = None
        tk.Label(form_frame, text="Usuário (dono do CRM):").grid(row=5, column=0, sticky='e', padx=10, pady=5)
        if ttk is not None and self.db:
            try:
                usuarios = self.db.listar_usuarios() or []
            except Exception:
                usuarios = []
            # Monta opções de exibição "login - nome" para evitar ambiguidade
            display_list = []
            display_to_id = {}
            for u in usuarios:
                login = str(u.get('login') or '').strip()
                nome_u = str(u.get('nome') or '').strip()
                uid = u.get('id')
                display = f"{login} - {nome_u}" if login else nome_u
                display_list.append(display)
                display_to_id[display] = uid
            self._usuarios_display_to_id = display_to_id
            combo_usuario = ttk.Combobox(form_frame, values=display_list, state='readonly', width=37)
            combo_usuario.grid(row=5, column=1, sticky='w', padx=10, pady=5)
            self.entries['usuario_display'] = combo_usuario
            # Pré-seleção quando em edição
            try:
                if self.medico_atual and self.medico_atual.get('usuario_id'):
                    alvo_id = self.medico_atual.get('usuario_id')
                    for disp, uid in display_to_id.items():
                        if uid == alvo_id:
                            combo_usuario.set(disp)
                            break
            except Exception:
                pass
        else:
            # Fallback sem ttk: apenas um campo de ID numérico
            entry_usuario_id = tk.Entry(form_frame, width=20)
            entry_usuario_id.grid(row=5, column=1, sticky='w', padx=10, pady=5)
            self.entries['usuario_id'] = entry_usuario_id
        
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
        # Linha 6 para não conflitar com o combobox de usuário (linha 5)
        botoes_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
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
            # Usuário alvo (dono do CRM)
            usuario_id = None
            if 'usuario_display' in self.entries:
                display = self.entries['usuario_display'].get().strip()
                usuario_id = (getattr(self, '_usuarios_display_to_id', {}) or {}).get(display)
            elif 'usuario_id' in self.entries:
                try:
                    usuario_id = int(self.entries['usuario_id'].get().strip())
                except Exception:
                    usuario_id = None
            
            # Verificação básica de campos obrigatórios (Nome, CRM, Telefone, Usuário)
            faltando = []
            if not nome:
                faltando.append("Nome")
            if not crm:
                faltando.append("CRM")
            if not telefone:
                faltando.append("Telefone")
            if not usuario_id:
                faltando.append("Usuário (dono do CRM)")
            if faltando:
                msg = "Preencha os campos obrigatórios: " + ", ".join(faltando)
                messagebox.showwarning("Atenção", msg)
                return
                
            # Prepara os dados para salvar
            dados = {
                'nome': nome,
                'crm': crm,
                'especialidade': especialidade,
                'telefone': telefone,
                'email': email,
                'usuario_id': usuario_id
            }
            
            # Adiciona o ID se for uma atualização
            if funcionario_id:
                dados['id'] = funcionario_id
            
            # Salva no banco de dados
            if self.db:
                try:
                    if funcionario_id:
                        # Atualiza médico existente
                        ok, msg, _ = self.db.salvar_medico(dados)
                        if ok:
                            messagebox.showinfo("Sucesso", msg)
                            self.mostrar_medicos()
                        else:
                            messagebox.showerror("Erro", msg)
                    else:
                        # Insere novo médico
                        ok, msg, novo_id = self.db.salvar_medico(dados)
                        if ok:
                            messagebox.showinfo("Sucesso", msg)
                            self.mostrar_medicos()
                        else:
                            messagebox.showerror("Erro", msg)
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
            {"nome": "👤 Pacientes", "comando": self.mostrar_pacientes},
            {"nome": "📝 Modelos", "comando": self.mostrar_tela_modelo},
            {"nome": "📜 Receitas", "comando": self.mostrar_tela_receitas},
            {"nome": "⏳ Exames & Consultas", "comando": self.mostrar_tela_exames_consultas},
            {"nome": "📅 Horários", "comando": self.horario_medico},
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
        elif acao == 'pacientes':
            self.mostrar_pacientes()
        elif acao == 'modelos':
            self.mostrar_tela_modelo()
        elif acao == 'receitas':
            self.mostrar_tela_receitas()
        elif acao == 'exames_consultas':
            self.mostrar_tela_exames_consultas()
        elif acao == 'horario_medico':
            self.horario_medico()
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
                self.mostrar_pacientes()
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
        # Corretor ortográfico (opcional)
        try:
            self._enable_spellcheck(self.txt_observacoes)
        except Exception:
            pass
        
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
            command=self.mostrar_pacientes,
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
            
            self.mostrar_pacientes()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_pacientes(self):
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

    def mostrar_tela_receitas(self):
        """Mostra a tela de gerenciamento de receitas médicas."""
        # Limpa o frame de conteúdo

        self.nome_receita_var = tk.StringVar()

        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
       
        # Frame principal
        main_frame = ttk.Frame(self.conteudo_frame, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            titulo_frame,
            text="Receitas Médicas",
            font=('Arial', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        # Frame de filtros
        filtros_frame = ttk.LabelFrame(main_frame, text="Filtros", padding=10)
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
 
        # Seletor de médico
        ttk.Label(filtros_frame, text="Médico:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.medico_var = tk.StringVar()
        self.medico_cb = ttk.Combobox(
            filtros_frame,
            textvariable=self.medico_var,
            state='readonly',
            width=50
        )
        self.medico_cb.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.medico_cb.bind('<<ComboboxSelected>>', lambda e: self._carregar_receitas())
     
        
        # Frame principal (lista + visualização)
        conteudo_frame = ttk.Frame(main_frame)
        conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame da lista de receitas
        lista_frame = ttk.LabelFrame(conteudo_frame, text="Receitas", padding=10)
        lista_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Botões de ação
        botoes_frame = ttk.Frame(lista_frame)
        botoes_frame.pack(fill=tk.X, pady=(0, 10))
    
        # Botão Novo
        self.btn_novo = tk.Button(
            botoes_frame,
            text="Novo",
            command=self._criar_receita,
            bg="#4CAF50",  # Verde
            fg="white",
            bd=0,
            padx=10,
            pady=5
        )
        self.btn_novo.pack(side=tk.LEFT, padx=2)
        
        # Botão Editar
        self.btn_editar = tk.Button(
            botoes_frame,
            text="Editar",
            command=self._editar_receita,
            bg="#4a6fa5",  # Azul
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_editar.pack(side=tk.LEFT, padx=2)
        
        # Botão Excluir
        self.btn_excluir = tk.Button(
            botoes_frame,
            text="Excluir",
            command=self._excluir_receita,
            bg="#f44336",  # Vermelho
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_excluir.pack(side=tk.LEFT, padx=2)
        
        # Lista de receitas
        self.lista_receitas = ttk.Treeview(
            lista_frame,
            columns=('id', 'nome', 'data_criacao'),
            show='headings',
            selectmode='browse',
            height=15
        )
        self.lista_receitas.heading('id', text='ID')
        self.lista_receitas.heading('nome', text='Nome')
        self.lista_receitas.heading('data_criacao', text='Data de Criação')
        
        # Configuração das colunas
        self.lista_receitas.column('id', width=50, anchor='center')
        self.lista_receitas.column('nome', width=200)
        self.lista_receitas.column('data_criacao', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            lista_frame,
            orient=tk.VERTICAL,
            command=self.lista_receitas.yview
        )
        self.lista_receitas.configure(yscrollcommand=scrollbar.set)
        
        # Empacota a lista e a scrollbar
        self.lista_receitas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de visualização
        vis_frame = ttk.LabelFrame(conteudo_frame, text="Visualização", padding=10)
        vis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
   
        
        # Nome da receita
        ttk.Label(vis_frame, text="Nome:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.nome_receita_var = tk.StringVar()
        self.entry_nome = ttk.Entry(vis_frame, textvariable=self.nome_receita_var, state='readonly')
        self.entry_nome.pack(fill=tk.X, pady=(0, 10))
      
        
        # Texto da receita
        ttk.Label(vis_frame, text="Receita:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        # Barra rápida para fonte (6-8) - insere/atualiza <<font:N>> na 1ª linha do texto
        def _aplicar_fonte_receita(n: int):
            try:
                txt = getattr(self, 'texto_receita', None)
                if not txt:
                    return
                conteudo = txt.get('1.0', 'end-1c')
                linhas = conteudo.splitlines()
                nova_dir = f"<<font:{n}>>"
                if not linhas:
                    txt.insert('1.0', nova_dir + "\n")
                    return
                primeira = linhas[0].strip()
                if primeira.lower().startswith('<<font:') and primeira.endswith('>>'):
                    linhas[0] = nova_dir
                    novo = "\n".join(linhas)
                    txt.delete('1.0', tk.END)
                    txt.insert('1.0', novo)
                else:
                    txt.insert('1.0', nova_dir + "\n")
                # Ajusta a fonte na tela para pré-visualização imediata
                try:
                    tam = max(6, min(12, int(n)))
                    txt.configure(font=('Arial', tam))
                except Exception:
                    pass
            except Exception:
                pass
        fonte_bar = tk.Frame(vis_frame, bg='#ffffff')
        fonte_bar.pack(fill=tk.X, pady=(0, 6))
        tk.Label(fonte_bar, text="Fonte:", bg='#ffffff', fg='#333333', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 6))
        for n in (6, 7, 8):
            tk.Button(fonte_bar, text=str(n), bg="#495057", fg="white", relief=tk.FLAT, cursor='hand2',
                      command=lambda v=n: _aplicar_fonte_receita(v)).pack(side=tk.LEFT, padx=2)

        # Frame para o texto com barra de rolagem
        text_frame = ttk.Frame(vis_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Barra de rolagem vertical
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Widget Text
        self.texto_receita = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            yscrollcommand=scrollbar.set
        )
        self.texto_receita.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Corretor ortográfico (opcional)
        try:
            self._enable_spellcheck(self.texto_receita)
        except Exception:
            pass

        # Configurar a scrollbar
        scrollbar.config(command=self.texto_receita.yview)

        # Frame de botões de ação
        botoes_acao_frame = ttk.Frame(vis_frame)
        botoes_acao_frame.pack(fill=tk.X, pady=(10, 0))
        
                
        # Frame de botões de ação
        botoes_acao_frame = ttk.Frame(vis_frame)
        botoes_acao_frame.pack(fill=tk.X, pady=(10, 0))
   
        
        # Botão Salvar
        self.btn_salvar = tk.Button(
            botoes_acao_frame,
            text="Salvar",
            command=self._salvar_receita,
            bg="#4CAF50",  # Verde
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_salvar.pack(side=tk.RIGHT, padx=5)
     
        
        # Configura o bind da lista de receitas
        self.lista_receitas.bind('<<TreeviewSelect>>', self._on_select_receita)
    
        
        # Chama carregar medicos
    
        self._carregar_medicos_receitas()
    
    def _carregar_medicos_receitas(self):
        """Carrega a lista de médicos no combobox de receitas."""
        try:
            
            
            # Inicializa o dicionário de médicos
            self.medicos_receita_dict = {}
            
            # Limpa o combobox
            if hasattr(self, 'medico_cb'):
                self.medico_cb.set('')  # Limpa a seleção atual
                self.medico_cb['values'] = []
            
            # Obtém a lista de médicos do banco de dados
            medicos = self.db.listar_medicos()
            
            
            if not medicos:
                print("Nenhum médico encontrado no banco de dados")
                messagebox.showwarning("Aviso", "Nenhum médico cadastrado.")
                return []
                    
            # Preenche o dicionário e a lista de valores
            valores = []
       
            for i, medico in enumerate(medicos, 1):
                medico_id = medico.get('id')
                medico_nome = medico.get('nome')
                if medico_id and medico_nome:
             
                    self.medicos_receita_dict[medico_nome] = medico_id
                    valores.append(medico_nome)
            
          
            
            # Atualiza o combobox sem selecionar nenhum item
            if hasattr(self, 'medico_cb'):
                self.medico_cb['values'] = valores
                # Não seleciona nenhum médico por padrão
                self.medico_cb.set('Selecione um médico...')
                
            return valores
                
        except Exception as e:
            print(f"Erro ao carregar médicos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao carregar lista de médicos: {str(e)}")
            return []

    def listar_receitas(self):
        """Lista as receitas cadastradas."""
        # Limpa a lista atual
        for widget in self.lista_receitas_frame.winfo_children():
            widget.destroy()
        
        # Obtém as receitas do banco de dados
        receitas = self.db.listar_receitas_por_medico(1)  # Substitua 1 pelo ID do médico logado
        
        if not receitas:
            tk.Label(
                self.lista_receitas_frame,
                text="Nenhuma receita cadastrada.",
                bg='#f0f2f5'
            ).pack(pady=20)
            return
        
        # Cabeçalho
        cabecalho = tk.Frame(self.lista_receitas_frame, bg='#e1e5eb')
        cabecalho.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            cabecalho, text="Nome", width=40, bg='#e1e5eb', font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5, pady=5)
        
        tk.Label(
            cabecalho, text="Data", width=20, bg='#e1e5eb', font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5, pady=5)
        
        # Lista de receitas
        for receita in receitas:
            frame = tk.Frame(self.lista_receitas_frame, bg='white', bd=1, relief='solid')
            frame.pack(fill='x', pady=2)
            
            # Nome da receita
            tk.Label(
                frame, 
                text=receita['nome'], 
                bg='white',
                width=40,
                anchor='w'
            ).pack(side='left', padx=5, pady=5)
            
            # Data de criação
            data_formatada = receita['criado_em'].strftime('%d/%m/%Y %H:%M')
            tk.Label(
                frame, 
                text=data_formatada, 
                bg='white',
                width=20
            ).pack(side='left', padx=5, pady=5)
            
            # Botão de visualizar
            btn_visualizar = ttk.Button(
                frame,
                text="Visualizar",
                command=lambda r=receita: self.visualizar_receita(r['id'])
            )
            btn_visualizar.pack(side='right', padx=5)

    def _criar_receita(self):
        """Prepara a interface para criar uma nova receita."""
        self.modo_edicao = 'novo'
        self.receita_atual = None
        
        # Habilita os campos para edição
        self.entry_nome.config(state='normal')
        self.texto_receita.config(state='normal')
        
        # Limpa os campos
        self.nome_receita_var.set('')
        self.texto_receita.delete(1.0, tk.END)
        
        # Habilita/desabilita botões
        self.btn_novo.config(state=tk.DISABLED)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.NORMAL)
        
        # Foca no campo de nome
        self.entry_nome.focus_set()

    def _editar_receita(self):
        """Prepara a interface para editar a receita selecionada."""
        selecionado = self.lista_receitas.selection()
        if not selecionado:
            return
            
        self.modo_edicao = 'editar'
        
        # Habilita os campos para edição
        self.entry_nome.config(state='normal')
        self.texto_receita.config(state='normal')
        # Força checagem do corretor ao entrar em modo de edição
        try:
            self._spellcheck_now(self.texto_receita)
        except Exception:
            pass
        
        # Habilita/desabilita botões
        self.btn_novo.config(state=tk.DISABLED)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.NORMAL)
        
        # Foca no campo de nome
        self.entry_nome.focus_set()

    def _salvar_receita(self):
        """Salva uma receita no banco de dados."""
        try:
      
            
            # Obtém os dados do formulário
            medico_nome = self.medico_cb.get()
            nome = self.nome_receita_var.get().strip()
            texto = self.texto_receita.get("1.0", tk.END).strip()
            
            # Validação básica
            if not medico_nome or not nome or not texto:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
                return
                
            # Obtém o ID do médico
            if not hasattr(self, 'medicos_receita_dict') or not self.medicos_receita_dict:
             
                if not self._carregar_medicos_receitas():
                    messagebox.showerror("Erro", "Não foi possível carregar os médicos.")
                    return
                    
            medico_id = self.medicos_receita_dict.get(medico_nome)
            if not medico_id:
                messagebox.showerror("Erro", "Médico não encontrado.")
                return
            
            # Verifica se é uma nova receita ou atualização
            if hasattr(self, 'receita_atual') and self.receita_atual:
                # Atualização de receita existente
                receita_id = self.receita_atual['id']
    
                
                # Prepara os dados para atualização
                dados_atualizacao = {
                    'nome': nome,
                    'texto': texto,
                    'medico_id': medico_id
                }
                
                # Remove campos vazios
                dados_atualizacao = {k: v for k, v in dados_atualizacao.items() if v is not None}
                
                # Chama o método de atualização
                if self.db.atualizar_receita(receita_id, dados_atualizacao):
    
                    messagebox.showinfo("Sucesso", "Receita atualizada com sucesso!")
                else:
                    raise Exception("Falha ao atualizar a receita no banco de dados")
            else:
              
                
                # Chama o método de criação do banco de dados
                receita_id = self.db.criar_receita(medico_id, nome, texto)
                
                if receita_id:
                  
                    messagebox.showinfo("Sucesso", "Receita criada com sucesso!")
                else:
                    raise Exception("Falha ao criar a receita no banco de dados")
            
            # Atualiza a lista de receitas
            self._carregar_receitas()
            
            # Limpa os campos
            self._limpar_campos()
            
        except Exception as e:
            print(f"Erro ao salvar receita: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao salvar receita: {str(e)}")
    
    def _excluir_receita(self):
        """Exclui a receita selecionada."""
        selecionado = self.lista_receitas.selection()
        if not selecionado:
            return
            
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta receita?"):
            return
            
        try:
            receita_id = self.lista_receitas.item(selecionado[0])['values'][0]
            
            if self.db.excluir_receita(receita_id):
                messagebox.showinfo("Sucesso", "Receita excluída com sucesso!")
                self._carregar_receitas()
                self._limpar_campos()
            else:
                messagebox.showerror("Erro", "Não foi possível excluir a receita.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir receita: {str(e)}")

    def _limpar_campos(self):
        """Limpa todos os campos do formulário."""
        self.nome_receita_var.set('')
        self.texto_receita.config(state='normal')
        self.texto_receita.delete(1.0, tk.END)
        self.texto_receita.config(state='disabled')
        
        # Desabilita os campos
        self.entry_nome.config(state='readonly')
        
        # Reseta os botões
        self.btn_novo.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.DISABLED)
        
        # Remove a seleção da lista
        for item in self.lista_receitas.selection():
            self.lista_receitas.selection_remove(item)

    def _on_select_receita(self, event):
        """Chamado quando uma receita é selecionada na lista."""
        selecionado = self.lista_receitas.selection()
        
        if selecionado:
            # Habilita os botões de editar e excluir
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)
            
            # Carrega os dados da receita selecionada
            receita_id = self.lista_receitas.item(selecionado[0])['values'][0]
            receita = self.db.obter_receita_por_id(receita_id)
            
            if receita:
                self.receita_atual = receita
                self.nome_receita_var.set(receita['nome'])
                
                self.texto_receita.config(state='normal')
                self.texto_receita.delete(1.0, tk.END)
                self.texto_receita.insert(tk.END, receita['texto'])
                # Força checagem do corretor após carregar o texto
                try:
                    self._spellcheck_now(self.texto_receita)
                except Exception:
                    pass
                self.texto_receita.config(state='disabled')
        else:
            self._limpar_campos()

    def _carregar_receitas(self, event=None):
        """Carrega as receitas do médico selecionado."""
        try:
            # Verifica se o dicionário de médicos está carregado
            if not hasattr(self, 'medicos_receita_dict') or not self.medicos_receita_dict:
                if not self._carregar_medicos_receitas():
                    return
                        
            # Obtém o médico selecionado
            medico_nome = self.medico_cb.get()
            if not medico_nome:
              
                return
                
            # Obtém o ID do médico
            medico_id = self.medicos_receita_dict.get(medico_nome)
            if not medico_id:
             
                return
                
         
            # Limpa a lista atual
            for item in self.lista_receitas.get_children():
                self.lista_receitas.delete(item)
            
            # Obtém as receitas do banco de dados
            receitas = self.db.listar_receitas_por_medico(medico_id)
      
            
            # Preenche a lista de receitas
            for i, receita in enumerate(receitas, 1):
                try:
                    # Formata os dados
                    receita_id = receita.get('id', '')
                    nome = receita.get('nome', 'Sem nome')
                    data = receita.get('data', '')
                    
                    # Formata a data se existir
                    data_formatada = data.strftime('%d/%m/%Y %H:%M') if data else 'Data não informada'
                    
                   
                    
                    # Adiciona à lista
                    self.lista_receitas.insert('', 'end', values=(
                        receita_id,
                        nome,
                        data_formatada
                    ))
                    
                except Exception as e:
                    print(f"Erro ao processar receita {i}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
           
                    
        except Exception as e:
            print(f"\n!!! ERRO EM _carregar_receitas: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao carregar receitas: {str(e)}")

    def mostrar_tela_exames_consultas(self):
        """Mostra a tela de gerenciamento de exames e consultas"""
        self.limpar_conteudo()
        
        try:
            # Importa o módulo de exames e consultas
            from .exames_consultas_module import ExamesConsultasModule
            
            # Cria uma instância do módulo de exames e consultas
            exames_consultas_module = ExamesConsultasModule(
                parent=self.conteudo_frame,
                controller=self.db,
                db=self.db
            )
            
            # Empacota o frame para preencher o espaço disponível
            exames_consultas_module.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a tela de exames e consultas: {str(e)}")
            print(f"Erro ao carregar exames e consultas: {str(e)}")
            
    def mostrar_tela_modelo(self):
        """Mostra a tela de gerenciamento de modelos de prontuário"""
        self.limpar_conteudo()
        
        try:
            # Cria uma instância do módulo de modelos
            modelo_module = ModeloProntuarioModule(
                parent=self.conteudo_frame,
                controller=self.controller,
                db_connection=self.db.db if self.db else None
            )
            
            # Empacota o frame do módulo para preencher o espaço disponível
            modelo_module.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Armazena a referência para evitar coleta de lixo
            self.modelo_module = modelo_module
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Não foi possível carregar a tela de modelos: {str(e)}")

    def horario_medico(self):
        """Mostra a tela de gerenciamento de horários dos médicos"""
        self.limpar_conteudo()
        
        try:
            # Cria uma instância do módulo de horários
            horario_module = HorarioDisponivelModule(
                parent=self.conteudo_frame,
                db_connection=self.db.db if hasattr(self.db, 'db') else None
            )
            
            # Empacota o frame do módulo para preencher o espaço disponível
            horario_module.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Armazena a referência para evitar coleta de lixo
            self.horario_module = horario_module
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Não foi possível carregar a tela de horários: {str(e)}")