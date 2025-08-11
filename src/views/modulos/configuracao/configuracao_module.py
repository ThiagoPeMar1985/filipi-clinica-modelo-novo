import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys


# Adicione o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from ..base_module import BaseModule
from src.controllers.permission_controller import PermissionController

class ConfiguracaoModule(BaseModule):
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
            entry.insert(0, folder)
    
    def __init__(self, parent, controller):
        """Inicializa o módulo de configuração."""
        super().__init__(parent, controller)
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Frame para o conteúdo
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Mostra a tela inicial
        self._show_default()
        
        self.permission_ctrl = PermissionController()
        
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
        
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo de configuração
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            
        self.current_view = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        self.current_view.pack(fill='both', expand=True)
        
        label = tk.Label(
            self.current_view, 
            text="Selecione uma opção de configuração no menu lateral", 
            font=('Arial', 12),
            bg='#f0f2f5'
        )
        label.place(relx=0.5, rely=0.5, anchor='center')
    
    def _show_nfe(self):
        # Tela de configuração de NF-e
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DE NOTA FISCAL ELETRÔNICA", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Frame do formulário com padding maior nas laterais para centralizar
        form_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=200, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Estilo dos labels e campos
        label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w', 'fg': '#000000'}
        entry_style = {'font': ('Arial', 10), 'width': 30, 'bg': 'white', 'borderwidth': 0, 'highlightthickness': 0}
        
        # Frame para o conteúdo
        content_frame = tk.Frame(form_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True)
        
        # Configura o grid
        content_frame.columnconfigure(1, weight=1, minsize=300)  # Coluna dos campos
        
        # Dados da NF-e
        tk.Label(content_frame, text="Dados da NF-e", font=('Arial', 12, 'bold'), 
                bg='#f0f2f5').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        # Série
        tk.Label(content_frame, text="Série:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.nfe_serie = tk.Entry(content_frame, **entry_style)
        self.nfe_serie.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        
        # Ambiente
        tk.Label(content_frame, text="Ambiente:", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        
        self.ambiente_var = tk.StringVar(value="Homologação")
        self.nfe_ambiente = ttk.Combobox(
            content_frame,
            textvariable=self.ambiente_var,
            values=["Homologação", "Produção"],
            state='readonly',
            width=27
        )
        self.nfe_ambiente.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Certificado Digital
        tk.Label(content_frame, text="Certificado:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky='w')
        
        # Frame para o campo de certificado e botão
        cert_frame = tk.Frame(content_frame, bg='#f0f2f5')
        cert_frame.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        
        self.nfe_certificado = tk.Entry(cert_frame, **entry_style)
        self.nfe_certificado.pack(side='left', fill='x', expand=True)
        
        btn_procurar = tk.Button(
            cert_frame, 
            text="...", 
            font=('Arial', 9, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            width=3,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white',
            command=lambda: self._selecionar_arquivo(self.nfe_certificado)
        )
        btn_procurar.pack(side='right', padx=(5, 0))
        
        # Senha do Certificado
        tk.Label(content_frame, text="Senha do Certificado:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.nfe_senha = tk.Entry(content_frame, show="*", **entry_style)
        self.nfe_senha.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        
        # Frame para os botões
        btn_frame = tk.Frame(content_frame, bg='#f0f2f5', pady=20)
        btn_frame.grid(row=5, column=0, columnspan=2, sticky='e')
        
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
            activebackground='#43a047',
            activeforeground='white',
            command=self._salvar_nfe
        )
        btn_salvar.pack(side='right', padx=5)
        
        # Botão Cancelar - Vermelho
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
            activebackground='#d32f2f',
            activeforeground='white',
            command=self._show_default
        )
        btn_cancelar.pack(side='right')
        
        # Ajusta o grid para expandir corretamente
        form_frame.columnconfigure(1, weight=1)
    
    def _salvar_nfe(self):
        """Salva as configurações de NF-e"""
        try:
            # Obter os valores dos campos
            serie = self.nfe_serie.get().strip()
            ambiente = self.ambiente_var.get()
            certificado = self.nfe_certificado.get().strip()
            senha = self.nfe_senha.get()
            
            # Validações básicas
            if not serie:
                messagebox.showwarning("Atenção", "O campo Série é obrigatório!")
                self.nfe_serie.focus_set()
                return
                
            if not certificado:
                messagebox.showwarning("Atenção", "O campo Certificado Digital é obrigatório!")
                self.nfe_certificado.focus_set()
                return
                
            try:
                # Prepara os dados para salvar
                dados = {
                    'serie': serie,
                    'ambiente': ambiente.lower(),
                    'certificado': certificado,
                    'senha': senha
                }
                
                # Salva as configurações
                if self.ctrl.salvar_config_nfe(dados):
                    messagebox.showinfo("Sucesso", "Configurações de NF-e salvas com sucesso!")
                else:
                    messagebox.showerror("Erro", "Não foi possível salvar as configurações.")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar as configurações: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")
    
    def _show_backup(self):
        # Limpa o frame atual
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
            
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DE BACKUP", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Frame do formulário
        form_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=120, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Configura o grid para expandir
        form_frame.columnconfigure(1, weight=1)
        
        # Carrega as configurações salvas
        config_backup = self.ctrl.carregar_config_backup()
        
        # Estilo dos labels e campos
        label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w', 'fg': '#000000'}
        entry_style = {'font': ('Arial', 10), 'width': 30, 'bg': 'white', 'borderwidth': 0, 'highlightthickness': 0}
        
        # Pasta de Backup
        tk.Label(form_frame, text="Pasta de Backup:", **label_style).grid(row=0, column=0, sticky='w', pady=5)
        
        # Frame para o campo de pasta
        pasta_frame = tk.Frame(form_frame, bg='#f0f2f5')
        pasta_frame.grid(row=0, column=1, sticky='ew', pady=5)
        pasta_frame.columnconfigure(0, weight=1)
        
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
            command=lambda: self._selecionar_pasta(self.backup_pasta)
        )
        btn_pasta.pack(side='right', padx=(5, 0))
        
        # Frequência de backup
        tk.Label(form_frame, text="Frequência:", **label_style).grid(row=1, column=0, sticky='w', pady=5)
        
        # Frame para o combobox
        freq_frame = tk.Frame(form_frame, bg='#f0f2f5')
        freq_frame.grid(row=1, column=1, sticky='w', pady=5)
        
        freq_padrao = config_backup.get('frequencia', 'Diário').capitalize()
        self.backup_frequencia = ttk.Combobox(
            freq_frame,
            values=["Diário", "Semanal", "Mensal"],
            state='readonly',
            width=22
        )
        self.backup_frequencia.set(freq_padrao)
        self.backup_frequencia.pack()
        
        # Manter últimos X backups
        tk.Label(form_frame, text="Manter últimos (dias):", **label_style).grid(row=2, column=0, sticky='w', pady=5)
        
        # Frame para o campo de dias
        dias_frame = tk.Frame(form_frame, bg='#f0f2f5')
        dias_frame.grid(row=2, column=1, sticky='ew', pady=5)
        dias_frame.columnconfigure(0, weight=1)
        
        manter_padrao = config_backup.get('manter_ultimos', '30')
        self.backup_manter = tk.Entry(dias_frame, **entry_style)
        self.backup_manter.insert(0, manter_padrao)
        self.backup_manter.pack(fill='x', expand=True)
        
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
        
        # Define a visualização atual
        self.current_view = main_frame
    
    def _executar_backup(self):
        """Executa o backup imediatamente após confirmação"""
        pasta_backup = self.backup_pasta.get()
        if not pasta_backup:
            messagebox.showwarning("Aviso", "Selecione uma pasta para salvar o backup.")
            return
            
        # Mostra confirmação antes de executar o backup
        confirmacao = messagebox.askyesno(
            "Confirmar Backup",
            f"Deseja realmente executar o backup agora?\n\n"
            f"Local: {pasta_backup}\n"
            "Esta ação pode demorar alguns instantes.",
            icon='question'
        )
        
        if confirmacao:
            if self.ctrl.fazer_backup_banco_dados(pasta_backup):
                messagebox.showinfo("Sucesso", "Backup executado com sucesso!")
            else:
                messagebox.showerror("Erro", "Não foi possível executar o backup. Verifique o log para mais detalhes.")
        else:
            messagebox.showinfo("Cancelado", "Operação de backup cancelada pelo usuário.")
    
    def _restaurar_backup(self):
        """Abre uma janela para selecionar e restaurar um arquivo de backup"""
        # Abre o diálogo para selecionar o arquivo de backup
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo de backup",
            filetypes=[("Arquivos SQL", "*.sql"), ("Todos os arquivos", "*.*")]
        )
        
        if not arquivo:
            return  # Usuário cancelou
            
        # Mostra confirmação antes de restaurar
        confirmacao = messagebox.askyesno(
            "Confirmar Restauração",
            f"ATENÇÃO: Esta operação irá SOBRESCREVER todos os dados atuais do banco.\n\n"
            f"Deseja realmente restaurar o backup?\n\n"
            f"Arquivo: {arquivo}",
            icon='warning'
        )
        
        if confirmacao:
            if self.ctrl.restaurar_backup_banco_dados(arquivo):
                messagebox.showinfo("Sucesso", "Backup restaurado com sucesso!")
            else:
                messagebox.showerror("Erro", "Não foi possível restaurar o backup. Verifique o log para mais detalhes.")
    
    def _salvar_backup(self):
        """Salva as configurações de backup e pergunta se deseja executar o backup"""
        pasta_backup = self.backup_pasta.get()
        if not pasta_backup:
            messagebox.showwarning("Aviso", "Selecione uma pasta para salvar o backup.")
            return
            
        dados = {
            'pasta': pasta_backup,
            'frequencia': self.backup_frequencia.get().lower(),
            'manter_ultimos': self.backup_manter.get()
        }
        
        if self.ctrl.salvar_config_backup(dados):
            messagebox.showinfo("Sucesso", "Configurações de backup salvas com sucesso!")
            
            if messagebox.askyesno("Backup", "Deseja criar um arquivo de backup agora?"):
                self._executar_backup()
    
    def criar_linha_impressora(self, parent, label_text, row, impressoras, valor_padrao=''):
        """
        Cria uma linha de configuração de impressora com um combobox e um botão de teste.
        
        Args:
            parent: Widget pai
            label_text: Texto do label
            row: Linha do grid
            impressoras: Lista de impressoras disponíveis
            valor_padrao: Valor padrão a ser selecionado
            
        Returns:
            ttk.Combobox: O combobox criado
        """
        ttk.Label(
            parent,
            text=label_text,
            font=('Arial', 9, 'bold'),
            background='#f0f2f5'
        ).grid(row=row, column=0, sticky='w', padx=5, pady=2)
        
        # Cria um nome único para a variável de controle
        var_name = f"var_{label_text.lower().replace(' ', '_').replace(':', '')}"
        
        # Cria a variável de controle como atributo da instância
        setattr(self, var_name, tk.StringVar(value=valor_padrao))
        var = getattr(self, var_name)
        
        style = ttk.Style()
        
        # Configura o estilo do combobox
        style.configure('TCombobox',
                      fieldbackground='white',
                      background='white',
                      foreground='black',
                      selectbackground='white',
                      selectforeground='black')
        
        # Configura o estilo do dropdown
        style.map('TCombobox',
                 fieldbackground=[('readonly', 'white')],
                 selectbackground=[('readonly', 'white')],
                 selectforeground=[('readonly', 'black')],
                 background=[('readonly', 'white')],
                 foreground=[('readonly', 'black')])
        
        # Cria o combobox
        combobox = ttk.Combobox(
            parent,
            textvariable=var,
            values=impressoras,
            state='readonly',
            width=50,
            font=('Arial', 9),
            style='TCombobox'
        )
        
        # Aplica o estilo ao dropdown
        combobox['style'] = 'TCombobox'
        combobox.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
        
        # Se não houver valor padrão e houver impressoras disponíveis, define a primeira
        if not valor_padrao and impressoras and impressoras[0] != "Nenhuma impressora disponível":
            combobox.set(impressoras[0])
        # Se houver valor padrão, tenta defini-lo
        elif valor_padrao:
            combobox.set(valor_padrao)
        
        # Botão para testar a impressão - Azul padrão
        btn_testar = tk.Button(
            parent,
            text="Testar",
            font=('Arial', 9, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            padx=10,
            pady=3,
            relief='flat',
            cursor='hand2',
            command=lambda: self._testar_impressao(combobox.get())
        )
        btn_testar.grid(row=row, column=2, padx=5, pady=2, sticky='e')
        

        
        return combobox
    
    def _show_impressoras(self):
        """Exibe a tela de configuração de impressoras"""
        # Limpa o frame de conteúdo
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
            
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DE IMPRESSORAS", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Frame do formulário
        frame = tk.Frame(main_frame, bg='#f0f2f5', padx=120, pady=20)
        frame.pack(fill='both', expand=True)
        
        # Configura o grid para expandir
        frame.columnconfigure(1, weight=1)
        
        try:
            # Título da seção
            tk.Label(
                frame, 
                text="Configuração de Impressoras",
                font=('Arial', 12, 'bold'),
                bg='#f0f2f5',
                fg='#000000'
            ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
            
            # Obtém a lista de impressoras disponíveis
            impressoras = self.ctrl.listar_impressoras()
            
            # Verifica se a lista de impressoras está vazia
            if not impressoras or (len(impressoras) == 1 and impressoras[0].startswith("Erro")):
                tk.Label(
                    frame,
                    text=impressoras[0] if impressoras else "Nenhuma impressora encontrada",
                    font=('Arial', 10),
                    bg='#f0f2f5',
                    fg='#dc3545' if impressoras and impressoras[0].startswith("Erro") else '#6c757d'
                ).grid(row=1, column=0, columnspan=3, pady=10, sticky='w')
                impressoras = ["Nenhuma impressora disponível"]
            else:
                # Exibe a lista de impressoras encontradas
                tk.Label(
                    frame,
                    text=f"Foram encontradas {len(impressoras)} impressoras no sistema:",
                    font=('Arial', 10),
                    bg='#f0f2f5',
                    fg='#000000'  # Texto preto
                ).grid(row=1, column=0, columnspan=3, pady=(10, 5), sticky='w')
                
                # Lista de impressoras em um frame sem bordas
                list_frame = tk.Frame(frame, bg='white', bd=0)
                list_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15), sticky='nsew')
                
                # Cria um texto para mostrar as impressoras com fundo branco e sem bordas
                printer_list = tk.Text(
                    list_frame,
                    height=6,
                    wrap=tk.WORD,
                    font=('Arial', 9),
                    padx=10,
                    pady=10,
                    bg='white',
                    fg='#000000',
                    bd=0,
                    highlightthickness=0
                )
                
                for i, impressora in enumerate(impressoras, 1):
                    printer_list.insert(tk.END, f"{i}. {impressora}\n")
                
                printer_list.config(state='disabled')
                printer_list.pack(fill='both', expand=True)
            
            # Carrega as configurações salvas
            config_salva = self.ctrl.carregar_config_impressoras()
            
            # Impressora de Cupom Fiscal
            row_start = 3
            tk.Label(frame, 
                    text="Configurar Impressoras por Finalidade", 
                    font=('Arial', 12, 'bold'),
                    bg='#f0f2f5',
                    fg='#000000').grid(
                row=row_start, column=0, columnspan=3, pady=(30, 15), sticky='w'
            )
            
            self.imp_impressora1 = self.criar_linha_impressora(
                frame, "impressora 1:", row_start+1, impressoras,
                config_salva.get('impressora 1', '')
            )
           
            self.imp_impressora2 = self.criar_linha_impressora(
                frame, "impressora 2:", row_start+2, impressoras,
                config_salva.get('impressora 2', '')
            )

            self.imp_impressora3 = self.criar_linha_impressora(
                frame, "impressora 3:", row_start+3, impressoras,
                config_salva.get('impressora 3', '')
            )

            self.imp_impressora4 = self.criar_linha_impressora(
                frame, "impressora 4:", row_start+4, impressoras,
                config_salva.get('impressora 4', '')
            )

            self.imp_impressora5 = self.criar_linha_impressora(
                frame, "impressora 5:", row_start+5, impressoras,
                config_salva.get('impressora 5', '')
            )   
            
            # Configura o tamanho da fonte
            tk.Label(
                frame,
                text="Tamanho da Fonte:",
                font=('Arial', 9, 'bold'),
                bg='#f0f2f5',
                fg='#000000'
            ).grid(row=row_start+6, column=0, sticky='w', padx=5, pady=(15, 5))
            
            # Define o valor padrão para o tamanho da fonte
            tamanho_padrao = str(config_salva.get('tamanho_fonte', '12'))
            
            self.imp_tamanho_fonte = ttk.Combobox(
                frame,
                values=["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24"],
                state='readonly',
                width=10,
                font=('Arial', 9)
            )
            self.imp_tamanho_fonte.grid(row=row_start+6, column=1, sticky='w', padx=5, pady=(15, 5))
            
            # Define o valor salvo ou o padrão
            if tamanho_padrao in self.imp_tamanho_fonte['values']:
                self.imp_tamanho_fonte.set(tamanho_padrao)
            else:
                self.imp_tamanho_fonte.set("12")
            
            # Label para exibir status
            self.status_label = tk.Label(
                frame,
                text="",
                font=('Arial', 9),
                foreground="black"
            )
            self.status_label.grid(row=row_start+7, column=0, columnspan=3, pady=(5, 0), sticky='w')
            
            # Frame para os botões
            btn_frame = tk.Frame(frame, bg='#f0f2f5', pady=20)
            btn_frame.grid(row=row_start+8, column=0, columnspan=3, sticky='e')
            
            # Frame para os botões à esquerda
            left_btns = tk.Frame(btn_frame, bg='#f0f2f5')
            left_btns.pack(side='left')
            
            # Botão para testar impressão - Azul padrão
            btn_testar = tk.Button(
                left_btns,
                text="Testar Impressão",
                font=('Arial', 10, 'bold'),
                bg='#4a6fa5',
                fg='white',
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
                activebackground='#3b5a7f',
                activeforeground='white',
                command=self._testar_impressao
            )
            btn_testar.pack(side='left', padx=5)
            
            # Botão para atualizar a lista de impressoras - Cinza
            btn_atualizar = tk.Button(
                left_btns,
                text="Atualizar Lista",
                font=('Arial', 10, 'bold'),
                bg='#6c757d',
                fg='white',
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
                activebackground='#5a6268',
                activeforeground='white',
                command=self._show_impressoras
            )
            btn_atualizar.pack(side='left', padx=5)
            
            # Frame para o botão à direita
            right_btns = tk.Frame(btn_frame, bg='#f0f2f5')
            right_btns.pack(side='right')
            
            # Botão para salvar configurações - Verde
            btn_salvar = tk.Button(
                right_btns,
                text="Salvar Configurações",
                font=('Arial', 10, 'bold'),
                bg='#28a745',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                activebackground='#218838',
                activeforeground='white',
                command=self._salvar_impressoras
            )
            btn_salvar.pack(side='right', padx=5)
            
        except Exception as e:
            print(f"Erro ao carregar configurações de impressoras: {e}")
            ttk.Label(
                frame,
                text=f"Erro ao carregar as configurações de impressão: {str(e)}",
                foreground="red"
            ).pack(pady=20)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
    def _testar_impressao(self, impressora_selecionada=None):
        """
        Testa a impressão na impressora selecionada
        
        Args:
            impressora_selecionada (str, optional): Nome da impressora para teste. 
                Se não informado, usará a impressora de cupom fiscal.
        """
        try:
            # Se não foi especificada uma impressora, usa a do cupom fiscal
            if not impressora_selecionada:
                if hasattr(self, 'imp_cupom') and self.imp_cupom.get():
                    impressora_selecionada = self.imp_cupom.get()
                else:
                    messagebox.showwarning("Aviso", "Nenhuma impressora de cupom fiscal selecionada.")
                    return
            
            # Exibe mensagem de processamento
            self.status_label.config(
                text=f"Enviando teste para {impressora_selecionada}...",
                foreground="blue"
            )
            self.parent.update()
            
            # Obtém o tamanho da fonte configurado
            tamanho_fonte = '12'  # Valor padrão
            if hasattr(self, 'imp_tamanho_fonte') and self.imp_tamanho_fonte.get():
                tamanho_fonte = self.imp_tamanho_fonte.get()
            
            # Executa o teste de impressão com o tamanho da fonte
            if self.ctrl.testar_impressora(impressora_selecionada, tamanho_fonte):
                self.status_label.config(
                    text=f"Teste enviado para {impressora_selecionada} com sucesso!",
                    foreground="green"
                )
                messagebox.showinfo(
                    "Sucesso",
                    f"Teste de impressão enviado para:\n{impressora_selecionada}\nTamanho da fonte: {tamanho_fonte}pt"
                )
                
        except Exception as e:
            self.status_label.config(
                text=f"Erro ao testar impressora: {str(e)}",
                foreground="red"
            )
            messagebox.showerror(
                "Erro",
                f"Falha ao testar impressora {impressora_selecionada}:\n{str(e)}"
            )
    
    def _salvar_impressoras(self):
        """
        Salva as configurações das impressoras no banco de dados
        """
        try:
            # Coleta os dados das impressoras
            dados = {
                'impressora 1': self.imp_impressora1.get() if hasattr(self, 'imp_impressora1') else '',
                'impressora 2': self.imp_impressora2.get() if hasattr(self, 'imp_impressora2') else '',
                'impressora 3': self.imp_impressora3.get() if hasattr(self, 'imp_impressora3') else '',
                'impressora 4': self.imp_impressora4.get() if hasattr(self, 'imp_impressora4') else '',
                'impressora 5': self.imp_impressora5.get() if hasattr(self, 'imp_impressora5') else '',
                'tamanho_fonte': self.imp_tamanho_fonte.get() if hasattr(self, 'imp_tamanho_fonte') else '12'
            }
            
            # Valida se pelo menos uma impressora foi configurada
            impressoras_configuradas = [
                v for k, v in dados.items() 
                if k != 'tamanho_fonte' and v and v != 'Nenhuma impressora disponível'
            ]
            
            if not impressoras_configuradas:
                messagebox.showwarning(
                    "Aviso",
                    "Nenhuma impressora configurada. Por favor, selecione pelo menos uma impressora."
                )
                return
            
            # Atualiza o status
            self.status_label.config(
                text="Salvando configurações de impressão...",
                foreground="blue"
            )
            self.parent.update()
            
            # Salva as configurações
            if self.ctrl.salvar_config_impressoras(dados):
                self.status_label.config(
                    text="Configurações de impressão salvas com sucesso!",
                    foreground="green"
                )
                messagebox.showinfo(
                    "Sucesso",
                    "Configurações de impressão salvas com sucesso!"
                )
            else:
                raise Exception("Falha ao salvar as configurações no banco de dados.")
                
        except Exception as e:
            self.status_label.config(
                text=f"Erro ao salvar configurações: {str(e)}",
                foreground="red"
            )
            messagebox.showerror(
                "Erro",
                f"Não foi possível salvar as configurações de impressão:\n{str(e)}"
            )
    
    def _testar_conexao_db(self):
        """Testa a conexão com o banco de dados"""
        # Obtém os valores dos campos
        host = self.db_host.get().strip()
        porta = self.db_porta.get().strip()
        usuario = self.db_usuario.get().strip()
        senha = self.db_senha.get()
        banco = self.db_nome.get().strip()
        
        # Atualiza o botão para mostrar que está testando
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Button) and 'Testar' in widget['text']:
                widget.config(state=tk.DISABLED, text="Testando...")
                break
        
        try:
            # Atualiza a interface para o usuário
            self.frame.update_idletasks()
            
            # Testa a conexão diretamente (sem thread)
            sucesso = self.ctrl.testar_conexao_banco_dados(
                host, porta, usuario, senha, banco
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", "✅ Conexão com o banco de dados realizada com sucesso!")
            else:
                messagebox.showerror("Erro", "Falha ao conectar ao banco de dados.")
                
        except Exception as error:
            messagebox.showerror("Erro", f"Erro ao testar conexão: {str(error)}")
        finally:
            # Restaura o botão
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Button) and 'Testar' in widget['text']:
                    widget.config(state=tk.NORMAL, text="Testar Conexão")
                    break
    
    def _fazer_backup_db(self):
        """Inicia o backup do banco de dados"""
        destino = filedialog.askdirectory(title="Selecionar pasta para salvar o backup")
        if destino and self.ctrl.fazer_backup_banco_dados(destino):
            messagebox.showinfo("Sucesso", "Backup do banco de dados realizado com sucesso!")
    
    def _restaurar_backup_db(self):
        """Restaura um backup do banco de dados"""
        filename = filedialog.askopenfilename(
            title="Selecione Arquivo de Backup",
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
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DO BANCO DE DADOS", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Frame do formulário com padding maior nas laterais para centralizar
        form_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=200, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Estilo dos labels e campos
        label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w', 'fg': '#000000'}
        entry_style = {'font': ('Arial', 10), 'width': 30, 'bg': 'white', 'borderwidth': 0, 'highlightthickness': 0}
        
        # Frame para o conteúdo
        content_frame = tk.Frame(form_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True)
        
        # Configura o grid
        content_frame.columnconfigure(1, weight=1, minsize=300)  # Coluna dos campos
        
        try:
            # Carrega as configurações atuais do banco de dados
            config = self.ctrl.carregar_config_banco_dados()
            
            # Título da seção
            tk.Label(content_frame, text="Conexão com o Banco de Dados", 
                    font=('Arial', 12, 'bold'), 
                    bg='#f0f2f5').grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            
            # Servidor
            tk.Label(content_frame, text="Servidor:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky='w')
            self.db_host = tk.Entry(content_frame, **entry_style)
            self.db_host.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
            self.db_host.insert(0, config.get('host', 'localhost'))
            
            # Porta
            tk.Label(content_frame, text="Porta:", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky='w')
            self.db_porta = tk.Entry(content_frame, **entry_style)
            self.db_porta.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
            self.db_porta.insert(0, str(config.get('porta', '3306')))
            
            # Usuário
            tk.Label(content_frame, text="Usuário:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky='w')
            self.db_usuario = tk.Entry(content_frame, **entry_style)
            self.db_usuario.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
            self.db_usuario.insert(0, config.get('usuario', 'postgres'))
            
            # Senha
            tk.Label(content_frame, text="Senha:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky='w')
            self.db_senha = tk.Entry(content_frame, show="*", **entry_style)
            self.db_senha.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
            self.db_senha.insert(0, config.get('senha', ''))
            
            # Nome do Banco
            tk.Label(content_frame, text="Nome do Banco:", **label_style).grid(row=5, column=0, padx=10, pady=5, sticky='w')
            self.db_nome = tk.Entry(content_frame, **entry_style)
            self.db_nome.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
            self.db_nome.insert(0, config.get('nome_bd', 'pdv_aquarius'))
            
            # Frame para os botões
            btn_frame = tk.Frame(content_frame, bg='#f0f2f5', pady=20)
            btn_frame.grid(row=6, column=0, columnspan=2, sticky='e')
            
            # Botão Testar Conexão - Azul
            btn_teste = tk.Button(
                btn_frame,
                text="Testar Conexão",
                font=('Arial', 10, 'bold'),
                bg='#4a6fa5',
                fg='white',
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
                activebackground='#3b5a7f',
                activeforeground='white',
                command=self._testar_conexao_db
            )
            btn_teste.pack(side='left', padx=5)
            
            # Botão Salvar Configurações - Verde
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
                activebackground='#43a047',
                activeforeground='white',
                command=self._salvar_banco_dados
            )
            btn_salvar.pack(side='left', padx=5)
            
            # Atualiza a visualização atual
            self.current_view = main_frame
            
        except Exception as e:
            print(f"Erro ao carregar configurações do banco de dados: {e}")
            tk.Label(
                main_frame,
                text=f"Erro ao carregar as configurações do banco de dados: {str(e)}",
                fg='red',
                bg='#f0f2f5',
                font=('Arial', 10)
            ).pack(pady=20)
    
    def _show_integracoes(self):
        # Tela de configuração de Integrações
        if hasattr(self, 'current_view') and self.current_view:
            self.current_view.destroy()
            
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DE INTEGRAÇÕES", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Frame do formulário com padding maior nas laterais para centralizar
        form_frame = tk.Frame(main_frame, bg='#f0f2f5', padx=200, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Estilo dos labels e campos
        label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w', 'fg': '#000000'}
        entry_style = {'font': ('Arial', 10), 'width': 30, 'bg': 'white', 'borderwidth': 0, 'highlightthickness': 0}
        
        # Frame para o conteúdo
        content_frame = tk.Frame(form_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True)
        
        # Configura o grid
        content_frame.columnconfigure(1, weight=1, minsize=300)  # Coluna dos campos
        
        try:
            # Carrega as configurações atuais das integrações
            config = self.ctrl.carregar_config_integracoes()
            
            # Seção de Integração com ERP
            tk.Label(content_frame, text="Sistema ERP", 
                    font=('Arial', 12, 'bold'), 
                    bg='#f0f2f5').grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')
            
            # Checkbox Ativar ERP
            self.erp_ativo = tk.BooleanVar(value=config.get('erp', {}).get('ativo', False))
            chk_erp = tk.Checkbutton(
                content_frame, 
                text="Ativar integração com ERP",
                variable=self.erp_ativo,
                font=('Arial', 10),
                bg='#f0f2f5',
                activebackground='#f0f2f5',
                selectcolor='#f0f2f5'
            )
            chk_erp.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='w')
            
            # URL do ERP
            tk.Label(content_frame, text="URL do ERP:", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky='w')
            self.erp_url = tk.Entry(content_frame, **entry_style)
            self.erp_url.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
            self.erp_url.insert(0, config.get('erp', {}).get('url', 'https://erp.empresa.com.br/api'))
            
            # Token de Acesso
            tk.Label(content_frame, text="Token de Acesso:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky='w')
            self.erp_token = tk.Entry(content_frame, **entry_style)
            self.erp_token.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
            self.erp_token.insert(0, config.get('erp', {}).get('token', ''))
            
            # Separador
            ttk.Separator(content_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, pady=20, sticky='ew')
            
            # Seção de E-commerce
            tk.Label(content_frame, text="E-commerce", 
                    font=('Arial', 12, 'bold'), 
                    bg='#f0f2f5').grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky='w')
            
            # Checkbox Ativar E-commerce
            self.ecommerce_ativo = tk.BooleanVar(value=config.get('ecommerce', {}).get('ativo', False))
            chk_ecommerce = tk.Checkbutton(
                content_frame, 
                text="Ativar integração com E-commerce",
                variable=self.ecommerce_ativo,
                font=('Arial', 10),
                bg='#f0f2f5',
                activebackground='#f0f2f5',
                selectcolor='#f0f2f5'
            )
            chk_ecommerce.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky='w')
            
            # Plataforma
            tk.Label(content_frame, text="Plataforma:", **label_style).grid(row=7, column=0, padx=10, pady=5, sticky='w')
            
            plataformas = ["Nenhuma", "Loja Integrada", "Nuvemshop", "Outra"]
            plataforma_atual = config.get('ecommerce', {}).get('plataforma', 'Nenhuma')
            if plataforma_atual not in plataformas:
                plataformas.append(plataforma_atual)
                
            self.ecommerce_plataforma = ttk.Combobox(
                content_frame,
                values=plataformas,
                state='readonly',
                font=('Arial', 10),
                width=27
            )
            self.ecommerce_plataforma.set(plataforma_atual)
            self.ecommerce_plataforma.grid(row=7, column=1, padx=10, pady=5, sticky='w')
            
            # Frame para os botões
            btn_frame = tk.Frame(content_frame, bg='#f0f2f5', pady=20)
            btn_frame.grid(row=8, column=0, columnspan=2, sticky='e')
            
            # Botão Salvar Configurações - Verde
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
                activebackground='#43a047',
                activeforeground='white',
                command=self._salvar_integracoes
            )
            btn_salvar.pack(side='right', padx=5)
            
            # Atualiza a visualização atual
            self.current_view = main_frame
            
        except Exception as e:
            print(f"Erro ao carregar configurações de integrações: {e}")
            tk.Label(
                main_frame,
                text=f"Erro ao carregar as configurações de integrações: {str(e)}",
                fg='red',
                bg='#f0f2f5',
                font=('Arial', 10)
            ).pack(pady=20)
    
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
    
    def _salvar_permissoes(self):
        """Salva as permissões alteradas"""
        try:
            # Cria uma cópia das permissões sem as variáveis Tkinter
            permissoes_para_salvar = {
                'modulos': {}
            }
            
            # Atualiza as permissões no gerenciador
            for modulo_id, modulo_data in self.permissoes['modulos'].items():
                permissoes_para_salvar['modulos'][modulo_id] = {
                    'nome': modulo_data['nome'],
                    'botoes': {}
                }
                
                for botao_id, botao_data in modulo_data['botoes'].items():
                    # Verifica se existem variáveis para este botão
                    if 'variaveis' in modulo_data and botao_id in modulo_data['variaveis']:
                        # Usa os valores das variáveis Tkinter
                        permissoes_para_salvar['modulos'][modulo_id]['botoes'][botao_id] = {
                            'nome': botao_data['nome'],
                            'basico': modulo_data['variaveis'][botao_id]['basico'].get(),
                            'master': modulo_data['variaveis'][botao_id]['master'].get()
                        }
                    else:
                        # Usa os valores padrão se não houver variáveis
                        permissoes_para_salvar['modulos'][modulo_id]['botoes'][botao_id] = {
                            'nome': botao_data['nome'],
                            'basico': botao_data.get('basico', False),
                            'master': botao_data.get('master', True)
                        }
            
            # Usa o PermissionController para salvar as permissões
            if self.permission_ctrl.salvar_todas_permissoes(permissoes_para_salvar):
                # Mostra mensagem de sucesso
                messagebox.showinfo("Sucesso", "Permissões salvas com sucesso!")
                
                # Recarrega a tela de segurança para garantir que os checkboxes estejam corretos
                self._show_seguranca()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar as permissões.")
                
        except Exception as e:
            print(f"Erro ao salvar permissões: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar permissões: {str(e)}")
        
    def _show_seguranca(self):
        # Tela de configuração de Segurança
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            self.frame = ttk.Frame(self.parent)
        
        # Limpa o frame atual
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
            
        # Frame principal
        main_frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Frame do título
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        # Título centralizado
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÕES DE SEGURANÇA", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='top', fill='x')
        
        # Subtítulo explicativo
        tk.Label(
            title_frame,
            text="Defina as permissões de acesso para cada tipo de usuário do sistema",
            font=('Arial', 10),
            bg='#f0f2f5',
            fg='#666666'
        ).pack(side='top', fill='x', pady=(5, 0))
        
        try:
            # Importa o gerenciador de permissões
            from src.utils.gerenciador_permissoes_db import GerenciadorPermissoesDB
            self.gerenciador_permissoes = GerenciadorPermissoesDB()
            self.permissoes = self.gerenciador_permissoes.obter_todas_permissoes()
            
            # Dicionário para armazenar o módulo atualmente selecionado
            self.modulo_selecionado = None
            
            # Container principal
            content_frame = tk.Frame(main_frame, bg='#f0f2f5')
            content_frame.pack(fill='both', expand=True, pady=10)
            
            # Layout principal com dois frames lado a lado
            main_layout = tk.Frame(content_frame, bg='#f0f2f5')
            main_layout.pack(fill='both', expand=True)
            
            # Frame esquerdo para os botões de módulos (fundo cinza)
            botoes_frame = tk.Frame(main_layout, bg='#f0f2f5', width=200)
            botoes_frame.pack(side='left', fill='y', padx=(0, 10))
            botoes_frame.pack_propagate(False)  # Mantém o tamanho fixo
            
            # Título dos módulos
            tk.Label(
                botoes_frame,
                text="Módulos",
                font=('Arial', 11, 'bold'),
                bg='#f0f2f5',
                fg='#000000',
                pady=10
            ).pack(fill='x', padx=5)
            
            # Frame direito para o conteúdo (container branco)
            conteudo_container = tk.Frame(main_layout, bg='#f0f2f5')
            conteudo_container.pack(side='right', fill='both', expand=True)
            
            # Container branco para exibir as permissões do módulo selecionado
            container_frame = tk.Frame(conteudo_container, bg='white', bd=1, relief='solid')
            container_frame.pack(fill='both', expand=True)
            
            # Frame principal para os cabeçalhos (não expansível)
            header_frame = tk.Frame(container_frame, bg='white')
            header_frame.pack(fill='x')
            
            # Frame interno para o conteúdo do cabeçalho
            header_content = tk.Frame(header_frame, bg='white', padx=15, pady=8)
            header_content.pack(fill='x')
            
            # Configuração fixa das colunas (sem weight)
            header_content.columnconfigure(0, minsize=300)  # Nome do botão
            header_content.columnconfigure(1, minsize=120)  # Usuário Master
            header_content.columnconfigure(2, minsize=120)  # Usuário Básico
            
            # Título da coluna de permissões (esquerda)
            tk.Label(
                header_content,
                text="Permissões",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#000000',
                anchor='w',
                padx=10
            ).grid(row=0, column=0, sticky='w')
            
            # Cabeçalho Usuário Master (centralizado)
            tk.Label(
                header_content,
                text="Medico",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#000000',
                width=18,
                anchor='center'
            ).grid(row=0, column=1, padx=0)
            
            # Cabeçalho Usuário Básico (centralizado)
            tk.Label(
                header_content,
                text="Funcionario",
                font=('Arial', 11, 'bold'),
                bg='white',
                fg='#000000',
                width=18,
                anchor='center'
            ).grid(row=0, column=2, padx=0)
            
            # Separador horizontal
            ttk.Separator(container_frame, orient='horizontal').pack(fill='x', padx=10)
            
            # Cria um canvas com barra de rolagem para o container
            canvas = tk.Canvas(container_frame, highlightthickness=0, bg='white')
            scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')
            
            # Configura o canvas para rolagem
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            # Cria uma janela no canvas para o frame rolável
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Empacota o canvas e a scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Dicionário para armazenar os frames de conteúdo de cada módulo
            self.modulo_frames = {}
            
            # Função para mostrar o conteúdo de um módulo
            def mostrar_modulo(modulo_id):
                # Esconde todos os frames de módulos
                for frame in self.modulo_frames.values():
                    frame.pack_forget()
                
                # Mostra o frame do módulo selecionado
                if modulo_id in self.modulo_frames:
                    self.modulo_frames[modulo_id].pack(fill='both', expand=True, padx=10, pady=10)
                    self.modulo_selecionado = modulo_id
            
            # Cria os frames de conteúdo para cada módulo (inicialmente ocultos)
            for modulo_id, modulo_data in self.permissoes['modulos'].items():
                # Inicializa o dicionário de variáveis para este módulo
                if 'variaveis' not in modulo_data:
                    modulo_data['variaveis'] = {}
                
                # Cria um frame para o conteúdo do módulo
                modulo_frame = tk.Frame(scrollable_frame, bg='white')
                self.modulo_frames[modulo_id] = modulo_frame
                
                # Adiciona os botões do módulo ao frame
                for botao_id, botao_data in modulo_data['botoes'].items():
                    # Garante que os valores sejam booleanos
                    valor_basico = bool(botao_data.get('basico', False))
                    valor_master = bool(botao_data.get('master', True))
                    
                    # Cria as variáveis para os checkboxes com os valores corretos
                    var_basico = tk.BooleanVar(value=valor_basico)
                    var_master = tk.BooleanVar(value=valor_master)
                    
                    # Armazena as variáveis para uso posterior
                    modulo_data['variaveis'][botao_id] = {
                        'basico': var_basico,
                        'master': var_master
                    }
                    
                    # Frame para a linha do botão
                    botao_frame = tk.Frame(modulo_frame, bg='white')
                    botao_frame.pack(fill='x', pady=5)
                    
                    # Configuração do grid para os itens do botão
                    botao_frame.columnconfigure(0, minsize=300)  # Nome do botão (largura fixa)
                    botao_frame.columnconfigure(1, minsize=120, weight=1)  # Usuário Master
                    botao_frame.columnconfigure(2, minsize=120, weight=1)  # Usuário Básico
                    
                    # Nome do botão
                    tk.Label(
                        botao_frame,
                        text=botao_data['nome'],
                        bg='white',
                        fg='#000000',
                        anchor='w',
                        width=30,
                        padx=10
                    ).grid(row=0, column=0, sticky='w')
                    
                    # Frame para centralizar o checkbox do usuário master
                    master_frame = tk.Frame(botao_frame, bg='white', width=180)
                    master_frame.grid(row=0, column=1, sticky='nsew')
                    master_frame.grid_propagate(False)
                    master_frame.columnconfigure(0, weight=1)
                    
                    # Checkbox para usuário master
                    check_master = tk.Checkbutton(
                        master_frame,
                        variable=var_master,
                        bg='white',
                        activebackground='white',
                        onvalue=True,
                        offvalue=False,
                        bd=0,
                        highlightthickness=0
                    )
                    check_master.place(relx=0.5, rely=0.5, anchor='center')
                    
                    # Frame para centralizar o checkbox do usuário básico
                    basico_frame = tk.Frame(botao_frame, bg='white', width=180)
                    basico_frame.grid(row=0, column=2, sticky='nsew')
                    basico_frame.grid_propagate(False)
                    basico_frame.columnconfigure(0, weight=1)
                    
                    # Checkbox para usuário básico
                    check_basico = tk.Checkbutton(
                        basico_frame,
                        variable=var_basico,
                        bg='white',
                        activebackground='white',
                        onvalue=True,
                        offvalue=False,
                        bd=0,
                        highlightthickness=0
                    )
                    check_basico.place(relx=0.5, rely=0.5, anchor='center')
            
            # Dicionário para armazenar os botões de módulos
            self.botoes_modulos = {}
            
            # Função para destacar o botão selecionado
            def selecionar_modulo(modulo_id):
                # Restaura a cor de todos os botões
                for mid, botao in self.botoes_modulos.items():
                    botao.config(bg='#2b579a')  # Cor azul igual ao botão "Criar arquivo" do backup
                
                # Destaca o botão selecionado com amarelo
                if modulo_id in self.botoes_modulos:
                    self.botoes_modulos[modulo_id].config(bg='#28b5f4')  # Cor amarela do backup
                
                # Mostra o conteúdo do módulo
                mostrar_modulo(modulo_id)
            
            # Nomes corretos dos módulos na interface
            nomes_modulos = {
                'cadastro': 'Cadastro',  
                'atendimento': 'Atendimento',
                'financeiro': 'Financeiro',
                'configuracao': 'Configuração'
            }
            
            # Cria os botões de módulos no frame esquerdo
            for modulo_id, modulo_data in self.permissoes['modulos'].items():
                # Usa o nome correto do módulo se estiver no dicionário, senão usa o nome original
                nome_modulo = nomes_modulos.get(modulo_id, modulo_data['nome'])
                
                # Cria um botão para o módulo com fundo azul (cor igual ao botão "Criar arquivo" do backup)
                botao_modulo = tk.Button(
                    botoes_frame,
                    text=nome_modulo,
                    font=('Arial', 10),
                    bg='#2b579a',  # Cor azul igual ao botão "Criar arquivo" do backup
                    fg='white',
                    activebackground='#28b5f4',  # Cor amarela ao passar o mouse
                    activeforeground='black',
                    relief='flat',
                    pady=8,
                    width=20,
                    cursor='hand2',
                    command=lambda mid=modulo_id: selecionar_modulo(mid)
                )
                botao_modulo.pack(fill='x', padx=5, pady=2)
                
                # Armazena o botão para referência futura
                self.botoes_modulos[modulo_id] = botao_modulo
            
            # Mostra o primeiro módulo por padrão (se houver algum)
            if self.permissoes['modulos']:
                primeiro_modulo = list(self.permissoes['modulos'].keys())[0]
                selecionar_modulo(primeiro_modulo)
            
            # Frame para os botões
            btn_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=20)
            btn_frame.pack(fill='x')
            
            # Botão Salvar - Verde
            btn_salvar = tk.Button(
                btn_frame,
                text="Salvar Permissões",
                font=('Arial', 10, 'bold'),
                bg='#4CAF50',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                activebackground='#43a047',
                activeforeground='white',
                command=self._salvar_permissoes
            )
            btn_salvar.pack(side='right', padx=5)
            
        except Exception as e:
            print(f"Erro ao carregar tela de permissões: {e}")
            ttk.Label(
                scrollable_frame,
                text=f"Erro ao carregar as configurações de permissões: {str(e)}",
                foreground="red"
            ).grid(row=0, column=0, columnspan=4, pady=20, padx=10)
        
        # Configura o frame rolável para se ajustar ao tamanho do conteúdo
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Configura o canvas para rolagem com o mouse
        canvas.bind_all("<MouseWheel>", 
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        )
        


        self.current_view = main_frame
    def _carregar_permissoes(self):
        """Carrega as permissões usando o PermissionController"""
        try:
            self.permissoes = self.permission_ctrl.obter_todas_permissoes()
            return True
        except Exception as e:
            print(f"Erro ao carregar permissões: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar permissões: {str(e)}")
            return False