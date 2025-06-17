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
    "texto": "#333333",         # Cinza escuro
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
    "padrao": {
        "bg": CORES["primaria"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
        "activebackground": CORES["secundaria"],
        "activeforeground": CORES["texto_claro"],
    },
    "secundario": {
        "bg": CORES["secundaria"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
    },
    "perigo": {
        "bg": CORES["alerta"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
    },
    "sucesso": {
        "bg": CORES["sucesso"],
        "fg": CORES["texto_claro"],
        "font": FONTES["normal"],
        "relief": "flat",
        "bd": 0,
    },
}

def aplicar_estilo(widget, estilo):
    """Aplica um estilo a um widget"""
    if estilo in ESTILOS_BOTAO:
        widget.config(**ESTILOS_BOTAO[estilo])
    return widget
