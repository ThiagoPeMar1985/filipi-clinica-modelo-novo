"""
Controlador de permissões do sistema
"""
from tkinter import messagebox
from src.utils.gerenciador_permissoes import GerenciadorPermissoes

class PermissionController:
    """Controlador responsável por gerenciar as permissões do sistema"""
    
    def __init__(self):
        """Inicializa o controlador de permissões"""
        self.gerenciador_permissoes = GerenciadorPermissoes()
    
    def verificar_permissao(self, usuario, modulo, acao=None):
        """
        Verifica se um usuário tem permissão para acessar um recurso
        
        Args:
            usuario: Instância do usuário autenticado
            modulo (str): Nome do módulo que está sendo acessado
            acao (str, optional): Ação específica dentro do módulo
            
        Returns:
            bool: True se tiver permissão, False caso contrário
        """
        try:
            # Obtém o nível do usuário em minúsculas para comparação
            nivel = getattr(usuario, 'nivel', '').lower()
            
            # Se o usuário for admin, tem acesso total a tudo
            if nivel in ['admin', 'administrador']:
                return True
                
            # Obtém o tipo de usuário (basico ou master)
            tipo_usuario = 'master' if nivel in ['gerente', 'master'] else 'basico'
            
            # Obtém as permissões do usuário
            permissoes = self.gerenciador_permissoes.obter_permissoes(tipo_usuario)
            
            # Verifica se o módulo existe nas permissões
            if modulo not in permissoes.get('modulos', {}):
                return False
                
            # Se não foi especificada uma ação, verifica apenas se tem acesso ao módulo
            if not acao:
                return True
                
            # Verifica se o botão existe e se o usuário tem permissão
            botao = permissoes['modulos'][modulo]['botoes'].get(acao, {})
            return botao.get('visivel', False)
            
        except Exception as e:
            print(f"Erro ao verificar permissão: {e}")
            return False
    
    def filtrar_menu(self, usuario, itens_menu):
        """
        Filtra os itens do menu com base nas permissões do usuário
        
        Args:
            usuario: Instância do usuário autenticado
            itens_menu (list): Lista de itens do menu
            
        Returns:
            list: Lista filtrada de itens do menu
        """
        if not itens_menu:
            return []
            
        # Obtém o nível do usuário em minúsculas para comparação
        nivel = getattr(usuario, 'nivel', '').lower()
            
        # Se for admin, retorna todos os itens sem filtrar
        if nivel in ['admin', 'administrador']:
            return itens_menu
            
        # Obtém o tipo de usuário (basico ou master)
        nivel = getattr(usuario, 'nivel', '').lower()
        tipo_usuario = 'master' if nivel in ['gerente', 'master'] else 'basico'
        
        # Obtém as permissões do usuário
        permissoes = self.gerenciador_permissoes.obter_permissoes(tipo_usuario)
        
        # Filtra os itens do menu
        itens_filtrados = []
        
        for item in itens_menu:
            # Se o item tiver subitens, filtra os subitens
            if 'subitens' in item:
                subitens_filtrados = []
                for subitem in item.get('subitens', []):
                    # Verifica se o usuário tem permissão para ver o subitem
                    if self.verificar_permissao(usuario, item.get('modulo', ''), subitem.get('acao')):
                        subitens_filtrados.append(subitem)
                
                # Se houver subitens visíveis, adiciona o item principal
                if subitens_filtrados:
                    novo_item = item.copy()
                    novo_item['subitens'] = subitens_filtrados
                    itens_filtrados.append(novo_item)
            else:
                # Verifica se o usuário tem permissão para ver o item
                if self.verificar_permissao(usuario, item.get('modulo', ''), item.get('acao')):
                    itens_filtrados.append(item)
        
        return itens_filtrados
