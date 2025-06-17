"""
Módulo de Cadastro - Gerencia cadastros do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo de banco de dados
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from db.cadastro_db import CadastroDB
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
            if self.db:
                self.dados_empresa = self.db.obter_empresa()
                # Aqui você pode adicionar os widgets para exibir/editar os dados da empresa
                tk.Label(self.conteudo_frame, text="Dados da Empresa", font=('Arial', 14, 'bold')).pack(pady=10)
                # Adicione mais widgets conforme necessário
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados da empresa: {str(e)}")
    
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
            main_frame.columnconfigure(0, weight=1)
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
                foreground='white',
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
            command=self.janela_novo_usuario.destroy,
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
                # Implementar a lógica para excluir o usuário
                # self.db.excluir_usuario(usuario_id)
                self.tree_usuarios.delete(selecionado[0])
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_funcionarios(self):
        """Mostra a tela de cadastro de funcionários"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_funcionarios = self.db.listar_funcionarios()
                tk.Label(self.conteudo_frame, text="Lista de Funcionários", font=('Arial', 14, 'bold')).pack(pady=10)
                # Adicione a tabela ou lista de funcionários aqui
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar funcionários: {str(e)}")
    
    def mostrar_clientes(self):
        """Mostra a tela de cadastro de clientes"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_clientes = self.db.listar_clientes()
                tk.Label(self.conteudo_frame, text="Lista de Clientes", font=('Arial', 14, 'bold')).pack(pady=10)
                # Adicione a tabela ou lista de clientes aqui
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar clientes: {str(e)}")
    
    def mostrar_produtos(self):
        """Mostra a tela de cadastro de produtos"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_produtos = self.db.listar_produtos()
                tk.Label(self.conteudo_frame, text="Lista de Produtos", font=('Arial', 14, 'bold')).pack(pady=10)
                # Adicione a tabela ou lista de produtos aqui
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar produtos: {str(e)}")
    
    def mostrar_fornecedores(self):
        """Mostra a tela de cadastro de fornecedores"""
        self.limpar_conteudo()
        try:
            if self.db:
                self.lista_fornecedores = self.db.listar_fornecedores()
                tk.Label(self.conteudo_frame, text="Lista de Fornecedores", font=('Arial', 14, 'bold')).pack(pady=10)
                # Adicione a tabela ou lista de fornecedores aqui
            else:
                messagebox.showwarning("Aviso", "Conexão com o banco de dados não disponível")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar fornecedores: {str(e)}")
            
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
        
    def carregar_tema(self):
        """Carrega as configurações de tema do controlador principal"""
        if hasattr(self.controller, 'cores'):
            self.cores = self.controller.cores
        else:
            # Cores padrão caso o controlador não tenha as cores definidas
            self.cores = {
                'fundo': '#f0f2f5',
                'fundo_conteudo': '#ffffff',
                'primaria': '#4a6fa5',
                'secundaria': '#28b5f4',
                'terciaria': '#333f50',
                'texto': '#333333',
                'texto_claro': '#ffffff',
                'destaque': '#4caf50',
                'alerta': '#f44336',
                'borda': '#e0e0e0'
            }
    
    def atualizar_tema(self, event=None):
        """Atualiza as cores da interface quando o tema é alterado"""
        self.carregar_tema()
        
        # Atualiza as cores do frame principal
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self.frame.config(style='TFrame')
            
        # Atualiza a view atual se existir
        if hasattr(self, 'current_view') and self.current_view and self.current_view.winfo_exists():
            self._aplicar_tema_view(self.current_view)
    
    def _aplicar_tema_view(self, frame):
        """Aplica o tema a todos os widgets de um frame"""
        try:
            # Configura o estilo do frame
            if isinstance(frame, (tk.Frame, ttk.Frame)):
                frame.config(style='TFrame')
                
            # Itera por todos os widgets do frame
            for widget in frame.winfo_children():
                if isinstance(widget, (tk.Frame, ttk.Frame)):
                    widget.config(style='TFrame')
                    self._aplicar_tema_view(widget)
                elif isinstance(widget, ttk.Label):
                    widget.config(style='TLabel')
                elif isinstance(widget, ttk.Button):
                    widget.config(style='TButton')
                elif isinstance(widget, ttk.Entry):
                    widget.config(style='TEntry')
                elif isinstance(widget, ttk.Combobox):
                    widget.config(style='TCombobox')
                # Adicione outros tipos de widgets conforme necessário
                
        except Exception as e:
            # Ignora erros de widgets que não podem ser estilizados
            pass
        

        
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
        if not self.dados_empresa or not hasattr(self, 'campos_empresa'):
            return
            
        for campo, entry in self.campos_empresa.items():
            try:
                if campo in self.dados_empresa and self.dados_empresa[campo] is not None:
                    valor = str(self.dados_empresa[campo])
                    if isinstance(entry, tk.Text):
                        entry.delete('1.0', tk.END)
                        entry.insert('1.0', valor)
                    else:
                        entry.delete(0, tk.END)
                        entry.insert(0, valor)
            except Exception as e:
                print(f"Erro ao preencher campo {campo}: {str(e)}")
    
    def salvar_empresa(self):
        """Salva os dados da empresa"""
        try:
            # Coleta os dados dos campos
            dados = {}
            for campo, entry in self.campos_empresa.items():
                if isinstance(entry, tk.Text):
                    dados[campo] = entry.get('1.0', 'end-1c').strip()
                else:
                    dados[campo] = entry.get().strip()
            
            # Validação dos campos obrigatórios
            if not dados.get('nome_fantasia'):
                messagebox.showwarning("Aviso", "O campo Nome Fantasia é obrigatório.")
                return
                
            if not dados.get('cnpj'):
                messagebox.showwarning("Aviso", "O campo CNPJ é obrigatório.")
                return
                
            # Remove caracteres não numéricos do CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, dados['cnpj']))
            if len(cnpj_limpo) != 14:
                messagebox.showwarning("Aviso", "CNPJ inválido. Deve conter 14 dígitos.")
                return
            
            # Formata o CNPJ
            dados['cnpj'] = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
            
            # Salva os dados no banco
            sucesso, mensagem = self.db.salvar_empresa(dados)
            
            if sucesso:
                # Atualiza os dados em memória
                self.dados_empresa = self.db.obter_empresa() or {}
                messagebox.showinfo("Sucesso", mensagem)
                # Volta para a tela inicial do módulo
                self.mostrar_inicio()
            else:
                messagebox.showerror("Erro", mensagem)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar os dados: {str(e)}")
    
    def cancelar_edicao(self):
        """Cancela a edição e volta para a tela inicial do módulo"""
        self.mostrar_inicio()
