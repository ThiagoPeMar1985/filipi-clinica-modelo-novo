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
from src.controllers.financeiro_controller import FinanceiroController
from src.controllers.estoque_controller import EstoqueController

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from views.modulos.cadastro.cadastro_module import CadastroModule
from src.controllers.permission_controller import PermissionController


class SistemaPDV:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title("Clinica Medica")
        
        # Conexão (mantida)
        self.db_connection = getattr(usuario, 'db_connection', None)

        # Garantir janela em estado normal e sem fullscreen.
        self.root.state('normal')
        try:
            self.root.attributes('-fullscreen', False)
        except Exception:
            pass
        self.root.resizable(True, True)
        
        # Inicialização das variáveis de controle do chat
        self._chat_unread_count = 0
        self._chat_blink_job = None
        self._chat_blink_on = False
        self._modulo_labels = {}
        
        # Cores do tema
        self.cores = {
            "primaria": "#4a6fa5",
            "secundaria": "#28b5f4",
            "terciaria": "#333f50",
            "fundo": "#f0f2f5",
            "fundo_conteudo": "#f0f2f5",  
            "texto": "#000000",
            "texto_claro": "#ffffff",
            "destaque": "#4caf50",
            "alerta": "#f44336",
            "borda": "#f0f2f5"  
        }
        
        # Configuração de fundo
        self.root.configure(bg=self.cores["fundo"])
        
        # Variável para armazenar o módulo atual
        self.modulo_atual = None
        
        # Criar layout principal
        self.criar_layout()

        # Inicializa o controlador de permissões
        self.permission_controller = PermissionController()


        # Inicializa o controlador de configurações
        try:
            from src.controllers.config_controller import ConfigController
            self.config_controller = ConfigController()
            # Tenta carregar as configurações de impressão
            try:
                self.config_controller.carregar_config_impressoras()
            except Exception:
                pass
                
        except Exception as e:
            print(f"Erro ao inicializar ConfigController: {e}")
            self.config_controller = None
        
        # Configurar módulos
        self.configurar_modulos()
        # Atualiza status do caixa logo na inicialização
        try:
            self._atualizar_status_caixa()
        except Exception:
            pass
        
        # Verifica alerta de estoque baixo na abertura da tela principal
        try:
            # Aguarda alguns ms para garantir que os widgets foram renderizados
            self.root.after(300, self._verificar_alerta_estoque)
        except Exception:
            pass

        if hasattr(self, 'root'):
            self.root.after(1000, self._iniciar_verificacao_chat)
    
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
            text="Clinica Medica",
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
        
        # Badge do status do caixa (abaixo da data)
        self.caixa_badge = tk.Label(
            self.content_frame,
            text="CAIXA FECHADO",
            font=("Arial", 16, 'bold'),
            bg=self.cores.get('alerta', '#f44336'),
            fg=self.cores.get('texto_claro', '#ffffff'),
            padx=40,
            pady=12,
            bd=0,
            relief='flat',
        )
        self.caixa_badge.pack(pady=(10, 0))
        
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

    def _verificar_alerta_estoque(self):
        """Verifica itens com estoque baixo e mostra um painel fixo no canto da tela
        com a lista de produtos e quantidades atuais. Mantém visível até normalizar.
        Também agenda nova verificação periódica.
        """
        try:
            # Garantir conexão com o banco
            if not getattr(self, 'db_connection', None):
                try:
                    from src.db.database import db
                    self.db_connection = db.get_connection()
                except Exception:
                    return

            ec = EstoqueController(self.db_connection)
            itens_baixos = []
            try:
                itens_baixos = ec.baixo() or []
            except Exception:
                itens_baixos = []

            if not itens_baixos:
                # Se existir painel/badge anterior, remove
                if hasattr(self, 'estoque_painel') and self.estoque_painel is not None:
                    try:
                        self.estoque_painel.destroy()
                    except Exception:
                        pass
                    self.estoque_painel = None
                if hasattr(self, 'estoque_badge') and self.estoque_badge is not None:
                    try:
                        self.estoque_badge.destroy()
                    except Exception:
                        pass
                    self.estoque_badge = None
                # Agenda próxima verificação
                try:
                    self.root.after(60000, self._verificar_alerta_estoque)
                except Exception:
                    pass
                return

            # Monta linhas detalhadas para exibição
            linhas = []
            for item in itens_baixos:
                nome = (item.get('nome') if isinstance(item, dict) else str(item)) or 'Produto'
                qtd_atual = item.get('qtd_atual') if isinstance(item, dict) else None
                qtd_min = item.get('qtd_minima') if isinstance(item, dict) else None
                if qtd_atual is not None and qtd_min is not None:
                    linhas.append(f"- {nome}: {qtd_atual} (mín: {qtd_min})")
                else:
                    linhas.append(f"- {nome}")

            # Cria/atualiza um painel centralizado logo abaixo do badge do caixa com a lista
            try:
                if not hasattr(self, 'estoque_painel') or self.estoque_painel is None:
                    self.estoque_painel = tk.Frame(
                        self.content_frame,
                        bg=self.cores.get('alerta', '#f44336'),
                        bd=0,
                        highlightthickness=0,
                    )
                    # Posiciona centralizado abaixo do badge do caixa
                    try:
                        self.estoque_painel.place_forget()
                    except Exception:
                        pass
                    self.estoque_painel.pack(pady=(8, 0))

                    self._estoque_title = tk.Label(
                        self.estoque_painel,
                        text='Estoque baixo',
                        font=("Arial", 12, 'bold'),
                        bg=self.cores.get('alerta', '#f44336'),
                        fg=self.cores.get('texto_claro', '#ffffff'),
                        padx=10, pady=6,
                    )
                    self._estoque_title.pack(fill='x')

                    self._estoque_lista = tk.Frame(
                        self.estoque_painel,
                        bg=self.cores.get('alerta', '#f44336'),
                    )
                    self._estoque_lista.pack(fill='both', expand=True, padx=10, pady=(0, 8))
                else:
                    # Limpa lista para repovoar
                    try:
                        # Garante que está usando pack (centralizado)
                        self.estoque_painel.place_forget()
                    except Exception:
                        pass
                    try:
                        # Se já estava empacotado, ignore erro
                        self.estoque_painel.pack_configure(pady=(8, 0))
                    except Exception:
                        try:
                            self.estoque_painel.pack(pady=(8, 0))
                        except Exception:
                            pass
                    for w in list(self._estoque_lista.winfo_children()):
                        w.destroy()

                # Popula a lista
                for linha in linhas:
                    lbl = tk.Label(
                        self._estoque_lista,
                        text=linha,
                        font=("Arial", 11),
                        bg=self.cores.get('alerta', '#f44336'),
                        fg=self.cores.get('texto_claro', '#ffffff'),
                        anchor='w',
                        justify='left',
                    )
                    lbl.pack(fill='x')

            except Exception:
                pass
            
            # Agenda próxima verificação periódica (60s)
            try:
                self.root.after(60000, self._verificar_alerta_estoque)
            except Exception:
                pass
        except Exception:
            # Silencia erros para não bloquear a abertura do sistema
            pass

    def _atualizar_status_caixa(self):
        """Atualiza o badge do status do caixa na tela inicial do PDV."""
        try:
            if not hasattr(self, 'caixa_badge') or self.caixa_badge is None:
                return
            # Garante conexão com o banco antes de consultar o status
            if not getattr(self, 'db_connection', None):
                try:
                    from src.db.database import db
                    self.db_connection = db.get_connection()
                except Exception:
                    return
            fc = FinanceiroController(self.db_connection)
            sessao = None
            try:
                sessao = fc.get_sessao_aberta()
            except Exception:
                sessao = None
            aberto = bool(sessao)
            if aberto:
                self.caixa_badge.config(
                    text='CAIXA ABERTO',
                    bg=self.cores.get('destaque', '#4CAF50'),
                    fg=self.cores.get('texto_claro', '#ffffff')
                )
            else:
                self.caixa_badge.config(
                    text='CAIXA FECHADO',
                    bg=self.cores.get('alerta', '#f44336'),
                    fg=self.cores.get('texto_claro', '#ffffff')
                )
        except Exception:
            pass
    
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
            {"nome": "🏢 Empresa", "metodo": "empresa"},
            {"nome": "👥 Usuários", "metodo": "usuarios"},
            {"nome": "👨 Médicos", "metodo": "medicos"},
            {"nome": "👤 Pacientes", "metodo": "pacientes"},
            {"nome": "📝 Modelos", "metodo": "modelos"},
            {"nome": "📜 Receitas", "metodo": "receitas"},
            {"nome": "⏳ Exames & Consultas", "metodo": "exames_consultas"},
            {"nome": "📅 Horário Médico", "metodo": "horario_medico"},
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

    def _get_opcoes_atendimento(self):
        """Retorna as opções do módulo de atendimento"""
        return [
            {"nome": "📅 Agenda", "metodo": "agenda"},
            {"nome": "📋 Consultas", "metodo": "consultas"},
            {"nome": "🏥 Exames", "metodo": "exames"}
        ]

    def _get_opcoes_financeiro(self):
        """Retorna as opções do módulo financeiro"""
        return [
            {"nome": "💵 Caixa", "metodo": "caixa"},
            {"nome": "📝 Contas a Pagar", "metodo": "contas_pagar"},
            {"nome": "📋 Contas a Receber", "metodo": "contas_receber"},
            {"nome": "📊 Relatórios", "metodo": "relatorios"},
            {"nome": "📦 Estoque", "metodo": "estoque"}
        ]
        
    def _get_opcoes_chat(self):
        """Retorna as opções do módulo de chat"""
        return [
            {"nome": "💬 mensagens", "metodo": "mensagens"}
        ]
        
    def configurar_modulos(self):
        """Configura os módulos do sistema"""
        # Obtém as opções dos módulos
        opcoes_cadastro = self._get_opcoes_cadastro()
        opcoes_configuracao = self._get_opcoes_configuracao()
        opcoes_atendimento = self._get_opcoes_atendimento()
        opcoes_financeiro = self._get_opcoes_financeiro()
        opcoes_chat = self._get_opcoes_chat()

        
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
            
        # Configura os comandos para cada opção de atendimento
        for opcao in opcoes_atendimento:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'atendimento'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('atendimento', m)
            
        # Configura os comandos para cada opção de financeiro
        for opcao in opcoes_financeiro:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'financeiro'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('financeiro', m)
        
        # Configura os comandos para cada opção de chat
        for opcao in opcoes_chat:
            metodo = opcao["metodo"]
            opcao["modulo"] = 'chat'
            opcao["acao"] = metodo
            opcao["comando"] = lambda m=metodo: self.mostrar_conteudo_modulo('chat', m)
        
        # Configura os módulos disponíveis
        self.modulos = {
            "cadastro": {
                "nome": "CADASTRO",
                "icone": "📋",
                "opcoes": opcoes_cadastro
            },
            "atendimento": {
                "nome": "ATENDIMENTO",
                "icone": "🏥",
                "opcoes": opcoes_atendimento
            },
            "financeiro": {
                "nome": "FINANCEIRO",
                "icone": "💰",
                "opcoes": opcoes_financeiro
            },
            "configuracao": {
                "nome": "CONFIGURAÇÃO",
                "icone": "⚙️",
                "opcoes": opcoes_configuracao
            },
            "chat": {
                "nome": "CHAT",
                "icone": "💬",
                "opcoes": opcoes_chat
            }
        }
        
        # Mantém referência para os botões de módulos (para piscar o Chat)
        self._modulo_labels = {}
        self._chat_blink_job = None
        self._chat_blink_on = False
        self._chat_unread_count = 0

        for modulo_id, modulo in self.modulos.items():
            # Cria um Label que funcionará como botão
            lbl = tk.Label(
                self.modulos_frame,
                text=f"{modulo['icone']} {modulo['nome']}",
                bg=self.cores["primaria"],  # Cor fixa
                fg=self.cores["texto_claro"],
                font=("Arial", 11),
                padx=10,
                pady=5,
                cursor="hand2"
            )
            
            # Adiciona o evento de clique sem mudar a cor
            lbl.bind("<Button-1>", lambda e, m=modulo_id: self.selecionar_modulo(m))
            lbl.pack(side="left", padx=5)
            self._modulo_labels[modulo_id] = lbl
        
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
            try:
                tem_permissao = self.permission_controller.verificar_permissao(
                    self.usuario,
                    modulo_id,  # módulo
                    opcao.get("acao")  # ação
                ) if hasattr(self, 'permission_controller') and self.permission_controller else True
            except Exception:
                tem_permissao = True

            # Removida exceção temporária de liberação do "estoque"; respeitar permissões do banco

            # Se não tiver permissão, pula para a próxima opção
            if not tem_permissao:
                continue
            # Cria um Label que funcionará como botão
            lbl = tk.Label(
                self.sidebar_options,
                text=opcao["nome"],
                bg=self.cores["terciaria"],  # Cor fixa
                fg=self.cores["texto_claro"],
                font=("Arial", 11),
                anchor="w",
                padx=15,
                pady=10,
                cursor="hand2"
            )
            
            # Adiciona o evento de clique sem mudar a cor
            lbl.bind("<Button-1>", lambda e, cmd=opcao["comando"]: cmd())
            lbl.pack(fill="x")
            
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
            if modulo_id == 'atendimento':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de atendimento
                from views.modulos.atendimento.atendimento_module import AtendimentoModule
                from src.db.database import db
                
                # Obtém a conexão com o banco de dados
                db_connection = db.get_connection()
                
                # Cria a instância do módulo
                modulo = AtendimentoModule(modulo_frame, self, db_connection)
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Se for uma ação específica, chama o método executar_acao
                if metodo_nome and metodo_nome != 'mostrar_inicio':
                    modulo.executar_acao(metodo_nome)
                else:
                    modulo.mostrar_inicio()
    
                    
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
                if hasattr(modulo, 'executar_acao'):
                    modulo.executar_acao(metodo_nome)
                elif hasattr(modulo, metodo_nome):
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
                    
            elif modulo_id == 'financeiro':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de financeiro
                from src.views.modulos.financeiro.financeiro_module import FinanceiroModule
                from src.db.database import db
                
                # Obtém a conexão com o banco de dados
                db_connection = db.get_connection()
                
                # Cria a instância do módulo
                modulo = FinanceiroModule(modulo_frame, self)
                
                # Define a conexão com o banco de dados
                self.db_connection = db_connection
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Se for uma ação específica, chama o método correspondente
                if metodo_nome and metodo_nome != 'mostrar_inicio':
                    modulo.show(metodo_nome)
                else:
                    modulo.show()
            
            elif modulo_id == 'chat':
                # Cria um frame para o módulo que ocupa todo o espaço
                modulo_frame = tk.Frame(self.content_frame, bg='#f0f2f5')
                modulo_frame.pack(fill='both', expand=True)
                
                # Importa o módulo de chat
                from src.views.modulos.chat.chat_module import ChatModule
                
                # Cria a instância do módulo
                modulo = ChatModule(modulo_frame, self)
                
                # Configura o frame do módulo para ocupar todo o espaço
                modulo.frame.pack(fill='both', expand=True, padx=10, pady=10)
                
                # Exibe o conteúdo principal do chat (respeitando ação)
                if hasattr(modulo, 'show'):
                    if metodo_nome and metodo_nome != 'mostrar_inicio':
                        modulo.show(metodo_nome)
                    else:
                        modulo.show()
                else:
                    try:
                        modulo.render(modulo_frame)
                    except Exception:
                        pass

                # Ao abrir o chat, limpar notificação de não lidas
                try:
                    self.notify_chat_unread(0)
                except Exception:
                    pass
                    
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

   
    def notify_chat_unread(self, count: int):
        """Atualiza contagem de mensagens não lidas e acende o botão Chat quando > 0."""
        # Garante que count seja um número inteiro não negativo
        self._chat_unread_count = max(0, int(count or 0))
        
        # Atualiza o botão de chat
        lbl = self._modulo_labels.get('chat')
        if lbl:
            try:
                if self._chat_unread_count > 0:
                    # Mantém o botão verde (aceso) quando há mensagens não lidas
                    lbl.config(bg=self.cores.get('destaque', '#4CAF50'))
                else:
                    # Restaura a cor original quando não há mensagens não lidas
                    lbl.config(bg=self.cores.get('primaria', lbl.cget('bg')))
            except Exception:
                pass
                
        # Cancela qualquer job de piscar que possa estar ativo
        if self._chat_blink_job is not None:
            try:
                self.root.after_cancel(self._chat_blink_job)
                self._chat_blink_job = None
            except Exception:
                pass
    
    def sair(self):
        """Fecha a aplicação"""
        """Fecha a aplicação"""
        # Cancela a verificação de mensagens
        if hasattr(self, '_chat_check_job') and self._chat_check_job:
            self.root.after_cancel(self._chat_check_job)
        
        # Fecha a janela
        self.root.destroy()

    def _iniciar_verificacao_chat(self):
        """Inicia a verificação periódica de mensagens não lidas"""
        def verificar_mensagens():
            try:
                if hasattr(self, 'usuario') and hasattr(self.usuario, 'id'):
                    from src.db.chat_db import ChatDB
                    from src.db.database import db
                    
                    # Usa a conexão existente se disponível
                    conn = getattr(self, 'db_connection', None) or db.get_connection()
                    try:
                        chat_db = ChatDB(conn)
                        contagem = chat_db.contar_nao_lidas_para(
                            self.usuario.id,
                            getattr(self.usuario, 'nome', 'Usuário')
                        )
                        
                        # Atualiza a interface
                        if hasattr(self, 'notify_chat_unread'):
                            self.notify_chat_unread(contagem)
                            
                    finally:
                        # Fecha a conexão apenas se não for a conexão compartilhada
                        if conn is not getattr(self, 'db_connection', None):
                            try:
                                conn.close()
                            except:
                                pass
                                
            except Exception as e:
                print(f"Erro ao verificar mensagens: {e}")
            
            # Agenda próxima verificação em 5 segundos
            if hasattr(self, 'root'):
                self.root.after(5000, self._iniciar_verificacao_chat)
        
        verificar_mensagens()
