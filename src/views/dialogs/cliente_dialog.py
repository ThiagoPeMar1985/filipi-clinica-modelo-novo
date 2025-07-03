"""
Diálogo para cadastro de clientes delivery.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import re
import datetime
import requests
from threading import Thread

class ClienteDialog(tk.Toplevel):
    """Diálogo para cadastro de clientes delivery."""
    
    def __init__(self, parent, controller, cliente_data=None, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.callback = kwargs.get('callback')
        
        # Configuração da janela
        self.title("Editar Cliente" if cliente_data else "Cadastrar Cliente")
        self.resizable(False, False)
        self.configure(bg="#f0f2f5")
        
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
        
        # Dados do cliente (se for edição) ou dicionário vazio (se for novo)
        self.cliente_data = cliente_data or {
            'nome': '',
            'telefone': '',
            'telefone2': '',
            'email': '',
            'endereco': '',
            'numero': '',
            'complemento': '',
            'bairro': '',
            'cidade': '',
            'uf': '',
            'cep': '',
            'ponto_referencia': '',
            'observacoes': '',
            'regiao_entrega_id': None
        }
        
        self._criar_widgets()
        self.center()
    
    def _criar_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="10", style="Card.TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Estilo para os campos
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Arial', 10))
        style.configure("TEntry", padding=5, font=('Arial', 10))
        style.configure("TButton", padding=5, font=('Arial', 10, 'bold'))
        
        # Título
        titulo_frame = tk.Frame(main_frame, bg=self.cores["fundo"])
        titulo_frame.grid(row=0, column=0, columnspan=3, sticky="we", pady=(0, 10))
        
        titulo = tk.Label(
            titulo_frame,
            text="CADASTRAR CLIENTE",
            font=('Arial', 12, 'bold'),
            bg=self.cores["fundo"],
            fg=self.cores["texto"],
            pady=8
        )
        titulo.pack(fill="x")
        
        # Nome
        ttk.Label(main_frame, text="Nome*").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.nome_entry = ttk.Entry(main_frame, width=40)
        nome = self.cliente_data.get('nome')
        if nome is not None and nome != '':
            self.nome_entry.insert(0, str(nome))
        self.nome_entry.grid(row=1, column=1, columnspan=3, sticky="we", padx=5, pady=5)
        
        # Telefone Principal
        ttk.Label(main_frame, text="Telefone*").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.telefone_entry = ttk.Entry(main_frame, width=20)
        telefone = self.cliente_data.get('telefone')
        if telefone is not None and telefone != '':
            self.telefone_entry.insert(0, str(telefone))
        self.telefone_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Telefone 2
        ttk.Label(main_frame, text="Telefone 2").grid(row=2, column=2, sticky="e", padx=5, pady=5)
        self.telefone2_entry = ttk.Entry(main_frame, width=20)
        telefone2 = self.cliente_data.get('telefone2')
        if telefone2 is not None and telefone2 != '':
            self.telefone2_entry.insert(0, str(telefone2))
        self.telefone2_entry.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        # Email
        ttk.Label(main_frame, text="Email").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=40)
        email = self.cliente_data.get('email')
        if email is not None and email != '':
            self.email_entry.insert(0, str(email))
        self.email_entry.grid(row=3, column=1, columnspan=3, sticky="we", padx=5, pady=5)
        
        # CEP
        ttk.Label(main_frame, text="CEP").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.cep_entry = ttk.Entry(main_frame, width=15)
        cep = self.cliente_data.get('cep')
        if cep is not None and cep != '':
            self.cep_entry.insert(0, str(cep))
        self.cep_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.cep_entry.bind('<FocusOut>', self._buscar_cep)
        
        # Rua
        ttk.Label(main_frame, text="Rua").grid(row=4, column=2, sticky="e", padx=5, pady=5)
        self.endereco_entry = ttk.Entry(main_frame, width=40)
        endereco = self.cliente_data.get('endereco')
        if endereco is not None and endereco != '':
            self.endereco_entry.insert(0, str(endereco))
        self.endereco_entry.grid(row=4, column=3, sticky="we", padx=5, pady=5)
        
        # Carregando imagem de loading
        self.loading_label = ttk.Label(main_frame, text="")
        self.loading_label.grid(row=4, column=4, padx=5, pady=5)
        
        # Número
        ttk.Label(main_frame, text="Número").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.numero_entry = ttk.Entry(main_frame, width=10)
        numero = self.cliente_data.get('numero')
        if numero is not None and numero != '':
            self.numero_entry.insert(0, str(numero))
        self.numero_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        
        # Bairro e Cidade
        ttk.Label(main_frame, text="Bairro").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.bairro_entry = ttk.Entry(main_frame, width=20)
        bairro = self.cliente_data.get('bairro')
        if bairro is not None and bairro != '':
            self.bairro_entry.insert(0, str(bairro))
        self.bairro_entry.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Cidade").grid(row=6, column=2, sticky="e", padx=5, pady=5)
        self.cidade_entry = ttk.Entry(main_frame, width=20)
        cidade = self.cliente_data.get('cidade')
        if cidade is not None and cidade != '':
            self.cidade_entry.insert(0, str(cidade))
        self.cidade_entry.grid(row=6, column=3, sticky="w", padx=5, pady=5)
        
        # UF e Complemento
        ttk.Label(main_frame, text="UF").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.uf_entry = ttk.Combobox(main_frame, width=5, values=["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        uf = self.cliente_data.get('uf')
        if uf is not None and uf != '':
            self.uf_entry.set(str(uf))
        self.uf_entry.grid(row=7, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(main_frame, text="Complemento").grid(row=7, column=2, sticky="e", padx=5, pady=5)
        self.complemento_entry = ttk.Entry(main_frame, width=20)
        complemento = self.cliente_data.get('complemento')
        if complemento is not None and complemento != '':
            self.complemento_entry.insert(0, str(complemento))
        self.complemento_entry.grid(row=7, column=3, sticky="w", padx=5, pady=5)
        
        # Ponto de Referência
        ttk.Label(main_frame, text="Ponto de Referência").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        self.ponto_referencia_entry = ttk.Entry(main_frame, width=40)
        ponto_referencia = self.cliente_data.get('ponto_referencia')
        if ponto_referencia is not None and ponto_referencia != '':
            self.ponto_referencia_entry.insert(0, str(ponto_referencia))
        self.ponto_referencia_entry.grid(row=8, column=1, columnspan=3, sticky="we", padx=5, pady=5)
        
        # Observações
        ttk.Label(main_frame, text="Observações").grid(row=9, column=0, sticky="ne", padx=5, pady=5)
        self.observacoes_text = tk.Text(main_frame, width=40, height=4)
        observacoes = self.cliente_data.get('observacoes')
        if observacoes is not None and observacoes != '':
            self.observacoes_text.insert('1.0', str(observacoes))
        self.observacoes_text.grid(row=9, column=1, columnspan=3, sticky="we", padx=5, pady=5)
        
        # Frame dos botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=10, column=0, columnspan=4, pady=15, sticky="e")
        
        # Botão Excluir (apenas para edição)
        if self.cliente_data.get('id'):
            btn_excluir = tk.Button(
                btn_frame,
                text="EXCLUIR",
                command=self._confirmar_exclusao,
                bg="#d32f2f",
                fg=self.cores["texto_claro"],
                bd=0,
                padx=15,
                pady=8,
                relief='flat',
                cursor='hand2',
                font=('Arial', 10, 'bold')
            )
            btn_excluir.pack(side="left", padx=5)
        
        # Frame para os botões da direita (Cancelar e Salvar)
        right_btn_frame = ttk.Frame(btn_frame)
        right_btn_frame.pack(side="right")
        
        # Botão Cancelar
        btn_cancelar = tk.Button(
            right_btn_frame,
            text="CANCELAR",
            command=self.destroy,
            bg=self.cores["alerta"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold')
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Botão Salvar
        btn_salvar = tk.Button(
            right_btn_frame,
            text="SALVAR",
            command=self._salvar_cliente,
            bg=self.cores["destaque"],
            fg=self.cores["texto_claro"],
            bd=0,
            padx=15,
            pady=8,
            relief='flat',
            cursor='hand2',
            font=('Arial', 10, 'bold')
        )
        btn_salvar.pack(side="right", padx=5)
        
        # Configurar foco
        self.nome_entry.focus()
        
        # Configurar atalhos
        self.bind('<Return>', lambda e: self._salvar_cliente())
        self.bind('<Escape>', lambda e: self.destroy())
    
    def _validar_campos(self):
        """Valida os campos obrigatórios."""
        # Obter os valores dos campos
        campos = {
            'nome': self.nome_entry.get().strip(),
            'telefone': self.telefone_entry.get().strip(),
            'telefone2': self.telefone2_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'endereco': self.endereco_entry.get().strip(),
            'numero': self.numero_entry.get().strip(),
            'complemento': self.complemento_entry.get().strip(),
            'bairro': self.bairro_entry.get().strip(),
            'cidade': self.cidade_entry.get().strip(),
            'uf': self.uf_entry.get().strip().upper(),
            'cep': self.cep_entry.get().strip(),
            'ponto_referencia': self.ponto_referencia_entry.get().strip(),
            'observacoes': self.observacoes_text.get('1.0', tk.END).strip()
        }
        
        # Remover caracteres não numéricos dos telefones
        telefone_limpo = re.sub(r'[^0-9]', '', campos['telefone'])
        telefone2_limpo = re.sub(r'[^0-9]', '', campos['telefone2']) if campos['telefone2'] else ''
        cep_limpo = re.sub(r'[^0-9]', '', campos['cep']) if campos['cep'] else ''
        
        # Validar telefone principal se preenchido
        if telefone_limpo and len(telefone_limpo) < 10:
            messagebox.showwarning("Telefone inválido", "O telefone principal deve conter pelo menos 10 dígitos.")
            self.telefone_entry.focus()
            return None
            
        # Validar telefone secundário se preenchido
        if telefone2_limpo and len(telefone2_limpo) < 10:
            messagebox.showwarning("Telefone inválido", "O telefone secundário deve conter pelo menos 10 dígitos.")
            self.telefone2_entry.focus()
            return None
            
        # Validar UF se preenchida
        if campos['uf'] and (len(campos['uf']) != 2 or not campos['uf'].isalpha()):
            messagebox.showwarning("UF inválida", "Informe a sigla do estado com 2 letras.")
            self.uf_entry.focus()
            return None
            
        # Validar CEP se preenchido
        if cep_limpo and len(cep_limpo) != 8:
            messagebox.showwarning("CEP inválido", "O CEP deve conter 8 dígitos.")
            self.cep_entry.focus()
            return None
            
        return {
            'nome': campos['nome'],
            'telefone': telefone_limpo if telefone_limpo else None,
            'telefone2': telefone2_limpo if telefone2_limpo else None,
            'email': campos['email'] if campos['email'] else None,
            'endereco': campos['endereco'],
            'numero': campos['numero'],
            'complemento': campos['complemento'] if campos['complemento'] else None,
            'bairro': campos['bairro'],
            'cidade': campos['cidade'],
            'uf': campos['uf'] if campos['uf'] else None,
            'cep': cep_limpo if cep_limpo else None,
            'ponto_referencia': campos['ponto_referencia'] if campos['ponto_referencia'] else None,
            'observacoes': campos['observacoes'] if campos['observacoes'] else None,
            'ativo': 1,
            'data_cadastro': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'regiao_entrega_id': None
        }
    
    def _salvar_cliente(self):
        """Salva os dados do cliente."""
        print("\n[DEBUG] Iniciando salvamento de cliente")
        dados = self._validar_campos()
        if not dados:
            print("[DEBUG] Validação falhou")
            return
            
        print("[DEBUG] Dados validados, chamando callback")
        if self.callback:
            self.callback(dados)
        else:
            print("[ERRO] Nenhum callback definido!")
        self.destroy()
    
    def _buscar_cep(self, event=None):
        """Busca o endereço a partir do CEP informado."""
        cep = self.cep_entry.get().strip().replace('-', '').replace('.', '')
        
        if len(cep) != 8 or not cep.isdigit():
            return
            
        self.loading_label.config(text="Buscando...")
        
        def buscar():
            try:
                response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
                if response.status_code == 200:
                    dados = response.json()
                    if 'erro' not in dados:
                        # Atualiza a interface na thread principal
                        self.after(0, self._preencher_campos, dados)
                    else:
                        self.after(0, self.loading_label.config, {"text": ""})
                else:
                    self.after(0, self.loading_label.config, {"text": ""})
            except Exception as e:
                print(f"Erro ao buscar CEP: {e}")
                self.after(0, self.loading_label.config, {"text": ""})
        
        # Executa a busca em uma thread separada para não travar a interface
        Thread(target=buscar, daemon=True).start()
    
    def _preencher_campos(self, dados):
        """Preenche os campos do formulário com os dados do CEP."""
        self.endereco_entry.delete(0, tk.END)
        self.endereco_entry.insert(0, dados.get('logradouro', ''))
        
        self.bairro_entry.delete(0, tk.END)
        self.bairro_entry.insert(0, dados.get('bairro', ''))
        
        self.cidade_entry.delete(0, tk.END)
        self.cidade_entry.insert(0, dados.get('localidade', ''))
        
        self.uf_entry.set(dados.get('uf', ''))
        
        # Mover o foco para o campo de número
        self.numero_entry.focus()
        
        self.loading_label.config(text="")
    
    def set_callback(self, callback):
        """Define a função de callback para quando o cliente for salvo."""
        self.callback = callback
    
    def _confirmar_exclusao(self):
        """Exibe um diálogo de confirmação antes de excluir o cliente."""
        if messagebox.askyesno(
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir permanentemente este cliente?\n\n"
            "Esta ação não pode ser desfeita!",
            icon='warning'
        ):
            self._excluir_cliente()
    
    def _excluir_cliente(self):
        """Exclui o cliente atual do banco de dados."""
        if not self.cliente_data.get('id'):
            messagebox.showerror("Erro", "Não é possível excluir um cliente que ainda não foi salvo.")
            return
            
        sucesso, mensagem = self.controller.excluir_cliente(self.cliente_data['id'])
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            if hasattr(self, 'on_delete') and callable(self.on_delete):
                self.on_delete()
            self.destroy()
        else:
            messagebox.showerror("Erro", mensagem)
    
    def set_on_delete(self, callback):
        """Define a função de callback para ser chamada após a exclusão do cliente."""
        self.on_delete = callback
    
    def center(self):
        """Centraliza o diálogo na tela."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')