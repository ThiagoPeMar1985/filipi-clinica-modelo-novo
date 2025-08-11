import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from typing import Dict, List, Optional, Any

class ExamesConsultasModule:
    def __init__(self, parent, controller, db):
        self.parent = parent
        self.controller = controller
        self.db = db
        self.exame_atual = None
        
        # Inicializa o dicionário de médicos
        self.medicos_dict = {}
        
        # Cria o frame principal
        self.frame = ttk.Frame(parent)
        self._criar_interface()
        
    def _criar_interface(self):
        """Cria a interface do módulo de exames/consultas."""
        # Frame superior (controles)
        frame_superior = ttk.LabelFrame(self.frame, text="tempo médio do Exame/Consulta", padding=10)
        frame_superior.pack(fill=tk.X, padx=5, pady=5)
        
        # Médico
        ttk.Label(frame_superior, text="Médico:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.medico_cb = ttk.Combobox(frame_superior, state="readonly", width=50)
        self.medico_cb.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.medico_cb.bind('<<ComboboxSelected>>', self._carregar_exames)
        
        # Nome do exame/consulta
        ttk.Label(frame_superior, text="Nome:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.nome_var = tk.StringVar()
        self.entry_nome = ttk.Entry(frame_superior, textvariable=self.nome_var, width=50)
        self.entry_nome.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Tempo (em minutos)
        ttk.Label(frame_superior, text="Tempo (minutos):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tempo_var = tk.StringVar()
        self.entry_tempo = ttk.Spinbox(frame_superior, from_=1, to=480, width=10, textvariable=self.tempo_var)
        self.entry_tempo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Frame dos botões
        frame_botoes = ttk.Frame(frame_superior)
        frame_botoes.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Botão Salvar
        self.btn_salvar = tk.Button(
            frame_botoes,
            text="Salvar",
            command=self._salvar_exame,
            bg="#4a6fa5",  # Azul
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=2)
        
        # Botão Cancelar
        self.btn_cancelar = tk.Button(
            frame_botoes,
            text="Cancelar",
            command=self._cancelar_edicao,
            bg="#f44336",  # Vermelho
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            state=tk.DISABLED  # Inicia desabilitado
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=2)
        
        # Botão Editar
        self.btn_editar = tk.Button(
            frame_botoes,
            text="Editar",
            command=self._editar_exame,
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
            frame_botoes,
            text="Excluir",
            command=self._excluir_exame,
            bg="#f44336",  # Vermelho
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_excluir.pack(side=tk.LEFT, padx=2)
        
        # Frame da lista de exames
        frame_lista = ttk.LabelFrame(self.frame, text="Lista de Exames/Consultas", padding=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para listar os exames
        colunas = ('id', 'nome', 'tempo')
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')
        
        # Configuração das colunas
        self.tree.heading('id', text='ID')
        self.tree.column('id', width=50)
        
        self.tree.heading('nome', text='Nome')
        self.tree.column('nome', width=300)
        
        self.tree.heading('tempo', text='Tempo (min)')
        self.tree.column('tempo', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Empacotando
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind do clique na lista
        self.tree.bind('<<TreeviewSelect>>', self._selecionar_exame)
        
        # Carrega os médicos
        self._carregar_medicos()
        
      
    
    def _carregar_medicos(self):
        """Carrega a lista de médicos no combobox."""
        try:
            medicos = self.controller.listar_medicos()
            if not medicos:
                messagebox.showwarning("Aviso", "Nenhum médico cadastrado.")
                return
                
            # Preenche o dicionário e o combobox
            valores = []
            for medico in medicos:
                medico_id = medico.get('id')
                medico_nome = medico.get('nome')
                if medico_id and medico_nome:
                    self.medicos_dict[medico_nome] = medico_id
                    valores.append(medico_nome)
            
            self.medico_cb['values'] = valores
            self.medico_cb.set('Selecione um médico...')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar médicos: {str(e)}")
    
    def _carregar_exames(self, event=None):
        """Carrega os exames do médico selecionado."""
        try:
            # Limpa a lista atual
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            medico_nome = self.medico_cb.get()
            if not medico_nome or not self.medicos_dict:
                return
                
            medico_id = self.medicos_dict.get(medico_nome)
            if not medico_id:
                return
                
            # Busca os exames do médico
            exames = self.controller.listar_exames_consultas_por_medico(medico_id)
            
            # Preenche a lista
            for exame in exames:
                self.tree.insert('', tk.END, values=(
                    exame['id'],
                    exame['nome'],
                    exame['tempo']
                ))
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar exames: {str(e)}")


    
    def _editar_exame(self):
        """Prepara a interface para editar o exame selecionado."""
        if not self.exame_atual:
            return
            
        # Habilita a edição
        self.entry_nome.config(state="normal")
        self.entry_tempo.config(state="normal")
        
        # Atualiza o estado dos botões
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)  # Habilita o botão cancelar
        
        # Coloca o foco no campo de nome
        self.entry_nome.focus()
        
    def _novo_exame(self):
        """Prepara a interface para cadastrar um novo exame."""
        self._limpar_campos()
        self.medico_cb.config(state="readonly")
        self.entry_nome.config(state="normal")
        self.entry_tempo.config(state="normal")
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.NORMAL)  # Habilita o botão cancelar
        self.entry_nome.focus()
        self.exame_atual = None  # Garante que é um novo exame
        
    def _cancelar_edicao(self):
        """Cancela a edição e volta ao estado anterior."""
        if self.exame_atual:
            # Se está editando um exame existente, volta para o modo de visualização
            self.nome_var.set(self.exame_atual['nome'])
            self.tempo_var.set(str(self.exame_atual['tempo']))
            
            # Volta para o modo de visualização
            self.entry_nome.config(state="readonly")
            self.entry_tempo.config(state="readonly")
            
            # Atualiza o estado dos botões
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)
            self.btn_salvar.config(state=tk.DISABLED)
            self.btn_cancelar.config(state=tk.DISABLED)
        else:
            # Se estava criando um novo, limpa os campos
            self._limpar_campos()
            
    def _salvar_exame(self):
        """Salva um exame/consulta."""
        try:
            # Obtém os dados do formulário
            medico_nome = self.medico_cb.get()
            nome = self.nome_var.get().strip()
            tempo = self.tempo_var.get().strip()
            
            # Validações
            if not medico_nome or medico_nome == 'Selecione um médico...':
                messagebox.showwarning("Aviso", "Selecione um médico.")
                self.medico_cb.focus()
                return
                
            if not nome:
                messagebox.showwarning("Aviso", "Informe o nome do exame/consulta.")
                self.entry_nome.focus()
                return
                
            if not tempo or not tempo.isdigit() or int(tempo) <= 0:
                messagebox.showwarning("Aviso", "Informe um tempo válido em minutos (número maior que zero).")
                self.entry_tempo.focus()
                return
                
            # Verifica se é uma edição ou novo cadastro
            if self.exame_atual:
                # Atualiza um exame existente
                sucesso = self.controller.atualizar_exame_consulta(
                    self.exame_atual['id'],
                    {
                        'nome': nome,
                        'tempo': int(tempo)
                    }
                )
                mensagem = "atualizado"
            else:
                # Cria um novo exame
                sucesso = self.controller.criar_exame_consulta(
                    medico_id=self.medicos_dict.get(medico_nome),
                    nome=nome,
                    tempo=int(tempo)
                )
                mensagem = "criado"
            
            if sucesso:
                messagebox.showinfo("Sucesso", f"Exame/Consulta {mensagem} com sucesso!")
                # Atualiza a lista e limpa os campos
                self._carregar_exames()
                self._limpar_campos()
            else:
                messagebox.showerror("Erro", f"Não foi possível salvar o exame/consulta.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar exame/consulta: {str(e)}")
    
    def _excluir_exame(self):
        """Exclui o exame/consulta selecionado."""
        if not self.exame_atual:
            return
            
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este exame/consulta?"):
            try:
                if self.controller.excluir_exame_consulta(self.exame_atual['id']):
                    messagebox.showinfo("Sucesso", "Exame/Consulta excluído com sucesso!")
                    self._limpar_campos()
                    self._carregar_exames()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o exame/consulta.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir exame/consulta: {str(e)}")
    
    def _selecionar_exame(self, event):
        """Preenche os campos quando um exame é selecionado na lista."""
        # Verifica se há algum item selecionado
        selecionado = self.tree.selection()
        if not selecionado:
            return
        
        item = selecionado[0]
        valores = self.tree.item(item)['values']
        
        # Se clicou no mesmo item que já está selecionado, limpa a seleção
        if self.exame_atual and self.exame_atual['id'] == valores[0]:
            self._limpar_campos()
            self.tree.selection_remove(selecionado)  # Remove a seleção visual
            return
        
        # Preenche os campos com os valores do item selecionado
        self.exame_atual = {
            'id': valores[0],
            'nome': valores[1],
            'tempo': valores[2]
        }
        
        self.nome_var.set(valores[1])
        self.tempo_var.set(valores[2])
        
        # Desabilita a edição direta e ativa os botões de ação
        self.entry_nome.config(state="readonly")
        self.entry_tempo.config(state="readonly")
        self.btn_editar.config(state=tk.NORMAL)
        self.btn_excluir.config(state=tk.NORMAL)
        self.btn_salvar.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.DISABLED)
        
    def _limpar_campos(self):
        """Limpa todos os campos do formulário."""
        self.exame_atual = None
        self.nome_var.set('')
        self.tempo_var.set('')
        
        # Configura o estado dos botões
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.DISABLED)
        
        # Habilita a seleção de médico
        self.medico_cb.config(state="readonly")
        self.entry_nome.config(state="readonly")
        self.entry_tempo.config(state="readonly")
        
        # Foca no campo de seleção de médico
        self.medico_cb.focus()

    