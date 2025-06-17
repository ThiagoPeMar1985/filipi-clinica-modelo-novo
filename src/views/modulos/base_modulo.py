import tkinter as tk
from tkinter import ttk

class BaseModulo(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.configurar_estilos()
        self.criar_widgets()
    
    def configurar_estilos(self):
        # Estilos comuns podem ser definidos aqui
        self.estilo = ttk.Style()
        self.estilo.configure('Titulo.TLabel', 
                           font=('Arial', 12, 'bold'),
                           padding=5)
    
    def criar_widgets(self):
        # Método que será sobrescrito por cada módulo
        pass
    
    def atualizar_dados(self):
        # Método para atualizar os dados exibidos no módulo
        pass
