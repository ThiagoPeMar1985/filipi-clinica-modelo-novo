"""
Módulo para visualização de mesas do restaurante.
Exibe o layout das mesas e seu status atual.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
from src.config.estilos import CORES, FONTES, ESTILOS_BOTAO
from src.views.modulos.base_module import BaseModule

class VisualizarMesasModule(BaseModule):
    def __init__(self, parent, controller, db_connection=None):
        """
        Inicializa o módulo de visualização de mesas.
        
        Args:
            parent: Widget pai
            controller: Controlador principal
            db_connection: Conexão com o banco de dados (opcional)
        """
        # Inicializa a classe base
        super().__init__(parent, controller)
        
        self.db_connection = db_connection
        self.mesas = []
        
        # Cores para os status das mesas (conforme solicitado pelo usuário)
        self.cores_status = {
            "livre": CORES["primaria"],     # Azul claro para mesas livres
            "ocupada": CORES["secundaria"], # Azul escuro para mesas ocupadas
            "reservada": CORES["atencao"],  # Amarelo
            "inativa": CORES["inativo"]     # Cinza muito escuro
        }
        
        # Carregar mesas do banco de dados
        self.carregar_mesas()
        
        # Configurar a interface
        self.setup_ui()
    
    def carregar_mesas(self):
        """Carrega as mesas do banco de dados"""
        if not self.db_connection:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            query = "SELECT * FROM mesas ORDER BY numero"
            cursor.execute(query)
            self.mesas = cursor.fetchall()
            
            # Buscar valores dos pedidos para cada mesa
            for mesa in self.mesas:
                mesa['valor_pedido'] = self.buscar_valor_pedido(mesa['id'])
                
            cursor.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar mesas: {str(e)}")
            self.mesas = []
            
    def buscar_valor_pedido(self, mesa_id):
        """Busca o valor total do pedido ativo para uma mesa"""
        if not self.db_connection:
            return 0
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Verificar se a tabela pedidos existe
            cursor.execute("SHOW TABLES LIKE 'pedidos'")
            if not cursor.fetchone():
                return 0
            
            # Busca por pedidos com status 'em andamento' ou 'aberto'
            query = """
            SELECT p.id, p.total, p.status 
            FROM pedidos p 
            WHERE p.mesa_id = %s AND (p.status = 'em andamento' OR p.status = 'aberto')
            ORDER BY p.data_abertura DESC LIMIT 1
            """
            
            cursor.execute(query, (mesa_id,))
            resultado = cursor.fetchone()
            
            # Se não encontrar com status 'em andamento' ou 'aberto', tenta encontrar qualquer pedido ativo
            if not resultado:
                query = """
                SELECT p.id, p.total, p.status 
                FROM pedidos p 
                WHERE p.mesa_id = %s
                ORDER BY p.data_abertura DESC LIMIT 1
                """
                cursor.execute(query, (mesa_id,))
                resultado = cursor.fetchone()
            
            if resultado and 'total' in resultado and resultado['total'] is not None:
                try:
                    return float(resultado['total'])
                except (ValueError, TypeError):
                    return 0
                    
            return 0
        except Exception as e:
            print(f"DEBUG - Erro ao buscar valor do pedido: {e}")
            return 0
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal com fundo padrão
        main_frame = tk.Frame(self.frame, bg=CORES['fundo'])
        main_frame.pack(fill="both", expand=True)
        
        # Frame para o título
        titulo_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        titulo_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Título
        tk.Label(
            titulo_frame, 
            text="VISUALIZAÇÃO DE MESAS", 
            font=FONTES['titulo'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(anchor="w")
        
        # Linha divisória
        separador = ttk.Separator(main_frame, orient="horizontal")
        separador.pack(fill="x", padx=20, pady=5)
        
        # Frame para o conteúdo principal
        # Usando pack_propagate(False) para controlar o tamanho e garantir que o footer fique visível
        conteudo_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        conteudo_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame para o grid de mesas com scrollbar para garantir responsividade
        # Usamos um canvas com scrollbar para permitir rolagem quando necessário
        canvas_container = tk.Frame(conteudo_frame, bg=CORES['fundo'])
        canvas_container.pack(fill="both", expand=True)
        
        # Canvas para conter o grid de mesas com scrollbar
        canvas = tk.Canvas(canvas_container, bg=CORES['fundo'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        # Frame dentro do canvas para as mesas
        mesas_frame = tk.Frame(canvas, bg=CORES['fundo'])
        
        # Configuração do canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Criar janela no canvas para o frame de mesas
        canvas_window = canvas.create_window((0, 0), window=mesas_frame, anchor="nw")
        
        # Função para ajustar o tamanho do scrollregion quando o frame de mesas mudar de tamanho
        def ajustar_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Ajustar a largura do frame de mesas para preencher o canvas
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        
        # Vincular evento de configuração para ajustar o scrollregion
        mesas_frame.bind("<Configure>", ajustar_scrollregion)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=canvas.winfo_width()))
        
        # Criar grid de mesas
        self.criar_grid_mesas(mesas_frame)
        
        # Frame para legenda
        acoes_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        acoes_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Iniciar atualização automática
        self.iniciar_atualizacao_automatica()
        
        # Legenda de status
        self.criar_legenda(acoes_frame)
    
    def criar_grid_mesas(self, parent):
        """Cria o grid de mesas de forma responsiva"""
        # Frame para o grid
        grid_frame = tk.Frame(parent, bg=CORES['fundo'])
        grid_frame.pack(fill="both", expand=True)
        
        # Número de colunas no grid - ajuste dinâmico baseado na largura da tela
        # Em resoluções maiores, mostramos mais colunas
        largura_tela = self.controller.root.winfo_screenwidth()
        
        # Ajuste dinâmico de colunas baseado na largura da tela
        if largura_tela >= 3000:  # Telas ultrawide como 3440x1440
            colunas = 6
        elif largura_tela >= 1920:  # Full HD e superior
            colunas = 5
        else:  # Resoluções menores
            colunas = 4
        
        # Se não houver mesas, exibir mensagem
        if not self.mesas:
            tk.Label(
                grid_frame,
                text="Nenhuma mesa cadastrada",
                font=FONTES['subtitulo'],
                bg=CORES['fundo'],
                fg=CORES['texto']
            ).pack(pady=50)
            return
        
        # Criar mesas no grid
        for i, mesa in enumerate(self.mesas):
            row = i // colunas
            col = i % colunas
            
            # Frame da mesa com cor conforme status e sem bordas
            status_cor = self.cores_status.get(mesa["status"].lower(), CORES['destaque'])
            mesa_frame = tk.Frame(
                grid_frame,
                bg=status_cor,  # Cor conforme status
                bd=0,
                relief="flat",
                cursor='hand2',  # Cursor de mão para indicar que é clicável
                width=150,  # Largura fixa para garantir consistência
                height=150   # Altura fixa para garantir consistência
            )
            
            # Impedir que o frame mude de tamanho
            mesa_frame.pack_propagate(False)
            
            # Adicionar eventos de clique na mesa
            mesa_frame.bind("<Button-1>", lambda event, m=mesa, frame=mesa_frame: self._clique_mesa(m, frame))
            
            # Adicionar menu de contexto com botão direito
            mesa_frame.bind("<Button-3>", lambda event, m=mesa, frame=mesa_frame: self._mostrar_menu_contexto(event, m, frame))
            
            # Frame para conteúdo da mesa
            status_cor = self.cores_status.get(mesa["status"].lower(), CORES['destaque'])
            conteudo_mesa = tk.Frame(mesa_frame, bg=status_cor, padx=10, pady=10)
            conteudo_mesa.pack(fill="both", expand=True)
            
            # Adicionar eventos de clique também no conteúdo da mesa
            conteudo_mesa.bind("<Button-1>", lambda event, m=mesa, frame=mesa_frame: self._clique_mesa(m, frame))
            conteudo_mesa.bind("<Button-3>", lambda event, m=mesa, frame=mesa_frame: self._mostrar_menu_contexto(event, m, frame))
            
            # Número da mesa
            status_cor = self.cores_status.get(mesa["status"].lower(), CORES['destaque'])
            tk.Label(
                conteudo_mesa,
                text=f"Mesa {mesa['numero']}",
                font=FONTES['subtitulo'],
                bg=status_cor,
                fg=CORES['texto_claro']  # Texto branco
            ).pack(pady=(0, 5))
            
            # Capacidade
            status_cor = self.cores_status.get(mesa["status"].lower(), CORES['destaque'])
            tk.Label(
                conteudo_mesa,
                text=f"Capacidade: {mesa['capacidade']} pessoas",
                font=FONTES['pequena'],
                bg=status_cor,
                fg=CORES['texto_claro']  # Texto branco
            ).pack(pady=(0, 5))
            
            # Status
            status_cor = self.cores_status.get(mesa["status"].lower(), CORES['terciaria'])
            tk.Label(
                conteudo_mesa,
                text=f"Status: {mesa['status'].capitalize()}",
                font=FONTES['pequena'],
                bg=status_cor,
                fg=CORES['texto_claro']  # Texto branco
            ).pack(pady=(0, 5))
            
            # Valor do pedido (se existir e a mesa estiver ocupada)
            if mesa['status'].lower() == 'ocupada':
                valor = float(mesa.get('valor_pedido', 0) or 0)
                if valor > 0:
                    valor_formatado = f"R$ {valor:,.2f}"
                    valor_formatado = valor_formatado.replace('.', 'v').replace(',', '.').replace('v', ',')
                    tk.Label(
                        conteudo_mesa,
                        text=f"Valor: {valor_formatado}",
                        font=FONTES['pequena'],
                        bg=status_cor,
                        fg=CORES['texto_claro']  # Texto branco
                    ).pack(pady=(0, 5))
            
            # Posicionar no grid
            mesa_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Configurar expansão do grid - garantir que todas as colunas tenham o mesmo peso
            grid_frame.columnconfigure(col, weight=1)
            grid_frame.rowconfigure(row, weight=1)
        
        # Garantir que o grid tenha um tamanho mínimo para evitar compressão
        # Isso ajuda a manter o footer visível
        grid_frame.update_idletasks()
        grid_frame.update()
    
    def criar_legenda(self, parent):
        """Cria a legenda de status"""
        legenda_frame = tk.Frame(parent, bg=CORES['fundo'])
        legenda_frame.pack(side="left", fill="x", pady=5)
        
        tk.Label(
            legenda_frame, 
            text="Legenda:", 
            font=FONTES['pequena'], 
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(side="left", padx=5)
        
        for status, cor in self.cores_status.items():
            frame = tk.Frame(legenda_frame, bg=CORES['fundo'])
            frame.pack(side="left", padx=5)
            
            # Quadrado colorido
            canvas = tk.Canvas(frame, width=15, height=15, bg=CORES['fundo'], highlightthickness=0)
            canvas.create_rectangle(0, 0, 15, 15, fill=cor, outline="")
            canvas.pack(side="left")
            
            # Texto do status
            tk.Label(
                frame, 
                text=status.capitalize(), 
                font=FONTES['pequena'],
                bg=CORES['fundo'],
                fg=CORES['texto']
            ).pack(side="left", padx=2)
    
    def ver_detalhes_mesa(self, mesa):
        """Exibe os detalhes da mesa selecionada"""
        # Criar janela de detalhes
        detalhes_window = tk.Toplevel(self.frame)
        detalhes_window.title(f"Detalhes da Mesa {mesa['numero']}")
        detalhes_window.geometry("400x400")
        detalhes_window.resizable(False, False)
        detalhes_window.transient(self.frame)
        detalhes_window.grab_set()
        detalhes_window.configure(bg=CORES['fundo'])
        
        # Frame principal
        main_frame = tk.Frame(detalhes_window, bg=CORES['fundo'], padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        tk.Label(
            main_frame, 
            text=f"DETALHES DA MESA {mesa['numero']}", 
            font=FONTES['titulo'],
            bg=CORES['fundo'],
            fg=CORES['texto']
        ).pack(anchor="w", pady=(0, 10))
        
        # Separador
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Frame para conteúdo
        conteudo_frame = tk.Frame(main_frame, bg=CORES['fundo_conteudo'], bd=1, relief="solid")
        conteudo_frame.pack(fill="both", expand=True, pady=10)
        
        # Barra de status na parte superior
        status_bar = tk.Frame(
            conteudo_frame,
            bg=self.cores_status.get(mesa["status"].lower(), CORES['inativo']),
            height=8
        )
        status_bar.pack(fill="x")
        
        # Informações da mesa
        info_frame = tk.Frame(conteudo_frame, bg=CORES['fundo_conteudo'], padx=20, pady=20)
        info_frame.pack(fill="both", expand=True)
        
        # ID
        tk.Label(
            info_frame, 
            text="ID:", 
            font=FONTES['pequena'], 
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=0, column=0, sticky="w", pady=8)
        
        tk.Label(
            info_frame, 
            text=str(mesa["id"]), 
            font=FONTES['pequena'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=0, column=1, sticky="w", pady=8, padx=10)
        
        # Número
        tk.Label(
            info_frame, 
            text="Número:", 
            font=FONTES['pequena'], 
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=1, column=0, sticky="w", pady=8)
        
        tk.Label(
            info_frame, 
            text=mesa["numero"], 
            font=FONTES['pequena'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=1, column=1, sticky="w", pady=8, padx=10)
        
        # Capacidade
        tk.Label(
            info_frame, 
            text="Capacidade:", 
            font=FONTES['pequena'], 
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=2, column=0, sticky="w", pady=8)
        
        tk.Label(
            info_frame, 
            text=f"{mesa['capacidade']} pessoas", 
            font=FONTES['pequena'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=2, column=1, sticky="w", pady=8, padx=10)
        
        # Status
        tk.Label(
            info_frame, 
            text="Status:", 
            font=FONTES['pequena'], 
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).grid(row=3, column=0, sticky="w", pady=8)
        
        status_frame = tk.Frame(info_frame, bg=CORES['fundo_conteudo'])
        status_frame.grid(row=3, column=1, sticky="w", pady=8, padx=10)
        
        # Indicador de status colorido
        status_cor = self.cores_status.get(mesa["status"].lower(), CORES['inativo'])
        canvas = tk.Canvas(status_frame, width=15, height=15, bg=CORES['fundo_conteudo'], highlightthickness=0)
        canvas.create_rectangle(0, 0, 15, 15, fill=status_cor, outline="")
        canvas.pack(side="left")
        
        tk.Label(
            status_frame, 
            text=f" {mesa['status'].capitalize()}", 
            font=FONTES['pequena'],
            bg=CORES['fundo_conteudo'],
            fg=CORES['texto']
        ).pack(side="left")
        
        # Frame para botões
        botoes_frame = tk.Frame(main_frame, bg=CORES['fundo'])
        botoes_frame.pack(fill="x", pady=(15, 0))
        
        # Botão para fechar
        tk.Button(
            botoes_frame, 
            text="FECHAR", 
            font=FONTES['pequena'],
            bg=CORES['primaria'],
            fg=CORES['texto_claro'],
            bd=0,
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2',
            command=detalhes_window.destroy
        ).pack(side="right")
        
        # Centralizar a janela
        self.centralizar_janela(detalhes_window, 400, 400)
    
    def atualizar_mesas(self, forcar_atualizacao=False):
        """Atualiza a lista de mesas silenciosamente sem recriar toda a interface"""
        try:
            # Verificar se o frame ainda existe
            if not hasattr(self, 'frame') or not self.frame.winfo_exists():
                return
                
            # Salvar a referência ao frame atual
            mesas_antigas = self.mesas.copy()
            
            # Recarregar as mesas do banco de dados
            self.carregar_mesas()
            
            # Verificar se houve mudanças ou se devemos forçar a atualização
            if self.mesas != mesas_antigas or forcar_atualizacao:
                # Verificar novamente se o frame ainda existe
                if not hasattr(self, 'frame') or not self.frame.winfo_exists():
                    return
                    
                # Limpar e recriar o grid de mesas
                for widget in self.frame.winfo_children():
                    try:
                        widget.destroy()
                    except:
                        continue
                        
                # Recriar apenas o grid de mesas, não a interface completa
                self.criar_grid_mesas(self.frame)
        except Exception as e:
            print(f"Erro ao atualizar mesas: {str(e)}")
    
    def iniciar_atualizacao_automatica(self):
        """Inicia a atualização automática das mesas a cada segundo"""
        try:
            # Verificar se o módulo ainda está ativo
            if not hasattr(self, 'frame') or not self.frame.winfo_exists():
                return
                
            self.atualizar_mesas()
            
            # Verificar novamente antes de agendar a próxima atualização
            if hasattr(self, 'frame') and self.frame.winfo_exists():
                # Agendar a próxima atualização em 1000ms (1 segundo)
                self.controller.root.after(1000, self.iniciar_atualizacao_automatica)
        except Exception as e:
            print(f"Erro na atualização automática: {str(e)}")
    
    def centralizar_janela(self, janela, largura, altura):
        """Centraliza uma janela na tela"""
        # Obter as dimensões da tela
        largura_tela = janela.winfo_screenwidth()
        altura_tela = janela.winfo_screenheight()
        
        # Calcular a posição para centralizar
        pos_x = (largura_tela - largura) // 2
        pos_y = (altura_tela - altura) // 2
        
        # Definir a geometria da janela
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    
    # Variável para controlar se uma janela de pedidos já está sendo aberta
    _abrindo_pedidos = False
    
    def abrir_tela_pedidos(self, mesa):
        """Abre a tela de pedidos para a mesa selecionada integrada ao layout principal"""
        if VisualizarMesasModule._abrindo_pedidos:
            return
            
        try:
            # Marcar que estamos abrindo uma janela para evitar cliques múltiplos
            VisualizarMesasModule._abrindo_pedidos = True
            
            # Criar uma janela de carregamento para feedback visual
            loading_window = tk.Toplevel(self.controller.root)
            loading_window.title("Carregando")
            loading_window.geometry("300x100")
            loading_window.transient(self.controller.root)
            loading_window.grab_set()
            
            # Centralizar a janela de carregamento
            self.centralizar_janela(loading_window, 300, 100)
            
            # Exibir mensagem de carregamento
            tk.Label(
                loading_window,
                text=f"Carregando pedidos da Mesa {mesa['numero']}...",
                font=FONTES['normal'],
                pady=20
            ).pack()
            
            # Atualizar a interface para mostrar a janela de carregamento
            loading_window.update()
            
            # Importar o módulo de pedidos
            from .pedidosMesas_module import PedidosMesasModule
            
            # Ocultar o módulo atual
            self.frame.pack_forget()
            
            # Inicializar o módulo de pedidos no frame principal
            pedidos_module = PedidosMesasModule(
                self.parent,
                self.controller,
                mesa=mesa,
                db_connection=self.db_connection,
                modulo_anterior=self  # Passar referência para voltar
            )
            
            # Mostrar o módulo de pedidos
            pedidos_module.show()
            
            # Fechar a janela de carregamento
            loading_window.destroy()
            
        except ImportError as ie:
            messagebox.showerror("Erro de Importação", f"Erro ao importar o módulo de pedidos: {str(ie)}\n\nVerifique se o arquivo pedidosMesas_module.py existe e está no local correto.")
            # Mostrar novamente o módulo atual em caso de erro
            self.frame.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            erro_detalhado = traceback.format_exc()
            messagebox.showerror("Erro", f"Erro ao abrir tela de pedidos:\n{str(e)}\n\nDetalhes:\n{erro_detalhado}")
            # Mostrar novamente o módulo atual em caso de erro
            self.frame.pack(fill="both", expand=True)
        finally:
            # Independentemente do resultado, marcar que não estamos mais abrindo uma janela
            VisualizarMesasModule._abrindo_pedidos = False
    
    def _clique_mesa(self, mesa, frame):
        """Gerencia o clique em uma mesa com feedback visual aprimorado"""
        # Evitar múltiplos cliques se já estiver abrindo
        if VisualizarMesasModule._abrindo_pedidos:
            return
            
        # Salvar a cor original
        cor_original = frame.cget("bg")
        
        # Mudar a cor para indicar que foi clicado
        frame.config(bg=CORES["secundaria"])
        
        # Adicionar texto de carregamento na mesa
        loading_labels = []
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Frame):
                loading_label = tk.Label(
                    widget,
                    text="Carregando...",
                    font=FONTES['pequena'],
                    bg=CORES["secundaria"],
                    fg=CORES['texto_claro']
                )
                loading_label.pack(pady=5)
                loading_labels.append(loading_label)
        
        # Atualizar a interface para mostrar a mudança de cor
        self.controller.root.update_idletasks()
        
        # Agendar a abertura da tela de pedidos imediatamente
        self.abrir_tela_pedidos(mesa)
        
        # Restaurar a cor original após um breve delay, verificando se o frame ainda existe
        self.controller.root.after(300, lambda: self._restaurar_cor_frame(frame, cor_original))
        
        # Remover os labels de carregamento após fechar a tela de pedidos
        self.controller.root.after(500, lambda: self._remover_labels_carregamento(loading_labels))
        
    def _remover_labels_carregamento(self, labels):
        """Remove os labels de carregamento das mesas"""
        for label in labels:
            if label.winfo_exists():
                label.destroy()
                
    def _atualizar_apos_fechar(self):
        """Método auxiliar para atualizar as mesas após fechar a tela de pedidos"""
        # Recarregar as mesas do banco de dados
        self.carregar_mesas()
        
        # Limpar e recriar o grid de mesas
        for widget in self.frame.winfo_children():
            widget.destroy()
            
        # Recriar apenas o grid de mesas
        self.criar_grid_mesas(self.frame)
        
    def _mostrar_menu_contexto(self, event, mesa, frame):
        """Exibe o menu de contexto para alterar o status da mesa"""
        menu = tk.Menu(self.frame, tearoff=0)
        
        # Adicionar opções de status disponíveis
        status_options = ["Livre", "Reservada", "Inativa"]
        
        # Se a mesa estiver ocupada, não permitir mudar o status
        if mesa['status'].lower() == 'ocupada':
            menu.add_command(label=f"Mesa ocupada - não pode ser alterada", state='disabled')
        else:
            for status in status_options:
                # Se for o status atual, marcar como selecionado
                if status.lower() == mesa['status'].lower():
                    menu.add_command(
                        label=f"✓ {status}",
                        command=lambda s=status: self._alterar_status_mesa(mesa, s.lower(), frame)
                    )
                else:
                    menu.add_command(
                        label=f"   {status}",
                        command=lambda s=status: self._alterar_status_mesa(mesa, s.lower(), frame)
                    )
        
        # Exibir o menu na posição do clique
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Garantir que o menu seja fechado ao soltar o botão
            menu.grab_release()
    
    def _alterar_status_mesa(self, mesa, novo_status, frame):
        """Altera o status de uma mesa no banco de dados"""
        if not self.db_connection:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados!")
            return
            
        try:
            cursor = self.db_connection.cursor()
            
            # Atualizar o status da mesa
            query = "UPDATE mesas SET status = %s WHERE id = %s"
            cursor.execute(query, (novo_status.lower(), mesa['id']))
            
            # Se a mesa estiver sendo marcada como ocupada, verificar se há pedido ativo
            if novo_status.lower() == 'ocupada':
                cursor.execute("""
                    SELECT id FROM pedidos 
                    WHERE mesa_id = %s 
                    AND status = 'EM_ANDAMENTO' 
                    ORDER BY data_hora DESC 
                    LIMIT 1
                """, (mesa['id'],))
                
                pedido = cursor.fetchone()
                
                if not pedido:
                    # Se não houver pedido ativo, criar um novo
                    from datetime import datetime
                    cursor.execute("""
                        INSERT INTO pedidos (mesa_id, status, data_hora, total)
                        VALUES (%s, 'EM_ANDAMENTO', %s, 0)
                    """, (mesa['id'], datetime.now()))
                    
                    pedido_id = cursor.lastrowid
                    
                    # Atualizar a mesa com o ID do pedido
                    cursor.execute("""
                        UPDATE mesas 
                        SET pedido_atual_id = %s 
                        WHERE id = %s
                    """, (pedido_id, mesa['id']))
            
            # Confirmar as alterações
            self.db_connection.commit()
            
            # Atualizar a lista de mesas do banco de dados
            self.carregar_mesas()
            
            # Reconstruir a interface
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.setup_ui()
            
            # Focar na janela principal
            self.frame.focus_set()
            
        except Exception as e:
            self.db_connection.rollback()
            messagebox.showerror("Erro", f"Erro ao alterar status da mesa: {str(e)}")
        finally:
            cursor.close()
    
    def _atualizar_apos_mudanca_status(self):
        """Método mantido para compatibilidade, mas não é mais usado"""
        pass
    
    def _restaurar_cor_frame(self, frame, cor):
        """Restaura a cor de um frame verificando se ele ainda existe"""
        if frame.winfo_exists():
            frame.configure(bg=cor)
            for child in frame.winfo_children():
                if hasattr(child, 'configure') and 'bg' in child.keys():
                    child.configure(bg=cor)
    
    def show(self):
        """Mostra o módulo"""
        if hasattr(self, 'frame') and self.frame:
            self.frame.pack(fill="both", expand=True, padx=20, pady=20)
            return self.frame
        return None
