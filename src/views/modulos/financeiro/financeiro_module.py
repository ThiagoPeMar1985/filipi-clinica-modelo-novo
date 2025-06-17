import tkinter as tk
from tkinter import ttk

class FinanceiroModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "Caixa", "acao": "caixa"},
            {"nome": "Contas a Pagar", "acao": "contas_pagar"},
            {"nome": "Contas a Receber", "acao": "contas_receber"},
            {"nome": "Relatórios", "acao": "relatorios"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        if self.current_view:
            self.current_view.destroy()
            
        if acao == 'caixa':
            self._show_caixa()
        elif acao == 'contas_pagar':
            self._show_contas_pagar()
        elif acao == 'contas_receber':
            self._show_contas_receber()
        elif acao == 'relatorios':
            self._show_relatorios()
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo financeiro
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção financeira no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_caixa(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Caixa", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o controle de caixa aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_contas_pagar(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Contas a Pagar", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o gerenciamento de contas a pagar aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_contas_receber(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Contas a Receber", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o gerenciamento de contas a receber aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_relatorios(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Relatórios Financeiros", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione os relatórios financeiros aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
