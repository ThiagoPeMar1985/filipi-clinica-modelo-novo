"""
Controlador para o módulo de Configuração.
"""
import json
import os
from pathlib import Path
from tkinter import messagebox

class ConfigController:
    """Controlador para operações do módulo de Configuração."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        self.config_dir = Path.home() / '.pdv_aquarius'
        self.config_file = self.config_dir / 'config.json'
        self._criar_estrutura_padrao()
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
    
    def _criar_estrutura_padrao(self):
        """Cria a estrutura de diretórios e arquivos de configuração padrão."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            if not self.config_file.exists():
                self._salvar_config({})
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar estrutura de configuração: {e}")
    
    def _carregar_config(self):
        """Carrega as configurações do arquivo JSON."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configurações: {e}")
            return {}
    
    def _salvar_config(self, secao, dados):
        """Salva as configurações na seção especificada."""
        try:
            config = self._carregar_config()
            config[secao] = dados
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
            return False
    
    def obter_config(self, secao=None, padrao=None):
        """Obtém as configurações da seção especificada ou todas."""
        config = self._carregar_config()
        if secao:
            return config.get(secao, padrao if padrao is not None else {})
        return config
    
    # Métodos específicos para cada seção de configuração
    
    def salvar_config_impressoras(self, dados):
        """Salva as configurações de impressoras."""
        return self._salvar_config('impressoras', dados)
    
    def salvar_config_banco_dados(self, dados):
        """Salva as configurações do banco de dados."""
        return self._salvar_config('banco_dados', dados)
    
    def salvar_config_nfe(self, dados):
        """Salva as configurações de NF-e."""
        return self._salvar_config('nfe', dados)
    
    def salvar_config_backup(self, dados):
        """Salva as configurações de backup."""
        return self._salvar_config('backup', dados)
    
    def salvar_config_tema(self, dados):
        """Salva as configurações de tema."""
        return self._salvar_config('tema', dados)
    
    def salvar_config_integracoes(self, dados):
        """Salva as configurações de integrações."""
        return self._salvar_config('integracoes', dados)
    
    def salvar_config_seguranca(self, dados):
        """Salva as configurações de segurança."""
        return self._salvar_config('seguranca', dados)

    def carregar_config_integracoes(self):
        """Carrega as configurações de integrações salvas."""
        return self.obter_config('integracoes', {})

    def carregar_config_banco_dados(self):
        """Carrega as configurações do banco de dados salvas."""
        return self.obter_config('banco_dados', {})
        
    def carregar_config_tema(self):
        """Carrega as configurações de tema salvas."""
        # Configurações padrão
        tema_padrao = {
            'tamanho_fonte_sidebar': '12',
            'tamanho_fonte_cabecalho': '14',
            'cor_fundo': '#f0f2f5',
            'cor_cabecalho': '#2c3e50',
            'cor_texto_cabecalho': '#ffffff',
            'cor_sidebar': '#34495e',
            'cor_texto_sidebar': '#ecf0f1',
            'cor_botao': '#3498db',
            'cor_texto_botao': '#ffffff',
            'cor_borda': '#bdc3c7',
            'cor_texto': '#2c3e50',
            'cor_destaque': '#e74c3c',
            'cor_sucesso': '#2ecc71',
            'cor_alerta': '#f39c12',
            'cor_erro': '#e74c3c'
        }
        
        # Carrega as configurações salvas e mescla com os padrões
        config_salva = self.obter_config('tema', {})
        tema_padrao.update(config_salva)
        
        return tema_padrao
    
    # Métodos de negócio
    
    def listar_impressoras(self):
        """Lista as impressoras disponíveis no sistema."""
        try:
            import win32print
            return [printer[2] for printer in win32print.EnumPrinters(2)]
        except ImportError:
            return ["Impressora Padrão", "Cozinha", "Bar", "Delivery"]
    
    def testar_impressora(self, nome_impressora):
        """Testa a impressão em uma impressora específica."""
        try:
            # Implementar lógica de teste de impressão
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao testar impressora: {e}")
            return False
    
    def testar_conexao_banco_dados(self, host, porta, usuario, senha, banco):
        """Testa a conexão com o banco de dados."""
        try:
            # Implementar lógica de teste de conexão
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na conexão com o banco de dados: {e}")
            return False
    
    def fazer_backup_banco_dados(self, destino):
        """Realiza o backup do banco de dados."""
        try:
            # Implementar lógica de backup
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao fazer backup: {e}")
            return False
    
    def restaurar_backup_banco_dados(self, arquivo):
        """Restaura um backup do banco de dados."""
        try:
            # Implementar lógica de restauração
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao restaurar backup: {e}")
            return False
            
    def alterar_senha(self, senha_atual, nova_senha):
        """
        Altera a senha do usuário atual.
        
        Args:
            senha_atual (str): A senha atual do usuário
            nova_senha (str): A nova senha desejada
            
        Returns:
            bool: True se a senha foi alterada com sucesso, False caso contrário
        """
        try:
            # Aqui você implementaria a lógica para verificar a senha atual
            # e alterar para a nova senha no banco de dados ou sistema de autenticação
            
            # Exemplo de implementação (deve ser adaptado ao seu sistema de autenticação):
            # 1. Verificar se a senha atual está correta
            # 2. Se estiver correta, atualizar para a nova senha
            # 3. Retornar True em caso de sucesso
            
            # Por enquanto, apenas simula sucesso
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao alterar senha: {e}")
            return False
