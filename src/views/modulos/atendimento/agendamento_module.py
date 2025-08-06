"""
Módulo de Agendamento - Gerencia agendamentos de consultas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar, DateEntry
from datetime import datetime
from datetime import timedelta

class AgendamentoModule:
    def __init__(self, parent, controller, db_connection=None):
        self.parent = parent
        self.controller = controller
        self.db_connection = db_connection
        
        # Inicializar o controlador
        from src.controllers.agenda_controller import AgendaController
        self.agenda_controller = AgendaController(db_connection)
        
        # Frame principal
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True)
        
        # Dados em memória
        self.consultas = []
        self.medicos = []
        self.pacientes = []
        
        # Inicializar interface
        self._criar_interface()

    def _criar_interface(self):
        """Cria a interface do módulo de agendamento"""
        # Garantir que não haja referências a instâncias anteriores
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        
        # Obter dimensões da tela para cálculos proporcionais
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        
        # Definir se é uma tela pequena (largura menor que 1024 pixels)
        is_small_screen = screen_width < 1024
        
        # Frame principal
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill='both', expand=True)
        
        # Frame para os botões (largura fixa)
        botoes_frame = ttk.LabelFrame(self.main_frame, text="Ações", padding=10)
        botoes_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        # Botão de novo agendamento
        btn_novo = tk.Button(
            botoes_frame, 
            text="Novo Agendamento", 
            command=self._novo_agendamento,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            width=20 if not is_small_screen else 15,
            relief='flat',
            activebackground='#43a047',
            activeforeground='white'
        )
        btn_novo.pack(pady=5, fill='x')
        
        # Botão de editar consulta
        btn_editar = tk.Button(
            botoes_frame,
            text="Editar",
            command=self._editar_consulta,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            width=20 if not is_small_screen else 15,
            relief='flat',
            activebackground='#4a6fa5',
            activeforeground='white'
        )
        btn_editar.pack(pady=5, fill='x')

        # Botão de excluir consulta
        btn_excluir = tk.Button(
            botoes_frame,
            text="Excluir",
            command=self._excluir_consulta,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            width=20 if not is_small_screen else 15,
            relief='flat',
            activebackground='#f44336',
            activeforeground='white'
        )
        btn_excluir.pack(pady=5, fill='x')
        
        # Frame para o conteúdo principal (calendário + tabela)
        self.conteudo_frame = ttk.Frame(self.main_frame)
        self.conteudo_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Calcular tamanhos proporcionais à tela
        if is_small_screen:
            # Em telas pequenas, o calendário e a tabela ficam um abaixo do outro
            calendario_width = int(screen_width * 0.7)  # 70% da largura da tela
            calendario_height = int(screen_height * 0.4)  # 40% da altura da tela
            tabela_width = int(screen_width * 0.7)  # 70% da largura da tela
        else:
            # Em telas maiores, o calendário e a tabela ficam lado a lado
            calendario_width = int(screen_width * 0.3)  # 30% da largura da tela
            calendario_height = 0  # Altura automática
            tabela_width = int(screen_width * 0.4)  # 40% da largura da tela
        
        # Frame para o calendário com tamanho adaptativo
        self.calendario_frame = ttk.LabelFrame(self.conteudo_frame, text="Calendário", padding=10, width=calendario_width)
        if is_small_screen:
            # Em telas pequenas, o calendário fica acima da tabela
            self.calendario_frame.pack(side='top', fill='both', expand=False, padx=0, pady=(0, 5))
            if calendario_height > 0:
                self.calendario_frame.configure(height=calendario_height)
        else:
            # Em telas maiores, o calendário fica à esquerda da tabela
            self.calendario_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.calendario_frame.pack_propagate(False)  # Impede que o frame seja redimensionado pelos filhos
        
        # Frame para o calendário (com altura fixa)
        self.calendario_inner = ttk.Frame(self.calendario_frame)
        self.calendario_inner.pack(fill='both', expand=True)
        
        # Adicionar o widget de calendário com tamanho adaptativo
        self.calendario = Calendar(
            self.calendario_inner,
            selectmode='day',
            date_pattern='dd/mm/yyyy',
            locale='pt_BR',
            cursor='hand2',
            showweeknumbers=False,
            firstweekday='sunday',
            showothermonthdays=True,
            weekendbackground='#f0f0f0',
            weekendforeground='#000000',
            othermonthbackground='#f9f9f9',
            othermonthwebackground='#f9f9f9',
            othermonthforeground='#999999',
            othermonthweforeground='#999999',
            bordercolor='#cccccc',
            headersbackground='#f0f0f0',
            headersforeground='#333333',
            selectbackground='#4a90e2',
            selectforeground='#ffffff',
            normalbackground='#ffffff',
            normalforeground='#000000',
            background='#ffffff',
            foreground='#000000',
            font=('Arial', 9 if is_small_screen else 10)  # Fonte menor em telas pequenas
        )
        self.calendario.pack(fill='both', expand=True)
        self.calendario.bind('<<CalendarSelected>>', self._on_date_selected)
        
        # Frame para os filtros (abaixo do calendário)
        self.filtros_frame = ttk.Frame(self.calendario_frame)
        self.filtros_frame.pack(fill='x', pady=(10, 0))
        
        # Filtro por médico
        ttk.Label(self.filtros_frame, text="Médico:").pack(side='left', padx=(0, 5))
        self.filtro_medico = ttk.Combobox(self.filtros_frame, state='readonly', width=25 if not is_small_screen else 15)
        self.filtro_medico.pack(side='left', padx=(0, 5))
        
        # Botão de filtrar
        btn_filtrar = tk.Button(
            self.filtros_frame,
            text="Filtrar",
            command=self._filtrar_agendamentos,
            bg='#4a6fa5',
            fg='white',
            font=('Arial', 9 if is_small_screen else 10, 'bold'),
            bd=0,
            padx=10,
            pady=5,
            relief='flat',
            activebackground='#3b5a7f',
            activeforeground='white'
        )
        btn_filtrar.pack(side='left')
        
        # Frame para a tabela com tamanho adaptativo
        self.tabela_frame = ttk.LabelFrame(self.conteudo_frame, text="Consultas do Dia", padding=10, width=tabela_width)
        if is_small_screen:
            # Em telas pequenas, a tabela fica abaixo do calendário
            self.tabela_frame.pack(side='top', fill='both', expand=True, padx=0, pady=(5, 0))
        else:
            # Em telas maiores, a tabela fica à direita do calendário
            self.tabela_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self.tabela_frame.pack_propagate(False)  # Impede que o frame seja redimensionado pelos filhos
        
        # Configurar a tabela de agendamentos
        colunas = ('hora', 'paciente', 'medico', 'status', 'id')
        self.tabela_agendamentos = ttk.Treeview(
            self.tabela_frame, 
            columns=colunas, 
            show='headings',
            selectmode='browse'
        )
        
        # Configurar colunas
        self.tabela_agendamentos.heading('hora', text='Hora')
        self.tabela_agendamentos.heading('paciente', text='Paciente')
        self.tabela_agendamentos.heading('medico', text='Médico')
        self.tabela_agendamentos.heading('status', text='Status')
        self.tabela_agendamentos.heading('id', text='ID')  # Coluna oculta para o ID
        
        # Configurar largura das colunas
        self.tabela_agendamentos.column('hora', width=80, anchor='center')
        self.tabela_agendamentos.column('paciente', width=150)
        self.tabela_agendamentos.column('medico', width=150)
        self.tabela_agendamentos.column('status', width=100, anchor='center')
        self.tabela_agendamentos.column('id', width=0, stretch=False)  # Coluna oculta
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(self.tabela_frame, orient='vertical', command=self.tabela_agendamentos.yview)
        self.tabela_agendamentos.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar widgets
        self.tabela_agendamentos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Carregar dados iniciais
        self._carregar_dados_iniciais()
    
    def _on_date_selected(self, event):
        """Chamado quando uma data é selecionada no calendário"""
        data_selecionada = self.calendario.selection_get()
        data_formatada = data_selecionada.strftime('%Y-%m-%d')
        
        # Atualizar a tabela com os agendamentos da data selecionada
        self.consultas = self._buscar_agendamentos(
            data_inicio=data_formatada,
            data_fim=data_formatada
        )
        self._atualizar_tabela_agendamentos()
    
    def _atualizar_tabela_agendamentos(self):
        """Atualiza a tabela de agendamentos com os dados atuais"""
        # Limpar tabela
        for item in self.tabela_agendamentos.get_children():
            self.tabela_agendamentos.delete(item)
        
        # Adicionar agendamentos à tabela
        for agendamento in self.consultas:
            self.tabela_agendamentos.insert(
                '', 
                'end',
                values=(
                    agendamento['hora_consulta'],
                    agendamento['paciente_nome'],
                    agendamento['medico_nome'],
                    agendamento['status'],
                    agendamento['id']  # ID da consulta
                )
            )
    
    def _buscar_medicos(self):
        """Busca todos os médicos no banco de dados"""
        try:
            if not self.db_connection:
                raise Exception("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, nome, crm, especialidade 
                FROM medicos 
                ORDER BY nome
            """)
            return [dict(zip([column[0] for column in cursor.description], row)) 
                   for row in cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar médicos: {str(e)}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    def _buscar_pacientes(self):
        """Busca todos os pacientes no banco de dados"""
        try:
            if not self.db_connection:
                raise Exception("Conexão com o banco de dados não disponível")
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT id, nome, cpf, data_nascimento, telefone, email
                FROM pacientes 
                ORDER BY nome
            """)
            return [dict(zip([column[0] for column in cursor.description], row)) 
                   for row in cursor.fetchall()]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar pacientes: {str(e)}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    def _buscar_agendamentos(self, filtro_medico=None, data_inicio=None, data_fim=None):
        """Busca agendamentos usando o controlador"""
        try:
            return self.agenda_controller.buscar_consultas(
                filtro_medico=filtro_medico,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar agendamentos: {str(e)}")
            return []

    def _carregar_dados_iniciais(self):
        """Carrega dados iniciais"""
        try:
            # Buscar médicos
            self.medicos = self.agenda_controller.buscar_medicos()
            
            # Buscar pacientes
            self.pacientes = self._buscar_pacientes()
            
            # Atualizar combobox de médicos
            if hasattr(self, 'filtro_medico'):
                self.filtro_medico['values'] = ["Todos"] + [m["nome"] for m in self.medicos]
                self.filtro_medico.set("Todos")
            
            # Buscar e exibir consultas do dia atual
            hoje = datetime.now().strftime('%Y-%m-%d')
            self.consultas = self._buscar_agendamentos(data_inicio=hoje, data_fim=hoje)
            self._atualizar_tabela_agendamentos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")

    def _filtrar_agendamentos(self):
        """Filtra os agendamentos com base nos critérios selecionados"""
        try:
            # Obter filtros
            medico = self.filtro_medico.get()
            data_inicio = self.calendario.selection_get().strftime('%Y-%m-%d')
            data_fim = self.calendario.selection_get().strftime('%Y-%m-%d')
            
            # Buscar agendamentos com filtros
            self.consultas = self._buscar_agendamentos(
                filtro_medico=medico if medico != "Todos" else None,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            
            # Atualizar tabela
            self._atualizar_tabela_agendamentos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar agendamentos: {str(e)}")
    
    def _novo_agendamento(self):
        """Abre o formulário para novo agendamento"""
        try:
            # Criar uma nova janela completamente separada do loop principal
            # usando um novo Toplevel com seu próprio loop de eventos
            form = tk.Toplevel(self.parent)
            form.title("Novo Agendamento")
            form.geometry("500x600")
            form.resizable(False, False)
            form.transient(self.parent)  # Torna a janela dependente da janela pai
            form.grab_set()  # Torna a janela modal
            
            # Centralizar a janela
            window_width = 500
            window_height = 600
            screen_width = form.winfo_screenwidth()
            screen_height = form.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            form.geometry(f'{window_width}x{window_height}+{x}+{y}')
            
            # Frame principal
            main_frame = tk.Frame(form, bg='#f0f2f5', padx=20, pady=20)
            main_frame.pack(fill='both', expand=True)
            
            # Título
            tk.Label(
                main_frame, 
                text="Novo Agendamento", 
                font=('Arial', 16, 'bold'),
                bg='#f0f2f5'
            ).pack(pady=(0, 20))
            
            # Frame para os campos
            campos_frame = tk.Frame(main_frame, bg='#f0f2f5')
            campos_frame.pack(fill='x', pady=5)
            
            # Função para criar campos com label
            def criar_campo(container, label_text, row, **kwargs):
                tk.Label(
                    container, 
                    text=label_text + ":", 
                    font=('Arial', 10),
                    bg='#f0f2f5',
                    anchor='w'
                ).grid(row=row, column=0, sticky='w', pady=5)
                
                if 'values' in kwargs:  # É um Combobox
                    var = tk.StringVar()
                    campo = ttk.Combobox(
                        container,
                        textvariable=var,
                        values=kwargs['values'],
                        state='readonly',
                        font=('Arial', 10)
                    )
                else:  # É um Entry normal
                    var = tk.StringVar()
                    campo = ttk.Entry(
                        container,
                        textvariable=var,
                        font=('Arial', 10),
                        **kwargs
                    )
                
                campo.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
                container.columnconfigure(1, weight=1)
                return campo, var
            
            # Campos do formulário
            campos = {}
            
            # Paciente
            campo_paciente, var_paciente = criar_campo(
                campos_frame, 
                "Paciente", 
                0,
                values=[p['nome'] for p in self.pacientes] if hasattr(self, 'pacientes') else []
            )
            campos['paciente'] = campo_paciente
            
            # Botão Novo Paciente
            def abrir_cadastro_paciente():
                # Criar uma janela para o cadastro de paciente
                paciente_window = tk.Toplevel(form)
                paciente_window.title("Novo Paciente")
                paciente_window.geometry("800x600")
                paciente_window.transient(form)  # Torna a janela dependente da janela pai
                paciente_window.grab_set()  # Torna a janela modal
                
                # Centralizar a janela
                window_width = 800
                window_height = 600
                screen_width = paciente_window.winfo_screenwidth()
                screen_height = paciente_window.winfo_screenheight()
                x = (screen_width // 2) - (window_width // 2)
                y = (screen_height // 2) - (window_height // 2)
                paciente_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
                
                # Importar o controlador de cliente
                from src.controllers.cliente_controller import ClienteController
                cliente_controller = ClienteController()
                
                # Frame principal
                main_frame = tk.Frame(paciente_window, bg='#f0f2f5')
                main_frame.pack(fill='both', expand=True, padx=20, pady=10)
                
                # Título
                tk.Label(main_frame, text="Novo Paciente", font=('Arial', 14, 'bold')).pack(pady=10)
                
                # Frame do formulário
                form_frame = tk.Frame(main_frame)
                form_frame.pack(fill='both', expand=True)
                
                # Campos do formulário
                campos_paciente = [
                    ('Nome:', 'nome', 0, 0, 40),
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
                    ('UF:', 'uf', 7, 0, 5)
                ]
                
                entries = {}
                for label, field, row, col, width in campos_paciente:
                    # Label
                    tk.Label(form_frame, text=label, font=('Arial', 10)).grid(row=row, column=col, sticky='e', padx=5, pady=5)
                    
                    # Entry
                    entry = tk.Entry(form_frame, font=('Arial', 10), width=width)
                    entry.grid(row=row, column=col+1, sticky='w', padx=5, pady=5)
                    entries[field] = entry
                    
                    # Adiciona botão de busca ao lado do campo CEP
                    if field == 'cep':
                        def buscar_cep():
                            try:
                                import requests
                                cep = entries['cep'].get().replace('-', '').replace('.', '')
                                if len(cep) != 8:
                                    messagebox.showwarning("Aviso", "CEP inválido. Digite 8 números.")
                                    return
                                
                                url = f"https://viacep.com.br/ws/{cep}/json/"
                                response = requests.get(url)
                                data = response.json()
                                
                                if "erro" not in data:
                                    entries['endereco'].delete(0, tk.END)
                                    entries['endereco'].insert(0, data.get('logradouro', ''))
                                    
                                    entries['bairro'].delete(0, tk.END)
                                    entries['bairro'].insert(0, data.get('bairro', ''))
                                    
                                    entries['cidade'].delete(0, tk.END)
                                    entries['cidade'].insert(0, data.get('localidade', ''))
                                    
                                    entries['uf'].delete(0, tk.END)
                                    entries['uf'].insert(0, data.get('uf', ''))
                                else:
                                    messagebox.showwarning("Aviso", "CEP não encontrado.")
                            except Exception as e:
                                messagebox.showerror("Erro", f"Erro ao buscar CEP: {str(e)}")
                        
                        btn_buscar_cep = tk.Button(
                            form_frame,
                            text="Buscar",
                            command=buscar_cep,
                            font=('Arial', 9),
                            bg='#4a6fa5',
                            fg='white',
                            padx=5,
                            pady=2
                        )
                        btn_buscar_cep.grid(row=row, column=col+2, padx=5, pady=5)
                
                # Campo de observações
                tk.Label(form_frame, text="Observações:", font=('Arial', 10)).grid(row=8, column=0, sticky='ne', padx=5, pady=5)
                txt_observacoes = tk.Text(form_frame, height=4, width=40, font=('Arial', 10))
                txt_observacoes.grid(row=8, column=1, sticky='w', padx=5, pady=5)
                
                # Frame para os botões
                botoes_frame = tk.Frame(form_frame)
                botoes_frame.grid(row=9, column=0, columnspan=4, pady=20, sticky='w')
                
                # Função para salvar o cliente
                def salvar_cliente():
                    try:
                        # Coletar dados do formulário
                        dados = {}
                        for field in entries:
                            dados[field] = entries[field].get()
                        
                        # Adicionar observações
                        dados['observacoes'] = txt_observacoes.get('1.0', tk.END).strip()
                        
                        # Salvar no banco de dados usando o método cadastrar_cliente
                        sucesso, mensagem = cliente_controller.cadastrar_cliente(**dados)
                        
                        if sucesso:
                            messagebox.showinfo("Sucesso", mensagem)
                            
                            # Atualizar a lista de pacientes
                            self.pacientes = self._buscar_pacientes()
                            
                            # Atualizar o combobox de pacientes
                            campo_paciente['values'] = [p['nome'] for p in self.pacientes] if self.pacientes else []
                            
                            # Selecionar o novo paciente no combobox
                            if self.pacientes:
                                for p in self.pacientes:
                                    if p['nome'] == dados['nome']:
                                        var_paciente.set(dados['nome'])
                                        break
                            
                            # Fechar a janela
                            paciente_window.destroy()
                        else:
                            messagebox.showerror("Erro", mensagem)
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao salvar paciente: {str(e)}")
                
                # Botão Salvar
                btn_salvar = tk.Button(
                    botoes_frame,
                    text="Salvar",
                    command=salvar_cliente,
                    bg='#4CAF50',
                    fg='white',
                    font=('Arial', 10, 'bold'),
                    bd=0,
                    padx=15,
                    pady=5
                )
                btn_salvar.pack(side='left', padx=5)
                
                # Botão Cancelar
                btn_cancelar = tk.Button(
                    botoes_frame,
                    text="Cancelar",
                    command=paciente_window.destroy,
                    bg='#f44336',
                    fg='white',
                    font=('Arial', 10, 'bold'),
                    bd=0,
                    padx=15,
                    pady=5
                )
                btn_cancelar.pack(side='left', padx=5)
                
                # Focar na janela
                paciente_window.focus_force()
            
            btn_novo_paciente = tk.Button(
                campos_frame,
                text="Novo Paciente",
                bg='#4a6fa5',
                fg='white',
                font=('Arial', 9, 'bold'),
                bd=0,
                padx=10,
                pady=3,
                command=abrir_cadastro_paciente
            )
            btn_novo_paciente.grid(row=0, column=2, padx=(5, 0), pady=5)
            
            # Médico
            campo_medico, var_medico = criar_campo(
                campos_frame,
                "Médico",
                1,
                values=[m['nome'] for m in self.medicos] if hasattr(self, 'medicos') else []
            )
            campos['medico'] = campo_medico
            
            # Data
            tk.Label(
                campos_frame,
                text="Data:",
                font=('Arial', 10),
                bg='#f0f2f5',
                anchor='w'
            ).grid(row=2, column=0, sticky='w', pady=5)
            
            data_entry = DateEntry(
                campos_frame,
                date_pattern='dd/mm/yyyy',
                locale='pt_BR',
                width=18,
                font=('Arial', 10)
            )
            data_entry.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
            campos['data'] = data_entry
            
            # Hora
            tk.Label(
                campos_frame,
                text="Hora:",
                font=('Arial', 10),
                bg='#f0f2f5',
                anchor='w'
            ).grid(row=3, column=0, sticky='w', pady=5)
            
            horas = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 10, 20, 30, 40, 50)]
            campo_hora = ttk.Combobox(
                campos_frame,
                values=horas,
                state='readonly',
                font=('Arial', 10),
                width=10
            )
            campo_hora.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
            campos['hora'] = campo_hora
            
            # Status
            campo_status, var_status = criar_campo(
                campos_frame,
                "Status",
                5,
                values=['Agendado', 'Confirmado', 'Cancelado', 'Concluído']
            )
            
            # Observações
            tk.Label(
                campos_frame,
                text="Observações:",
                font=('Arial', 10),
                bg='#f0f2f5',
                anchor='nw'
            ).grid(row=6, column=0, sticky='nw', pady=5)
            
            text_obs = tk.Text(
                campos_frame,
                height=5,
                width=40,
                font=('Arial', 10),
                wrap='word',
                bd=1,
                relief='solid'
            )
            text_obs.grid(row=6, column=1, sticky='nsew', pady=5, padx=(10, 0))
            campos['obs'] = text_obs
            
            # Frame para os botões
            botoes_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=20)
            botoes_frame.pack(fill='x')
            
            # Função para salvar o agendamento
            def salvar():
                try:
                    # Validar campos obrigatórios
                    if not all([var_paciente.get(), var_medico.get(), data_entry.get_date(), campo_hora.get()]):
                        messagebox.showwarning("Atenção", "Preencha todos os campos obrigatórios!")
                        return
                    
                    # Obter IDs dos pacientes e médicos selecionados
                    paciente_nome = var_paciente.get()
                    medico_nome = var_medico.get()
                    
                    # Encontrar o ID do paciente selecionado
                    paciente_id = None
                    for p in self.pacientes:
                        if p['nome'] == paciente_nome:
                            paciente_id = p['id']
                            break
                    
                    # Encontrar o ID do médico selecionado
                    medico_id = None
                    for m in self.medicos:
                        if m['nome'] == medico_nome:
                            medico_id = m['id']
                            break
                    
                    if not paciente_id or not medico_id:
                        messagebox.showwarning("Atenção", "Paciente ou médico não encontrado!")
                        return
                    
                    # Formatar a data para o formato do banco de dados (YYYY-MM-DD)
                    data_consulta = data_entry.get_date().strftime('%Y-%m-%d')
                    
                    # Preparar os dados para salvar
                    dados_consulta = {
                        'paciente_id': paciente_id,
                        'medico_id': medico_id,
                        'data': data_consulta,
                        'hora': campo_hora.get(),
                        'status': var_status.get(),
                        'observacoes': text_obs.get('1.0', tk.END).strip()
                    }
                    
                    # Salvar no banco de dados usando o AgendaController
                    sucesso, mensagem = self.agenda_controller.salvar_consulta(dados_consulta)
                    
                    if sucesso:
                        messagebox.showinfo("Sucesso", "Agendamento salvo com sucesso!")
                        form.destroy()
                        self._carregar_dados_iniciais()  # Atualiza a lista de agendamentos
                    else:
                        messagebox.showerror("Erro", mensagem)
                        
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar agendamento: {str(e)}")
            
            # Botão Salvar
            btn_salvar = tk.Button(
                botoes_frame,
                text="Salvar",
                command=salvar,
                bg='#4CAF50',
                fg='white',
                font=('Arial', 10, 'bold'),
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                activebackground='#43a047',
                activeforeground='white'
            )
            btn_salvar.pack(side='left', padx=5)
            
            # Botão Cancelar
            btn_cancelar = tk.Button(
                botoes_frame,
                text="Cancelar",
                command=form.destroy,
                bg='#f44336',
                fg='white',
                font=('Arial', 10, 'bold'),
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                activebackground='#e91e63',
                activeforeground='white'
            )
            btn_cancelar.pack(side='right', padx=5)
            
            # Focar na janela do formulário e garantir que ela seja modal
            form.focus_force()
            form.wait_window()  # Espera a janela ser fechada antes de continuar
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir formulário: {str(e)}")
    
    def _editar_consulta(self):
        """Edita a consulta selecionada na tabela"""
        try:
            # Verificar se há uma consulta selecionada
            selecao = self.tabela_agendamentos.selection()
            if not selecao:
                messagebox.showwarning("Aviso", "Selecione uma consulta para editar.")
                return
            
            # Obter o ID da consulta selecionada
            item_id = selecao[0]
            valores = self.tabela_agendamentos.item(item_id)['values']
            
            # Verificar se temos valores suficientes
            if not valores or len(valores) < 5:  # 5 colunas: hora, paciente, médico, status, id
                messagebox.showerror("Erro", "Dados da consulta incompletos.")
                return
                
            consulta_id = valores[-1]  # Último valor é o ID
            
            # Buscar dados completos da consulta
            try:
                cursor = self.db_connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT 
                        c.*, 
                        p.nome as paciente_nome, 
                        m.nome as medico_nome
                    FROM consultas c
                    LEFT JOIN pacientes p ON c.paciente_id = p.id
                    LEFT JOIN medicos m ON c.medico_id = m.id
                    WHERE c.id = %s
                """, (consulta_id,))
                
                consulta = cursor.fetchone()
                cursor.close()
                
                if not consulta:
                    messagebox.showerror("Erro", "Consulta não encontrada no banco de dados.")
                    return
                    
                # Garantir que temos todos os campos necessários
                if 'observacoes' not in consulta:
                    consulta['observacoes'] = ''

                
                # Criar janela de edição
                self._abrir_formulario_consulta(consulta)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar dados da consulta: {str(e)}")
                import traceback
                print(traceback.format_exc())
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar consulta: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _abrir_formulario_consulta(self, consulta=None):
        """Abre o formulário para edição ou criação de consulta"""
        # Se consulta for None, é um novo agendamento
        if consulta is None:
            self._novo_agendamento()
            return
            
        # Criar janela de edição
        consulta_window = tk.Toplevel(self.parent)
        consulta_window.title("Editar Consulta")
        consulta_window.geometry("600x500")
        consulta_window.resizable(False, False)
        consulta_window.transient(self.parent)
        consulta_window.focus_force()
        consulta_window.grab_set()
        
        # Centralizar a janela
        consulta_window.update_idletasks()
        width = consulta_window.winfo_width()
        height = consulta_window.winfo_height()
        x = (consulta_window.winfo_screenwidth() // 2) - (width // 2)
        y = (consulta_window.winfo_screenheight() // 2) - (height // 2)
        consulta_window.geometry(f"600x500+{x}+{y}")
        
        # Frame para os campos
        campos_frame = ttk.Frame(consulta_window, padding=20)
        campos_frame.pack(fill='both', expand=True)
        
        # Função para criar campos
        def criar_campo(container, label_text, row, **kwargs):
            ttk.Label(container, text=label_text).grid(row=row, column=0, sticky='w', pady=5)
            var = tk.StringVar()
            campo = ttk.Combobox(container, textvariable=var, **kwargs) if 'values' in kwargs else ttk.Entry(container, textvariable=var, **kwargs)
            campo.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
            container.grid_columnconfigure(1, weight=1)
            return campo, var
        
        # Campos do formulário
        # Campo de Paciente
        campo_paciente, var_paciente = criar_campo(
            campos_frame, 
            "Paciente", 
            0,
            values=[p['nome'] for p in self.pacientes] if hasattr(self, 'pacientes') else []
        )
        
        # Preencher com o valor atual
        if 'paciente_nome' in consulta:
            var_paciente.set(consulta['paciente_nome'])
        
        # Campo de Médico
        campo_medico, var_medico = criar_campo(
            campos_frame,
            "Médico",
            1,
            values=[m['nome'] for m in self.medicos] if hasattr(self, 'medicos') else []
        )
        
        # Preencher com o valor atual
        if 'medico_nome' in consulta:
            var_medico.set(consulta['medico_nome'])
        
        # Campo de Data
        ttk.Label(campos_frame, text="Data").grid(row=2, column=0, sticky='w', pady=5)
        var_data = tk.StringVar()
        
        # Formatar a data para exibição
        if 'data' in consulta and consulta['data']:
            data_obj = datetime.strptime(str(consulta['data']), '%Y-%m-%d')
            var_data.set(data_obj.strftime('%d/%m/%Y'))
        
        campo_data = DateEntry(
            campos_frame,
            textvariable=var_data,
            date_pattern='dd/mm/yyyy',
            locale='pt_BR',
            width=17
        )
        campo_data.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Campo de Hora
        ttk.Label(campos_frame, text="Hora").grid(row=3, column=0, sticky='w', pady=5)
        var_hora = tk.StringVar()
        
        # Formatar a hora para exibição
        if 'hora' in consulta and consulta['hora']:
            # Converter para string se for um objeto time
            hora_str = str(consulta['hora'])
            # Extrair apenas a parte da hora (HH:MM:SS)
            if ':' in hora_str:
                hora_str = hora_str.split('.')[0]  # Remove frações de segundo se houver
            var_hora.set(hora_str)
        
        # Gerar lista de horários de 10 em 10 minutos
        horarios = []
        hora_atual = datetime.strptime("08:00", "%H:%M")
        hora_final = datetime.strptime("18:00", "%H:%M")
        while hora_atual <= hora_final:
            horarios.append(hora_atual.strftime("%H:%M"))
            hora_atual = hora_atual + timedelta(minutes=10)
        
        campo_hora = ttk.Combobox(campos_frame, textvariable=var_hora, values=horarios, width=17)
        campo_hora.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Campo de Status
        ttk.Label(campos_frame, text="Status").grid(row=5, column=0, sticky='w', pady=5)
        var_status = tk.StringVar()
        status_opcoes = ["Agendado", "Confirmado", "Realizado", "Cancelado", "Faltou"]
        campo_status = ttk.Combobox(campos_frame, textvariable=var_status, values=status_opcoes, width=17)
        campo_status.grid(row=5, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Preencher com o valor atual
        if 'status' in consulta and consulta['status']:
            var_status.set(consulta['status'])
        else:
            var_status.set("Agendado")  # Valor padrão
        
        # Campo de Observações
        ttk.Label(campos_frame, text="Observações").grid(row=6, column=0, sticky='nw', pady=5)
        var_obs = tk.Text(campos_frame, height=5, width=40)
        var_obs.grid(row=6, column=1, sticky='nsew', pady=5, padx=(10, 0))
        
        # Preencher com o valor atual
        if 'observacoes' in consulta and consulta['observacoes']:
            var_obs.insert('1.0', consulta['observacoes'])
        
        # Frame para os botões
        botoes_frame = ttk.Frame(consulta_window)
        botoes_frame.pack(fill='x', padx=20, pady=10)
        
        # Botão Salvar
        def salvar_edicao():
            # Obter valores dos campos
            paciente_nome = var_paciente.get()
            medico_nome = var_medico.get()
            data = var_data.get()
            hora = var_hora.get()
            status = var_status.get()
            observacoes = var_obs.get('1.0', 'end-1c')
            
            # Validar campos obrigatórios
            if not all([paciente_nome, medico_nome, data, hora, status]):
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
                return
            
            # Obter IDs do paciente e médico
            paciente_id = None
            for p in self.pacientes:
                if p['nome'] == paciente_nome:
                    paciente_id = p['id']
                    break
            
            medico_id = None
            for m in self.medicos:
                if m['nome'] == medico_nome:
                    medico_id = m['id']
                    break
            
            if not paciente_id or not medico_id:
                messagebox.showwarning("Aviso", "Paciente ou médico não encontrado.")
                return
            
            # Formatar data para o formato do banco (YYYY-MM-DD)
            try:
                data_formatada = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
                return
            
            # Preparar dados para atualização
            dados_consulta = {
                'id': consulta['id'],
                'paciente_id': paciente_id,
                'medico_id': medico_id,
                'data': data_formatada,
                'hora': hora,
                'status': status,
                'observacoes': observacoes
            }
            
            try:
                # Atualizar consulta no banco
                sucesso, mensagem = self.agenda_controller.atualizar_consulta(dados_consulta)
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    # Atualizar tabela e fechar janela
                    self._carregar_dados_iniciais()
                    consulta_window.destroy()
                else:
                    messagebox.showerror("Erro", mensagem)
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar consulta: {str(e)}")
       # Botão Salvar
        btn_salvar = tk.Button(
            botoes_frame, 
            text="Salvar", 
            command=salvar_edicao,
            bg='#4CAF50',  # Verde
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5
        )
        btn_salvar.pack(side='right', padx=5)

        # Botão Cancelar
        btn_cancelar = tk.Button(
            botoes_frame, 
            text="Cancelar", 
            command=consulta_window.destroy,
            bg='#f44336',  # Vermelho
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=15,
            pady=5
        )
        btn_cancelar.pack(side='right', padx=5)
        # Configurar o grid para expandir corretamente
        campos_frame.grid_rowconfigure(6, weight=1)
        campos_frame.grid_columnconfigure(1, weight=1)
        
        # Focar na janela
        consulta_window.focus_force()

    def _excluir_consulta(self):
        """Exclui a consulta selecionada"""
        try:
            # Verificar se há uma consulta selecionada
            selecao = self.tabela_agendamentos.selection()
            if not selecao:
                messagebox.showwarning("Aviso", "Selecione uma consulta para excluir.")
                return
            
            # Obter o ID da consulta selecionada
            item_id = selecao[0]
            valores = self.tabela_agendamentos.item(item_id)['values']
            
            if not valores or len(valores) < 5:  # 5 colunas: hora, paciente, médico, status, id
                messagebox.showerror("Erro", "Não foi possível identificar a consulta selecionada.")
                return
                
            consulta_id = valores[-1]  # Último valor é o ID
            
            # Confirmar exclusão
            if not messagebox.askyesno("Confirmar Exclusão", 
                                    "Tem certeza que deseja excluir esta consulta?"):
                return
            
            # Chamar o controlador para excluir
            sucesso, mensagem = self.agenda_controller.excluir_consulta(consulta_id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                # Atualizar a lista de consultas
                self._carregar_dados_iniciais()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir consulta: {str(e)}")