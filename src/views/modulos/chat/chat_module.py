import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
import sys

# Ajusta o path para permitir importações absolutas (mesmo padrão do módulo Configuração)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from ..base_module import BaseModule
from src.db.chat_db import ChatDB
from src.db.database import db


class ChatModule(BaseModule):
    """
    Módulo de Chat na rede local usando o banco compartilhado.

    Recursos:
    - Presença: heartbeat no banco a cada ~10s.
    - Lista de usuários online (à esquerda).
    - Conversas 1:1 (mensagens persistidas no banco).
    - Polling de novas mensagens (~1.5s) e notificação (piscar botão Chat).
    """

    def __init__(self, parent, controller):
        # Inicializa BaseModule (estilos, frame, helpers)
        super().__init__(parent, controller)
        
        # Identidade do usuário atual - CORRIGIDO
        self.me_id = getattr(self.controller.usuario, 'id', None) if hasattr(self.controller, 'usuario') else None
        self.me_nome = getattr(self.controller.usuario, 'nome', 'Usuário') if hasattr(self.controller, 'usuario') else 'Usuário'
        self.me_disp = None  # ChatDB usa hostname por padrão

        # Estado de conversa/seleção
        self._contato_sel = None  # dict: {usuario_id, usuario_nome, dispositivo}
        self._poll_job = None
        self._hb_job = None

        # DB
        self.conn = db.get_connection()
        self.chatdb = ChatDB(self.conn)

        # Frame de conteúdo padronizado (como em ConfiguracaoModule)
        self.conteudo_frame = tk.Frame(self.frame, bg='#f0f2f5')
        self.conteudo_frame.pack(fill=tk.BOTH, expand=True)

        # Opções do menu lateral (renderizado pelo container principal)
        self.opcoes = [
            {"nome": "Mensagens", "acao": "mensagens"}
        ]

        # Mostra a tela inicial padrão
        self._show_default()

    # ------------------------- Integração com BaseModule -------------------------
    def get_opcoes(self):
        return self.opcoes

    def show(self, acao=None):
        # Ao trocar de view, garantir que polling/heartbeat parem
        self._stop_polling_and_heartbeat()

        # Limpa a view atual
        if hasattr(self, 'current_view') and self.current_view:
            try:
                self.current_view.destroy()
            except tk.TclError:
                pass
            self.current_view = None

        # Direciona para a view solicitada
        if acao == 'mensagens':
            self._show_mensagens()
        else:
            self._show_default()

        return self.frame

    # ------------------------- Tela inicial padrão -------------------------
    def _show_default(self):
        self.current_view = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        self.current_view.pack(fill='both', expand=True)

        label = tk.Label(
            self.current_view,
            text="Selecione uma opção no menu lateral para começar.",
            font=('Arial', 12),
            bg='#f0f2f5'
        )
        label.pack(pady=20)

        # Badge de status do caixa padronizado
        try:
            self.create_caixa_status_badge(self.current_view, pady=(0, 0))
        except Exception:
            pass

    # ------------------------- Tela de mensagens (chat) -------------------------
    def _show_mensagens(self):
        # Cria a view de mensagens
        self.current_view = tk.Frame(self.conteudo_frame, bg='#f0f2f5')
        self.current_view.pack(fill='both', expand=True)

        # Cabeçalho
        header = tk.Frame(self.current_view, bg='#f0f2f5')
        header.pack(fill='x', padx=10, pady=(10, 0))

        titulo = tk.Label(
            header,
            text='Chat',
            font=("Arial", 16, 'bold'),
            bg='#f0f2f5',
            fg='#333333'
        )
        titulo.pack(side='left')

        # Corpo com 2 colunas: contatos | conversa
        corpo = tk.Frame(self.current_view, bg='#f0f2f5')
        corpo.pack(fill='both', expand=True, padx=10, pady=10)

        # Coluna esquerda (contatos online)
        left = tk.Frame(corpo, width=240, bg='#f0f2f5')
        left.pack(side='left', fill='y')
        left.pack_propagate(False)

        self.left_header = tk.Label(left, text='Usuários Online', bg='#f0f2f5', fg='#333333', font=("Arial", 12, 'bold'))
        self.left_header.pack(fill='x', padx=8, pady=(8, 4))

        # Área dos nomes (branca)
        self.lista_contatos = tk.Frame(left, bg='#ffffff')
        self.lista_contatos.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        # Coluna direita (conversa)
        right = tk.Frame(corpo, bg='#f0f2f5')
        right.pack(side='left', fill='both', expand=True, padx=(8, 0))

        self.lbl_conversa = tk.Label(right, text='Selecione um contato à esquerda', bg='#f0f2f5', fg='#555555', font=("Arial", 12, 'italic'))
        self.lbl_conversa.pack(anchor='w', padx=4, pady=(0, 6))

        self.txt_mensagens = scrolledtext.ScrolledText(
            right,
            wrap='word',
            state='disabled',
            font=("Arial", 11),
            bg='#ffffff',
            fg='#333333',
            height=18
        )
        self.txt_mensagens.pack(fill='both', expand=True, side='top')

        # Base cinza; input branco
        entrada_frame = tk.Frame(right, bg='#f0f2f5')
        entrada_frame.pack(fill='x', side='bottom', pady=(8, 0))

        self.entry_msg = tk.Entry(entrada_frame, font=("Arial", 12), bg='#ffffff', fg='#000000')
        self.entry_msg.pack(fill='x', expand=True, side='left', padx=(0, 8))
        self.entry_msg.bind('<Return>', self._on_enter)

        btn_enviar = tk.Button(
            entrada_frame,
            text='Enviar',
            font=("Arial", 11, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            activebackground='#43A047',
            activeforeground='#ffffff',
            relief='flat',
            padx=16, pady=8,
            command=self._enviar
        )
        btn_enviar.pack(side='right')

        # Inicializações: carregar contatos e iniciar presença/polling
        self._refresh_online()
        self._start_heartbeat()
        self._start_polling()

        # Foco no campo ao abrir
        try:
            self.entry_msg.focus_set()
        except Exception:
            pass

    # ------------------------- Polling / Presença -------------------------
    def _start_heartbeat(self):
        self._do_heartbeat()

    def _do_heartbeat(self):
        try:
            # Tenta obter o ID e nome do usuário do controller.usuario
            if hasattr(self.controller, 'usuario'):
                usuario_id = getattr(self.controller.usuario, 'id', None)
                usuario_nome = getattr(self.controller.usuario, 'nome', 'Usuário')
                
                # Atualiza os atributos da instância
                if usuario_id is not None:
                    self.me_id = usuario_id
                    self.me_nome = str(usuario_nome) if usuario_nome else 'Usuário'
                    
                    # Dispositivo padrão se não estiver definido
                    if not hasattr(self, 'me_disp') or not self.me_disp:
                        import socket
                        self.me_disp = socket.gethostname()
                    
                    # Faz o heartbeat (silencioso)
                    self.chatdb.heartbeat(self.me_id, self.me_nome, self.me_disp)
                    self.conn.commit()
                    return  # Sucesso, sai da função
            
            # Se chegou aqui, não conseguiu obter o usuário
            print("Aguardando login do usuário...")
            
        except Exception as e:
            print(f"Erro no heartbeat: {e}")
            # Tenta reconectar
            try:
                self.conn = db.get_connection()
                self.chatdb = ChatDB(self.conn)
            except Exception as e2:
                print(f"Falha ao reconectar: {e2}")
        
        # Agenda próximo heartbeat (5s)
        try:
            if hasattr(self, '_hb_job') and self._hb_job:
                self.frame.after_cancel(self._hb_job)
            self._hb_job = self.frame.after(5000, self._do_heartbeat)
        except Exception as e:
            print(f"Erro ao agendar heartbeat: {e}")
            self._hb_job = None


    def _start_polling(self):
        self._poll_messages()
        self._poll_online()

    def _poll_messages(self):
        try:
            # Verifica se o usuário está logado
            if not hasattr(self, 'me_id') or self.me_id is None:
                # Tenta obter do controller.usuario
                if hasattr(self.controller, 'usuario'):
                    self.me_id = getattr(self.controller.usuario, 'id', None)
                    self.me_nome = getattr(self.controller.usuario, 'nome', 'Usuário')
                
                # Se ainda não tem ID, aguarda
                if self.me_id is None:
                    print("Poll: Usuário não logado, aguardando...")
                    # Agenda próxima verificação (1 segundo)
                    if self._poll_job:
                        self.frame.after_cancel(self._poll_job)
                    self._poll_job = self.frame.after(1000, self._poll_messages)
                    return
            
            # Garante que temos valores válidos
            if not isinstance(self.me_id, int):
                print(f"Poll: ID do usuário inválido: {type(self.me_id)}")
                # Agenda próxima verificação (1 segundo)
                if self._poll_job:
                    self.frame.after_cancel(self._poll_job)
                self._poll_job = self.frame.after(1000, self._poll_messages)
                return
                
            # Busca mensagens não lidas
            nao_lidas = self.chatdb.listar_nao_lidas_para(self.me_id, self.me_nome, self.me_disp)
            total = len(nao_lidas)
            
            # Notifica app principal
            if hasattr(self.controller, 'notify_chat_unread'):
                self.controller.notify_chat_unread(total)

            # Atualiza a conversa atual se houver mensagens novas
            if total and self._contato_sel is not None:
                self._carregar_conversa(self._contato_sel)
                try:
                    contato_nome = self._contato_sel.get('usuario_nome') if isinstance(self._contato_sel, dict) else None
                    ids_para_marcar = [
                        m.get('id') for m in nao_lidas
                        if m and isinstance(m, dict)
                        and m.get('id') is not None
                        and (contato_nome is None or m.get('remetente_nome') == contato_nome)
                    ]
                    if ids_para_marcar:
                        self.chatdb.marcar_lidas(ids_para_marcar)
                        if hasattr(self.controller, 'notify_chat_unread'):
                            restante = max(0, total - len(ids_para_marcar))
                            self.controller.notify_chat_unread(restante)
                except Exception as e:
                    print(f"Erro ao marcar mensagens como lidas: {e}")
        except Exception as e:
            print(f"Erro ao verificar mensagens: {e}")
            # Tenta reconectar
            try:
                self.conn = db.get_connection()
                self.chatdb = ChatDB(self.conn)
            except Exception as e2:
                print(f"Falha ao reconectar ao banco: {e2}")
        
        # Agenda próxima verificação (1 segundo)
        try:
            if self._poll_job:
                self.frame.after_cancel(self._poll_job)
            self._poll_job = self.frame.after(1000, self._poll_messages)
        except Exception as e:
            print(f"Erro ao agendar verificação de mensagens: {e}")
            self._poll_job = None

    def _poll_online(self):
        try:
            # Verifica se o usuário está logado
            if not hasattr(self, 'me_id') or self.me_id is None:
                # Tenta obter do controller.usuario
                if hasattr(self.controller, 'usuario'):
                    self.me_id = getattr(self.controller.usuario, 'id', None)
                    self.me_nome = getattr(self.controller.usuario, 'nome', 'Usuário')
                
                # Se ainda não tem ID, aguarda
                if self.me_id is None:
                    print("Poll online: Usuário não logado, aguardando...")
                    # Agenda próxima verificação
                    self.frame.after(3000, self._poll_online)
                    return
            
            # Atualiza a lista de usuários online
            self._refresh_online()
        except Exception as e:
            print(f"Erro ao atualizar lista de online: {e}")
            # Tenta reconectar
            try:
                self.conn = db.get_connection()
                self.chatdb = ChatDB(self.conn)
            except Exception as e2:
                print(f"Falha ao reconectar ao banco: {e2}")
        
        # Agenda próxima verificação (1s)
        try:
            self.frame.after(1000, self._poll_online)
        except Exception as e:
            print(f"Erro ao agendar verificação de online: {e}")

    def _stop_polling_and_heartbeat(self):
        # Para o polling de mensagens
        if self._poll_job:
            try:
                self.frame.after_cancel(self._poll_job)
                self._poll_job = None
            except Exception:
                pass
        # Para o heartbeat
        if self._hb_job:
            try:
                self.frame.after_cancel(self._hb_job)
                self._hb_job = None
            except Exception:
                pass

    # ------------------------- UI Actions -------------------------
    def _refresh_online(self):
        # Limpa lista
        if hasattr(self, 'lista_contatos') and self.lista_contatos:
            for w in list(self.lista_contatos.winfo_children()):
                w.destroy()
        try:
            # Lista todas as sessões (sem filtro de tempo)
            online = self.chatdb.listar_online()
            if len(online) == 0:
                # Se não encontrou ninguém, pode ser um problema de conexão
                # Tenta reconectar e buscar novamente
                try:
                    self.conn = db.get_connection()
                    self.chatdb = ChatDB(self.conn)
                    online = self.chatdb.listar_online()
                except Exception as e:
                    print(f"Erro ao reconectar para buscar usuários online: {e}")
        except Exception as e:
            print(f"Erro ao listar usuários online: {e}")
            online = []

        # Atualiza contador no cabeçalho (exclui o próprio usuário)
        try:
            total_exibidos = 0
            if online:
                for u in online:
                    uid = None
                    try:
                        uid = u.get('usuario_id')
                    except Exception:
                        try:
                            uid = u[0] if len(u) > 0 else None
                        except Exception:
                            uid = None
                    if self.me_id is not None and uid == self.me_id:
                        continue
                    total_exibidos += 1
            if hasattr(self, 'left_header') and self.left_header:
                self.left_header.config(text=f"Usuários Online ({total_exibidos})")
        except Exception:
            pass

        # Adiciona botões de contato (exceto eu mesmo)
        for user in online:
            try:
                uid = user.get('usuario_id')
                nome = user.get('usuario_nome') or 'Usuário'
                disp = user.get('dispositivo')
            except Exception:
                uid = user[0] if len(user) > 0 else None
                nome = user[1] if len(user) > 1 else 'Usuário'
                disp = user[2] if len(user) > 2 else None

            # Pula o próprio usuário
            if (uid is not None and self.me_id is not None and uid == self.me_id) or (uid is None and nome == self.me_nome):
                continue

            contato = {'usuario_id': uid, 'usuario_nome': nome, 'dispositivo': disp}
            btn = tk.Button(
                self.lista_contatos,
                text=nome,
                font=("Arial", 11),
                bg='#ffffff',
                fg='#333333',
                activebackground='#e6e6e6',
                activeforeground='#333333',
                relief='flat',
                anchor='w',
                padx=8, pady=6,
                command=lambda c=contato: self._selecionar_contato(c)
            )
            btn.pack(fill='x', pady=1)

    def _selecionar_contato(self, contato: dict):
        self._contato_sel = contato
        self._carregar_conversa(contato)

    def _carregar_conversa(self, contato: dict):
        # Atualiza label de conversa
        try:
            nome = contato.get('usuario_nome', 'Usuário')
            if hasattr(self, 'lbl_conversa') and self.lbl_conversa:
                self.lbl_conversa.config(text=f'Conversa com {nome}')
        except Exception:
            pass

        # Busca mensagens
        try:
            msgs = self.chatdb.listar_conversa(
                self.me_id, self.me_nome, self.me_disp,
                contato.get('usuario_id'), contato.get('usuario_nome'), contato.get('dispositivo')
            )
        except Exception:
            msgs = []

        # Atualiza área de texto
        if hasattr(self, 'txt_mensagens') and self.txt_mensagens:
            self.txt_mensagens.config(state='normal')
            self.txt_mensagens.delete(1.0, 'end')

            for msg in msgs:
                try:
                    remetente_nome = msg.get('remetente_nome', 'Usuário')
                    texto = msg.get('texto', '')
                    criado_em = msg.get('criado_em')
                    hora = criado_em.strftime('%H:%M') if criado_em else ''
                    # Linha única, tudo alinhado à esquerda, fundo branco e texto preto
                    linha = f"{remetente_nome} {hora}: {texto}\n"
                    self.txt_mensagens.insert('end', linha, 'linha_msg')
                except Exception:
                    continue

            # Configura tag única para todas as mensagens (preto no branco, alinhado à esquerda)
            self.txt_mensagens.tag_configure('linha_msg', foreground='#000000', background='#ffffff', justify='left', lmargin1=4, lmargin2=4, spacing1=2, spacing3=2)

            # Rola para o final
            self.txt_mensagens.config(state='disabled')
            self.txt_mensagens.see('end')

    def _on_enter(self, event):
        self._enviar()

    def _enviar(self):
        # Verifica se há contato selecionado
        if not self._contato_sel:
            return

        # Obtém texto
        texto = self.entry_msg.get().strip()
        if not texto:
            return

        # Limpa campo
        self.entry_msg.delete(0, 'end')

        # Envia mensagem
        try:
            self.chatdb.enviar_mensagem(
                self.me_id, self.me_nome, self.me_disp,
                self._contato_sel.get('usuario_id'), self._contato_sel.get('usuario_nome'), self._contato_sel.get('dispositivo'),
                texto
            )
            # Recarrega conversa
            self._carregar_conversa(self._contato_sel)
        except Exception:
            pass
