

from typing import Dict, List, Optional, Any
from src.db.database import get_db
from src.utils.gerenciador_permissoes_db import GerenciadorPermissoesDB

class PermissionController:
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
        self.gerenciador = GerenciadorPermissoesDB(self.db)
    
    def verificar_permissao(self, usuario, modulo: str, acao: Optional[str] = None) -> bool:
        """
        Verifica se um usuário tem permissão para acessar um recurso
        
        Args:
            usuario: Pode ser um objeto Usuario ou o ID do usuário (int)
            modulo: Nome do módulo
            acao: Nome da ação (opcional)
            
        Returns:
            bool: True se tiver permissão, False caso contrário
        """
        try:
            # Se for um objeto Usuario, pega o ID
            if hasattr(usuario, 'id'):
                usuario_id = int(usuario.id)
            elif hasattr(usuario, 'get_id'):
                usuario_id = int(usuario.get_id())
            elif isinstance(usuario, (int, str)):
                usuario_id = int(usuario)
            else:
                print(f"[ERRO] Não foi possível obter o ID do usuário. Tipo: {type(usuario)}")
                return False
        
            return self.gerenciador.verificar_permissao(usuario_id, modulo, acao)
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
        

    
    def obter_todas_permissoes(self) -> Dict[str, Any]:
        """
        Obtém todas as permissões do sistema
        
        Returns:
            dict: Dicionário com todas as permissões
        """
        return self.gerenciador.obter_todas_permissoes()
    
    def salvar_todas_permissoes(self, permissoes: Dict[str, Any]) -> bool:
        """
        Salva todas as permissões no banco de dados
        
        Args:
            permissoes: Dicionário com as permissões a serem salvas
            
        Returns:
            bool: True se as permissões foram salvas com sucesso
        """
        return self.gerenciador.salvar_todas_permissoes(permissoes)
    
    def obter_todos_os_perfis(self) -> List[Dict]:
        """Obtém todos os perfis do sistema"""
        perfis_map = self.gerenciador._obter_perfis_por_nome()
        # Ordena por ID para manter alinhamento estável no front-end
        return sorted(perfis_map.values(), key=lambda p: p['id'])
    
    def obter_todos_os_modulos(self) -> List[Dict]:
        """Obtém todos os módulos do sistema"""
        return list(self.gerenciador._obter_modulos_por_chave().values())
    
    def obter_botoes_por_modulo(self, modulo_id: int) -> List[Dict]:
        """Obtém todos os botões de um módulo específico"""
        botoes_por_modulo = self.gerenciador._obter_botoes_por_modulo_e_chave()
        return list(botoes_por_modulo.get(modulo_id, {}).values())
    
    def obter_permissoes_por_perfil(self, perfil_id: int) -> Dict[str, Any]:
        """
        Obtém todas as permissões de um perfil específico
        Retorna um dicionário com a estrutura: {modulo_id: {botao_id: permissao}}
        """
        query = """
            SELECT modulo_id, botao_id, permitido 
            FROM perfil_permissao 
            WHERE perfil_id = %s
        """
        permissoes = self.db.execute_query(query, (perfil_id,), fetch_all=True) or []
        
        # Estrutura o resultado
        resultado = {}
        for permissao in permissoes:
            if permissao['modulo_id'] not in resultado:
                resultado[permissao['modulo_id']] = {}
            resultado[permissao['modulo_id']][permissao['botao_id']] = bool(permissao['permitido'])
        
        return resultado
    
    def salvar_permissoes(self, perfil_id: int, permissoes: Dict[str, Any]) -> bool:
        """
        Atualiza as permissões (0 ou 1) para um perfil específico.
        Todos os botões e módulos devem existir previamente.
        
        Args:
            perfil_id: ID do perfil
            permissoes: Dicionário com a estrutura {modulo_id: {botao_id: permissao (0 ou 1)}}
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Inicia uma transação
            self.db.connection.autocommit = False
            cursor = self.db.connection.cursor()
            
            try:
                # Prepara as atualizações de permissão
                for modulo_id, botoes in permissoes.items():
                    for botao_id, permissao in botoes.items():
                        # Garante que o valor seja 0 ou 1
                        valor_permissao = 1 if permissao else 0
                        
                        # Usa ON DUPLICATE KEY UPDATE para atualizar apenas se existir
                        query = """
                            INSERT INTO perfil_permissao 
                            (perfil_id, modulo_id, botao_id, permitido)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE permitido = VALUES(permitido)
                        """
                        cursor.execute(query, (
                            int(perfil_id),
                            int(modulo_id),
                            int(botao_id),
                            valor_permissao
                        ))
                
                # Confirma a transação
                self.db.connection.commit()
                return True
                
            except Exception as e:
                # Em caso de erro, faz rollback
                self.db.connection.rollback()
                print(f"Erro ao salvar permissões: {str(e)}")
                return False
                
            finally:
                # Restaura o autocommit
                self.db.connection.autocommit = True
                cursor.close()
                
        except Exception as e:
            print(f"Erro na transação de permissões: {str(e)}")
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
            
        # Obtém o tipo de usuário (funcionario ou medico)
        nivel = getattr(usuario, 'nivel', '').lower()
        tipo_usuario = 'medico' if nivel in ['medico'] else 'funcionario'
        
        # Obtém as permissões do usuário
        permissoes = self.gerenciador.obter_permissoes(tipo_usuario)
        
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
