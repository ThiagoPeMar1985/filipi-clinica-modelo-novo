"""
Tela de login do PDV Bar & Restaurante
"""
import tkinter as tk
from tkinter import messagebox
import mysql.connector
import json
import os
import sys
from pathlib import Path
import platform
import logging

# Importa as configurações do banco de dados (caminho absoluto do pacote src)
from src.db.config import get_db_config

# Caminho para o arquivo de configuração
CONFIG_FILE = "login_config.json"


class Usuario:
    """Classe que representa um usuário"""
    def __init__(self, id, nome, login, senha, nivel):
        self.id = id
        self.nome = nome
        self.login = login
        self.senha = senha
        self.nivel = nivel

class TelaLogin:
    """Tela de login do sistema"""
    
    def __init__(self, root, on_login_sucesso):
        self.root = root
        self.on_login_sucesso = on_login_sucesso
        # Configura logger para diagnosticar comportamento no executável
        try:
            logs_dir = Path.home() / '.clinicas'
            logs_dir.mkdir(parents=True, exist_ok=True)
            self._log_path = logs_dir / 'clinica_app.log'
            logging.basicConfig(
                filename=self._log_path,
                level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s'
            )
            logging.info('=== App iniciado: TelaLogin.__init__ ===')
        except Exception:
            self._log_path = None
        
        # Configuração do banco de dados a partir do config.py
        self.db_config = get_db_config()
        # Remove chaves que não são necessárias para a conexão
        for key in ['raise_on_warnings', 'charset', 'collation', 'connect_timeout']:
            self.db_config.pop(key, None)
        # Força parâmetros que melhoram compatibilidade no executável
        self.db_config['use_pure'] = True
        self.db_config['autocommit'] = True
        self.db_config.setdefault('connection_timeout', 5)
        # Garante tipo correto da porta
        if 'port' in self.db_config:
            try:
                self.db_config['port'] = int(self.db_config['port'])
            except Exception:
                self.db_config.pop('port', None)
        # Log da configuração (sem senha)
        try:
            cfg_log = {k: ('***' if k == 'password' and v is not None else v) for k, v in self.db_config.items()}
            logging.info(f'DB config aplicada: {cfg_log}')
        except Exception:
            pass
        
        # Configura a janela
        self.root.title("Login -Clinicas")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centralizar a janela
        window_width = 400
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configuração de estilo
        self.root.configure(bg="#f0f0f0")
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, text="Clinicas", 
                              font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)
        
        # Frame de login
        login_frame = tk.Frame(main_frame, bg="#f0f0f0")
        login_frame.pack(pady=10)
        
        # Labels e entradas
        tk.Label(login_frame, text="Login:", bg="#f0f0f0", 
                font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_usuario = tk.Entry(login_frame, width=25, font=("Arial", 12))
        self.entry_usuario.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(login_frame, text="Senha:", bg="#f0f0f0", 
                font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_senha = tk.Entry(login_frame, width=25, font=("Arial", 12), show="*")
        self.entry_senha.grid(row=1, column=1, pady=5, padx=5)
        
        # Checkbutton para lembrar usuário
        self.lembrar_usuario = tk.BooleanVar(value=False)
        lembrar_check = tk.Checkbutton(
            login_frame, 
            text="Lembrar usuário", 
            variable=self.lembrar_usuario,
            bg="#f0f0f0",
            font=("Arial", 10)
        )
        lembrar_check.grid(row=2, column=1, sticky="w", pady=5)
        
        # Botão de login
        login_button = tk.Button(main_frame, text="Entrar", command=self._fazer_login, 
                               bg="#3498db", fg="white", font=("Arial", 12, "bold"),
                               width=15, height=1)
        login_button.pack(pady=15)
        
        # Carregar credenciais salvas
        self.carregar_credenciais()
        
        # Focar no campo de senha
        self.entry_senha.focus()
        
        # Permitir login com Enter
        self.root.bind('<Return>', lambda e: self._fazer_login())
    
    def carregar_credenciais(self):
        """Carrega as credenciais salvas do arquivo de configuração"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    if 'login' in config:
                        self.entry_usuario.insert(0, config['login'])
                        self.lembrar_usuario.set(True)
        except Exception as e:
            print(f"Erro ao carregar credenciais: {e}")
    
    def salvar_credenciais(self, login):
        """Salva as credenciais no arquivo de configuração"""
        try:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
            
            config['login'] = login
            
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Erro ao salvar credenciais: {e}")
    
    def remover_credenciais(self):
        """Remove as credenciais salvas"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                
                if 'login' in config:
                    del config['login']
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f)
        except Exception as e:
            print(f"Erro ao remover credenciais: {e}")
    
    def _verificar_credenciais(self, usuario, senha):
        """Verifica se o usuário e senha estão corretos"""
        try:
            logging.info(f'Tentando conexão MySQL para login de usuario={usuario!r}')
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Diagnóstico: descobrir o schema atual e existência do login
            try:
                cursor.execute("SELECT DATABASE() AS db")
                row_db = cursor.fetchone() or {}
                current_db = row_db.get('db')
            except Exception:
                current_db = None
            
            try:
                cursor.execute("SELECT COUNT(*) AS c FROM usuarios WHERE login = %s", (usuario,))
                row_cnt = cursor.fetchone() or {}
                login_count = row_cnt.get('c')
            except Exception:
                login_count = None
            
            # Autenticação
            query = "SELECT * FROM usuarios WHERE login = %s AND senha = %s"
            cursor.execute(query, (usuario, senha))
            resultado = cursor.fetchone()
            
            if resultado:
                usuario = Usuario(resultado.get('id'), resultado.get('nome'), resultado.get('login'), resultado.get('senha'), resultado.get('nivel'))
                # Fecha a conexão após obter os dados
                cursor.close()
                conn.close()
                logging.info(f'Login bem-sucedido para usuario={usuario.login!r} (id={usuario.id})')
                return usuario
            else:
                logging.warning(f'Falha de login para usuario={usuario!r}: credenciais inválidas')
                # Mostra diagnóstico útil para identificar divergência de banco/schema ou credenciais
                try:
                    messagebox.showerror(
                        "Erro",
                        f"Usuário ou senha inválidos!\n\n"
                        f"Banco (DATABASE): {current_db}\n"
                        f"Login informado: {usuario}\n"
                        f"Existe login neste banco? {'sim' if (login_count and int(login_count) > 0) else 'não'}"
                    )
                except Exception:
                    pass
                cursor.close()
                conn.close()
                return None
        
        except Exception as e:
            import traceback
            erro = traceback.format_exc()
            try:
                logging.exception(f'Erro ao conectar/autenticar no banco: {e}')
            except Exception:
                pass
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {str(e)}")
            return None
    
    def _registrar_chat_sessao(self, usuario_obj, dispositivo: str | None = None):
        """Registra (insere) uma sessão de chat para o usuário logado.
        Usa o nome do host como dispositivo quando não informado.
        """
        try:
            dispositivo_detectado = (
                dispositivo
                or platform.node()
                or os.getenv('COMPUTERNAME')
                or 'desconhecido'
            )
            conn = mysql.connector.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO chat_sessoes (usuario_id, usuario_nome, dispositivo, ultimo_heartbeat)
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    usuario_nome = VALUES(usuario_nome),
                    dispositivo = VALUES(dispositivo),
                    ultimo_heartbeat = VALUES(ultimo_heartbeat)
                """,
                (usuario_obj.id, usuario_obj.nome, dispositivo_detectado),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            # Evita quebrar o fluxo de login por falha não-crítica de auditoria
            try:
                print(f"[chat_sessoes] Falha ao registrar sessão: {e}")
            except Exception:
                pass
    
    def _fazer_login(self, event=None):
        """Tenta fazer o login"""
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        
        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return
        
        usuario_encontrado = self._verificar_credenciais(usuario, senha)
        
        if usuario_encontrado:
            # Salvar ou remover credenciais conforme a opção selecionada
            if self.lembrar_usuario.get():
                self.salvar_credenciais(usuario)
            else:
                self.remover_credenciais()
            try:
                # Registra a sessão do chat para o usuário logado
                self._registrar_chat_sessao(usuario_encontrado)
                # Chama a função de callback para continuar para o sistema
                self.on_login_sucesso(usuario_encontrado, self.root)
            except Exception as e:
                try:
                    import traceback
                    logging.exception("Falha ao abrir a tela principal após login")
                    detalhe = traceback.format_exc()
                    messagebox.showerror(
                        "Erro ao abrir o sistema",
                        f"Ocorreu um erro ao abrir a tela principal.\n\nDetalhes:\n{e}\n\nTraceback:\n{detalhe}"
                    )
                except Exception:
                    pass
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            self.entry_senha.delete(0, 'end')
            self.entry_senha.focus()