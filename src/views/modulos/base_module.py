"""
Módulo base para todos os módulos do sistema.
Fornece funcionalidades comuns e estilos padronizados.
"""
import tkinter as tk
from tkinter import ttk

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
        
        # Configura os estilos padrão
        self.configurar_estilos()
        
        # Aplica os estilos iniciais
        self.aplicar_estilos()
    
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
            'borda': '#e0e0e0'
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
                 
       
        
        # Estilo personalizado para Treeview sem relevo 3D
        style.configure('Custom.Treeview',
                      background='white',
                      foreground='#000000',  # Texto preto para melhor legibilidade
                      fieldbackground='white',
                      borderwidth=0,
                      relief='flat')  # Removendo o relevo 3D
        style.configure('Custom.Treeview.Heading',
                      background='#4a6fa5',  # Fundo azul para cabeçalho
                      foreground='white',    # Texto branco para contraste
                      font=('Arial', 10, 'bold'),
                      relief='flat')  # Removendo o relevo 3D do cabeçalho
        style.map('Custom.Treeview',
                 background=[('selected', '#4a6fa5')],
                 foreground=[('selected', 'white')])
                 
        # Aplicar o estilo Custom.Treeview como padrão para todas as Treeviews
        style.configure('Treeview',
                      background='white',
                      foreground='#000000',  # Texto preto para melhor legibilidade
                      fieldbackground='white',
                      borderwidth=0,
                      relief='flat')
        style.configure('Treeview.Heading',
                      background='#4a6fa5',  # Fundo azul para cabeçalho
                      foreground='white',    # Texto branco para contraste
                      font=('Arial', 10, 'bold'),
                      relief='flat')
        style.map('Treeview',
                 background=[('selected', '#4a6fa5')],
                 foreground=[('selected', 'white')])
    
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
