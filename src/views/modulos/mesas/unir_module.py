"""
Módulo para unir mesas do restaurante.
Permite unir pedidos de duas mesas em uma única conta.
"""
import tkinter as tk
from tkinter import ttk, messagebox, BOTH, YES, END
from typing import List, Dict, Any
from src.controllers.mesas_controller import MesasController


class UnirMesasModule:
    def __init__(self, parent, controller, db_connection=None):
        """
        Inicializa o módulo de unir mesas.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
            db_connection: Conexão com o banco de dados (opcional)
        """
        self.parent = parent
        self.controller = controller
        self.db_connection = db_connection or getattr(controller, 'db_connection', None)
        self.frame = ttk.Frame(parent)
        
        # Inicializar o controlador de mesas com a conexão
        self.mesas_controller = MesasController(db_connection=self.db_connection)
        
        # Configurar a interface
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.frame, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # Frame para o título no topo
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        # Título
        ttk.Label(
            title_frame,
            text=" Unir Mesas",
            font=('Arial', 16, 'bold')
        ).pack(side='left', anchor='w')
        
        # Criar um frame horizontal para organizar os elementos
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=YES)
        
        # Frame para os botões (lado esquerdo)
        left_frame = ttk.Frame(content_frame, padding=(0, 0, 10, 0))
        left_frame.pack(side='left', fill='y')
        
        # Estilo do botão
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 15
        }
        
        # Botão Unir Mesas
        btn_unir = tk.Button(
            left_frame,
            text=" Unir Mesas",
            **btn_style,
            command=self.unir_mesas
        )
        btn_unir.pack(pady=5, fill='x')
        
        # Adicionar mais botões ou widgets à esquerda, se necessário
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Tabela de mesas (lado direito)
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side='right', fill=BOTH, expand=YES)
        
        # Criar a tabela no frame direito
        self.criar_tabela_mesas(right_frame)
    
    def criar_tabela_mesas(self, parent):
        """Cria a tabela de mesas"""
        # Frame para a tabela com barra de rolagem
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=BOTH, expand=YES)
        
        # Barra de rolagem
        scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        scroll_y.pack(side='right', fill='y')
        
        # Criar a tabela
        colunas = ('selecao', 'numero', 'status', 'capacidade', 'valor')
        self.tabela = ttk.Treeview(
            table_frame,
            columns=colunas,
            show='headings',
            yscrollcommand=scroll_y.set,
            selectmode='extended',
            height=15
        )
        
        # Configurar colunas
        self.tabela.heading('selecao', text='Selecionar')
        self.tabela.heading('numero', text='Número')
        self.tabela.heading('status', text='Status')
        self.tabela.heading('capacidade', text='Capacidade')
        self.tabela.heading('valor', text='Valor')
        
        # Ajustar largura das colunas
        self.tabela.column('selecao', width=80, anchor='center')
        self.tabela.column('numero', width=80, anchor='center')
        self.tabela.column('status', width=120, anchor='center')
        self.tabela.column('capacidade', width=100, anchor='center')
        self.tabela.column('valor', width=100, anchor='center')
        
        # Adicionar checkboxes para seleção
        self.tabela.tag_configure('selected', background='#e6f3ff')
        
        # Configurar barra de rolagem
        scroll_y.config(command=self.tabela.yview)
        
        # Empacotar tabela
        self.tabela.pack(fill=BOTH, expand=YES)
        
        # Carregar dados das mesas
        self.carregar_mesas()
    
    def carregar_mesas(self):
        """Carrega as mesas do banco de dados"""
        
        # Limpar tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        try:
            # Carregar as mesas usando o método correto do controller

            if self.mesas_controller.carregar_mesas():

                
                # Verificar se há mesas
                if not self.mesas_controller.mesas:

                    messagebox.showinfo("Informação", "Nenhuma mesa encontrada no banco de dados.")
                    return
                    
                # Preencher tabela com as mesas carregadas
                for mesa in self.mesas_controller.mesas:

                    status = "Ocupada" if mesa.get('status') == 'OCUPADA' else "Livre"
                    
                    # Tratar o valor total corretamente
                    valor_total = mesa.get('valor_total', 0)
                    if valor_total is None:
                        valor_total = 0
                    valor = f"R$ {float(valor_total):.2f}"
                    
                    self.tabela.insert('', END, values=(
                        '☐',  # Checkbox vazio
                        mesa.get('numero', ''),
                        status,
                        mesa.get('capacidade', ''),
                        valor
                    ), tags=('unselected',))
                                
                # Configurar evento de clique para seleção
                self.tabela.bind('<Button-1>', self.on_click)

            else:

                messagebox.showwarning("Aviso", "Não foi possível carregar as mesas.")
                
        except Exception as e:
            import traceback
            traceback.print_exc()  # Isso mostrará o traceback completo no console
            messagebox.showerror("Erro", f"Falha ao carregar mesas: {str(e)}")
        
    def on_click(self, event):
        """Manipula o clique na tabela para selecionar/desselecionar mesas"""
        region = self.tabela.identify_region(event.x, event.y)
        if region != 'cell':
            return
            
        item = self.tabela.identify_row(event.y)
        column = self.tabela.identify_column(event.x)  # Corrigido: usando event.x em vez de event.y
        
        # Se clicou na coluna de seleção
        if column == '#1':
            values = self.tabela.item(item, 'values')
            
            # Verificar se values tem elementos suficientes
            if not values or len(values) <= 1:  # Ajustado o índice para 1 já que o primeiro item é o checkbox
                return
                
            # Converter para lista para poder modificar
            values = list(values)
            
            # Alternar entre selecionado e não selecionado
            if values[0] == '☐':
                values[0] = '☑'
                self.tabela.item(item, tags=('selected',), values=values)
            else:
                values[0] = '☐'
                self.tabela.item(item, tags=('unselected',), values=values)
    
    def unir_mesas(self):
        """Executa a ação de unir as mesas selecionadas"""
        # Obter itens selecionados na tabela
        mesas_selecionadas = []
        for item in self.tabela.get_children():
            values = self.tabela.item(item, 'values')
            if values and values[0] == '☑':  # Se a mesa está selecionada
                numero_mesa = values[1]  # Número da mesa
                mesas_selecionadas.append(numero_mesa)
        
        # Validar seleção
        if len(mesas_selecionadas) < 2:
            messagebox.showwarning("Aviso", "Selecione pelo menos 2 mesas para unir.")
            return

        # Criar diálogo para selecionar a mesa principal
        dialog = tk.Toplevel(self.frame)
        dialog.title("Selecionar Mesa Principal")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.frame)  # Define como janela filha
        dialog.grab_set()  # Torna a janela modal
        dialog.configure(bg='#f0f0f0')

        # Centralizar a janela
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'400x300+{x}+{y}')

        # Frame principal
        main_frame = tk.Frame(dialog, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)

        # Título
        tk.Label(
            main_frame, 
            text="Selecione a mesa que permanecerá ativa:",
            font=('Arial', 12, 'bold'),
            bg='#f0f0f0'
        ).pack(pady=(0, 20))

        # Frame para os botões
        frame_botoes = tk.Frame(main_frame, bg='#f0f0f0')
        frame_botoes.pack(fill='both', expand=True)

        # Variável para armazenar a escolha
        mesa_escolhida = tk.StringVar()

        # Estilo dos botões
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 10,
            'relief': 'flat',
            'cursor': 'hand2',
            'activebackground': '#3a5a80',
            'activeforeground': 'white'
        }

        # Criar botões para cada mesa
        for mesa in mesas_selecionadas:
            btn = tk.Button(
                frame_botoes,
                text=f"Mesa {mesa}",
                **btn_style,
                command=lambda m=mesa: (mesa_escolhida.set(m), dialog.destroy())
            )
            btn.pack(pady=5, fill='x')

        # Estilo do botão cancelar
        btn_cancelar_style = btn_style.copy()
        btn_cancelar_style['bg'] = '#f44336'
        
        # Botão cancelar
        tk.Button(
            main_frame,
            text="Cancelar",
            command=dialog.destroy,
            **btn_cancelar_style
        ).pack(pady=(20, 0), fill='x')

        # Aguardar fechamento da janela
        self.frame.wait_window(dialog)

        # Se o usuário não escolheu nenhuma mesa, cancelar
        if not mesa_escolhida.get():
            return

        # Obter a mesa principal e as outras mesas
        mesa_principal = mesa_escolhida.get()
        mesas_para_unir = [m for m in mesas_selecionadas if m != mesa_principal]

        # Confirmar ação
        if messagebox.askyesno(
            "Confirmar",
            f"Deseja mesmo unir as mesas {', '.join(mesas_para_unir)} para a Mesa {mesa_principal}?"
        ):
            try:
                if self.mesas_controller.unir_mesas(int(mesa_principal), [int(m) for m in mesas_para_unir]):
                    messagebox.showinfo("Sucesso", "Mesas unidas com sucesso!")
                    self.carregar_mesas()  # Atualizar a lista
                else:
                    messagebox.showerror("Erro", "Não foi possível unir as mesas.")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao unir as mesas: {str(e)}")
        
    def show(self):
        """Retorna o frame principal do módulo"""
        return self.frame