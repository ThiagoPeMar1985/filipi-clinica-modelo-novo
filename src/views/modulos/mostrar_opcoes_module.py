"""
Módulo para exibição de opções de produtos.
Centraliza a lógica de exibição de opções que é usada em várias partes do sistema.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Callable, Any, Optional
from tkinter import Button


class MostrarOpcoesModule:
    def __init__(self, master, root_window, callback_confirmar: Callable, db_connection=None):
        """
        Inicializa o módulo de opções.
        
        Args:
            master: Widget pai
            root_window: Janela principal da aplicação
            callback_confirmar: Função chamada quando o usuário confirma as opções
            db_connection: Conexão com o banco de dados
        """
        self.master = master
        self.root = root_window
        self.callback_confirmar = callback_confirmar
        self.db_connection = db_connection
        self.janela_opcoes = None
        self.selecoes_opcoes = {}
        
        # Inicializa o controlador de opções
        self._inicializar_opcoes_controller()
    
    def _inicializar_opcoes_controller(self):
        """Inicializa o controlador de opções com a conexão fornecida"""
        if not self.db_connection:
            return
            
        try:
            from controllers.opcoes_controller import OpcoesController
            self.opcoes_controller = OpcoesController(db_connection=self.db_connection)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível inicializar o controlador de opções: {str(e)}")
    
    def set_db_connection(self, db_connection):
        """Define a conexão com o banco de dados"""
        self.db_connection = db_connection
        self._inicializar_opcoes_controller()
    
    def mostrar_opcoes(self, produto: Dict) -> None:
        """Mostra as opções de um produto"""
        if not hasattr(self, 'opcoes_controller') or not self.opcoes_controller:
            messagebox.showerror("Erro", "Controlador de opções não inicializado.")
            return
        
        try:
            # Primeiro tenta buscar as opções completas
            opcoes = self.opcoes_controller.listar_opcoes_por_produto(produto['id'])
            
            # Se não retornar dados, usa o método antigo
            if not opcoes:
                # Buscar grupos de opções
                grupos_opcoes = self.opcoes_controller.listar_grupos_por_produto(produto['id'])
                
                if not grupos_opcoes:
                    messagebox.showinfo("Informação", "Este produto não possui opções configuradas.")
                    return
                
                # Processa os grupos para o formato esperado
                opcoes = {}
                for grupo in grupos_opcoes:
                    itens = self.opcoes_controller.listar_itens_por_grupo(grupo['id'], ativo=True)
                    
                    # Determinar o tipo de seleção baseado nas configurações
                    if grupo.get('selecao_maxima', 1) > 1:
                        tipo = 'selecao_multipla'
                    elif any(item.get('tipo') == 'texto_livre' for item in itens):
                        tipo = 'texto_livre'
                    else:
                        tipo = 'selecao_unica'
                    
                    opcoes[grupo['id']] = {
                        'id': grupo['id'],
                        'nome': grupo['nome'],
                        'descricao': grupo.get('descricao', ''),
                        'obrigatorio': bool(grupo.get('obrigatorio', False)),
                        'selecao_minima': grupo.get('selecao_minima', 0),
                        'selecao_maxima': grupo.get('selecao_maxima', 1),
                        'ordem': grupo.get('ordem', 0),
                        'tipo': tipo,
                        'itens': itens
                    }
            
            # Verifica se há opções após o processamento
            if not opcoes:
                messagebox.showinfo("Informação", "Este produto não possui opções configuradas.")
                return
                
            # Debug: Mostrar a estrutura das opções no console
            print("Estrutura das opções:", opcoes)
                
            # Adiciona as opções ao produto e exibe o diálogo
            produto['opcoes'] = opcoes
            self._mostrar_dialogo_opcoes(produto)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar opções: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _mostrar_dialogo_opcoes(self, produto):
        # Criar janela de diálogo
        self.dialogo = tk.Toplevel(self.root)
        self.dialogo.title(f"Opções para {produto.get('nome', 'Produto')}")
        self.dialogo.geometry("600x500")
        self.dialogo.transient(self.root)
        self.dialogo.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(self.dialogo, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Frame para as opções com barra de rolagem
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Dicionário para armazenar as seleções
        self.selecoes_opcoes = {}
        
        # Para cada grupo de opções
        for grupo_id, grupo in produto.get('opcoes', {}).items():
            # Criar frame para o grupo
            grupo_frame = ttk.LabelFrame(scrollable_frame, text=grupo.get('nome', 'Opções'), padding="10")
            grupo_frame.pack(fill="x", pady=5, padx=5, expand=True, anchor="nw")
            
            # Inicializar lista de seleções para este grupo
            self.selecoes_opcoes[grupo_id] = {
                'tipo': 'grupo',
                'itens': {},
                'obrigatorio': grupo.get('obrigatorio', False)
            }
            
            # Processar cada item do grupo
            for item in grupo.get('itens', []):
                item_id = item.get('id')
                
                # Se for um item de texto livre
                if item.get('tipo') == 'texto_livre':
                    item_frame = ttk.Frame(grupo_frame)
                    item_frame.pack(fill="x", pady=2, expand=True)
                    
                    # Criar variável para o checkbox
                    check_var = tk.BooleanVar(value=False)  # Já vem marcado por padrão
                    # Criar variável para o texto
                    text_var = tk.StringVar()
                    
                    # Armazenar ambas as variáveis
                    self.selecoes_opcoes[grupo_id]['itens'][item_id] = {
                        'var': text_var,
                        'check_var': check_var,
                        'tipo': 'texto_livre'
                    }
                    
                    # Criar checkbox
                    cb = ttk.Checkbutton(
                        item_frame, 
                        text=item.get('nome', 'Observações:'),
                        variable=check_var
                    )
                    cb.pack(side="left", padx=(0, 5))
                    
                    # Criar campo de entrada
                    entry = ttk.Entry(item_frame, textvariable=text_var, width=30)
                    entry.pack(side="left", fill="x", expand=True)
                    
                    # Se for obrigatório, adicionar asterisco e forçar seleção
                    if grupo.get('obrigatorio', False):
                        ttk.Label(item_frame, text="*", 
                                foreground="red", font=('Arial', 10, 'bold')).pack(side="left", padx=2)
                        check_var.set(True)  # Marca como selecionado
                        entry.config(state=tk.NORMAL)
                    else:
                        # Estado inicial
                        entry.config(state=tk.DISABLED)
    
                        # Função para alternar o estado - versão corrigida
                        def criar_toggle_entry(entry_ref, check_var_ref, text_var_ref):
                            def toggle_entry(*args):
                                if check_var_ref.get():
                                    entry_ref.config(state=tk.NORMAL)
                                else:
                                    entry_ref.config(state=tk.DISABLED)
                                    text_var_ref.set("")
                            return toggle_entry
                        
                        # Criar a função com as referências corretas
                        toggle_func = criar_toggle_entry(entry, check_var, text_var)
                        
                        # Configurar o trace
                        check_var.trace_add('write', toggle_func)
                
                # Se for um item de seleção simples
                else:
                    # Criar frame para o item
                    item_frame = ttk.Frame(grupo_frame)
                    item_frame.pack(fill="x", pady=2, expand=True)
                    
                    # Criar variável para armazenar a seleção
                    var = tk.BooleanVar()
                    self.selecoes_opcoes[grupo_id]['itens'][item_id] = {
                        'var': var,
                        'tipo': 'opcao_simples'
                    }
                    
                    # Criar checkbox
                    cb = ttk.Checkbutton(
                        item_frame, 
                        text=f"{item.get('nome')} (+R$ {float(item.get('preco_adicional', 0)):.2f})",
                        variable=var
                    )
                    cb.pack(anchor="w")
                    
                    # Adicionar descrição se existir
                    if item.get('descricao'):
                        ttk.Label(
                            item_frame, 
                            text=f"  {item.get('descricao')}",
                            style='Small.TLabel'
                        ).pack(anchor="w", padx=20)

        # Frame para os botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(fill="x", pady=10)
        
        # Botão de confirmar (mantendo o estilo original)
        Button(
            botoes_frame, 
            text="  Confirmar  ",
            command=lambda: self._processar_confirmacao(produto),
            bg='#4CAF50',  # Verde
            fg='white',     # Texto branco
            font=('Arial', 10, 'bold'),
            relief='flat',  # Remove o efeito 3D
            bd=0,           # Remove a borda
            padx=10,        # Espaçamento interno horizontal
            pady=5          # Espaçamento interno vertical
        ).pack(side="right", padx=10)

        # Ajustar o tamanho da janela
        self.dialogo.update_idletasks()
        width = 600
        height = min(600, self.dialogo.winfo_reqheight() + 100)  # Altura máxima de 600px
        x = (self.dialogo.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialogo.winfo_screenheight() // 2) - (height // 2)
        self.dialogo.geometry(f"{width}x{height}+{x}+{y}")
    
        # Focar na janela
        self.dialogo.focus_set()
    
    def _processar_confirmacao(self, produto):
        """Processa a confirmação das opções selecionadas"""
        try:
            opcoes_selecionadas = []
            grupos_obrigatorios = []
            
            # Verificar grupos obrigatórios
            for grupo_id, grupo in produto.get('opcoes', {}).items():
                if grupo.get('obrigatorio', False):
                    grupos_obrigatorios.append(grupo_id)
            
            # Processar cada grupo
            for grupo_id, selecao in self.selecoes_opcoes.items():
                grupo_info = produto.get('opcoes', {}).get(grupo_id, {})
                
                if 'itens' in selecao:
                    for item_id, item_data in selecao['itens'].items():
                        # Texto livre
                        if item_data.get('tipo') == 'texto_livre' and item_data['check_var'].get():
                            texto = item_data['var'].get().strip()
                            if texto:
                                opcoes_selecionadas.append({
                                    'id': item_id,
                                    'tipo': 'texto_livre',
                                    'valor': texto,
                                    'nome': texto,
                                    'grupo_id': grupo_id,
                                    'grupo_nome': grupo_info.get('nome', 'Observações')
                                })
                        
                        # Outros tipos de opções
                        elif item_data.get('tipo') == 'opcao_simples' and item_data['var'].get():
                            for item_original in grupo_info.get('itens', []):
                                if item_original.get('id') == item_id:
                                    opcoes_selecionadas.append({
                                        'id': item_id,
                                        'tipo': 'opcao_simples',
                                        'nome': item_original.get('nome', 'Item'),
                                        'preco_adicional': float(item_original.get('preco_adicional', 0)),
                                        'grupo_id': grupo_id,
                                        'grupo_nome': grupo_info.get('nome', 'Opções')
                                    })
                                    break
            
            # Resto do código (fechar diálogo e retornar)
            print(f"\n=== Opções selecionadas para confirmação ===")
            print(f"Total de opções: {len(opcoes_selecionadas)}")
            for i, opcao in enumerate(opcoes_selecionadas, 1):
                print(f"Opção {i}: {opcao}")
            
            if hasattr(self, 'dialogo') and self.dialogo.winfo_exists():
                self.dialogo.destroy()
            
            if hasattr(self, 'callback_confirmar') and self.callback_confirmar:
                self.callback_confirmar(produto, opcoes_selecionadas)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao processar opções: {str(e)}")