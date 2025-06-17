import tkinter as tk
from tkinter import ttk

class ModuloManager:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.modulos = {}
        self.modulo_atual = None
        
        # Frame simples para conter os módulos
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True)
        
        # Label de placeholder
        self.placeholder = ttk.Label(
            self.frame, 
            text="Selecione um módulo no menu lateral",
            font=('Arial', 12)
        )
        self.placeholder.pack(expand=True)
    
    def adicionar_modulo(self, nome, modulo_class):
        """Adiciona um novo módulo ao gerenciador"""
        self.modulos[nome] = {
            'class': modulo_class,
            'instance': None
        }
    
    def mostrar_modulo(self, nome):
        """Mostra o módulo especificado"""
        try:
            if nome not in self.modulos:
                raise ValueError(f"Módulo '{nome}' não encontrado")
            
            # Remove o placeholder
            self.placeholder.pack_forget()
            
            # Esconde o módulo atual
            if self.modulo_atual and hasattr(self.modulo_atual, 'pack_forget'):
                self.modulo_atual.pack_forget()
            
            # Cria uma nova instância se não existir
            if self.modulos[nome]['instance'] is None:
                self.modulos[nome]['instance'] = self.modulos[nome]['class'](
                    self.frame,  # Usa self.frame como parent
                    self.controller
                )
            
            # Mostra o módulo
            modulo = self.modulos[nome]['instance']
            
            # Garante que o frame do módulo esteja visível
            if not modulo.frame.winfo_ismapped():
                modulo.frame.pack(fill='both', expand=True)
                
            self.modulo_atual = modulo
            
        except Exception as e:
            print(f"Erro ao mostrar o módulo {nome}: {str(e)}")
            self.placeholder.config(
                text=f"Erro ao carregar o módulo: {str(e)}", 
                foreground='red'
            )
            self.placeholder.pack(expand=True)
            raise
    
    def obter_modulo(self, nome):
        """Retorna a instância de um módulo"""
        return self.modulos.get(nome, {}).get('instance')
