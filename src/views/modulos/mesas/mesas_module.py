"""
Módulo de gerenciamento de mesas do restaurante.
Permite visualizar, adicionar, editar e remover mesas.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from .editarMesas_module import EditarMesasModule
from .visualizar_module import VisualizarMesasModule
from .transferir_mesa_module import TransferirMesaModule

class MesasModule:
    def __init__(self, parent, controller):
        """
        Inicializa o módulo de gerenciamento de mesas.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
        """
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
        """
        Retorna a lista de opções para a barra lateral.
        
        Returns:
            list: Lista de dicionários com as opções do menu
        """
        return self.opcoes
    
    def show(self, acao=None):
        """
        Exibe a visualização solicitada com base na ação fornecida.
        
        Args:
            acao (str, optional): Ação a ser executada ('visualizar', 'editar', 'transferir'). 
                                Se None, exibe a visualização padrão.
        """
        # Limpar visualização atual se existir
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
        
        # Exibir a visualização solicitada
        if acao == 'visualizar':
            self._show_visualizar()
        elif acao == 'editar':
            self._show_editar()
        elif acao == 'transferir':
            self._show_transferir()
        else:
            self._show_default()
        
        # Empacotar o frame principal
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        """Exibe a tela inicial do módulo de mesas."""
        frame = ttk.Frame(self.frame, padding=20)
        
        ttk.Label(
            frame, 
            text="Gerenciamento de Mesas", 
            font=('Arial', 16, 'bold')
        ).pack(pady=(20, 10))
        
        ttk.Label(
            frame,
            text="Selecione uma opção no menu lateral para começar.",
            font=('Arial', 11)
        ).pack(pady=(0, 20))
        
        # Adicionar ícones ou instruções visuais, se necessário
        
        frame.pack(fill='both', expand=True)
        self.current_view = frame
    
    def _show_visualizar(self):
        """Exibe o módulo de visualização de mesas."""
        try:
            # Limpar a visualização atual se existir
            if self.current_view:
                self.current_view.destroy()
                
            # Criar um novo frame para a visualização
            container = tk.Frame(self.frame)
            container.pack(fill='both', expand=True)
            
            # Inicializar o módulo de visualização
            self.visualizar_module = VisualizarMesasModule(
                container, 
                self.controller,
                db_connection=self.db_connection
            )
            
            # Chamar o método show() para configurar a exibição
            self.current_view = self.visualizar_module.show()
            
        except Exception as e:
            self._show_error(f"Erro ao carregar visualização de mesas: {str(e)}")
    
    def _show_editar(self):
        """Exibe o módulo de edição de mesas."""
        try:
            self.editar_module = EditarMesasModule(
                self.frame, 
                self.controller,
                db_connection=self.db_connection
            )
            self.current_view = self.editar_module.frame
            self.current_view.pack(fill='both', expand=True, padx=20, pady=20)
        except Exception as e:
            self._show_error(f"Erro ao carregar edição de mesas: {str(e)}")
    
    def _show_transferir(self):
        """Exibe a funcionalidade de transferência de mesas."""
        try:
            print("\n=== INÍCIO _show_transferir ===")
            print(f"Tipo de self.frame: {type(self.frame)}")
            print(f"Tipo de self.controller: {type(self.controller)}")
            print(f"Conexão com banco: {'Sim' if self.db_connection else 'Não'}")
            
            # Limpar visualização atual se existir
            if self.current_view:
                print("Destruindo visualização atual...")
                self.current_view.destroy()
            
            # Criar um novo frame para o conteúdo
            content_frame = ttk.Frame(self.frame)
            content_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            print("Criando TransferirMesaModule...")
            # Inicializar o módulo de transferência
            self.transferir_module = TransferirMesaModule(
                content_frame,  # Usar o novo frame como pai
                self.controller,
                db_connection=self.db_connection
            )
            
            print("Chamando show() do TransferirMesaModule...")
            # Exibir o módulo
            self.current_view = self.transferir_module.show()
            print(f"Tipo do retorno de show(): {type(self.current_view)}")
            
            # Forçar atualização da interface
            self.frame.update_idletasks()
            
            print("=== FIM _show_transferir ===\n")
            
        except Exception as e:
            import traceback
            error_msg = f"ERRO em _show_transferir: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self._show_error(f"Erro ao carregar transferência de mesas: {str(e)}")
    
    def _show_error(self, message):
        """
        Exibe uma mensagem de erro na interface.
        
        Args:
            message (str): Mensagem de erro a ser exibida
        """
        error_frame = ttk.Frame(self.frame, padding=20)
        
        ttk.Label(
            error_frame,
            text="Erro",
            font=('Arial', 14, 'bold'),
            foreground='red'
        ).pack()
        
        ttk.Label(
            error_frame,
            text=message,
            font=('Arial', 11),
            wraplength=400
        ).pack(pady=10)
        
        ttk.Button(
            error_frame,
            text="Voltar",
            command=lambda: self.show()
        ).pack(pady=(10, 0))
        
        error_frame.pack(fill='both', expand=True)
        self.current_view = error_frame
