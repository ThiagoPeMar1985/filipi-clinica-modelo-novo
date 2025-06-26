"""
Gerenciador de permissões do sistema
"""
import json
import os
from pathlib import Path

class GerenciadorPermissoes:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GerenciadorPermissoes, cls).__new__(cls)
            cls._instance.inicializar()
        return cls._instance
    
    def inicializar(self):
        """Inicializa o gerenciador de permissões"""
        # Define os caminhos dos arquivos
        self.permissoes_file = Path.home() / '.pdv_aquarius' / 'permissoes.json'
        self.permissoes_padrao_file = Path(__file__).parent.parent / 'data' / 'permissoes_padrao.json'
        
        # Garante que o diretório existe
        self.permissoes_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Carrega as permissões
        self.permissoes = self._carregar_permissoes()
        
        # Garante que o arquivo de permissões existe e está atualizado
        self._garantir_arquivo_permissoes()
    
    def _carregar_permissoes(self):
        """Carrega as permissões do arquivo de permissões personalizado ou do padrão"""
        try:
            # Tenta carregar o arquivo de permissões personalizado
            if os.path.exists(self.permissoes_file):
                with open(self.permissoes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Se não existir, carrega o arquivo padrão
            with open(self.permissoes_padrao_file, 'r', encoding='utf-8') as f:
                permissoes = json.load(f)
                
                # Salva as permissões padrão no arquivo personalizado
                with open(self.permissoes_file, 'w', encoding='utf-8') as f_out:
                    json.dump(permissoes, f_out, indent=4, ensure_ascii=False)
                
                return permissoes
                
        except Exception as e:
            # Retorna um dicionário vazio em caso de erro
            return {'modulos': {}}
            
    def _garantir_arquivo_permissoes(self):
        """Garante que o arquivo de permissões existe e está atualizado"""
        try:
            # Se o arquivo não existe, cria um novo com as permissões padrão
            if not os.path.exists(self.permissoes_file):
                # Carrega as permissões padrão
                with open(self.permissoes_padrao_file, 'r', encoding='utf-8') as f:
                    permissoes = json.load(f)
                
                # Salva as permissões no arquivo personalizado
                with open(self.permissoes_file, 'w', encoding='utf-8') as f:
                    json.dump(permissoes, f, indent=4, ensure_ascii=False)
            else:
                # Se o arquivo existe, verifica se precisa ser atualizado
                with open(self.permissoes_padrao_file, 'r', encoding='utf-8') as f:
                    permissoes_padrao = json.load(f)
                
                with open(self.permissoes_file, 'r', encoding='utf-8') as f:
                    permissoes_atual = json.load(f)
                
                # Verifica se o botão 'mostrar_opcoes' está faltando no módulo cadastro
                if ('cadastro' in permissoes_padrao.get('modulos', {}) and 
                    'mostrar_opcoes' in permissoes_padrao['modulos']['cadastro'].get('botoes', {}) and 
                    'cadastro' in permissoes_atual.get('modulos', {}) and 
                    'mostrar_opcoes' not in permissoes_atual['modulos']['cadastro'].get('botoes', {})):
                    
                    # Adiciona o botão 'mostrar_opcoes' ao módulo cadastro
                    permissoes_atual['modulos']['cadastro']['botoes']['mostrar_opcoes'] = \
                        permissoes_padrao['modulos']['cadastro']['botoes']['mostrar_opcoes']
                    
                    # Salva as permissões atualizadas
                    with open(self.permissoes_file, 'w', encoding='utf-8') as f:
                        json.dump(permissoes_atual, f, indent=4, ensure_ascii=False)
                    
        except Exception:
            pass
    
    def _criar_estrutura_padrao(self):
        """Cria uma estrutura de permissões padrão a partir do arquivo de permissões padrão"""
        permissoes = None
        
        try:
            # Tenta carregar do arquivo de permissões padrão
            from pathlib import Path
            
            # Obtém o diretório do arquivo atual
            current_dir = Path(__file__).parent
            # Monta o caminho para o arquivo de permissões padrão
            default_perms_path = current_dir.parent / 'data' / 'permissoes_padrao.json'
            
            if default_perms_path.exists():
                with open(default_perms_path, 'r', encoding='utf-8') as f:
                    permissoes = json.load(f)
                    # Adiciona os tipos de usuário
                    permissoes['tipos_usuario'] = ['basico', 'master']
        except Exception:
            pass
        
        # Se não conseguir carregar do arquivo, usa uma estrutura básica
        if permissoes is None:
            permissoes = {
                'tipos_usuario': ['basico', 'master'],
                'modulos': {
                    'vendas': {
                        'nome': 'Vendas',
                        'botoes': {
                            'nova_venda': {'nome': 'Nova Venda', 'master': True, 'basico': True},
                            'consultar_venda': {'nome': 'Consultar Venda', 'master': True, 'basico': True},
                            'cancelar_venda': {'nome': 'Cancelar Venda', 'master': True, 'basico': False},
                        }
                    },
                    'cadastro': {
                        'nome': 'Cadastros',
                        'botoes': {
                            'clientes': {'nome': 'Clientes', 'master': True, 'basico': True},
                            'produtos': {'nome': 'Produtos', 'master': True, 'basico': True},
                            'usuarios': {'nome': 'Usuários', 'master': True, 'basico': False},
                        }
                    },
                    'configuracao': {
                        'nome': 'Configurações',
                        'botoes': {
                            'geral': {'nome': 'Geral', 'master': True, 'basico': False},
                            'seguranca': {'nome': 'Segurança', 'master': True, 'basico': False},
                        }
                    }
                }
            }
        
        # Garante que o diretório existe
        self.permissoes_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Salva as permissões padrão
        self._salvar_permissoes(permissoes)
        return permissoes
    
    def _salvar_permissoes(self, permissoes):
        """Salva as permissões no arquivo"""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.permissoes_file), exist_ok=True)
            
            # Cria uma cópia das permissões para não modificar a original
            permissoes_para_salvar = {
                'tipos_usuario': ['basico', 'master'],
                'modulos': {}
            }
            
            # Copia os módulos e botões, removendo campos desnecessários
            for modulo_id, modulo_data in permissoes.get('modulos', {}).items():
                permissoes_para_salvar['modulos'][modulo_id] = {
                    'nome': modulo_data.get('nome', ''),
                    'botoes': {}
                }
                
                for botao_id, botao_data in modulo_data.get('botoes', {}).items():
                    permissoes_para_salvar['modulos'][modulo_id]['botoes'][botao_id] = {
                        'nome': botao_data.get('nome', ''),
                        'basico': bool(botao_data.get('basico', False)),
                        'master': bool(botao_data.get('master', True))
                    }
            
            # Salva no arquivo
            with open(self.permissoes_file, 'w', encoding='utf-8') as f:
                json.dump(permissoes_para_salvar, f, indent=4, ensure_ascii=False)
                f.flush()  # Força a escrita no disco
                os.fsync(f.fileno())  # Garante que os dados foram escritos
            
            # Atualiza as permissões em memória
            self.permissoes = permissoes
            return True
            
        except Exception as e:
            print(f"\nERRO ao salvar permissões: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def salvar_todas_permissoes(self, permissoes):
        """Salva todas as permissões no arquivo"""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.permissoes_file), exist_ok=True)
            
            # Salva no arquivo
            with open(self.permissoes_file, 'w', encoding='utf-8') as f:
                json.dump(permissoes, f, indent=4, ensure_ascii=False)
                f.flush()  # Força a escrita no disco
                os.fsync(f.fileno())  # Garante que os dados foram escritos
            
            # Atualiza as permissões em memória
            self.permissoes = permissoes
            return True
            
        except Exception as e:
            print(f"\nERRO ao salvar permissões: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def obter_permissoes(self, tipo_usuario):
        """
        Obtém as permissões para um tipo de usuário
        
        Args:
            tipo_usuario (str): 'admin', 'basico' ou 'master'
            
        Returns:
            dict: Dicionário com as permissões do usuário
        """
        # Cria uma cópia profunda das permissões para não modificar a original
        permissoes = {'modulos': {}}
        
        # Se for admin, retorna todas as permissões como True
        if tipo_usuario == 'admin':
            for modulo_id, dados in self.permissoes.get('modulos', {}).items():
                permissoes['modulos'][modulo_id] = {
                    'nome': dados.get('nome', ''),
                    'botoes': {}
                }
                
                for botao_id, botao in dados.get('botoes', {}).items():
                    permissoes['modulos'][modulo_id]['botoes'][botao_id] = {
                        'nome': botao.get('nome', ''),
                        'visivel': True,
                        'master': True,
                        'basico': True
                    }
                    
            return permissoes
            
        # Para outros tipos de usuário, segue a lógica normal
        for modulo_id, dados in self.permissoes.get('modulos', {}).items():
            permissoes['modulos'][modulo_id] = {
                'nome': dados.get('nome', ''),
                'botoes': {}
            }
            
            for botao_id, botao in dados.get('botoes', {}).items():
                visivel = botao.get(tipo_usuario, False)
                
                permissoes['modulos'][modulo_id]['botoes'][botao_id] = {
                    'nome': botao.get('nome', ''),
                    'visivel': visivel,
                    'master': botao.get('master', False),
                    'basico': botao.get('basico', False)
                }
                
        return permissoes
    
    def obter_todas_permissoes(self):
        """
        Retorna todas as permissões para edição
        
        Returns:
            dict: Estrutura completa de permissões
        """
        return self.permissoes
    
    def salvar_todas_permissoes(self, permissoes):
        """
        Salva todas as permissões
        
        Args:
            permissoes (dict): Estrutura completa de permissões
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        self.permissoes = permissoes
        return self._salvar_permissoes(permissoes)
    
    def atualizar_permissao(self, modulo_id, botao_id, tipo_usuario, permitido):
        """Atualiza uma permissão específica"""
        if modulo_id in self.permissoes.get('modulos', {}) and \
           botao_id in self.permissoes['modulos'][modulo_id]['botoes']:
            
            self.permissoes['modulos'][modulo_id]['botoes'][botao_id][tipo_usuario] = bool(permitido)
            return self._salvar_permissoes(self.permissoes)
        return False
