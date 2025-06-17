import tkinter as tk
from tkinter import ttk

class EstoqueModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "Ver Estoque", "acao": "ver_estoque"},
            {"nome": "Adicionar ao Estoque", "acao": "add_estoque"},
            {"nome": "Remover do Estoque", "acao": "remover_estoque"},
            {"nome": "Criar Receita", "acao": "criar_receita"},
            {"nome": "Relatórios", "acao": "relatorios_estoque"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        if self.current_view:
            self.current_view.destroy()
            
        if acao == 'ver_estoque':
            self._show_ver_estoque()
        elif acao == 'add_estoque':
            self._show_add_estoque()
        elif acao == 'remover_estoque':
            self._show_remover_estoque()
        elif acao == 'criar_receita':
            self._show_criar_receita()
        elif acao == 'relatorios_estoque':
            self._show_relatorios_estoque()
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo de estoque
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção de estoque no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_ver_estoque(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Visualizar Estoque", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione a visualização do estoque aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_add_estoque(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Adicionar ao Estoque", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o formulário de adição de estoque aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_remover_estoque(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Remover do Estoque", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o formulário de remoção de estoque aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_criar_receita(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Criar Nova Receita", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o formulário de criação de receita aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_relatorios_estoque(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Relatórios de Estoque", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione os relatórios de estoque aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
