"""
Controlador para o módulo de Configuração.
"""
import json
import os
import re
import sys
from pathlib import Path
from tkinter import messagebox

# Adiciona o diretório raiz do projeto ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

class ConfigController:
    """Controlador para operações do módulo de Configuração."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        self.config_dir = Path.home() / '.pdv_aquarius'
        self.config_file = self.config_dir / 'config.json'
        self.db_config_file = Path(__file__).parent.parent / 'db' / 'config.py'
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
            error_msg = f"Erro ao salvar configurações: {e}"
            messagebox.showerror("Erro", error_msg)
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
        """Salva as configurações do banco de dados no arquivo config.py."""
        try:
            # Atualiza o arquivo config.py com as novas configurações
            with open(self.db_config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Atualiza as configurações do DB_CONFIG
            db_config_str = f"""DB_CONFIG = {{
    'host': '{dados.get('host', '127.0.0.1')}',
    'user': '{dados.get('usuario', 'root')}',
    'password': '{dados.get('senha', '')}',
    'database': '{dados.get('nome_bd', 'pdv_bar')}',
    'port': {dados.get('porta', 3306)},
    'raise_on_warnings': True,
    'use_pure': True,
    'autocommit': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'connection_timeout': 30
}}"""
            
            # Atualiza o conteúdo do arquivo
            content = re.sub(
                r'DB_CONFIG\s*=\s*\{.*?\}(?=\s*(?:#|$|\n\w))',
                db_config_str,
                content,
                flags=re.DOTALL
            )
            
            # Atualiza as configurações de desenvolvimento
            dev_config_str = f"""DEV_CONFIG = {{
    **DB_CONFIG,
    'host': '{dados.get('host', '127.0.0.1')}',
    'connect_timeout': 30
}}"""
            
            content = re.sub(
                r'DEV_CONFIG\s*=\s*\{.*?\}(?=\s*(?:#|$|\n\w))',
                dev_config_str,
                content,
                flags=re.DOTALL
            )
            
            # Salva as alterações no arquivo
            with open(self.db_config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Atualiza também o arquivo de configuração JSON para manter a compatibilidade
            self._salvar_config('banco_dados', dados)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações do banco de dados: {e}")
            return False
    
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
        """Carrega as configurações do banco de dados do arquivo config.py."""
        try:
            # Tenta carregar do arquivo config.py
            with open(self.db_config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrai as configurações usando expressões regulares
            db_config_match = re.search(
                r"DB_CONFIG\s*=\s*\{\s*[\s\S]*?\}",
                content
            )
            
            if db_config_match:
                db_config_str = db_config_match.group(0)
                # Converte o dicionário em string para um dicionário Python
                db_config = {}
                for key in ['host', 'user', 'password', 'database', 'port']:
                    match = re.search(f"'{key}'\s*:\s*'([^']*)'", db_config_str)
                    if match:
                        db_config[key] = match.group(1)
                    else:
                        match = re.search(f"'{key}'\s*:\s*(\\d+)", db_config_str)
                        if match:
                            db_config[key] = int(match.group(1))
                
                # Formata no formato esperado pela interface
                return {
                    'host': db_config.get('host', '127.0.0.1'),
                    'porta': str(db_config.get('port', 3306)),
                    'usuario': db_config.get('user', 'root'),
                    'senha': db_config.get('password', ''),
                    'nome_bd': db_config.get('database', 'pdv_bar')
                }
        except Exception as e:
            print(f"Erro ao carregar configurações do banco de dados: {e}")
        
        # Se não conseguir carregar do config.py, tenta do arquivo JSON
        return self.obter_config('banco_dados', {
            'host': '127.0.0.1',
            'porta': '3306',
            'usuario': 'root',
            'senha': '',
            'nome_bd': 'pdv_bar'
        })
        
    def carregar_config_impressoras(self):
        """
        Carrega as configurações de impressoras salvas.
        
        Returns:
            dict: Dicionário com as configurações de impressoras ou dicionário vazio se não houver configurações
        """
        try:
            return self.obter_config('impressoras', {})
        except Exception:
            return {}
        
    def carregar_config_backup(self):
        """Carrega as configurações de backup salvas."""
        return self.obter_config('backup', {})
        
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
        """Lista todas as impressoras disponíveis no sistema, incluindo USB e rede."""
        try:
            import win32print
            import win32serviceutil
            import win32service
            import servicemanager
            import socket
            
            # Função para verificar se um serviço está em execução
            def is_service_running(service_name):
                try:
                    status = win32serviceutil.QueryServiceStatus(service_name)
                    return status[1] == win32service.SERVICE_RUNNING
                except Exception:
                    return False
            
            # Verifica se o serviço de Spooler está em execução
            if not is_service_running('Spooler'):
                mensagem = (
                    "O serviço de Spooler de Impressão não está em execução.\n\n"
                    "Para ativar o serviço de Spooler de Impressão:\n"
                    "1. Pressione Win + R, digite 'services.msc' e pressione Enter\n"
                    "2. Localize o serviço 'Spooler de Impressão'\n"
                    "3. Clique com o botão direito e selecione 'Iniciar'\n"
                    "4. Se o serviço não iniciar, reinicie o computador"
                )
                print("Erro:", mensagem)
                return [mensagem]
                
            # Lista para armazenar todas as impressoras
            todas_impressoras = []
            
            # Tenta obter a impressora padrão primeiro
            try:
                impressora_padrao = win32print.GetDefaultPrinter()
                if impressora_padrao:
                    todas_impressoras.append(impressora_padrao)
            except Exception as e:
                print(f"Aviso: Não foi possível obter a impressora padrão: {e}")
            
            # Tenta listar impressoras com diferentes níveis de permissão
            try:
                # Tenta primeiro apenas com impressoras locais (menos provável de causar erros)
                impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
                for printer in impressoras:
                    nome_impressora = printer[2]
                    if nome_impressora and nome_impressora not in todas_impressoras:
                        todas_impressoras.append(nome_impressora)
            except Exception as e:
                print(f"Aviso: Não foi possível listar impressoras locais: {e}")
            
            # Se não encontrou nenhuma impressora, tenta métodos alternativos
            if not todas_impressoras:
                print("Tentando métodos alternativos para listar impressoras...")
                
                # Tenta obter a impressora padrão novamente
                try:
                    impressora_padrao = win32print.GetDefaultPrinter()
                    if impressora_padrao and impressora_padrao not in todas_impressoras:
                        todas_impressoras.append(impressora_padrao)
                except:
                    pass
                
                # Tenta listar impressoras de conexão
                try:
                    impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS)
                    for printer in impressoras:
                        nome_impressora = printer[2]
                        if nome_impressora and nome_impressora not in todas_impressoras:
                            todas_impressoras.append(nome_impressora)
                except:
                    pass
            
            # Se ainda não encontrou nenhuma impressora, tenta listar impressoras de rede
            if not todas_impressoras:
                try:
                    impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_NETWORK)
                    for printer in impressoras:
                        nome_impressora = printer[2]
                        if nome_impressora and nome_impressora not in todas_impressoras:
                            todas_impressoras.append(nome_impressora)
                except Exception as e:
                    print(f"Aviso: Não foi possível listar impressoras de rede: {e}")
            
            # Se não encontrou nenhuma impressora, adiciona a impressora virtual PDF como padrão
            if not todas_impressoras:
                print("Nenhuma impressora física encontrada. Usando impressora virtual 'Microsoft Print to PDF' como padrão.")
                # Adiciona a impressora virtual PDF como padrão
                todas_impressoras.append("Microsoft Print to PDF")
                
                # Tenta definir como impressora padrão
                try:
                    import win32print
                    win32print.SetDefaultPrinter("Microsoft Print to PDF")
                except Exception as e:
                    print(f"Não foi possível definir 'Microsoft Print to PDF' como impressora padrão: {e}")
                
            return sorted(todas_impressoras)
            
        except ImportError as e:
            mensagem_erro = (
                "Módulo win32print não encontrado.\n\n"
                "Para usar recursos de impressão, instale o pacote pywin32 com o comando:\n"
                "pip install pywin32\n\n"
                "Certifique-se de executar o comando como administrador."
            )
            print("Erro:", mensagem_erro)
            return ["Erro: Módulo win32print não instalado"]
            
        except Exception as e:
            mensagem_erro = (
                f"Falha ao acessar as impressoras: {str(e)}\n\n"
                "Soluções possíveis:\n"
                "1. Verifique se o serviço 'Spooler de Impressão' está em execução\n"
                "2. Verifique se o serviço 'Chamada de Procedimento Remoto (RPC)' está em execução\n"
                "3. Tente reiniciar o computador\n"
                "4. Verifique se há impressoras instaladas no Painel de Controle"
            )
            print("Erro:", mensagem_erro)
            return [f"Erro ao acessar impressoras: {str(e)}"]
    
    def testar_impressora(self, nome_impressora, tamanho_fonte=12):
        """
        Testa a impressão em uma impressora específica.
        
        Args:
            nome_impressora (str): Nome da impressora a ser testada
            tamanho_fonte (int, optional): Tamanho da fonte para o teste. Padrão é 12.
            
        Returns:
            bool: True se o teste foi bem-sucedido, False caso contrário
        """
        if not nome_impressora or nome_impressora == "Nenhuma impressora disponível":
            messagebox.showwarning("Aviso", "Nenhuma impressora selecionada para teste.")
            return False
            
        try:
            import win32print
            import win32ui
            import win32con
            import win32gui
            import time
            
            # Converte o tamanho da fonte para inteiro
            try:
                tamanho_fonte = int(tamanho_fonte)
                # Garante um tamanho mínimo e máximo razoável
                tamanho_fonte = max(8, min(72, tamanho_fonte))
            except (ValueError, TypeError):
                tamanho_fonte = 12  # Valor padrão se a conversão falhar
            
            # Obtém o handle da impressora
            hprinter = win32print.OpenPrinter(nome_impressora)
            
            try:
                # Obtém as informações da impressora
                printer_info = win32print.GetPrinter(hprinter, 2)
                
                # Verifica se a impressora está pronta
                status = printer_info['Status']
                
                # Verifica se há erros na impressora
                if status != 0:
                    status_str = []
                    if status & win32print.PRINTER_STATUS_PAUSED:
                        status_str.append("PAUSADA")
                    if status & win32print.PRINTER_STATUS_ERROR:
                        status_str.append("ERRO")
                    if status & win32print.PRINTER_STATUS_PAPER_JAM:
                        status_str.append("PAPEL ENCRAVADO")
                    if status & win32print.PRINTER_STATUS_OUT_OF_PAPER:
                        status_str.append("SEM PAPEL")
                    if status & win32print.PRINTER_STATUS_OFFLINE:
                        status_str.append("OFFLINE")
                    
                    messagebox.showerror(
                        "Erro na Impressora",
                        f"A impressora não está pronta. Status: {', '.join(status_str)}"
                    )
                    return False
                
                # Cria um documento de teste
                try:
                    # Tenta usar win32ui para impressão direta
                    hdc = win32ui.CreateDC()
                    hdc.CreatePrinterDC(nome_impressora)
                    hdc.StartDoc('Teste de Impressão')
                    hdc.StartPage()
                    
                    # Configurações de fonte com o tamanho configurado
                    altura_fonte = -int(tamanho_fonte * 20)  # Converte para unidades lógicas (negativo para altura em pontos)
                    font = win32ui.CreateFont({
                        'name': 'Arial',
                        'height': altura_fonte,
                        'weight': 400,  # Peso normal
                    })
                    hdc.SelectObject(font)
                    
                    # Texto de teste
                    texto = [
                        "TESTE DE IMPRESSÃO",
                        "==================",
                        f"Impressora: {nome_impressora}",
                        f"Tamanho da Fonte: {tamanho_fonte}pt",
                        f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}",
                        "",
                        "Este é um teste de impressão.",
                        "Se você está lendo esta mensagem,",
                        "sua impressora está configurada",
                        "corretamente.",
                        "",
                        "Sistema PDV Aquarius"
                    ]
                    
                    # Imprime cada linha
                    y = 1000  # Posição Y inicial
                    espacamento = int(tamanho_fonte * 25)  # Ajusta o espaçamento com base no tamanho da fonte
                    
                    for linha in texto:
                        hdc.TextOut(500, y, linha)
                        y += espacamento  # Espaçamento entre linhas
                    
                    # Finaliza a impressão
                    hdc.EndPage()
                    hdc.EndDoc()
                    
                    return True
                    
                except Exception as e:
                    # Se falhar, tenta um método alternativo
                    try:
                        # Usa o método de impressão de texto simples
                        hprinter = win32print.OpenPrinter(nome_impressora)
                        try:
                            # Abre um trabalho de impressão
                            job = win32print.StartDocPrinter(hprinter, 1, ("Teste de Impressão", None, "RAW"))
                            win32print.StartPagePrinter(hprinter)
                            
                            # Texto de teste
                            texto = [
                                "TESTE DE IMPRESSÃO",
                                "==================",
                                f"Impressora: {nome_impressora}",
                                f"Tamanho da Fonte: {tamanho_fonte}pt",
                                f"Data/Hora: {time.strftime('%d/%m/%Y %H:%M:%S')}",
                                "",
                                "Este é um teste de impressão.",
                                "Se você está lendo esta mensagem,",
                                "sua impressora está configurada",
                                "corretamente.",
                                "",
                                "Sistema PDV Aquarius"
                            ]
                            
                            # Envia o texto para impressão
                            for linha in texto:
                                linha_bytes = (linha + "\r\n").encode('utf-8')
                                win32print.WritePrinter(hprinter, linha_bytes)
                            
                            # Finaliza a impressão
                            win32print.EndPagePrinter(hprinter)
                            win32print.EndDocPrinter(hprinter)
                            
                            return True
                            
                        finally:
                            win32print.ClosePrinter(hprinter)
                            
                    except Exception as inner_e:
                        messagebox.showerror(
                            "Erro ao Imprimir",
                            f"Não foi possível enviar para a impressora. Erro: {str(inner_e)}"
                        )
                        return False
                        
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Falha ao testar impressora {nome_impressora}. Erro: {str(e)}"
            )
            return False
    
    def testar_conexao_banco_dados(self, host, porta, usuario, senha, banco):
        """Testa a conexão com o banco de dados.
        
        Args:
            host (str): Endereço do servidor do banco de dados
            porta (str): Porta do servidor do banco de dados
            usuario (str): Nome de usuário para autenticação
            senha (str): Senha para autenticação
            banco (str): Nome do banco de dados
            
        Returns:
            bool: True se a conexão for bem-sucedida, False caso contrário
        """
        import mysql.connector
        from mysql.connector import Error
        import socket
        
        # Configuração da conexão com timeout reduzido
        config = {
            'host': host,
            'port': int(porta) if porta else 3306,
            'user': usuario,
            'password': senha,
            'database': banco,
            'connection_timeout': 3,  # Reduzido para 3 segundos
            'connect_timeout': 3,     # Timeout específico para conexão
            'raise_on_warnings': True,
            'autocommit': True,       # Garante que as consultas são confirmadas automaticamente
            'buffered': True          # Evita o erro "unread result"
        }
        
        conn = None
        cursor = None
        try:
            # Tenta resolver o host primeiro com timeout
            socket.setdefaulttimeout(3)
            try:
                socket.gethostbyname(host)
            except (socket.gaierror, socket.timeout):
                raise Exception(f"Não foi possível resolver o endereço do servidor: {host}")
            
            # Tenta conectar ao banco de dados com timeout
            try:
                conn = mysql.connector.connect(**config)
                if conn.is_connected():
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    # Consome todos os resultados
                    cursor.fetchall()
                    cursor.close()
                    cursor = None
                    return True
                return False
                
            except mysql.connector.Error as e:
                error_msg = str(e).lower()
                if "access denied" in error_msg:
                    raise Exception("Acesso negado. Verifique o usuário e senha.")
                elif "unknown database" in error_msg:
                    raise Exception(f"Banco de dados '{banco}' não encontrado.")
                elif "can't connect to mysql server" in error_msg:
                    raise Exception(f"Não foi possível conectar ao servidor {host}:{porta}")
                else:
                    raise Exception(f"Falha na conexão com o banco de dados: {e}")
            
        except Exception as e:
            raise Exception(f"Erro ao conectar ao banco de dados: {e}")
            
        finally:
            # Fecha o cursor se ainda estiver aberto
            if cursor is not None:
                try:
                    cursor.close()
                except:
                    pass
            
            # Fecha a conexão se ainda estiver aberta
            if conn is not None and conn.is_connected():
                try:
                    conn.close()
                except:
                    pass
    
    def fazer_backup_banco_dados(self, pasta_destino):
        """
        Executa o backup do banco de dados MySQL usando mysqldump.
        
        Args:
            pasta_destino (str): Caminho da pasta onde o backup será salvo
            
        Returns:
            bool: True se o backup foi bem-sucedido, False caso contrário
        """
        import subprocess
        import os
        from datetime import datetime
        from src.db.config import DB_CONFIG
        
        try:
            # Verifica se o diretório de destino existe, se não, cria
            os.makedirs(pasta_destino, exist_ok=True)
            
            # Define o nome do arquivo de backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_backup = os.path.join(pasta_destino, f"backup_pdv_{timestamp}.sql")
            
            # Verifica se o mysqldump está disponível
            mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
            if not os.path.exists(mysqldump_path):
                messagebox.showerror("Erro", "mysqldump não encontrado. Verifique a instalação do MySQL.")
                return False
            
            # Configurações do banco de dados
            db_config = DB_CONFIG
            
            # Monta o comando mysqldump
            comando = [
                f'"{mysqldump_path}"',
                f'--host={db_config["host"]}',
                f'--port={db_config["port"]}',
                f'--user={db_config["user"]}',
                f'--password={db_config["password"]}',
                '--routines',
                '--triggers',
                '--single-transaction',
                f'--result-file="{arquivo_backup}"',
                db_config['database']
            ]
            
            # Converte a lista de comando para string para execução
            comando_str = ' '.join(comando)
            
            # Executa o comando
            processo = subprocess.Popen(
                comando_str,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            
            # Aguarda o término do processo
            stdout, stderr = processo.communicate()
            
            # Verifica se o arquivo foi criado e tem conteúdo
            if os.path.exists(arquivo_backup) and os.path.getsize(arquivo_backup) > 0:
                return True
            else:
                messagebox.showerror("Erro no Backup", "O arquivo de backup não foi criado ou está vazio.")
                return False
                
        except Exception as e:
            messagebox.showerror("Erro no Backup", f"Ocorreu um erro durante o backup:\n{str(e)}")
            return False
        except Exception as e:
            import traceback
            erro_detalhado = f"Erro inesperado: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(erro_detalhado)
            messagebox.showerror("Erro no Backup", f"Ocorreu um erro durante o backup:\n{str(e)}")
            return False
    
    def restaurar_backup_banco_dados(self, arquivo_backup):
        """
        Restaura um backup do banco de dados.
        
        Args:
            arquivo_backup (str): Caminho completo para o arquivo de backup
            
        Returns:
            bool: True se a restauração foi bem-sucedida, False caso contrário
        """
        import subprocess
        import os
        from src.db.config import DB_CONFIG
        
        try:
            # Verifica se o arquivo de backup existe
            if not os.path.exists(arquivo_backup):
                messagebox.showerror("Erro", f"Arquivo de backup não encontrado: {arquivo_backup}")
                return False
            
            # Caminho para o executável do MySQL
            mysql_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
            if not os.path.exists(mysql_path):
                messagebox.showerror("Erro", "MySQL não encontrado. Verifique a instalação do MySQL.")
                return False
                
            # Configurações do banco de dados
            db_config = DB_CONFIG
            
            # Monta o comando como string para evitar problemas com espaços no caminho
            comando = (
                f'"{mysql_path}" '  # Caminho para o mysql.exe entre aspas
                f'--host={db_config["host"]} '
                f'--port={db_config["port"]} '
                f'--user={db_config["user"]} '
                f'--password={db_config["password"]} '
                f'{db_config["database"]} < "{arquivo_backup}"'
            )
            
            # Executa o comando no shell do Windows
            processo = subprocess.Popen(
                comando,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguarda o término do processo
            stdout, stderr = processo.communicate()
            
            if processo.returncode != 0:
                erro_msg = f"Erro ao restaurar o backup. Código: {processo.returncode}"
                if stderr:
                    erro_msg += f"\nErro: {stderr}"
                messagebox.showerror("Erro", erro_msg)
                return False
                    
            # Retorna True sem mostrar mensagem (a mensagem será exibida na UI)
            return True
            
        except Exception as e:
            import traceback
            print(f"Erro ao restaurar backup: {str(e)}\n{traceback.format_exc()}")
            messagebox.showerror("Erro", f"Erro ao restaurar o backup:\n{str(e)}")
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
