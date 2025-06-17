import tkinter as tk
from tkinter import ttk

class VendasModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "Venda Avulsa", "acao": "venda_avulsa"},
            {"nome": "Delivery", "acao": "delivery"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        if self.current_view:
            self.current_view.destroy()
            
        if acao == 'venda_avulsa':
            self._show_venda_avulsa()
        elif acao == 'delivery':
            self._show_delivery()
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo de vendas
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção de vendas no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_venda_avulsa(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Venda Avulsa", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione a venda avulsa aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_delivery(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Delivery", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o delivery aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
