"""
Módulo de Prontuários - Gerencia a visualização e edição de prontuários de pacientes
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
import win32print
from datetime import datetime
import re
try:
    # Corretor ortográfico (pt)
    from spellchecker import SpellChecker
except Exception:
    SpellChecker = None

from ..base_module import BaseModule
from src.controllers.cliente_controller import ClienteController
from src.controllers.prontuario_controller import ProntuarioController
from src.controllers.auth_controller import AuthController
from src.controllers.config_controller import ConfigController
from src.utils.impressao import GerenciadorImpressao

# Filtra prints de debug específicos deste módulo, sem afetar outros prints úteis
try:
    import builtins as _bi
    def _print_filter(*args, **kwargs):
        try:
            msg = " ".join(str(a) for a in args)
            if str(msg).startswith("[DEBUG][Prontuario]"):
                return  # suprime logs de debug solicitados
        except Exception:
            pass
        return _bi.print(*args, **kwargs)
    print = _print_filter  # type: ignore
except Exception:
    pass

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
        
        # Inicializa os controladores (prioriza os do controller principal para reutilizar a mesma conexão de BD)
        self.cliente_controller = getattr(self.controller, 'cliente_controller', None) or ClienteController()
        self.prontuario_controller = getattr(self.controller, 'prontuario_controller', None) or ProntuarioController()
        self.auth_controller = getattr(self.controller, 'auth_controller', None) or AuthController()
        self.cadastro_controller = getattr(self.controller, 'cadastro_controller', None)
        # Configurações e impressão
        self.config_controller = getattr(self.controller, 'config_controller', None) or ConfigController()
        self.impressao = GerenciadorImpressao(config_controller=self.config_controller)
        # Removido controle de fonte persistente: impressão usa padrão do sistema
        # Garante que todos os controllers usem a mesma conexão real (com .cursor)
        self._alinhar_conexoes_db()
        
        # Obtém o usuário logado (prioriza o controller principal se disponível)
        try:
            self.usuario_atual = getattr(self.controller, 'usuario', None)
        except Exception:
            self.usuario_atual = None
        if not self.usuario_atual:
            self.usuario_atual = self.auth_controller.obter_usuario_autenticado()
        # Normaliza usuário em dict e resolve médico logado
        self.usuario_dict = self._usuario_to_dict(self.usuario_atual)
        self.medico_id = None
        self._resolver_medico_logado()
        # DEBUG: identificar usuário e medico_id resolvido
        try:
            print("[DEBUG][Prontuario] usuario_dict=", self.usuario_dict, "medico_id_resolvido=", self.medico_id)
            if self.medico_id is None:
                print("[DEBUG][Prontuario] medico_id vazio (None) - usará fallback por usuario_id/nome/telefone")
        except Exception:
            pass
        
        # Variáveis de estado
        self.paciente_selecionado = None
        self.prontuario_atual = None
        self.modo_edicao = False
        # Estado do corretor ortográfico
        self._spell = None
        self._spell_after_id = None
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Constrói a interface
        self._construir_interface()
    
    def _usuario_to_dict(self, usuario):
        """Garante um dicionário a partir do usuário autenticado (objeto ou dict)."""
        try:
            if usuario is None:
                return None
            if isinstance(usuario, dict):
                return usuario
            if hasattr(usuario, 'to_dict') and callable(getattr(usuario, 'to_dict')):
                return usuario.to_dict()
            data = {}
            for attr in ('id', 'nome', 'login', 'nivel', 'telefone'):
                if hasattr(usuario, attr):
                    data[attr] = getattr(usuario, attr)
            return data or None
        except Exception:
            return None

    def _resolver_medico_logado(self):
        """
        Define self.medico_id a partir do usuário autenticado usando o ID do usuário
        quando o nível for 'medico' ou 'funcionario'. Isso garante que os modelos de
        prontuário sejam buscados por usuário (medico_id).
        """
        # A partir de agora, salvamos e consultamos por usuario_id diretamente.
        # Não é necessário resolver/consultar medico_id.
        self.medico_id = None
        usr = getattr(self, 'usuario_dict', None) or {}
        if not isinstance(usr, dict):
            return
        user_id = usr.get('id')
        try:
            print("[DEBUG][Prontuario] usuario logado id=", user_id)
        except Exception:
            pass

    def _candidatos_identificador_medico(self):
        """Retorna possíveis identificadores do médico para compatibilidade de filtros."""
        usr = getattr(self, 'usuario_dict', None) or {}
        candidatos = []
        # id numérico do usuário (nova chave para modelos_texto)
        uid = usr.get('id')
        if uid:
            candidatos.append(uid)
        # id de médico (para outras tabelas/legados)
        if self.medico_id:
            candidatos.append(self.medico_id)
        # possíveis chaves comuns em bases existentes
        for k in ('crm', 'imp', 'codigo_medico', 'matricula', 'login', 'nome'):
            v = usr.get(k)
            if v:
                candidatos.append(v)
        # elimina duplicados preservando ordem
        seen = set()
        uniq = []
        for c in candidatos:
            if c not in seen:
                uniq.append(c)
                seen.add(c)
        # DEBUG: listar candidatos
        try:
            print("[DEBUG][Prontuario] candidatos_identificador_medico=", uniq)
        except Exception:
            pass
        return uniq

    def _obter_conexao_valida(self):
        """Retorna uma conexão que possua .cursor, priorizando a do controller principal e do cadastro_controller."""
        # 1) controller.db
        try:
            ctrl_db = getattr(self.controller, 'db', None)
            if ctrl_db and hasattr(ctrl_db, 'cursor'):
                return ctrl_db
        except Exception:
            pass
        # 2) cadastro_controller.db
        try:
            cad = getattr(self, 'cadastro_controller', None)
            cad_db = getattr(cad, 'db', None)
            if cad_db and hasattr(cad_db, 'cursor'):
                return cad_db
        except Exception:
            pass
        # 3) self.db_connection se já for conexão real
        try:
            if self.db_connection and hasattr(self.db_connection, 'cursor'):
                return self.db_connection
        except Exception:
            pass
        return None

    def _alinhar_conexoes_db(self):
        """Configura a mesma conexão válida em todos os controllers que precisarem."""
        conn = self._obter_conexao_valida()
        try:
            print("[DEBUG][Prontuario] alinhando conexões: conexao_valida_existe=", bool(conn))
        except Exception:
            pass
        if not conn:
            return
        # Atribui nos controllers com set_db_connection ou atributo .db
        for ctrl in (self.cliente_controller, self.prontuario_controller, self.auth_controller, self.cadastro_controller):
            if not ctrl:
                continue
            try:
                if hasattr(ctrl, 'set_db_connection') and callable(getattr(ctrl, 'set_db_connection')):
                    ctrl.set_db_connection(conn)
                elif hasattr(ctrl, 'db'):
                    setattr(ctrl, 'db', conn)
            except Exception:
                continue

    def _listar_modelos_compat(self):
        """Tenta listar modelos por múltiplos identificadores do médico para compatibilidade."""
        erros = []
        # tentar pelas APIs conhecidas, variando o identificador
        for ident in self._candidatos_identificador_medico():
            try:
                print(f"[DEBUG][Prontuario] tentando listar modelos com ident={ident}")
            except Exception:
                pass
            # tentar listar_modelos_texto somente quando ident for usuario_id numérico
            try:
                ident_uid = None
                if isinstance(ident, int):
                    ident_uid = ident
                else:
                    # strings numéricas
                    try:
                        ident_uid = int(str(ident)) if str(ident).isdigit() else None
                    except Exception:
                        ident_uid = None
                modelos = []
                if ident_uid is not None:
                    modelos = self.prontuario_controller.listar_modelos_texto(ident_uid)
                if modelos:
                    try:
                        print(f"[DEBUG][Prontuario] listar_modelos_texto encontrou {len(modelos)} modelos para usuario_id={ident_uid}")
                    except Exception:
                        pass
                    return modelos
            except Exception as e:
                erros.append(str(e))
                try:
                    print(f"[DEBUG][Prontuario] erro listar_modelos_texto usuario_id={ident_uid}: {e}")
                except Exception:
                    pass
            # tentar buscar_modelos_texto
            try:
                modelos = getattr(self.prontuario_controller, 'buscar_modelos_texto', lambda *_: [])(ident)
                if modelos:
                    try:
                        print(f"[DEBUG][Prontuario] buscar_modelos_texto encontrou {len(modelos)} modelos para ident={ident}")
                    except Exception:
                        pass
                    return modelos
            except Exception as e:
                erros.append(str(e))
                try:
                    print(f"[DEBUG][Prontuario] erro buscar_modelos_texto ident={ident}: {e}")
                except Exception:
                    pass
        # se nada encontrado, retorna lista vazia; erros podem ser mostrados em chamadas
        return []

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
        self.busca_entry.bind("<Return>", self._buscar_paciente)
        # Busca dinâmica ao digitar (debounce)
        self._busca_after_id = None
        self.busca_entry.bind("<KeyRelease>", self._on_change_busca)
        
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
            columns=("id", "nome"),
            show="headings",
            height=15
        )
        
        # Configuração das colunas
        self.resultados_tree.heading("id", text="ID")
        self.resultados_tree.heading("nome", text="Nome")
        
        self.resultados_tree.column("id", width=50)
        self.resultados_tree.column("nome", width=220)
        
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
            
        # Nenhum botão de ação no topo deste painel
        
        # Frame para a área esquerda (carrossel) e conteúdo à direita (editor)
        prontuario_container = tk.Frame(conteudo_frame, bg='#f0f2f5')
        prontuario_container.pack(fill=tk.BOTH, expand=True)
        
        # Frame para o carrossel de prontuários (esquerda)
        carrossel_frame = tk.Frame(prontuario_container, bg='#f0f2f5', width=380)
        carrossel_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        carrossel_frame.pack_propagate(False)
        
        # Frame para o conteúdo do prontuário (editor à direita)
        self.prontuario_content_frame = tk.Frame(prontuario_container, bg='#ffffff', relief=tk.SUNKEN, bd=1)
        self.prontuario_content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Renderiza editor do novo prontuário
        self._render_editor_novo_prontuario(self.prontuario_content_frame)
        
        # Renderiza o carrossel do histórico do paciente
        self._render_carrossel_prontuarios(carrossel_frame)
        # Carrega os prontuários do paciente no carrossel
        self._carregar_prontuarios()
    
    def _buscar_paciente(self, event=None):
        """Busca pacientes com base no texto inserido. Pode ser chamada por botão ou tecla Enter."""
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
                    paciente["nome"]
                ))
            
            # Busca por telefone
            pacientes = self.cliente_controller.buscar_cliente_por_telefone(termo_busca)
            for paciente in pacientes:
                # Evita duplicatas se já encontrou por ID
                if not sucesso or paciente["id"] != int(termo_busca):
                    self.resultados_tree.insert("", "end", values=(
                        paciente["id"],
                        paciente["nome"]
                    ))
        else:
            # Busca por nome
            pacientes = self.cliente_controller.buscar_cliente_por_nome(termo_busca)
            for paciente in pacientes:
                self.resultados_tree.insert("", "end", values=(
                    paciente["id"],
                    paciente["nome"]
                ))
        
        # Verifica se encontrou resultados
        if not self.resultados_tree.get_children():
            messagebox.showinfo("Resultado", "Nenhum paciente encontrado")
        
        # Se foi chamado via evento de teclado, evita propagação
        return "break"
    
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
        """Carrega os prontuários do paciente selecionado no carrossel."""
        if not self.paciente_selecionado:
            return
        prontuarios = self.prontuario_controller.buscar_prontuarios_paciente(self.paciente_selecionado["id"])
        # Armazena e reinicia o índice do carrossel
        self.prontuarios_lista = prontuarios or []
        self.carousel_index = 0 if self.prontuarios_lista else -1
        self._atualizar_carrossel()

    def _render_carrossel_prontuarios(self, parent):
        """Monta a UI do carrossel do histórico do paciente."""
        # Título
        tk.Label(
            parent,
            text=f"Histórico de {self.paciente_selecionado['nome']}",
            font=('Arial', 11, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Navegação
        nav = tk.Frame(parent, bg='#f0f2f5')
        nav.pack(fill=tk.X, pady=(0, 5))
        self.btn_prev = tk.Button(nav, text='◀', width=3, command=self._carrossel_prev)
        self.btn_prev.pack(side=tk.LEFT)
        self.carousel_pos_label = tk.Label(nav, text='0/0', bg='#f0f2f5')
        self.carousel_pos_label.pack(side=tk.LEFT, padx=8)
        self.btn_next = tk.Button(nav, text='▶', width=3, command=self._carrossel_next)
        self.btn_next.pack(side=tk.LEFT)
        
        # Preview
        preview_frame = tk.Frame(parent, bg='#f0f2f5')
        preview_frame.pack(fill=tk.BOTH, expand=True)
        self.carousel_preview = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            state=tk.DISABLED,
            height=18
        )
        self.carousel_preview.pack(fill=tk.BOTH, expand=True)

    def _atualizar_carrossel(self):
        """Atualiza o preview e estado dos botões do carrossel."""
        total = len(getattr(self, 'prontuarios_lista', []) or [])
        idx = getattr(self, 'carousel_index', -1)
        # Atualiza label de posição
        self.carousel_pos_label.config(text=f"{(idx+1) if total and idx>=0 else 0}/{total}")
        # Habilita/desabilita botões
        state_prev = tk.NORMAL if idx > 0 else tk.DISABLED
        state_next = tk.NORMAL if (total and idx < total - 1) else tk.DISABLED
        self.btn_prev.config(state=state_prev)
        self.btn_next.config(state=state_next)
        
        # Atualiza conteúdo
        self.carousel_preview.config(state=tk.NORMAL)
        self.carousel_preview.delete(1.0, tk.END)
        if total and 0 <= idx < total:
            item = self.prontuarios_lista[idx]
            # Cabeçalho com data (coluna 'data' da tabela prontuarios) e médico
            data_val = item.get('data', '')
            if isinstance(data_val, str):
                # 'data' vem como YYYY-MM-DD
                data_fmt = ''
                try:
                    d = datetime.strptime(data_val, '%Y-%m-%d')
                    data_fmt = d.strftime('%d/%m/%Y')
                except Exception:
                    data_fmt = data_val
            else:
                data_fmt = data_val.strftime('%d/%m/%Y') if data_val else ''
            medico = item.get('nome_medico', 'Médico não identificado')
            titulo = item.get('titulo') or ''
            if titulo:
                self.carousel_preview.insert(tk.END, f"{titulo}\n\n", 'title')
            self.carousel_preview.insert(tk.END, f"Data: {data_fmt}\n", 'info')
            self.carousel_preview.insert(tk.END, f"Médico: {medico}\n\n", 'info')
            self.carousel_preview.insert(tk.END, item.get('conteudo', ''))
        else:
            self.carousel_preview.insert(tk.END, 'Nenhum prontuário encontrado.')
        self.carousel_preview.config(state=tk.DISABLED)

    def _carrossel_prev(self):
        if getattr(self, 'carousel_index', -1) > 0:
            self.carousel_index -= 1
            self._atualizar_carrossel()

    def _carrossel_next(self):
        total = len(getattr(self, 'prontuarios_lista', []) or [])
        if total and getattr(self, 'carousel_index', -1) < total - 1:
            self.carousel_index += 1
            self._atualizar_carrossel()
    
    def _selecionar_prontuario(self, event=None):
        """Seleciona um prontuário da lista e abre pré-visualização sem afetar o editor."""
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
            self._mostrar_prontuario_modal(prontuario)
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
        self.texto_prontuario.tag_configure("conteudo", font=("Arial", 10))
        
        # Desabilita a edição do texto (modo somente leitura)
        self.texto_prontuario.config(state=tk.DISABLED)
        
        # Rola para o início do texto
        self.texto_prontuario.see("1.0")

    def _render_editor_novo_prontuario(self, parent):
        """Renderiza o editor do novo prontuário à direita."""
        # Cabeçalho do editor
        header = tk.Frame(parent, bg='#ffffff')
        header.pack(fill=tk.X)
        tk.Label(header, text="Novo Prontuário", bg='#ffffff', fg='#333333', font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=8, pady=8)

        # Botões de ação do editor
        botoes = tk.Frame(parent, bg='#ffffff')
        botoes.pack(fill=tk.X)
        tk.Button(botoes, text="Salvar", bg="#28a745", fg="white", relief=tk.FLAT, cursor='hand2',
                  command=self._salvar_novo_prontuario).pack(side=tk.LEFT, padx=(8, 4), pady=(0, 8))
        tk.Button(botoes, text="Inserir Modelo", bg="#4a6fa5", fg="white", relief=tk.FLAT, cursor='hand2',
                  command=self._selecionar_modelo).pack(side=tk.LEFT, padx=4, pady=(0, 8))
        tk.Button(botoes, text="Limpar", bg="#6c757d", fg="white", relief=tk.FLAT, cursor='hand2',
                  command=lambda: self.editor_texto.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=4, pady=(0, 8))
        # Botão Imprimir (abre pré-visualização)
        tk.Button(botoes, text="Imprimir", bg="#17a2b8", fg="white", relief=tk.FLAT, cursor='hand2',
                  command=self._abrir_pre_visualizacao).pack(side=tk.RIGHT, padx=(4, 8), pady=(0, 8))

        # Área de texto do editor
        self.editor_texto = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=('Arial', 11))
        self.editor_texto.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        # Mantém fonte padrão do editor; sem controle de tamanho persistente
        try:
            current_font = tkfont.Font(font=self.editor_texto['font'])
            self._editor_font_family = current_font.actual().get('family', 'Arial')
        except Exception:
            self._editor_font_family = 'Arial'

        # Compatibilidade com rotinas existentes de inserção de modelo
        # Usa os mesmos atributos esperados: self.modo_edicao e self.texto_prontuario
        self.modo_edicao = True
        self.texto_prontuario = self.editor_texto

        # Prefill: Paciente e Data de hoje no novo prontuário
        self._preencher_cabecalho_novo_prontuario()

        # Ativa corretor ortográfico (se disponível)
        self._habilitar_corretor_ortografico()

    def _imprimir_prontuario(self):
        """Gera um laudo simples com o conteúdo atual e envia para a impressora escolhida."""
        try:
            # Coleta conteúdo
            txt = getattr(self, 'editor_texto', None)
            if not txt:
                messagebox.showwarning("Atenção", "Editor não disponível para impressão.")
                return
            corpo = txt.get('1.0', 'end-1c').strip()
            if not corpo:
                messagebox.showwarning("Atenção", "O conteúdo do prontuário está vazio.")
                return
            # Identificação de paciente e médico
            paciente = {
                'nome': (self.paciente_selecionado or {}).get('nome', 'Paciente')
            }
            medico = {}
            try:
                # Tenta recuperar nome e CRM a partir do cadastro_controller/prontuario_atual se existirem
                medico['nome'] = (self.usuario_dict or {}).get('nome') or 'Médico(a) Responsável'
            except Exception:
                medico['nome'] = 'Médico(a) Responsável'
            # Empresa (opcional)
            empresa = {}
            # Monta laudo: imprime exatamente o corpo, sem diretivas automáticas
            corpo_emitir = corpo
            laudo = {
                'titulo': 'Prontuário',
                'corpo': corpo_emitir,
                'data': datetime.now().strftime('%d/%m/%Y')
            }
            # Escolhe SALA de impressão (1..5) conforme Configurações
            escolhido = self._dialogo_escolher_sala()
            if not escolhido:
                return
            # Chamada correta: (empresa, paciente, medico, laudo, impressora)
            self.impressao.imprimir_laudo_medico(empresa, paciente, medico, laudo, impressora=escolhido)
            messagebox.showinfo("Impressão", "Documento enviado para impressão.")
            
        except Exception as e:
            messagebox.showerror("Erro ao imprimir", str(e))
            print("[DEBUG][Prontuario] Erro ao imprimir:", e)

    def _abrir_pre_visualizacao(self):
        """Abre janela de pré-visualização A4 com edição rápida e ajuste de fonte."""
        try:
            conteudo_atual = (self.editor_texto.get('1.0', 'end-1c') if hasattr(self, 'editor_texto') else '').strip()
        except Exception:
            conteudo_atual = ''

        win = tk.Toplevel(self.frame)
        win.title("Pré-visualização de Impressão")
        win.geometry("1200x800")
        win.transient(self.frame)
        win.grab_set()
        win.configure(bg='#f0f2f5')
        # Não maximizar: mantém janela em tamanho padrão

        # Barra superior: somente alternância Editor/Prévia
        topbar = tk.Frame(win, bg='#e9ecef')
        topbar.pack(fill=tk.X, padx=8, pady=(8, 0))

        # Alternância Editor/Prévia (uma visão por vez), com edição dentro da página A4
        show_editor = {'val': False}  # inicia na PRÉ-VISUALIZAÇÃO
        def toggle_editor():
            show_editor['val'] = not show_editor['val']
            if show_editor['val']:
                # Modo Editar: editor embutido na página A4 do canvas
                toggle_btn.configure(text='Pré-visualizar')
            else:
                # Modo Prévia: oculta overlay
                toggle_btn.configure(text='Editar')
            atualizar_preview()
        toggle_btn = tk.Button(topbar, text="Pré-visualizar", bg="#6c757d", fg="white", relief=tk.FLAT, cursor='hand2', command=toggle_editor)
        toggle_btn.pack(side=tk.RIGHT, padx=4)

        main = tk.Frame(win, bg='#f0f2f5')
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = tk.Frame(main, bg='#f0f2f5', width=1, height=1)
        # mantém o editor como widget existente, mas sem exibir o frame
        right = tk.Frame(main, bg='#f0f2f5')
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Barra de fonte global
        bar = tk.Frame(left, bg='#f0f2f5')
        bar.pack(fill=tk.X, pady=(0, 6))
        tk.Label(bar, text="Fonte:", bg='#f0f2f5', fg='#333', font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        def aplicar_fonte_global(n: int):
            # Atualiza/insere diretiva <<font:N>> e reflete no Text
            txt = editor
            prev = txt.get('1.0', 'end-1c')
            linhas = prev.splitlines()
            nova = f"<<font:{n}>>"
            if not linhas:
                txt.insert('1.0', nova + "\n")
            else:
                prim = (linhas[0].strip() if linhas else '')
                if prim.lower().startswith('<<font:') and prim.endswith('>>'):
                    linhas[0] = nova
                    novo = "\n".join(linhas)
                    txt.delete('1.0', tk.END)
                    txt.insert('1.0', novo)
                else:
                    txt.insert('1.0', nova + "\n")
            try:
                editor.configure(font=('Arial', int(n)))
            except Exception:
                pass
            atualizar_preview()
        for n in range(6, 13):
            tk.Button(bar, text=str(n), bg="#495057", fg="white", relief=tk.FLAT,
                      cursor='hand2', command=lambda v=n: aplicar_fonte_global(v)).pack(side=tk.LEFT, padx=2)

        # Editor local da prévia
        editor_frame = tk.Frame(left, bg='#fff', bd=1, relief=tk.SOLID)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        editor_scroll = tk.Scrollbar(editor_frame)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        editor = tk.Text(left, wrap=tk.WORD, font=('Times New Roman', 10), undo=True, relief=tk.FLAT, bg='white', fg='#111')
        # não faz pack; será inserido no canvas como janela
        editor_scroll.config(command=editor.yview)
        if conteudo_atual:
            editor.insert('1.0', conteudo_atual)

        # Canvas A4 para prévia
        canvas = tk.Canvas(right, bg='#cccccc')
        canvas.pack(fill=tk.BOTH, expand=True)

        # Parâmetros A4 fixos para preview de tela (DPI=96)
        DPI = 96
        A4_W_IN, A4_H_IN = 8.27, 11.69
        page_w = int(A4_W_IN * DPI)
        page_h = int(A4_H_IN * DPI)
        margem_mm = 10
        def mm_to_px(mm):
            return int((mm / 25.4) * DPI)
        m_esq = mm_to_px(margem_mm)
        m_dir = mm_to_px(margem_mm)
        m_top = mm_to_px(margem_mm)
        m_bot = mm_to_px(margem_mm)

        page_id = None
        editor_win_id = {'val': None}
        text_items = []

        def parse_base_font(texto: str, default_pt=10):
            for ln in texto.splitlines():
                s = ln.strip()
                if s.lower().startswith('<<font:') and s.endswith('>>'):
                    try:
                        v = int(s[7:-2])
                        if 6 <= v <= 12:
                            return v
                    except Exception:
                        continue
            return default_pt

        def atualizar_preview():
            nonlocal page_id, text_items
            canvas.delete('all')
            # Centraliza página no canvas
            cw = canvas.winfo_width() or (page_w + 40)
            ch = canvas.winfo_height() or (page_h + 40)
            x0 = max(20, (cw - page_w)//2)
            y0 = max(20, (ch - page_h)//2)
            page_id = canvas.create_rectangle(x0, y0, x0+page_w, y0+page_h, fill='white', outline='#888')

            texto = editor.get('1.0', 'end-1c')
            base_pt = parse_base_font(texto)
            try:
                editor.configure(font=('Arial', base_pt))
            except Exception:
                pass
            # Remove a linha de diretiva da pré-visualização (como na impressão)
            lines = texto.replace('\r\n', '\n').replace('\r', '\n').split('\n')
            for i, ln in enumerate(lines):
                s = ln.strip()
                if s.lower().startswith('<<font:') and s.endswith('>>'):
                    del lines[i]
                    break
            texto = "\n".join(lines)

            # Desenha com margens utilizando o MESMO comportamento da impressão:
            # wrap por palavras medindo com tkfont.Font.measure e altura = linespace
            import tkinter.font as tkfont
            largura_util = page_w - m_esq - m_dir
            x_left = x0 + m_esq
            x_right = x0 + page_w - m_dir
            y_cursor = y0 + m_top
            tkf = tkfont.Font(family='Times New Roman', size=base_pt)
            line_h = int(tkf.metrics('linespace') or (base_pt + 6))

            # Se estiver em modo Editar, embute o Text exatamente na área útil da página
            # para o usuário editar dentro do retângulo A4 real
            try:
                if show_editor['val']:
                    if editor_win_id['val'] is None:
                        editor_win_id['val'] = canvas.create_window(x_left, y0 + m_top, anchor='nw', window=editor,
                                                                    width=largura_util, height=(page_h - m_top - m_bot))
                    else:
                        canvas.coords(editor_win_id['val'], x_left, y0 + m_top)
                        canvas.itemconfigure(editor_win_id['val'], width=largura_util, height=(page_h - m_top - m_bot))
                    # Ajusta a fonte do editor para a base detectada
                    try:
                        editor.configure(font=('Times New Roman', base_pt))
                    except Exception:
                        pass
                    aplicar_alinhamento_no_editor()
                else:
                    if editor_win_id['val'] is not None:
                        try:
                            canvas.delete(editor_win_id['val'])
                        except Exception:
                            pass
                        editor_win_id['val'] = None
            except Exception:
                pass

            # Heurística: alinhar ao CENTRO a linha com 'CRM' e a linha anterior (nome)
            # e ADICIONAR 5 LINHAS de espaçamento APENAS antes da linha do nome (primeira do bloco)
            linhas_full = texto.split('\n')
            indices_center = set()
            indices_first_of_block = set()
            for i, ln in enumerate(linhas_full):
                if 'crm' in ln.lower():
                    indices_center.add(i)
                    if i > 0:
                        indices_center.add(i-1)
                        indices_first_of_block.add(i-1)

            def wrap_and_draw(line_raw: str, idx: int):
                nonlocal y_cursor
                line = line_raw
                align = 'center' if idx in indices_center else 'left'
                s = line.strip()
                low = s.lower()
                if low.startswith('<<center>>'):
                    line = line.lower().replace('<<center>>', '', 1).lstrip()
                    align = 'center'
                elif low.startswith('<<right>>'):
                    line = line.lower().replace('<<right>>', '', 1).lstrip()
                    align = 'right'

                if line == '':
                    # linha em branco
                    canvas.create_text(x_left, y_cursor, text='', font=('Times New Roman', base_pt), anchor='nw', fill='#000')
                    y_cursor += line_h
                    return

                words = line.split()
                atual = ''
                desenhados = []
                for w in words:
                    tentativa = (atual + (' ' if atual else '') + w)
                    wpx = tkf.measure(tentativa)
                    if wpx <= largura_util:
                        atual = tentativa
                    else:
                        desenhados.append(atual)
                        atual = w
                if atual or line.endswith(' '):
                    desenhados.append(atual)

                # Se este é o PRIMEIRO índice do bloco Nome/CRM, adiciona 5 linhas antes
                add_spacing = (idx in indices_first_of_block)
                for j, part in enumerate(desenhados):
                    if add_spacing and j == 0:
                        y_cursor += 5 * line_h
                    if align == 'center':
                        px = tkf.measure(part)
                        cx = x_left + max(0, (largura_util - px)//2)
                        canvas.create_text(cx, y_cursor, text=part, font=('Times New Roman', base_pt), anchor='nw', fill='#000')
                    elif align == 'right':
                        px = tkf.measure(part)
                        rx = x_left + max(0, largura_util - px)
                        canvas.create_text(rx, y_cursor, text=part, font=('Times New Roman', base_pt), anchor='nw', fill='#000')
                    else:
                        canvas.create_text(x_left, y_cursor, text=part, font=('Times New Roman', base_pt), anchor='nw', fill='#000')
                    y_cursor += line_h

            text_items = []
            if not show_editor['val']:
                for i, raw in enumerate(linhas_full):
                    wrap_and_draw(raw, i)

            # Sem controles de zoom: tamanho fixo

        canvas.bind('<Configure>', lambda e: atualizar_preview())

        # Rodapé com botões
        footer = tk.Frame(win, bg='#f0f2f5')
        footer.pack(fill=tk.X, pady=(6, 0))
        def imprimir_da_previa():
            # Sobrescreve conteúdo do editor principal com o editado na prévia e chama impressão real
            try:
                if hasattr(self, 'editor_texto'):
                    self.editor_texto.delete('1.0', tk.END)
                    self.editor_texto.insert('1.0', editor.get('1.0', 'end-1c'))
            except Exception:
                pass
            win.destroy()
            self._imprimir_prontuario()
        tk.Button(footer, text="Imprimir", bg="#17a2b8", fg="white", relief=tk.FLAT, cursor='hand2',
                  command=imprimir_da_previa).pack(side=tk.RIGHT, padx=6)
        tk.Button(footer, text="Fechar", bg="#6c757d", fg="white", relief=tk.FLAT, cursor='hand2',
                  command=win.destroy).pack(side=tk.RIGHT, padx=6)

        atualizar_preview()

    def _dialogo_escolher_sala(self):
        """Dialoga a escolha de Sala de Impressão (1..5) e retorna o nome da impressora configurada ou None.
        - Janela centralizada e com tamanho adequado.
        - Sem ttk.Button (usa tk.Button no padrão do app).
        """
        # Carrega mapeamento de salas -> impressoras
        cfg = {}
        try:
            if self.config_controller and hasattr(self.config_controller, 'carregar_config_impressoras'):
                cfg = self.config_controller.carregar_config_impressoras() or {}
        except Exception:
            cfg = {}

        itens = []
        for i in range(1, 6):
            nome_imp = cfg.get(f'impressora {i}') or ''
            label = f"Sala {i} — {nome_imp if nome_imp else 'Não configurada'}"
            itens.append((label, nome_imp))

        sel = {'valor': None}
        dlg = tk.Toplevel(self.parent)
        dlg.title("Selecionar Sala de Impressão")
        dlg.configure(bg='#ffffff')
        dlg.transient(self.parent)
        dlg.grab_set()
        # Dimensão amigável
        W, H = 560, 420
        try:
            sw = dlg.winfo_screenwidth(); sh = dlg.winfo_screenheight()
            x = (sw - W) // 2; y = (sh - H) // 2
            dlg.geometry(f"{W}x{H}+{x}+{y}")
        except Exception:
            dlg.geometry(f"{W}x{H}")
        dlg.minsize(520, 360)

        tk.Label(dlg, text="Escolha a sala:", bg='#ffffff', fg='#333333', font=('Arial', 11, 'bold')).pack(padx=12, pady=(12, 8))

        # Área da lista com scrollbar
        cont = tk.Frame(dlg, bg='#ffffff')
        cont.pack(fill=tk.BOTH, expand=True, padx=12)
        sb = tk.Scrollbar(cont, orient=tk.VERTICAL)
        lb = tk.Listbox(cont, height=10, yscrollcommand=sb.set)
        sb.config(command=lb.yview)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        for label, _ in itens:
            lb.insert(tk.END, label)
        if itens:
            lb.selection_set(0)
            lb.see(0)

        # Botões padrão do app (tk.Button)
        btns = tk.Frame(dlg, bg='#ffffff')
        btns.pack(fill=tk.X, padx=12, pady=12)
        def _ok():
            try:
                idx = lb.curselection()
                if not idx:
                    return
                _, nome_imp = itens[idx[0]]
                if not nome_imp:
                    messagebox.showwarning("Sala sem impressora", "Esta sala não possui impressora configurada em Configurações.")
                    return
                sel['valor'] = nome_imp
                dlg.destroy()
            except Exception:
                dlg.destroy()
        def _cancel():
            dlg.destroy()
        tk.Button(btns, text="Imprimir", bg="#17a2b8", fg="white", relief=tk.FLAT, cursor='hand2', command=_ok).pack(side=tk.RIGHT, padx=6)
        tk.Button(btns, text="Cancelar", bg="#6c757d", fg="white", relief=tk.FLAT, cursor='hand2', command=_cancel).pack(side=tk.RIGHT)

        dlg.wait_window()
        return sel['valor']

    # ------------------------- Corretor ortográfico -------------------------
    def _habilitar_corretor_ortografico(self):
        """Configura tags e binds para correção ortográfica em PT.
        Requer 'pyspellchecker'. Se ausente, ignora silenciosamente.
        Também ativa o menu de contexto de sugestões do BaseModule."""
        try:
            txt = getattr(self, 'editor_texto', None)
            if not txt:
                return
            if SpellChecker is None:
                # Dependência ausente: não ativa
                return
            # Inicializa dicionário em português
            if self._spell is None:
                try:
                    self._spell = SpellChecker(language='pt')
                except Exception:
                    self._spell = None
                    return
            # Configura a tag visual das palavras incorretas
            try:
                txt.tag_configure('misspelled', underline=True, foreground='#c82333')
            except Exception:
                pass

            # Bind com debounce para não pesar a digitação
            def _on_key_release(event=None):
                # cancela análise pendente
                if self._spell_after_id:
                    try:
                        self.frame.after_cancel(self._spell_after_id)
                    except Exception:
                        pass
                    self._spell_after_id = None
                # agenda nova verificação
                def _run():
                    self._verificar_ortografia()
                self._spell_after_id = self.frame.after(250, _run)

            txt.bind('<KeyRelease>', _on_key_release, add=True)
            # Primeira verificação do conteúdo inicial (após prefill)
            self._verificar_ortografia()
            # Menu de contexto com sugestões (usa utilitário do BaseModule)
            try:
                self._bind_spell_menu(txt, language='pt', limit_chars=30000)
            except Exception:
                pass
        except Exception:
            pass

    def _verificar_ortografia(self):
        """Varre o texto e marca palavras desconhecidas pelo dicionário PT."""
        if not self._spell or not getattr(self, 'editor_texto', None):
            return
        txt = self.editor_texto
        try:
            # Limita análise para não travar em textos muito grandes
            conteudo = txt.get('1.0', 'end-1c')
            limite = 30000
            analisado = conteudo[:limite]

            # Limpa marcações anteriores
            txt.tag_remove('misspelled', '1.0', tk.END)

            # Encontra palavras (inclui letras acentuadas)
            for m in re.finditer(r"\b[\wÀ-ÖØ-öø-ÿ]+\b", analisado, flags=re.UNICODE):
                palavra = m.group(0)
                # Ignora números puros e tokens muito curtos
                if palavra.isdigit() or len(palavra) <= 2:
                    continue
                # Checa no dicionário
                try:
                    if palavra.lower() in self._spell:  # acesso rápido ao dicionário
                        continue
                except Exception:
                    pass
                # Método padrão da lib
                try:
                    if palavra.lower() not in self._spell:  # redundância segura
                        # Confere probabilidade: unknown retorna conjunto de não reconhecidas
                        if palavra.lower() in self._spell.unknown([palavra.lower()]):
                            start = f"1.0+{m.start()}c"
                            end = f"1.0+{m.end()}c"
                            txt.tag_add('misspelled', start, end)
                except Exception:
                    # Em caso de erro, não marca
                    continue
        except Exception:
            pass

    def _preencher_cabecalho_novo_prontuario(self):
        """Insere cabeçalho com nome do paciente e data atual no editor, se estiver vazio."""
        try:
            if not getattr(self, 'paciente_selecionado', None):
                return
            txt = getattr(self, 'editor_texto', None)
            if not txt:
                return
            # Não sobrescreve se já houver conteúdo
            if txt.get("1.0", "end-1c").strip():
                return
            nome_paciente = self.paciente_selecionado.get('nome', 'Paciente')
            data_hoje = datetime.now().strftime('%d/%m/%Y')
            header = f"Paciente: {nome_paciente}\nData: {data_hoje}\n\n"
            txt.insert("1.0", header)
        except Exception:
            pass

    def _inserir_assinatura_medico(self):
        """Insere duas linhas em branco e, na sequência, o nome do médico e o CRM no final do texto."""
        try:
            txt = getattr(self, 'editor_texto', None) or getattr(self, 'texto_prontuario', None)
            if not txt:
                return
            # Obtém dados do médico a partir do usuário logado via banco (FK usuario_id) com fallback por nome
            medico_info = self._buscar_medico_por_usuario()
            usr = getattr(self, 'usuario_dict', None) or {}
            # Nome exibido: sempre prioriza o nome do médico (tabela medicos); nunca usar login
            nome = (medico_info.get('nome') if medico_info else None) or (usr.get('nome') or 'Médico')
            nome = (nome or 'Médico').strip()
            crm = (medico_info.get('crm') if medico_info else None) or (usr.get('crm') or usr.get('CRM') or usr.get('imp') or usr.get('codigo_medico') or '')
            crm = (crm or '').strip()
            try:
                print(f"[DEBUG][Prontuario] assinatura_medico: nome='{nome}', crm='{crm}', medico_info_resolvido={bool(medico_info)}")
            except Exception:
                pass
            assinatura = f"{nome}\nCRM: {crm}" if crm else f"{nome}\nCRM: ______"
            # Garante separação de duas linhas em branco antes da assinatura
            # e centraliza horizontalmente o bloco inserido
            try:
                txt.tag_configure('center', justify='center')
            except Exception:
                pass
            start_idx = txt.index(tk.END)
            txt.insert(tk.END, "\n\n" + assinatura)
            end_idx = txt.index(tk.END)
            try:
                txt.tag_add('center', start_idx, end_idx)
            except Exception:
                pass
            try:
                # Reaplica verificação ortográfica, se ativo
                self._verificar_ortografia()
            except Exception:
                pass
        except Exception:
            pass

    def _buscar_medico_por_usuario(self):
        """Busca nome e CRM do médico vinculado ao usuário logado.
        Estratégia:
        1) Tenta SELECT por medicos.usuario_id = usuarios.id (se a coluna existir).
        2) Se não achar, tenta vincular automaticamente por (nome + telefone) e repete (1).
        3) Fallback: tenta por nome e filtra por telefone (quando disponível), senão usa o primeiro.
        Retorna dict {nome, crm} ou None.
        """
        try:
            usr = getattr(self, 'usuario_dict', None) or {}
            user_id = usr.get('id')
            if not user_id:
                return None
            db = self._obter_conexao_valida()
            if not db:
                return None
            cur = db.cursor()
            try:
                print(f"[DEBUG][Prontuario] buscar_medico_por_usuario: user_id={user_id}")
            except Exception:
                pass
            # 1) Tenta por FK usuario_id (se existir)
            try:
                cur.execute("SELECT nome, crm FROM medicos WHERE usuario_id = %s LIMIT 1", (user_id,))
                row = cur.fetchone()
                if row:
                    try:
                        print(f"[DEBUG][Prontuario] médico encontrado por usuario_id: nome='{row[0]}', crm='{row[1]}'")
                    except Exception:
                        pass
                    return {"nome": row[0], "crm": row[1]}
            except Exception:
                # coluna pode não existir; segue para fallback
                pass
            # 2) Tenta vincular automaticamente por nome+telefone e tenta novamente por usuario_id
            try:
                print("[DEBUG][Prontuario] tentando vincular medico por nome+telefone...")
                self._tentar_vincular_medico_por_nome_telefone()
                try:
                    cur.execute("SELECT nome, crm FROM medicos WHERE usuario_id = %s LIMIT 1", (user_id,))
                    row = cur.fetchone()
                    if row:
                        try:
                            print(f"[DEBUG][Prontuario] médico vinculado e encontrado: nome='{row[0]}', crm='{row[1]}'")
                        except Exception:
                            pass
                        return {"nome": row[0], "crm": row[1]}
                except Exception:
                    pass
            except Exception:
                pass
            # 2) Fallback por nome (pode gerar múltiplos; pega o primeiro)
            try:
                nome_usr = (usr.get('nome') or '').strip()
                tel_usr = (usr.get('telefone') or '').strip()
                if not nome_usr:
                    return None
                cur.execute("SELECT id, nome, crm, telefone, usuario_id FROM medicos WHERE LOWER(nome) = LOWER(%s)", (nome_usr,))
                rows = cur.fetchall() or []
                if not rows:
                    try:
                        print(f"[DEBUG][Prontuario] nenhum médico encontrado por nome='{nome_usr}'")
                    except Exception:
                        pass
                    return None
                # Se houver telefone do usuário, tente match exato de telefone normalizado
                if tel_usr:
                    nt_usr = self._normalizar_telefone(tel_usr)
                    candidatos = []
                    for r in rows:
                        nt_med = self._normalizar_telefone(r[3] or '')
                        if nt_med and nt_med == nt_usr:
                            candidatos.append(r)
                    if len(candidatos) == 1:
                        r = candidatos[0]
                        try:
                            print(f"[DEBUG][Prontuario] médico por nome+telefone: nome='{r[1]}', crm='{r[2]}'")
                        except Exception:
                            pass
                        return {"nome": r[1], "crm": r[2]}
                    # se múltiplos, preferir aquele que já tem usuario_id preenchido
                    for r in candidatos:
                        if r[4]:
                            try:
                                print(f"[DEBUG][Prontuario] múltiplos por nome+telefone, escolhendo com usuario_id: nome='{r[1]}', crm='{r[2]}'")
                            except Exception:
                                pass
                            return {"nome": r[1], "crm": r[2]}
                else:
                    # Sem telefone do usuário: se houver exatamente um médico com este nome, usar este
                    if len(rows) == 1:
                        r = rows[0]
                        try:
                            print(f"[DEBUG][Prontuario] único médico por nome (sem telefone): nome='{r[1]}', crm='{r[2]}'")
                        except Exception:
                            pass
                        return {"nome": r[1], "crm": r[2]}
                # fallback: primeiro registro por nome
                r = rows[0]
                try:
                    print(f"[DEBUG][Prontuario] fallback por nome: nome='{r[1]}', crm='{r[2]}'")
                except Exception:
                    pass
                return {"nome": r[1], "crm": r[2]}
            except Exception:
                return None
        except Exception:
            return None

    def _normalizar_telefone(self, tel: str) -> str:
        """Mantém apenas dígitos para comparação (ex.: '(11) 99999-0000' -> '11999990000')."""
        try:
            return re.sub(r"\D+", "", tel or "")
        except Exception:
            return tel or ""

    def _tentar_vincular_medico_por_nome_telefone(self):
        """Se encontrar exatamente um médico com mesmo nome e telefone do usuário e sem vinculação,
        atualiza medicos.usuario_id.
        """
        try:
            usr = getattr(self, 'usuario_dict', None) or {}
            user_id = usr.get('id')
            nome_usr = (usr.get('nome') or '').strip()
            tel_usr = (usr.get('telefone') or '').strip()
            if not (user_id and nome_usr):
                try:
                    print("[DEBUG][Prontuario] vinculação ignorada: faltam user_id/nome")
                except Exception:
                    pass
                return False
            db = self._obter_conexao_valida()
            if not db:
                try:
                    print("[DEBUG][Prontuario] vinculação ignorada: sem conexão DB válida")
                except Exception:
                    pass
                return False
            cur = db.cursor()
            nt_usr = self._normalizar_telefone(tel_usr)
            # Busca todos com mesmo nome (case-insensitive)
            cur.execute("SELECT id, nome, crm, telefone, usuario_id FROM medicos WHERE LOWER(nome) = LOWER(%s)", (nome_usr,))
            rows = cur.fetchall() or []
            # Filtra por telefone normalizado igual
            candidatos = []
            if tel_usr:
                for r in rows:
                    nt_med = self._normalizar_telefone(r[3] or '')
                    if nt_med and nt_med == nt_usr:
                        candidatos.append(r)
                if len(candidatos) != 1:
                    try:
                        print(f"[DEBUG][Prontuario] vinculação: candidatos por nome+telefone = {len(candidatos)} (esperado 1)")
                    except Exception:
                        pass
                    return False
                r = candidatos[0]
            else:
                # Sem telefone: só vincula se houver exatamente um médico com o nome e ainda sem usuario_id
                sem_vinculo = [r for r in rows if not r[4]]
                if len(sem_vinculo) != 1:
                    try:
                        print(f"[DEBUG][Prontuario] vinculação por nome (sem telefone) ambígua: candidatos_sem_vinculo={len(sem_vinculo)}")
                    except Exception:
                        pass
                    return False
                r = sem_vinculo[0]
            if r[4]:
                # já vinculado
                try:
                    print(f"[DEBUG][Prontuario] vinculação: já possuía usuario_id (medico_id={r[0]})")
                except Exception:
                    pass
                return False
            # Atualiza vinculação
            cur.execute("UPDATE medicos SET usuario_id = %s WHERE id = %s", (user_id, r[0]))
            try:
                db.commit()
            except Exception:
                pass
            try:
                print(f"[DEBUG][Prontuario] vinculação realizada: medico_id={r[0]}, user_id={user_id}")
            except Exception:
                pass
            return True
        except Exception:
            return False

    def _mostrar_prontuario_modal(self, prontuario):
        """Exibe um prontuário histórico em uma janela modal de visualização."""
        dlg = tk.Toplevel(self.frame)
        dlg.title(f"Prontuário #{prontuario.get('id', '')}")
        dlg.geometry("700x500")
        dlg.transient(self.frame)
        dlg.grab_set()
        body = tk.Frame(dlg, bg='#f0f2f5', padx=10, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho
        info = tk.Frame(body, bg='#f0f2f5')
        info.pack(fill=tk.X)
        data = prontuario.get("data_criacao") or prontuario.get("data")
        if isinstance(data, str):
            try:
                d = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                data_fmt = d.strftime('%d/%m/%Y %H:%M')
            except Exception:
                data_fmt = str(data)
        else:
            data_fmt = data.strftime('%d/%m/%Y %H:%M') if data else 'N/A'
        tk.Label(info, text=f"Data: {data_fmt}", bg='#f0f2f5', font=('Arial', 10, 'italic')).pack(anchor='w')
        tk.Label(info, text=f"Médico: {prontuario.get('nome_medico', 'N/I')}", bg='#f0f2f5', font=('Arial', 10, 'italic')).pack(anchor='w')

        # Conteúdo
        txt = scrolledtext.ScrolledText(body, wrap=tk.WORD, font=('Arial', 10), state=tk.NORMAL)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, prontuario.get('conteudo', ''))
        txt.config(state=tk.DISABLED)

        # Fechar
        tk.Button(body, text="Fechar", command=dlg.destroy).pack(pady=8)
    
    def _salvar_novo_prontuario(self):
        """Salva um novo prontuário."""
        # Valida paciente selecionado
        if not self.paciente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um paciente antes de salvar o prontuário.")
            return
        # Garante que há um usuário logado (usuario_id) para atribuir ao prontuário
        usuario_id = None
        try:
            usuario_id = (getattr(self, 'usuario_dict', None) or {}).get('id')
        except Exception:
            usuario_id = None
        if not usuario_id:
            messagebox.showwarning(
                "Aviso",
                "Não foi possível identificar o usuário logado. Faça login novamente."
            )
            return
        
        # Obtém o conteúdo do editor
        origem = getattr(self, 'editor_texto', None) or getattr(self, 'texto_prontuario', None)
        conteudo = origem.get(1.0, tk.END).strip() if origem else ''
        
        if not conteudo:
            messagebox.showinfo("Aviso", "O conteúdo do prontuário não pode estar vazio")
            return
        
        # Monta os dados conforme schema da tabela 'prontuarios'
        primeira_linha = (conteudo.splitlines()[0] if conteudo.splitlines() else "").strip()
        titulo = (primeira_linha or "Prontuário")[0:255]

        dados = {
            "paciente_id": self.paciente_selecionado["id"],
            "usuario_id": usuario_id,
            "conteudo": conteudo,
            "data": datetime.now().strftime('%Y-%m-%d'),  # campo 'data' é DATE na tabela
            "titulo": titulo,
            "consulta_id": None  # manter None se não houver consulta vinculada
        }
        
        sucesso, resultado = self.prontuario_controller.criar_prontuario(dados)
        
        if sucesso:
            messagebox.showinfo("Sucesso", "Prontuário criado com sucesso")
            
            # Recarrega o painel de prontuários
            self._carregar_prontuarios()
        else:
            messagebox.showerror("Erro", f"Não foi possível criar o prontuário: {resultado}")
    
    def _on_change_busca(self, event=None):
        """Dispara busca com pequeno atraso ao digitar, como em Consultas."""
        # cancela agendamento anterior
        if hasattr(self, '_busca_after_id') and self._busca_after_id:
            try:
                self.frame.after_cancel(self._busca_after_id)
            except Exception:
                pass
            self._busca_after_id = None
        # agenda nova execução
        def _run():
            termo = self.busca_var.get().strip()
            if termo:
                self._buscar_paciente()
            else:
                # limpar lista se vazio
                for item in self.resultados_tree.get_children():
                    self.resultados_tree.delete(item)
        self._busca_after_id = self.frame.after(200, _run)

    def _selecionar_modelo(self):
        """Abre uma janela para selecionar um modelo de texto para inserir no prontuário."""
        # Verifica se está em modo de edição
        if not self.modo_edicao:
            messagebox.showinfo("Aviso", "É necessário estar em modo de edição para inserir modelos")
            return
        
        # Verifica se o usuário é um médico: aceita se nivel='medico' ou se houver medico_id mapeado
        nivel_usr = ((self.usuario_dict or {}).get('nivel') or '').strip().lower()
        if not (nivel_usr == 'medico' or self.medico_id):
            messagebox.showinfo("Aviso", "É necessário estar logado como médico para usar modelos")
            return
        if nivel_usr == 'medico' and not self.medico_id:
            try:
                print("[DEBUG][Prontuario] prosseguindo com inserção de modelo: nivel=medico porém medico_id não mapeado; usaremos fallback de identificadores")
            except Exception:
                pass
        
        # Busca os modelos do médico com fallback de identificadores
        try:
            print("[DEBUG][Prontuario] _selecionar_modelo: iniciando listagem de modelos")
        except Exception:
            pass
        try:
            modelos = self._listar_modelos_compat()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar modelos de texto: {e}")
            return
        
        if not modelos:
            messagebox.showinfo(
                "Nenhum Modelo",
                "Você ainda não possui modelos de texto disponíveis."
            )
            return
        
        # Cria um diálogo modal
        dialogo = tk.Toplevel(self.frame)
        dialogo.title("Selecionar Modelo de Texto")
        dialogo.geometry("900x650")
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
        
        # Listbox com os modelos (altura maior)
        listbox = tk.Listbox(
            frame_listbox,
            font=('Arial', 11),
            selectbackground='#4a6fa5',
            selectforeground='white',
            activestyle='none',
            height=20
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
        
        # Removido preview do modelo por solicitação
        
        # Frame para os botões
        frame_botoes = tk.Frame(frame_principal, bg='#f0f2f5')
        frame_botoes.pack(fill=tk.X, pady=(0, 5))
        
        # Removido: função de pré-visualização, não é mais necessária
        
        # Função para inserir o modelo selecionado
        def inserir_modelo():
            selecao = listbox.curselection()
            if not selecao:
                messagebox.showinfo("Aviso", "Selecione um modelo para inserir")
                return
            
            modelo_id = modelo_ids[selecao[0]]
            modelo = self.prontuario_controller.buscar_modelo_por_id(modelo_id)
            
            if not modelo:
                return
            
            # Obtém o conteúdo do modelo exatamente como foi salvo
            conteudo = modelo["conteudo"]
            # Se o conteúdo possuir diretiva <<font:N>>, aplica no editor para manter padrão visual
            try:
                m = re.search(r"^\s*<<font:(\d{1,2})>>\s*$", conteudo, flags=re.IGNORECASE | re.MULTILINE)
                if m:
                    n = int(m.group(1))
                    if 6 <= n <= 12:
                        try:
                            self.editor_texto.configure(font=('Arial', n))
                        except Exception:
                            pass
            except Exception:
                pass
            
            # Insere no NOVO editor do prontuário (somente a tela atual)
            try:
                existente = self.editor_texto.get("1.0", "end-1c").strip()
                if existente:
                    self.editor_texto.insert(tk.END, "\n\n")
            except Exception:
                pass
            self.editor_texto.insert(tk.END, conteudo)
            # Assinatura do médico duas linhas abaixo do modelo inserido
            try:
                self._inserir_assinatura_medico()
            except Exception:
                pass
            
            # Fecha o diálogo
            dialogo.destroy()
        
        # Duplo clique para inserir diretamente
        listbox.bind("<Double-1>", lambda e: inserir_modelo())
        
        # Botões de ação
        tk.Button(
            frame_botoes,
            text="Inserir",
            command=inserir_modelo,
            bg="#4a6fa5",
            fg="white",
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=5, pady=2)
        
        tk.Button(
            frame_botoes,
            text="Cancelar",
            command=dialogo.destroy,
            bg="#6c757d",
            fg="white",
            relief=tk.FLAT,
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=5, pady=2)
        
        # Removido botão 'Gerenciar Modelos' por solicitação
        
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
        
        # Botões para a lista (sem criação de modelos nesta tela)
        frame_botoes_lista = tk.Frame(frame_lista, bg='#f0f2f5')
        frame_botoes_lista.pack(fill=tk.X, pady=(10, 0))
        
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
            
            # Carrega os modelos do médico com fallback de identificadores
            try:
                modelos = self._listar_modelos_compat()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao listar modelos de texto: {e}")
                return
            
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
                # modelos_texto agora usa usuario_id
                "usuario_id": (self.usuario_dict or {}).get('id')
            }
            
            sucesso, resultado = self.prontuario_controller.criar_modelo_texto(dados)
            
            if sucesso:
                messagebox.showinfo("Sucesso", "Modelo criado com sucesso!")
                
                # Recarrega a lista de modelos
                listbox.delete(0, tk.END)
                modelo_ids.clear()
                
                modelos = self.prontuario_controller.listar_modelos_texto((self.usuario_dict or {}).get('id'))
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
        """Exibe o módulo sem adicionar elementos extras na tela."""
        # Apenas garante que o frame do módulo esteja na tela
        self.frame.pack(fill=tk.BOTH, expand=True)

    def _criar_novo_prontuario(self):
        """Prepara o editor à direita para um novo prontuário, limpo e pronto para edição."""
        # Garante que o container da direita exista
        if not hasattr(self, 'prontuario_content_frame') or not self.prontuario_content_frame.winfo_exists():
            return
        # Limpa o conteúdo atual do painel direito
        for w in self.prontuario_content_frame.winfo_children():
            w.destroy()
        # Renderiza novamente o editor de novo prontuário
        self._render_editor_novo_prontuario(self.prontuario_content_frame)
        # Foco no editor
        try:
            self.editor_texto.focus_set()
        except Exception:
            pass
