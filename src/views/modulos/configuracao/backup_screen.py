import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class BackupScreen:
    def __init__(self, parent, ctrl):
        self.parent = parent
        self.ctrl = ctrl
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        self.main_frame = tk.Frame(self.parent, bg='#f0f2f5')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(self.main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DE BACKUP", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Frame do formulário com padding maior nas laterais para centralizar
        form_frame = tk.Frame(self.main_frame, bg='#f0f2f5', padx=200, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Carrega as configurações salvas
        config_backup = self.ctrl.carregar_config_backup()
        
        # Estilo dos labels e campos
        label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w', 'fg': '#000000'}
        entry_style = {'font': ('Arial', 10), 'width': 25, 'bg': 'white', 'borderwidth': 0, 'highlightthickness': 0}
        
        # Pasta de Backup
        tk.Label(form_frame, text="Pasta de Backup:", **label_style).grid(row=0, column=0, sticky='w', pady=5)
        
        # Frame para o campo de pasta
        pasta_frame = tk.Frame(form_frame, bg='#f0f2f5')
        pasta_frame.grid(row=0, column=1, sticky='ew', pady=5)
        
        self.backup_pasta = tk.Entry(pasta_frame, **entry_style)
        self.backup_pasta.pack(side='left', fill='x', expand=True)
        
        # Preenche com a pasta salva, se existir
        if config_backup and 'pasta' in config_backup:
            self.backup_pasta.insert(0, config_backup['pasta'])
        
        # Botão para selecionar pasta
        btn_pasta = tk.Button(
            pasta_frame,
            text="...",
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            width=3,
            relief='flat',
            cursor='hand2',
            command=self._selecionar_pasta
        )
        btn_pasta.pack(side='right', padx=(5, 0))
        
        # Frequência de backup
        tk.Label(form_frame, text="Frequência:", **label_style).grid(row=1, column=0, sticky='w', pady=5)
        
        # Frame para o combobox
        freq_frame = tk.Frame(form_frame, bg='#f0f2f5')
        freq_frame.grid(row=1, column=1, sticky='ew', pady=5)
        
        freq_padrao = config_backup.get('frequencia', 'Diário').capitalize()
        self.backup_frequencia = ttk.Combobox(
            freq_frame,
            values=["Diário", "Semanal", "Mensal"],
            state='readonly',
            width=22
        )
        self.backup_frequencia.set(freq_padrao)
        self.backup_frequencia.pack(fill='x')
        
        # Manter últimos X backups
        tk.Label(form_frame, text="Manter últimos (dias):", **label_style).grid(row=2, column=0, sticky='w', pady=5)
        
        # Frame para o campo de dias
        dias_frame = tk.Frame(form_frame, bg='#f0f2f5')
        dias_frame.grid(row=2, column=1, sticky='ew', pady=5)
        
        manter_padrao = config_backup.get('manter_ultimos', '30')
        self.backup_manter = tk.Entry(dias_frame, **entry_style)
        self.backup_manter.insert(0, manter_padrao)
        self.backup_manter.pack(fill='x')
        
        # Frame para os botões
        btn_frame = tk.Frame(form_frame, bg='#f0f2f5', pady=20)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky='e', pady=(30, 0))
        
        # Botão Criar Arquivo - Azul padrão
        btn_executar = tk.Button(
            btn_frame,
            text="Criar Arquivo",
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self._executar_backup
        )
        btn_executar.pack(side='right', padx=5)
        
        # Botão Restaurar Backup - Laranja
        btn_restaurar = tk.Button(
            btn_frame,
            text="Restaurar Backup",
            font=('Arial', 10, 'bold'),
            bg='#ff8c00',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self._restaurar_backup
        )
        btn_restaurar.pack(side='right', padx=5)
        
        # Botão Salvar - Verde
        btn_salvar = tk.Button(
            btn_frame,
            text="Salvar Configurações",
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=self._salvar_backup
        )
        btn_salvar.pack(side='right', padx=5)
        
        # Configura o grid para expandir corretamente
        form_frame.columnconfigure(1, weight=1)
    
    def _selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.backup_pasta.delete(0, tk.END)
            self.backup_pasta.insert(0, pasta)
    
    def _executar_backup(self):
        # Implementação do backup
        pass
    
    def _restaurar_backup(self):
        # Implementação da restauração
        pass
    
    def _salvar_backup(self):
        # Implementação do salvamento
        pass
