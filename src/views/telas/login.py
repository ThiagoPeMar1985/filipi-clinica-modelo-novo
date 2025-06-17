"""
Tela de login do PDV Bar & Restaurante
"""
import tkinter as tk
from tkinter import messagebox
import mysql.connector
import json
import os

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
        
        # Configuração do banco de dados
        self.db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': 'Beer1234@',
            'database': 'pdv_bar'
        }
        
        # Configura a janela
        self.root.title("Login - PDV")
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
        title_label = tk.Label(main_frame, text="PDV BAR & RESTAURANTE", 
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
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM usuarios WHERE login = %s AND senha = %s"
            
            cursor.execute(query, (usuario, senha))
            
            resultado = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if resultado:
                usuario = Usuario(resultado.get('id'), resultado.get('nome'), resultado.get('login'), resultado.get('senha'), resultado.get('nivel'))
                # Adiciona a conexão ao objeto de usuário
                usuario.db_connection = conn
                return usuario
            else:
                cursor.close()
                conn.close()
                return None
            
        except Exception as e:
            import traceback
            erro = traceback.format_exc()
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {str(e)}")
            return None
    
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
                
            # Chama a função de callback para continuar para o sistema
            self.on_login_sucesso(usuario_encontrado, self.root)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            self.entry_senha.delete(0, 'end')
            self.entry_senha.focus()