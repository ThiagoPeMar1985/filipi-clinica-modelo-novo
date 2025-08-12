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
import mysql.connector
from pathlib import Path

# Adiciona o diretório raiz ao path para garantir que os imports funcionem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as configurações do banco de dados
from src.db.config import get_db_config

def _conectar_banco_dados():
    """Função interna para testar a conexão com o banco de dados."""
    try:
        # Obtém as configurações do banco de dados
        db_config = get_db_config()
        
        # Remove chaves que não são necessárias para a conexão
        for key in ['raise_on_warnings', 'use_pure', 'autocommit', 'charset', 'collation', 'connection_timeout', 'connect_timeout']:
            db_config.pop(key, None)
        
        # Configura timeout aumentado para a conexão
        db_config['connection_timeout'] = 10
        db_config['connect_timeout'] = 10
        
        # Imprime informações de diagnóstico (será removido no executável final)
        print(f"Tentando conectar ao banco: {db_config.get('host')}:{db_config.get('port')}/{db_config.get('database')}")
        
        # Tenta conectar ao banco de dados
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            conn.close()
            return True, "Conexão com o banco de dados estabelecida com sucesso!"
        return False, "Falha ao conectar ao banco de dados."
    except ImportError as e:
        print(f"Erro de importação: {str(e)}")
        return False, f"Erro ao importar módulos necessários: {str(e)}"
    except mysql.connector.Error as e:
        print(f"Erro MySQL: {str(e)}")
        return False, f"Erro de conexão MySQL: {str(e)}"
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        return False, f"Erro ao conectar ao banco de dados: {str(e)}"

def testar_conexao_banco_dados(root=None):
    """Testa a conexão com o banco de dados.
    
    Args:
        root: Janela raiz do Tkinter (opcional, mantido para compatibilidade)
        
    Returns:
        tuple: (sucesso, mensagem) indicando o resultado da conexão
    """
    return _conectar_banco_dados()

def mostrar_tela_banco_dados(root):
    """Mostra a tela de configuração do banco de dados"""
    from src.views.modulos.configuracao.configuracao_module import ConfiguracaoModule
    
    # Configura a janela
    janela = tk.Toplevel(root)
    janela.title("Configuração do Banco de Dados")
    janela.geometry("800x600")
    janela.resizable(True, True)
    
    # Centraliza a janela
    window_width = 800
    window_height = 600
    screen_width = janela.winfo_screenwidth()
    screen_height = janela.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    janela.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Cria o módulo de configuração
    config_module = ConfiguracaoModule(janela, None)
    config_module.show('banco_dados')
    
    # Variável para controlar se o salvamento foi bem-sucedido
    salvamento_ok = False
    
    # Sobrescreve o método de salvar do módulo de configuração
    def salvar_banco_dados_original():
        nonlocal salvamento_ok
        # Chama o método original de salvar
        if config_module._salvar_banco_dados():
            salvamento_ok = True
    
    # Substitui o método de salvar
    if hasattr(config_module, '_salvar_banco_dados'):
        config_module._salvar_banco_dados_original = config_module._salvar_banco_dados
        config_module._salvar_banco_dados = salvar_banco_dados_original
    
    # Configura o que acontece ao fechar a janela
    def on_closing():
        # Se o salvamento foi bem-sucedido, apenas fecha a janela e volta para o login
        if salvamento_ok:
            janela.destroy()
            mostrar_tela_login(root)
            return
            
        # Se não foi um salvamento, pergunta se deseja sair sem salvar
        if messagebox.askyesno(
            "Sair sem salvar", 
            "Deseja sair sem salvar as alterações?"
        ):
            janela.destroy()
            mostrar_tela_login(root)
    
    # Configura o protocolo de fechamento da janela
    janela.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Mantém a janela modal
    janela.grab_set()
    janela.focus_force()
    janela.wait_window()

def mostrar_tela_conexao_db(root):
    """Mostra a tela de configuração de conexão com o banco de dados"""
    # Limpa a janela
    for widget in root.winfo_children():
        widget.destroy()
    
    # Configura a janela
    root.title("Configuração do Banco de Dados")
    root.geometry("800x600")
    root.resizable(True, True)
    
    # Centraliza a janela
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Cria a tela de conexão com o banco de dados
    from src.views.telas.conexao_db import TelaConexaoDB
    
    # Define o callback para quando a conexão for bem-sucedida
    def on_conexao_sucesso():
        # Mostra a tela de login
        mostrar_tela_login(root)
    
    # Cria a tela de conexão
    TelaConexaoDB(root, callback_sucesso=on_conexao_sucesso)
    
    # Mostra a janela
    root.deiconify()

def mostrar_tela_login(root):
    """Mostra a tela de login"""
    # Limpa a janela
    for widget in root.winfo_children():
        widget.destroy()
    
    # Cria a tela de login
    from src.views.telas.login import TelaLogin
    TelaLogin(root, mostrar_sistema_pdv)

def mostrar_sistema_pdv(usuario, login_window):
    """Mostra a tela principal do sistema após o login"""
    from src.views.telas.sistema_pdv import SistemaPDV
    
    # Limpa a janela de login
    for widget in login_window.winfo_children():
        widget.destroy()
    
    # Configura a janela principal
    login_window.title("Clinica Medica")
    # Abrir em 1766x768 centralizado (sem fullscreen)
    try:
        window_width = 1766
        window_height = 768
        screen_width = login_window.winfo_screenwidth()
        screen_height = login_window.winfo_screenheight()
        x = max(0, (screen_width - window_width) // 2)
        y = max(0, (screen_height - window_height) // 2)
        login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        login_window.resizable(True, True)
    except Exception:
        # Fallback: apenas define a geometria sem centralizar
        login_window.geometry("1766x768")
    
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
        # Cria a janela principal
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal inicialmente
        
        # Testa a conexão com o banco de dados
        try:
            sucesso, mensagem = testar_conexao_banco_dados()
            
            if sucesso:
                # Se a conexão for bem-sucedida, mostra a tela de login
                print("Conexão com banco de dados bem-sucedida. Exibindo tela de login.")
                mostrar_tela_login(root)
            else:
                # Se a conexão falhar, mostra a tela de configuração do banco de dados
                print(f"Falha na conexão com banco de dados: {mensagem}")
                print("Exibindo tela de configuração de conexão.")
                mostrar_tela_conexao_db(root)
                    
        except Exception as e:
            # Em caso de erro inesperado, mostra a tela de configuração do banco
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            print("Exibindo tela de configuração de conexão devido a erro.")
            mostrar_tela_conexao_db(root)
        
        # Configura o que acontece ao fechar a janela principal
        def on_closing():
            if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Mostra a janela principal e inicia o loop
        root.deiconify()
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao iniciar o sistema: {str(e)}")
        print(f"Erro fatal: {str(e)}")

if __name__ == "__main__":
    main()
