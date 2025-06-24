"""
Tela de carregamento exibida durante a tentativa de conexão com o banco de dados.
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
import os

class TelaCarregamento:
    """Tela de carregamento com animação giratória."""
    
    def __init__(self, root, mensagem="Tentando conectar ao banco de dados, aguarde..."):
        """Inicializa a tela de carregamento.
        
        Args:
            root: Janela raiz do Tkinter
            mensagem (str): Mensagem a ser exibida abaixo do ícone de carregamento
        """
        self.root = root
        self.root.title("PDV Bar & Restaurante")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centraliza a janela
        self._centralizar_janela()
        
        # Configura o estilo
        self.root.configure(bg="#f0f0f0")
        
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Título
        self.titulo_label = tk.Label(
            self.main_frame, 
            text="PDV BAR & RESTAURANTE", 
            font=("Arial", 16, "bold"), 
            bg="#f0f0f0"
        )
        self.titulo_label.pack(pady=(20, 10))
        
        # Subtítulo
        self.subtitulo_label = tk.Label(
            self.main_frame, 
            text="Sistema de Vendas", 
            font=("Arial", 12), 
            bg="#f0f0f0"
        )
        self.subtitulo_label.pack(pady=(0, 30))
        
        # Frame do ícone de carregamento
        self.loading_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.loading_frame.pack(pady=(10, 20))
        
        # Ícone de carregamento (será animado)
        self.loading_icon = tk.Label(self.loading_frame, bg="#f0f0f0")
        self.loading_icon.pack()
        
        # Mensagem de carregamento
        self.mensagem_label = tk.Label(
            self.main_frame, 
            text=mensagem,
            font=("Arial", 10),
            bg="#f0f0f0"
        )
        self.mensagem_label.pack(pady=(0, 20))
        
        # Inicia a animação
        self.angle = 0
        self.animar_icone()
    
    def _centralizar_janela(self):
        """Centraliza a janela na tela."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def animar_icone(self):
        """Anima o ícone de carregamento."""
        try:
            # Tenta carregar um ícone de carregamento
            from PIL import Image, ImageTk
            
            # Cria uma imagem de carregamento simples (um círculo)
            size = 40
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # Desenha um círculo com uma parte faltando para simular rotação
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            
            # Desenha um círculo vazio
            bbox = [2, 2, size-2, size-2]
            draw.arc(bbox, 0, 360, fill="#3498db", width=3)
            
            # Adiciona uma parte preenchida para simular rotação
            start_angle = self.angle % 360
            end_angle = (start_angle + 270) % 360
            draw.arc(bbox, start_angle, end_angle, fill="#3498db", width=3)
            
            # Converte para PhotoImage
            self.loading_image = ImageTk.PhotoImage(img)
            self.loading_icon.config(image=self.loading_image)
            
            # Atualiza o ângulo para a próxima iteração
            self.angle = (self.angle + 20) % 360
            
            # Agenda a próxima atualização
            self.root.after(50, self.animar_icone)
            
        except ImportError:
            # Se o PIL não estiver disponível, usa um texto simples
            self.loading_icon.config(text="Carregando...", font=("Arial", 10))
    
    def atualizar_mensagem(self, nova_mensagem):
        """Atualiza a mensagem exibida.
        
        Args:
            nova_mensagem (str): Nova mensagem a ser exibida
        """
        self.mensagem_label.config(text=nova_mensagem)
        self.root.update()
    
    def fechar(self):
        """Fecha a tela de carregamento."""
        self.root.destroy()


def mostrar_tela_carregamento(root, funcao_carregamento, *args, **kwargs):
    """Mostra uma tela de carregamento enquanto executa uma função em segundo plano.
    
    Args:
        root: Janela raiz do Tkinter
        funcao_carregamento: Função a ser executada em segundo plano
        *args: Argumentos posicionais para a função
        **kwargs: Argumentos nomeados para a função
        
    Returns:
        O resultado da função de carregamento, se houver
    """
    # Cria uma janela para a tela de carregamento como filha da janela principal
    janela_carregamento = tk.Toplevel(root)
    janela_carregamento.transient(root)  # Torna a janela modal em relação à janela principal
    janela_carregamento.overrideredirect(True)  # Remove a barra de título
    
    # Cria a tela de carregamento
    tela = TelaCarregamento(janela_carregamento)
    
    # Variável para armazenar o resultado da função
    resultado = []
    
    def executar_funcao():
        """Executa a função em segundo plano."""
        try:
            # Executa a função e armazena o resultado
            resultado.append(funcao_carregamento(*args, **kwargs))
        except Exception as e:
            # Em caso de erro, armazena a exceção
            resultado.append(e)
        # Não fechamos a janela aqui, será fechada no loop principal
    
    # Função para centralizar a janela de forma segura
    def centralizar_janela():
        try:
            if janela_carregamento.winfo_exists():
                janela_carregamento.update_idletasks()
                width = janela_carregamento.winfo_reqwidth()
                height = janela_carregamento.winfo_reqheight()
                x = (janela_carregamento.winfo_screenwidth() // 2) - (width // 2)
                y = (janela_carregamento.winfo_screenheight() // 2) - (height // 2)
                janela_carregamento.geometry(f'400x200+{x}+{y}')
        except Exception:
            pass  # Ignora erros ao centralizar
    
    # Centraliza a janela
    centralizar_janela()
    
    # Inicia a execução da função em uma thread separada
    thread = threading.Thread(target=executar_funcao)
    thread.daemon = True
    thread.start()
    
    # Usamos um dicionário para armazenar o estado da janela
    estado = {'janela_fechada': False}
    
    # Função para fechar a janela de forma segura
    def fechar_janela():
        if not estado['janela_fechada'] and janela_carregamento.winfo_exists():
            try:
                janela_carregamento.grab_release()
                janela_carregamento.destroy()
                estado['janela_fechada'] = True
            except Exception:
                pass
    
    # Função para verificar se a thread terminou
    def verificar_thread():
        if not estado['janela_fechada'] and thread.is_alive():
            # Se a thread ainda estiver rodando, verifica novamente em 100ms
            if janela_carregamento.winfo_exists():
                janela_carregamento.after(100, verificar_thread)
            else:
                estado['janela_fechada'] = True
        else:
            # Quando a thread terminar, fecha a janela
            fechar_janela()
    
    # Configura o fechamento da janela
    def on_closing():
        fechar_janela()
        root.focus_force()
    
    janela_carregamento.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Foca a janela de carregamento
    try:
        if not estado['janela_fechada'] and janela_carregamento.winfo_exists():
            janela_carregamento.grab_set()
    except Exception:
        pass
    
    # Inicia a verificação
    if not estado['janela_fechada'] and janela_carregamento.winfo_exists():
        janela_carregamento.after(100, verificar_thread)
    
    # Mantém a janela aberta até ser fechada
    try:
        janela_carregamento.wait_window()
    except tk.TclError:
        pass  # Janela já foi fechada
    
    # Retorna o resultado da função, se houver
    if resultado:
        # Se o resultado for uma exceção, levante-a
        if isinstance(resultado[0], Exception):
            raise resultado[0]
        return resultado[0]
    return None
