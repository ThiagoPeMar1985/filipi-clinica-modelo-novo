"""
Controlador base para gerenciar a lógica de negócios
"""
from abc import ABC, abstractmethod

class BaseController(ABC):
    """Classe base para todos os controladores do sistema"""
    
    def __init__(self, view):
        """Inicializa o controlador com uma referência à view"""
        self.view = view
    
    @abstractmethod
    def inicializar(self):
        """Inicializa o controlador e configura os eventos"""
        pass
    
    def mostrar_mensagem(self, titulo, mensagem, tipo='info'):
        """Exibe uma mensagem para o usuário"""
        if hasattr(self.view, 'mostrar_mensagem'):
            self.view.mostrar_mensagem(titulo, mensagem, tipo)
        else:
            # Fallback caso a view não tenha o método mostrar_mensagem
            from tkinter import messagebox
            if tipo == 'erro':
                messagebox.showerror(titulo, mensagem)
            elif tipo == 'aviso':
                messagebox.showwarning(titulo, mensagem)
            else:
                messagebox.showinfo(titulo, mensagem)
