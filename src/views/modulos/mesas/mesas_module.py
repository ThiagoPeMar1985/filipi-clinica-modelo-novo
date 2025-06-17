import tkinter as tk
from tkinter import ttk

class MesasModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        self.db_connection = getattr(controller, 'db_connection', None)
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "Visualizar Mesas", "acao": "visualizar"},
            {"nome": "Editar Mesas", "acao": "editar"},
            {"nome": "Transferir Mesa", "acao": "transferir"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        if self.current_view:
            self.current_view.destroy()
            
        if acao == 'visualizar':
            self._show_visualizar()
        elif acao == 'editar':
            self._show_editar()
        elif acao == 'transferir':
            self._show_transferir()
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo de mesas
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção de mesas no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_visualizar(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Visualização de Mesas", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione a visualização de mesas aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_editar(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Edição de Mesas", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione a edição de mesas aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_transferir(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Transferir Mesa", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione a transferência de mesa aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
