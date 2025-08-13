"""
Módulo base para todos os módulos do sistema.
Fornece funcionalidades comuns e estilos padronizados.
"""
import tkinter as tk
from tkinter import ttk
import re
import sys
try:
    # Corretor ortográfico opcional
    from spellchecker import SpellChecker
except Exception:
    SpellChecker = None

class BaseModule:
    def __init__(self, parent, controller):
        """
        Inicializa o módulo base.
        
        Args:
            parent: Widget pai onde o módulo será exibido
            controller: Controlador principal da aplicação
        """
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        # Estado compartilhado do corretor (por módulo)
        self._spellchecker = None
        self._spell_jobs = {}
        
        # Configura os estilos padrão
        self.configurar_estilos()
        
        # Aplica os estilos iniciais
        self.aplicar_estilos()
        # Controller financeiro (cache em módulos não-financeiros)
        self._fin_controller = None

    # ------------------------- Utilitário: Corretor ortográfico -------------------------
    def _get_spellchecker(self, language: str = 'pt'):
        """Obtém (cache) uma instância do SpellChecker para o idioma informado."""
        # Em executável (PyInstaller), desativa para evitar erros de locale/language
        if getattr(sys, 'frozen', False):
            return None
        if SpellChecker is None:
            return None
        try:
            if not self._spellchecker:
                self._spellchecker = SpellChecker(language=language)
        except Exception:
            self._spellchecker = None
        return self._spellchecker

    def _enable_spellcheck(self, text_widget: tk.Text, language: str = 'pt', limit_chars: int = 30000):
        """Ativa verificação ortográfica em um widget Text/ScrolledText.
        - Sublinha em vermelho palavras desconhecidas (tag 'misspelled').
        - Debounce para não pesar a digitação.
        Se a dependência não existir, não faz nada.
        """
        try:
            if text_widget is None or not hasattr(text_widget, 'winfo_exists'):
                return
            sc = self._get_spellchecker(language)
            if sc is None:
                return
            # Configuração de tag
            try:
                text_widget.tag_configure('misspelled', underline=True, foreground='#c82333')
            except Exception:
                pass

            # Função de verificação
            def _run_check():
                try:
                    conteudo = text_widget.get('1.0', 'end-1c')
                    analisado = conteudo[:limit_chars]
                    text_widget.tag_remove('misspelled', '1.0', tk.END)
                    for m in re.finditer(r"\b[\wÀ-ÖØ-öø-ÿ]+\b", analisado, flags=re.UNICODE):
                        palavra = m.group(0)
                        if palavra.isdigit() or len(palavra) <= 2:
                            continue
                        low = palavra.lower()
                        try:
                            # unknown é mais confiável que 'in'
                            if low in sc.unknown([low]):
                                start = f"1.0+{m.start()}c"
                                end = f"1.0+{m.end()}c"
                                text_widget.tag_add('misspelled', start, end)
                        except Exception:
                            continue
                except Exception:
                    pass

            # Debounce por widget
            def _on_key_release(event=None):
                try:
                    job = self._spell_jobs.get(text_widget)
                    if job:
                        self.frame.after_cancel(job)
                except Exception:
                    pass
                self._spell_jobs[text_widget] = self.frame.after(250, _run_check)

            text_widget.bind('<KeyRelease>', _on_key_release, add=True)
            # Primeira checagem imediata
            _run_check()
            # Context menu (botão direito) para correções
            try:
                self._bind_spell_menu(text_widget, language, limit_chars)
            except Exception:
                pass
        except Exception:
            pass

    def _spellcheck_now(self, text_widget: tk.Text, language: str = 'pt', limit_chars: int = 30000):
        """Força a verificação ortográfica imediatamente para o conteúdo atual.
        Útil após inserir texto programaticamente (ex.: carregar/editar receita)."""
        try:
            if text_widget is None or not hasattr(text_widget, 'winfo_exists'):
                return
            sc = self._get_spellchecker(language)
            if sc is None:
                return
            try:
                text_widget.tag_configure('misspelled', underline=True, foreground='#c82333')
            except Exception:
                pass
            conteudo = text_widget.get('1.0', 'end-1c')
            analisado = conteudo[:limit_chars]
            text_widget.tag_remove('misspelled', '1.0', tk.END)
            for m in re.finditer(r"\b[\wÀ-ÖØ-öø-ÿ]+\b", analisado, flags=re.UNICODE):
                palavra = m.group(0)
                if palavra.isdigit() or len(palavra) <= 2:
                    continue
                low = palavra.lower()
                try:
                    if low in sc.unknown([low]):
                        start = f"1.0+{m.start()}c"
                        end = f"1.0+{m.end()}c"
                        text_widget.tag_add('misspelled', start, end)
                except Exception:
                    continue
        except Exception:
            pass

    def _bind_spell_menu(self, text_widget: tk.Text, language: str = 'pt', limit_chars: int = 30000):
        """Associa menu de contexto (botão direito) para corrigir palavras 'misspelled'."""
        try:
            if text_widget is None or not hasattr(text_widget, 'winfo_exists'):
                return
            # Evita múltiplos binds no mesmo widget
            if getattr(text_widget, '_spell_menu_bound', False):
                return
            sc = self._get_spellchecker(language)
            if sc is None:
                return

            def _on_right_click(event):
                try:
                    # 1) Tenta palavra sob o ponteiro do mouse
                    idx = text_widget.index(f"@{event.x},{event.y}")
                    start = text_widget.index(f"{idx} wordstart")
                    end = text_widget.index(f"{idx} wordend")
                    palavra = text_widget.get(start, end)
                    low = palavra.lower()
                    valida = bool(palavra) and not low.isdigit() and len(low) > 2
                    desconhecida = False
                    if valida:
                        try:
                            desconhecida = (low in sc.unknown([low]))
                        except Exception:
                            desconhecida = False
                    # 2) Se não for válida/desconhecida, tenta palavra no cursor de inserção
                    if not (valida and desconhecida):
                        idx = text_widget.index('insert')
                        start = text_widget.index(f"{idx} wordstart")
                        end = text_widget.index(f"{idx} wordend")
                        palavra = text_widget.get(start, end)
                        low = palavra.lower()
                        valida = bool(palavra) and not low.isdigit() and len(low) > 2
                        if valida:
                            try:
                                desconhecida = (low in sc.unknown([low]))
                            except Exception:
                                desconhecida = False
                    if not (valida and desconhecida):
                        return
                    try:
                        best = sc.correction(low)
                    except Exception:
                        best = None
                    try:
                        cand = list(sc.candidates(low))
                    except Exception:
                        cand = []
                    opcoes = []
                    if best:
                        opcoes.append(best)
                    for c in cand:
                        if c and c not in opcoes:
                            opcoes.append(c)
                    opcoes = opcoes[:7]

                    menu = tk.Menu(text_widget, tearoff=0)
                    if opcoes:
                        for s in opcoes:
                            def _repl(sug=s, s_idx=start, e_idx=end, original=palavra):
                                try:
                                    rep = sug.capitalize() if original[:1].isupper() else sug
                                    prev = text_widget.cget('state')
                                    try:
                                        text_widget.config(state='normal')
                                        text_widget.delete(s_idx, e_idx)
                                        text_widget.insert(s_idx, rep)
                                    finally:
                                        text_widget.config(state=prev)
                                    self._spellcheck_now(text_widget, language, limit_chars)
                                except Exception:
                                    pass
                            menu.add_command(label=s, command=_repl)
                    else:
                        menu.add_command(label='Sem sugestões', state='disabled')
                    menu.add_separator()
                    menu.add_command(label='Ignorar', command=lambda s_idx=start, e_idx=end: text_widget.tag_remove('misspelled', s_idx, e_idx))
                    try:
                        menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        try:
                            menu.grab_release()
                        except Exception:
                            pass
                except Exception:
                    pass

            # Windows/Linux principal
            text_widget.bind('<Button-3>', _on_right_click, add=True)
            # Compatibilidade extra (alguns ambientes usam Button-2 ou Ctrl+Click)
            text_widget.bind('<Button-2>', _on_right_click, add=True)
            text_widget.bind('<Control-Button-1>', _on_right_click, add=True)
            try:
                text_widget._spell_menu_bound = True
            except Exception:
                pass
        except Exception:
            pass
    
    def configurar_estilos(self):
        """Configura os estilos padrão para todos os widgets"""
        style = ttk.Style()
        
        # Cores padrão
        self.cores = {
            'fundo': '#f0f2f5',          # Fundo principal
            'fundo_conteudo': '#f0f2f5',  # Fundo dos painéis
            'fundo_tabela': '#ffffff',    # Fundo das tabelas
            'primaria': '#4a6fa5',        # Azul padrão
            'secundaria': '#3b5a7f',      # Azul mais escuro (hover)
            'terciaria': '#333f50',
            'texto': '#000000',
            'texto_claro': '#ffffff',
            'texto_cabecalho': '#ffffff', # Texto do cabeçalho
            'destaque': '#4CAF50',        # Verde
            'destaque_hover': '#43a047',  # Verde mais escuro (hover)
            'alerta': '#f44336',          # Vermelho
            'alerta_hover': '#d32f2f',    # Vermelho mais escuro (hover)
            'borda': '#e0e0e0',
            'mesa_card': '#4CAF50'        # Verde para cards de mesa
        }
        
        # Estilo para frames
        style.configure('TFrame', background=self.cores['fundo'])
        
        # Estilo para frames de conteúdo
        style.configure('Content.TFrame', 
                      background=self.cores['fundo_conteudo'],
                      borderwidth=0,
                      relief='flat')
        
        # Estilo para labels
        style.configure('TLabel', 
                      background=self.cores['fundo_conteudo'],
                      foreground=self.cores['texto'],
                      font=('Arial', 10))
        
        # Estilo para botões padrão (azul)
        style.configure('TButton',
                      background=self.cores['primaria'],
                      foreground=self.cores['texto_claro'],
                      font=('Arial', 10, 'bold'),
                      borderwidth=0,
                      padding=5)
        style.map('TButton',
                 background=[('active', self.cores['secundaria'])],
                 foreground=[('active', self.cores['texto_claro'])])
                 
        # Estilo para botão de destaque (verde)
        style.configure('Accent.TButton',
                      background=self.cores['destaque'],
                      foreground=self.cores['texto_claro'],
                      font=('Arial', 10, 'bold'),
                      borderwidth=0,
                      padding=8)
        style.map('Accent.TButton',
                 background=[('active', self.cores['destaque_hover'])],
                 foreground=[('active', self.cores['texto_claro'])])
                 
        # Estilo para botão de alerta (vermelho)
        style.configure('Danger.TButton',
                      background=self.cores['alerta'],
                      foreground=self.cores['texto_claro'],
                      font=('Arial', 10, 'bold'),
                      borderwidth=0,
                      padding=8)
        style.map('Danger.TButton',
                 background=[('active', self.cores['alerta_hover'])],
                 foreground=[('active', self.cores['texto_claro'])])
        
        # Estilo para campos de entrada
        style.configure('TEntry',
                      fieldbackground=self.cores['fundo_tabela'],
                      foreground=self.cores['texto'],
                      borderwidth=0,
                      relief='solid')
        style.map('TEntry',
                 fieldbackground=[('readonly', self.cores['fundo_conteudo'])])
        
        # Estilo para combobox
        style.configure('TCombobox',
                      fieldbackground=self.cores['fundo_tabela'],
                      foreground=self.cores['texto'],
                      borderwidth=0,
                      relief='solid')
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.cores['fundo_tabela'])])
        
        # Estilo para abas
        style.configure('TNotebook', background=self.cores['fundo'])
        style.configure('TNotebook.Tab', 
                       padding=[10, 5],
                       background=self.cores['fundo'],
                       foreground=self.cores['texto'],
                       font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.cores['fundo_conteudo'])],
                 foreground=[('selected', self.cores['primaria'])])
                 
       
        
     
                 
        # Aplicar o estilo Custom.Treeview como padrão para todas as Treeviews
        style.configure('Treeview',
                      background='white',
                      foreground='#000000',  # Texto preto para melhor legibilidade
                      fieldbackground='white',
                      borderwidth=0,
                      relief='flat')
        style.configure('Treeview.Heading',
                      background='white',  # Fundo branco para cabeçalho
                      foreground='#000000',    # Texto preto para contraste
                      font=('Arial', 10, 'bold'),  # Texto em negrito
                      relief='flat',
                      padding=5)  # Adiciona um pouco de espaço ao redor do texto
        style.map('Treeview',
                 background=[('selected', self.cores['primaria'])],
                 foreground=[('selected', self.cores['texto_claro'])])
    
    def aplicar_estilos(self):
        """Aplica os estilos aos widgets existentes"""
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self.frame.config(style='TFrame')
            
        if hasattr(self, 'current_view') and self.current_view and self.current_view.winfo_exists():
            self._aplicar_estilos_aos_widgets(self.current_view)
    
    def _aplicar_estilos_aos_widgets(self, frame):
        """
        Aplica os estilos a todos os widgets de um frame.
        
        Args:
            frame: Frame raiz onde os estilos serão aplicados
        """
        try:
            # Configura o estilo do frame
            if isinstance(frame, (tk.Frame, ttk.Frame)):
                frame.config(style='TFrame')
                
            # Itera por todos os widgets do frame
            for widget in frame.winfo_children():
                if isinstance(widget, (tk.Frame, ttk.Frame)):
                    widget.config(style='TFrame')
                    self._aplicar_estilos_aos_widgets(widget)
                elif isinstance(widget, ttk.Label):
                    widget.config(style='TLabel')
                elif isinstance(widget, ttk.Button):
                    widget.config(style='TButton')
                elif isinstance(widget, ttk.Entry):
                    widget.config(style='TEntry')
                elif isinstance(widget, ttk.Combobox):
                    widget.config(style='TCombobox')
                elif isinstance(widget, ttk.Notebook):
                    widget.config(style='TNotebook')
                    for tab in widget.tabs():
                        widget.tab(tab, style='TNotebook.Tab')
                
                # Aplica fonte padrão se não tiver fonte definida
                if hasattr(widget, 'cget') and 'font' not in widget.config():
                    widget.config(font=('Arial', 10))
                    
        except Exception as e:
            # Ignora erros de widgets que não podem ser estilizados
            print(f"Erro ao aplicar estilos: {e}")
            pass
    
    def get_opcoes(self):
        """
        Retorna a lista de opções para a barra lateral.
        
        Deve ser sobrescrito pelos módulos filhos.
        """
        return []
    
    def show(self, acao=None):
        """
        Exibe o módulo.
        
        Deve ser sobrescrito pelos módulos filhos.
        """
        pass
    
    def _limpar_view(self):
        """Limpa a view atual"""
        if hasattr(self, 'current_view') and self.current_view:
            try:
                self.current_view.destroy()
            except tk.TclError:
                pass  # Widget já foi destruído
            self.current_view = None
    
    def _criar_titulo(self, frame, texto):
        """
        Cria um título padronizado para as telas.
        
        Args:
            frame: Frame onde o título será adicionado
            texto: Texto do título
            
        Returns:
            O frame do título
        """
        titulo_frame = ttk.Frame(frame, style='TFrame')
        ttk.Label(
            titulo_frame, 
            text=texto,
            style='TLabel',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        return titulo_frame

    # ------------------------- Utilitário: Status do Caixa (Badge) -------------------------
    def _get_financeiro_controller_base(self):
        """Obtém uma instância do FinanceiroController para ler o status do caixa."""
        try:
            if getattr(self, '_fin_controller', None):
                return self._fin_controller
            try:
                from src.controllers.financeiro_controller import FinanceiroController
            except Exception:
                return None
            db_conn = None
            for attr in ('db_connection', 'db'):
                if hasattr(self.controller, attr):
                    db_conn = getattr(self.controller, attr)
                    if db_conn:
                        break
            if db_conn is None:
                try:
                    from src.db.database import db as default_db
                    db_conn = default_db
                except Exception:
                    db_conn = None
            self._fin_controller = FinanceiroController(db_conn)
            try:
                uid = getattr(self.controller, 'usuario_id', None)
                uname = getattr(self.controller, 'usuario_nome', None)
                if hasattr(self._fin_controller, 'set_usuario'):
                    self._fin_controller.set_usuario(uid, uname)
            except Exception:
                pass
            return self._fin_controller
        except Exception:
            return None

    def create_caixa_status_badge(self, parent, pady=(10, 10)):
        """Cria e retorna um Label no topo com o status do caixa (verde/vermelho)."""
        try:
            badge = tk.Label(
                parent,
                text="",
                font=("Arial", 16, 'bold'),
                bg=self.cores.get('fundo_conteudo', '#ffffff'),
                fg=self.cores.get('texto_claro', '#ffffff'),
                padx=40,
                pady=12,
                bd=0,
                relief='flat',
            )
            badge.pack(pady=pady)
            self.refresh_caixa_status_badge(badge)
            return badge
        except Exception:
            return None

    def refresh_caixa_status_badge(self, badge: tk.Label):
        """Atualiza o label do badge conforme status atual do caixa."""
        try:
            if badge is None or not hasattr(badge, 'winfo_exists') or not badge.winfo_exists():
                return
            fc = self._get_financeiro_controller_base()
            aberto = False
            try:
                sessao = fc.get_sessao_aberta() if fc else None
                aberto = bool(sessao)
            except Exception:
                aberto = False
            if aberto:
                badge.config(text='CAIXA ABERTO', bg=self.cores.get('destaque', '#4CAF50'), fg=self.cores.get('texto_claro', '#ffffff'))
            else:
                badge.config(text='CAIXA FECHADO', bg=self.cores.get('alerta', '#f44336'), fg=self.cores.get('texto_claro', '#ffffff'))
        except Exception:
            pass
