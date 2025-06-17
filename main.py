"""
Ponto de entrada principal do Sistema PDV - Versão simplificada

usamos somente(exclusivamente) mysql  para banco de dados
o formato de criação de botoes  vai ser sempre o mesmo
é iniaceitavel qualquer tipo de mudança de estrategia de construção sem autorização
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def mostrar_sistema_pdv(usuario, login_window):
    """Mostra a tela principal do sistema após o login"""
    from src.views.telas.sistema_pdv import SistemaPDV
    
    # Limpa a janela de login
    for widget in login_window.winfo_children():
        widget.destroy()
    
    # Configura a janela principal
    login_window.title("PDV Bar & Restaurante")
    login_window.state('zoomed')  # Maximiza a janela
    
    # Configura o que acontece ao fechar a janela
    def on_closing():
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            login_window.destroy()
    
    login_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Cria a tela principal (SistemaPDV) dentro da janela existente
    app = SistemaPDV(login_window, usuario)

def main():
    """Função principal que inicia a aplicação"""
    try:
        # Cria a janela de login
        root = tk.Tk()
        
        # Importa aqui para evitar erros circulares
        from src.views.telas.login import TelaLogin
        
        # Cria a tela de login
        login = TelaLogin(root, mostrar_sistema_pdv)
        
        # Inicia o loop principal da interface
        root.mainloop()
        
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
