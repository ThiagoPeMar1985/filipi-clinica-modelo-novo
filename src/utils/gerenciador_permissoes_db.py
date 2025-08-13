"""
Gerenciador de permissões baseado em banco de dados
"""
from typing import Optional, Dict, Any, List
from src.db.database import get_db
import traceback

class GerenciadorPermissoesDB:
    """Gerencia permissões no banco de dados"""
    
    def __init__(self, db=None):
        self.db = db if db is not None else get_db()
    
    def verificar_permissao(self, usuario_id: int, modulo: str, acao: Optional[str] = None) -> bool:

        try:
            # Mapeamento de módulos para suas chaves no banco
            modulos_map = {
                'cadastro': 'cadastro',
                'atendimento': 'atendimento',
                'financeiro': 'financeiro',
                'configuracao': 'configuracao'
            }
            
            # Mapeamento de ações para suas chaves no banco
            acoes_map = {
                # Módulo Cadastro (ID 1)
                'empresa': 'empresa',
                'usuarios': 'usuarios',
                'medicos': 'medicos',
                'pacientes': 'pacientes',  
                'modelo': 'modelo',  
                'receita': 'receita',  
                'exames_consultas': 'exames_consultas',
                # Módulo Atendimento (ID 2)
                'agenda': 'agenda',
                'area_medica': 'area_medica',
                'exames': 'exames', 
                # Módulo Financeiro (ID 3)
                'caixa': 'caixa',
                'contas_pagar': 'contas_pagar',
                'contas_receber': 'contas_receber',
                'relatorios': 'relatorios',
                'estoque': 'estoque',
                # Módulo Configuração (ID 4)
                'nfe': 'nfe',
                'backup': 'backup',
                'impressoras': 'impressoras',
                'banco_dados': 'banco_dados',
                # Botão no banco utiliza chave 'integracoes' (plural)
                'integracao': 'integracoes',   # alias singular
                'integracoes': 'integracoes',  # chave real no DB
                'seguranca': 'seguranca'
            }

            # Obtém as chaves normalizadas
            modulo_chave = modulos_map.get(modulo, modulo)
            acao_chave = acoes_map.get(acao, acao) if acao else None
            
            # Consulta o perfil do usuário
            query_perfil = """
                SELECT p.id as perfil_id
                FROM usuarios u
                JOIN perfil p ON u.nivel = p.nome
                WHERE u.id = %s
                LIMIT 1
            """
            resultado = self.db.execute_query(query_perfil, (usuario_id,), fetch_all=False)
            
            if not resultado or 'perfil_id' not in resultado:
                print(f"[ERRO] Perfil não encontrado para o usuário {usuario_id}")
                return False
                
            perfil_id = resultado['perfil_id']
            
            # Se não há ação, verifica permissão no módulo
            if not acao_chave:
                return self._verificar_permissao_modulo(perfil_id, modulo_chave)
                
            # Verifica permissão na ação
            return self._verificar_permissao_acao(perfil_id, modulo_chave, acao_chave)
            
        except Exception as e:
            print(f"[ERRO] Erro ao verificar permissão: {e}")
            try:
                print(f"[ERRO] Tipo: {type(e)}")
                traceback.print_exc()
            except Exception:
                pass
            return False

    def _verificar_permissao_modulo(self, perfil_id: int, modulo: str) -> bool:
        """Verifica permissão para o módulo"""
        try:
            query = """
                SELECT MAX(CASE WHEN pp.permitido = 1 THEN 1 ELSE 0 END) AS permitido
                FROM perfil_permissao pp
                JOIN modulos m ON pp.modulo_id = m.id
                WHERE pp.perfil_id = %s
                  AND m.chave = %s
            """
            
            resultado = self.db.execute_query(query, (perfil_id, modulo), fetch_all=False)
            
            return bool(resultado and resultado.get('permitido'))
        except Exception as e:
            print(f"[ERRO] Erro ao verificar permissão de módulo: {e}")
            try:
                print(f"[ERRO] Tipo: {type(e)}")
                traceback.print_exc()
            except Exception:
                pass
            return False

    def _verificar_permissao_acao(self, perfil_id: int, modulo: str, acao: str) -> bool:
        """Verifica permissão para ação específica"""
        try:
            query = """
                SELECT pp.permitido
                FROM perfil_permissao pp
                JOIN botoes b ON pp.botao_id = b.id
                JOIN modulos m ON pp.modulo_id = m.id
                WHERE pp.perfil_id = %s 
                AND m.chave = %s 
                AND b.chave = %s
                LIMIT 1
            """
            resultado = self.db.execute_query(query, (perfil_id, modulo, acao), fetch_all=False)
            return bool(resultado and resultado.get('permitido'))
        except Exception as e:
            print(f"[ERRO] Erro ao verificar permissão de ação: {e}")
            try:
                print(f"[ERRO] Tipo: {type(e)}")
                traceback.print_exc()
            except Exception:
                pass
            return False
    
    def obter_todas_permissoes(self) -> Dict[str, Any]:
        """
        Obtém todas as permissões do sistema com os valores para cada perfil
        
        Returns:
            dict: Dicionário com todas as permissões
        """
        permissoes = {'modulos': {}}
        
        try:
            # Obtém todos os perfis (ordenados por ID, sem criar/alterar registros)
            perfis = self.db.execute_query("SELECT id, nome FROM perfil ORDER BY id", fetch_all=True)
            if not perfis:
                return permissoes
            
            # Obtém todos os módulos
            modulos = self.db.execute_query("SELECT id, nome, chave FROM modulos", fetch_all=True)
            if not modulos:
                return permissoes
                
            # Obtém todos os botões
            botoes = self.db.execute_query("SELECT id, modulo_id, nome, chave FROM botoes", fetch_all=True)
            
            # Mapeia os botões por módulo
            botoes_por_modulo = {}
            for botao in botoes:
                modulo_id = botao['modulo_id']
                if modulo_id not in botoes_por_modulo:
                    botoes_por_modulo[modulo_id] = []
                botoes_por_modulo[modulo_id].append(botao)
            
            # Obtém todas as permissões
            permissoes_db = self.db.execute_query("""
                SELECT pp.perfil_id, pp.modulo_id, pp.botao_id, pp.permitido
                FROM perfil_permissao pp
            """, fetch_all=True)
            
            # Cria um dicionário de permissões para consulta rápida
            permissoes_dict = {}
            for perm in permissoes_db:
                chave = f"{perm['perfil_id']}_{perm['modulo_id']}_{perm['botao_id']}"
                permissoes_dict[chave] = perm['permitido']
            
            # Inclui metadados de perfis no payload para o frontend mapear corretamente
            permissoes['perfis'] = perfis

            # Constrói a estrutura de permissões
            for modulo in modulos:
                modulo_chave = modulo['chave']
                permissoes['modulos'][modulo_chave] = {
                    'nome': modulo['nome'],
                    'botoes': {}
                }
                
                # Adiciona os botões do módulo
                for botao in botoes_por_modulo.get(modulo['id'], []):
                    botao_chave = botao['chave']
                    permissoes['modulos'][modulo_chave]['botoes'][botao_chave] = {
                        'nome': botao['nome']
                    }
                    
                    # Adiciona as permissões para cada perfil
                    for perfil in perfis:
                        chave = f"{perfil['id']}_{modulo['id']}_{botao['id']}"
                        valor = bool(permissoes_dict.get(chave, False))
                        # Disponibiliza por NOME do perfil (compatibilidade)
                        nome = perfil['nome']
                        permissoes['modulos'][modulo_chave]['botoes'][botao_chave][nome] = valor
                        # E também por ID do perfil (evita desalinhamento por nomes)
                        permissoes['modulos'][modulo_chave]['botoes'][botao_chave][str(perfil['id'])] = valor
                        # Aliases comuns de exibição para tolerar variações no front-end
                        aliases_map = {
                            'dev': ['Desenvolvedor', 'DEV', 'Dev'],
                            'medico': ['Médico', 'Medico', 'MÉDICO'],
                            'funcionario': ['Funcionário', 'Funcionario', 'FUNCIONÁRIO']
                        }
                        for alias in aliases_map.get(nome.lower(), []):
                            permissoes['modulos'][modulo_chave]['botoes'][botao_chave][alias] = valor
            
            return permissoes
            
        except Exception as e:
            print(f"[ERRO] Erro ao obter permissões: {str(e)}")
            return {'modulos': {}}
    
    def salvar_todas_permissoes(self, permissoes: Dict[str, Any]) -> bool:
        """
        Salva todas as permissões no banco de dados
        
        Args:
            permissoes: Dicionário com as permissões a serem salvas
            
        Returns:
            bool: True se as permissões foram salvas com sucesso, False caso contrário
        """
        try:
            # Obtém o mapeamento de chaves para IDs
            modulos = self._obter_modulos_por_chave()
            botoes = self._obter_botoes_por_modulo_e_chave()
            perfis = self._obter_perfis_por_nome()
            
            # ID do perfil de dev(fixo como 1)
            ADMIN_ID = 1
            
            # Prepara as permissões para inserção
            valores = []
            for modulo_chave, modulo_info in permissoes.get('modulos', {}).items():
                if modulo_chave not in modulos:
                    continue
                    
                modulo_id = modulos[modulo_chave]['id']
                
                for botao_chave, botao_info in modulo_info.get('botoes', {}).items():
                    if modulo_id not in botoes or botao_chave not in botoes[modulo_id]:
                        continue
                        
                    botao_id = botoes[modulo_id][botao_chave]['id']
                    
                    for perfil_nome, permitido in botao_info.items():
                        if perfil_nome in ['nome'] or perfil_nome not in perfis:
                            continue
                            
                        perfil_id = perfis[perfil_nome]['id']
                        # Perfil 1 (dev) é imutável: não grava alterações para ele
                        if perfil_id == ADMIN_ID:
                            continue
                        valores.append((perfil_id, modulo_id, botao_id, bool(permitido)))
            
            # Remove apenas as permissões que serão atualizadas
            if valores:
                # Cria uma lista de tuplas (perfil_id, modulo_id, botao_id) para o IN
                params = [(v[0], v[1], v[2]) for v in valores]
                placeholders = ','.join(['(%s,%s,%s)'] * len(params))
                flat_params = [item for sublist in params for item in sublist]
                
                # Remove as permissões que serão atualizadas
                delete_query = f"""
                    DELETE FROM perfil_permissao 
                    WHERE (perfil_id, modulo_id, botao_id) IN ({placeholders})
                """
                self.db.execute_query(delete_query, flat_params)
                
                # Insere as novas permissões
                query = """
                    INSERT INTO perfil_permissao (perfil_id, modulo_id, botao_id, permitido)
                    VALUES (%s, %s, %s, %s)
                """
                # Se houver um método execute_many, use-o, senão faça um loop
                if hasattr(self.db, 'execute_many'):
                    self.db.execute_many(query, valores)
                else:
                    for valor in valores:
                        self.db.execute_query(query, valor)
            
            return True
                
        except Exception as e:
            print(f"Erro ao salvar permissões: {str(e)}")
            return False
            
    def _obter_modulos_por_chave(self) -> Dict[str, Dict[str, Any]]:
        """Obtém todos os módulos indexados por chave"""
        modulos = self.db.execute_query("SELECT id, nome, chave FROM modulos", fetch_all=True)
        return {modulo['chave']: modulo for modulo in modulos}
    
    def _obter_botoes_por_modulo_e_chave(self) -> Dict[int, Dict[str, Dict[str, Any]]]:
        """Obtém todos os botões indexados por módulo_id e chave"""
        botoes = self.db.execute_query("SELECT id, modulo_id, nome, chave FROM botoes", fetch_all=True)
        resultado = {}
        for botao in botoes:
            modulo_id = botao['modulo_id']
            if modulo_id not in resultado:
                resultado[modulo_id] = {}
            resultado[modulo_id][botao['chave']] = botao
        return resultado
    
    def _obter_perfis_por_nome(self) -> Dict[str, Dict[str, Any]]:
        """Obtém todos os perfis indexados por nome"""
        perfis = self.db.execute_query("SELECT id, nome FROM perfil", fetch_all=True)
        return {perfil['nome']: perfil for perfil in perfis}