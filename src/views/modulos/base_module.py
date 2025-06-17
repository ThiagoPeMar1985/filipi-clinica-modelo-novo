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
            'fundo': '#f0f2f5',
            'fundo_conteudo': '#ffffff',
            'primaria': '#4a6fa5',
            'secundaria': '#28b5f4',
            'terciaria': '#333f50',
            'texto': '#333333',
            'texto_claro': '#ffffff',
            'destaque': '#4caf50',
            'alerta': '#f44336',
            'borda': '#e0e0e0'
        }
        
        # Estilo para frames
        style.configure('TFrame', background=self.cores['fundo_conteudo'])
        
        # Estilo para labels
        style.configure('TLabel', 
                      background=self.cores['fundo_conteudo'],
                      foreground=self.cores['texto'],
                      font=('Arial', 10))
        
        # Estilo para botões
        style.configure('TButton',
                      background=self.cores['primaria'],
                      foreground=self.cores['texto_claro'],
                      font=('Arial', 10, 'bold'),
                      borderwidth=1)
        style.map('TButton',
                 background=[('active', self.cores['secundaria'])])
        
        # Estilo para campos de entrada
        style.configure('TEntry',
                      fieldbackground=self.cores['fundo_conteudo'],
                      foreground=self.cores['texto'],
                      borderwidth=1)
        
        # Estilo para combobox
        style.configure('TCombobox',
                      fieldbackground=self.cores['fundo_conteudo'],
                      foreground=self.cores['texto'],
                      borderwidth=1)
        
        # Estilo para abas
        style.configure('TNotebook', background=self.cores['fundo'])
        style.configure('TNotebook.Tab', 
                       padding=[10, 5],
                       background=self.cores['fundo'],
                       foreground=self.cores['texto'])
        style.map('TNotebook.Tab',
                 background=[('selected', self.cores['fundo_conteudo'])],
                 foreground=[('selected', self.cores['primaria'])])
    
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
