"""

modulo da tela principal do sistema PDV

e que nao vai ter nenhuma função logica  alem do criar tela e sair do programa
 a barra lateral esquerda precisa mostrar os botoes criados nos arquivos de cada modulo
 a tela central cinza mostra os dados 

"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sys
import os

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from views.modulos.cadastro.cadastro_module import CadastroModule
from src.controllers.permission_controller import PermissionController

class SistemaPDV:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title("PDV Bar & Restaurante")
        
        # Configura o tamanho da janela
        largura = 1780
        altura = 1280
        
        self.db_connection = getattr(usuario, 'db_connection', None)  


        # Obtém as dimensões da tela
        largura_tela = root.winfo_screenwidth()
        altura_tela = root.winfo_screenheight()
        
        # Calcula a posição para centralizar
        pos_x = (largura_tela // 2) - (largura // 2)
        pos_y = (altura_tela // 2) - (altura // 2)
        
        # Define a geometria da janela e desativa tela cheia
        self.root.state('normal')  # Garante que não está maximizado
        self.root.attributes('-fullscreen', False)  # Desativa tela cheia
        self.root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')
        self.root.resizable(True, True)  # Permite redimensionamento
        
        # Cores do tema
        self.cores = {
            "primaria": "#4a6fa5",
            "secundaria": "#28b5f4",
            "terciaria": "#333f50",
            "fundo": "#f0f2f5",
            "fundo_conteudo": "#f0f2f5",  # Mesma cor do fundo para remover a borda branca
            "texto": "#000000",
            "texto_claro": "#ffffff",
            "destaque": "#4caf50",
            "alerta": "#f44336",
            "borda": "#f0f2f5"  # Mesma cor do fundo para remover a borda
        }
        
        # Configuração de fundo
        self.root.configure(bg=self.cores["fundo"])
        
        # Variável para armazenar o módulo atual
        self.modulo_atual = None
        
        # Criar layout principal
        self.criar_layout()
        
        # Inicializa o controlador de permissões
        self.permission_controller = PermissionController()
        
        # Configurar módulos
        self.configurar_modulos()
        
        # Configurar manipulador de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.sair)
    
    def criar_layout(self):
        """Cria o layout principal da aplicação"""
        # Frame principal que conterá todo o conteúdo
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame do cabeçalho
        self.header_frame = tk.Frame(self.main_frame, bg=self.cores["primaria"], height=60)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        # Título no cabeçalho
        title_label = tk.Label(
            self.header_frame, 
            text="QUIOSQUE AQUARIUS",
            font=("Arial", 16, "bold"),
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"]
        )
        title_label.pack(side="left", padx=25, pady=15)
        
        # Frame para botões dos módulos
        self.modulos_frame = tk.Frame(self.header_frame, bg=self.cores["primaria"])
        self.modulos_frame.pack(side="left", padx=25, pady=10, fill="y")
        
        # Frame para informações do usuário
        user_frame = tk.Frame(self.header_frame, bg=self.cores["primaria"])
        user_frame.pack(side="right", padx=25, pady=10)
        
        # Informações do usuário
        user_label = tk.Label(
            user_frame,
            text=f"{self.usuario.nome} ({self.usuario.nivel})",
            font=("Arial", 12),
            bg=self.cores["primaria"],
            fg=self.cores["texto_claro"]
        )
        user_label.pack(side="left", padx=10)
        
        # Botão de sair
        sair_button = tk.Button(
            user_frame,
            text="🚪 Sair",
            command=self.sair,
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            font=("Arial", 11, "bold"),
            relief="flat",
            padx=15,
            pady=5,
            activebackground="#d32f2f",
            activeforeground=self.cores["texto_claro"],
            cursor="hand2"
        )
        sair_button.pack(side="left", padx=10)
        
        # Container principal
        self.container = tk.Frame(self.main_frame, bg=self.cores["fundo"])
        self.container.pack(expand=True, fill="both")
        
        # Barra lateral
        self.sidebar = tk.Frame(self.container, bg=self.cores["terciaria"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Título da barra lateral
        self.sidebar_title = tk.Label(
            self.sidebar,
            text="",
            font=("Arial", 14, "bold"),
            bg=self.cores["terciaria"],
            fg=self.cores["texto_claro"]
        )
        self.sidebar_title.pack(pady=(20, 10), fill="x", padx=10)
        
        # Frame para opções da barra lateral
        self.sidebar_options = tk.Frame(self.sidebar, bg=self.cores["terciaria"])
        self.sidebar_options.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Área de conteúdo
        self.content_frame = tk.Frame(self.container, bg=self.cores["fundo_conteudo"])
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Mensagem de boas-vindas
        welcome_label = tk.Label(
            self.content_frame,
            text=f"Bem-vindo, {self.usuario.nome}!",
            font=("Arial", 28, "bold"),
            bg=self.cores["fundo_conteudo"],
            fg=self.cores["texto"]
        )
        welcome_label.pack(pady=50)
        
        # Data atual
        meses_pt_br = {
            'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
            'April': 'abril', 'May': 'maio', 'June': 'junho',
            'July': 'julho', 'August': 'agosto', 'September': 'setembro',
            'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
        }
        data_ingles = datetime.now().strftime("%d de %B de %Y")
        for eng, pt in meses_pt_br.items():
            data_ingles = data_ingles.replace(eng, pt)
            
        date_label = tk.Label(
            self.content_frame,
            text=data_ingles,
            font=("Arial", 20),
            bg=self.cores["fundo_conteudo"],
            fg=self.cores["texto"]
        )
        date_label.pack()
        
        # Créditos do software
        credits_label = tk.Label(
            self.content_frame,
            text="Software produzido por Thiago Periard Martins",
            font=("Arial", 14),
            bg=self.cores["fundo_conteudo"],
            fg=self.cores["texto"]
        )
        credits_label.pack(side="bottom", pady=50)
        
        # Inicializa o gerenciador de módulos como None
        self.modulo_manager = None
        
        # Barra de status
        self.status_bar = tk.Frame(self.main_frame, bg=self.cores["terciaria"], height=30)
        self.status_bar.pack(fill="x", side="bottom")
        
        # Data e hora com atualização automática
        self.data_label = tk.Label(
            self.status_bar,
            text="",
            bg=self.cores["terciaria"],
            fg=self.cores["texto_claro"],
            font=("Arial", 10)
        )
        self.data_label.pack(side="right", padx=15, pady=3)
        
        # Iniciar a atualização do relógio
        self._atualizar_relogio()
    
    def _atualizar_relogio(self):
        """Atualiza o relógio a cada segundo"""
        # Atualizar a data e hora atual
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.data_label.config(text=data_atual)
        
        # Agendar a próxima atualização em 1000ms (1 segundo)
        self.root.after(1000, self._atualizar_relogio)
    
    def _get_opcoes_cadastro(self):
        """Retorna as opções do módulo de cadastro"""
        return [
            {"nome": "🏢 Empresa", "metodo": "mostrar_empresa"},
            {"nome": "👥 Usuários", "metodo": "mostrar_usuarios"},
            {"nome": "👷 Funcionários", "metodo": "mostrar_funcionarios"},
            {"nome": "👤 Clientes", "metodo": "mostrar_clientes"},
            {"nome": "📦 Produtos", "metodo": "mostrar_produtos"},
            {"nome": "🏭 Fornecedores", "metodo": "mostrar_fornecedores"},
            {"nome": "➕ Opções", "metodo": "mostrar_opcoes"}
        ]

    def _get_opcoes_configuracao(self):
        """Retorna as opções do módulo de configuração"""
        return [
            {"nome": "📄 NF-e", "metodo": "nfe"},
            {"nome": "💾 Backup", "metodo": "backup"},
            {"nome": "🖨 Impressoras", "metodo": "impressoras"},
            {"nome": "💿 Banco de Dados", "metodo": "banco_dados"},
            {"nome": "🔌 Integrações", "metodo": "integracoes"},
            {"nome": "🔒 Segurança", "metodo": "seguranca"}
        ]

    def _get_opcoes_vendas(self):
        """Retorna as opções do módulo de vendas"""
        return [
            {"nome": "💰 Venda Avulsa", "metodo": "venda_avulsa"},
            {"nome": "🛵 Delivery", "metodo": "delivery"},
            {"nome": "📊 Status Pedidos", "metodo": "status_pedidos"}
        ]
        
    def _get_opcoes_mesas(self):
        """Retorna as opções do módulo de mesas"""
        return [
            {"nome": "👁️ Visualizar Mesas", "metodo": "visualizar"},
            {"nome": "✏️ Editar Mesas", "metodo": "editar"},
            {"nome": "🔄 Transferir Mesa", "metodo": "transferir"}
        ]

    def configurar_modulos(self):
        """Configura os módulos do sistema"""
        # Obtém as opções dos módulos
        opcoes_cadastro = self._get_opcoes_cadastro()
        opcoes_configuracao = self._get_opcoes_configuracao()
        opcoes_vendas = self._get_opcoes_vendas()
        opcoes_mesas = self._get_opcoes_mesas()
        
        # Configura os comandos para cada opção do cadastro
        for opcao in opcoes_cadastro:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'cadastro'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('cadastro', m)
        
        # Configura os comandos para cada opção de configuração
        for opcao in opcoes_configuracao:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'configuracao'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('configuracao', m)
            
        # Configura os comandos para cada opção de vendas
        for opcao in opcoes_vendas:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'vendas'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('vendas', m)
            
        # Configura os comandos para cada opção de mesas
        for opcao in opcoes_mesas:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'mesas'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('mesas', m)
        
        # Configura os módulos disponíveis
        self.modulos = {
            "cadastro": {
                "nome": "CADASTRO",
                "icone": "📋",
                "opcoes": opcoes_cadastro
            },
            "vendas": {
                "nome": "VENDAS",
                "icone": "💰",
                "opcoes": opcoes_vendas
            },
            "mesas": {
                "nome": "MESAS",
                "icone": "🍽️",
                "opcoes": opcoes_mesas
            },
            "financeiro": {
                "nome": "FINANCEIRO",
                "icone": "💰",
                "opcoes": []
            },
            "estoque": {
                "nome": "ESTOQUE",
                "icone": "📦",
                "opcoes": []
            },
            "configuracao": {
                "nome": "CONFIGURAÇÃO",
                "icone": "⚙️",
                "opcoes": opcoes_configuracao
            }
        }
        
        # Criar botões dos módulos no cabeçalho
        for modulo_id, modulo in self.modulos.items():
            btn = tk.Button(
                self.modulos_frame,
                text=f"{modulo['icone']} {modulo['nome']}",
                command=lambda m=modulo_id: self.selecionar_modulo(m),
                bg=self.cores["primaria"],
                fg=self.cores["texto_claro"],
                font=("Arial", 11),
                relief="flat",
                padx=10,
                pady=5,
                activebackground=self.cores["secundaria"],
                activeforeground=self.cores["texto_claro"]
            )
            btn.pack(side="left", padx=5)
    
    def selecionar_modulo(self, modulo_id):
        """Seleciona um módulo para exibição"""
        # Limpa opções anteriores
        for widget in self.sidebar_options.winfo_children():
            widget.destroy()
        
        # Atualiza o título da barra lateral
        modulo = self.modulos.get(modulo_id, {})
        self.sidebar_title.config(text=modulo.get("nome", ""))
        
        # Adiciona as opções do módulo na barra lateral
        for opcao in modulo.get("opcoes", []):
            # Verifica se o usuário tem permissão para ver esta opção
            tem_permissao = self.permission_controller.verificar_permissao(
                self.usuario, 
                opcao.get("modulo", ""), 
                opcao.get("acao", "")
            )
            
            if tem_permissao:
                btn = tk.Button(
                    self.sidebar_options,
                    text=opcao["nome"],
                    command=opcao["comando"],
                    bg=self.cores["terciaria"],
                    fg=self.cores["texto_claro"],
                    font=("Arial", 11),
                    relief="flat",
                    anchor="w",
                    padx=15,
                    pady=10,  # Aumentado o padding vertical
                    width=20,  # Definindo largura fixa para todos os botões
                    activebackground=self.cores["secundaria"],
                    activeforeground=self.cores["texto_claro"]
                )
                btn.pack(fill="x", pady=3)  # Aumentado o espaçamento entre botões
        
        # Atualiza o módulo atual
        self.modulo_atual = modulo_id
        
        # Chama o método mostrar_conteudo_modulo com o módulo selecionado
        self.mostrar_conteudo_modulo(modulo_id)
            

    def mostrar_conteudo_modulo(self, modulo_id, metodo_nome='mostrar_inicio'):
        """Mostra o conteúdo do módulo selecionado"""
        # Limpa o conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        try:
            if modulo_id == 'vendas':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de vendas
                from src.views.modulos.vendas.vendas_module import VendasModule
                from src.db.database import db
                
                # Obtém a conexão com o banco de dados
                db_connection = db.get_connection()
                
                # Cria a instância do módulo
                modulo = VendasModule(modulo_frame, self)
                
                # Define a conexão com o banco de dados
                self.db_connection = db_connection
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Chama o método show com a ação específica
                modulo.show(metodo_nome)
                
            elif modulo_id == 'cadastro':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de cadastro
                from views.modulos.cadastro.cadastro_module import CadastroModule
                from src.db.database import db
                
                # Obtém a conexão com o banco de dados
                db_connection = db.get_connection()
                
                # Cria a instância do módulo
                modulo = CadastroModule(modulo_frame, self, db_connection)
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Chama o método solicitado ou o padrão
                if hasattr(modulo, metodo_nome):
                    metodo = getattr(modulo, metodo_nome)
                    metodo()
                else:
                    modulo.mostrar_inicio()
            
            elif modulo_id == 'configuracao':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de configuração
                from views.modulos.configuracao.configuracao_module import ConfiguracaoModule
                
                # Cria a instância do módulo
                modulo = ConfiguracaoModule(modulo_frame, self)
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Se for uma ação específica (como 'impressoras'), chama diretamente o método correspondente
                if metodo_nome and metodo_nome != 'mostrar_inicio':
                    if hasattr(modulo, f'_show_{metodo_nome}'):
                        metodo = getattr(modulo, f'_show_{metodo_nome}')
                        metodo()
                    else:
                        modulo.show(metodo_nome)
                else:
                    modulo.show()
                    
            elif modulo_id == 'mesas':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de mesas
                from src.views.modulos.mesas.mesas_module import MesasModule
                from src.db.database import db
                
                # Obtém a conexão com o banco de dados
                db_connection = db.get_connection()
                
                # Cria a instância do módulo
                modulo = MesasModule(modulo_frame, self)
                
                # Define a conexão com o banco de dados
                self.db_connection = db_connection
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Se for uma ação específica, chama o método correspondente
                if metodo_nome and metodo_nome != 'mostrar_inicio':
                    modulo.show(metodo_nome)
                else:
                    modulo.show()
                    
            # Força a atualização da interface
            self.content_frame.update_idletasks()
                
        except Exception as e:
            error_label = tk.Label(
                self.content_frame,
                text=f"Erro ao carregar o conteúdo: {str(e)}",
                font=("Arial", 11),
                bg=self.cores["fundo"],
                fg=self.cores["alerta"],
                wraplength=500,
                justify="left"
            )
            error_label.pack(pady=20, padx=20, anchor='w')
    
    def sair(self):
        """Fecha a aplicação"""
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.root.destroy()