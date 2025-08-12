"""
Tela de configuração de conexão com o banco de dados.

Esta tela é exibida quando o sistema não consegue se conectar ao banco de dados
durante a inicialização, permitindo ao usuário configurar os parâmetros de conexão.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os
import sys

# Adiciona o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.db.config import get_db_config, DB_CONFIG, is_server_machine

class TelaConexaoDB:
    """Classe para a tela de configuração de conexão com o banco de dados."""
    
    def __init__(self, parent, callback_sucesso=None):
        """
        Inicializa a tela de conexão com o banco de dados.
        
        Args:
            parent: Widget pai (janela principal)
            callback_sucesso: Função a ser chamada quando a conexão for bem-sucedida
        """
        self.parent = parent
        self.callback_sucesso = callback_sucesso
        self.frame = tk.Frame(parent, bg='#f0f2f5')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Carrega as configurações atuais
        self.config = get_db_config()
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface da tela de conexão."""
        # Frame do título
        title_frame = tk.Frame(self.frame, bg='#f0f2f5')
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            title_frame, 
            text="CONFIGURAÇÃO DO BANCO DE DADOS", 
            font=('Arial', 16, 'bold'),
            bg='#f0f2f5',
            fg='#000000',
            anchor='center'
        ).pack(fill='x')
        
        # Mensagem de erro
        msg_frame = tk.Frame(self.frame, bg='#f0f2f5')
        msg_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            msg_frame,
            text="Não foi possível conectar ao banco de dados. Por favor, verifique as configurações abaixo:",
            font=('Arial', 11),
            bg='#f0f2f5',
            fg='#000000',
            wraplength=600,
            justify='center',
            anchor='center'
        ).pack(fill='x')
        
        # Frame do formulário com padding maior nas laterais para centralizar
        form_container = tk.Frame(self.frame, bg='#f0f2f5')
        form_container.pack(fill='both', expand=True)
        
        # Centralizando o formulário com frames laterais
        tk.Frame(form_container, bg='#f0f2f5', width=100).pack(side='left', fill='y')
        form_frame = tk.Frame(form_container, bg='#f0f2f5', padx=50, pady=20)
        form_frame.pack(side='left', fill='both', expand=True)
        tk.Frame(form_container, bg='#f0f2f5', width=100).pack(side='right', fill='y')
        
        # Estilo dos labels e campos
        label_style = {'font': ('Arial', 10, 'bold'), 'bg': '#f0f2f5', 'anchor': 'w', 'fg': '#000000'}
        entry_style = {'font': ('Arial', 10), 'width': 30, 'bg': 'white', 'borderwidth': 0, 'highlightthickness': 0}
        
        # Frame para o conteúdo
        content_frame = tk.Frame(form_frame, bg='#f0f2f5')
        content_frame.pack(fill='both', expand=True)
        
        # Configura o grid
        content_frame.columnconfigure(1, weight=1, minsize=300)  # Coluna dos campos
        
        # Opção para detectar se é servidor ou cliente
        self.is_server = tk.BooleanVar(value=False)
        try:
            # Tenta importar a função is_server_machine
            self.is_server.set(is_server_machine())
        except:
            # Se não conseguir importar, assume que não é servidor
            self.is_server.set(False)
            
        server_frame = tk.Frame(content_frame, bg='#f0f2f5')
        server_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')
        
        self.server_check = tk.Checkbutton(
            server_frame, 
            text="Esta máquina é o servidor do banco de dados", 
            variable=self.is_server,
            bg='#f0f2f5',
            font=('Arial', 10),
            command=self._atualizar_campos_servidor
        )
        self.server_check.pack(side='left', padx=5)
        
        # Servidor
        tk.Label(content_frame, text="Servidor:", **label_style).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.db_host = tk.Entry(content_frame, **entry_style)
        self.db_host.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        self.db_host.insert(0, self.config.get('host', 'localhost'))
        
        # Porta
        tk.Label(content_frame, text="Porta:", **label_style).grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.db_porta = tk.Entry(content_frame, **entry_style)
        self.db_porta.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
        self.db_porta.insert(0, str(self.config.get('port', '3306')))
        
        # Usuário
        tk.Label(content_frame, text="Usuário:", **label_style).grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.db_usuario = tk.Entry(content_frame, **entry_style)
        self.db_usuario.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
        self.db_usuario.insert(0, self.config.get('user', 'root'))
        
        # Senha
        tk.Label(content_frame, text="Senha:", **label_style).grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.db_senha = tk.Entry(content_frame, show="*", **entry_style)
        self.db_senha.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        self.db_senha.insert(0, self.config.get('password', ''))
        
        # Nome do Banco
        tk.Label(content_frame, text="Nome do Banco:", **label_style).grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.db_nome = tk.Entry(content_frame, **entry_style)
        self.db_nome.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
        self.db_nome.insert(0, self.config.get('database', 'clinica_filipi'))
        
        # Status da conexão
        self.status_label = tk.Label(
            content_frame,
            text="",
            font=('Arial', 9),
            bg='#f0f2f5',
            fg='#6c757d'
        )
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky='w')
        
        # Frame para os botões
        btn_frame = tk.Frame(content_frame, bg='#f0f2f5', pady=20)
        btn_frame.grid(row=7, column=0, columnspan=2, sticky='ew')
        
        # Frame para centralizar os botões
        btn_container = tk.Frame(btn_frame, bg='#f0f2f5')
        btn_container.pack(expand=True)
        
        # Botão Testar Conexão - Azul
        self.btn_teste = tk.Button(
            btn_container,
            text="Testar Conexão",
            font=('Arial', 10, 'bold'),
            bg='#4a6fa5',
            fg='white',
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#3b5a7f',
            activeforeground='white',
            command=self._testar_conexao
        )
        self.btn_teste.pack(side='left', padx=5)
        
        # Botão Salvar - Verde
        self.btn_salvar = tk.Button(
            btn_container,
            text="Salvar e Conectar",
            font=('Arial', 10, 'bold'),
            bg='#4CAF50',
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#43a047',
            activeforeground='white',
            command=self._salvar_e_conectar
        )
        self.btn_salvar.pack(side='left', padx=5)
        
        # Botão Sair - Vermelho
        self.btn_sair = tk.Button(
            btn_container,
            text="Sair",
            font=('Arial', 10, 'bold'),
            bg='#f44336',
            fg='white',
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            activebackground='#d32f2f',
            activeforeground='white',
            command=self._sair
        )
        self.btn_sair.pack(side='left', padx=5)
    
    def _atualizar_campos_servidor(self):
        """Atualiza os campos de servidor e porta com base na opção de servidor."""
        if self.is_server.get():
            self.db_host.delete(0, tk.END)
            self.db_host.insert(0, 'localhost')
            self.db_porta.delete(0, tk.END)
            self.db_porta.insert(0, '3306')
        else:
            self.db_host.delete(0, tk.END)
            self.db_host.insert(0, self.config.get('host', 'localhost'))
            self.db_porta.delete(0, tk.END)
            self.db_porta.insert(0, str(self.config.get('port', '3306')))
    
    def _testar_conexao(self):
        """Testa a conexão com o banco de dados usando os parâmetros informados."""
        # Obtém os valores dos campos
        host = self.db_host.get().strip()
        porta = self.db_porta.get().strip()
        usuario = self.db_usuario.get().strip()
        senha = self.db_senha.get()
        banco = self.db_nome.get().strip()
        
        # Valida os campos obrigatórios
        if not host or not porta or not usuario or not banco:
            messagebox.showwarning("Campos Obrigatórios", "Todos os campos são obrigatórios, exceto a senha.")
            return
        
        # Atualiza o botão e o status para mostrar que está testando
        self.btn_teste.config(state=tk.DISABLED, text="Testando...")
        self.status_label.config(text="Testando conexão...", fg='#6c757d')
        self.frame.update_idletasks()
        
        try:
            # Configura timeout reduzido para a conexão
            db_config = {
                'host': host,
                'port': int(porta),
                'user': usuario,
                'password': senha,
                'database': "clinica_filipi",
                'connection_timeout': 5,
                'connect_timeout': 5
            }
            
            # Tenta conectar ao banco de dados
            conn = mysql.connector.connect(**db_config)
            
            if conn.is_connected():
                conn.close()
                self.status_label.config(text="✅ Conexão bem-sucedida!", fg='#28a745')
                messagebox.showinfo("Sucesso", "Conexão com o banco de dados realizada com sucesso!")
                return True
            else:
                self.status_label.config(text="❌ Falha na conexão", fg='#dc3545')
                messagebox.showerror("Erro", "Falha ao conectar ao banco de dados.")
                return False
                
        except Exception as e:
            self.status_label.config(text=f"❌ Erro: {str(e)}", fg='#dc3545')
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {str(e)}")
            return False
        finally:
            # Restaura o botão
            self.btn_teste.config(state=tk.NORMAL, text="Testar Conexão")
    
    def _salvar_e_conectar(self):
        """Salva as configurações e tenta conectar ao banco de dados."""
        if self._testar_conexao():
            # Obtém os valores dos campos
            host = self.db_host.get().strip()
            porta = self.db_porta.get().strip()
            usuario = self.db_usuario.get().strip()
            senha = self.db_senha.get()
            banco = self.db_nome.get().strip()
            
            # Atualiza as configurações globais
            DB_CONFIG['host'] = host
            DB_CONFIG['port'] = int(porta)
            DB_CONFIG['user'] = usuario
            DB_CONFIG['password'] = senha
            DB_CONFIG['database'] = banco
            
            # Salva as configurações em um arquivo
            self._salvar_config_arquivo()
            
            # Fecha a tela de configuração
            self.frame.destroy()
            
            # Chama o callback de sucesso, se existir
            if self.callback_sucesso:
                self.callback_sucesso()
    
    def _salvar_config_arquivo(self):
        """Salva as configurações em um arquivo."""
        try:
            from src.controllers.config_controller import ConfigController
            
            # Cria uma instância do controlador
            ctrl = ConfigController(None)
            
            # Prepara os dados para salvar
            dados = {
                'host': self.db_host.get().strip(),
                'porta': self.db_porta.get().strip(),
                'usuario': self.db_usuario.get().strip(),
                'senha': self.db_senha.get(),
                'nome_bd': self.db_nome.get().strip(),
                'is_server': self.is_server.get()  # Salva a informação se é servidor
            }
            
            # Salva as configurações
            resultado = ctrl.salvar_config_db(
                host=dados['host'],
                porta=dados['porta'],
                usuario=dados['usuario'],
                senha=dados['senha'],
                banco=dados['nome_bd']
            )
            
            if not resultado:
                messagebox.showwarning(
                    "Aviso", 
                    "As configurações foram aplicadas, mas não foi possível salvá-las permanentemente.\n"
                    "Você precisará configurar novamente ao reiniciar o sistema."
                )
            
        except Exception as e:
            print(f"Erro ao salvar configurações em arquivo: {e}")
            messagebox.showwarning(
                "Aviso", 
                "As configurações foram aplicadas, mas não foi possível salvá-las permanentemente.\n"
                f"Erro: {str(e)}\n"
                "Você precisará configurar novamente ao reiniciar o sistema."
            )
    
    def _sair(self):
        """Fecha a aplicação."""
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.parent.quit()
