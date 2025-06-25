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
            entry.insert(0, folder)
    
    def __init__(self, parent, controller):
        """Inicializa o módulo de configuração."""
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True)  # Adicionando empacotamento do frame
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
        cert_frame = tk.Frame(frame, bg='#f0f2f5')
        cert_frame.grid(row=3, column=1, sticky='ew')
        ttk.Label(frame, text="Certificado:").grid(row=3, column=0, sticky='w', pady=2, padx=5)
        
        self.nfe_certificado = ttk.Entry(cert_frame, width=40)
        self.nfe_certificado.pack(side='left', fill='x', expand=True)
        
        btn_procurar = tk.Button(
            cert_frame, 
            text="...", 
            font=('Arial', 8, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            width=3,
            relief='flat',
            cursor='hand2',
            command=lambda: self._selecionar_arquivo(self.nfe_certificado)
        )
        btn_procurar.pack(side='left', padx=(5, 0))
        
        self.nfe_senha = self._criar_campo(
            frame, "Senha do Certificado:", 4, "", 30
        )
        self.nfe_senha.config(show="*")
        
        # Frame para o botão Salvar
        btn_frame = tk.Frame(frame, bg='#f0f2f5')
        btn_frame.grid(row=5, column=0, columnspan=3, pady=15, sticky='e')
        
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
            command=self._salvar_nfe
        )
        btn_salvar.pack(side='right', padx=5)
        
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
        
        try:
            # Título
            ttk.Label(
                frame, 
                text="Configurações de Backup", 
                font=('Arial', 14, 'bold')
            ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
            
            # Carrega as configurações salvas
            config_backup = self.ctrl.carregar_config_backup()
            
            # Frame para o campo de pasta de backup
            backup_frame = ttk.Frame(frame)
            backup_frame.grid(row=1, column=1, sticky='ew')
            ttk.Label(frame, text="Pasta de Backup:").grid(row=1, column=0, sticky='w', pady=2, padx=5)
            
            self.backup_pasta = ttk.Entry(backup_frame, width=40)
            self.backup_pasta.pack(side='left', fill='x', expand=True)
            
            # Preenche com a pasta salva, se existir
            if config_backup and 'pasta' in config_backup:
                self.backup_pasta.insert(0, config_backup['pasta'])
            
            btn_selecionar = tk.Button(
                backup_frame, 
                text="...", 
                font=('Arial', 8, 'bold'),
                bg='#4a6fa5',
                fg='white',
                bd=0,
                width=3,
                relief='flat',
                cursor='hand2',
                command=lambda: self._selecionar_pasta(self.backup_pasta)
            )
            btn_selecionar.pack(side='left', padx=(5, 0))
            
            # Frequência de backup
            freq_padrao = config_backup.get('frequencia', 'Diário').capitalize()
            self.backup_frequencia = self._criar_combobox(
                frame, "Frequência:", 2,
                ["Diário", "Semanal", "Mensal"], 
                freq_padrao
            )
            
            # Manter últimos X backups
            manter_padrao = config_backup.get('manter_ultimos', '30')
            self.backup_manter = self._criar_campo(
                frame, "Manter últimos (dias):", 3, manter_padrao
            )
            
            # Frame para os botões
            btn_frame = tk.Frame(frame, bg='#f0f2f5')
            btn_frame.grid(row=4, column=0, columnspan=3, pady=15, sticky='ew')
            
            # Frame para botões da esquerda
            left_btns = tk.Frame(btn_frame, bg='#f0f2f5')
            left_btns.pack(side='left')
            
            # Botão Criar Arquivo - Azul padrão
            btn_executar = tk.Button(
                left_btns,
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
            btn_executar.pack(side='left', padx=5)
            
            # Botão Restaurar Backup - Laranja
            btn_restaurar = tk.Button(
                left_btns,
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
            btn_restaurar.pack(side='left', padx=5)
            
            # Frame para botões da direita
            right_btns = tk.Frame(btn_frame, bg='#f0f2f5')
            right_btns.pack(side='right')
            
            # Botão Salvar - Verde
            btn_salvar = tk.Button(
                right_btns,
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
            
        except Exception as e:
            print(f"Erro ao carregar configurações de backup: {e}")
            ttk.Label(
                frame,
                text=f"Erro ao carregar as configurações de backup: {str(e)}",
                foreground="red"
            ).pack(pady=20)
        
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.current_view = frame
    
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
            font=('Arial', 9, 'bold')
        ).grid(row=row, column=0, sticky='w', padx=5, pady=2)
        
        # Cria um nome único para a variável de controle
        var_name = f"var_{label_text.lower().replace(' ', '_').replace(':', '')}"
        
        # Cria a variável de controle como atributo da instância
        setattr(self, var_name, tk.StringVar(value=valor_padrao))
        var = getattr(self, var_name)
        
        combobox = ttk.Combobox(
            parent,
            textvariable=var,
            values=impressoras,
            state='readonly',
            width=50,
            font=('Arial', 9)
        )
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
                text="Configuração de Impressoras", 
                font=('Arial', 14, 'bold')
            ).grid(row=0, column=0, columnspan=3, pady=10, sticky='w')
            
            # Obtém a lista de impressoras disponíveis
            impressoras = self.ctrl.listar_impressoras()
            
            # Verifica se a lista de impressoras está vazia
            if not impressoras or (len(impressoras) == 1 and impressoras[0].startswith("Erro")):
                ttk.Label(
                    frame,
                    text=impressoras[0] if impressoras else "Nenhuma impressora encontrada",
                    foreground="red" if impressoras and impressoras[0].startswith("Erro") else "black"
                ).grid(row=1, column=0, columnspan=3, pady=10, sticky='w')
                impressoras = ["Nenhuma impressora disponível"]
            else:
                # Exibe a lista de impressoras encontradas
                ttk.Label(
                    frame,
                    text=f"Foram encontradas {len(impressoras)} impressoras no sistema:",
                    font=('Arial', 10)
                ).grid(row=1, column=0, columnspan=3, pady=(10, 5), sticky='w')
                
                # Lista de impressoras em um frame
                list_frame = ttk.Frame(frame)
                list_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15), sticky='ew')
                
                # Cria um texto para mostrar as impressoras
                printer_list = tk.Text(
                    list_frame,
                    height=6,
                    wrap=tk.WORD,
                    font=('Arial', 9),
                    padx=5,
                    pady=5,
                    bg='#f9f9f9',
                    relief='flat'
                )
                
                for i, impressora in enumerate(impressoras, 1):
                    printer_list.insert(tk.END, f"{i}. {impressora}\n")
                
                printer_list.config(state='disabled')
                printer_list.pack(fill='both', expand=True)
            
            # Carrega as configurações salvas
            config_salva = self.ctrl.carregar_config_impressoras()
            
            # Impressora de Cupom Fiscal
            row_start = 3
            ttk.Label(frame, text="Configurar Impressoras por Finalidade", font=('Arial', 10, 'bold')).grid(
                row=row_start, column=0, columnspan=3, pady=(15, 10), sticky='w'
            )
            
            valor_cupom = config_salva.get('cupom_fiscal', '')
            self.imp_cupom = self.criar_linha_impressora(
                frame, "Cupom Fiscal:", row_start+1, impressoras,
                valor_cupom
            )
            
            # Impressora da Cozinha
            self.imp_cozinha = self.criar_linha_impressora(
                frame, "Cozinha:", row_start+2, impressoras,
                config_salva.get('cozinha', '')
            )
            
            # Impressora do Bar
            self.imp_bar = self.criar_linha_impressora(
                frame, "Bar:", row_start+3, impressoras,
                config_salva.get('bar', '')
            )
            
            # Impressora de Sobremesas
            self.imp_sobremesas = self.criar_linha_impressora(
                frame, "Sobremesas:", row_start+4, impressoras,
                config_salva.get('sobremesas', '')
            )
            
            # Impressora de Delivery
            self.imp_delivery = self.criar_linha_impressora(
                frame, "Delivery:", row_start+5, impressoras,
                config_salva.get('delivery', '')
            )
            
            # Configura o tamanho da fonte
            ttk.Label(
                frame,
                text="Tamanho da Fonte:",
                font=('Arial', 9, 'bold')
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
            btn_frame.grid(row=row_start+8, column=0, columnspan=3, sticky='ew')
            
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
                command=self._testar_impressao
            )
            btn_testar.pack(side='left', padx=5)
            
            # Botão para atualizar a lista de impressoras - Cinza
            btn_atualizar = tk.Button(
                left_btns,
                text="Atualizar Lista",
                font=('Arial', 10, 'bold'),
                bg='#757575',
                fg='white',
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
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
                bg='#4CAF50',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
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
                'cupom_fiscal': self.imp_cupom.get() if hasattr(self, 'imp_cupom') else '',
                'cozinha': self.imp_cozinha.get() if hasattr(self, 'imp_cozinha') else '',
                'bar': self.imp_bar.get() if hasattr(self, 'imp_bar') else '',
                'sobremesas': self.imp_sobremesas.get() if hasattr(self, 'imp_sobremesas') else '',
                'delivery': self.imp_delivery.get() if hasattr(self, 'imp_delivery') else '',
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
            self.db_porta = self._criar_campo(frame, "Porta:", 2, str(config.get('porta', '3306')))
            self.db_usuario = self._criar_campo(frame, "Usuário:", 3, config.get('usuario', 'postgres'))
            
            # Senha
            ttk.Label(frame, text="Senha:").grid(row=4, column=0, sticky='w', pady=2, padx=5)
            self.db_senha = ttk.Entry(frame, show="*", width=30)
            self.db_senha.grid(row=4, column=1, sticky='ew', pady=2)
            self.db_senha.insert(0, config.get('senha', ''))
            
            self.db_nome = self._criar_campo(frame, "Nome do Banco:", 5, config.get('nome_bd', 'pdv_aquarius'))
            
            # Frame para os botões
            btn_frame = tk.Frame(frame, bg='#f0f2f5', pady=20)
            btn_frame.grid(row=6, column=0, columnspan=3, sticky='ew')
            
            # Frame para os botões à esquerda
            left_btns = tk.Frame(btn_frame, bg='#f0f2f5')
            left_btns.pack(side='left')
            
            # Botão Testar Conexão - Azul padrão
            btn_teste = tk.Button(
                left_btns,
                text="Testar Conexão",
                font=('Arial', 10, 'bold'),
                bg='#4a6fa5',
                fg='white',
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=self._testar_conexao_db
            )
            btn_teste.pack(side='left', padx=5)
            
            # Frame para o botão à direita
            right_btns = tk.Frame(btn_frame, bg='#f0f2f5')
            right_btns.pack(side='right')
            
            # Botão Salvar Configurações - Verde
            btn_salvar = tk.Button(
                right_btns,
                text="Salvar Configurações",
                font=('Arial', 10, 'bold'),
                bg='#4CAF50',
                fg='white',
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=self._salvar_banco_dados
            )
            btn_salvar.pack(side='right', padx=5)
            
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
            
            self.erp_ativo = tk.BooleanVar(value=config.get('erp', {}).get('ativo', False))
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
            
            self.ecommerce_ativo = tk.BooleanVar(value=config.get('ecommerce', {}).get('ativo', False))
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
            
            # Frame para os botões
            btn_frame = tk.Frame(frame, bg='#f0f2f5')
            btn_frame.grid(row=8, column=0, columnspan=2, pady=15, sticky='e')
            
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
                command=self._salvar_integracoes
            )
            btn_salvar.grid(row=0, column=0, padx=5)
            
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
            
            # Salva as permissões
            if self.gerenciador_permissoes.salvar_todas_permissoes(permissoes_para_salvar):
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
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Cria o frame principal com scrollbar
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Cria um canvas com barra de rolagem
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
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
        
        try:
            # Importa o gerenciador de permissões
            from src.utils.gerenciador_permissoes import GerenciadorPermissoes
            self.gerenciador_permissoes = GerenciadorPermissoes()
            self.permissoes = self.gerenciador_permissoes.obter_todas_permissoes()
            
            # Título
            ttk.Label(
                scrollable_frame, 
                text="Gerenciamento de Permissões", 
                font=('Arial', 14, 'bold')
            ).grid(row=0, column=0, columnspan=4, pady=10, sticky='w')
            
            # Cabeçalho
            ttk.Label(
                scrollable_frame,
                text="Módulo",
                font=('Arial', 10, 'bold'),
                padding=5
            ).grid(row=1, column=0, sticky='w')
            
            ttk.Label(
                scrollable_frame,
                text="Botão",
                font=('Arial', 10, 'bold'),
                padding=5
            ).grid(row=1, column=1, sticky='w')
            
            ttk.Label(
                scrollable_frame,
                text="Usuário Básico",
                font=('Arial', 10, 'bold'),
                padding=5
            ).grid(row=1, column=2, sticky='w')
            
            ttk.Label(
                scrollable_frame,
                text="Usuário Master",
                font=('Arial', 10, 'bold'),
                padding=5
            ).grid(row=1, column=3, sticky='w')
            
            # Linha separadora
            ttk.Separator(scrollable_frame, orient='horizontal').grid(
                row=2, column=0, columnspan=4, sticky='ew', pady=5
            )
            
            # Variáveis para armazenar os estados dos checkboxes
            row = 3
            for modulo_id, modulo_data in self.permissoes['modulos'].items():
                # Inicializa o dicionário de variáveis para este módulo
                if 'variaveis' not in modulo_data:
                    modulo_data['variaveis'] = {}
                
                # Adiciona o nome do módulo
                ttk.Label(
                    scrollable_frame,
                    text=modulo_data['nome'],
                    font=('Arial', 10, 'bold'),
                    padding=5
                ).grid(row=row, column=0, sticky='w')
                
                # Adiciona os botões do módulo
                for botao_id, botao_data in modulo_data['botoes'].items():
                    # Garante que os valores sejam booleanos
                    valor_basico = bool(botao_data.get('basico', False))
                    valor_master = bool(botao_data.get('master', True))
                    
                    # Cria as variáveis para os checkboxes com os valores corretos
                    var_basico = tk.BooleanVar(value=valor_basico)
                    var_master = tk.BooleanVar(value=valor_master)
                    
                    # Armazena as variáveis para uso posterior
                    if 'variaveis' not in modulo_data:
                        modulo_data['variaveis'] = {}
                    
                    modulo_data['variaveis'][botao_id] = {
                        'basico': var_basico,
                        'master': var_master
                    }
                    
                    # Nome do botão
                    ttk.Label(
                        scrollable_frame,
                        text=botao_data['nome'],
                        padding=(20, 5, 5, 5)
                    ).grid(row=row, column=1, sticky='w')
                    
                    # Checkbox para usuário básico
                    ttk.Checkbutton(
                        scrollable_frame,
                        variable=var_basico
                    ).grid(row=row, column=2, sticky='w', padx=5)
                    
                    # Checkbox para usuário master
                    ttk.Checkbutton(
                        scrollable_frame,
                        variable=var_master
                    ).grid(row=row, column=3, sticky='w', padx=5)
                    
                    row += 1
                
                # Adiciona um pequeno espaço entre os módulos
                row += 1
            
            # Botão para salvar as alterações
            btn_frame = ttk.Frame(scrollable_frame)
            btn_frame.grid(row=row, column=0, columnspan=4, pady=20)
            
            tk.Button(
                btn_frame,
                text="Salvar Permissões",
                font=('Arial', 10, 'bold'),
                bg='#4CAF50',
                fg='white',
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
                command=self._salvar_permissoes
            ).pack(side='right', padx=5)
            
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
