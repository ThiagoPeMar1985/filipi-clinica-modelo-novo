"""
Módulo de Prontuários - Gerencia a visualização e edição de prontuários de pacientes
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import re

from ..base_module import BaseModule
from src.controllers.cliente_controller import ClienteController
from src.controllers.prontuario_controller import ProntuarioController
from src.controllers.auth_controller import AuthController

class ProntuarioModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        """
        Inicializa o módulo de prontuários.
        
        Args:
            parent: Widget pai onde este módulo será renderizado
            controller: Controlador principal da aplicação
            db_connection: Conexão com o banco de dados
        """
        super().__init__(parent, controller)
        
        # Armazena a conexão com o banco de dados
        self.db_connection = db_connection
        
        # Inicializa os controladores
        self.cliente_controller = ClienteController()
        self.prontuario_controller = ProntuarioController()
        self.auth_controller = AuthController()
        
        # Obtém o usuário logado
        self.usuario_atual = self.auth_controller.obter_usuario_autenticado()
        self.medico_id = self.usuario_atual.get('id') if self.usuario_atual else None
        
        # Variáveis de estado
        self.paciente_selecionado = None
        self.prontuario_atual = None
        self.modo_edicao = False
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Constrói a interface
        self._construir_interface()
    
    def _construir_interface(self):
        """Constrói a interface do módulo de prontuários."""
        # Frame principal dividido em duas partes
        self.painel_esquerdo = tk.Frame(self.frame, bg='#f0f2f5', width=300)
        self.painel_esquerdo.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.painel_esquerdo.pack_propagate(False)
        
        self.painel_direito = tk.Frame(self.frame, bg='#f0f2f5')
        self.painel_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Constrói o painel de busca de pacientes
        self._construir_painel_busca()
        
        # Constrói o painel de prontuários (inicialmente vazio)
        self._construir_painel_prontuarios()
    
    def _construir_painel_busca(self):
        """Constrói o painel de busca de pacientes."""
        # Frame para o título
        titulo_frame = tk.Frame(self.painel_esquerdo, bg='#f0f2f5')
        titulo_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            titulo_frame,
            text="Buscar Paciente",
            font=('Arial', 14, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(side=tk.LEFT)
        
        # Frame para a busca
        busca_frame = tk.Frame(self.painel_esquerdo, bg='#f0f2f5')
        busca_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Campo de busca
        self.busca_var = tk.StringVar()
        self.busca_entry = ttk.Entry(
            busca_frame,
            textvariable=self.busca_var,
            width=25
        )
        self.busca_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.busca_entry.bind("<Return>", lambda e: self._buscar_paciente())
        
        # Botão de busca
        tk.Button(
            busca_frame,
            text="Buscar",
            command=self._buscar_paciente,
            bg='#4a6fa5',      # Cor de fundo do botão
            fg='#ffffff',      # Cor do texto
            activebackground='#3b5a7f',  # Cor quando o botão é pressionado
            activeforeground='#ffffff',  # Cor do texto quando pressionado
            relief=tk.FLAT,  # Estilo do relevo do botão
            borderwidth=2,     # Largura da borda
            font=('Arial', 10, 'bold'),  # Fonte em negrito
            cursor='hand2'     # Cursor de mão ao passar por cima
        ).pack(side=tk.LEFT, padx=(0, 5))  # Adiciona um pequeno espaço à direita

        # Frame para a lista de resultados
        resultados_frame = tk.Frame(self.painel_esquerdo, bg='#f0f2f5')
        resultados_frame.pack(fill=tk.BOTH, expand=True)
                
        # Lista de resultados com scrollbar
        self.resultados_tree = ttk.Treeview(
            resultados_frame,
            columns=("id", "nome", "telefone"),
            show="headings",
            height=15
        )
        
        # Configuração das colunas
        self.resultados_tree.heading("id", text="ID")
        self.resultados_tree.heading("nome", text="Nome")
        self.resultados_tree.heading("telefone", text="Telefone")
        
        self.resultados_tree.column("id", width=50)
        self.resultados_tree.column("nome", width=150)
        self.resultados_tree.column("telefone", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            resultados_frame,
            orient="vertical",
            command=self.resultados_tree.yview
        )
        self.resultados_tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionamento
        self.resultados_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de seleção
        self.resultados_tree.bind("<<TreeviewSelect>>", self._selecionar_paciente)
    
    def _construir_painel_prontuarios(self):
        """Constrói o painel de prontuários."""
        # Limpa o painel direito se já existir algum conteúdo
        for widget in self.painel_direito.winfo_children():
            widget.destroy()
            
        # Frame principal do painel de prontuários
        conteudo_frame = tk.Frame(self.painel_direito, bg='#f0f2f5')
        conteudo_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Se não houver paciente selecionado, exibe mensagem
        if not self.paciente_selecionado:
            tk.Label(
                conteudo_frame,
                text="Selecione um paciente para visualizar ou criar prontuários",
                font=('Arial', 12),
                bg='#f0f2f5',
                fg='#666666',
                pady=50
            ).pack(expand=True)
            return
            
        # Frame para os botões de ação
        botoes_frame = tk.Frame(conteudo_frame, bg='#f0f2f5')
        botoes_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botão para criar novo prontuário
        if self.medico_id:  # Apenas se for um médico logado
            tk.Button(
                botoes_frame,
                text="Novo Prontuário",
                command=self._criar_novo_prontuario,
                bg='#28a745',
                fg='white',
                font=('Arial', 10, 'bold'),
                relief=tk.FLAT,
                cursor='hand2',
                padx=10,
                pady=5
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            # Botão para gerenciar modelos de texto
            tk.Button(
                botoes_frame,
                text="Modelos de Texto",
                command=self._gerenciar_modelos,
                bg='#6c757d',
                fg='white',
                font=('Arial', 10, 'bold'),
                relief=tk.FLAT,
                cursor='hand2',
                padx=10,
                pady=5
            ).pack(side=tk.LEFT)
        
        # Frame para a lista de prontuários à esquerda e conteúdo à direita
        prontuario_container = tk.Frame(conteudo_frame, bg='#f0f2f5')
        prontuario_container.pack(fill=tk.BOTH, expand=True)
        
        # Frame para a lista de prontuários
        lista_frame = tk.Frame(prontuario_container, bg='#f0f2f5', width=300)
        lista_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        lista_frame.pack_propagate(False)
        
        # Frame para o conteúdo do prontuário
        self.prontuario_content_frame = tk.Frame(prontuario_container, bg='#ffffff', relief=tk.SUNKEN, bd=1)
        self.prontuario_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Título da lista de prontuários
        tk.Label(
            lista_frame,
            text=f"Prontuários de {self.paciente_selecionado['nome']}",
            font=('Arial', 11, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Lista de prontuários com scrollbar
        self.prontuarios_tree = ttk.Treeview(
            lista_frame,
            columns=("id", "data"),
            show="headings",
            height=15,
            selectmode='browse'
        )
        
        # Configuração das colunas
        self.prontuarios_tree.heading("id", text="ID")
        self.prontuarios_tree.heading("data", text="Data")
        
        self.prontuarios_tree.column("id", width=50, anchor='center')
        self.prontuarios_tree.column("data", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            lista_frame,
            orient="vertical",
            command=self.prontuarios_tree.yview
        )
        self.prontuarios_tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionamento
        self.prontuarios_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de seleção
        self.prontuarios_tree.bind("<<TreeviewSelect>>", self._selecionar_prontuario)
        
        # Carrega os prontuários do paciente
        self._carregar_prontuarios()
    
    def _buscar_paciente(self):
        """Busca pacientes com base no texto inserido."""
        termo_busca = self.busca_var.get().strip()
        
        if not termo_busca:
            messagebox.showinfo("Aviso", "Digite um termo para busca")
            return
        
        # Limpa a lista de resultados
        for item in self.resultados_tree.get_children():
            self.resultados_tree.delete(item)
        
        # Verifica se o termo é numérico (possível ID ou telefone)
        if termo_busca.isdigit():
            # Busca por ID
            sucesso, paciente = self.cliente_controller.buscar_cliente_por_id(int(termo_busca))
            if sucesso and paciente:
                self.resultados_tree.insert("", "end", values=(
                    paciente["id"],
                    paciente["nome"],
                    paciente.get("telefone", "")
                ))
            
            # Busca por telefone
            pacientes = self.cliente_controller.buscar_cliente_por_telefone(termo_busca)
            for paciente in pacientes:
                # Evita duplicatas se já encontrou por ID
                if not sucesso or paciente["id"] != int(termo_busca):
                    self.resultados_tree.insert("", "end", values=(
                        paciente["id"],
                        paciente["nome"],
                        paciente.get("telefone", "")
                    ))
        else:
            # Busca por nome
            pacientes = self.cliente_controller.buscar_cliente_por_nome(termo_busca)
            for paciente in pacientes:
                self.resultados_tree.insert("", "end", values=(
                    paciente["id"],
                    paciente["nome"],
                    paciente.get("telefone", "")
                ))
        
        # Verifica se encontrou resultados
        if not self.resultados_tree.get_children():
            messagebox.showinfo("Resultado", "Nenhum paciente encontrado")
    
    def _selecionar_paciente(self, event):
        """Seleciona um paciente da lista de resultados."""
        selecao = self.resultados_tree.selection()
        if not selecao:
            return
        
        # Obtém o ID do paciente selecionado
        item = self.resultados_tree.item(selecao[0])
        paciente_id = item["values"][0]
        
        # Busca os dados completos do paciente
        sucesso, paciente = self.cliente_controller.buscar_cliente_por_id(paciente_id)
        if sucesso and paciente:
            self.paciente_selecionado = paciente
            # Reconstrói o painel de prontuários com o novo paciente
            self._construir_painel_prontuarios()
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do paciente")
    
    def _carregar_prontuarios(self):
        """Carrega os prontuários do paciente selecionado."""
        if not self.paciente_selecionado:
            return
        
        # Limpa a lista de prontuários
        for item in self.prontuarios_tree.get_children():
            self.prontuarios_tree.delete(item)
        
        # Busca os prontuários do paciente
        prontuarios = self.prontuario_controller.buscar_prontuarios_paciente(self.paciente_selecionado["id"])
        
        for prontuario in prontuarios:
            # Formata a data para exibição
            data_criacao = prontuario.get("data_criacao")
            if data_criacao:
                if isinstance(data_criacao, str):
                    try:
                        data_obj = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                        data_formatada = data_obj.strftime('%d/%m/%Y')
                    except ValueError:
                        data_formatada = data_criacao
                else:
                    data_formatada = data_criacao.strftime('%d/%m/%Y')
            else:
                data_formatada = "N/A"
            
            self.prontuarios_tree.insert("", "end", values=(
                prontuario["id"],
                data_formatada,
            ))
    
    def _selecionar_prontuario(self, event=None):
        """Seleciona um prontuário da lista."""
        # Se não houver seleção (quando event é None), tenta obter a seleção atual
        if event is None:
            selecao = self.prontuarios_tree.selection()
        else:
            selecao = self.prontuarios_tree.selection()
        
        if not selecao:
            return
        
        # Obtém o ID do prontuário selecionado
        item = self.prontuarios_tree.item(selecao[0])
        prontuario_id = item['values'][0]
        
        # Se for a mensagem de "Nenhum prontuário encontrado", não faz nada
        if not prontuario_id:
            return
        
        # Busca os dados do prontuário
        prontuario = self.prontuario_controller.buscar_prontuario_por_id(prontuario_id)
        
        if prontuario:
            self.prontuario_atual = prontuario
            self._exibir_prontuario()
        else:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do prontuário")
    
    def _exibir_prontuario(self):
        """Exibe o conteúdo do prontuário selecionado."""
        # Limpa o frame de conteúdo
        for widget in self.prontuario_content_frame.winfo_children():
            widget.destroy()
        
        if not self.prontuario_atual:
            return
        
        # Habilita a edição do texto para inserir o conteúdo
        self.texto_prontuario = scrolledtext.ScrolledText(
            self.prontuario_content_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            height=20
        )
        self.texto_prontuario.pack(fill=tk.BOTH, expand=True)
        
        # Limpa o conteúdo atual
        self.texto_prontuario.delete(1.0, tk.END)
        
        # Formata o cabeçalho do prontuário
        data_criacao = self.prontuario_atual.get("data_criacao", "Data não disponível")
        if isinstance(data_criacao, str):
            try:
                data_obj = datetime.strptime(data_criacao, '%Y-%m-%d %H:%M:%S')
                data_formatada = data_obj.strftime('%d/%m/%Y às %H:%M')
            except ValueError:
                data_formatada = data_criacao
        else:
            data_formatada = data_criacao.strftime('%d/%m/%Y às %H:%M')
        
        medico_nome = self.prontuario_atual.get("nome_medico", "Médico não identificado")
        
        # Insere o cabeçalho formatado
        self.texto_prontuario.insert(tk.END, f"Data: {data_formatada}\n", "info")
        self.texto_prontuario.insert(tk.END, f"Médico: {medico_nome}\n", "info")
        self.texto_prontuario.insert(tk.END, f"Paciente: {self.paciente_selecionado['nome']}\n\n", "info")
        
        # Insere o conteúdo do prontuário
        conteudo = self.prontuario_atual.get("conteudo", "")
        self.texto_prontuario.insert(tk.END, conteudo, "conteudo")
        
        # Configura as tags de formatação
        self.texto_prontuario.tag_configure("titulo", font=("Arial", 12, "bold"))
        self.texto_prontuario.tag_configure("info", font=("Arial", 10, "italic"))
        self.texto_prontuario.tag_configure("conteudo", font=("Arial", 11))
        
        # Desabilita a edição do texto (modo somente leitura)
        self.texto_prontuario.config(state=tk.DISABLED)
        
        # Rola para o início do texto
        self.texto_prontuario.see("1.0")
    
    def _salvar_novo_prontuario(self):
        """Salva um novo prontuário."""
        if not self.paciente_selecionado or not self.medico_id:
            return
        
        # Obtém o conteúdo
        conteudo = self.texto_prontuario.get(1.0, tk.END).strip()
        
        if not conteudo:
            messagebox.showinfo("Aviso", "O conteúdo do prontuário não pode estar vazio")
            return
        
        # Cria o novo prontuário
        dados = {
            "paciente_id": self.paciente_selecionado["id"],
            "medico_id": self.medico_id,
            "conteudo": conteudo,
            "data_criacao": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        sucesso, resultado = self.prontuario_controller.criar_prontuario(dados)
        
        if sucesso:
            messagebox.showinfo("Sucesso", "Prontuário criado com sucesso")
            
            # Recarrega o painel de prontuários
            self._carregar_prontuarios()
        else:
            messagebox.showerror("Erro", f"Não foi possível criar o prontuário: {resultado}")
    
    def _selecionar_modelo(self):
        """Abre uma janela para selecionar um modelo de texto para inserir no prontuário."""
        # Verifica se está em modo de edição
        if not self.modo_edicao:
            messagebox.showinfo("Aviso", "É necessário estar em modo de edição para inserir modelos")
            return
        
        # Verifica se o usuário é um médico
        if not self.medico_id:
            messagebox.showinfo("Aviso", "É necessário estar logado como médico para usar modelos")
            return
        
        # Busca os modelos do médico
        modelos = self.prontuario_controller.listar_modelos_texto(self.medico_id)
        
        if not modelos:
            resposta = messagebox.askyesno(
                "Nenhum Modelo",
                "Você ainda não possui modelos de texto. Deseja criar um novo modelo agora?"
            )
            
            if resposta:
                self._gerenciar_modelos()
            
            return
        
        # Cria um diálogo modal
        dialogo = tk.Toplevel(self.frame)
        dialogo.title("Selecionar Modelo de Texto")
        dialogo.geometry("600x500")
        dialogo.transient(self.frame)
        dialogo.grab_set()
        dialogo.focus_set()
        dialogo.configure(bg='#f0f2f5')
        
        # Frame principal
        frame_principal = tk.Frame(dialogo, bg='#f0f2f5', padx=15, pady=15)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            frame_principal,
            text="Selecione um Modelo para Inserir",
            font=('Arial', 14, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Frame para a lista de modelos
        frame_lista = tk.Frame(frame_principal, bg='#f0f2f5')
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Lista de modelos com scrollbar
        frame_listbox = tk.Frame(frame_lista, bg='#f0f2f5')
        frame_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Listbox com os modelos
        listbox = tk.Listbox(
            frame_listbox,
            font=('Arial', 11),
            selectbackground='#4a6fa5',
            selectforeground='white',
            activestyle='none',
            height=15
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            frame_listbox,
            orient="vertical",
            command=listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Preenche a listbox com os modelos
        modelo_ids = []
        for modelo in modelos:
            listbox.insert(tk.END, modelo["nome"])
            modelo_ids.append(modelo["id"])
        
        # Frame para visualização do modelo
        frame_preview = tk.Frame(frame_principal, bg='#f0f2f5')
        frame_preview.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Título do preview
        tk.Label(
            frame_preview,
            text="Prévia do Modelo:",
            font=('Arial', 11, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(anchor="w")
        
        # Área de texto para o preview
        preview_text = scrolledtext.ScrolledText(
            frame_preview,
            wrap=tk.WORD,
            font=('Arial', 11),
            height=8,
            state=tk.DISABLED
        )
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame para os botões
        frame_botoes = tk.Frame(frame_principal, bg='#f0f2f5')
        frame_botoes.pack(fill=tk.X, pady=(0, 5))
        
        # Função para exibir o preview do modelo
        def exibir_preview(event=None):
            selecao = listbox.curselection()
            if not selecao:
                return
            
            modelo_id = modelo_ids[selecao[0]]
            modelo = self.prontuario_controller.buscar_modelo_texto_por_id(modelo_id)
            
            if not modelo:
                return
            
            # Exibe o conteúdo do modelo
            preview_text.config(state=tk.NORMAL)
            preview_text.delete(1.0, tk.END)
            
            # Substitui as variáveis do modelo
            conteudo = modelo["conteudo"]
            
            # Substitui as variáveis pelos valores reais
            if self.paciente_selecionado:
                conteudo = conteudo.replace("{paciente}", self.paciente_selecionado["nome"])
            
            from datetime import datetime
            data_atual = datetime.now().strftime("%d/%m/%Y")
            hora_atual = datetime.now().strftime("%H:%M")
            
            conteudo = conteudo.replace("{data}", data_atual)
            conteudo = conteudo.replace("{hora}", hora_atual)
            
            if self.usuario_atual:
                conteudo = conteudo.replace("{medico}", self.usuario_atual.get("nome", ""))
            
            preview_text.insert(tk.END, conteudo)
            preview_text.config(state=tk.DISABLED)
        
        # Função para inserir o modelo selecionado
        def inserir_modelo():
            selecao = listbox.curselection()
            if not selecao:
                messagebox.showinfo("Aviso", "Selecione um modelo para inserir")
                return
            
            modelo_id = modelo_ids[selecao[0]]
            modelo = self.prontuario_controller.buscar_modelo_texto_por_id(modelo_id)
            
            if not modelo:
                return
            
            # Obtém o conteúdo do modelo
            conteudo = modelo["conteudo"]
            
            # Substitui as variáveis pelos valores reais
            if self.paciente_selecionado:
                conteudo = conteudo.replace("{paciente}", self.paciente_selecionado["nome"])
            
            from datetime import datetime
            data_atual = datetime.now().strftime("%d/%m/%Y")
            hora_atual = datetime.now().strftime("%H:%M")
            
            conteudo = conteudo.replace("{data}", data_atual)
            conteudo = conteudo.replace("{hora}", hora_atual)
            
            if self.usuario_atual:
                conteudo = conteudo.replace("{medico}", self.usuario_atual.get("nome", ""))
            
            # Insere o conteúdo no prontuário
            self.texto_prontuario.insert(tk.INSERT, conteudo)
            
            # Fecha o diálogo
            dialogo.destroy()
        
        # Vincula a seleção da listbox ao preview
        listbox.bind("<<ListboxSelect>>", exibir_preview)
        listbox.bind("<Double-1>", lambda e: inserir_modelo())
        
        # Botões de ação
        ttk.Button(
            frame_botoes,
            text="Inserir",
            command=inserir_modelo,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="Cancelar",
            command=dialogo.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="Gerenciar Modelos",
            command=lambda: [dialogo.destroy(), self._gerenciar_modelos()]
        ).pack(side=tk.LEFT)
        
        # Centraliza o diálogo
        dialogo.update_idletasks()
        width = dialogo.winfo_width()
        height = dialogo.winfo_height()
        x = (dialogo.winfo_screenwidth() // 2) - (width // 2)
        y = (dialogo.winfo_screenheight() // 2) - (height // 2)
        dialogo.geometry(f"{width}x{height}+{x}+{y}")
        
        # Seleciona o primeiro item da lista, se houver
        if listbox.size() > 0:
            listbox.selection_set(0)
            exibir_preview()
    
    def _gerenciar_modelos(self):
        """Abre uma janela para gerenciar modelos de texto."""
        # Verifica se o usuário é um médico
        if not self.medico_id:
            messagebox.showwarning("Acesso Restrito", "Apenas médicos podem gerenciar modelos de texto.")
            return
        
        # Cria uma janela de diálogo
        dialogo = tk.Toplevel(self.frame)
        dialogo.title("Gerenciar Modelos de Texto")
        dialogo.geometry("800x600")
        dialogo.transient(self.frame)
        dialogo.grab_set()
        dialogo.configure(bg='#f0f2f5')
        
        # Frame principal
        frame_principal = tk.Frame(dialogo, bg='#f0f2f5', padx=15, pady=15)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(
            frame_principal,
            text="Gerenciar Modelos de Texto",
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Descrição
        tk.Label(
            frame_principal,
            text="Aqui você pode criar, editar e excluir seus modelos de texto personalizados.",
            font=('Arial', 11),
            bg='#f0f2f5',
            fg='#555555',
            wraplength=750
        ).pack(fill=tk.X, pady=(0, 15))
        
        # Frame para a lista e o conteúdo
        frame_conteudo = tk.Frame(frame_principal, bg='#f0f2f5')
        frame_conteudo.pack(fill=tk.BOTH, expand=True)
        
        # Frame para a lista de modelos
        frame_lista = tk.Frame(frame_conteudo, bg='#f0f2f5', width=250)
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Título da lista
        tk.Label(
            frame_lista,
            text="Seus Modelos",
            font=('Arial', 12, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Lista de modelos com scrollbar
        frame_listbox = tk.Frame(frame_lista, bg='#f0f2f5')
        frame_listbox.pack(fill=tk.BOTH, expand=True)
        
        listbox = tk.Listbox(
            frame_listbox,
            font=('Arial', 11),
            selectbackground='#4a6fa5',
            selectforeground='white',
            activestyle='none',
            height=15
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(
            frame_listbox,
            orient="vertical",
            command=listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox.configure(yscrollcommand=scrollbar.set)
        
        # Botões para a lista
        frame_botoes_lista = tk.Frame(frame_lista, bg='#f0f2f5')
        frame_botoes_lista.pack(fill=tk.X, pady=(10, 0))
        
        # Botão para criar novo modelo
        ttk.Button(
            frame_botoes_lista,
            text="Novo Modelo",
            command=lambda: self._novo_modelo_texto(frame_conteudo_direito, listbox, modelo_ids),
            style='Accent.TButton'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        # Botão para excluir modelo
        ttk.Button(
            frame_botoes_lista,
            text="Excluir",
            command=lambda: self._excluir_modelo(listbox, modelo_ids, frame_conteudo_direito),
            style='Danger.TButton'
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Frame para o conteúdo do modelo
        frame_conteudo_direito = tk.Frame(frame_conteudo, bg='#f0f2f5')
        frame_conteudo_direito.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Mensagem inicial
        tk.Label(
            frame_conteudo_direito,
            text="Selecione um modelo para visualizar ou editar",
            font=('Arial', 12),
            bg='#f0f2f5',
            fg='#555555'
        ).pack(pady=50)
        
        # Armazena os IDs dos modelos
        modelo_ids = []
        
        # Função para carregar os modelos
        def carregar_modelos():
            # Limpa a lista
            listbox.delete(0, tk.END)
            modelo_ids.clear()
            
            # Carrega os modelos do médico
            modelos = self.prontuario_controller.buscar_modelos_texto(self.medico_id)
            
            if not modelos:
                listbox.insert(tk.END, "Nenhum modelo encontrado")
                return
            
            # Adiciona os modelos à lista
            for modelo in modelos:
                listbox.insert(tk.END, modelo['nome'])
                modelo_ids.append(modelo['id'])
        
        # Função para exibir o modelo selecionado
        def exibir_modelo_selecionado(event):
            # Limpa o frame de conteúdo
            for widget in frame_conteudo_direito.winfo_children():
                widget.destroy()
            
            # Obtém o índice selecionado
            try:
                indice = listbox.curselection()[0]
            except IndexError:
                return
            
            # Verifica se há modelos
            if not modelo_ids:
                return
            
            # Obtém o ID do modelo
            modelo_id = modelo_ids[indice]
            
            # Busca o modelo
            modelo = self.prontuario_controller.buscar_modelo_texto_por_id(modelo_id)
            
            if not modelo:
                return
            
            # Frame para o nome do modelo
            frame_nome = tk.Frame(frame_conteudo_direito, bg='#f0f2f5')
            frame_nome.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(
                frame_nome,
                text="Nome:",
                font=('Arial', 11),
                bg='#f0f2f5'
            ).pack(side=tk.LEFT)
            
            nome_var = tk.StringVar(value=modelo['nome'])
            nome_entry = ttk.Entry(
                frame_nome,
                textvariable=nome_var,
                font=('Arial', 11),
                width=40
            )
            nome_entry.pack(side=tk.LEFT, padx=(5, 0))
            
            # Frame para o conteúdo do modelo
            frame_texto = tk.Frame(frame_conteudo_direito, bg='#f0f2f5')
            frame_texto.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            tk.Label(
                frame_texto,
                text="Conteúdo:",
                font=('Arial', 11),
                bg='#f0f2f5'
            ).pack(anchor="w")
            
            # Área de texto para o conteúdo
            texto_modelo = scrolledtext.ScrolledText(
                frame_texto,
                wrap=tk.WORD,
                font=('Arial', 11),
                height=15
            )
            texto_modelo.pack(fill=tk.BOTH, expand=True)
            texto_modelo.insert(tk.END, modelo['conteudo'])
            
            # Frame para os botões
            frame_botoes = tk.Frame(frame_conteudo_direito, bg='#f0f2f5')
            frame_botoes.pack(fill=tk.X)
            
            # Botão para salvar alterações
            ttk.Button(
                frame_botoes,
                text="Salvar Alterações",
                command=lambda: salvar_alteracoes(modelo_id, nome_var.get(), texto_modelo.get("1.0", tk.END)),
                style='Accent.TButton'
            ).pack(side=tk.RIGHT)
        
        # Função para salvar alterações no modelo
        def salvar_alteracoes(modelo_id, nome, conteudo):
            # Valida os campos
            if not nome or not conteudo.strip():
                messagebox.showwarning("Campos Obrigatórios", "Preencha todos os campos.")
                return
            
            # Atualiza o modelo
            sucesso = self.prontuario_controller.atualizar_modelo_texto(
                modelo_id,
                nome,
                conteudo.strip()
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso", "Modelo atualizado com sucesso!")
                carregar_modelos()
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar o modelo.")
        
        # Vincula a seleção de um modelo
        listbox.bind("<<ListboxSelect>>", exibir_modelo_selecionado)
        
        # Carrega os modelos iniciais
        carregar_modelos()
        
        # Centraliza o diálogo
        dialogo.update_idletasks()
        width = dialogo.winfo_width()
        height = dialogo.winfo_height()
        x = (dialogo.winfo_screenwidth() // 2) - (width // 2)
        y = (dialogo.winfo_screenheight() // 2) - (height // 2)
        dialogo.geometry(f"{width}x{height}+{x}+{y}")
    
    def _novo_modelo_texto(self, frame_conteudo, listbox, modelo_ids):
        """Cria um novo modelo de texto."""
        # Limpa o frame de conteúdo
        for widget in frame_conteudo.winfo_children():
            widget.destroy()
        
        # Título
        tk.Label(
            frame_conteudo,
            text="Novo Modelo",
            font=('Arial', 12, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(fill=tk.X, pady=(0, 10))
        
        # Frame para o nome do modelo
        frame_nome = tk.Frame(frame_conteudo, bg='#f0f2f5')
        frame_nome.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            frame_nome,
            text="Nome:",
            font=('Arial', 11),
            bg='#f0f2f5'
        ).pack(side=tk.LEFT)
        
        nome_var = tk.StringVar()
        nome_entry = ttk.Entry(
            frame_nome,
            textvariable=nome_var,
            font=('Arial', 11),
            width=40
        )
        nome_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para o conteúdo
        frame_texto = tk.Frame(frame_conteudo, bg='#f0f2f5')
        frame_texto.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(
            frame_texto,
            text="Conteúdo:",
            font=('Arial', 11),
            bg='#f0f2f5'
        ).pack(anchor="w")
        
        # Área de texto para o conteúdo
        texto = scrolledtext.ScrolledText(
            frame_texto,
            wrap=tk.WORD,
            font=('Arial', 11),
            height=15
        )
        texto.pack(fill=tk.BOTH, expand=True)
        
        # Frame para os botões
        frame_botoes = tk.Frame(frame_conteudo, bg='#f0f2f5')
        frame_botoes.pack(fill=tk.X, pady=(0, 5))
        
        # Função para salvar o novo modelo
        def salvar_modelo():
            nome = nome_var.get().strip()
            conteudo = texto.get(1.0, tk.END).strip()
            
            if not nome or not conteudo:
                messagebox.showwarning("Campos Obrigatórios", "Preencha todos os campos.")
                return
            
            # Cria o novo modelo
            dados = {
                "nome": nome,
                "conteudo": conteudo,
                "medico_id": self.medico_id
            }
            
            sucesso, resultado = self.prontuario_controller.criar_modelo_texto(dados)
            
            if sucesso:
                messagebox.showinfo("Sucesso", "Modelo criado com sucesso!")
                
                # Recarrega a lista de modelos
                listbox.delete(0, tk.END)
                modelo_ids.clear()
                
                modelos = self.prontuario_controller.listar_modelos_texto(self.medico_id)
                for modelo in modelos:
                    listbox.insert(tk.END, modelo['nome'])
                    modelo_ids.append(modelo['id'])
                
                # Limpa o formulário
                nome_var.set("")
                texto.delete(1.0, tk.END)
            else:
                messagebox.showerror("Erro", f"Não foi possível criar o modelo: {resultado}")
        
        # Botões de ação
        ttk.Button(
            frame_botoes,
            text="Salvar",
            command=salvar_modelo,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            frame_botoes,
            text="Cancelar",
            command=lambda: frame_conteudo.winfo_children()[0].destroy()
        ).pack(side=tk.RIGHT, padx=5)
        
        # Define o foco no campo de nome
        nome_entry.focus_set()

    def exibir(self):
        """Exibe o módulo de prontuários."""
        # Configura o título da página
        titulo_frame = tk.Frame(self.frame, bg='#f0f0f0', padx=10, pady=5)
        titulo_frame.pack(fill=tk.X)
        
        # Título
        tk.Label(
            titulo_frame,
            text="Prontuários",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT)
        
        # Botões de ação
        botoes_frame = tk.Frame(titulo_frame, bg='#f0f0f0')
        botoes_frame.pack(side=tk.RIGHT)
        
        # Botão para gerenciar modelos de texto
        if self.medico_id:
            ttk.Button(
                botoes_frame,
                text="Gerenciar Modelos de Texto",
                command=self._gerenciar_modelos
            ).pack(side=tk.RIGHT, padx=5)
        
        # Exibe o frame principal
        self.frame.pack(fill=tk.BOTH, expand=True)
