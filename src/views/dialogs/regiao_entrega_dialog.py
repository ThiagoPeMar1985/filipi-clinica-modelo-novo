"""
Diálogo para cadastro de regiões de entrega.
"""
import tkinter as tk
from tkinter import ttk, messagebox

class RegiaoEntregaDialog(tk.Toplevel):
    """Diálogo para cadastro de regiões de entrega."""
    
    def __init__(self, parent, controller, regiao_data=None, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.callback = kwargs.get('callback')
        
        # Configuração da janela
        self.title("Editar Região de Entrega" if regiao_data else "Nova Região de Entrega")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")
        
        # Tornar a janela modal
        self.transient(parent)
        self.grab_set()
        
        # Garantir que a janela fique em primeiro plano
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
        
        # Cores do tema
        self.cores = {
            "primaria": "#4a6fa5",
            "secundaria": "#4a6fa5",
            "terciaria": "#333f50",
            "fundo": "#f0f2f5",
            "texto": "#000000",
            "texto_claro": "#ffffff",
            "destaque": "#4caf50",
            "alerta": "#f44336"
        }
        
        # Dados da região (se for edição) ou dicionário vazio (se for novo)
        self.regiao_data = regiao_data or {
            'nome': '',
            'taxa_entrega': '0.00',
            'tempo_medio_entrega': '30',
            'ativo': True
        }
        
        # Variáveis de controle
        self.var_nome = tk.StringVar(value=self.regiao_data['nome'])
        self.var_taxa = tk.StringVar(value=self.regiao_data['taxa_entrega'])
        self.var_tempo = tk.StringVar(value=str(self.regiao_data['tempo_medio_entrega']))
        self.var_ativo = tk.BooleanVar(value=bool(self.regiao_data['ativo']))
        
        self._criar_widgets()
        self._centralizar_janela()
        
        # Focar no primeiro campo
        self.entry_nome.focus_set()
    
    def _criar_widgets(self):
        """Cria os widgets do diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame do formulário
        form_frame = ttk.LabelFrame(main_frame, text="Dados da Região de Entrega")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Nome da Região
        ttk.Label(form_frame, text="Nome da Região:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.entry_nome = ttk.Entry(form_frame, textvariable=self.var_nome, width=40)
        self.entry_nome.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5, padx=5)
        
        # Taxa de Entrega
        ttk.Label(form_frame, text="Taxa de Entrega (R$):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entry_taxa = ttk.Entry(form_frame, textvariable=self.var_taxa, width=15)
        self.entry_taxa.grid(row=1, column=1, sticky="w", pady=5, padx=5)
        
        # Tempo Médio de Entrega
        ttk.Label(form_frame, text="Tempo Médio (min):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.entry_tempo = ttk.Spinbox(form_frame, from_=1, to=240, textvariable=self.var_tempo, width=10)
        self.entry_tempo.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        # Status (Ativo/Inativo)
        ttk.Label(form_frame, text="Status:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.chk_ativo = ttk.Checkbutton(form_frame, text="Ativo", variable=self.var_ativo)
        self.chk_ativo.grid(row=3, column=1, sticky="w", pady=5, padx=5)
        
        # Frame dos botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Botão Salvar
        btn_salvar = tk.Button(
            btn_frame,
            text="Salvar",
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self._salvar
        )
        btn_salvar.pack(side=tk.RIGHT, padx=5)
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            btn_frame,
            text="Cancelar",
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=5,
            relief='flat',
            cursor='hand2',
            command=self.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)
    
    def _salvar(self):
        """Valida e salva os dados da região de entrega."""
        # Validar campos obrigatórios
        if not self.var_nome.get().strip():
            messagebox.showerror("Erro", "O nome da região é obrigatório.", parent=self)
            self.entry_nome.focus_set()
            return
            
        try:
            # Validar e formatar a taxa
            taxa = float(self.var_taxa.get().replace(',', '.'))
            if taxa < 0:
                raise ValueError("A taxa não pode ser negativa.")
                
            # Validar e formatar o tempo
            tempo = int(self.var_tempo.get())
            if tempo <= 0:
                raise ValueError("O tempo médio deve ser maior que zero.")
                
            # Preparar dados para salvar
            dados = {
                'nome': self.var_nome.get().strip(),
                'taxa_entrega': f"{taxa:.2f}",
                'tempo_medio_entrega': tempo,
                'ativo': 1 if self.var_ativo.get() else 0
            }
            
            # Se for edição, adicionar o ID
            if 'id' in self.regiao_data:
                dados['id'] = self.regiao_data['id']
            
            # Chamar o callback com os dados
            if self.callback:
                self.callback(dados)
                
            # Fechar o diálogo
            self.destroy()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Dados inválidos: {str(e)}", parent=self)
    
    def _centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        largura = 500
        altura = 300
        
        # Obter a posição da janela pai
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (largura // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (altura // 2)
        else:
            # Se não houver janela pai, centraliza na tela
            x = (self.winfo_screenwidth() // 2) - (largura // 2)
            y = (self.winfo_screenheight() // 2) - (altura // 2)
        
        # Definir geometria e garantir que a janela esteja visível
        self.geometry(f'{largura}x{altura}+{x}+{y}')
        self.deiconify()  # Garante que a janela seja exibida
