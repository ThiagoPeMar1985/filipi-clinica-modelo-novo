import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class ConfiguracaoModule:
    def _criar_campo(self, frame, label_text, row, value='', width=30):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky='w', pady=2, padx=5)
        entry = ttk.Entry(frame, width=width)
        entry.insert(0, value)
        entry.grid(row=row, column=1, sticky='ew', pady=2, padx=5)
        return entry
        
    def _criar_combobox(self, frame, label_text, row, values, value, width=30):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky='w', pady=2, padx=5)
        combo = ttk.Combobox(frame, values=values, width=width-2)
        combo.set(value)
        combo.grid(row=row, column=1, sticky='ew', pady=2, padx=5)
        return combo
        
    def _criar_botao(self, frame, text, command, row, column=1):
        btn = ttk.Button(frame, text=text, command=command)
        btn.grid(row=row, column=column, pady=5, sticky='e')
        return btn
    
    def _selecionar_arquivo(self, entry):
        filename = filedialog.askopenfilename()
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)
    
    def _selecionar_pasta(self, entry):
        folder = filedialog.askdirectory()
        if folder:
            entry.delete(0, tk.END)
    
    def __init__(self, parent, controller):
        """Inicializa o módulo de configuração."""
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        
        # Inicializa o controlador de configuração
        from src.controllers.config_controller import ConfigController
        self.ctrl = ConfigController(self)
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "NF-e", "acao": "nfe"},
            {"nome": "Backup", "acao": "backup"},
            {"nome": "Tema", "acao": "tema"},
            {"nome": "Impressoras", "acao": "impressoras"},
            {"nome": "Banco de Dados", "acao": "banco_dados"},
            {"nome": "Integrações", "acao": "integracoes"},
            {"nome": "Segurança", "acao": "seguranca"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        # Limpa a view atual
        if hasattr(self, 'current_view') and self.current_view:
            try:
                self.current_view.destroy()
            except tk.TclError:
                pass  # Ignora erros de widget já destruído
        
        # Garante que self.frame existe e está configurado corretamente
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Cria a view solicitada ou a view padrão
        if acao == 'nfe':
            self._show_nfe()
        elif acao == 'backup':
            self._show_backup()
        elif acao == 'tema':
            self._show_tema()
        elif acao == 'impressoras':
            self._show_impressoras()
        elif acao == 'banco_dados':
            self._show_banco_dados()
        elif acao == 'integracoes':
            self._show_integracoes()
        elif acao == 'seguranca':
            self._show_seguranca()
        else:
            self._show_default()
        
        # Empacota o frame principal
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo de configuração
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção de configuração no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_nfe(self):
        # Tela de configuração de NF-e
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.frame, padding=10)
        
        # Título
        ttk.Label(
            frame, 
            text="Configurações de NF-e", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
        
        # Campos do formulário
        self.nfe_serie = self._criar_campo(frame, "Série:", 1, "1")
        
        self.nfe_ambiente = self._criar_combobox(
            frame, "Ambiente:", 2, 
            ["Homologação", "Produção"], "Homologação"
        )
        
        # Frame para o campo de certificado com botão de procurar
        cert_frame = ttk.Frame(frame)
        cert_frame.grid(row=3, column=1, sticky='ew')
        ttk.Label(frame, text="Certificado:").grid(row=3, column=0, sticky='w', pady=2, padx=5)
        
        self.nfe_certificado = ttk.Entry(cert_frame, width=40)
        self.nfe_certificado.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            cert_frame, text="...", width=3,
            command=lambda: self._selecionar_arquivo(self.nfe_certificado)
        ).pack(side='left', padx=(5, 0))
        
        self.nfe_senha = self._criar_campo(
            frame, "Senha do Certificado:", 4, "", 30
        )
        self.nfe_senha.config(show="*")
        
        # Botão Salvar
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=15)
        
        ttk.Button(
            btn_frame, text="Salvar",
            command=self._salvar_nfe,
            style="Accent.TButton"
        ).pack(side='right', padx=5)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _salvar_nfe(self):
        """Salva as configurações de NF-e"""
        dados = {
            'serie': self.nfe_serie.get(),
            'ambiente': self.nfe_ambiente.get().lower(),
            'certificado': self.nfe_certificado.get(),
            'senha': self.nfe_senha.get()
        }
        if self.ctrl.salvar_config_nfe(dados):
            messagebox.showinfo("Sucesso", "Configurações de NF-e salvas com sucesso!")
    
    def _show_backup(self):
        # Tela de configuração de Backup
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.frame, padding=10)
        
        # Título
        ttk.Label(
            frame, 
            text="Configurações de Backup", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
        
        # Frame para o campo de pasta de backup
        backup_frame = ttk.Frame(frame)
        backup_frame.grid(row=1, column=1, sticky='ew')
        ttk.Label(frame, text="Pasta de Backup:").grid(row=1, column=0, sticky='w', pady=2, padx=5)
        
        self.backup_pasta = ttk.Entry(backup_frame, width=40)
        self.backup_pasta.pack(side='left', fill='x', expand=True)
        
        ttk.Button(
            backup_frame, text="...", width=3,
            command=lambda: self._selecionar_pasta(self.backup_pasta)
        ).pack(side='left', padx=(5, 0))
        
        # Frequência de backup
        self.backup_frequencia = self._criar_combobox(
            frame, "Frequência:", 2,
            ["Diário", "Semanal", "Mensal"], "Diário"
        )
        
        # Manter últimos X backups
        self.backup_manter = self._criar_campo(
            frame, "Manter últimos (dias):", 3, "30"
        )
        
        # Botão Executar Backup Agora
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=15)
        
        ttk.Button(
            btn_frame, text="Executar Backup Agora",
            command=self._executar_backup,
            style="Accent.TButton"
        ).pack(side='left', padx=5)
        
        # Botão Salvar
        ttk.Button(
            btn_frame, text="Salvar",
            command=self._salvar_backup,
            style="Accent.TButton"
        ).pack(side='right', padx=5)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _executar_backup(self):
        """Executa o backup imediatamente"""
        print("Executando backup agora...")
        # Implementar lógica de backup aqui
    
    def _salvar_backup(self):
        """Salva as configurações de backup"""
        dados = {
            'pasta': self.backup_pasta.get(),
            'frequencia': self.backup_frequencia.get().lower(),
            'manter_ultimos': self.backup_manter.get()
        }
        if self.ctrl.salvar_config_backup(dados):
            messagebox.showinfo("Sucesso", "Configurações de backup salvas com sucesso!")
    
    def _criar_seletor_cor(self, frame, label_text, row, variavel, command=None):
        """Cria um seletor de cor com label e botão"""
        # Frame para agrupar label e controles de cor
        frame_linha = ttk.Frame(frame)
        frame_linha.grid(row=row, column=0, columnspan=2, sticky='ew', pady=2)
        
        # Label
        lbl = ttk.Label(frame_linha, text=label_text, width=25, anchor='w')
        lbl.pack(side='left', padx=5)
        
        # Frame para os controles de cor
        frame_controles = ttk.Frame(frame_linha)
        frame_controles.pack(side='right', fill='x', expand=True)
        
        # Botão para selecionar cor
        btn = tk.Button(
            frame_controles, 
            text='', 
            width=3, 
            command=command if command else (lambda: self._selecionar_cor(variavel, btn)),
            relief='solid',
            bd=1
        )
        btn.pack(side='left', padx=(0, 5))
        
        # Atualiza a cor do botão com o valor atual
        try:
            btn.configure(bg=variavel.get())
        except:
            pass
            
        # Entrada de texto para o código da cor
        entry = ttk.Entry(frame_controles, textvariable=variavel, width=10)
        entry.pack(side='left', fill='x', expand=True)
        
        return btn, entry
        
    def _selecionar_cor(self, variavel, btn):
        """Abre o seletor de cores e atualiza o botão"""
        from tkinter import colorchooser
        cor = colorchooser.askcolor(title="Selecionar Cor", color=variavel.get())
        if cor[1]:  # Se o usuário não clicou em Cancelar
            variavel.set(cor[1])
            try:
                btn.configure(bg=cor[1])
            except:
                pass

    def _show_tema(self):
        """Exibe a tela de configuração de tema."""
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Cria um frame principal para o conteúdo
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Frame para as configurações de fonte (lado esquerdo)
        frame_fontes = ttk.LabelFrame(main_frame, text=" Configurações de Fonte ", padding=10)
        frame_fontes.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Frame para as configurações de cores (lado direito)
        frame_cores = ttk.LabelFrame(main_frame, text=" Configurações de Cores ", padding=10)
        frame_cores.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Configura o peso das colunas para dividir 50/50
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Frame para rolagem na seção de fontes
        canvas_fontes = tk.Canvas(frame_fontes, highlightthickness=0)
        scrollbar_fontes = ttk.Scrollbar(frame_fontes, orient="vertical", command=canvas_fontes.yview)
        scrollable_frame_fontes = ttk.Frame(canvas_fontes)
        
        def _on_fontes_configure(event):
            canvas_fontes.configure(scrollregion=canvas_fontes.bbox("all"))
        
        scrollable_frame_fontes.bind("<Configure>", _on_fontes_configure)
        canvas_fontes.create_window((0, 0), window=scrollable_frame_fontes, anchor="nw")
        canvas_fontes.configure(yscrollcommand=scrollbar_fontes.set)
        
        # Frame para rolagem na seção de cores
        canvas_cores = tk.Canvas(frame_cores, highlightthickness=0)
        scrollbar_cores = ttk.Scrollbar(frame_cores, orient="vertical", command=canvas_cores.yview)
        scrollable_frame_cores = ttk.Frame(canvas_cores)
        
        def _on_cores_configure(event):
            canvas_cores.configure(scrollregion=canvas_cores.bbox("all"))
        
        scrollable_frame_cores.bind("<Configure>", _on_cores_configure)
        canvas_cores.create_window((0, 0), window=scrollable_frame_cores, anchor="nw")
        canvas_cores.configure(yscrollcommand=scrollbar_cores.set)
        
        # Empacota os canais e barras de rolagem
        canvas_fontes.pack(side='left', fill='both', expand=True)
        scrollbar_fontes.pack(side='right', fill='y')
        
        canvas_cores.pack(side='left', fill='both', expand=True)
        scrollbar_cores.pack(side='right', fill='y')
        
        # Carrega as configurações salvas
        self.config_tema = self.ctrl.carregar_config_tema()
        
        # Frame para o conteúdo da seção de fontes
        frame_fontes_interno = ttk.Frame(scrollable_frame_fontes, padding=10)
        frame_fontes_interno.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Título da seção de fontes
        ttk.Label(
            frame_fontes_interno, 
            text="Tamanhos de Fonte", 
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='w')
        
        # Configurações de fonte
        row = 1
        
        # 1. Fonte do nome do programa
        ttk.Label(frame_fontes_interno, text="1. Nome do programa:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        self.var_fonte_nome_programa = tk.StringVar(value=self.config_tema.get('fonte_nome_programa', 'Arial'))
        fonte_nome_programa = ttk.Combobox(frame_fontes_interno, textvariable=self.var_fonte_nome_programa, 
                                        values=['Arial', 'Segoe UI', 'Helvetica', 'Verdana'], width=15)
        fonte_nome_programa.grid(row=row, column=1, sticky='w', pady=2)
        
        self.var_tamanho_nome_programa = tk.StringVar(value=self.config_tema.get('tamanho_nome_programa', '16'))
        ttk.Spinbox(frame_fontes_interno, from_=8, to=36, width=5, textvariable=self.var_tamanho_nome_programa).grid(row=row, column=2, padx=5, pady=2)
        
        # 2. Fonte dos botões do cabeçalho
        row += 1
        ttk.Label(frame_fontes_interno, text="2. Botões do cabeçalho:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        self.var_fonte_botoes_cabecalho = tk.StringVar(value=self.config_tema.get('fonte_botoes_cabecalho', 'Arial'))
        fonte_botoes_cabecalho = ttk.Combobox(frame_fontes_interno, textvariable=self.var_fonte_botoes_cabecalho, 
                                           values=['Arial', 'Segoe UI', 'Helvetica', 'Verdana'], width=15)
        fonte_botoes_cabecalho.grid(row=row, column=1, sticky='w', pady=2)
        
        self.var_tamanho_botoes_cabecalho = tk.StringVar(value=self.config_tema.get('tamanho_botoes_cabecalho', '12'))
        ttk.Spinbox(frame_fontes_interno, from_=8, to=24, width=5, textvariable=self.var_tamanho_botoes_cabecalho).grid(row=row, column=2, padx=5, pady=2)
        
        # 3. Fonte do nome do módulo
        row += 1
        ttk.Label(frame_fontes_interno, text="3. Nome do módulo:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        self.var_fonte_modulo = tk.StringVar(value=self.config_tema.get('fonte_modulo', 'Arial'))
        fonte_modulo = ttk.Combobox(frame_fontes_interno, textvariable=self.var_fonte_modulo, 
                                 values=['Arial', 'Segoe UI', 'Helvetica', 'Verdana'], width=15)
        fonte_modulo.grid(row=row, column=1, sticky='w', pady=2)
        
        self.var_tamanho_modulo = tk.StringVar(value=self.config_tema.get('tamanho_modulo', '14'))
        ttk.Spinbox(frame_fontes_interno, from_=8, to=24, width=5, textvariable=self.var_tamanho_modulo).grid(row=row, column=2, padx=5, pady=2)
        
        # 4. Fonte dos botões do módulo
        row += 1
        ttk.Label(frame_fontes_interno, text="4. Botões do módulo:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        self.var_fonte_botoes_modulo = tk.StringVar(value=self.config_tema.get('fonte_botoes_modulo', 'Arial'))
        fonte_botoes_modulo = ttk.Combobox(frame_fontes_interno, textvariable=self.var_fonte_botoes_modulo, 
                                        values=['Arial', 'Segoe UI', 'Helvetica', 'Verdana'], width=15)
        fonte_botoes_modulo.grid(row=row, column=1, sticky='w', pady=2)
        
        self.var_tamanho_botoes_modulo = tk.StringVar(value=self.config_tema.get('tamanho_botoes_modulo', '11'))
        ttk.Spinbox(frame_fontes_interno, from_=8, to=20, width=5, textvariable=self.var_tamanho_botoes_modulo).grid(row=row, column=2, padx=5, pady=2)
        
        # 5. Fonte do texto da tela
        row += 1
        ttk.Label(frame_fontes_interno, text="5. Texto da tela:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        self.var_fonte_texto = tk.StringVar(value=self.config_tema.get('fonte_texto', 'Arial'))
        fonte_texto = ttk.Combobox(frame_fontes_interno, textvariable=self.var_fonte_texto, 
                                 values=['Arial', 'Segoe UI', 'Helvetica', 'Verdana'], width=15)
        fonte_texto.grid(row=row, column=1, sticky='w', pady=2)
        
        self.var_tamanho_texto = tk.StringVar(value=self.config_tema.get('tamanho_texto', '10'))
        ttk.Spinbox(frame_fontes_interno, from_=8, to=18, width=5, textvariable=self.var_tamanho_texto).grid(row=row, column=2, padx=5, pady=2)
        
        # 6. Fonte dos itens da barra lateral
        row += 1
        ttk.Label(frame_fontes_interno, text="6. Itens da barra lateral:", font=('Arial', 10)).grid(row=row, column=0, sticky='w', pady=2)
        self.var_fonte_sidebar = tk.StringVar(value=self.config_tema.get('fonte_sidebar', 'Arial'))
        fonte_sidebar = ttk.Combobox(frame_fontes_interno, textvariable=self.var_fonte_sidebar, 
                                  values=['Arial', 'Segoe UI', 'Helvetica', 'Verdana'], width=15)
        fonte_sidebar.grid(row=row, column=1, sticky='w', pady=2)
        
        self.var_tamanho_sidebar = tk.StringVar(value=self.config_tema.get('tamanho_sidebar', '11'))
        ttk.Spinbox(frame_fontes_interno, from_=8, to=20, width=5, textvariable=self.var_tamanho_sidebar).grid(row=row, column=2, padx=5, pady=2)
        
        # Ajusta o grid
        for i in range(1, 7):
            frame_fontes_interno.grid_rowconfigure(i, pad=5)
        
        # Frame para os botões da seção de fontes
        btn_frame_fontes = ttk.Frame(frame_fontes_interno)
        btn_frame_fontes.grid(row=20, column=0, columnspan=2, pady=(20, 10), sticky='e')
        
        # Botão Aplicar
        ttk.Button(
            btn_frame_fontes, 
            text="Aplicar Configurações",
            command=self._aplicar_tema,
            style='Accent.TButton'
        ).pack(side='right', padx=5)
        
        # Botão Padrão
        ttk.Button(
            btn_frame_fontes,
            text="Restaurar Padrões",
            command=self._restaurar_tema_padrao
        ).pack(side='right', padx=5)
        
        # Frame para o conteúdo da seção de cores
        frame_cores_interno = ttk.Frame(scrollable_frame_cores, padding=10)
        frame_cores_interno.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Título da seção de cores
        ttk.Label(
            frame_cores_interno, 
            text="Cores do Tema", 
            font=('Arial', 12, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky='w')
        
        # Variáveis para as cores (baseado no sistema_pdv.py)
        self.var_cor_primaria = tk.StringVar(value=self.config_tema.get('cor_primaria', '#4a6fa5'))  # Azul médio - barra superior
        self.var_cor_secundaria = tk.StringVar(value=self.config_tema.get('cor_secundaria', '#28b5f4'))  # Azul claro
        self.var_cor_terciaria = tk.StringVar(value=self.config_tema.get('cor_terciaria', '#333f50'))  # Azul escuro - barra lateral
        self.var_cor_fundo = tk.StringVar(value=self.config_tema.get('cor_fundo', '#f0f2f5'))  # Cinza azulado - fundo
        self.var_cor_texto_claro = tk.StringVar(value=self.config_tema.get('cor_texto_claro', '#ffffff'))  # Branco
        self.var_cor_texto_escuro = tk.StringVar(value=self.config_tema.get('cor_texto_escuro', '#333333'))  # Cinza escuro
        self.var_cor_destaque = tk.StringVar(value=self.config_tema.get('cor_destaque', '#4caf50'))  # Verde
        self.var_cor_alerta = tk.StringVar(value=self.config_tema.get('cor_alerta', '#f44336'))  # Vermelho
        self.var_cor_borda = tk.StringVar(value=self.config_tema.get('cor_borda', '#e0e0e0'))  # Cinza claro
        
        # Criar seletores de cor
        row = 1
        self.btn_cor_primaria, _ = self._criar_seletor_cor(
            frame_cores_interno, "1. Cor Primária (barra superior):", row, self.var_cor_primaria
        )
        
        row += 1
        self.btn_cor_secundaria, _ = self._criar_seletor_cor(
            frame_cores_interno, "2. Cor Secundária (destaques):", row, self.var_cor_secundaria
        )
        
        row += 1
        self.btn_cor_terciaria, _ = self._criar_seletor_cor(
            frame_cores_interno, "3. Cor Terciária (barra lateral):", row, self.var_cor_terciaria
        )
        
        row += 1
        self.btn_cor_fundo, _ = self._criar_seletor_cor(
            frame_cores_interno, "4. Fundo da tela:", row, self.var_cor_fundo
        )
        
        row += 1
        self.btn_cor_texto_claro, _ = self._criar_seletor_cor(
            frame_cores_interno, "5. Texto claro (sobre fundo escuro):", row, self.var_cor_texto_claro
        )
        
        row += 1
        self.btn_cor_texto_escuro, _ = self._criar_seletor_cor(
            frame_cores_interno, "6. Texto escuro:", row, self.var_cor_texto_escuro
        )
        
        row += 1
        self.btn_cor_destaque, _ = self._criar_seletor_cor(
            frame_cores_interno, "7. Destaque (verde):", row, self.var_cor_destaque
        )
        
        row += 1
        self.btn_cor_alerta, _ = self._criar_seletor_cor(
            frame_cores_interno, "8. Alerta (vermelho):", row, self.var_cor_alerta
        )
        
        row += 1
        self.btn_cor_borda, _ = self._criar_seletor_cor(
            frame_cores_interno, "9. Bordas:", row, self.var_cor_borda
        )
        
        # Frame para os botões da aba de cores
        btn_frame_cores = ttk.Frame(frame_cores_interno)
        btn_frame_cores.grid(row=20, column=0, columnspan=2, pady=(20, 10), sticky='e')
        
        # Botão Aplicar
        ttk.Button(
            btn_frame_cores, 
            text="Aplicar Cores",
            command=self._aplicar_tema,
            style='Accent.TButton'
        ).pack(side='right', padx=5)
        
        # Botão Padrão
        ttk.Button(
            btn_frame_cores,
            text="Restaurar Padrões",
            command=self._restaurar_tema_padrao
        ).pack(side='right', padx=5)
        
        # Empacota o frame de cores
        frame_cores_interno.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Atualiza o frame atual
        self.current_view = main_frame
        
    def _clarear_cor(self, cor_hex, percentual=10):
        """Clareia uma cor em um determinado percentual"""
        try:
            # Remove o # se existir
            cor_hex = cor_hex.lstrip('#')
            
            # Converte para RGB
            r, g, b = int(cor_hex[0:2], 16), int(cor_hex[2:4], 16), int(cor_hex[4:6], 16)
            
            # Clareia a cor
            r = min(255, int(r * (1 + percentual / 100)))
            g = min(255, int(g * (1 + percentual / 100)))
            b = min(255, int(b * (1 + percentual / 100)))
            
            # Retorna no formato #RRGGBB
            return f'#{r:02x}{g:02x}{b:02x}'
            
        except Exception:
            return cor_hex
    
    def _aplicar_tema(self):
        """Aplica as configurações de tema"""
        try:
            # Prepara os dados do tema com as novas variáveis
            dados = {
                # Cores
                'cor_primaria': self.var_cor_primaria.get(),
                'cor_secundaria': self.var_cor_secundaria.get(),
                'cor_terciaria': self.var_cor_terciaria.get(),
                'cor_fundo': self.var_cor_fundo.get(),
                'cor_texto_claro': self.var_cor_texto_claro.get(),
                'cor_texto_escuro': self.var_cor_texto_escuro.get(),
                'cor_destaque': self.var_cor_destaque.get(),
                'cor_alerta': self.var_cor_alerta.get(),
                'cor_borda': self.var_cor_borda.get(),
                
                # Fontes
                'fonte_nome_programa': self.var_fonte_nome_programa.get(),
                'tamanho_nome_programa': self.var_tamanho_nome_programa.get(),
                'fonte_botoes_cabecalho': self.var_fonte_botoes_cabecalho.get(),
                'tamanho_botoes_cabecalho': self.var_tamanho_botoes_cabecalho.get(),
                'fonte_modulo': self.var_fonte_modulo.get(),
                'tamanho_modulo': self.var_tamanho_modulo.get(),
                'fonte_botoes_modulo': self.var_fonte_botoes_modulo.get(),
                'tamanho_botoes_modulo': self.var_tamanho_botoes_modulo.get(),
                'fonte_texto': self.var_fonte_texto.get(),
                'tamanho_texto': self.var_tamanho_texto.get(),
                'fonte_sidebar': self.var_fonte_sidebar.get(),
                'tamanho_sidebar': self.var_tamanho_sidebar.get()
            }
            
            # Adiciona as cores adicionais necessárias
            dados.update({
                'cor_botao': dados['cor_secundaria'],
                'cor_texto_botao': dados['cor_texto_claro'],
                'cor_cabecalho': dados['cor_primaria'],
                'cor_texto_cabecalho': dados['cor_texto_claro'],
                'cor_sidebar': dados['cor_terciaria'],
                'cor_texto_sidebar': dados['cor_texto_claro'],
                'cor_texto': dados['cor_texto_escuro'],
                'cor_sucesso': '#2ecc71',
                'cor_erro': '#e74c3c'
            })
            
            # Verifica se houve alterações em relação ao tema atual
            alteracoes = False
            for chave, valor in dados.items():
                if chave not in self.config_tema or str(self.config_tema[chave]).lower() != str(valor).lower():
                    alteracoes = True
                    break
            
            if not alteracoes:
                messagebox.showinfo("Sem alterações", "Nenhuma alteração foi feita no tema.")
                return
            
            # Valida as cores - verifica se começa com # e tem 4 ou 7 caracteres
            for key, color_value in dados.items():
                if key.startswith('cor_'):
                    if not (isinstance(color_value, str) and 
                           (color_value.startswith('#') and len(color_value) in (4, 7)) or 
                           color_value.lower() in ['black', 'white', 'red', 'green', 'blue', 'yellow', 'gray']):
                        messagebox.showerror("Erro de validação", 
                            f"Formato de cor inválido para {key}: {color_value}\n"
                            "Use o formato #RGB ou #RRGGBB ou nomes de cores comuns.")
                        return
            
            # Salva as configurações
            if self.ctrl.salvar_config_tema(dados):
                # Mostra mensagem de sucesso
                messagebox.showinfo(
                    "Tema Atualizado",
                    "As configurações de tema foram salvas com sucesso!\n\n"
                    "O programa será reiniciado para aplicar as alterações."
                )
                
                # Fecha o programa para aplicar as alterações
                if hasattr(self.controller, 'root') and hasattr(self.controller.root, 'destroy'):
                    self.controller.root.destroy()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar as configurações de tema.")
                
        except Exception as e:
            print(f"Erro ao aplicar tema: {e}")
            messagebox.showerror(
                "Erro",
                f"Ocorreu um erro ao aplicar o tema:\n{str(e)}"
            )
    
    def _restaurar_tema_padrao(self):
        """Restaura as configurações padrão do tema"""
        # Cores padrão baseadas no sistema_pdv.py
        self.var_cor_primaria.set('#4a6fa5')      # Azul médio - barra superior
        self.var_cor_secundaria.set('#28b5f4')    # Azul claro - destaques
        self.var_cor_terciaria.set('#333f50')     # Azul escuro - barra lateral
        self.var_cor_fundo.set('#f0f2f5')         # Cinza azulado - fundo
        self.var_cor_texto_claro.set('#ffffff')    # Branco - texto claro
        self.var_cor_texto_escuro.set('#333333')   # Cinza escuro - texto
        self.var_cor_destaque.set('#4caf50')       # Verde - destaques
        self.var_cor_alerta.set('#f44336')         # Vermelho - alertas
        self.var_cor_borda.set('#e0e0e0')          # Cinza claro - bordas
        
        # Atualiza os botões de cor
        self.btn_cor_primaria.configure(bg='#4a6fa5')
        self.btn_cor_secundaria.configure(bg='#28b5f4')
        self.btn_cor_terciaria.configure(bg='#333f50')
        self.btn_cor_fundo.configure(bg='#f0f2f5')
        self.btn_cor_texto_claro.configure(bg='#ffffff')
        self.btn_cor_texto_escuro.configure(bg='#333333')
        self.btn_cor_destaque.configure(bg='#4caf50')
        self.btn_cor_alerta.configure(bg='#f44336')
        self.btn_cor_borda.configure(bg='#e0e0e0')
        
        messagebox.showinfo("Sucesso", "Tema restaurado para os valores padrão.")
    
    def _aplicar_estilo_tema(self, config_tema):
        """Aplica o estilo de tema com base nas configurações fornecidas"""
        try:
            # Obtém o estilo do sistema
            estilo = ttk.Style()
            
            # Usa um nome de tema fixo para evitar múltiplas instâncias
            tema_nome = "CustomTemaAquarius"
            
            # Verifica se o tema já existe
            if tema_nome in estilo.theme_names():
                # Se já existe, apenas reutiliza
                estilo.theme_use(tema_nome)
            else:
                # Se não existe, cria um novo
                estilo.theme_create(tema_nome, parent="alt")
                estilo.theme_use(tema_nome)
            
            # Limpa qualquer configuração anterior
            estilo.theme_settings(tema_nome, {"TButton": {}, "TLabel": {}, "TFrame": {}})
            
            # Define as fontes a partir das configurações
            fonte_empresa = (config_tema.get('fonte_nome_programa', 'Arial'), 
                           int(config_tema.get('tamanho_nome_programa', 24)), 'bold')
            fonte_botoes_cabecalho = (config_tema.get('fonte_botoes_cabecalho', 'Arial'), 
                                   int(config_tema.get('tamanho_botoes_cabecalho', 12)))
            fonte_nomes_modulos = (config_tema.get('fonte_modulo', 'Arial'), 
                                int(config_tema.get('tamanho_modulo', 12)), 'bold')
            fonte_botoes_sidebar = (config_tema.get('fonte_sidebar', 'Arial'), 
                                 int(config_tema.get('tamanho_sidebar', 11)))
            fonte_texto_principal = (config_tema.get('fonte_texto', 'Arial'), 
                                  int(config_tema.get('tamanho_texto', 10)))
            
            # Configura o estilo dos botões padrão
            estilo.configure('TButton',
                background=config_tema.get('cor_secundaria', '#28b5f4'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                font=fonte_texto_principal,
                padding=5,
                relief='flat'
            )
            
            # Configura o estilo dos botões de cabeçalho
            estilo.configure('Header.TButton',
                background=config_tema.get('cor_primaria', '#4a6fa5'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                font=fonte_botoes_cabecalho,
                padding=5,
                relief='flat'
            )
            
            # Configura o estilo dos botões da barra lateral
            estilo.configure('Sidebar.TButton',
                background=config_tema.get('cor_terciaria', '#333f50'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                font=fonte_botoes_sidebar,
                padding=10,
                relief='flat',
                width=20
            )
            
            # Configura o estado hover dos botões
            estilo.map('TButton',
                background=[('active', self._clarear_cor(config_tema.get('cor_secundaria', '#28b5f4'), 20))],
                foreground=[('active', config_tema.get('cor_texto_claro', '#ffffff'))]
            )
            
            # Configura o estilo dos labels
            estilo.configure('TLabel',
                background=config_tema.get('cor_fundo', '#f0f2f5'),
                foreground=config_tema.get('cor_texto_escuro', '#333333'),
                font=fonte_texto_principal
            )
            
            # Estilo para títulos de módulo
            estilo.configure('Title.TLabel',
                background=config_tema.get('cor_fundo', '#f0f2f5'),
                foreground=config_tema.get('cor_texto_escuro', '#333333'),
                font=fonte_nomes_modulos
            )
            
            # Estilo para o nome do programa
            estilo.configure('AppName.TLabel',
                background=config_tema.get('cor_primaria', '#4a6fa5'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                font=fonte_empresa
            )
            
            # Configura o estilo do notebook (abas)
            estilo.configure('TNotebook',
                background=config_tema.get('cor_fundo', '#f0f2f5')
            )
            estilo.configure('TNotebook.Tab',
                background=config_tema.get('cor_terciaria', '#333f50'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                padding=[10, 5],
                font=('Arial', 10, 'bold')
            )
            estilo.map('TNotebook.Tab',
                background=[('selected', config_tema.get('cor_primaria', '#4a6fa5'))],
                foreground=[('selected', config_tema.get('cor_texto_claro', '#ffffff'))]
            )
            
            # Configura o estilo dos frames
            estilo.configure('TFrame',
                background=config_tema.get('cor_fundo', '#f0f2f5')
            )
            
            # Configura o estilo dos campos de entrada
            estilo.configure('TEntry',
                fieldbackground='white',
                foreground='black',
                font=fonte_texto_principal,
                borderwidth=1,
                relief='solid'
            )
            
            # Configura o estilo dos checkbuttons
            estilo.configure('TCheckbutton',
                background=config_tema.get('cor_fundo', '#f0f2f5'),
                font=fonte_texto_principal,
                foreground=config_tema.get('cor_texto_escuro', '#333333')
            )
            
            # Configura o estilo dos radiobuttons
            estilo.configure('TRadiobutton',
                background=config_tema.get('cor_fundo', '#f0f2f5'),
                font=fonte_texto_principal,
                foreground=config_tema.get('cor_texto_escuro', '#333333')
            )
            
            # Configura o estilo dos combobox
            estilo.configure('TCombobox',
                fieldbackground='white',
                background='white',
                font=fonte_texto_principal,
                arrowsize=12
            )
            
            # Configura o estilo da barra de rolagem
            estilo.configure('Vertical.TScrollbar',
                background=config_tema.get('cor_terciaria', '#333f50'),
                arrowcolor=config_tema.get('cor_texto_claro', '#ffffff'),
                troughcolor=config_tema.get('cor_terciaria', '#333f50'),
                bordercolor=config_tema.get('cor_terciaria', '#333f50'),
                lightcolor=config_tema.get('cor_terciaria', '#333f50'),
                darkcolor=config_tema.get('cor_terciaria', '#333f50')
            )
            estilo.map('Vertical.TScrollbar',
                background=[('active', self._clarear_cor(config_tema.get('cor_terciaria', '#333f50'), 20))]
            )
            
            # 1. Estilo do nome da empresa
            estilo.configure('Empresa.TLabel',
                font=fonte_empresa,
                background=config_tema.get('cor_primaria', '#4a6fa5'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff')
            )
            
            # 2. Estilo dos botões do cabeçalho (cadastro, mesas, etc)
            estilo.configure('Cabecalho.TButton',
                background=config_tema.get('cor_primaria', '#4a6fa5'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                font=fonte_botoes_cabecalho,
                borderwidth=0
            )
            
            # 3. Estilo dos nomes dos módulos na barra lateral
            estilo.configure('Modulos.TLabel',
                background=config_tema.get('cor_terciaria', '#333f50'),
                foreground=config_tema.get('cor_texto_claro', '#ffffff'),
                font=fonte_nomes_modulos,
                padding=(10, 5, 10, 5)
            )
            
            # 4. Estilo dos botões da barra lateral
            estilo.configure('Sidebar.TButton',
                background=config_tema['cor_sidebar'],
                foreground=config_tema['cor_texto_sidebar'],
                font=fonte_botoes_sidebar,
                borderwidth=0,
                padding=(20, 5, 20, 5)
            )
            
            # Configura o estilo da barra lateral
            estilo.configure('Sidebar.TFrame',
                background=config_tema['cor_sidebar']
            )
            
            # Configura o estilo dos campos de entrada
            estilo.configure('TEntry',
                fieldbackground='white',
                foreground='black',
                insertcolor='black',
                font=fonte_texto_principal
            )
            
            # Configura o estilo dos comboboxes
            estilo.configure('TCombobox',
                fieldbackground='white',
                foreground='black',
                selectbackground=config_tema['cor_botao'],
                selectforeground=config_tema['cor_texto_botao'],
                font=fonte_texto_principal
            )
            
            # Configura o estilo dos checkbuttons
            estilo.configure('TCheckbutton',
                background=config_tema['cor_fundo'],
                foreground='black',
                font=fonte_texto_principal
            )
            
            # Configura o estilo dos radiobuttons
            estilo.configure('TRadiobutton',
                background=config_tema['cor_fundo'],
                foreground='black',
                font=fonte_texto_principal
            )
            
            # Configura o estilo dos notebooks (abas)
            estilo.configure('TNotebook',
                background=config_tema['cor_fundo']
            )
            estilo.configure('TNotebook.Tab',
                background=config_tema['cor_sidebar'],
                foreground=config_tema['cor_texto_sidebar'],
                padding=[10, 5],
                font=fonte_botoes_sidebar
            )
            
            # Mapeia os estilos dos estados dos botões
            estilo.map('TButton',
                background=[('active', config_tema['cor_botao']), ('!disabled', config_tema['cor_botao'])],
                foreground=[('active', config_tema['cor_texto_botao']), ('!disabled', config_tema['cor_texto_botao'])]
            )
            
            estilo.map('Cabecalho.TButton',
                background=[('active', config_tema['cor_botao']), ('!disabled', config_tema['cor_cabecalho'])],
                foreground=[('active', config_tema['cor_texto_botao']), ('!disabled', config_tema['cor_texto_cabecalho'])]
            )
            
            estilo.map('Sidebar.TButton',
                background=[('active', config_tema['cor_botao']), ('!disabled', config_tema['cor_sidebar'])],
                foreground=[('active', config_tema['cor_texto_botao']), ('!disabled', config_tema['cor_texto_sidebar'])]
            )
            
            estilo.map('TNotebook.Tab',
                background=[('selected', config_tema['cor_botao']), ('active', config_tema['cor_botao'])],
                foreground=[('selected', config_tema['cor_texto_botao']), ('active', config_tema['cor_texto_botao'])]
            )
            
            # Aplica o tema a janela principal
            self.parent.configure(background=config_tema['cor_fundo'])
            
            # Notifica o controlador para atualizar outros componentes
            if hasattr(self.controller, 'atualizar_tema'):
                self.controller.atualizar_tema(config_tema)
                
        except Exception as e:
            print(f"Erro ao aplicar estilo de tema: {e}")
    
    def _show_impressoras(self):
        # Tela de configuração de impressoras
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.frame, padding=10)
        
        # Título
        ttk.Label(
            frame, 
            text="Configuração de Impressoras", 
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
        
        try:
            # Obtém a lista de impressoras disponíveis
            impressoras = self.ctrl.listar_impressoras()
            
            # Verifica se a lista de impressoras está vazia
            if not impressoras:
                impressoras = ["Nenhuma impressora encontrada"]
                
            # Impressora de Cupom Fiscal
            self.imp_cupom = self._criar_combobox(
                frame, "Cupom Fiscal:", 1,
                impressoras, impressoras[0] if impressoras else ""
            )
            
            # Impressora da Cozinha
            self.imp_cozinha = self._criar_combobox(
                frame, "Cozinha:", 2,
                impressoras, impressoras[0] if impressoras else ""
            )
            
            # Impressora do Bar
            self.imp_bar = self._criar_combobox(
                frame, "Bar:", 3,
                impressoras, impressoras[0] if impressoras else ""
            )
            
            # Impressora de Delivery
            self.imp_delivery = self._criar_combobox(
                frame, "Delivery:", 4,
                impressoras, impressoras[0] if impressoras else ""
            )
            
            # Configurações de impressão
            ttk.Label(
                frame, 
                text="Configurações de Impressão", 
                font=('Arial', 10, 'bold')
            ).grid(row=5, column=0, columnspan=2, pady=(15,5), sticky='w')
            
            # Tamanho da fonte
            self.imp_tamanho_fonte = self._criar_combobox(
                frame, "Tamanho da Fonte:", 6,
                ["8", "9", "10", "11", "12", "14", "16"], "12"
            )
            
            # Botão Testar Impressão
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=7, column=0, columnspan=2, pady=15)
            
            ttk.Button(
                btn_frame, text="Testar Impressão",
                command=self._testar_impressao
            ).pack(side='left', padx=5)
            
            ttk.Button(
                btn_frame, text="Salvar Configurações",
                command=self._salvar_impressoras,
                style="Accent.TButton"
            ).pack(side='right')
            
        except Exception as e:
            print(f"Erro ao carregar impressoras: {e}")
            ttk.Label(
                frame,
                text=f"Erro ao carregar as impressoras: {str(e)}",
                foreground="red"
            ).pack(pady=20)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _testar_impressao(self):
        """Testa a impressão na impressora selecionada"""
        if hasattr(self, 'imp_cupom') and self.imp_cupom.get():
            if self.ctrl.testar_impressora(self.imp_cupom.get()):
                messagebox.showinfo("Sucesso", "Teste de impressão enviado com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Nenhuma impressora selecionada para teste.")
    
    def _salvar_impressoras(self):
        """Salva as configurações das impressoras"""
        dados = {
            'cupom_fiscal': self.imp_cupom.get(),
            'cozinha': self.imp_cozinha.get(),
            'bar': self.imp_bar.get(),
            'delivery': self.imp_delivery.get(),
            'tamanho_fonte': self.imp_tamanho_fonte.get()
        }
        if self.ctrl.salvar_config_impressoras(dados):
            messagebox.showinfo("Sucesso", "Configurações de impressão salvas com sucesso!")
    
    def _testar_conexao_db(self):
        """Testa a conexão com o banco de dados"""
        if self.ctrl.testar_conexao_banco_dados(
            self.db_host.get(),
            self.db_porta.get(),
            self.db_usuario.get(),
            self.db_senha.get(),
            self.db_nome.get()
        ):
            messagebox.showinfo("Sucesso", "Conexão com o banco de dados realizada com sucesso!")
    
    def _fazer_backup_db(self):
        """Inicia o backup do banco de dados"""
        destino = filedialog.askdirectory(title="Selecionar pasta para salvar o backup")
        if destino and self.ctrl.fazer_backup_banco_dados(destino):
            messagebox.showinfo("Sucesso", "Backup do banco de dados realizado com sucesso!")
    
    def _restaurar_backup_db(self):
        """Restaura um backup do banco de dados"""
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Backup",
            filetypes=[("Arquivos de Backup", "*.sql *.backup")]
        )
        if filename and self.ctrl.restaurar_backup_banco_dados(filename):
            messagebox.showinfo("Sucesso", "Backup restaurado com sucesso!")
    
    def _salvar_banco_dados(self):
        """Salva as configurações do banco de dados"""
        dados = {
            'host': self.db_host.get(),
            'porta': self.db_porta.get(),
            'usuario': self.db_usuario.get(),
            'senha': self.db_senha.get(),
            'nome_bd': self.db_nome.get()
        }
        if self.ctrl.salvar_config_banco_dados(dados):
            messagebox.showinfo("Sucesso", "Configurações do banco de dados salvas com sucesso!")
        
    def _show_banco_dados(self):
        # Tela de configuração do Banco de Dados
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.frame, padding=10)
        
        try:
            # Título
            ttk.Label(
                frame, 
                text="Configurações do Banco de Dados", 
                font=('Arial', 14, 'bold')
            ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
            
            # Carrega as configurações atuais do banco de dados
            config = self.ctrl.carregar_config_banco_dados()
            
            # Campos de conexão
            self.db_host = self._criar_campo(frame, "Servidor:", 1, config.get('host', 'localhost'))
            self.db_porta = self._criar_campo(frame, "Porta:", 2, str(config.get('porta', '5432')))
            self.db_usuario = self._criar_campo(frame, "Usuário:", 3, config.get('usuario', 'postgres'))
            
            # Senha
            ttk.Label(frame, text="Senha:").grid(row=4, column=0, sticky='w', pady=2, padx=5)
            self.db_senha = ttk.Entry(frame, show="*", width=30)
            self.db_senha.grid(row=4, column=1, sticky='ew', pady=2)
            self.db_senha.insert(0, config.get('senha', ''))
            
            self.db_nome = self._criar_campo(frame, "Nome do Banco:", 5, config.get('nome_bd', 'pdv_aquarius'))
            
            # Botões
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=6, column=0, columnspan=3, pady=15, sticky='ew')
            
            # Frame para os botões à esquerda
            left_btns = ttk.Frame(btn_frame)
            left_btns.pack(side='left')
            
            ttk.Button(
                left_btns, text="Testar Conexão",
                command=self._testar_conexao_db
            ).grid(row=0, column=0, padx=5)
            
            ttk.Button(
                left_btns, text="Fazer Backup",
                command=self._fazer_backup_db
            ).grid(row=0, column=1, padx=5)
            
            ttk.Button(
                left_btns, text="Restaurar Backup",
                command=self._restaurar_backup_db
            ).grid(row=0, column=2, padx=5)
            
            # Frame para o botão à direita
            right_btns = ttk.Frame(btn_frame)
            right_btns.pack(side='right')
            
            # Botão Salvar
            ttk.Button(
                right_btns, text="Salvar Configurações",
                command=self._salvar_banco_dados,
                style="Accent.TButton"
            ).grid(row=0, column=0, padx=5)
            
        except Exception as e:
            print(f"Erro ao carregar configurações do banco de dados: {e}")
            ttk.Label(
                frame,
                text=f"Erro ao carregar as configurações do banco de dados: {str(e)}",
                foreground="red"
            ).pack(pady=20)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _show_integracoes(self):
        # Tela de configuração de Integrações
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.frame, padding=10)
        
        try:
            # Título
            ttk.Label(
                frame, 
                text="Configurações de Integrações", 
                font=('Arial', 14, 'bold')
            ).grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            
            # Carrega as configurações atuais das integrações
            config = self.ctrl.carregar_config_integracoes()
            
            # Integração com ERP
            ttk.Label(
                frame, 
                text="Sistema ERP", 
                font=('Arial', 10, 'bold')
            ).grid(row=1, column=0, columnspan=2, pady=(5,2), sticky='w')
            
            self.erp_ativo = ttk.BooleanVar(value=config.get('erp', {}).get('ativo', False))
            ttk.Checkbutton(
                frame, text="Ativar integração com ERP",
                variable=self.erp_ativo
            ).grid(row=2, column=0, columnspan=2, sticky='w')
            
            self.erp_url = self._criar_campo(
                frame, "URL do ERP:", 3, 
                config.get('erp', {}).get('url', 'https://erp.empresa.com.br/api')
            )
            
            self.erp_token = self._criar_campo(
                frame, "Token de Acesso:", 4, 
                config.get('erp', {}).get('token', '')
            )
            
            # Integração com E-commerce
            ttk.Label(
                frame, 
                text="E-commerce", 
                font=('Arial', 10, 'bold')
            ).grid(row=5, column=0, columnspan=2, pady=(15,2), sticky='w')
            
            self.ecommerce_ativo = ttk.BooleanVar(value=config.get('ecommerce', {}).get('ativo', False))
            ttk.Checkbutton(
                frame, text="Ativar integração com E-commerce",
                variable=self.ecommerce_ativo
            ).grid(row=6, column=0, columnspan=2, sticky='w')
            
            plataformas = ["Nenhuma", "Loja Integrada", "Nuvemshop", "Outra"]
            plataforma_atual = config.get('ecommerce', {}).get('plataforma', 'Nenhuma')
            if plataforma_atual not in plataformas:
                plataformas.append(plataforma_atual)
                
            self.ecommerce_plataforma = self._criar_combobox(
                frame, "Plataforma:", 7,
                plataformas, plataforma_atual
            )
            
            # Botão Salvar
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=8, column=0, columnspan=2, pady=15, sticky='e')
            
            ttk.Button(
                btn_frame, text="Salvar Configurações",
                command=self._salvar_integracoes,
                style="Accent.TButton"
            ).grid(row=0, column=0, padx=5)
            
        except Exception as e:
            print(f"Erro ao carregar configurações de integrações: {e}")
            ttk.Label(
                frame,
                text=f"Erro ao carregar as configurações de integrações: {str(e)}",
                foreground="red"
            ).grid(row=0, column=0, pady=20, padx=10)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _salvar_integracoes(self):
        """Salva as configurações de integrações"""
        dados = {
            'erp': {
                'ativo': self.erp_ativo.get(),
                'url': self.erp_url.get(),
                'token': self.erp_token.get()
            },
            'ecommerce': {
                'ativo': self.ecommerce_ativo.get(),
                'plataforma': self.ecommerce_plataforma.get()
            }
        }
        if self.ctrl.salvar_config_integracoes(dados):
            messagebox.showinfo("Sucesso", "Configurações de integrações salvas com sucesso!")
    
    def _show_seguranca(self):
        # Tela de configuração de Segurança
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.frame, padding=10)
        
        try:
            # Carrega as configurações atuais de segurança
            config = self.ctrl.carregar_config_seguranca()
            
            # Título
            ttk.Label(
                frame, 
                text="Configurações de Segurança", 
                font=('Arial', 14, 'bold')
            ).grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            
            # Senha de administrador
            ttk.Label(
                frame, 
                text="Alterar Senha do Administrador", 
                font=('Arial', 10, 'bold')
            ).grid(row=1, column=0, columnspan=2, pady=(5,2), sticky='w')
            
            self.senha_atual = self._criar_campo(
                frame, "Senha Atual:", 2, "", 30
            )
            self.senha_atual.config(show="*")
            
            self.nova_senha = self._criar_campo(
                frame, "Nova Senha:", 3, "", 30
            )
            self.nova_senha.config(show="*")
            
            self.confirmar_senha = self._criar_campo(
                frame, "Confirmar Nova Senha:", 4, "", 30
            )
            self.confirmar_senha.config(show="*")
            
            # Configurações de segurança
            ttk.Label(
                frame, 
                text="Configurações de Segurança", 
                font=('Arial', 10, 'bold')
            ).grid(row=5, column=0, columnspan=2, pady=(15,2), sticky='w')
            
            self.bloquear_tela = ttk.BooleanVar(value=config.get('bloquear_tela', True))
            ttk.Checkbutton(
                frame, text="Bloquear tela após inatividade",
                variable=self.bloquear_tela
            ).grid(row=6, column=0, columnspan=2, sticky='w')
            
            tempos = ["1", "5", "10", "15", "30", "60"]
            tempo_atual = str(config.get('tempo_inatividade', '15'))
            if tempo_atual not in tempos:
                tempos.append(tempo_atual)
                
            self.tempo_inatividade = self._criar_combobox(
                frame, "Tempo de inatividade (minutos):", 7,
                tempos, tempo_atual
            )
            
            # Botão Salvar
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=8, column=0, columnspan=2, pady=15)
            
            ttk.Button(
                btn_frame, text="Alterar Senha",
                command=self._alterar_senha
            ).pack(side='left', padx=5)
            
            ttk.Button(
                btn_frame, text="Salvar Configurações",
                command=self._salvar_seguranca,
                style="Accent.TButton"
            ).pack(side='right')
            
        except Exception as e:
            print(f"Erro ao carregar configurações de segurança: {e}")
            ttk.Label(
                frame,
                text=f"Erro ao carregar as configurações de segurança: {str(e)}",
                foreground="red"
            ).pack(pady=20)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _alterar_senha(self):
        """Altera a senha do usuário atual"""
        senha_atual = self.senha_atual.get()
        nova_senha = self.nova_senha.get()
        confirmar_senha = self.confirmar_senha.get()
        
        if not senha_atual or not nova_senha or not confirmar_senha:
            messagebox.showwarning("Atenção", "Preencha todos os campos de senha!")
            return
            
        if nova_senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não conferem!")
            return
            
        if self.ctrl.alterar_senha(senha_atual, nova_senha):
            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
            # Limpa os campos de senha
            self.senha_atual.delete(0, tk.END)
            self.nova_senha.delete(0, tk.END)
            self.confirmar_senha.delete(0, tk.END)
    
    def _salvar_seguranca(self):
        """Salva as configurações de segurança"""
        dados = {
            'bloquear_tela': self.bloquear_tela.get(),
            'tempo_inatividade': int(self.tempo_inatividade.get())
        }
        if self.ctrl.salvar_config_seguranca(dados):
            messagebox.showinfo("Sucesso", "Configurações de segurança salvas com sucesso!")
