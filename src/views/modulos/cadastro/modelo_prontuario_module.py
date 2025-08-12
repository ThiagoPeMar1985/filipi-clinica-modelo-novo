"""
Módulo para gerenciamento de modelos de prontuário.
Permite criar, editar, visualizar e excluir modelos de texto para prontuários.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime
from typing import Optional, Dict, Any, List

# Importações locais
from ..base_module import BaseModule
from src.controllers.prontuario_controller import ProntuarioController
from src.controllers.cadastro_controller import CadastroController

class ModeloProntuarioModule(BaseModule):
    """Módulo para gerenciamento de modelos de prontuário."""
    
    def __init__(self, parent, controller, db_connection=None):
        """
        Inicializa o módulo de modelos de prontuário.
        
        Args:
            parent: Widget pai onde o módulo será renderizado.
            controller: Controlador principal da aplicação.
            db_connection: Conexão com o banco de dados (opcional).
        """
        super().__init__(parent, controller)
        
        # Inicializa os controladores
        self.prontuario_controller = ProntuarioController()
        self.cadastro_controller = CadastroController(db_connection)
        
        # Configura a conexão com o banco de dados nos controladores
        if db_connection:
            self.prontuario_controller.set_db_connection(db_connection)
            self.cadastro_controller.set_db_connection(db_connection)
        
        # Variáveis de estado
        self.modelo_atual = None
        self.medico_selecionado = None  # id do médico
        self.medico_selecionado_usuario_id = None  # usuario_id do médico
        self.modo_edicao = False
        
        # Dicionário para armazenar a lista de médicos
        self.medicos = {}
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Constrói a interface
        self._construir_interface()
        
        # Carrega os médicos disponíveis após a construção da interface
        self.frame.after(100, self._carregar_medicos)
    
    def _construir_interface(self):
        """Constrói a interface do módulo de modelos de prontuário."""
        # Frame principal
        self.main_frame = ttk.Frame(self.frame, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        titulo_frame = ttk.Frame(self.main_frame)
        titulo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            titulo_frame,
            text="Modelos de Prontuário",
            font=('Arial', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        # Frame de filtros
        self._construir_filtros()
        
        # Frame principal (lista + visualização)
        conteudo_frame = ttk.Frame(self.main_frame)
        conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame da lista de modelos
        self._construir_lista_modelos(conteudo_frame)
        
        # Frame de visualização/edição
        self._construir_visualizacao(conteudo_frame)
    
    def _construir_filtros(self):
        """Constrói a seção de filtros."""
        filtros_frame = ttk.LabelFrame(self.main_frame, text="Filtros", padding=10)
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Seletor de médico
        ttk.Label(filtros_frame, text="Médico:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.medico_var = tk.StringVar()
        self.medico_cb = ttk.Combobox(
            filtros_frame,
            textvariable=self.medico_var,
            state='readonly',
            width=50
        )
        self.medico_cb.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.medico_cb.bind('<<ComboboxSelected>>', self._on_medico_selecionado)
    
    def _construir_lista_modelos(self, parent):
        """Constrói a lista de modelos."""
        lista_frame = ttk.LabelFrame(parent, text="Modelos", padding=10)
        lista_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Botões de ação
        botoes_frame = ttk.Frame(lista_frame)
        botoes_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botão Novo
        self.btn_novo = tk.Button(
            botoes_frame,
            text="Novo",
            command=self._criar_modelo,
            bg="#4CAF50",  # Verde
            fg="white",
            bd=0,
            padx=10,
            pady=5
        )
        self.btn_novo.pack(side=tk.LEFT, padx=2)
        
        # Botão Editar
        self.btn_editar = tk.Button(
            botoes_frame,
            text="Editar",
            command=self._editar_modelo,
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
            botoes_frame,
            text="Excluir",
            command=self._excluir_modelo,
            bg="#f44336",  # Vermelho
            fg="white",
            bd=0,
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_excluir.pack(side=tk.LEFT, padx=2)
        
        # Lista de modelos
        self.lista_modelos = ttk.Treeview(
            lista_frame,
            columns=('id', 'nome', 'data_criacao'),
            show='headings',
            selectmode='browse',
            height=15
        )
        self.lista_modelos.heading('id', text='ID')
        self.lista_modelos.heading('nome', text='Nome')
        self.lista_modelos.heading('data_criacao', text='Data de Criação')
        
        # Configuração das colunas
        self.lista_modelos.column('id', width=50, anchor='center')
        self.lista_modelos.column('nome', width=200)
        self.lista_modelos.column('data_criacao', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            lista_frame,
            orient=tk.VERTICAL,
            command=self.lista_modelos.yview
        )
        self.lista_modelos.configure(yscrollcommand=scrollbar.set)
        
        # Empacota a lista e a scrollbar
        self.lista_modelos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de seleção
        self.lista_modelos.bind('<<TreeviewSelect>>', self._on_modelo_selecionado)

    def _construir_visualizacao(self, parent):
        """Constrói a área de visualização/edição do modelo."""
        self.visualizacao_frame = ttk.LabelFrame(parent, text="Visualização", padding=10)
        self.visualizacao_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Frame para o nome do modelo
        self.nome_frame = ttk.Frame(self.visualizacao_frame)
        self.nome_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Rótulo "Nome:"
        ttk.Label(self.nome_frame, text="Nome:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Campo para exibir o nome do modelo
        self.nome_modelo = ttk.Entry(
            self.nome_frame,
            background='white',
            foreground='black',
            width=50,
        )
        self.nome_modelo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Texto do modelo
        ttk.Label(self.visualizacao_frame, text="Modelo:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Frame para o texto com barra de rolagem
        text_frame = ttk.Frame(self.visualizacao_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem vertical
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Widget Text
        self.texto_modelo = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            yscrollcommand=scrollbar.set
        )
        self.texto_modelo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Fonte fixa Arial 8 na visualização/edição
        try:
            self.texto_modelo.configure(font=('Arial', 8))
        except Exception:
            pass
        
        # Corretor ortográfico (opcional)
        try:
            self._enable_spellcheck(self.texto_modelo)
        except Exception:
            pass
        
        # Configurar a scrollbar
        scrollbar.config(command=self.texto_modelo.yview)
        
        # Inicia como somente leitura
        self.texto_modelo.config(state=tk.DISABLED)
        
        # Frame de botões de ação
        self.botoes_acao_frame = ttk.Frame(self.visualizacao_frame)
        self.botoes_acao_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botão Salvar
        self.btn_salvar = tk.Button(
            self.botoes_acao_frame,
            text="Salvar",
            command=self._salvar_modelo,
            bg="#4CAF50",  # Verde
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            state=tk.DISABLED
        )
        self.btn_salvar.pack(side=tk.RIGHT, padx=5)


    def _carregar_medicos(self):
        """Carrega a lista de médicos no combobox."""
        try:
            # Prioriza usuários que possuem modelos (fonte: ProntuarioController)
            usuarios_com_modelos = self.prontuario_controller.listar_medicos_com_modelos() or []
            medicos = usuarios_com_modelos
            
            # Se vier vazio, cai no cadastro de médicos apenas para exibir nomes (sem usuario_id)
            if not medicos:
                medicos = self.cadastro_controller.listar_medicos() or []
                if not medicos:
                    return
            
            # Limpa o dicionário de médicos/usuários
            self.medicos = {}
            
            # Preenche o dicionário e a lista de opções
            opcoes = []
            for m in medicos:
                nome = m.get('nome', 'Sem nome')
                crm = m.get('crm', '')  # pode não existir quando vier de usuarios
                texto = f"{nome} - {crm}" if crm else nome
                # Quando vem de listar_medicos_com_modelos (ProntuarioController), o campo é usuario_id
                uid = m.get('usuario_id') or m.get('id') if 'usuario_id' in m else None
                # Mantém medico_id se existir
                self.medicos[texto] = {
                    'medico_id': m.get('id') if 'crm' in m else None,
                    'usuario_id': uid
                }
                opcoes.append(texto)
            
            # Atualiza o combobox
            if hasattr(self, 'medico_cb') and self.medico_cb.winfo_exists():
                self.medico_cb['values'] = opcoes
                # Se houver apenas um, seleciona automaticamente
                if len(opcoes) == 1:
                    self.medico_cb.current(0)
                    self._on_medico_selecionado()
                
        except Exception as e:
            import traceback
            traceback.print_exc()  # Imprime o stack trace completo

    def _on_medico_selecionado(self, event=None):
        """Chamado quando um médico é selecionado no combobox."""
        medico_nome = self.medico_var.get()
        if not medico_nome:
            return
            
        sel = self.medicos[medico_nome]
        self.medico_selecionado = sel.get('medico_id')
        self.medico_selecionado_usuario_id = sel.get('usuario_id')
        if not self.medico_selecionado_usuario_id:
            messagebox.showinfo(
                "Aviso",
                "Este profissional não possui usuário vinculado. Vincule um usuário para visualizar os modelos."
            )
            # Limpa lista e visualização
            for item in self.lista_modelos.get_children():
                self.lista_modelos.delete(item)
            self._limpar_visualizacao()
            return
        self._carregar_modelos()

    def _carregar_modelos(self):
        """Carrega os modelos do médico selecionado."""
        # Passa a depender do usuario_id (dono dos modelos)
        if not self.medico_selecionado_usuario_id:
            messagebox.showinfo("Aviso", "Selecione um profissional com usuário vinculado para listar modelos.")
            return
        
        try:
            # Limpa a lista atual
            for item in self.lista_modelos.get_children():
                self.lista_modelos.delete(item)
            
            # Busca os modelos do usuário (médico) pelo usuario_id
            uid = self.medico_selecionado_usuario_id
            modelos = self.prontuario_controller.listar_modelos_texto(uid) or []
            
            # Preenche a lista com os modelos encontrados
            for modelo in modelos:
                data_criacao = modelo.get('data_criacao', '')
                if data_criacao:
                    if isinstance(data_criacao, str):
                        data_formatada = data_criacao
                    else:
                        data_formatada = data_criacao.strftime('%d/%m/%Y %H:%M')
                else:
                    data_formatada = 'Data não disponível'
                
                self.lista_modelos.insert('', 'end', values=(
                    modelo['id'],
                    modelo.get('nome', 'Sem nome'),
                    data_formatada
                ))
            
            # Atualiza o status (se o método existir)
            if hasattr(self.controller, 'atualizar_status'):
                self.controller.atualizar_status(f"Carregados {len(modelos)} modelo(s)")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar modelos: {str(e)}")
    
    def _criar_modelo(self):
        """Prepara a interface para criar um novo modelo de prontuário."""
        # Verifica se há usuário vinculado selecionado
        if not self.medico_selecionado_usuario_id:
            messagebox.showwarning("Aviso", "Selecione um profissional com usuário vinculado antes de criar um novo modelo.")
            return
        
            
        # Limpa a seleção atual
        self.lista_modelos.selection_remove(self.lista_modelos.selection())
        
        # Habilita a edição do texto
        self.texto_modelo.config(state=tk.NORMAL)
        self.texto_modelo.delete(1.0, tk.END)
        # Insere diretiva de fonte 8 e aplica fonte no widget
        try:
            self.texto_modelo.insert('1.0', '<<font:8>>\n')
            self.texto_modelo.configure(font=('Arial', 8))
        except Exception:
            pass
        
        # Atualiza o estado dos botões
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.NORMAL)
        
        # Define o modo de edição e armazena o nome do modelo
        self.modo_edicao = 'criar'
        self.modelo_atual = {'nome': self.nome_modelo.get(), 'conteudo': ''}
        
        # Define o foco no campo de texto
        self.texto_modelo.focus_set()

    def _editar_modelo(self):
        """Prepara a interface para editar o modelo de prontuário selecionado."""
        # Verifica se há um item selecionado na lista
        selecionado = self.lista_modelos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um modelo para editar.")
            return
        
        # Obtém o ID do modelo selecionado
        item = self.lista_modelos.item(selecionado[0])
        modelo_id = item['values'][0]  # O ID está na primeira coluna
        
        try:
            # Busca os dados do modelo no controlador
            modelo = self.prontuario_controller.buscar_modelo_por_id(modelo_id)
            
            if not modelo:
                messagebox.showerror("Erro", "Modelo não encontrado.")
                return
            
            # Atualiza o modelo atual
            self.modelo_atual = modelo
            
            # Habilita a edição do campo de nome
            self.nome_modelo.delete(0, tk.END)
            self.nome_modelo.insert(0, modelo.get('nome', ''))
            
            # Habilita a edição do texto
            self.texto_modelo.config(state=tk.NORMAL)
            # Garante diretiva de fonte 8 e aplica fonte no widget
            try:
                conteudo = self.texto_modelo.get('1.0', 'end-1c')
                linhas = conteudo.splitlines()
                nova_dir = '<<font:8>>'
                if not linhas:
                    self.texto_modelo.insert('1.0', nova_dir + "\n")
                else:
                    primeira = linhas[0].strip()
                    if primeira.lower().startswith('<<font:') and primeira.endswith('>>'):
                        linhas[0] = nova_dir
                        novo = "\n".join(linhas)
                        self.texto_modelo.delete('1.0', tk.END)
                        self.texto_modelo.insert('1.0', novo)
                    else:
                        self.texto_modelo.insert('1.0', nova_dir + "\n")
                self.texto_modelo.configure(font=('Arial', 8))
            except Exception:
                pass
            
            # Atualiza o estado dos botões
            self.btn_editar.config(state=tk.DISABLED)
            self.btn_excluir.config(state=tk.DISABLED)
            self.btn_salvar.config(state=tk.NORMAL)
            
            # Define o modo de edição
            self.modo_edicao = 'editar'
            
            # Define o foco no campo de texto
            self.texto_modelo.focus_set()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o modelo: {str(e)}")
        
    def _excluir_modelo(self):
        """Exclui o modelo de prontuário selecionado."""
        # Verifica se há um item selecionado na lista
        selecionado = self.lista_modelos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um modelo para excluir.")
            return
        
        # Obtém o ID e nome do modelo selecionado
        item = self.lista_modelos.item(selecionado[0])
        modelo_id = item['values'][0]  # O ID está na primeira coluna
        modelo_nome = item['values'][1]  # O nome está na segunda coluna
        
        # Confirmação do usuário
        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o modelo '{modelo_nome}'?\nEsta ação não pode ser desfeita."
        ):
            return
        
        try:
            # Chama o controlador para excluir o modelo
            sucesso, mensagem = self.prontuario_controller.excluir_modelo_texto(modelo_id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                # Atualiza a lista de modelos
                self._carregar_modelos()
                # Limpa a visualização
                self._limpar_visualizacao()
            else:
                messagebox.showerror("Erro", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir o modelo: {str(e)}")
    
    def _on_modelo_selecionado(self, event=None):
        """Chamado quando um modelo é selecionado na lista."""
        # Verifica se há um item selecionado
        selecionado = self.lista_modelos.selection()
        if not selecionado:
            return
        
        # Obtém o ID do modelo selecionado
        item = self.lista_modelos.item(selecionado[0])
        modelo_id = item['values'][0]  # O ID está na primeira coluna
        
        try:
            # Verifica se está em modo de edição
            if self.modo_edicao:
                if not messagebox.askyesno(
                    "Alteração de Seleção",
                    "Há alterações não salvas no modelo atual. Deseja descartá-las?"
                ):
                    # Se o usuário não quiser descartar, mantém a seleção anterior
                    if self.modelo_atual:
                        for item in self.lista_modelos.get_children():
                            if self.lista_modelos.item(item)['values'][0] == self.modelo_atual['id']:
                                self.lista_modelos.selection_set(item)
                                break
                    return
            
            # Busca os dados completos do modelo
            modelo = self.prontuario_controller.buscar_modelo_por_id(modelo_id)
            
            if not modelo:
                messagebox.showerror("Erro", "Modelo não encontrado.")
                return
            
            # Atualiza o modelo atual
            self.modelo_atual = modelo
            
            # Atualiza a visualização
            self.nome_modelo.delete(0, tk.END)
            self.nome_modelo.insert(0, modelo.get('nome', ' '))
            self.texto_modelo.config(state=tk.NORMAL)
            self.texto_modelo.delete(1.0, tk.END)
            self.texto_modelo.insert(tk.END, modelo.get('conteudo', ''))
            # Exibe sempre com fonte 8
            try:
                self.texto_modelo.configure(font=('Arial', 8))
            except Exception:
                pass
            self.texto_modelo.config(state=tk.DISABLED)  # Desabilita a edição
            
            # Atualiza o estado dos botões
            self.btn_editar.config(state=tk.NORMAL)
            self.btn_excluir.config(state=tk.NORMAL)
            self.btn_salvar.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o modelo: {str(e)}")

    def _salvar_modelo(self):
        """Salva o modelo de prontuário, seja criando um novo ou atualizando um existente."""
        # Verifica se há um usuário (profissional) vinculado selecionado
        if not self.medico_selecionado_usuario_id:
            messagebox.showwarning("Aviso", "Selecione um profissional com usuário vinculado antes de salvar o modelo.")
            return
        
        # Obtém e garante diretiva de fonte 8 no conteúdo
        conteudo = self.texto_modelo.get("1.0", tk.END).strip()
        try:
            linhas = conteudo.splitlines()
            nova_dir = '<<font:8>>'
            if not linhas:
                conteudo = nova_dir
            else:
                primeira = linhas[0].strip() if linhas else ''
                if primeira.lower().startswith('<<font:') and primeira.endswith('>>'):
                    linhas[0] = nova_dir
                    conteudo = "\n".join(linhas)
                else:
                    conteudo = nova_dir + "\n" + "\n".join(linhas)
        except Exception:
            pass
        
        # Verifica se o conteúdo não está vazio
        if not conteudo:
            messagebox.showwarning("Aviso", "O conteúdo do modelo não pode estar vazio.")
            return
        
        try:
            if self.modo_edicao == 'criar':
                # Cria um novo modelo
                dados = {
                    'nome': self.nome_modelo.get(),
                    'conteudo': conteudo,
                    # modelos_texto agora usa usuario_id
                    'usuario_id': self.medico_selecionado_usuario_id,
                    'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                sucesso, resultado = self.prontuario_controller.criar_modelo_texto(dados)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", "Modelo criado com sucesso!")
                    # Atualiza a lista de modelos
                    self._carregar_modelos()
                    # Limpa a visualização
                    self._limpar_visualizacao()
                else:
                    messagebox.showerror("Erro", f"Falha ao criar o modelo: {resultado}")
                    
            elif self.modo_edicao == 'editar' and self.modelo_atual:
                # Atualiza um modelo existente
                dados = {
                    'nome': self.nome_modelo.get(),
                    'conteudo': conteudo,
                    'data_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                sucesso, mensagem = self.prontuario_controller.atualizar_modelo_texto(
                    self.modelo_atual['id'],
                    dados
                )
                
                if sucesso:
                    messagebox.showinfo("Sucesso", mensagem)
                    # Atualiza a lista de modelos
                    self._carregar_modelos()
                    # Limpa a visualização
                    self._limpar_visualizacao()
                else:
                    messagebox.showerror("Erro", mensagem)
            
            # Sai do modo de edição
            self.modo_edicao = False
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o modelo: {str(e)}")
    
    def _cancelar_edicao(self):
        """Cancela a edição em andamento e retorna ao modo de visualização."""
        # Verifica se há alterações não salvas
        if self.modo_edicao and self._verificar_alteracoes_nao_salvas():
            if not messagebox.askyesno(
                "Cancelar Edição",
                "Há alterações não salvas. Deseja realmente descartá-las?"
            ):
                return  # Usuário optou por não cancelar
        
        # Limpa a visualização
        self._limpar_visualizacao()
        
        # Sai do modo de edição
        self.modo_edicao = False
        
        # Atualiza o estado dos botões
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_excluir.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.DISABLED)
            
        # Limpa a seleção na lista
        self.lista_modelos.selection_remove(self.lista_modelos.selection())

    def _verificar_alteracoes_nao_salvas(self):
        """Verifica se há alterações não salvas no modelo atual."""
        if not self.modo_edicao:
            return False
        
        # Se estiver criando um novo modelo, verifica se há conteúdo
        if self.modo_edicao == 'criar':
            conteudo = self.texto_modelo.get("1.0", "end-1c").strip()
            return bool(conteudo)
        
        # Se estiver editando um modelo existente, compara com o conteúdo original
        if self.modo_edicao == 'editar' and self.modelo_atual:
            conteudo_atual = self.texto_modelo.get("1.0", "end-1c").strip()
            conteudo_original = self.modelo_atual.get('conteudo', '').strip()
            return conteudo_atual != conteudo_original
        
        return False

    def _limpar_visualizacao(self):
        """Limpa a área de visualização do modelo."""
        self.nome_modelo.delete(0, tk.END)
        self.texto_modelo.config(state=tk.NORMAL)
        self.texto_modelo.delete(1.0, tk.END)
        self.texto_modelo.config(state=tk.DISABLED)
        self.modelo_atual = None