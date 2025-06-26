"""
Módulo de Opções - Gerencia as opções personalizáveis dos produtos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os
import sys
from datetime import datetime

# Adicione o diretório raiz ao path para permitir importações absolutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Importações locais
from src.controllers.opcoes_controller import OpcoesController
from ..base_module import BaseModule

class OpcoesModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        super().__init__(parent, controller)
        
        # Inicializa o controlador
        self.controller = OpcoesController(self, db_connection)
        
        # Configura o frame principal
        self.frame.pack_propagate(False)
        
        # Frame para o conteúdo
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)
        
        # Variáveis de controle
        self.grupo_selecionado = None
        self.item_selecionado = None
        
        # Inicializa a interface
        self._inicializar_interface()
    
    def _inicializar_interface(self):
        """Inicializa a interface do módulo de opções."""
        # Limpa o frame de conteúdo
        for widget in self.conteudo_frame.winfo_children():
            widget.destroy()
        
        # Frame superior para os botões de ação
        frame_superior = tk.Frame(self.conteudo_frame, bg='#f0f2f5', padx=10, pady=10)
        frame_superior.pack(fill=tk.X)
        
        # Botões de ação
        btn_grupos = ttk.Button(
            frame_superior,
            text="Gerenciar Grupos",
            command=self._mostrar_gerenciador_grupos,
            style='Accent.TButton'
        )
        btn_grupos.pack(side=tk.LEFT, padx=5)
        
        btn_vincular = ttk.Button(
            frame_superior,
            text="Vincular a Produtos",
            command=self._mostrar_vinculacao_produtos,
            style='Accent.TButton'
        )
        btn_vincular.pack(side=tk.LEFT, padx=5)
        
        # Frame principal para o conteúdo dinâmico
        self.frame_principal = tk.Frame(self.conteudo_frame, bg='#f0f2f5', padx=10, pady=10)
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Mostra a tela inicial
        self._mostrar_tela_inicial()
    
    def _mostrar_tela_inicial(self):
        """Mostra a tela inicial do módulo de opções."""
        # Limpa o frame principal
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        # Título
        lbl_titulo = ttk.Label(
            self.frame_principal,
            text="Gerenciamento de Opções de Produtos",
            font=('Arial', 14, 'bold'),
            background='#f0f2f5'
        )
        lbl_titulo.pack(pady=20)
        
        # Instruções
        lbl_instrucoes = ttk.Label(
            self.frame_principal,
            text="Selecione uma das opções acima para começar.",
            font=('Arial', 10),
            background='#f0f2f5'
        )
        lbl_instrucoes.pack(pady=10)
        
        # Estatísticas (opcional)
        frame_estatisticas = tk.Frame(self.frame_principal, bg='#e9ecef', padx=20, pady=20)
        frame_estatisticas.pack(pady=20, fill=tk.X)
        
        # Aqui você pode adicionar estatísticas como:
        # - Total de grupos de opções
        # - Total de itens de opções
        # - Produtos com opções cadastradas
        # etc.
    
    def _mostrar_gerenciador_grupos(self):
        """Mostra o gerenciador de grupos de opções."""
        # Limpa o frame principal
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
        
        # Frame para os grupos (lado esquerdo)
        frame_grupos = tk.Frame(self.frame_principal, bg='#e9ecef', padx=10, pady=10, width=300)
        frame_grupos.pack(side=tk.LEFT, fill=tk.Y)
        frame_grupos.pack_propagate(False)
        
        # Título dos grupos
        ttk.Label(
            frame_grupos,
            text="Grupos de Opções",
            font=('Arial', 10, 'bold'),
            background='#e9ecef'
        ).pack(pady=(0, 10), anchor=tk.W)
        
        # Lista de grupos
        self.lista_grupos = ttk.Treeview(
            frame_grupos,
            columns=('id', 'nome'),
            show='headings',
            selectmode='browse',
            height=15
        )
        self.lista_grupos.heading('id', text='ID')
        self.lista_grupos.heading('nome', text='Nome')
        self.lista_grupos.column('id', width=40, anchor=tk.CENTER)
        self.lista_grupos.column('nome', width=200, anchor=tk.W)
        self.lista_grupos.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem
        scrollbar_y = ttk.Scrollbar(frame_grupos, orient=tk.VERTICAL, command=self.lista_grupos.yview)
        self.lista_grupos.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação para grupos
        frame_botoes_grupo = tk.Frame(frame_grupos, bg='#e9ecef', pady=5)
        frame_botoes_grupo.pack(fill=tk.X)
        
        btn_novo_grupo = ttk.Button(
            frame_botoes_grupo,
            text="Novo Grupo",
            command=self._criar_novo_grupo,
            style='Accent.TButton',
            width=15
        )
        btn_novo_grupo.pack(side=tk.LEFT, padx=2)
        
        btn_editar_grupo = ttk.Button(
            frame_botoes_grupo,
            text="Editar",
            command=self._editar_grupo,
            width=10
        )
        btn_editar_grupo.pack(side=tk.LEFT, padx=2)
        
        btn_excluir_grupo = ttk.Button(
            frame_botoes_grupo,
            text="Excluir",
            command=self._excluir_grupo,
            width=10
        )
        btn_excluir_grupo.pack(side=tk.LEFT, padx=2)
        
        # Frame para os itens (lado direito)
        frame_itens = tk.Frame(self.frame_principal, bg='#f8f9fa', padx=10, pady=10)
        frame_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Título dos itens
        ttk.Label(
            frame_itens,
            text="Itens do Grupo",
            font=('Arial', 10, 'bold'),
            background='#f8f9fa'
        ).pack(pady=(0, 10), anchor=tk.W)
        
        # Lista de itens
        self.lista_itens = ttk.Treeview(
            frame_itens,
            columns=('id', 'nome', 'preco'),
            show='headings',
            selectmode='browse',
            height=15
        )
        self.lista_itens.heading('id', text='ID')
        self.lista_itens.heading('nome', text='Nome')
        self.lista_itens.heading('preco', text='Preço Adicional')
        self.lista_itens.column('id', width=40, anchor=tk.CENTER)
        self.lista_itens.column('nome', width=200, anchor=tk.W)
        self.lista_itens.column('preco', width=100, anchor=tk.E)
        self.lista_itens.pack(fill=tk.BOTH, expand=True)
        
        # Barra de rolagem
        scrollbar_y = ttk.Scrollbar(frame_itens, orient=tk.VERTICAL, command=self.lista_itens.yview)
        self.lista_itens.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação para itens
        frame_botoes_item = tk.Frame(frame_itens, bg='#f8f9fa', pady=5)
        frame_botoes_item.pack(fill=tk.X)
        
        btn_novo_item = ttk.Button(
            frame_botoes_item,
            text="Novo Item",
            command=self._criar_novo_item,
            style='Accent.TButton',
            width=15
        )
        btn_novo_item.pack(side=tk.LEFT, padx=2)
        
        btn_editar_item = ttk.Button(
            frame_botoes_item,
            text="Editar",
            command=self._editar_item,
            width=10
        )
        btn_editar_item.pack(side=tk.LEFT, padx=2)
        
        btn_excluir_item = ttk.Button(
            frame_botoes_item,
            text="Excluir",
            command=self._excluir_item,
            width=10
        )
        btn_excluir_item.pack(side=tk.LEFT, padx=2)
        
        # Carrega os grupos
        self._carregar_grupos()
        
        # Configura os eventos
        self.lista_grupos.bind('<<TreeviewSelect>>', self._selecionar_grupo)
    
    def _carregar_grupos(self):
        """Carrega a lista de grupos de opções."""
        # Limpa a lista atual
        for item in self.lista_grupos.get_children():
            self.lista_grupos.delete(item)
        
        # Busca os grupos no banco de dados
        grupos = self.controller.listar_grupos()
        
        # Preenche a lista
        for grupo in grupos:
            self.lista_grupos.insert('', 'end', values=(grupo['id'], grupo['nome']))
        
        # Limpa a lista de itens
        self._limpar_lista_itens()
    
    def _limpar_lista_itens(self):
        """Limpa a lista de itens."""
        for item in self.lista_itens.get_children():
            self.lista_itens.delete(item)
    
    def _selecionar_grupo(self, event):
        """Carrega os itens do grupo selecionado."""
        # Obtém o item selecionado
        selecionado = self.lista_grupos.selection()
        
        if not selecionado:
            self.grupo_selecionado = None
            self._limpar_lista_itens()
            return
        
        # Obtém os dados do grupo
        item = self.lista_grupos.item(selecionado[0])
        grupo_id = item['values'][0]
        self.grupo_selecionado = grupo_id
        
        # Limpa a lista de itens
        self._limpar_lista_itens()
        
        # Busca os itens do grupo no banco de dados
        itens = self.controller.listar_itens_por_grupo(grupo_id)
        
        # Preenche a lista de itens
        for item in itens:
            self.lista_itens.insert('', 'end', values=(
                item['id'],
                item['nome'],
                f"R$ {item['preco_adicional']:.2f}" if item['preco_adicional'] else ""
            ))
    
    def _criar_novo_grupo(self):
        """Abre o formulário para criar um novo grupo."""
        self._abrir_formulario_grupo()
    
    def _editar_grupo(self):
        """Abre o formulário para editar o grupo selecionado."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para editar.")
            return
        
        self._abrir_formulario_grupo(self.grupo_selecionado)
    
    def _excluir_grupo(self):
        """Exclui o grupo selecionado."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para excluir.")
            return
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este grupo?"):
            return
        
        # Exclui o grupo
        if self.controller.excluir_grupo(self.grupo_selecionado):
            messagebox.showinfo("Sucesso", "Grupo excluído com sucesso!")
            self._carregar_grupos()
        else:
            messagebox.showerror("Erro", "Não foi possível excluir o grupo.")
    
    def _criar_novo_item(self):
        """Abre o formulário para criar um novo item."""
        if not self.grupo_selecionado:
            messagebox.showwarning("Aviso", "Selecione um grupo para adicionar itens.")
            return
        
        self._abrir_formulario_item()
    
    def _editar_item(self):
        """Abre o formulário para editar o item selecionado."""
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para editar.")
            return
        
        self._abrir_formulario_item(self.item_selecionado)
    
    def _excluir_item(self):
        """Exclui o item selecionado."""
        if not self.item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para excluir.")
            return
        
        # Confirma a exclusão
        if not messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este item?"):
            return
        
        # Exclui o item
        if self.controller.excluir_item(self.item_selecionado):
            messagebox.showinfo("Sucesso", "Item excluído com sucesso!")
            self._selecionar_grupo(None)  # Recarrega os itens
        else:
            messagebox.showerror("Erro", "Não foi possível excluir o item.")
    
    def _abrir_formulario_grupo(self, grupo_id=None):
        """Abre o formulário de grupo."""
        # Implementar a abertura do formulário de grupo
        pass
    
    def _abrir_formulario_item(self, item_id=None):
        """Abre o formulário de item."""
        # Implementar a abertura do formulário de item
        pass
    
    def _mostrar_vinculacao_produtos(self):
        """Mostra a tela de vinculação de opções a produtos."""
        # Implementar a tela de vinculação de opções a produtos
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = OpcoesModule(root, None)
    root.mainloop()
