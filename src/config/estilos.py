"""
Módulo de configuração de estilos e temas do sistema PDV
"""

# Cores do tema
CORES = {
    "primaria": "#4a6fa5",      # Azul médio
    "secundaria": "#28b5f4",    # Azul claro
    "terciaria": "#333f50",     # Azul escuro
    "fundo": "#f0f2f5",         # Cinza muito claro
    "fundo_conteudo": "#ffffff", # Branco
    "texto": "#000000",         # Preto 
    "texto_claro": "#ffffff",   # Branco
    "destaque": "#4caf50",      # Verde
    "alerta": "#f44336",        # Vermelho
    "bordo": "#e0e0e0",         # Cinza claro
    "sucesso": "#4caf50",       # Verde
    "atencao": "#ff9800",       # Laranja
}

# Fontes
FONTES = {
    "titulo": ("Arial", 16, "bold"),
    "subtitulo": ("Arial", 14, "bold"),
    "normal": ("Arial", 12),
    "pequena": ("Arial", 10),
    "grande": ("Arial", 18, "bold"),
}

# Estilos de botões
ESTILOS_BOTAO = {
    # Botão padrão (Azul)
    "padrao": {
        "bg": CORES["primaria"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
        "activebackground": CORES["secundaria"],
        "activeforeground": CORES["texto_claro"],
        "cursor": "hand2",
        "highlightthickness": 0,
    },
    # Botão de perigo (Vermelho)
    "perigo": {
        "bg": CORES["alerta"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
        "cursor": "hand2",
        "highlightthickness": 0,
    },
    # Botão de sucesso (Verde)
    "sucesso": {
        "bg": CORES["destaque"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
        "padx": 20,
        "pady": 15,
        "activebackground": "#43a047",
        "activeforeground": CORES["texto_claro"],
        "cursor": "hand2",
        "highlightthickness": 0,
        "highlightbackground": CORES["fundo"],
        "highlightcolor": CORES["fundo"]
    },
}

def aplicar_estilo(widget, estilo):
    """Aplica um estilo a um widget"""
    if estilo in ESTILOS_BOTAO:
        widget.config(**ESTILOS_BOTAO[estilo])
    return widget

def configurar_estilo_tabelas():
    """Configura o estilo padrão para todas as tabelas (Treeview) do sistema"""
    import tkinter.ttk as ttk
    
    style = ttk.Style()
    style.configure("Treeview",
        background="#FFFFFF",
        foreground="#000000",
        fieldbackground="#FFFFFF",
        borderwidth=0
    )
    style.map('Treeview', 
        background=[('selected', CORES['primaria'])],
        foreground=[('selected', CORES['texto_claro'])]
    )
    
    return style
