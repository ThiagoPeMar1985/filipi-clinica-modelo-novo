"""
Controlador principal do sistema PDV
"""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from src.controllers.base_controller import BaseController
from src.config.estilos import CORES, FONTES, ESTILOS_BOTAO, aplicar_estilo

class SistemaController(BaseController):
    """Controlador principal do sistema PDV"""
    
    def __init__(self, view, usuario=None):
        """
        Inicializa o controlador do sistema
        
        Args:
            view: Referência à view do sistema
            usuario: Dicionário com as informações do usuário autenticado
        """
        super().__init__(view)
        self.usuario_atual = usuario
        self.modulo_atual = None
        self.telas_abertas = {}
    
    def inicializar(self):
        """Inicializa o controlador e configura a interface"""
        self.configurar_estilos()
        self.atualizar_data_hora()
        
        # Se não houver usuário, carrega um padrão (apenas para desenvolvimento)
        if not self.usuario_atual:
            self.usuario_atual = {
                'id': 1,
                'nome': 'Usuário',
                'nivel': 'admin',
                'email': 'admin@exemplo.com'
            }
        
        self.atualizar_info_usuario()
    
    def configurar_estilos(self):
        """Configura os estilos padrão da aplicação"""
        # Estilos podem ser configurados aqui
        pass
    

    def atualizar_info_usuario(self):
        """Atualiza a exibição das informações do usuário"""
        if hasattr(self.view, 'atualizar_info_usuario'):
            self.view.atualizar_info_usuario(self.usuario_atual)
    
    def atualizar_data_hora(self):
        """Atualiza a data e hora na interface"""
        if hasattr(self.view, 'atualizar_data_hora'):
            agora = datetime.now()
            data_hora = agora.strftime("%d/%m/%Y %H:%M:%S")
            self.view.atualizar_data_hora(data_hora)
        
        # Agendar próxima atualização (a cada segundo)
        self.view.root.after(1000, self.atualizar_data_hora)
    
    def sair(self):
        """Método para encerrar o sistema"""
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.view.root.quit()
    
    def alternar_modulo(self, modulo):
        """Alterna entre os módulos do sistema"""
        self.modulo_atual = modulo
        if hasattr(self.view, 'atualizar_modulo_atual'):
            self.view.atualizar_modulo_atual(modulo)
    
    def mostrar_tela(self, nome_tela, *args, **kwargs):
        """Exibe uma tela específica na área de conteúdo"""
        if hasattr(self.view, 'mostrar_tela'):
            return self.view.mostrar_tela(nome_tela, *args, **kwargs)
        return None
