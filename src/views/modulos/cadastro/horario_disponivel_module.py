import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time
from src.controllers.horario_controller import HorarioController
from src.controllers.cadastro_controller import CadastroController
from config.estilos import CORES, FONTES

class HorarioDisponivelModule:
    def __init__(self, parent, db_connection, medico_id=None):
        self.parent = parent
        self.db_connection = db_connection
        self.medico_id = medico_id
        self.horario_controller = HorarioController(db_connection)
        self.cadastro_controller = CadastroController(db_connection)
        
        # Cria o frame principal
        self.frame = tk.Frame(parent, bg=CORES['fundo'])
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.criar_interface()
        self.carregar_medicos()
        self.carregar_horarios()

    def criar_interface(self):
        # Frame principal
        main_frame = tk.Frame(self.frame, bg=CORES['fundo'], padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título da tela
        title_frame = tk.Frame(main_frame, bg='#f0f2f5')
        title_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            title_frame,
            text="Lista de Horários Médicos",
            font=FONTES['titulo'],
            bg='#f0f2f5',
            fg='#000000'
        ).pack(side='left')
        
        # Seletor de Médico
        tk.Label(main_frame, text="Médico:", bg=CORES['fundo'], font=FONTES['pequena']).pack(anchor='w')
        self.combo_medico = ttk.Combobox(main_frame, state="readonly", font=FONTES['pequena'])
        self.combo_medico.pack(fill=tk.X, pady=5)
        self.combo_medico.bind('<<ComboboxSelected>>', self.carregar_horarios)
        
        # Frame para os dias da semana
        dias_frame = tk.LabelFrame(main_frame, text="Dias da Semana", bg=CORES['fundo'], fg=CORES['texto'],
                                 font=FONTES['pequena'], padx=10, pady=10)
        dias_frame.pack(fill=tk.X, pady=10)
        
        self.dias_semana = [
            ("Segunda-feira", 0),
            ("Terça-feira", 1),
            ("Quarta-feira", 2),
            ("Quinta-feira", 3),
            ("Sexta-feira", 4),
            ("Sábado", 5),
            ("Domingo", 6)
        ]
        
        self.var_dias = []
        for i, (dia, _) in enumerate(self.dias_semana):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(dias_frame, text=dia, variable=var, bg=CORES['fundo'],
                              fg=CORES['texto'], selectcolor='white',
                              activebackground=CORES['fundo'], activeforeground=CORES['texto'],
                              font=FONTES['pequena'])
            cb.grid(row=i//4, column=i%4, sticky='w', padx=5, pady=2)
            self.var_dias.append((var, dia))
        
        # Horários
        tk.Label(main_frame, text="Horário de Atendimento:", bg=CORES['fundo'],
                font=FONTES['pequena']).pack(anchor='w', pady=(10,0))
        
        horario_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        horario_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(horario_frame, text="Das", bg=CORES['fundo'],
                font=FONTES['pequena']).pack(side=tk.LEFT) 
        
        self.hora_inicio = ttk.Combobox(horario_frame, values=self.gerar_horarios(), 
                                      width=8, font=FONTES['pequena'])
        self.hora_inicio.pack(side=tk.LEFT, padx=5)
        
        tk.Label(horario_frame, text="às", bg=CORES['fundo'],
                font=FONTES['pequena']).pack(side=tk.LEFT)
        
        self.hora_fim = ttk.Combobox(horario_frame, values=self.gerar_horarios(), 
                                   width=8, font=FONTES['pequena'])
        self.hora_fim.pack(side=tk.LEFT, padx=5)
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Botão Adicionar Horário
        btn_adicionar = tk.Button(
            btn_frame,
            text="Adicionar Horário",
            command=self.adicionar_horario,
            bg=CORES['destaque'],
            fg='white',
            font=FONTES['pequena'],
            relief='flat',
            padx=15,
            pady=5,
            activebackground='#43a047',
            activeforeground='white',
            cursor='hand2'
        )
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        # Botão Remover Horário
        btn_remover = tk.Button(
            btn_frame,
            text="Remover Horário",
            command=self.remover_horario,
            bg=CORES['alerta'],
            fg='white',
            font=FONTES['pequena'],
            relief='flat',
            padx=15,
            pady=5,
            activebackground='#e53935',
            activeforeground='white',
            cursor='hand2'
        )
        btn_remover.pack(side=tk.LEFT, padx=5)
        
        # Tabela de horários
        style = ttk.Style()
        style.configure("Treeview", 
                       background=CORES['fundo_conteudo'],
                       foreground=CORES['texto'],
                       fieldbackground=CORES['fundo_conteudo'],
                       font=FONTES['pequena'])
        
        self.tree = ttk.Treeview(main_frame, columns=('dia', 'horario'), show='headings')
        self.tree.heading('dia', text='Dia da Semana')
        self.tree.heading('horario', text='Horário')
        self.tree.column('dia', width=150)
        self.tree.column('horario', width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
    def gerar_horarios(self):
        """Gera uma lista de horários em intervalos de 30 minutos"""
        horarios = []
        for hora in range(0, 24):
            for minuto in [0, 30]:
                horarios.append(f"{hora:02d}:{minuto:02d}")
        return horarios
        
    def verificar_medicos_banco(self):
        """Método temporário para verificar médicos no banco de dados"""
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM medicos ORDER BY nome")
            medicos = cursor.fetchall()
            cursor.close()
            return medicos
        except Exception as e:
            print(f"Erro ao verificar médicos no banco: {str(e)}")
            return []

    def carregar_medicos(self):
        """Carrega a lista de médicos no combobox"""
        try:
            # Usar o controller para listar médicos
            medicos = self.cadastro_controller.listar_medicos()
            
            if not medicos:
                messagebox.showwarning("Aviso", "Nenhum médico cadastrado no sistema.")
                return
                
            # Criar lista de tuplas (nome, id) para o combobox
            valores = [(m['nome'], m['id']) for m in medicos]
            self.combo_medico['values'] = [v[0] for v in valores]
            
            # Armazenar o mapeamento de nome para ID
            self.medicos_map = {nome: id_ for nome, id_ in valores}
            
            # Selecionar o primeiro médico por padrão
            if self.medico_id:
                for nome, id_ in self.medicos_map.items():
                    if id_ == self.medico_id:
                        self.combo_medico.set(nome)
                        self.medico_id = id_
                        break
            elif valores:
                self.combo_medico.current(0)
                self.medico_id = valores[0][1]
                
            # Forçar atualização da interface
            self.frame.update_idletasks()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os médicos: {str(e)}")
            self.combo_medico['values'] = []
            self.medicos_map = {}

    def carregar_horarios(self, event=None):
        """Carrega os horários do médico selecionado"""
        try:
            if not hasattr(self, 'tree'):
                return
                
            # Limpa a árvore de horários
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            if not hasattr(self, 'medicos_map'):
                return
                
            medico_nome = self.combo_medico.get()
            if not medico_nome:
                return
                
            # Obtém o ID do médico selecionado
            self.medico_id = self.medicos_map.get(medico_nome)
            if not self.medico_id:
                return
                
            # Busca os horários do médico
            horarios = self.horario_controller.listar_horarios_medico(self.medico_id)
            
            # Mapeia os números dos dias para nomes
            dias_nome = {
                0: "Segunda-feira",
                1: "Terça-feira",
                2: "Quarta-feira",
                3: "Quinta-feira",
                4: "Sexta-feira",
                5: "Sábado",
                6: "Domingo"
            }
            
            # Adiciona os horários na árvore
            for horario in horarios:
                dia_nome = dias_nome.get(horario['dia_semana'], f"Dia {horario['dia_semana']}")
                hora_formatada = f"{self.formatar_horario(horario['hora_inicio'])} - {self.formatar_horario(horario['hora_fim'])}"
                self.tree.insert('', 'end', values=(dia_nome, hora_formatada))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar os horários: {str(e)}")
            
    def formatar_horario(self, horario_timedelta):
        """Formata um timedelta para o formato HH:MM"""
        if isinstance(horario_timedelta, str):
            return horario_timedelta
            
        total_segundos = int(horario_timedelta.total_seconds())
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        return f"{horas:02d}:{minutos:02d}"
        
    def adicionar_horario(self):
        """Adiciona um novo horário"""
        try:
            if not hasattr(self, 'medico_id') or not self.medico_id:
                messagebox.showwarning("Aviso", "Selecione um médico primeiro")
                return
                
            # Obter os dias selecionados
            dias_selecionados = [i for i, (var, _) in enumerate(self.var_dias) if var.get()]
            if not dias_selecionados:
                messagebox.showwarning("Aviso", "Selecione pelo menos um dia da semana")
                return
                
            # Validar horários
            hora_inicio = self.hora_inicio.get()
            hora_fim = self.hora_fim.get()
            
            if not hora_inicio or not hora_fim:
                messagebox.showwarning("Aviso", "Preencha os horários de início e fim")
                return
                
            try:
                # Validar formato dos horários
                h1 = time.fromisoformat(hora_inicio)
                h2 = time.fromisoformat(hora_fim)
                
                if h1 >= h2:
                    raise ValueError("Horário de início deve ser anterior ao horário de fim")
                
                # Salvar horário para cada dia selecionado
                for dia in dias_selecionados:
                    sucesso, mensagem = self.horario_controller.salvar_horario(
                        medico_id=self.medico_id,
                        dia_semana=dia,
                        hora_inicio=hora_inicio,
                        hora_fim=hora_fim
                    )
                    
                    if not sucesso:
                        raise Exception(mensagem)
                
                # Atualizar a lista de horários
                self.carregar_horarios()
                
                # Limpar seleção
                for var, _ in self.var_dias:
                    var.set(False)
                self.hora_inicio.set('')
                self.hora_fim.set('')
                
                messagebox.showinfo("Sucesso", "Horário(s) adicionado(s) com sucesso!")
                
            except ValueError as e:
                messagebox.showerror("Erro", f"Formato de horário inválido. Use o formato HH:MM (ex: 09:00)")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o horário: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def remover_horario(self):
        """Remove o horário selecionado"""
        try:
            if not hasattr(self, 'medico_id') or not self.medico_id:
                messagebox.showwarning("Aviso", "Selecione um médico primeiro")
                return
                
            # Obter o item selecionado na árvore
            item_selecionado = self.tree.selection()
            if not item_selecionado:
                messagebox.showwarning("Aviso", "Selecione um horário para remover")
                return
                
            # Obter os valores da linha selecionada
            valores = self.tree.item(item_selecionado)['values']
            if not valores or len(valores) < 2:
                messagebox.showerror("Erro", "Não foi possível obter os dados do horário selecionado")
                return
                
            # Mapear o nome do dia de volta para o número
            dia_nome = valores[0]
            dias_nome = {
                "Segunda-feira": 0,
                "Terça-feira": 1,
                "Quarta-feira": 2,
                "Quinta-feira": 3,
                "Sexta-feira": 4,
                "Sábado": 5,
                "Domingo": 6
            }
            
            dia_numero = dias_nome.get(dia_nome)
                    
            if dia_numero is None:
                messagebox.showerror("Erro", f"Dia da semana inválido: {dia_nome}")
                return
                
            # Obter o horário formatado (HH:MM - HH:MM)
            horario_str = valores[1]
            try:
                # Extrair os horários de início e fim
                hora_inicio_str, hora_fim_str = horario_str.split(' - ')
                
                # Converter strings para objetos time
                hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()
                
                # Buscar o ID do horário no banco de dados
                cursor = self.db_connection.cursor(dictionary=True)
                query = """
                    SELECT id FROM horarios_disponiveis 
                    WHERE medico_id = %s 
                    AND dia_semana = %s 
                    AND TIME(hora_inicio) = %s 
                    AND TIME(hora_fim) = %s
                """
                cursor.execute(query, (
                    self.medico_id,
                    dia_numero,
                    hora_inicio.strftime('%H:%M:%S'),
                    hora_fim.strftime('%H:%M:%S')
                ))
                
                horario = cursor.fetchone()
                cursor.close()
                
                if not horario:
                    messagebox.showerror("Erro", "Horário não encontrado no banco de dados")
                    return
                    
                # Confirmar a remoção
                if messagebox.askyesno("Confirmar", f"Deseja realmente remover o horário de {hora_inicio_str} às {hora_fim_str} de {dia_nome}?"):
                    # Chamar o controlador para remover o horário
                    sucesso, mensagem = self.horario_controller.remover_horario(horario['id'])
                    
                    if sucesso:
                        messagebox.showinfo("Sucesso", mensagem)
                        # Atualizar a lista de horários
                        self.carregar_horarios()
                    else:
                        messagebox.showerror("Erro", mensagem)
                        
            except ValueError as e:
                messagebox.showerror("Erro", f"Formato de horário inválido: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao remover o horário: {str(e)}")
            import traceback
            traceback.print_exc()