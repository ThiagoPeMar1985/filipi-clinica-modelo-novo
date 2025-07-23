"""
Utilitários para manipulação e exibição de produtos no sistema PDV Aquarius.
Este módulo contém funções reutilizáveis para trabalhar com produtos em diferentes partes do sistema.
"""
import tkinter as tk
from tkinter import messagebox

def obter_tipos_produtos(db_connection):
    """
    Obtém os tipos de produtos do banco de dados.
    
    Args:
        db_connection: Conexão com o banco de dados
        
    Returns:
        list: Lista de dicionários com os tipos de produtos
    """
    tipos = []
    try:
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tipos_produtos ORDER BY nome")
        tipos = cursor.fetchall()
        cursor.close()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar tipos de produtos: {str(e)}")
        print(f"Erro detalhado: {e}")
        import traceback
        traceback.print_exc()
    return tipos

def criar_botoes_tipos_produtos(parent_frame, tipos_produtos, cores, callback_func, botoes_por_linha=5, editar_callback=None):  # Alterado para 5 botões por linha por padrão
    """
    Cria botões para os tipos de produtos em um frame pai.
    
    Args:
        parent_frame: Frame onde os botões serão criados
        tipos_produtos: Lista de dicionários com os tipos de produtos
        cores: Dicionário com as cores do sistema
        callback_func: Função a ser chamada quando um botão for clicado
        botoes_por_linha: Número máximo de botões por linha
        editar_callback: Função a ser chamada quando o botão de editar for clicado
        
    Returns:
        None
    """
    # Limpar o frame antes de adicionar novos botões
    for widget in parent_frame.winfo_children():
        widget.destroy()
    
    # Frame principal para conter os botões e o botão de edição
    main_frame = tk.Frame(parent_frame, bg=cores.get("fundo", "#f0f2f5"))
    main_frame.pack(fill="both", expand=True)
        
    # Frame para os botões de tipos
    tipos_frame = tk.Frame(main_frame, bg=cores.get("fundo", "#f0f2f5"))
    tipos_frame.pack(fill="both", expand=True)
    
    # Se não houver tipos cadastrados, exibir mensagem
    if not tipos_produtos:
        label = tk.Label(
            tipos_frame,
            text="Nenhum tipo de produto cadastrado.",
            font=("Arial", 12),
            bg=cores.get("fundo", "#f0f2f5"),
            fg=cores.get("texto_escuro", "#2c3e50")
        )
        label.pack(pady=50)
        return
    
    # Configurações para os botões
    botao_width = 150  # Largura fixa para os botões
    botao_height = 40  # Altura fixa para os botões
    padding = 5  # Espaçamento entre botões
    
    # Criar frames para cada linha de botões
    linha_atual = 0
    coluna_atual = 0
    linha_frame = None
    
    for i, tipo in enumerate(tipos_produtos):
        # Se estamos no início de uma nova linha ou é o primeiro botão
        if coluna_atual == 0:
            linha_frame = tk.Frame(tipos_frame, bg=cores.get("fundo", "#f0f2f5"))
            linha_frame.pack(fill="x", pady=padding)
        
        # Frame para o botão (para controlar tamanho)
        botao_frame = tk.Frame(
            linha_frame,
            width=botao_width,
            height=botao_height,
            bg=cores.get("fundo", "#f0f2f5")
        )
        botao_frame.pack(side="left", padx=padding)
        botao_frame.pack_propagate(False)  # Impede que o conteúdo altere o tamanho do frame
        
        # Botão do tipo de produto
        botao = tk.Button(
            botao_frame,
            text=tipo["nome"],
            bg=cores.get("primaria", "#3498db"),
            fg=cores.get("texto_claro", "#ffffff"),
            font=("Arial", 10, "bold"),
            bd=0,
            relief="flat",
            cursor="hand2",
            command=lambda t=tipo: callback_func(t)
        )
        botao.pack(fill="both", expand=True)
        
        # Atualizar posição para o próximo botão
        coluna_atual += 1
        
        # Se completou a linha, reinicia para a próxima
        if coluna_atual >= botoes_por_linha:
            coluna_atual = 0
            linha_atual += 1
