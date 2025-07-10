"""
Módulo para edição de mesas do restaurante.
Permite adicionar, editar e remover mesas.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.views.modulos.base_module import BaseModule
from src.config.estilos import CORES, FONTES, ESTILOS_BOTAO, configurar_estilo_tabelas

class EditarMesasModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        """
        Inicializa o módulo de edição de mesas.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
            db_connection: Conexão com o banco de dados (opcional)
        """
        # Inicializa a classe base
        super().__init__(parent, controller)
        
        self.db_connection = db_connection
        
        # Inicializa a lista de mesas vazia
        self.mesas = []
        
        # Tenta carregar as mesas do banco de dados
        self.carregar_mesas_do_banco()
        
        # Configura a interface
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal com grid
        main_frame = tk.Frame(self.frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(
            title_frame, 
            text="GERENCIAMENTO DE MESAS", 
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
        
        # Botão Nova Mesa
        self.btn_nova_mesa = tk.Button(
            botoes_frame,
            text="+ Nova Mesa",
            **btn_style,
            command=self.adicionar_mesa
        )
        self.btn_nova_mesa.pack(pady=5, fill='x')
        
        # Botão Editar (inicialmente desabilitado)
        self.btn_editar_mesa = tk.Button(
            botoes_frame,
            text="✏️ Editar",
            **btn_style,
            state='disabled',
            command=self._editar_mesa_selecionada
        )
        self.btn_editar_mesa.pack(pady=5, fill='x')
        
        # Botão Excluir (inicialmente desabilitado)
        btn_excluir_style = btn_style.copy()
        btn_excluir_style['bg'] = '#f44336'  # Cor vermelha para o botão excluir
        self.btn_excluir_mesa = tk.Button(
            botoes_frame,
            text="🗑️ Excluir",
            **btn_excluir_style,
            state='disabled',
            command=self._excluir_mesa_selecionada
        )
        self.btn_excluir_mesa.pack(pady=5, fill='x')
        
        # Frame para a tabela (lado direito)
        tabela_container = tk.Frame(main_frame, bg='#d1d8e0')
        tabela_container.grid(row=1, column=1, sticky='nsew', padx=(5, 0))
        
        # Frame interno para a tabela
        tabela_frame = tk.Frame(tabela_container, bg='white', padx=1, pady=1)
        tabela_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Criar a tabela de mesas
        self.criar_tabela_mesas(tabela_frame)
    
    def criar_tabela_mesas(self, parent):
        """Cria a tabela com a lista de mesas"""
        # Cabeçalho da tabela
        colunas = ("id", "numero", "capacidade", "status")
        
        # Configurar o estilo padrão para tabelas
        style = configurar_estilo_tabelas()
        
        # Criar a tabela
        self.tree = ttk.Treeview(
            parent,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Treeview"
        )
        
        # Configurar as colunas
        self.tree.heading("id", text="ID", anchor="center")
        self.tree.heading("numero", text="Número", anchor="center")
        self.tree.heading("capacidade", text="Capacidade", anchor="center")
        self.tree.heading("status", text="Status", anchor="center")
        
        # Ajustar largura das colunas
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("numero", width=100, anchor="center")
        self.tree.column("capacidade", width=120, anchor="center")
        self.tree.column("status", width=150, anchor="center")
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empacotar a tabela e a barra de rolagem
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Sem cores de status para seguir o padrão da tabela de clientes
        
        # Adicionar evento de duplo clique para editar
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Adicionar evento de seleção para atualizar os botões
        self.tree.bind("<<TreeviewSelect>>", self._atualizar_botoes_mesas)
        
        # Adicionar menu de contexto
        self._criar_menu_contexto()
        
        # Preencher a tabela com os dados
        self.atualizar_tabela()
    
    def _criar_menu_contexto(self):
        """Cria o menu de contexto para ações na tabela"""
        self.menu_contexto = tk.Menu(self.tree, tearoff=0)
        self.menu_contexto.add_command(
            label="Editar Mesa",
            command=self._editar_mesa_selecionada
        )
        self.menu_contexto.add_command(
            label="Excluir Mesa",
            command=self._excluir_mesa_selecionada
        )
        
        # Vincular evento de botão direito do mouse
        self.tree.bind("<Button-3>", self._mostrar_menu_contexto)
    
    def _mostrar_menu_contexto(self, event):
        """Mostra o menu de contexto no local do clique"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu_contexto.post(event.x_root, event.y_root)
    
    def _on_double_click(self, event):
        """Trata o evento de duplo clique na tabela"""
        item = self.tree.identify_row(event.y)
        if item:
            self._editar_mesa_selecionada()
    
    def _editar_mesa_selecionada(self):
        """Obtém a mesa selecionada e chama o método de edição"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            mesa_id = self.tree.item(item, "values")[0]
            # Encontrar a mesa correspondente
            for mesa in self.mesas:
                if str(mesa["id"]) == mesa_id:
                    self.editar_mesa(mesa)
                    break
    
    def _excluir_mesa_selecionada(self):
        """Obtém a mesa selecionada e chama o método de confirmação de exclusão"""
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            mesa_id = self.tree.item(item, "values")[0]
            # Encontrar a mesa correspondente
            for mesa in self.mesas:
                if str(mesa["id"]) == mesa_id:
                    self.confirmar_exclusao(mesa)
                    break
                    
    def formatar_status(self, status):
        """Retorna o status formatado com a cor correspondente.
        
        Args:
            status (str): Status da mesa
            
        Returns:
            str: Status formatado
        """
        # Mapeamento de status para texto formatado
        status_map = {
            'livre': 'LIVRE',
            'ocupada': 'OCUPADA',
            'reservada': 'RESERVADA',
            'em manutencao': 'EM MANUTENÇÃO',
            'inativa': 'INATIVA'
        }
        return status_map.get(status.lower(), status.upper())
        
    def _atualizar_botoes_mesas(self, event=None):
        """Atualiza o estado dos botões com base na seleção"""
        selecionado = bool(self.tree.selection())
        state = 'normal' if selecionado else 'disabled'
        self.btn_editar_mesa.config(state=state)
        self.btn_excluir_mesa.config(state=state)
    
    def carregar_mesas_do_banco(self):
        """Carrega as mesas do banco de dados"""
        if not self.db_connection:
            messagebox.showerror("Erro", "Sem conexão com o banco de dados")
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, numero, capacidade, status 
                FROM mesas 
                ORDER BY numero
            """)
            self.mesas = cursor.fetchall()
            
            # Se não houver mesas, exibe mensagem
            if not self.mesas:
                messagebox.showinfo("Informação", "Nenhuma mesa cadastrada no sistema.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mesas: {str(e)}")
            self.mesas = []
    
    def atualizar_tabela(self):
        """Atualiza a tabela com os dados das mesas"""
        # Limpar a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Se não houver mesas, exibe mensagem
        if not self.mesas:
            self.tree.insert("", "end", values=("0", "Nenhuma mesa encontrada", "", ""))
            return
        
        # Adicionar as mesas à tabela
        for mesa in self.mesas:
            status = mesa.get('status', '').lower()
            self.tree.insert(
                "", "end",
                values=(
                    mesa.get('id', ''),
                    mesa.get('numero', ''),
                    mesa.get('capacidade', ''),
                    self.formatar_status(mesa.get('status', ''))
                )
            )
    
    def adicionar_mesa(self, event=None):
        """Abre o formulário para adicionar uma nova mesa"""
        self.abrir_formulario_mesa()
        
    def editar_mesa(self, mesa):
        """Abre o formulário para editar uma mesa existente"""
        self.abrir_formulario_mesa(mesa)
    
    def abrir_formulario_mesa(self, mesa=None):
        """Abre o formulário para adicionar ou editar uma mesa"""
        # Criar janela modal
        form_window = tk.Toplevel(self.parent)
        form_window.title("Nova Mesa" if not mesa else f"Editar Mesa {mesa['numero']}")
        form_window.transient(self.parent)  # Torna a janela dependente da janela principal
        form_window.grab_set()  # Torna a janela modal
        
        # Centralizar a janela
        window_width = 400
        window_height = 350
        screen_width = form_window.winfo_screenwidth()
        screen_height = form_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        form_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        form_window.resizable(False, False)
        form_window.configure(bg="#f0f2f5")
        
        # Frame principal
        main_frame = tk.Frame(form_window, bg="#f0f2f5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título em maiúsculas, igual ao módulo de clientes
        tk.Label(
            main_frame, 
            text="NOVA MESA" if not mesa else "EDITAR MESA",
            font=("Arial", 14, "bold"),
            bg="#f0f2f5"
        ).pack(pady=(0, 20))
        
        # Formulário
        form_frame = tk.Frame(main_frame, bg="#f0f2f5")
        form_frame.pack(fill="x", pady=5)
        
        # Campo Número da Mesa
        tk.Label(form_frame, text="Número da Mesa*", font=("Arial", 10), bg="#f0f2f5", anchor="w").pack(anchor="w")
        numero_var = tk.StringVar(value=mesa["numero"] if mesa else "")
        ttk.Entry(form_frame, textvariable=numero_var, font=("Arial", 11)).pack(fill="x", pady=(0, 15))
        
        # Campo Capacidade
        tk.Label(form_frame, text="Capacidade*", font=("Arial", 10), bg="#f0f2f5", anchor="w").pack(anchor="w")
        capacidade_var = tk.StringVar(value=str(mesa["capacidade"]) if mesa else "4")
        ttk.Spinbox(
            form_frame, 
            from_=1, 
            to=20, 
            textvariable=capacidade_var,
            font=("Arial", 11),
            width=5
        ).pack(anchor="w", pady=(0, 15))
        
        # Campo Status
        tk.Label(form_frame, text="Status*", font=("Arial", 10), bg="#f0f2f5", anchor="w").pack(anchor="w")
        status_var = tk.StringVar(value=mesa["status"] if mesa else "livre")
        status_combo = ttk.Combobox(
            form_frame,
            textvariable=status_var,
            values=["livre", "ocupada", "reservada", "inativa"],
            state="readonly",
            font=("Arial", 11)
        )
        status_combo.pack(fill="x", pady=(0, 15))
        
        # Frame para os botões - posicionado na parte inferior direita
        botoes_frame = tk.Frame(main_frame, bg="#f0f2f5")
        botoes_frame.pack(fill="x", pady=(20, 0), side="bottom")
        
        # Botão CANCELAR (vermelho, à direita)
        tk.Button(
            botoes_frame,
            text="CANCELAR",
            font=FONTES['pequena'],
            bg=CORES['alerta'],  # Vermelho do sistema
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            width=10,
            command=form_window.destroy
        ).pack(side="right", padx=5)
        
        # Botão SALVAR (verde, à direita do CANCELAR)
        tk.Button(
            botoes_frame,
            text="SALVAR",
            font=FONTES['pequena'],
            bg=CORES['sucesso'],  # Verde do sistema
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            width=10,
            command=lambda: self.salvar_mesa(
                mesa["id"] if mesa else None,
                numero_var.get(),
                int(capacidade_var.get()),
                status_var.get(),
                form_window
            )
        ).pack(side="right", padx=5)
    
    def salvar_mesa(self, mesa_id, numero, capacidade, status, janela):
        """Salva uma mesa nova ou existente no banco de dados"""
        # Validação básica
        if not numero.strip():
            messagebox.showerror("Erro", "O número da mesa é obrigatório!")
            return
        
        try:
            # Extrai apenas os números do campo de número da mesa
            numero_mesa = int(''.join(filter(str.isdigit, numero)))
            
            if capacidade <= 0:
                raise ValueError("A capacidade deve ser maior que zero")
                
            # Verificar se o número da mesa já existe (exceto na edição da mesma mesa)
            cursor = self.db_connection.cursor(dictionary=True)
            if mesa_id:  # Edição
                cursor.execute(
                    "SELECT id FROM mesas WHERE numero = %s AND id != %s", 
                    (numero_mesa, mesa_id)
                )
            else:  # Nova mesa
                cursor.execute(
                    "SELECT id FROM mesas WHERE numero = %s", 
                    (numero_mesa,)
                )
                
            if cursor.fetchone():
                messagebox.showerror("Erro", f"Já existe uma mesa com o número {numero_mesa}.")
                return
                
        except ValueError as e:
            messagebox.showerror("Erro", str(e) or "Valor inválido informado.")
            return
        
        # Salvar no banco de dados
        try:
            cursor = self.db_connection.cursor()
            
            if mesa_id:  # Atualizar mesa existente
                cursor.execute(
                    """
                    UPDATE mesas 
                    SET numero = %s, capacidade = %s, status = %s 
                    WHERE id = %s
                    """,
                    (numero_mesa, capacidade, status, mesa_id)
                )
                mensagem = "Mesa atualizada com sucesso!"
            else:  # Nova mesa
                cursor.execute(
                    """
                    INSERT INTO mesas (numero, capacidade, status)
                    VALUES (%s, %s, %s)
                    """,
                    (numero_mesa, capacidade, status)
                )
                mensagem = "Mesa adicionada com sucesso!"
            
            # Confirmar as alterações no banco de dados
            self.db_connection.commit()
            
            # Atualizar a lista de mesas
            self.carregar_mesas_do_banco()
            
            # Atualizar a tabela
            self.atualizar_tabela()
            
            # Fechar a janela do formulário
            janela.destroy()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", mensagem)
            
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Erro", f"Erro ao salvar mesa: {str(e)}")
    
    def confirmar_exclusao(self, mesa):
        """Confirma a exclusão de uma mesa"""
        if messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir a {mesa['numero']}?\n\n"
            "Esta ação não pode ser desfeita!"
        ):
            self.excluir_mesa(mesa)
    
    def excluir_mesa(self, mesa):
        """Exclui uma mesa do banco de dados"""
        try:
            # Executar o comando SQL para excluir a mesa do banco de dados
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM mesas WHERE id = %s", (mesa["id"],))
            
            # Confirmar a exclusão no banco de dados
            self.db_connection.commit()
            
            # Remover da lista local em memória
            self.mesas = [m for m in self.mesas if m["id"] != mesa["id"]]
            
            # Exibir mensagem de sucesso
            messagebox.showinfo("Sucesso", f"Mesa {mesa['numero']} excluída com sucesso!")
            
            # Atualizar a tabela
            self.atualizar_tabela()
            
        except Exception as e:
            # Em caso de erro, reverter as alterações e mostrar mensagem
            self.db_connection.rollback()
            messagebox.showerror("Erro", f"Erro ao excluir mesa: {str(e)}")
            
            # Recarregar as mesas do banco de dados
            self.carregar_mesas_do_banco()
            self.atualizar_tabela()
    
    def centralizar_janela(self, janela, largura, altura):
        """Centraliza uma janela na tela"""
        # Obter as dimensões da tela
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        
        # Calcular a posição
        x = (largura_tela - largura) // 2
        y = (altura_tela - altura) // 2
        
        # Definir a posição da janela
        janela.geometry(f"{largura}x{altura}+{x}+{y}")
    
    def show(self):
        """Mostra o módulo"""
        self.frame.pack(fill="both", expand=True)
        return self.frame
