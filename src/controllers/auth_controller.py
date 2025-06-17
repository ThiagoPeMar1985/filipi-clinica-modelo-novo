"""
Controlador de autenticação do sistema
"""
from tkinter import messagebox
from src.models.usuario import Usuario
from src.controllers.base_controller import BaseController

class AuthController(BaseController):
    """Controlador responsável pela autenticação de usuários"""
    
    def __init__(self, view=None):
        """Inicializa o controlador de autenticação"""
        super().__init__(view)
        self.usuario_autenticado = None
    
    def autenticar(self, usuario, senha):
        """
        Autentica um usuário com nome de usuário e senha
        
        Args:
            usuario (str): Nome de usuário
            senha (str): Senha do usuário
            
        Returns:
            bool: True se a autenticação for bem-sucedida, False caso contrário
        """
        try:
            usuario = Usuario.autenticar(usuario, senha)
            if usuario:
                self.usuario_autenticado = usuario
                return True
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao autenticar: {str(e)}")
            return False
    
    def obter_usuario_autenticado(self):
        """
        Retorna o usuário atualmente autenticado
        
        Returns:
            Usuario: Instância do usuário autenticado ou None
        """
        return self.usuario_autenticado
    
    def sair(self):
        """Realiza o logout do usuário atual"""
        self.usuario_autenticado = None
        return True
        
    def inicializar(self):
        """Inicializa o controlador de autenticação"""
        # Nada a ser inicializado por enquanto
        pass
