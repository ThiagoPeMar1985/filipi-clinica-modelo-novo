"""
Módulo de Agendamento - Gerencia agendamentos de consultas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar, DateEntry
from datetime import datetime, timedelta

from src.controllers.horario_controller import HorarioController

class MedicoCalendar(Calendar):
    """Calendário personalizado que desabilita os dias em que o médico não atende"""
    
    def __init__(self, master=None, dias_atendimento=None, modo='livre', **kw):
        """
        Inicializa o calendário
        
        Args:
            master: Widget pai
            dias_atendimento: Lista de dias da semana (0-6) em que o médico atende
            **kw: Argumentos adicionais para o Calendar
        """
        self.dias_atendimento = dias_atendimento or []
        self.modo = modo
        Calendar.__init__(self, master, **kw)

    
        
    def _display_calendar(self):
        """Sobrescreve o método _display_calendar para controlar a exibição dos dias"""
        # Exibe o calendário normalmente
        Calendar._display_calendar(self)
        
        # Dados para destacar a data selecionada corretamente (mesmo após clique)
        try:
            sel_date = self.selection_get()
        except Exception:
            sel_date = None
        # Mês/ano exibidos atualmente
        try:
            disp_year = self._date.year
            disp_month = self._date.month
        except Exception:
            disp_year = disp_month = None
        # Cores auxiliares
        try:
            other_fg = self.cget('othermonthforeground')
        except Exception:
            other_fg = '#888888'
        try:
            other_we_fg = self.cget('othermonthweforeground')
        except Exception:
            other_we_fg = '#888888'
        try:
            select_bg = self.cget('selectbackground')
        except Exception:
            select_bg = '#4a90e2'
        try:
            select_fg = self.cget('selectforeground')
        except Exception:
            select_fg = '#ffffff'
        
        # Para cada dia no calendário
        for i in range(6):  # 6 semanas no calendário
            for j in range(7):  # 7 dias na semana
                # j é o dia da semana (0=segunda, 1=terça, ..., 6=domingo)
                # Mas o Calendar usa 0=domingo, 1=segunda, ..., 6=sábado
                # Então precisamos converter
                dia_semana_calendar = (j + 1) % 7
                day_label = self._calendar[i][dia_semana_calendar]
                
                if day_label.cget('text') != '':
                    if self.modo == 'livre':
                        # Modo livre: todos os dias são clicáveis
                        day_label.state(['!disabled'])
                        # Se não for dia de atendimento, destaca em cinza
                        if j not in self.dias_atendimento:
                            day_label.configure(
                                background='#f9f9f9',
                                foreground='#000000',
                                relief='flat'
                            )
                    else:
                        # Modo restrito: apenas dias de atendimento são clicáveis
                        if j in self.dias_atendimento:
                            day_label.state(['!disabled'])
                            day_label.configure(
                                background='#e8f5e9',  # Verde claro
                                foreground='#000000',   # Verde escuro
                                relief='flat'
                            )
                        else:
                            day_label.state(['disabled'])
                            day_label.configure(
                                background='#f9f9f9',
                                foreground='#000000',  # Cinza mais claro
                                relief='flat'
                            )
                    
                    # Adiciona um efeito de hover nos dias ativos
                    if day_label.instate(['!disabled']):
                        day_label.bind('<Enter>', lambda e, d=day_label: d.configure(relief='raised') if d['state'] == 'normal' else None)
                        day_label.bind('<Leave>', lambda e, d=day_label: d.configure(relief='flat') if d['state'] == 'normal' else None)
                    
                    # Se este label representa exatamente a data selecionada, aplica cores de seleção
                    txt = day_label.cget('text')
                    if (txt and sel_date and disp_year and disp_month and
                        day_label.cget('foreground') not in (other_fg, other_we_fg)):
                        try:
                            if int(txt) == sel_date.day and sel_date.year == disp_year and sel_date.month == disp_month:
                                day_label.configure(background=select_bg, foreground=select_fg, relief='flat')
                            
                        except Exception:
                            pass
                    
        # Destaca o dia selecionado (se visível no mês corrente)
        try:
            sel = self.selection_get()
        except Exception:
            sel = None
        if sel:
            selected_day = str(sel.day)
            # Cores para identificar dias de outros meses
            try:
                other_fg = self.cget('othermonthforeground')
            except Exception:
                other_fg = '#888888'
            try:
                other_we_fg = self.cget('othermonthweforeground')
            except Exception:
                other_we_fg = '#888888'
            try:
                select_bg = self.cget('selectbackground')
            except Exception:
                select_bg = '#4a90e2'
            try:
                select_fg = self.cget('selectforeground')
            except Exception:
                select_fg = '#ffffff'
            # Aplica ao label do dia selecionado
            for i in range(6):
                for j in range(7):
                    dia_semana_calendar = (j + 1) % 7
                    lbl = self._calendar[i][dia_semana_calendar]
                    txt = lbl.cget('text')
                    if not txt:
                        continue
                    # Ignora dias de outros meses
                    fg = lbl.cget('foreground')
                    if fg in (other_fg, other_we_fg):
                        continue
                    if txt == selected_day and lbl.instate(['!disabled']):
                        lbl.configure(background=select_bg, foreground=select_fg, relief='flat')
                        break

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
        self.tipos_atendimento_map = {}
        self.exames_medico = {}  
        self.tempo_exame = 0    

        self.carregar_tipos_atendimento()
        self._carregar_dados_iniciais()
        
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
        # Definir se a altura é curta (ex.: ~700px)
        is_short_height = screen_height < 800
        
        # Frame principal
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill='both', expand=True)
        
        # Vamos montar uma coluna à esquerda (botões em cima + calendário abaixo)
        # e a tabela à direita ocupando o restante.
        
        # Frame para o conteúdo principal (coluna esquerda + tabela)
        self.conteudo_frame = ttk.Frame(self.main_frame)
        self.conteudo_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Calcular tamanhos proporcionais à tela
        # Coluna esquerda (botões + calendário)
        # Redução lateral de ~200px em monitores por volta de 1366px de largura
        left_reduce = 200 if 1200 <= screen_width <= 1440 else 0
        base_left = int(screen_width * 0.26)
        left_col_width = min(max(base_left - left_reduce, 220), 340)
        # Altura do calendário mais contida em telas baixas (subir calendário e dar mais espaço para a tabela)
        calendario_height = int(screen_height * (0.26 if is_short_height else 0.40))
        
        # Coluna esquerda
        self.left_col = ttk.Frame(self.conteudo_frame, width=left_col_width)
        self.left_col.pack(side='left', fill='y', expand=False, padx=(0, 5))
        self.left_col.pack_propagate(False)

        # Frame para os botões (em cima do calendário)
        botoes_frame = ttk.LabelFrame(self.left_col, text="Ações", padding=10)
        botoes_frame.pack(side='top', fill='x', padx=0, pady=(0, 5))

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
        btn_novo.pack(fill='x', pady=5)
        
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
        btn_editar.pack(fill='x', pady=5)

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
        btn_excluir.pack(fill='x', pady=5)

        # Frame para o calendário com tamanho adaptativo (abaixo dos botões)
        self.calendario_frame = ttk.LabelFrame(self.left_col, text="Calendário", padding=10, width=left_col_width)
        self.calendario_frame.pack(side='top', fill='both', expand=False)
        if calendario_height > 0:
            self.calendario_frame.configure(height=calendario_height)
        
        self.calendario_frame.pack_propagate(False)  # Impede que o frame seja redimensionado pelos filhos
        
        # Frame para o calendário (com altura fixa)
        self.calendario_inner = ttk.Frame(self.calendario_frame)
        self.calendario_inner.pack(fill='both', expand=False)
        
        # Adicionar o widget de calendário com tamanho adaptativo
        cal_font_size = 8 if is_short_height else 9
        try:
            self.calendario = MedicoCalendar(
                self.calendario_inner,
                modo='livre',
                selectmode='day',
                date_pattern='dd/mm/yyyy',
                locale='pt_BR',
                cursor='hand2',
                showweeknumbers=False,
                firstweekday='sunday',
                showothermonthdays=True,
                # Cores dos dias da semana (segunda a sexta)
                normalbackground='#ffffff',    # Fundo branco
                normalforeground='#000000',   # Texto preto
                # Cores do fim de semana (sábado e domingo)
                weekendbackground='#e0e0e0',  # Fundo cinza claro
                weekendforeground='#000000',  # Texto preto
                # Cores dos dias de outros meses
                othermonthbackground='#f9f9f9',
                othermonthwebackground='#f9f9f9',
                othermonthforeground='#888888',
                othermonthweforeground='#888888',
                # Cores de borda
                bordercolor='#000000',        # Linhas pretas
                # Cores do cabeçalho
                headersbackground='#f0f0f0',
                headersforeground='#000000',
                # Cores de seleção
                selectbackground='#4a90e2',   # Azul para dia selecionado
                selectforeground='#ffffff',   # Texto branco no dia selecionado
                # Configurações gerais
                background='#ffffff',
                foreground='#000000',
                relief='flat',
                font=('Arial', cal_font_size)
            )
        except Exception:
            # Fallback de locale para ambientes empacotados sem recursos de locale
            self.calendario = MedicoCalendar(
                self.calendario_inner,
                modo='livre',
                selectmode='day',
                date_pattern='dd/mm/yyyy',
                locale='en_US',
                cursor='hand2',
                showweeknumbers=False,
                firstweekday='sunday',
                showothermonthdays=True,
                normalbackground='#ffffff',
                normalforeground='#000000',
                weekendbackground='#e0e0e0',
                weekendforeground='#000000',
                othermonthbackground='#f9f9f9',
                othermonthwebackground='#f9f9f9',
                othermonthforeground='#888888',
                othermonthweforeground='#888888',
                bordercolor='#000000',
                headersbackground='#f0f0f0',
                headersforeground='#000000',
                selectbackground='#4a90e2',
                selectforeground='#ffffff',
                background='#ffffff',
                foreground='#000000',
                relief='flat',
                font=('Arial', cal_font_size)
            )

        self.calendario.pack(fill='x', expand=False)
        self.calendario.bind('<<CalendarSelected>>', self._on_date_selected)
        
        # Frame para os filtros (abaixo do calendário)
        self.filtros_frame = ttk.Frame(self.calendario_frame)
        self.filtros_frame.pack(fill='x', pady=(10, 0))
        
        # Filtro por médico
        ttk.Label(self.filtros_frame, text="Médico:").pack(side='left', padx=(0, 5))
        self.filtro_medico = ttk.Combobox(self.filtros_frame, state='readonly', width=25 if not is_small_screen else 15)
        self.filtro_medico.pack(side='left', padx=(0, 5))

        # Adicione esta linha para chamar a função quando o médico for selecionado
        self.filtro_medico.bind('<<ComboboxSelected>>', self._ao_selecionar_medico)
                
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
        self.tabela_frame = ttk.LabelFrame(self.conteudo_frame, text="Consultas do Dia", padding=10)
        # A tabela ocupa o restante à direita
        self.tabela_frame.pack(side='left', fill='both', expand=True, padx=(5, 0))
        
        self.tabela_frame.pack_propagate(False)  # Impede que o frame seja redimensionado pelos filhos
        
        # Toolbar da tabela (ações rápidas)
        self.tabela_toolbar = tk.Frame(self.tabela_frame)
        self.tabela_toolbar.pack(fill='x', side='top', pady=(0, 6))

        btn_chegada = tk.Button(
            self.tabela_toolbar,
            text="Marcar Chegada",
            command=self._marcar_chegada,
            bg='#4a6fa5', fg='white', font=('Arial', 9, 'bold'), bd=0,
            padx=10, pady=5, relief='flat', activebackground='#3b5a7f', activeforeground='white'
        )
        btn_chegada.pack(side='left')

        # Configurar a tabela de agendamentos
        colunas = ('hora', 'paciente', 'medico', 'tipo_agendamento', 'status', 'pagamento', 'chegada', 'id')
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
        self.tabela_agendamentos.heading('tipo_agendamento', text='Tipo Agendamento')
        self.tabela_agendamentos.heading('status', text='Status')
        self.tabela_agendamentos.heading('pagamento', text='Pagamento')
        self.tabela_agendamentos.heading('chegada', text='Chegada')
        self.tabela_agendamentos.heading('id', text='ID')  # Coluna oculta para o ID
        
        # Configurar largura das colunas
        self.tabela_agendamentos.column('hora', width=80, anchor='center')
        self.tabela_agendamentos.column('paciente', width=150)
        self.tabela_agendamentos.column('medico', width=150)
        self.tabela_agendamentos.column('tipo_agendamento', width=160)
        self.tabela_agendamentos.column('status', width=100, anchor='center')
        self.tabela_agendamentos.column('pagamento', width=90, anchor='center')
        self.tabela_agendamentos.column('chegada', width=150, anchor='center')
        self.tabela_agendamentos.column('id', width=0, stretch=False)  # Coluna oculta
        
        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(self.tabela_frame, orient='vertical', command=self.tabela_agendamentos.yview)
        self.tabela_agendamentos.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar widgets
        self.tabela_agendamentos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Carregar dados iniciais
        self._carregar_dados_iniciais()
        # Atualização periódica para refletir pagamentos/chegadas
        try:
            self.parent.after(30000, self._refresh_consultas_periodico)
        except Exception:
            pass


    
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
        
        # Reaplica o destaque no calendário após o ciclo atual de eventos (garante selection_get() atualizado)
        try:
            self.parent.after_idle(self.calendario._display_calendar)
        except Exception:
            pass
    
    def _atualizar_tabela_agendamentos(self):
        """Atualiza a tabela de agendamentos com os dados atuais"""
        # Limpar tabela
        for item in self.tabela_agendamentos.get_children():
            self.tabela_agendamentos.delete(item)
        
        # Adicionar agendamentos à tabela
        for agendamento in self.consultas:
            pago_flag = agendamento.get('status_pagameto')
            pagamento_txt = 'Pago' if (str(pago_flag) == '1' or pago_flag == 1 or pago_flag is True) else 'Aberto'
            chegada_raw = agendamento.get('horario_chegada')
            chegada_txt = ''
            try:
                # suporta datetime/time/str e exibe HORA e DATA (HH:MM DD/MM)
                if chegada_raw:
                    s = str(chegada_raw)
                    # ISO: "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DDTHH:MM:SS"
                    if len(s) >= 16 and s[4] == '-' and s[7] == '-' and (s[10] == ' ' or s[10] == 'T'):
                        hora_pt = s[11:16]
                        data_pt = f"{s[8:10]}/{s[5:7]}"
                        chegada_txt = f"{hora_pt} {data_pt}"
                    else:
                        chegada_txt = s
            except Exception:
                chegada_txt = str(chegada_raw) if chegada_raw is not None else ''
            self.tabela_agendamentos.insert(
                '', 
                'end',
                values=(
                    agendamento['hora_consulta'],
                    agendamento['paciente_nome'],
                    agendamento['medico_nome'],
                    agendamento.get('tipo_agendamento') or 'Consulta',
                    agendamento['status'],
                    pagamento_txt,
                    chegada_txt,
                    agendamento['id']  # ID da consulta
                )
            )

    def _marcar_chegada(self):
        """Marca a chegada do paciente na consulta selecionada e sincroniza pagamento."""
        try:
            sel = self.tabela_agendamentos.selection()
            if not sel:
                messagebox.showinfo("Consultas", "Selecione uma consulta para marcar a chegada.")
                return
            item_id = sel[0]
            valores = self.tabela_agendamentos.item(item_id, 'values')
            consulta_id = int(valores[-1])  # última coluna é o ID

            ok, msg = self.agenda_controller.marcar_chegada(consulta_id)
            if not ok:
                messagebox.showerror("Consultas", msg)
                return

            # Tenta sincronizar pagamento automaticamente com base no financeiro
            try:
                ok2, msg2, pago = self.agenda_controller.sincronizar_status_pagamento(consulta_id)
                # Não precisa exibir mensagem sempre; apenas atualiza a tela
            except Exception:
                pass

            # Recarrega a lista do dia atual mantendo filtro
            try:
                data_sel = self.calendario.selection_get()
                data_fmt = data_sel.strftime('%Y-%m-%d')
            except Exception:
                data_fmt = datetime.now().strftime('%Y-%m-%d')

            medico_nome = self.filtro_medico.get() if hasattr(self, 'filtro_medico') else 'Todos'
            if medico_nome and medico_nome != 'Todos':
                mid = self._obter_id_medico_por_nome(medico_nome)
                self.consultas = self.agenda_controller.buscar_consultas_por_medico(mid, data_fmt, data_fmt)
            else:
                self.consultas = self._buscar_agendamentos(data_inicio=data_fmt, data_fim=data_fmt)
            self._atualizar_tabela_agendamentos()
        except Exception as e:
            messagebox.showerror("Consultas", f"Falha ao marcar chegada: {e}")

    def _refresh_consultas_periodico(self):
        """Atualiza periodicamente a lista do dia para refletir pagamentos/chegadas."""
        try:
            try:
                data_sel = self.calendario.selection_get()
                data_fmt = data_sel.strftime('%Y-%m-%d')
            except Exception:
                data_fmt = datetime.now().strftime('%Y-%m-%d')

            medico_nome = self.filtro_medico.get() if hasattr(self, 'filtro_medico') else 'Todos'
            if medico_nome and medico_nome != 'Todos':
                mid = self._obter_id_medico_por_nome(medico_nome)
                if mid:
                    self.consultas = self.agenda_controller.buscar_consultas_por_medico(mid, data_fmt, data_fmt)
            else:
                self.consultas = self._buscar_agendamentos(data_inicio=data_fmt, data_fim=data_fmt)
            # Sincroniza status de pagamento das consultas visíveis (se necessário)
            try:
                for c in (self.consultas or []):
                    pago_flag = c.get('status_pagameto')
                    if not (str(pago_flag) == '1' or pago_flag == 1 or pago_flag is True):
                        try:
                            self.agenda_controller.sincronizar_status_pagamento(int(c['id']))
                        except Exception:
                            pass
                # Recarrega após sincronização para refletir alterações
                if medico_nome and medico_nome != 'Todos' and 'mid' in locals() and mid:
                    self.consultas = self.agenda_controller.buscar_consultas_por_medico(mid, data_fmt, data_fmt)
                else:
                    self.consultas = self._buscar_agendamentos(data_inicio=data_fmt, data_fim=data_fmt)
            except Exception:
                pass
            if hasattr(self, 'tabela_agendamentos'):
                self._atualizar_tabela_agendamentos()
        except Exception:
            pass
        finally:
            try:
                self.parent.after(30000, self._refresh_consultas_periodico)
            except Exception:
                pass
    
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
            
            # Verificar se a tabela de agendamentos já foi criada antes de tentar atualizá-la
            if hasattr(self, 'tabela_agendamentos'):
                self._atualizar_tabela_agendamentos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")

    def _filtrar_agendamentos(self, event=None):
        """Filtra os agendamentos com base no médico e data selecionados"""
        try:
            # Verificar se um médico foi selecionado
            if not hasattr(self, 'filtro_medico') or self.filtro_medico.get() == "Selecione um médico":
                self.consultas = []
                self._atualizar_tabela_agendamentos()
                return
                
            # Obter a data selecionada (ou data atual se não houver seleção)
            try:
                data_selecionada = self.calendario.selection_get()
            except:
                data_selecionada = datetime.now()
                
            data_formatada = data_selecionada.strftime('%Y-%m-%d')
            
            # Obter o médico selecionado
            nome_medico = self.filtro_medico.get()
            
            # Buscar ID do médico
            medico_id = self._obter_id_medico_por_nome(nome_medico)
            
            if not medico_id:
                messagebox.showwarning("Aviso", "Médico não encontrado!")
                return
                
            # Buscar agendamentos usando o ID do médico
            self.consultas = self.agenda_controller.buscar_consultas_por_medico(
                medico_id=medico_id,
                data_inicio=data_formatada,
                data_fim=data_formatada
            )
                
            # Atualizar tabela
            self._atualizar_tabela_agendamentos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar agendamentos: {str(e)}")

    def _ao_selecionar_medico(self, event=None):
        """Chamado quando um médico é selecionado"""
        # Obtém o nome do médico selecionado
        nome_medico = self.filtro_medico.get()
        if not nome_medico or nome_medico == "Todos":
            return
            
        # Obtém o ID do médico
        medico_id = self._obter_id_medico_por_nome(nome_medico)
        if not medico_id:
            return
            
        try:
            # Carrega os exames do médico
            exames = self.agenda_controller.buscar_exames_por_medico(medico_id)
            
            # Armazena os exames para acesso rápido
            self.exames_medico = {str(exame['id']): exame for exame in exames}
            
            # Atualiza o combobox de exames (se existir)
            if hasattr(self, 'combobox_exame'):
                valores_exames = [(str(e['id']), e['nome']) for e in exames]
                self._atualizar_combobox_exames(valores_exames)
            
            # Mostra o calendário com os dias disponíveis do médico
            self._mostrar_calendario_medico()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar exames: {str(e)}")

    def _atualizar_combobox_exames(self, exames):
        """Atualiza o combobox com a lista de exames"""
        if not hasattr(self, 'combobox_exame'):
            # Cria o combobox se não existir
            frame_exame = ttk.Frame(self.filtros_frame)
            frame_exame.pack(side='left', padx=(10, 0), pady=5)
            
            ttk.Label(frame_exame, text="Exame:").pack(side='left', padx=(0, 5))
            self.combobox_exame = ttk.Combobox(frame_exame, state='readonly', width=25)
            self.combobox_exame.pack(side='left')
            self.combobox_exame.bind('<<ComboboxSelected>>', self._ao_selecionar_exame)
        
        # Atualiza os valores do combobox
        self.combobox_exame['values'] = [nome for _, nome in exames]
        self.combobox_exame.set('')  # Limpa a seleção
        self.combobox_exame['state'] = 'readonly' if exames else 'disabled'
    
    def _ao_selecionar_exame(self, event=None):
        """Chamado quando um exame é selecionado"""
        # Obtém o ID do exame selecionado
        exame_id = self.combobox_exame.get()
        
        # Verifica se o exame existe no dicionário
        
        if exame_id and exame_id in self.exames_medico:
            # Atualiza o tempo do exame
            self.tempo_exame = self.exames_medico[exame_id]['tempo']
            
            # Atualiza a interface (se necessário)
            if hasattr(self, 'label_tempo_exame'):
                self.label_tempo_exame.config(
                    text=f"Tempo: {self.tempo_exame} min"
                )
                
            # Mostra o calendário com os dias disponíveis do médico
            self._mostrar_calendario_medico()
    def _carregar_exames_medico(self, medico_id):
        """Carrega os exames/consultas de um médico específico"""
        try:
            exames = self.agenda_controller.buscar_exames_por_medico(medico_id)
            self.exames_medico = {str(e['id']): e for e in exames}
            return [e['nome'] for e in exames]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar exames: {str(e)}")
            return []
                
    def _novo_agendamento(self):
        """Abre o formulário para criar um novo agendamento."""
        try:
            # Verificar se há médicos cadastrados
            if not self.medicos:
                messagebox.showwarning("Aviso", "Não há médicos cadastrados!")
                return

            # Criar a janela de agendamento
            self.janela_agendamento = tk.Toplevel(self.parent)
            self.janela_agendamento.title("Novo Agendamento")
            self.janela_agendamento.resizable(False, False)
            self.janela_agendamento.grab_set()
            
            # Centralizar a janela
            window_width = 500
            window_height = 700  # Aumentado para acomodar o novo campo
            screen_width = self.janela_agendamento.winfo_screenwidth()
            screen_height = self.janela_agendamento.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            self.janela_agendamento.geometry(f'{window_width}x{window_height}+{x}+{y}')
            
            # Frame principal
            main_frame = tk.Frame(self.janela_agendamento, bg='#f0f2f5', padx=20, pady=20)
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
            
            # Dicionário para armazenar referências aos campos
            campos = {}
            
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
                    campo.grid(row=row, column=1, sticky='ew', pady=5, padx=(0, 10))
                    return campo, var
                else:  # É um Entry normal
                    var = tk.StringVar()
                    campo = ttk.Entry(
                        container,
                        textvariable=var,
                        font=('Arial', 10)
                    )
                    campo.grid(row=row, column=1, sticky='ew', pady=5, padx=(0, 10))
                    return campo, var
            
            # Paciente
            campo_paciente, var_paciente = criar_campo(
                campos_frame,
                "Paciente",
                0,
                values=[p['nome'] for p in self.pacientes]
            )
            campos['paciente'] = campo_paciente
            
            # Botão para novo paciente
            def abrir_cadastro_paciente():
                # Implemente a abertura do cadastro de paciente aqui
                pass
                
            btn_novo_paciente = tk.Button(
                campos_frame,
                text="Novo Paciente",
                command=abrir_cadastro_paciente,
                bg='#4a6fa5',
                fg='white',
                font=('Arial', 9, 'bold'),
                bd=0,
                padx=10,
                pady=3
            )
            btn_novo_paciente.grid(row=0, column=2, padx=(5, 0), pady=5)
            
            # Médico
            self.campo_medico, var_medico = criar_campo(
                campos_frame,
                "Médico",
                1,
                values=[m['nome'] for m in self.medicos]
            )
            campos['medico'] = self.campo_medico

            if not self.tipos_atendimento_map:
                messagebox.showerror("Erro", "Não foi possível carregar os tipos de atendimento.")
                self.janela_agendamento.destroy()
                return

            # Campo de Tipo de Atendimento (já existe, apenas mostrando o contexto)
            campo_tipo, var_tipo = criar_campo(
                campos_frame,
                "Tipo de Atendimento",
                2,
                values=[]
                
            )
            campos['tipo_atendimento'] = campo_tipo
                        
            
            # Label para mostrar a duração
            lbl_duracao = tk.Label(
                campos_frame,
                text="Duração: -",
                font=('Arial', 10),
                anchor='w'
            )
            lbl_duracao.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))
                        
            def atualizar_duracao(*args):
                try:
                    tipo_selecionado = var_tipo.get()
                    if tipo_selecionado in self.tipos_atendimento_map:
                        duracao = self.tipos_atendimento_map[tipo_selecionado]['tempo']
                        lbl_duracao.config(text=f"Duração: {duracao} minutos")
                    else:
                        lbl_duracao.config(text="Duração: -")
                except Exception as e:
                    print(f"Erro ao atualizar duração: {e}")
                    lbl_duracao.config(text="Duração: -")
            
            var_tipo.trace('w', atualizar_duracao)
            
            # Adicione esta função aqui
            def ao_selecionar_medico(event=None):
                # Limpa o tipo de atendimento atual
                var_tipo.set('')
                
                # Obtém o médico selecionado
                nome_medico = self.campo_medico.get()
                if not nome_medico:
                    # Se não tiver médico selecionado, mostra mensagem e desabilita
                    campo_tipo['values'] = ["Selecione um médico primeiro"]
                    campo_tipo.set("Selecione um médico primeiro")
                    campo_tipo['state'] = 'readonly'
                    return
                    
                # Obtém o ID do médico
                medico_id = self._obter_id_medico_por_nome(nome_medico)
                if not medico_id:
                    campo_tipo['values'] = ["Erro ao carregar médico"]
                    campo_tipo.set("Erro ao carregar médico")
                    campo_tipo['state'] = 'readonly'
                    return
                
                self._configurar_calendario_medico(medico_id)
                    
                try:
                    # Carrega os exames do médico
                    exames = self._carregar_exames_medico(medico_id)
                    
                    # Atualiza o combobox de tipos de atendimento
                    if exames:
                        campo_tipo['values'] = exames
                        campo_tipo.set("Selecione um exame/consulta")  # Mensagem padrão
                        campo_tipo['state'] = 'readonly'
                    else:
                        campo_tipo['values'] = ["Nenhum exame disponível"]
                        campo_tipo.set("Nenhum exame disponível")
                        campo_tipo['state'] = 'readonly'
                        
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao carregar exames: {str(e)}")
                    campo_tipo['values'] = ["Erro ao carregar exames"]
                    campo_tipo.set("Erro ao carregar exames")
                    campo_tipo['state'] = 'readonly'
            
            # Adicione o evento ao combobox de médicos
            self.campo_medico.bind('<<ComboboxSelected>>', ao_selecionar_medico)

            var_tipo.set("Selecione um médico primeiro")
            
            
            # Data (o código que já existe continua aqui)
            tk.Label(
                campos_frame,
                text="Data:",
                font=('Arial', 10),
                anchor='w'
            ).grid(row=4, column=0, sticky='w', pady=5)
            
            # Data
            tk.Label(
                campos_frame,
                text="Data:",
                font=('Arial', 10),
                anchor='w'
            ).grid(row=4, column=0, sticky='w', pady=5)

            data_frame = ttk.Frame(campos_frame)
            data_frame.grid(row=4, column=1, sticky='w', pady=5)

            # Frame para o campo de data
            frame_data = ttk.Frame(data_frame)
            frame_data.pack(fill='x')

            

            # Campo de entrada de data
            self.entry_data = ttk.Entry(
                frame_data,
                width=12,
                validate="key",
                validatecommand=(self.frame.register(self._validar_data), '%P')
            )
            self.entry_data.pack(side='left', padx=(0, 5))

            self.data_entry = self.entry_data
            
            # Botão para abrir o calendário
            btn_calendario = tk.Button(
                frame_data,
                text="📅",
                font=('Arial', 10),
                command=self._mostrar_calendario_medico,
                bg='#4a90e2',
                fg='white',
                bd=0,
                padx=5,
                pady=0,
                relief='flat',
                cursor='hand2'
            )
            btn_calendario.pack(side='left')

            # Adiciona um evento quando o campo perde o foco
            self.entry_data.bind('<FocusOut>', lambda e: self._atualizar_horarios_disponiveis())
            
            # 2. Crie o campo_hora
            campo_hora, var_hora = criar_campo(
                campos_frame,
                "Hora",
                5,
                values=[f"{h:02d}:00" for h in range(8, 19)] + 
                    [f"{h:02d}:30" for h in range(8, 19)]
            )

            # 3. Agora que campo_hora existe, podemos atribuí-lo a self.campo_hora
            self.campo_hora = campo_hora

            
            # Status
            campo_status, var_status = criar_campo(
                campos_frame,
                "Status",
                6,
                values=['Agendado', 'Confirmado', 'Cancelado', 'Realizado']
            )
            var_status.set('Agendado')  # Valor padrão
            
            # Observações
            ttk.Label(campos_frame, text="Observações", font=('Arial', 10), anchor='w').grid(row=7, column=0, sticky='nw', pady=5)
            var_obs = tk.Text(campos_frame, width=40, height=5, font=('Arial', 10))
            var_obs.grid(row=7, column=1, sticky='nsew', pady=5, padx=(0, 10))
            # Corretor ortográfico (opcional)
            try:
                self._enable_spellcheck(var_obs)
            except Exception:
                pass
            
            # Frame para os botões
            botoes_frame = tk.Frame(main_frame, bg='#f0f2f5', pady=20)
            botoes_frame.pack(fill='x', side='bottom')
            
            # Função para salvar o agendamento
            def salvar():
                try:
                    # Validações iniciais
                    if not var_paciente.get():
                        messagebox.showwarning("Aviso", "Selecione um paciente!")
                        return
                        
                    if not var_medico.get():
                        messagebox.showwarning("Aviso", "Selecione um médico!")
                        return
                        
                    # Obter o ID do paciente
                    paciente_id = None
                    for p in self.pacientes:
                        if p['nome'] == var_paciente.get():
                            paciente_id = p['id']
                            break
                            
                    if not paciente_id:
                        messagebox.showerror("Erro", "Paciente não encontrado!")
                        return
                        
                    # Obter o ID do médico
                    medico_id = None
                    for m in self.medicos:
                        if m['nome'] == var_medico.get():
                            medico_id = m['id']
                            break
                            
                    if not medico_id:
                        messagebox.showerror("Erro", "Médico não encontrado!")
                        return

                    # Valida tipo de atendimento
                    tipo_selecionado = var_tipo.get()
                    if not tipo_selecionado or tipo_selecionado == "Selecione um médico primeiro":
                        messagebox.showwarning("Aviso", "Selecione um tipo de atendimento!")
                        return
                        
                    # Validar data e hora
                    try:
                        data_str = self.entry_data.get()
                        data_consulta = datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                        hora = campo_hora.get()
                        if not hora:
                            messagebox.showwarning("Aviso", "Selecione um horário!")
                            return
                    except Exception as e:
                        messagebox.showerror("Erro", f"Data inválida: {str(e)}")
                        return
                        
                    # Validar tipo de atendimento
                    disponivel, mensagem = self.validar_horario_disponivel(
                        medico_id,
                        data_consulta,
                        hora,
                        self.tipos_atendimento_map[tipo_selecionado]['tempo']
                    )
                    if not disponivel:  
                        messagebox.showwarning("Horário Indisponível", mensagem)
                        try:
                            if hasattr(self, 'janela_agendamento') and self.janela_agendamento.winfo_exists():
                                self.janela_agendamento.lift()
                                self.janela_agendamento.focus_force()
                                # topmost temporário para garantir ficar acima
                                self.janela_agendamento.attributes('-topmost', True)
                                self.janela_agendamento.after(150, lambda: self.janela_agendamento.attributes('-topmost', False))
                        except Exception:
                            pass
                        return

                                            
                    # Montar dicionário com os dados
                    dados_consulta = {
                        'paciente_id': paciente_id,
                        'medico_id': medico_id,
                        'tipo_atendimento': tipo_selecionado,
                        'data': data_consulta,
                        'hora': hora,
                        'status': var_status.get(),
                        'observacoes': var_obs.get('1.0', tk.END).strip()
                    }
                    
                    # Salvar no banco de dados
                    sucesso, mensagem = self.agenda_controller.salvar_consulta(dados_consulta)
                    
                    if sucesso:
                        messagebox.showinfo("Sucesso", mensagem)
                        # Atualizar a lista de consultas
                        self._carregar_dados_iniciais()
                        # Fechar a janela de agendamento
                        if hasattr(self, 'janela_agendamento') and self.janela_agendamento.winfo_exists():
                            self.janela_agendamento.destroy()
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
                command=self.janela_agendamento.destroy,
                bg='#f44336',
                fg='white',
                font=('Arial', 10, 'bold'),
                bd=0,
                padx=20,
                pady=8,
                relief='flat',
                activebackground='#d32f2f',
                activeforeground='white'
            )
            btn_cancelar.pack(side='left', padx=5)
            
            # Configurar o grid para expandir corretamente
            campos_frame.columnconfigure(1, weight=1)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir formulário de agendamento: {str(e)}")
    
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

                
                # Criar janela de edição (modo edição simplificada)
                self.criar_formulario_edicao(consulta)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar dados da consulta: {str(e)}")
                import traceback
                print(traceback.format_exc())
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar consulta: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def criar_formulario_edicao(self, consulta):
        """Abre o formulário de edição isolado do fluxo de 'novo agendamento'."""
        # Ativa modo edição simplificada (usado dentro de _abrir_formulario_consulta)
        setattr(self, '_edicao_simplificada', True)
        try:
            self._abrir_formulario_consulta(consulta)
        finally:
            # Garantir que o flag seja sempre desligado
            try:
                delattr(self, '_edicao_simplificada')
            except Exception:
                setattr(self, '_edicao_simplificada', False)

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
        
        try:
            campo_data = DateEntry(
                campos_frame,
                textvariable=var_data,
                date_pattern='dd/mm/yyyy',
                locale='pt_BR',
                width=17
            )
        except Exception:
            # Fallback de locale para ambientes empacotados sem recursos de locale
            campo_data = DateEntry(
                campos_frame,
                textvariable=var_data,
                date_pattern='dd/mm/yyyy',
                locale='en_US',
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
            var_hora.set(hora_str[:5])  # Normaliza para HH:MM
        
        # Combo de hora (valores dinâmicos conforme médico/data)
        campo_hora = ttk.Combobox(campos_frame, textvariable=var_hora, values=[], width=17)
        campo_hora.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))

        # Campo de Tipo de Atendimento (edição)
        ttk.Label(campos_frame, text="Tipo de Atendimento").grid(row=4, column=0, sticky='w', pady=5)
        var_tipo = tk.StringVar()
        campo_tipo = ttk.Combobox(campos_frame, textvariable=var_tipo, values=[], width=30, state='readonly')
        campo_tipo.grid(row=4, column=1, sticky='w', pady=5, padx=(10, 0))

        # Pré-carregar com valor atual se houver
        try:
            if consulta.get('tipo_atendimento'):
                var_tipo.set(consulta['tipo_atendimento'])
        except Exception:
            pass

        # Função para carregar exames pelo médico selecionado
        def _carregar_tipos_para_medico_nome(nome_medico: str):
            try:
                if not nome_medico:
                    campo_tipo['values'] = []
                    return
                medico_id_local = None
                for m in getattr(self, 'medicos', []):
                    if m.get('nome') == nome_medico:
                        medico_id_local = m.get('id')
                        break
                if not medico_id_local:
                    campo_tipo['values'] = []
                    return
                exames = self.agenda_controller.buscar_exames_por_medico(medico_id_local)
                nomes = [e.get('nome') for e in (exames or [])]
                campo_tipo['values'] = nomes
                # Se o valor atual não pertence mais, limpa
                if var_tipo.get() and var_tipo.get() not in nomes:
                    var_tipo.set('')
            except Exception:
                campo_tipo['values'] = []

        # Ao mudar médico, recarrega tipos
        try:
            _carregar_tipos_para_medico_nome(var_medico.get())
            campo_medico.bind('<<ComboboxSelected>>', lambda e: _carregar_tipos_para_medico_nome(var_medico.get()))
        except Exception:
            pass

        # Modo de edição simplificada: limpar Data e Hora ao abrir
        if getattr(self, '_edicao_simplificada', False):
            try:
                var_data.set("")
            except Exception:
                pass
            try:
                campo_hora['values'] = []
                var_hora.set("")
            except Exception:
                pass

        # Função para atualizar horários disponíveis (10 em 10 minutos) conforme médico/data
        def _atualizar_horarios_edicao():
            try:
                medico_nome = var_medico.get()
                if not medico_nome:
                    campo_hora['values'] = []
                    var_hora.set('')
                    return
                # Encontrar medico_id
                medico_id = None
                for m in self.medicos:
                    if m['nome'] == medico_nome:
                        medico_id = m['id']
                        break
                if not medico_id:
                    campo_hora['values'] = []
                    var_hora.set('')
                    return

                # Obter data
                data_txt = var_data.get()
                if not data_txt:
                    campo_hora['values'] = []
                    var_hora.set('')
                    return
                try:
                    data_dt = datetime.strptime(data_txt, '%d/%m/%Y').date()
                except Exception:
                    campo_hora['values'] = []
                    var_hora.set('')
                    return
                dia_semana = data_dt.weekday()

                # Buscar faixas disponíveis (mesma fonte do novo agendamento)
                horario_controller = HorarioController(self.db_connection)
                faixas = horario_controller.obter_horarios_disponiveis(medico_id, dia_semana)
                if not faixas:
                    campo_hora['values'] = []
                    var_hora.set('')
                    return

                # Helper para converter para datetime base (HH:MM)
                def to_datetime_hm(value):
                    """Converte value (time | timedelta | str HH:MM[:SS]) em datetime base 1900-01-01 com hora/min."""
                    base = datetime(1900, 1, 1)
                    # time
                    try:
                        return datetime.combine(base.date(), value)
                    except Exception:
                        pass
                    # timedelta
                    try:
                        total = int(value.total_seconds())
                        horas = total // 3600
                        minutos = (total % 3600) // 60
                        return base.replace(hour=horas, minute=minutos, second=0, microsecond=0)
                    except Exception:
                        pass
                    # str HH:MM[:SS]
                    try:
                        txt = str(value)
                        if len(txt) == 8:
                            return datetime.strptime(txt, '%H:%M:%S')
                        return datetime.strptime(txt[:5], '%H:%M')
                    except Exception:
                        return None

                # Geração dos slots de 10 em 10 minutos
                slots = []
                for faixa in faixas:
                    h_ini = to_datetime_hm(faixa.get('hora_inicio'))
                    h_fim = to_datetime_hm(faixa.get('hora_fim'))
                    if not h_ini or not h_fim:
                        continue
                    # Gera de 10 em 10 minutos, incluindo o limite final
                    t = h_ini
                    while t <= h_fim:
                        slots.append(t.strftime('%H:%M'))
                        t += timedelta(minutes=10)
                slots = sorted(set(slots))

                # Atualiza combobox, preservando seleção válida
                selecionada = var_hora.get()
                campo_hora['values'] = slots
                if selecionada in slots:
                    var_hora.set(selecionada)
                elif slots:
                    var_hora.set(slots[0])
                else:
                    var_hora.set('')
            except Exception:
                campo_hora['values'] = []
                var_hora.set('')

        # Validação de dia disponível para o médico no formulário de edição
        def _dia_tem_atendimento():
            try:
                medico_nome = var_medico.get()
                data_txt = var_data.get()
                if not medico_nome or not data_txt:
                    return False
                # medico_id
                medico_id = None
                for m in self.medicos:
                    if m['nome'] == medico_nome:
                        medico_id = m['id']
                        break
                if not medico_id:
                    return False
                # data -> weekday
                try:
                    data_dt = datetime.strptime(data_txt, '%d/%m/%Y').date()
                except Exception:
                    return False
                dia_semana = data_dt.weekday()
                # checar faixas no dia
                horario_controller = HorarioController(self.db_connection)
                faixas = horario_controller.obter_horarios_disponiveis(medico_id, dia_semana)
                return bool(faixas)
            except Exception:
                return False

        def _validar_dia_disponivel(event=None):
            # Não validar nem limpar durante a carga inicial
            if getattr(self, '_loading_edicao', False):
                return True
            if not _dia_tem_atendimento():
                try:
                    messagebox.showwarning("Aviso", "O médico não atende nesse dia. Selecione outra data.")
                except Exception:
                    pass
                var_data.set("")
                if 'campo_hora' in locals():
                    try:
                        campo_hora['values'] = []
                        var_hora.set('')
                    except Exception:
                        pass
                return False
            return True

        # Flag de carga para suprimir validações no início
        self._loading_edicao = True

        # Binds para atualizar quando campos mudarem
        try:
            if not getattr(self, '_edicao_simplificada', False):
                campo_medico.bind('<<ComboboxSelected>>', lambda e: (_validar_dia_disponivel(e), _atualizar_horarios_edicao()))
        except Exception:
            pass
        try:
            campo_data.bind('<<DateEntrySelected>>', lambda e: (_validar_dia_disponivel(e), _atualizar_horarios_edicao()))
            campo_data.bind('<FocusOut>', lambda e: (_validar_dia_disponivel(e), _atualizar_horarios_edicao()))
        except Exception:
            pass
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
        # Corretor ortográfico (opcional)
        try:
            self._enable_spellcheck(var_obs)
        except Exception:
            pass
        
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
            tipo_atendimento = var_tipo.get()
            
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
                messagebox.showerror("Erro", "Formato de data inválido. Use o formato dd/mm/aaaa")
                return
            
            # Preparar dados para atualização
            dados_consulta = {
                'id': consulta['id'],
                'paciente_id': paciente_id,
                'medico_id': medico_id,
                'data': data_formatada,
                'hora': hora,
                'status': status,
                'observacoes': observacoes,
                'tipo_atendimento': tipo_atendimento or None
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

        # Validação de conflito e disponibilidade deve ocorrer apenas dentro de salvar_edicao()

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

        self._loading_edicao = False

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
    
    def buscar_tipos_atendimento(self, medico_id=None):
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            if medico_id:
                # Buscar apenas os tipos de atendimento associados ao médico
                cursor.execute("""
                    SELECT e.id, e.nome, e.tempo, e.valor 
                    FROM exames_consultas e
                    INNER JOIN medico_exames me ON e.id = me.exame_id
                    WHERE me.medico_id = %s
                    ORDER BY e.nome
                """, (medico_id,))
            else:
                # Buscar todos os tipos de atendimento
                cursor.execute("""
                    SELECT id, nome, tempo, valor 
                    FROM exames_consultas 
                    ORDER BY nome
                """)
                
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar exames/consultas: {str(e)}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()

    def carregar_tipos_atendimento(self):
        """Carrega os tipos de atendimento do banco de dados"""
        try:
            tipos = self.buscar_tipos_atendimento()
            if tipos:
                self.tipos_atendimento_map = {
                    tipo['nome']: {
                        'id': tipo['id'],
                        'tempo': tipo['tempo'],
                        'valor': tipo.get('valor', 0)
                    } 
                    for tipo in tipos
                }
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar tipos de atendimento: {str(e)}")
            self.tipos_atendimento_map = {}
    
    def _obter_id_medico_por_nome(self, nome_medico):
        """Retorna o ID do médico com base no nome"""
        for medico in self.medicos:
            if medico['nome'] == nome_medico:
                return medico['id']
        return None
    
    def _configurar_calendario_medico(self, medico_id):
        """Configura o calendário para mostrar apenas os dias em que o médico atende"""
        # Se não tiver um médico selecionado, não faz nada
        if not medico_id:
            return
        
        # Obtém os dias da semana em que o médico atende (0=segunda, 6=domingo)
        horario_controller = HorarioController(self.db_connection)
        dias_atendimento = horario_controller.obter_dias_atendimento(medico_id)
        
        # Se não houver dias de atendimento, mostra mensagem
        if not dias_atendimento:
            messagebox.showwarning("Aviso", "Este médico não possui horários cadastrados!")
            return
        
        # Configura o DateEntry para permitir apenas os dias de atendimento
        def dia_permitido(date):
            # Verifica se o dia da semana está na lista de dias de atendimento
            return date.weekday() in dias_atendimento
        
        # Aplica a validação ao DateEntry
        if hasattr(self, 'data_entry'):
            self.data_entry['validate'] = 'all'
            # Permite vazio/parcial durante digitação; só valida quando a data estiver completa e válida
            def _vc_data(d):
                try:
                    if not d or len(d) < 10:
                        return True
                    dt = datetime.strptime(d, '%d/%m/%Y').date()
                    return dia_permitido(dt)
                except Exception:
                    # Durante digitação pode haver formatos parciais; não bloquear
                    return True
            self.data_entry['validatecommand'] = (self.data_entry.register(_vc_data), '%P')

    def _atualizar_horarios_disponiveis(self):
        """Atualiza os horários disponíveis para o médico na data selecionada"""
        try:
            # Verifica se os campos necessários existem
            if not hasattr(self, 'campo_medico') or not hasattr(self, 'entry_data') or not hasattr(self, 'campo_hora'):
                return
                
            # Obtém o médico selecionado
            nome_medico = self.campo_medico.get()
            if not nome_medico:
                messagebox.showwarning("Aviso", "Selecione um médico primeiro")
                return
                
            # Obtém o ID do médico
            medico_id = self._obter_id_medico_por_nome(nome_medico)
            if not medico_id:
                messagebox.showwarning("Aviso", "Médico não encontrado")
                return
                
            # Obtém a data selecionada
            data_str = self.entry_data.get()
            if not data_str:
                return
                
            # Converte a string de data para objeto datetime
            try:
                data_partes = data_str.split('/')
                if len(data_partes) != 3:
                    return
                    
                dia, mes, ano = map(int, data_partes)
                data = datetime(ano, mes, dia).date()
            except ValueError:
                messagebox.showwarning("Aviso", "Data inválida")
                return
                
            # Obtém o dia da semana (0=segunda, 1=terça, ..., 6=domingo)
            dia_semana = data.weekday()
                
            # Obtém os horários disponíveis para o médico neste dia da semana
            horario_controller = HorarioController(self.db_connection)
            horarios_disponiveis = horario_controller.obter_horarios_disponiveis(medico_id, dia_semana)
            
            if not horarios_disponiveis:
                messagebox.showwarning("Aviso", "Não há horários disponíveis para este médico nesta data")
                # Limpa o combobox de horários
                self.campo_hora['values'] = []
                self.campo_hora.set("")
                return
                
            # Formata os horários para exibição (HH:MM)
            horarios_formatados = []
            def to_datetime_hm(value):
                """Converte value (time | timedelta | str HH:MM[:SS]) em datetime base 1900-01-01 com hora/min."""
                base = datetime(1900, 1, 1)
                try:
                    # time
                    return datetime.combine(base.date(), value)
                except Exception:
                    pass
                try:
                    # timedelta
                    total = int(value.total_seconds())
                    horas = total // 3600
                    minutos = (total % 3600) // 60
                    return base.replace(hour=horas, minute=minutos, second=0, microsecond=0)
                except Exception:
                    pass
                try:
                    # string
                    txt = str(value)
                    if len(txt) == 8:  # HH:MM:SS
                        return datetime.strptime(txt, '%H:%M:%S')
                    return datetime.strptime(txt[:5], '%H:%M')
                except Exception:
                    return None

            for intervalo in horarios_disponiveis:
                try:
                    h_ini = to_datetime_hm(intervalo.get('hora_inicio'))
                    h_fim = to_datetime_hm(intervalo.get('hora_fim'))
                    if not h_ini or not h_fim:
                        continue
                    # Gera de 10 em 10 minutos, incluindo o limite final
                    t = h_ini
                    while t <= h_fim:
                        horarios_formatados.append(t.strftime('%H:%M'))
                        t += timedelta(minutes=10)
                except Exception as e:
                    print(f"Erro ao processar intervalo: {e}")
                    continue
            
            # Remove duplicados e ordena
            horarios_formatados = sorted(set(horarios_formatados))
            
            # Atualiza o combobox de horários
            self.campo_hora['values'] = horarios_formatados
            if horarios_formatados:
                self.campo_hora.set(horarios_formatados[0])  # Seleciona o primeiro horário disponível
            else:
                self.campo_hora.set("")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar horários disponíveis: {str(e)}")
    
    def _validar_data(self, texto):
        """Valida o formato da data digitada"""
        if not texto:  # Se o campo estiver vazio, permita
            return True
        try:
            datetime.strptime(texto, '%d/%m/%Y')
            return True
        except ValueError:
            return False

    def _obter_data(self):
        """Obtém e valida a data do campo"""
        try:
            texto = self.entry_data.get().strip()
            if not texto:
                return None
            # Remove espaços extras e formata a data
            texto = texto.replace(' ', '')
            return datetime.strptime(texto, '%d/%m/%Y').date()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa")
            return None
            
    def _mostrar_calendario_medico(self):
        """Mostra um calendário com apenas os dias em que o médico atende"""
        # Verifica se está sendo chamado do formulário de novo agendamento
        nome_medico = None
        
        # Verifica se está no formulário de novo agendamento
        if hasattr(self, 'campo_medico'):
            try:
                # Tenta obter o valor do campo_medico
                nome_medico = self.campo_medico.get()
            except (tk.TclError, AttributeError):
                # Se der erro, provavelmente o campo não existe mais ou não é um widget válido
                nome_medico = None
        
        # Se não encontrou no campo_medico, tenta no filtro_medico (tela principal)
        if not nome_medico and hasattr(self, 'filtro_medico'):
            try:
                nome_medico = self.filtro_medico.get()
                if nome_medico == "Todos":
                    nome_medico = None
            except (tk.TclError, AttributeError):
                nome_medico = None
        
        if not nome_medico:
            messagebox.showwarning("Aviso", "Selecione um médico primeiro")
            return
            
        medico_id = self._obter_id_medico_por_nome(nome_medico)
        if not medico_id:
            messagebox.showwarning("Aviso", "Médico não encontrado")
            return

        # Obtém os dias da semana em que o médico atende
        horario_controller = HorarioController(self.db_connection)
        dias_atendimento = horario_controller.obter_dias_atendimento(medico_id)
        
        if not dias_atendimento:
            messagebox.showwarning("Aviso", "Este médico não possui horários cadastrados")
            return
            
        # Cria uma janela para o calendário
        janela_calendario = tk.Toplevel(self.parent)
        janela_calendario.title("Calendário de Atendimento")
        janela_calendario.geometry("350x400")
        janela_calendario.resizable(False, False)
        janela_calendario.transient(self.parent)
        janela_calendario.focus_force()
        janela_calendario.grab_set()
        
        # Centralizar a janela
        janela_calendario.update_idletasks()
        width = janela_calendario.winfo_width()
        height = janela_calendario.winfo_height()
        x = (janela_calendario.winfo_screenwidth() // 2) - (width // 2)
        y = (janela_calendario.winfo_screenheight() // 2) - (height // 2)
        janela_calendario.geometry(f"350x400+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(janela_calendario, bg='#f0f2f5', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        tk.Label(
            main_frame, 
            text=f"Calendário de Atendimento\n{nome_medico}", 
            font=('Arial', 14, 'bold'),
            bg='#f0f2f5'
        ).pack(pady=(0, 20))
        
        # Mapeia os dias da semana para nomes
        dias_semana = {
            0: "Segunda-feira",
            1: "Terça-feira",
            2: "Quarta-feira",
            3: "Quinta-feira",
            4: "Sexta-feira",
            5: "Sábado",
            6: "Domingo"
        }
        
        # Mostra os dias de atendimento
        dias_texto = ", ".join([dias_semana[dia] for dia in dias_atendimento])
        tk.Label(
            main_frame,
            text=f"Dias de atendimento:\n{dias_texto}",
            font=('Arial', 10),
            bg='#f0f2f5',
            justify='left'
        ).pack(anchor='w', pady=(0, 10))
        
        # Função para validar dias no calendário
        def dia_permitido(date):
            # Verifica se o dia da semana está na lista de dias de atendimento
            return date.weekday() in dias_atendimento
        
        # Calendário
        cal = MedicoCalendar(
            main_frame,
            dias_atendimento=dias_atendimento,
            modo='restrito',
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
            font=('Arial', 10)
        )
        cal.pack(fill='both', expand=True, pady=10)
        
        # Garante que, ao selecionar um dia neste calendário, o destaque azul fique no dia clicado
        try:
            cal.bind('<<CalendarSelected>>', lambda e: main_frame.after_idle(cal._display_calendar), add='+')
        except Exception:
            pass
        
        # Função para selecionar a data e fechar o calendário
        def selecionar_data():
            try:
                data_selecionada = cal.selection_get()
                
                # Verifica se a data selecionada é um dia permitido
                if not dia_permitido(data_selecionada):
                    messagebox.showwarning("Aviso", "Este dia não está disponível para atendimento.")
                    return
                
                # Atualiza o campo de data no formulário principal
                if hasattr(self, 'entry_data'):
                    self.entry_data.delete(0, 'end')
                    self.entry_data.insert(0, data_selecionada.strftime('%d/%m/%Y'))
                    
                # Fecha apenas a janela do calendário
                janela_calendario.destroy()

                # Usa after para garantir que a janela seja mostrada após o calendário fechar
                self.parent.after(50, lambda: (
                    self.janela_agendamento.lift(),
                    self.janela_agendamento.focus_force()
                ))
                
                # Atualiza os horários disponíveis após um pequeno delay
                self.parent.after(100, self._atualizar_horarios_disponiveis)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao selecionar data: {str(e)}")
        
        # Botão para selecionar a data
        btn_selecionar = tk.Button(
            main_frame,
            text="Selecionar Data",
            command=selecionar_data,
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
        btn_selecionar.pack(pady=10)
        
        # Botão para cancelar
        btn_cancelar = tk.Button(
            main_frame,
            text="Cancelar",
            command=janela_calendario.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 10, 'bold'),
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            activebackground='#d32f2f',
            activeforeground='white'
        )
        btn_cancelar.pack(pady=5)

    def validar_horario_disponivel(self, medico_id, data, hora_consulta, duracao, ignore_id=None):
        try:
            # 1) Verifica se o médico atende nesse intervalo (agenda base)
            horario_controller = HorarioController(self.db_connection)
            if not horario_controller.verificar_disponibilidade(
                medico_id,
                data,
                hora_consulta,
                duracao
            ):
                return False, "Médico não atende neste horário"

            # 2) Verifica conflitos com consultas existentes na mesma data/médico
            # Normaliza data/hora de entrada
            req_data = data
            if isinstance(req_data, str):
                req_data = datetime.strptime(req_data, '%Y-%m-%d').date()

            # Helper para converter diferentes tipos em datetime.time
            def to_time(h):
                try:
                    from datetime import time as dtime
                    # Já é time
                    if isinstance(h, dtime):
                        return h
                except Exception:
                    pass
                try:
                    # timedelta -> base 00:00 + delta
                    from datetime import timedelta
                    if isinstance(h, timedelta):
                        base = datetime(1900, 1, 1)
                        dt = base + h
                        return dt.time()
                except Exception:
                    pass
                try:
                    # string 'HH:MM' ou 'HH:MM:SS'
                    s = str(h)
                    if len(s) >= 8 and s[2] == ':' and s[5] == ':':
                        return datetime.strptime(s[:8], '%H:%M:%S').time()
                    return datetime.strptime(s[:5], '%H:%M').time()
                except Exception:
                    return None

            hc_time = to_time(hora_consulta)
            if not hc_time:
                return False, "Hora da consulta inválida"
            req_inicio = datetime.combine(req_data, hc_time)

            # Busca consultas existentes do médico nessa data
            cursor = self.db_connection.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT id, hora, tipo_atendimento
                    FROM consultas
                    WHERE medico_id = %s AND data = %s
                    """,
                    (medico_id, req_data.strftime('%Y-%m-%d'))
                )
                rows = cursor.fetchall() or []
            finally:
                cursor.close()

            # Mapa de tipos -> duração (se carregado)
            tipos_map = getattr(self, 'tipos_atendimento_map', {}) or {}

            for row in rows:
                # Ignora a própria consulta em edição
                if ignore_id and row.get('id') == ignore_id:
                    continue

                # Início existente
                h = row.get('hora')
                # Converte hora existente para time
                ex_inicio_time = to_time(h)
                if not ex_inicio_time:
                    # Se não interpretar, ignora esse registro
                    continue
                ex_inicio = datetime.combine(req_data, ex_inicio_time)

                # Duração existente pelo tipo; se não achar, fallback = max(duracao_solicitada, 10)
                ex_tipo = row.get('tipo_atendimento')
                ex_dur = None
                try:
                    if ex_tipo and tipos_map.get(ex_tipo):
                        ex_dur = int(tipos_map[ex_tipo]['tempo'])
                except Exception:
                    ex_dur = None
                if not ex_dur:
                    ex_dur = max(int(duracao or 10), 10)

                ex_fim = ex_inicio + timedelta(minutes=ex_dur)

                # Sobreposição se (req_inicio < ex_fim) e (ex_inicio < req_inicio + duracao)
                if req_inicio < ex_fim and ex_inicio < (req_inicio + timedelta(minutes=duracao)):
                    return False, f"Conflito com atendimento existente às {ex_inicio.strftime('%H:%M')}"

            return True, ""
        except Exception as e:
            return False, f"Erro ao validar horário: {str(e)}"
