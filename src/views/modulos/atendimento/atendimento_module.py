"""
Módulo de Atendimento - Gerencia a navegação entre as telas de atendimento
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ..base_module import BaseModule
# Importa o módulo de agendamento uma única vez
from .agendamento_module import AgendamentoModule

class AtendimentoModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        super().__init__(parent, controller)
        
        # Armazena a conexão com o banco de dados
        self.db_connection = db_connection
        
        # Inicializa o módulo de agendamento como None
        self.agendamento_module = None
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Frame para o conteúdo
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mapeamento de ações para as funções correspondentes
        # As chaves DEVEM corresponder exatamente ao que é passado pelo menu lateral
        # Suporta rótulos antigos ("prontuario") e novos ("Consultas" e "Área Médica")
        self.acoes = {
            "inicio": self.mostrar_inicio,
            "agenda": self.mostrar_agenda,
            "prontuario": self.mostrar_prontuario,
            # aliases para o novo nome do botão/rota "Consultas"
            "consultas": self.mostrar_prontuario,
            "consulta": self.mostrar_prontuario,
            # aliases para o novo nome do botão/rota
            "area_medica": self.mostrar_prontuario,
            "área_médica": self.mostrar_prontuario,
            "área médica": self.mostrar_prontuario,
            "area medica": self.mostrar_prontuario,
            "exames": self.mostrar_exames,
        }
        
        # Mostra a tela inicial
        self.mostrar_inicio()
    
    def mostrar_inicio(self):
        """Mostra a tela inicial do módulo de atendimento"""
        self.limpar_conteudo()
        
        # Adiciona uma mensagem de boas-vindas
        tk.Label(
            self.conteudo_frame, 
            text="Selecione uma opção no menu lateral para começar.", 
            font=('Arial', 12),
            bg='#f0f2f5',
            fg='#333333'
        ).pack(pady=20)

        # Badge do status do caixa abaixo da frase
        try:
            # BaseModule fornece o helper reutilizável
            self.create_caixa_status_badge(self.conteudo_frame, pady=(0, 0))
        except Exception:
            pass
    
    def mostrar_agenda(self):
        """Mostra a tela de agenda"""
        self.limpar_conteudo()
        
        try:
            # Se o módulo já existe, apenas reconfigura o frame
            if hasattr(self, 'agendamento_module') and self.agendamento_module is not None:
                # Remove o frame antigo se existir
                if hasattr(self.agendamento_module, 'frame') and self.agendamento_module.frame.winfo_exists():
                    self.agendamento_module.frame.pack_forget()
                
                # Cria um novo frame para o módulo
                self.agendamento_module.frame = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
                self.agendamento_module.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Reconstroi a interface do módulo
                self.agendamento_module._criar_interface()
            else:
                # Cria uma nova instância do módulo se não existir
                self.agendamento_module = AgendamentoModule(
                    self.conteudo_frame, 
                    self.controller,
                    self.db_connection
                )
                
                # Configura o frame do módulo
                self.agendamento_module.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            # Em caso de erro, mostra uma mensagem de erro
            error_msg = f"Erro ao carregar o módulo de agendamento: {str(e)}"
            messagebox.showerror("Erro", error_msg)
            print(error_msg)
            
            # Volta para a tela inicial em caso de erro
            self.mostrar_inicio()
    
    def mostrar_prontuario(self):
        """Mostra a tela de prontuário (Consultas / Área Médica)."""
        
        self.limpar_conteudo()
        
        # Importa o módulo de prontuários
        from .prontuario_module import ProntuarioModule
        
        # Cria e exibe o módulo de prontuários (garante conexão DB para resolver CRM)
        prontuario_module = ProntuarioModule(self.conteudo_frame, self.controller, db_connection=self.db_connection)
        prontuario_module.exibir()
    
    def mostrar_exames(self):
        """Mostra a tela de exames"""
        self.limpar_conteudo()
        
        # Importa o módulo de Exames que reutiliza o layout/fluxo do Prontuário
        from .exames_prontuario_module import ExamesProntuarioModule
        
        # Cria e exibe o módulo de Exames (mesma UX do Prontuário)
        exames_module = ExamesProntuarioModule(self.conteudo_frame, self.controller, db_connection=self.db_connection)
        frame = exames_module.get_frame()
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def limpar_conteudo(self):
        """Limpa o conteúdo do frame"""
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
    
    def executar_acao(self, acao):
        """
        Executa uma ação específica no módulo
        
        Args:
            acao (str): Nome da ação a ser executada (deve corresponder a uma chave em self.acoes)
        """
        if acao in self.acoes:
            self.acoes[acao]()