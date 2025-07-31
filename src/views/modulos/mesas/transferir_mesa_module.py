"""
Módulo para transferência de pedidos entre mesas.
Permite transferir um pedido de uma mesa ocupada para uma mesa livre.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from src.views.modulos.base_module import BaseModule
from src.config.estilos import CORES, FONTES, ESTILOS_BOTAO, aplicar_estilo

class TransferirMesaModule:
    def __init__(self, parent, controller, db_connection=None):
        """
        Inicializa o módulo de transferência de mesas.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
            db_connection: Conexão com o banco de dados
        """
        self.parent = parent
        self.controller = controller
        self.db_connection = db_connection
        
        # Dados das mesas
        self.mesas_ocupadas = []
        self.mesas_livres = []
        self.mesa_origem = None
        self.mesa_destino = None
        
        # Frame principal
        self.frame = ttk.Frame(parent, padding=20, style='TFrame')
        
        # Configurar a interface
        self._setup_ui()
        self._carregar_mesas()
    
    def show(self):
        """Configura e retorna o frame principal do módulo"""
        # Garantir que o frame ocupe todo o espaço disponível
        self.frame.pack(fill='both', expand=True)
        
        # Forçar atualização da interface
        self.frame.update_idletasks()
        
        return self.frame
    
    def _setup_ui(self):
        """Configura a interface do usuário"""
        try:

            # Frame para o título no topo
            title_frame = ttk.Frame(self.frame)
            title_frame.pack(fill='x', pady=(0, 20))
            
            # Título
            titulo = ttk.Label(
                title_frame, 
                text="Transferir Mesa", 
                font=('Arial', 16, 'bold')
            )
            titulo.pack(side='left', anchor='w')
            
            # Frame para as listas de mesas
            listas_frame = ttk.Frame(self.frame)
            listas_frame.pack(fill='both', expand=True, pady=10)
            
            # Configuração das listas
            listbox_config = {
                'height': 15,
                'font': ('Arial', 11),
                'selectmode': 'browse',
                'exportselection': False,  # Permite seleção em ambas as listas
                'highlightthickness': 0,   # Remove a borda de foco
                'activestyle': 'none',     # Remove o sublinhado do item ativo
                'selectbackground': '#4a7abc',
                'selectforeground': 'white'
            }
            
            # Configurar estilo para remover a linha tracejada de foco
            style = ttk.Style()
            style.configure('NoFocus', highlightthickness=0, highlightcolor='white')
            
            # Frame para mesas ocupadas
            ocupadas_frame = ttk.LabelFrame(listas_frame, text="Mesas Ocupadas", padding=10)
            ocupadas_frame.pack(side='left', fill='both', expand=True, padx=5)
            
            # Lista de mesas ocupadas
            self.lista_ocupadas = tk.Listbox(ocupadas_frame, **listbox_config)
            self.lista_ocupadas.pack(fill='both', expand=True, pady=5)
            self.lista_ocupadas.bind('<<ListboxSelect>>', self._on_select_ocupada)
            
            # Scrollbar para a lista de ocupadas
            scroll_ocupadas = ttk.Scrollbar(ocupadas_frame, orient='vertical', command=self.lista_ocupadas.yview)
            scroll_ocupadas.pack(side='right', fill='y')
            self.lista_ocupadas.config(yscrollcommand=scroll_ocupadas.set)
            
            # Frame para mesas livres
            livres_frame = ttk.LabelFrame(listas_frame, text="Mesas Livres", padding=10)
            livres_frame.pack(side='right', fill='both', expand=True, padx=5)
            
            # Lista de mesas livres
            self.lista_livres = tk.Listbox(livres_frame, **listbox_config)
            self.lista_livres.pack(fill='both', expand=True, pady=5)
            self.lista_livres.bind('<<ListboxSelect>>', self._on_select_livre)
            
            # Scrollbar para a lista de livres
            scroll_livres = ttk.Scrollbar(livres_frame, orient='vertical', command=self.lista_livres.yview)
            scroll_livres.pack(side='right', fill='y')
            self.lista_livres.config(yscrollcommand=scroll_livres.set)
            
            # Frame para botões
            botoes_frame = ttk.Frame(self.frame)
            botoes_frame.pack(fill='x', pady=10)
            
            # Importar estilos
            from src.config.estilos import aplicar_estilo, ESTILOS_BOTAO
            
            # Largura fixa para os botões (baseada no texto mais longo)
            btn_width = 15
            btn_padx = 20
            btn_pady = 8
            
            # Botão de transferir (estilo padrão - azul)
            self.btn_transferir = tk.Button(
                botoes_frame, 
                text="TRANSFERIR",
                command=self._transferir,
                state='disabled',
                width=btn_width
            )
            aplicar_estilo(self.btn_transferir, "padrao")
            self.btn_transferir.pack(side='right', padx=10, pady=5, ipadx=btn_padx, ipady=btn_pady)
            
            # Botão de cancelar
            btn_cancelar = tk.Button(
                botoes_frame,
                text="CANCELAR",
                command=self._cancelar,
                width=btn_width
            )
            aplicar_estilo(btn_cancelar, "perigo")
            btn_cancelar.pack(side='right', padx=10, pady=5, ipadx=btn_padx, ipady=btn_pady)
            
            # Estilo para o frame dos botões
            botoes_frame.configure(style='Botoes.TFrame')
            
        except Exception as e:
            print(f"ERRO em _setup_ui: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _carregar_mesas(self):
        """Carrega as mesas do banco de dados"""
        if not self.db_connection:
            messagebox.showerror("Erro", "Sem conexão com o banco de dados.")
            return
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Buscar mesas ocupadas (com pedido EM_ANDAMENTO)
            cursor.execute("""
                SELECT DISTINCT m.*, p.id as pedido_id, COALESCE(p.total, 0) as total 
                FROM mesas m
                JOIN pedidos p ON m.id = p.mesa_id
                WHERE p.status = 'EM_ANDAMENTO'
                ORDER BY m.numero
            """)
            self.mesas_ocupadas = cursor.fetchall()
            
            # Buscar mesas livres
            cursor.execute("""
                SELECT * FROM mesas 
                WHERE LOWER(status) = 'livre' 
                ORDER BY numero
            """)
            self.mesas_livres = cursor.fetchall()
            
            # Atualizar as listas
            self._atualizar_listas()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mesas: {str(e)}")
        finally:
            cursor.close()
    
    def _atualizar_listas(self):
        """Atualiza as listas de mesas na interface"""
        try:
            # Salvar as seleções atuais
            selected_ocupada = next(iter(self.lista_ocupadas.curselection()), None)
            selected_livre = next(iter(self.lista_livres.curselection()), None)
            
            # Limpar listas
            self.lista_ocupadas.delete(0, 'end')
            self.lista_livres.delete(0, 'end')
            
            # Preencher lista de mesas ocupadas
            for mesa in self.mesas_ocupadas:
                valor = float(mesa.get('total', 0))
                texto = f"Mesa {mesa['numero']} - R$ {valor:.2f}"
                self.lista_ocupadas.insert('end', texto)
            
            # Preencher lista de mesas livres
            for mesa in self.mesas_livres:
                self.lista_livres.insert('end', f"Mesa {mesa['numero']}")
            
            # Restaurar seleções
            if selected_ocupada is not None and selected_ocupada < self.lista_ocupadas.size():
                self.lista_ocupadas.selection_set(selected_ocupada)
                self.lista_ocupadas.activate(selected_ocupada)
                
            if selected_livre is not None and selected_livre < self.lista_livres.size():
                self.lista_livres.selection_set(selected_livre)
                self.lista_livres.activate(selected_livre)
                
        except Exception as e:
            print(f"Erro ao atualizar listas: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar as listas de mesas: {str(e)}")
            
        # Atualizar estado do botão após carregar as listas
        self._atualizar_botao()
    
    def _on_select_ocupada(self, event):
        """Lida com a seleção de uma mesa ocupada"""
        try:
            # Obter a seleção atual
            selection = self.lista_ocupadas.curselection()
            if selection:
                index = selection[0]
                if 0 <= index < len(self.mesas_ocupadas):
                    self.mesa_origem = self.mesas_ocupadas[index]
                    # Atualizar botão
                    self._atualizar_botao()
        except Exception as e:
            print(f"Erro ao selecionar mesa ocupada: {str(e)}")
    
    def _on_select_livre(self, event):
        """Lida com a seleção de uma mesa livre"""
        try:
            # Obter a seleção atual
            selection = self.lista_livres.curselection()
            if selection:
                index = selection[0]
                if 0 <= index < len(self.mesas_livres):
                    self.mesa_destino = self.mesas_livres[index]
                    # Atualizar botão
                    self._atualizar_botao()
        except Exception as e:
            print(f"Erro ao selecionar mesa livre: {str(e)}")
    
    def _atualizar_botao(self):
        """Atualiza o estado do botão de transferir"""
        try:
            # Verificar se ambas as seleções foram feitas
            if hasattr(self, 'mesa_origem') and hasattr(self, 'mesa_destino'):
                if self.mesa_origem and self.mesa_destino:
                    self.btn_transferir['state'] = 'normal'
                    return
            
            # Se não, desabilitar o botão
            self.btn_transferir['state'] = 'disabled'
            
        except Exception as e:
            print(f"Erro ao atualizar botão: {str(e)}")
            self.btn_transferir['state'] = 'disabled'
    
    def _transferir(self):
        """Realiza a transferência do pedido entre as mesas"""
        if not self.mesa_origem or not self.mesa_destino:
            return
        
        # Confirmar a transferência
        confirmacao = messagebox.askyesno(
            "Confirmar Transferência",
            f"Transferir pedido da Mesa {self.mesa_origem['numero']} para a Mesa {self.mesa_destino['numero']}?"
        )
        
        if not confirmacao:
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Iniciar transação
            cursor.execute("START TRANSACTION")
            
            # 1. Atualizar o pedido para apontar para a nova mesa
            cursor.execute(
                "UPDATE pedidos SET mesa_id = %s WHERE id = %s",
                (self.mesa_destino['id'], self.mesa_origem['pedido_id'])
            )
            
            # 2. Atualizar o status da mesa de origem para livre
            cursor.execute(
                "UPDATE mesas SET status = 'livre', pedido_atual_id = NULL WHERE id = %s",
                (self.mesa_origem['id'],)
            )
            
            # 3. Atualizar o status da mesa de destino para ocupada
            cursor.execute(
                "UPDATE mesas SET status = 'ocupada', pedido_atual_id = %s WHERE id = %s",
                (self.mesa_origem['pedido_id'], self.mesa_destino['id'])
            )
            
            # Confirmar as alterações
            self.db_connection.commit()
            
            # Fechar a janela de transferência
            self._cancelar()
            
            # Recarregar a visualização de mesas
            if hasattr(self.controller, 'mostrar_conteudo_modulo'):
                self.controller.mostrar_conteudo_modulo('mesas', 'visualizar')
            
        except Exception as e:
            # Em caso de erro, desfaz as alterações
            self.db_connection.rollback()
            messagebox.showerror("Erro", f"Erro ao transferir pedido: {str(e)}")
        finally:
            cursor.close()
    
    def _cancelar(self):
        """Fecha a janela de transferência"""
        self.frame.master.destroy()
