import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import webbrowser
import tempfile
import os
from src.utils.impressao import GerenciadorImpressao
from src.controllers.financeiro_controller import FinanceiroController
from src.config.estilos import aplicar_estilo, CORES, FONTES
from src.views.modulos.financeiro.contaspagar_module import ContasPagarModule
from src.views.modulos.financeiro.contasreceber_module import ContasReceberModule
from src.views.modulos.financeiro.relatorios_module import RelatoriosModule
from src.views.modulos.financeiro.estoque_module import EstoqueModule

class FinanceiroModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.frame = ttk.Frame(parent)
        self.current_view = None
        self.financeiro_controller = None
        
        # Opções do menu lateral
        self.opcoes = [
            {"nome": "Caixa", "acao": "caixa"},
            {"nome": "Contas a Pagar", "acao": "contas_pagar"},
            {"nome": "Contas a Receber", "acao": "contas_receber"},
            {"nome": "Relatórios", "acao": "relatorios"},
            {"nome": "Estoque", "acao": "estoque"}
        ]
        
    def get_opcoes(self):
        """Retorna a lista de opções para a barra lateral"""
        return self.opcoes
        
    def show(self, acao=None):
        if self.current_view:
            self.current_view.destroy()
            
        if acao == 'caixa':
            self._show_caixa()
        elif acao == 'contas_pagar':
            self._show_contas_pagar()
        elif acao == 'contas_receber':
            self._show_contas_receber()
        elif acao == 'relatorios':
            self._show_relatorios()
        elif acao == 'estoque':
            self._show_estoque()
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo financeiro
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção no menu lateral para começar.", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
        # Badge do status do caixa abaixo da frase
        try:
            # Obtém conexão do controller principal, se houver
            db_conn = None
            for attr in ('db_connection', 'db'):
                if hasattr(self.controller, attr):
                    db_conn = getattr(self.controller, attr)
                    if db_conn:
                        break
            fc = FinanceiroController(db_conn)
            sessao = None
            try:
                sessao = fc.get_sessao_aberta()
            except Exception:
                sessao = None
            aberto = bool(sessao)
            badge = tk.Label(
                self.frame,
                text=("CAIXA ABERTO" if aberto else "CAIXA FECHADO"),
                font=("Arial", 16, 'bold'),
                bg=(CORES.get('destaque', '#4CAF50') if aberto else CORES.get('alerta', '#f44336')),
                fg=CORES.get('texto_claro', '#ffffff'),
                padx=40,
                pady=12,
                bd=0,
                relief='flat',
            )
            badge.pack()
        except Exception:
            pass
    
    def _show_caixa(self):
        # Define a cor base a partir do container pai para harmonizar com o layout
        try:
            bg_base = self.parent.cget("bg")
        except Exception:
            bg_base = CORES["fundo_conteudo"]

        frame = tk.Frame(self.frame, bg=bg_base)
        tk.Label(frame, text="Caixa", font=FONTES["subtitulo"], bg=bg_base, fg=CORES["texto"]).pack(pady=(10, 5), anchor='w')

        # Coluna esquerda com botões
        left_col = tk.Frame(frame, bg=bg_base)
        left_col.pack(side='left', anchor='n', padx=10, pady=5, fill='y')

        # Estilo de botões padronizado (igual ao módulo Cadastro > Usuários)
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 15,
        }

        # Botões principais empilhados
        # Botão 'Fundo de Caixa' removido conforme solicitação

        self.btn_abrir = tk.Button(left_col, text="Abrir Caixa", command=self._on_abrir_caixa, **btn_style)
        self.btn_abrir.pack(fill='x', pady=4)

        self.btn_lancar_pagto = tk.Button(left_col, text="Lançar Pagamento", command=self._on_lancar_pagamento, **btn_style)
        self.btn_lancar_pagto.pack(fill='x', pady=4)

        # Novo: botão para lançar despesas (saídas)
        self.btn_despesa = tk.Button(left_col, text="Lançar Despesa", command=self._on_lancar_despesa, **btn_style)
        self.btn_despesa.pack(fill='x', pady=4)

        self.btn_fechar = tk.Button(left_col, text="Fechar Caixa", command=self._on_fechar_caixa, **btn_style)
        self.btn_fechar.pack(fill='x', pady=4)

        # Área direita: status centralizado como um "badge"
        right_space = tk.Frame(frame, bg=bg_base)
        right_space.pack(side='left', fill='both', expand=True)

        status_center = tk.Frame(right_space, bg=bg_base)
        status_center.pack(fill='x', pady=(10, 0))

        # Badge de status (inicialmente neutro, será configurado em _refresh_caixa_state)
        self.status_badge = tk.Label(
            status_center,
            text="Status...",
            font=("Arial", 16, 'bold'),
            bg=bg_base,
            fg=CORES["texto"],
            padx=40,
            pady=12,
            bd=0,
            relief='flat',
            highlightthickness=0,
        )
        # Exibe no topo e centraliza horizontalmente
        self.status_badge.pack()

        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
        # Atualiza imediatamente o badge de status ao entrar na tela de Caixa
        try:
            self._refresh_caixa_state()
        except Exception:
            pass

    def _show_contas_pagar(self):
        """Tela de Contas a Pagar"""
        try:
            # Limpa view atual
            if self.current_view:
                try:
                    self.current_view.destroy()
                except Exception:
                    pass

            # Instancia o módulo de Contas a Pagar seguindo o mesmo padrão de layout
            modulo = ContasPagarModule(self.frame, self.controller)
            modulo.frame.pack(fill='both', expand=True, padx=20, pady=20)
            self.current_view = modulo.frame
            # Guarda referência (opcional) para interações futuras
            self._contas_pagar_module = modulo

            # Atualiza estado dos botões conforme sessão (protegido)
            try:
                self._refresh_caixa_state()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Contas a Pagar", f"Falha ao abrir a tela: {e}")

    def _show_contas_receber(self):
        """Tela de Contas a Receber"""
        try:
            # Limpa view atual
            if self.current_view:
                try:
                    self.current_view.destroy()
                except Exception:
                    pass

            # Instancia o módulo de Contas a Receber seguindo o mesmo padrão de layout
            modulo = ContasReceberModule(self.frame, self.controller)
            modulo.frame.pack(fill='both', expand=True, padx=20, pady=20)
            self.current_view = modulo.frame
            # Guarda referência (opcional)
            self._contas_receber_module = modulo

            # Atualiza estado dos botões conforme sessão (protegido)
            try:
                self._refresh_caixa_state()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Contas a Receber", f"Falha ao abrir a tela: {e}")

    def _show_relatorios(self):
        """Tela de Relatórios"""
        try:
            # Limpa view atual
            if self.current_view:
                try:
                    self.current_view.destroy()
                except Exception:
                    pass

            # Instancia o módulo de Relatórios seguindo o mesmo padrão
            modulo = RelatoriosModule(self.frame, self.controller)
            modulo.frame.pack(fill='both', expand=True, padx=20, pady=20)
            self.current_view = modulo.frame
            # Guarda referência (opcional)
            self._relatorios_module = modulo

            # Atualiza estado do caixa (se aplicável)
            try:
                self._refresh_caixa_state()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Relatórios", f"Falha ao abrir a tela: {e}")

    def _show_estoque(self):
        """Tela de Estoque"""
        try:
            # Limpa view atual
            if self.current_view:
                try:
                    self.current_view.destroy()
                except Exception:
                    pass

            # Instancia o módulo de Estoque seguindo o mesmo padrão
            modulo = EstoqueModule(self.frame, self.controller)
            modulo.frame.pack(fill='both', expand=True, padx=20, pady=20)
            self.current_view = modulo.frame
            # Guarda referência (opcional)
            self._estoque_module = modulo

            # Atualiza estado do caixa (se aplicável)
            try:
                self._refresh_caixa_state()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Estoque", f"Falha ao abrir a tela: {e}")

    # ----------------- Handlers e Helpers do Caixa -----------------
    def _center_window(self, win, w, h):
        try:
            top = self.parent.winfo_toplevel()
        except Exception:
            top = win
        top.update_idletasks()
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

    def _parse_currency_br(self, text: str):
        if text is None:
            return None
        s = str(text).strip()
        if not s:
            return None
        # Remove separadores de milhar e troca vírgula por ponto
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            return None

    def _update_status_badge(self, aberto: bool):
        """Atualiza o badge de status com estilo tipo 'neon'."""
        try:
            if aberto:
                text = "CAIXA ABERTO"
                bg = CORES.get('sucesso', '#4caf50')
            else:
                text = "CAIXA FECHADO"
                bg = CORES.get('alerta', '#f44336')
            self.status_badge.config(
                text=text,
                bg=bg,
                fg='white',
                font=('Arial', 16, 'bold'),
                padx=40,
                pady=12,
                bd=0,
                relief='flat',
                cursor='arrow'
            )
        except Exception:
            pass

    def _dialog_fundo_caixa(self):
        # Fundo de Caixa com vírgula, janela maior e botões estilizados
        dlg = tk.Toplevel(self.parent)
        dlg.title("Fundo de Caixa")
        dlg.configure(bg=self.parent.cget("bg"))
        dlg.transient(self.parent)
        dlg.grab_set()
        # Mais espaço lateral
        self._center_window(dlg, 560, 240)

        bg_base = self.parent.cget("bg")
        title = tk.Label(dlg, text="Definir Fundo de Caixa", font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"])
        title.pack(padx=20, pady=(20, 10), anchor='w')

        frm = tk.Frame(dlg, bg=bg_base)
        frm.pack(fill='both', expand=True, padx=20)

        lbl = tk.Label(frm, text="Informe o valor (use vírgula):", font=("Arial", 10, 'bold'), bg=bg_base, fg=CORES["texto"])
        lbl.pack(anchor='w')

        valor_var = tk.StringVar(value="")
        ent = tk.Entry(frm, textvariable=valor_var, font=("Arial", 10))
        ent.pack(fill='x', pady=8)
        ent.focus_set()

        btns = tk.Frame(dlg, bg=bg_base)
        btns.pack(fill='x', padx=20, pady=(10, 20))

        def on_confirm():
            valor = self._parse_currency_br(valor_var.get())
            if valor is None or valor < 0:
                messagebox.showwarning("Valor inválido", "Informe um valor numérico válido.")
                return
            try:
                fc = self._get_financeiro_controller()
                if fc.get_sessao_aberta():
                    messagebox.showwarning("Fundo de Caixa", "O caixa já está aberto. Feche o caixa para alterar o fundo inicial.")
                    return
                sessao_id = fc.abrir_caixa(
                    valor_inicial=valor,
                    usuario_id=getattr(self.controller, 'usuario_id', None),
                    usuario_nome=getattr(self.controller, 'usuario_nome', None)
                )
                if sessao_id:
                    messagebox.showinfo("Caixa", f"Caixa aberto com fundo de R$ {valor:.2f}. Sessão #{sessao_id}")
                else:
                    messagebox.showerror("Caixa", "Não foi possível abrir o caixa.")
                self._refresh_caixa_state()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao definir fundo de caixa: {e}")
            finally:
                dlg.destroy()

        def on_cancel():
            dlg.destroy()

        # Mesma largura para os dois botões
        btn_ok = tk.Button(btns, text="Confirmar", command=on_confirm, width=14)
        aplicar_estilo(btn_ok, 'sucesso')
        btn_ok.pack(side='right', padx=5)

        btn_cancel = tk.Button(btns, text="Cancelar", command=on_cancel, width=14)
        aplicar_estilo(btn_cancel, 'perigo')
        btn_cancel.pack(side='right', padx=5)

        dlg.bind('<Return>', lambda e: on_confirm())
        dlg.bind('<Escape>', lambda e: on_cancel())

    def _get_financeiro_controller(self) -> FinanceiroController:
        if self.financeiro_controller:
            return self.financeiro_controller
        # Tenta obter conexão do controller principal
        db_conn = None
        if hasattr(self.controller, 'db_connection'):
            db_conn = getattr(self.controller, 'db_connection')
        elif hasattr(self.controller, 'db'):
            db_conn = getattr(self.controller, 'db')
        if db_conn is None:
            try:
                from src.db.database import db as default_db
                db_conn = default_db
            except Exception:
                db_conn = None
        self.financeiro_controller = FinanceiroController(db_conn)
        # Define usuário padrão no controller financeiro, se disponível no controller principal
        try:
            uid = getattr(self.controller, 'usuario_id', None)
            uname = getattr(self.controller, 'usuario_nome', None)
            if hasattr(self.financeiro_controller, 'set_usuario'):
                self.financeiro_controller.set_usuario(uid, uname)
            # Vincula esta view ao controller financeiro para fallback de usuário
            if hasattr(self.financeiro_controller, 'configurar_view'):
                self.financeiro_controller.configurar_view(self)
        except Exception:
            pass
        return self.financeiro_controller

    def _refresh_caixa_state(self):
        fc = self._get_financeiro_controller()
        sessao = fc.get_sessao_aberta()
        aberto = bool(sessao)
        # Atualiza badge central (sem exibir ID da sessão)
        self._update_status_badge(aberto)

        # Ajusta botões
        try:
            if aberto:
                self.btn_lancar_pagto.config(state='normal')
                self.btn_despesa.config(state='normal')
                self.btn_abrir.config(state='disabled')
                self.btn_fechar.config(state='normal')
            else:
                self.btn_lancar_pagto.config(state='disabled')
                self.btn_despesa.config(state='disabled')
                self.btn_abrir.config(state='normal')
                self.btn_fechar.config(state='disabled')
        except Exception:
            pass

    def _on_abrir_caixa(self):
        """Abre o caixa solicitando o valor inicial (permite R$ 0,00) em janela estilizada."""
        try:
            fc = self._get_financeiro_controller()
            if fc.get_sessao_aberta():
                messagebox.showinfo("Caixa", "Já existe um caixa aberto.")
                return
            # Janela maior e centralizada para confirmar abertura
            dlg = tk.Toplevel(self.parent)
            dlg.title("Abrir Caixa")
            bg_base = self.parent.cget("bg")
            dlg.configure(bg=bg_base)
            dlg.transient(self.parent)
            dlg.grab_set()
            # Mais espaço lateral
            self._center_window(dlg, 600, 260)

            # Título no padrão do diálogo de lançamento
            tk.Label(
                dlg,
                text="Abrir Caixa",
                font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"]
            ).pack(padx=20, pady=(20, 10), anchor='w')

            # Campo para fundo de caixa
            form = tk.Frame(dlg, bg=bg_base)
            form.pack(fill='x', padx=20, pady=(0, 8))
            tk.Label(form, text="Fundo do Caixa (R$):", font=("Arial", 10), bg=bg_base, fg=CORES["texto"]).grid(row=0, column=0, sticky='w')
            # Sem valor padrão para não atrapalhar a digitação
            valor_ini_var = tk.StringVar(value="")
            ent_valor_ini = tk.Entry(form, textvariable=valor_ini_var, font=("Arial", 12))
            ent_valor_ini.grid(row=0, column=1, sticky='ew', padx=(10, 0))
            form.grid_columnconfigure(1, weight=1)
            ent_valor_ini.focus_set()

            btns = tk.Frame(dlg, bg=bg_base)
            btns.pack(fill='x', padx=20, pady=(15, 20))

            def do_open():
                try:
                    valor_inicial = self._parse_currency_br(valor_ini_var.get())
                    if valor_inicial is None or valor_inicial < 0:
                        messagebox.showwarning("Valor inválido", "Informe um valor numérico válido (use vírgula para decimais).")
                        return
                    sessao_id = fc.abrir_caixa(
                        valor_inicial=valor_inicial,
                        usuario_id=getattr(self.controller, 'usuario_id', None),
                        usuario_nome=getattr(self.controller, 'usuario_nome', None)
                    )
                    if not sessao_id:
                        messagebox.showerror("Caixa", "Não foi possível abrir o caixa.")
                    self._refresh_caixa_state()
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao abrir caixa: {e}")
                finally:
                    dlg.destroy()

            def cancel():
                dlg.destroy()

            # Botões no padrão do módulo Cadastro
            btn_ok = tk.Button(btns, text="Abrir", command=do_open, width=14)
            aplicar_estilo(btn_ok, 'sucesso')
            btn_ok.pack(side='right', padx=5)

            btn_cancel = tk.Button(btns, text="Cancelar", command=cancel, width=14)
            aplicar_estilo(btn_cancel, 'perigo')
            btn_cancel.pack(side='right', padx=5)

            dlg.bind('<Return>', lambda e: do_open())
            dlg.bind('<Escape>', lambda e: cancel())
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir caixa: {e}")

    def _on_fundo_caixa(self):
        """Define o fundo de caixa com suporte a vírgula, em janela estilizada."""
        self._dialog_fundo_caixa()

    def _on_lancar_pagamento(self):
        """Abre um diálogo completo para lançar movimento (pagamento/recebimento)."""
        try:
            fc = self._get_financeiro_controller()
            if not fc.get_sessao_aberta():
                messagebox.showwarning("Lançar Movimento", "Abra o caixa antes de lançar um movimento.")
                return

            dlg = tk.Toplevel(self.parent)
            dlg.title("Lançar Movimento")
            bg_base = self.parent.cget("bg")
            dlg.configure(bg=bg_base)
            dlg.transient(self.parent)
            dlg.grab_set()
            self._center_window(dlg, 720, 520)

            title = tk.Label(dlg, text="Lançamento Financeiro", font=FONTES["grande"], bg=bg_base, fg=CORES["texto"]) 
            title.pack(padx=20, pady=(20, 10), anchor='w')

            form = tk.Frame(dlg, bg=bg_base)
            form.pack(fill='both', expand=True, padx=20)

            # Linhas/colunas
            # Tipo fixo: recebimento (campo removido da UI)
            tipo_fixo = "recebimento"

            # 2) Forma de pagamento
            tk.Label(form, text="Forma:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=1, column=0, sticky='w', pady=4)
            forma_var = tk.StringVar(value="dinheiro")
            forma_cb = ttk.Combobox(form, textvariable=forma_var, values=[
                "dinheiro", "pix", "cartao_credito", "cartao_debito", "outro"
            ], state="readonly")
            forma_cb.grid(row=1, column=1, sticky='ew', padx=8, pady=4)

            # 3) Valor
            tk.Label(form, text="Valor (R$):", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=2, column=0, sticky='w', pady=4)
            valor_var = tk.StringVar(value="")
            valor_ent = tk.Entry(form, textvariable=valor_var, font=("Arial", 12))
            valor_ent.grid(row=2, column=1, sticky='ew', padx=8, pady=4)

            # 4) Status
            tk.Label(form, text="Status:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=3, column=0, sticky='w', pady=4)
            status_var = tk.StringVar(value="pago")
            status_cb = ttk.Combobox(form, textvariable=status_var, values=["pago", "aberto"], state="readonly")
            status_cb.grid(row=3, column=1, sticky='ew', padx=8, pady=4)

            # 4) Data da consulta a listar no combo (permite lançar hoje pagamentos de datas futuras/passadas)
            tk.Label(form, text="Data:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=4, column=0, sticky='w', pady=4)
            data_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
            data_row = tk.Frame(form, bg=bg_base)
            data_row.grid(row=4, column=1, sticky='ew', padx=8, pady=4)
            data_entry = tk.Entry(data_row, textvariable=data_var, font=("Arial", 12))
            data_entry.pack(side='left', fill='x', expand=True)
            btn_carregar = tk.Button(data_row, text="Carregar", cursor='hand2')
            aplicar_estilo(btn_carregar, 'primario') if 'aplicar_estilo' in globals() else None
            btn_carregar.pack(side='left', padx=(6, 0))

            # 5) Consultas da data escolhida (preenche automaticamente Paciente/Médico; IDs ficam ocultos)
            tk.Label(form, text="Consulta:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=5, column=0, sticky='w', pady=4)
            consultas_map = {}
            consulta_opts = []
            consulta_var = tk.StringVar()
            consulta_cb = ttk.Combobox(form, textvariable=consulta_var, values=consulta_opts, state="readonly")
            consulta_cb.grid(row=5, column=1, sticky='ew', padx=8, pady=4)

            def load_consultas_for_date():
                nonlocal consultas_map, consulta_opts
                try:
                    consultas_map = {}
                    consulta_opts = []
                    data_escolhida = (data_var.get() or "").strip()
                    # Converte data BR (DD/MM/AAAA) para ISO (AAAA-MM-DD) para consulta no controller
                    data_query = None
                    if data_escolhida:
                        try:
                            # Tenta converter do formato brasileiro
                            dt = datetime.strptime(data_escolhida, '%d/%m/%Y')
                            data_query = dt.strftime('%Y-%m-%d')
                        except Exception:
                            # Se já vier em ISO válido, usa direto; senão, deixa None
                            try:
                                dt = datetime.strptime(data_escolhida, '%Y-%m-%d')
                                data_query = data_escolhida
                            except Exception:
                                data_query = None
                    consultas = fc.listar_consultas_do_dia(data_query if data_query else None)
                    for c in (consultas or []):
                        hora_str = str(c.get('hora')) if c.get('hora') is not None else '--:--'
                        ta = c.get('tipo_atendimento') or ''
                        label = f"{hora_str} - {c.get('paciente_nome','')} - {c.get('medico_nome','')}" + (f" - {ta}" if ta else "")
                        consulta_opts.append(label)
                        consultas_map[label] = {
                            'consulta_id': c.get('consulta_id'),
                            'paciente_id': c.get('paciente_id'),
                            'medico_id': c.get('medico_id'),
                            'paciente_nome': c.get('paciente_nome'),
                            'medico_nome': c.get('medico_nome'),
                            'tipo_atendimento': ta,
                            'valor_exame': c.get('valor_exame'),
                            'hora': c.get('hora'),
                        }
                    # Atualiza combobox
                    if consulta_opts:
                        consulta_cb.configure(values=consulta_opts, state='readonly')
                        consulta_var.set(consulta_opts[0])
                        on_consulta_change()
                    else:
                        consulta_cb.configure(values=["Nenhuma consulta para a data"], state='disabled')
                        consulta_var.set("")
                except Exception:
                    consulta_cb.configure(values=["Nenhuma consulta"], state='disabled')
                    consulta_var.set("")

            btn_carregar.configure(command=load_consultas_for_date)

            # Variáveis ocultas para IDs e nomes (precisam existir antes do callback)
            paciente_id_var = tk.StringVar()
            consulta_id_var = tk.StringVar()
            medico_id_var = tk.StringVar()
            paciente_nome_var = tk.StringVar()
            medico_nome_var = tk.StringVar()

            def on_consulta_change(event=None):
                sel = consulta_var.get()
                info = consultas_map.get(sel)
                if not info:
                    return
                paciente_id_var.set(str(info.get('paciente_id') or ''))  # oculto
                consulta_id_var.set(str(info.get('consulta_id') or ''))  # oculto
                medico_id_var.set(str(info.get('medico_id') or ''))      # oculto
                paciente_nome_var.set(str(info.get('paciente_nome') or ''))
                medico_nome_var.set(str(info.get('medico_nome') or ''))
                # Auto-preenche o valor do exame/consulta, se disponível
                try:
                    v = info.get('valor_exame')
                    if v is not None:
                        # Formata para padrão BR (vírgula)
                        valor_var.set(f"{float(v):.2f}".replace('.', ','))
                except Exception:
                    pass

            consulta_cb.bind('<<ComboboxSelected>>', on_consulta_change)
            # Carrega consultas da data padrão (hoje) e pré-seleciona primeira se houver
            load_consultas_for_date()

            # 6) Campos visuais para nomes (readonly), preenchidos automaticamente
            tk.Label(form, text="Paciente:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=6, column=0, sticky='w', pady=4)
            paciente_nome_ent = tk.Entry(
                form,
                textvariable=paciente_nome_var,
                state='disabled',
                disabledbackground='white',
                disabledforeground=CORES.get('texto', '#000')
            )
            paciente_nome_ent.grid(row=6, column=1, sticky='ew', padx=8, pady=4)

            tk.Label(form, text="Médico:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=7, column=0, sticky='w', pady=4)
            medico_nome_ent = tk.Entry(
                form,
                textvariable=medico_nome_var,
                state='disabled',
                disabledbackground='white',
                disabledforeground=CORES.get('texto', '#000')
            )
            medico_nome_ent.grid(row=7, column=1, sticky='ew', padx=8, pady=4)

            # 7) Descrição
            tk.Label(form, text="Descrição:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=8, column=0, sticky='nw', pady=4)
            desc_txt = tk.Text(form, height=4, wrap='word')
            desc_txt.grid(row=9, column=1, sticky='nsew', padx=8, pady=4)

            # Grid config
            form.columnconfigure(1, weight=1)
            for r in range(10):
                form.rowconfigure(r, weight=0)
            form.rowconfigure(9, weight=1)

            # Botões
            btns = tk.Frame(dlg, bg=bg_base)
            btns.pack(fill='x', padx=20, pady=(10, 20))

            def parse_int_or_none(s):
                s = (s or "").strip()
                if not s:
                    return None
                try:
                    return int(s)
                except Exception:
                    return None

            def on_confirm():
                try:
                    # Validar
                    forma = forma_var.get().strip().lower()
                    if forma not in {"dinheiro", "pix", "cartao_credito", "cartao_debito", "outro"}:
                        messagebox.showwarning("Forma inválida", "Escolha uma forma válida.")
                        return
                    valor = self._parse_currency_br(valor_var.get())
                    if valor is None or valor <= 0:
                        messagebox.showwarning("Valor inválido", "Informe um valor maior que zero.")
                        return
                    tipo_escolhido = "recebimento"
                    status = status_var.get().strip().lower()
                    descricao = (desc_txt.get("1.0", "end").strip())
                    paciente_id = parse_int_or_none(paciente_id_var.get())
                    consulta_id = parse_int_or_none(consulta_id_var.get())
                    medico_id = parse_int_or_none(medico_id_var.get())
                    # Captura o tipo de atendimento da consulta selecionada para salvar como motivo (exame/consulta)
                    sel_label = consulta_var.get()
                    info_sel = consultas_map.get(sel_label) if sel_label else None
                    exame_consulta = (info_sel or {}).get('tipo_atendimento')
                    # Se a descrição estiver vazia, usa o exame/consulta como descrição
                    if not descricao and exame_consulta:
                        descricao = exame_consulta

                    # Monta dados do comprovante (preview) e posterga o lançamento até a finalização
                    # Extrai hora da consulta e nome do procedimento/consulta
                    hora_sel = None
                    nome_consulta = None
                    if info_sel:
                        try:
                            hora_sel = info_sel.get('hora')
                        except Exception:
                            hora_sel = None
                        nome_consulta = info_sel.get('tipo_atendimento') or None
                    # Fallback: tenta extrair da label (formato "HH:MM - ... - tipo")
                    if not hora_sel:
                        try:
                            part = (sel_label or '').split(' - ')[0]
                            hora_sel = part if part else None
                        except Exception:
                            pass
                    if not nome_consulta:
                        try:
                            # pega último segmento como tipo
                            parts = (sel_label or '').split(' - ')
                            nome_consulta = parts[-1] if parts else None
                        except Exception:
                            pass

                    recibo = {
                        'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'hora_consulta': str(hora_sel or '').strip(),
                        'paciente': paciente_nome_var.get() or '-',
                        'medico': medico_nome_var.get() or '-',
                        'tipo': (nome_consulta or descricao or '-'),
                        'forma': forma,
                        'valor': f"R$ {float(valor):.2f}".replace('.', ','),
                        'descricao': descricao or '-',
                        'status': status,
                    }
                    # Prepara payload do lançamento para ser executado ao finalizar
                    lancamento = {
                        'tipo': tipo_escolhido,
                        'tipo_pagamento': forma,
                        'valor': float(valor),
                        'descricao': descricao,
                        'usuario_id': getattr(self.controller, 'usuario_id', None),
                        'paciente_id': paciente_id,
                        'consulta_id': consulta_id,
                        'medico_id': medico_id,
                        'status': status,
                    }
                    try:
                        # Passa o controller já configurado (com sessão aberta) para a tela de preview
                        self._show_receipt_preview(recibo, lancamento, fc)
                    except Exception:
                        messagebox.showerror("Financeiro", "Falha ao abrir a pré-visualização do comprovante.")
                    dlg.destroy()
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao registrar lançamento: {e}")

            def on_cancel():
                dlg.destroy()

            btn_style = {
                'font': ('Arial', 10, 'bold'),
                'bg': '#4a6fa5',
                'fg': 'white',
                'bd': 0,
                'padx': 20,
                'pady': 8,
                'relief': 'flat',
                'cursor': 'hand2',
                'width': 15,
            }
            btn_ok = tk.Button(btns, text="Confirmar", command=on_confirm, **btn_style)
            btn_ok.pack(side='right', padx=5)

            btn_cancel = tk.Button(btns, text="Cancelar", command=on_cancel, **btn_style)
            btn_cancel.pack(side='right', padx=5)

            dlg.bind('<Return>', lambda e: on_confirm())
            dlg.bind('<Escape>', lambda e: on_cancel())
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir diálogo de lançamento: {e}")

    def _show_receipt_preview(self, recibo: dict, lancamento: dict, fc: FinanceiroController):
        """Exibe uma janela de pré-visualização do comprovante e permite finalizar com ou sem impressão.
        Usa o mesmo FinanceiroController (com sessão aberta) para efetivar o lançamento.
        """
        win = tk.Toplevel(self.parent)
        win.title("Comprovante de Pagamento")
        bg_base = self.parent.cget("bg")
        win.configure(bg=bg_base)
        win.transient(self.parent)
        win.grab_set()
        # Centraliza a janela de pré-visualização sem alterar o tamanho
        try:
            win.update_idletasks()
            w = win.winfo_width() or win.winfo_reqwidth()
            h = win.winfo_height() or win.winfo_reqheight()
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = int((sw - w) / 2)
            y = int((sh - h) / 2)
            win.geometry(f"+{x}+{y}")
        except Exception:
            pass

        titulo = tk.Label(win, text="Clínica - Comprovante de Pagamento", font=("Arial", 16, 'bold'), bg=bg_base, fg=CORES["texto"]) 
        titulo.pack(padx=20, pady=(20, 10))

        # Corpo do comprovante (visual simples)
        frame = tk.Frame(win, bg=bg_base)
        frame.pack(fill='both', expand=True, padx=20)

        txt = tk.Text(frame, wrap='word')
        txt.tag_configure('center', justify='center')
        txt.pack(fill='both', expand=True)
        linhas = []
        linhas.append(f"Data/Hora: {recibo.get('data_hora','-')}")
        if recibo.get('hora_consulta'):
            linhas.append(f"Hora da Consulta: {recibo.get('hora_consulta')}")
        if recibo.get('paciente'):
            linhas.append(f"Paciente: {recibo.get('paciente')}")
        if recibo.get('medico'):
            linhas.append(f"Médico: {recibo.get('medico')}")
        if recibo.get('tipo'):
            linhas.append(" ")
            linhas.append(str(recibo.get('tipo')))
            linhas.append(" ")
        linhas.append(f"Forma: {recibo.get('forma','-').upper()}")
        linhas.append(f"Valor: {recibo.get('valor','-')}")
        linhas.append(f"Status: {recibo.get('status','-').upper()}")
        linhas.append(f"Descrição: {recibo.get('descricao','-')}")
        txt.insert('1.0', "\n".join(linhas))
        txt.tag_add('center', '1.0', 'end')
        txt.configure(state='disabled')

        # Botões
        btns = tk.Frame(win, bg=bg_base)
        btns.pack(fill='x', padx=20, pady=(10, 20))

        def finalizar_e_imprimir():
            """Efetiva o lançamento e, em seguida, imprime via GerenciadorImpressao."""
            try:
                # 1) Registrar movimento usando o controller já configurado
                mid = fc.registrar_movimento(
                    tipo=lancamento['tipo'],
                    tipo_pagamento=lancamento['tipo_pagamento'],
                    valor=lancamento['valor'],
                    descricao=lancamento['descricao'],
                    usuario_id=lancamento['usuario_id'],
                    paciente_id=lancamento['paciente_id'],
                    consulta_id=lancamento['consulta_id'],
                    medico_id=lancamento['medico_id'],
                    status=lancamento['status'],
                )
                if not mid:
                    messagebox.showerror("Financeiro", "Falha ao registrar lançamento. Verifique o caixa.")
                    return

                # 2) Imprimir via utilitário padrão do sistema
                try:
                    ger = GerenciadorImpressao()
                except Exception:
                    ger = None
                ok_print = False
                if ger:
                    # 2.1) Carrega dados da empresa para cabeçalho
                    try:
                        from src.controllers.cadastro_controller import CadastroController
                        cad = CadastroController(db_connection=getattr(fc.financeiro_db, 'db', None))
                        empresa = cad.obter_empresa() or {}
                    except Exception:
                        empresa = {}
                    # 2.2) Paciente com nome e médico (para impressão)
                    paciente = {
                        'nome': recibo.get('paciente', '-'),
                        'medico': recibo.get('medico', '-')
                    }
                    # 2.3) Pagamentos: usar valor numérico para somar corretamente
                    pagamentos = [{
                        'forma': lancamento.get('tipo_pagamento', recibo.get('forma', '-')),
                        'valor': float(lancamento.get('valor', 0.0) or 0.0)
                    }]
                    # 2.4) Itens: somente um item com o nome do exame/consulta
                    itens = [{'descricao': recibo.get('tipo','-')}]

                    # Diálogo simples para escolher uma das 5 impressoras (pontos de impressão)
                    escolhido = None
                    try:
                        import tkinter as tk
                        from tkinter import ttk
                        sel = tk.Toplevel(win)
                        sel.title("Selecionar Impressora")
                        sel.transient(win)
                        sel.grab_set()
                        sel.configure(bg=bg_base)
                        # Cabeçalho
                        tk.Label(sel, text="Escolha o ponto de impressão:", bg=bg_base, font=('Arial', 12, 'bold')).pack(padx=16, pady=(40, 12))
                        var = tk.StringVar(value="impressora 1")
                        # Lista de opções (até 5 pontos)
                        pontos = [f"impressora {i}" for i in range(1, 6)]
                        for chave in pontos:
                            nome = ger.impressoras.get(chave) or "(não configurada)"
                            tk.Radiobutton(
                                sel,
                                text=f"{chave}: {nome}",
                                value=chave,
                                variable=var,
                                bg=bg_base,
                                activebackground=bg_base,
                                selectcolor='white',
                                anchor='w',
                                padx=16
                            ).pack(fill='x', padx=16, pady=4)
                        # Botões
                        btns = tk.Frame(sel, bg=bg_base)
                        btns.pack(fill='x', padx=16, pady=(16, 40))
                        def _ok():
                            nonlocal escolhido
                            escolhido = var.get()
                            sel.destroy()
                        def _cancel():
                            nonlocal escolhido
                            escolhido = None
                            sel.destroy()
                        tk.Button(
                            btns,
                            text="Confirmar",
                            command=_ok,
                            bg='#4a6fa5', fg='white',
                            activebackground='#3f5e8a', activeforeground='white',
                            font=('Arial', 10, 'bold'),
                            bd=0, padx=20, pady=8, cursor='hand2', width=14
                        ).pack(side='right', padx=8)
                        tk.Button(
                            btns,
                            text="Cancelar",
                            command=_cancel,
                            font=('Arial', 10),
                            padx=16, pady=8, cursor='hand2', width=12
                        ).pack(side='right')
                        # Aumenta a altura em +80px e centraliza sem alterar a largura calculada
                        try:
                            sel.update_idletasks()
                            w = sel.winfo_reqwidth()
                            h = sel.winfo_reqheight() + 80
                            sw = sel.winfo_screenwidth()
                            sh = sel.winfo_screenheight()
                            x = int((sw - w) / 2)
                            y = int((sh - h) / 2)
                            sel.geometry(f"{w}x{h}+{x}+{y}")
                        except Exception:
                            pass
                        sel.wait_window()
                        # Resolve nome real da impressora a partir da chave
                        if escolhido:
                            escolhido = ger.impressoras.get(escolhido) or None
                    except Exception:
                        escolhido = None
                    try:
                        ok_print = ger.imprimir_comprovante_pagamento(empresa, paciente, pagamentos, itens, impressora=escolhido)
                    except Exception as e:
                        ok_print = False
                if not ok_print:
                    messagebox.showwarning("Imprimir", "Lançado com sucesso, mas falhou a impressão. Verifique as configurações de impressora em Configurações > Impressoras.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Imprimir", f"Falha ao finalizar/imprimir: {e}")

        estilo_btn = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 22,
        }
        btn_print = tk.Button(btns, text="Finalizar e Imprimir...", command=finalizar_e_imprimir, **estilo_btn)
        btn_print.pack(side='right', padx=5)

        def finalizar_sem_imprimir():
            try:
                mid = fc.registrar_movimento(
                    tipo=lancamento['tipo'],
                    tipo_pagamento=lancamento['tipo_pagamento'],
                    valor=lancamento['valor'],
                    descricao=lancamento['descricao'],
                    usuario_id=lancamento['usuario_id'],
                    paciente_id=lancamento['paciente_id'],
                    consulta_id=lancamento['consulta_id'],
                    medico_id=lancamento['medico_id'],
                    status=lancamento['status'],
                )
                if mid:
                    messagebox.showinfo("Financeiro", "Lançamento registrado com sucesso.")
                    win.destroy()
                else:
                    messagebox.showerror("Financeiro", "Falha ao registrar lançamento. Verifique o caixa.")
            except Exception as e:
                messagebox.showerror("Financeiro", f"Falha ao finalizar: {e}")

        btn_finalizar = tk.Button(btns, text="Finalizar sem Imprimir", command=finalizar_sem_imprimir, **estilo_btn)
        btn_finalizar.pack(side='right', padx=5)

        btn_close = tk.Button(btns, text="Fechar", command=win.destroy, **estilo_btn)
        btn_close.pack(side='left', padx=5)

    def _build_receipt_html(self, recibo: dict, auto_print: bool = False) -> str:
        """Gera HTML formatado para A4 do comprovante. Se auto_print=True, dispara window.print() ao abrir."""
        css = """
        <style>
        @page { size: A4; margin: 20mm; }
        body { font-family: Arial, sans-serif; color: #111; text-align: center; }
        .header { text-align: center; margin-bottom: 16px; }
        .title { font-size: 22px; font-weight: bold; }
        .meta { font-size: 12px; color: #444; }
        .section { border-top: 1px solid #ddd; padding-top: 12px; margin-top: 12px; }
        .row { margin: 6px 0; }
        .label { color: #666; margin-right: 6px; }
        .value { font-weight: bold; }
        .valor { font-size: 18px; }
        .footer { margin-top: 24px; font-size: 12px; color: #555; text-align: center; }
        </style>
        """
        script = "<script>window.onload = function(){ %s };</script>" % ("window.print();" if auto_print else "")
        h = recibo
        html = f"""
        <html><head><meta charset='utf-8'>{css}{script}</head><body>
        <div class='header'>
          <div class='title'>Clínica - Comprovante de Pagamento</div>
          <div class='meta'>Emitido em {h.get('data_hora','-')}</div>
        </div>
        <div class='section'>
          {f"<div class='row'><span class='label'>Hora da Consulta</span> <span class='value'>{h.get('hora_consulta','-')}</span></div>" if h.get('hora_consulta') else ''}
          {f"<div class='row'><span class='label'>Paciente</span> <span class='value'>{h.get('paciente','-')}</span></div>" if h.get('paciente') else ''}
          {f"<div class='row'><span class='label'>Médico</span> <span class='value'>{h.get('medico','-')}</span></div>" if h.get('medico') else ''}
          {f"<div class='row'><span class='value'>{h.get('tipo','-')}</span></div>" if h.get('tipo') else ''}
        </div>
        <div class='section'>
          <div class='row'><div class='label'>Forma</div><div class='value'>{h.get('forma','-').upper()}</div></div>
          <div class='row'><div class='label'>Status</div><div class='value'>{h.get('status','-').upper()}</div></div>
          <div class='row valor'><div class='label'>Valor</div><div class='value'>{h.get('valor','-')}</div></div>
          <div class='row'><div class='label'>Descrição</div><div class='value'>{h.get('descricao','-')}</div></div>
        </div>
        <div class='footer'></div>
        </body></html>
        """
        return html

    # Removidos utilitários específicos do Windows em favor de src.utils.impressao.GerenciadorImpressao

    def _on_lancar_despesa(self):
        """Lança uma despesa (saída) simples: valor, forma e descrição. Status sempre 'pago'."""
        try:
            fc = self._get_financeiro_controller()
            if not fc.get_sessao_aberta():
                messagebox.showwarning("Lançar Despesa", "Abra o caixa antes de lançar uma despesa.")
                return

            dlg = tk.Toplevel(self.parent)
            dlg.title("Lançar Despesa")
            bg_base = self.parent.cget("bg")
            dlg.configure(bg=bg_base)
            dlg.transient(self.parent)
            dlg.grab_set()
            self._center_window(dlg, 560, 360)

            title = tk.Label(dlg, text="Lançamento de Despesa", font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"]) 
            title.pack(padx=20, pady=(20, 10), anchor='w')

            form = tk.Frame(dlg, bg=bg_base)
            form.pack(fill='both', expand=True, padx=20)

            # 1) Forma de pagamento
            tk.Label(form, text="Forma:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=0, column=0, sticky='w', pady=4)
            forma_var = tk.StringVar(value="dinheiro")
            forma_cb = ttk.Combobox(form, textvariable=forma_var, values=[
                "dinheiro", "pix", "cartao_credito", "cartao_debito", "outro"
            ], state="readonly")
            forma_cb.grid(row=0, column=1, sticky='ew', padx=8, pady=4)

            # 2) Valor
            tk.Label(form, text="Valor (R$):", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=1, column=0, sticky='w', pady=4)
            valor_var = tk.StringVar(value="")
            valor_ent = tk.Entry(form, textvariable=valor_var, font=("Arial", 12))
            valor_ent.grid(row=1, column=1, sticky='ew', padx=8, pady=4)

            # 3) Descrição
            tk.Label(form, text="Descrição:", bg=bg_base, fg=CORES["texto"], font=FONTES["normal"]).grid(row=2, column=0, sticky='nw', pady=4)
            desc_txt = tk.Text(form, height=5, wrap='word')
            desc_txt.grid(row=2, column=1, sticky='nsew', padx=8, pady=4)

            # Grid config
            form.columnconfigure(1, weight=1)
            form.rowconfigure(2, weight=1)
            valor_ent.focus_set()

            # Botões
            btns = tk.Frame(dlg, bg=bg_base)
            btns.pack(fill='x', padx=20, pady=(10, 20))

            def on_confirm():
                try:
                    forma = forma_var.get().strip().lower()
                    if forma not in {"dinheiro", "pix", "cartao_credito", "cartao_debito", "outro"}:
                        messagebox.showwarning("Forma inválida", "Escolha uma forma válida.")
                        return
                    valor = self._parse_currency_br(valor_var.get())
                    if valor is None or valor <= 0:
                        messagebox.showwarning("Valor inválido", "Informe um valor maior que zero.")
                        return
                    descricao = (desc_txt.get("1.0", "end").strip())

                    # tipo='pagamento' no controller => persiste como 'saida' na tabela financeiro
                    mov_id = fc.registrar_movimento(
                        tipo='pagamento',
                        tipo_pagamento=forma,
                        valor=float(valor),
                        descricao=descricao,
                        usuario_id=getattr(self.controller, 'usuario_id', None),
                        status='pago',
                    )
                    if mov_id:
                        messagebox.showinfo("Despesa", "Despesa registrada com sucesso.")
                        dlg.destroy()
                    else:
                        messagebox.showerror("Despesa", "Falha ao registrar a despesa. Verifique o caixa.")
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao registrar despesa: {e}")

            def on_cancel():
                dlg.destroy()

            btn_ok = tk.Button(btns, text="Confirmar", command=on_confirm, width=14)
            aplicar_estilo(btn_ok, 'sucesso')
            btn_ok.pack(side='right', padx=5)

            btn_cancel = tk.Button(btns, text="Cancelar", command=on_cancel, width=14)
            aplicar_estilo(btn_cancel, 'perigo')
            btn_cancel.pack(side='right', padx=5)

            dlg.bind('<Return>', lambda e: on_confirm())
            dlg.bind('<Escape>', lambda e: on_cancel())
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir diálogo de despesa: {e}")

    def _carregar_movimentos(self):
        fc = self._get_financeiro_controller()
        movimentos = fc.listar_movimentos() or []
        # limpa
        # (tela simplificada: sem tabela de movimentos)
        # Mantido método para compatibilidade, caso seja utilizado em outro local.
        # adiciona
        pass

    def _atualizar_resumo(self):
        fc = self._get_financeiro_controller()
        resumo = fc.resumo_sessao()
        if not resumo:
            # (tela simplificada: sem resumo visível)
            return
        # Mantido método para possível uso futuro.
        return

    def _on_fechar_caixa(self):
        # Janela de confirmação estilizada
        bg_base = self.parent.cget("bg")
        confirm = tk.Toplevel(self.parent)
        confirm.title("Fechar Caixa")
        confirm.configure(bg=bg_base)
        confirm.transient(self.parent)
        confirm.grab_set()
        self._center_window(confirm, 520, 260)

        # Título padrão (Arial 12 negrito) e texto (Arial 10)
        tk.Label(confirm, text="Fechar Caixa", font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"]).pack(padx=24, pady=(20, 6), anchor='w')
        tk.Label(
            confirm,
            text="Deseja fechar o caixa e gerar o relatório desta sessão?",
            font=("Arial", 10), bg=bg_base, fg=CORES["texto"],
            wraplength=460, justify='left'
        ).pack(padx=24, pady=(0, 12), anchor='w')

        btns_c = tk.Frame(confirm, bg=bg_base)
        btns_c.pack(fill='x', padx=24, pady=(8, 20))

        def do_close():
            # Primeiro passo do fechamento cego: abrir diálogo para o usuário lançar conferência
            confirm.destroy()
            self._show_conferencia_dialog()

        def cancel_c():
            confirm.destroy()

        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 15,
        }
        btn_yes = tk.Button(btns_c, text="Fechar", command=do_close, **btn_style)
        btn_yes.pack(side='right', padx=5)

        btn_no = tk.Button(btns_c, text="Cancelar", command=cancel_c, **btn_style)
        btn_no.pack(side='right', padx=5)

        confirm.bind('<Return>', lambda e: do_close())
        confirm.bind('<Escape>', lambda e: cancel_c())

    def _show_relatorio_dialog(self, resumo: dict, comparativo: dict | None = None):
        # Relatório de fechamento alinhado e padronizado
        bg_base = self.parent.cget("bg")
        dlg = tk.Toplevel(self.parent)
        dlg.title("Relatório de Fechamento do Caixa")
        dlg.configure(bg=bg_base)
        dlg.transient(self.parent)
        dlg.grab_set()
        self._center_window(dlg, 720, 540)

        title = tk.Label(dlg, text="Relatório de Caixa", font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"]) 
        title.pack(padx=24, pady=(24, 8), anchor='w')

        # Fonte monoespaçada para alinhar colunas como no exemplo
        content_font = ("Courier New", 10)
        container = tk.Frame(dlg, bg=bg_base)
        container.pack(fill='both', expand=True, padx=24, pady=(0, 12))

        formas_ordem = ["dinheiro", "cartao_credito", "cartao_debito", "pix", "outro"]
        label_map = {
            'dinheiro': 'Dinheiro',
            'cartao_credito': 'Cartão Crédito',
            'cartao_debito': 'Cartão Débito',
            'pix': 'PIX',
            'outro': 'Outro'
        }
        entradas = resumo.get('entradas_por_forma') or {}
        saidas = resumo.get('saidas_por_forma') or {}

        # Helpers para alinhar rótulos exatamente como o exemplo
        def fmt_total(label: str, valor: float) -> str:
            # Mantém os dois espaços antes de R$
            return f"{label:<17}  R$ {valor:.2f}"

        def fmt_item(label: str, valor: float) -> str:
            return f"  - {label:<11} R$ {valor:.2f}"

        linhas = [
            fmt_total("Fundo inicial:", float(resumo.get('valor_inicial', 0.0))),
            fmt_total("Total Entradas:", float(resumo.get('total_entradas', 0.0))),
            fmt_total("Total Saídas:", float(resumo.get('total_saidas', 0.0))),
            fmt_total("Saldo Final:", float(resumo.get('saldo_final', 0.0))),
            "",
            "Entradas por forma:",
        ]
        for f in formas_ordem:
            total = float(entradas.get(f, 0.0))
            linhas.append(fmt_item(label_map.get(f, f) + ":", total))

        linhas.append("\nSaídas por forma:")
        for f in formas_ordem:
            total = float(saidas.get(f, 0.0))
            linhas.append(fmt_item(label_map.get(f, f) + ":", total))

        # Se houver comparativo (fechamento cego), exibir contados e diferenças
        if comparativo:
            cont_e = (comparativo.get('contados') or {}).get('entradas', {})
            cont_s = (comparativo.get('contados') or {}).get('saidas', {})
            difs_e = (comparativo.get('diferencas') or {}).get('entradas', {})
            difs_s = (comparativo.get('diferencas') or {}).get('saidas', {})
            tot_cont_e = float((comparativo.get('contados') or {}).get('total_entradas', 0.0))
            tot_cont_s = float((comparativo.get('contados') or {}).get('total_saidas', 0.0))
            tot_dif_e = float((comparativo.get('diferencas') or {}).get('total_entradas', 0.0))
            tot_dif_s = float((comparativo.get('diferencas') or {}).get('total_saidas', 0.0))

            linhas += [
                "",
                "Totais contados pelo usuário:",
                fmt_total("Entradas (cont.):", tot_cont_e),
                fmt_total("Saídas (cont.):", tot_cont_s),
                "",
                "Diferenças totais (cont - sist):",
                fmt_total("Entradas dif.:", tot_dif_e),
                fmt_total("Saídas dif.:", tot_dif_s),
                "",
                "Entradas (contado pelo usuário):",
            ]
            for f in formas_ordem:
                linhas.append(fmt_item(label_map.get(f, f) + ":", float(cont_e.get(f, 0.0) or 0.0)))
            linhas.append("\nDiferenças por forma (Entradas):")
            for f in formas_ordem:
                linhas.append(fmt_item(label_map.get(f, f) + ":", float(difs_e.get(f, 0.0) or 0.0)))
            linhas.append("\nSaídas (contado pelo usuário):")
            for f in formas_ordem:
                linhas.append(fmt_item(label_map.get(f, f) + ":", float(cont_s.get(f, 0.0) or 0.0)))
            linhas.append("\nDiferenças por forma (Saídas):")
            for f in formas_ordem:
                linhas.append(fmt_item(label_map.get(f, f) + ":", float(difs_s.get(f, 0.0) or 0.0)))

        txt = tk.Text(container, height=18, wrap='word', bg=bg_base, fg=CORES['texto'], relief='flat')
        txt.pack(fill='both', expand=True)
        txt.tag_configure('content', font=content_font)
        txt.insert('end', "\n".join(linhas), 'content')
        txt.config(state='disabled')

        btns = tk.Frame(dlg, bg=bg_base)
        btns.pack(fill='x', padx=24, pady=(4, 20))

        def close_dlg():
            dlg.destroy()

        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 15,
        }
        btn_close = tk.Button(btns, text="Fechar", command=close_dlg, **btn_style)
        btn_close.pack(side='right', padx=5)

    def _show_comparativo_dialog(self, resumo: dict, comparativo: dict):
        """Exibe comparação lado a lado: Usuário (contado) x Sistema, com campos somente leitura de fundo branco."""
        bg_base = self.parent.cget("bg")
        dlg = tk.Toplevel(self.parent)
        dlg.title("Comparação de Fechamento: Usuário x Sistema")
        dlg.configure(bg=bg_base)
        dlg.transient(self.parent)
        dlg.grab_set()
        self._center_window(dlg, 820, 740)

        title = tk.Label(dlg, text="Comparação de Fechamento", font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"])
        title.pack(padx=24, pady=(20, 8), anchor='w')

        container = tk.Frame(dlg, bg=bg_base)
        container.pack(fill='both', expand=True, padx=24, pady=(0, 10))

        left = tk.Frame(container, bg=bg_base)
        right = tk.Frame(container, bg=bg_base)
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))
        right.pack(side='left', fill='both', expand=True, padx=(10, 0))

        section_font = ("Arial", 10, 'bold')
        label_font = ("Arial", 10)

        def fmt(v: float) -> str:
            try:
                return (f"{float(v):,.2f}").replace(',', 'X').replace('.', ',').replace('X', '.')
            except Exception:
                return "0,00"

        # Dados
        formas_ordem = ["dinheiro", "cartao_credito", "cartao_debito", "pix", "outro"]
        label_map = {
            'dinheiro': 'Dinheiro',
            'cartao_credito': 'Cartão Crédito',
            'cartao_debito': 'Cartão Débito',
            'pix': 'PIX',
            'outro': 'Outro'
        }

        cont = comparativo.get('contados') or {}
        cont_e = cont.get('entradas', {})
        cont_s = cont.get('saidas', {})

        sis_e = (resumo.get('entradas_por_forma') or {})
        sis_s = (resumo.get('saidas_por_forma') or {})

        # Cabeçalhos
        tk.Label(left, text="Usuário (contado)", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))
        tk.Label(right, text="Sistema", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 6))

        # Entradas
        tk.Label(left, text="Entradas", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=1, column=0, columnspan=2, sticky='w', pady=(6, 4))
        tk.Label(right, text="Entradas", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=1, column=0, columnspan=2, sticky='w', pady=(6, 4))

        r = 2
        for f in formas_ordem:
            tk.Label(left, text=label_map.get(f, f)+":", font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=r, column=0, sticky='w', pady=2)
            e1 = tk.Entry(left, font=("Arial", 10), state='readonly', readonlybackground='white')
            e1.grid(row=r, column=1, sticky='ew', pady=2)
            e1_var = tk.StringVar(value=fmt(cont_e.get(f, 0.0) or 0.0))
            e1.config(textvariable=e1_var)
            left.grid_columnconfigure(1, weight=1)

            tk.Label(right, text=label_map.get(f, f)+":", font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=r, column=0, sticky='w', pady=2)
            e2 = tk.Entry(right, font=("Arial", 10), state='readonly', readonlybackground='white')
            e2.grid(row=r, column=1, sticky='ew', pady=2)
            e2_var = tk.StringVar(value=fmt(sis_e.get(f, 0.0) or 0.0))
            e2.config(textvariable=e2_var)
            right.grid_columnconfigure(1, weight=1)
            r += 1

        # Saídas título
        tk.Label(left, text="", bg=bg_base).grid(row=r, column=0, pady=(6,0))
        tk.Label(left, text="Saídas", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=r+1, column=0, columnspan=2, sticky='w', pady=(6, 4))
        tk.Label(right, text="", bg=bg_base).grid(row=r, column=0, pady=(6,0))
        tk.Label(right, text="Saídas", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=r+1, column=0, columnspan=2, sticky='w', pady=(6, 4))
        r += 2

        for f in formas_ordem:
            tk.Label(left, text=label_map.get(f, f)+":", font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=r, column=0, sticky='w', pady=2)
            e1 = tk.Entry(left, font=("Arial", 10), state='readonly', readonlybackground='white')
            e1.grid(row=r, column=1, sticky='ew', pady=2)
            e1_var = tk.StringVar(value=fmt(cont_s.get(f, 0.0) or 0.0))
            e1.config(textvariable=e1_var)

            tk.Label(right, text=label_map.get(f, f)+":", font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=r, column=0, sticky='w', pady=2)
            e2 = tk.Entry(right, font=("Arial", 10), state='readonly', readonlybackground='white')
            e2.grid(row=r, column=1, sticky='ew', pady=2)
            e2_var = tk.StringVar(value=fmt(sis_s.get(f, 0.0) or 0.0))
            e2.config(textvariable=e2_var)
            r += 1

        # Totais
        tot_cont_e = float(cont.get('total_entradas', 0.0) or 0.0)
        tot_cont_s = float(cont.get('total_saidas', 0.0) or 0.0)
        tot_sis_e = float(resumo.get('total_entradas', 0.0) or 0.0)
        tot_sis_s = float(resumo.get('total_saidas', 0.0) or 0.0)

        tk.Label(left, text="", bg=bg_base).grid(row=r, column=0, pady=(6,0))
        tk.Label(left, text="Totais (Usuário)", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=r+1, column=0, columnspan=2, sticky='w', pady=(6, 4))
        tk.Label(right, text="", bg=bg_base).grid(row=r, column=0, pady=(6,0))
        tk.Label(right, text="Totais (Sistema)", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=r+1, column=0, columnspan=2, sticky='w', pady=(6, 4))
        r += 2

        for lbl, v1, v2 in (
            ("Entradas:", tot_cont_e, tot_sis_e),
            ("Saídas:", tot_cont_s, tot_sis_s),
        ):
            tk.Label(left, text=lbl, font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=r, column=0, sticky='w', pady=2)
            e1 = tk.Entry(left, font=("Arial", 10), state='readonly', readonlybackground='white')
            e1.grid(row=r, column=1, sticky='ew', pady=2)
            e1.config(textvariable=tk.StringVar(value=fmt(v1)))

            tk.Label(right, text=lbl, font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=r, column=0, sticky='w', pady=2)
            e2 = tk.Entry(right, font=("Arial", 10), state='readonly', readonlybackground='white')
            e2.grid(row=r, column=1, sticky='ew', pady=2)
            e2.config(textvariable=tk.StringVar(value=fmt(v2)))
            r += 1

        # Observação
        obs_frame = tk.Frame(dlg, bg=bg_base)
        obs_frame.pack(fill='x', padx=24, pady=(8, 4))
        tk.Label(obs_frame, text="Observação (justificativa do operador):", font=("Arial", 10, 'bold'), bg=bg_base, fg=CORES["texto"]).pack(anchor='w')
        obs_txt = tk.Text(obs_frame, height=4, bg='white', fg=CORES['texto'], font=("Arial", 10))
        obs_txt.pack(fill='x', pady=(4, 0))

        # Botões
        btns = tk.Frame(dlg, bg=bg_base)
        btns.pack(fill='x', padx=24, pady=(8, 16))

        def close_dlg():
            dlg.destroy()

        def salvar_obs():
            try:
                fc = self._get_financeiro_controller()
                ok = fc.salvar_observacao_fechamento(obs_txt.get('1.0', 'end').strip())
                if ok:
                    messagebox.showinfo("Observação", "Observação salva com sucesso.")
                else:
                    messagebox.showwarning("Observação", "Não foi possível salvar a observação neste momento.")
            except Exception as e:
                messagebox.showerror("Observação", f"Falha ao salvar observação: {e}")

        # Ordem de empacotamento para que o Salvar fique mais à direita
        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 15,
        }
        btn_close = tk.Button(btns, text="Fechar", command=close_dlg, **btn_style)
        btn_close.pack(side='right', padx=5)

        btn_save = tk.Button(btns, text="Salvar Observação", command=salvar_obs, **btn_style)
        btn_save.pack(side='right', padx=5)

    def _show_conferencia_dialog(self):
        """Diálogo para o usuário informar os valores contados de entradas e saídas por forma."""
        bg_base = self.parent.cget("bg")
        dlg = tk.Toplevel(self.parent)
        dlg.title("Conferência de Fechamento")
        dlg.configure(bg=bg_base)
        dlg.transient(self.parent)
        dlg.grab_set()
        self._center_window(dlg, 620, 420)

        tk.Label(dlg, text="Conferência de Fechamento (valores contados)", font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES["texto"]).pack(padx=24, pady=(20, 8), anchor='w')

        body = tk.Frame(dlg, bg=bg_base)
        body.pack(fill='both', expand=True, padx=24, pady=(0, 10))

        section_font = ("Arial", 10, 'bold')
        label_font = ("Arial", 10)

        entradas_vars = {}
        saidas_vars = {}
        formas = [
            ("dinheiro", "Dinheiro"),
            ("cartao_credito", "Cartão Crédito"),
            ("cartao_debito", "Cartão Débito"),
            ("pix", "PIX"),
            ("outro", "Outro"),
        ]

        # Grid: Entradas à esquerda, Saídas à direita
        left = tk.Frame(body, bg=bg_base)
        right = tk.Frame(body, bg=bg_base)
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))
        right.pack(side='left', fill='both', expand=True, padx=(10, 0))

        tk.Label(left, text="Entradas (contado)", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0,6))
        tk.Label(right, text="Saídas (contado)", font=section_font, bg=bg_base, fg=CORES["texto"]).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0,6))

        for i,(key, rotulo) in enumerate(formas, start=1):
            tk.Label(left, text=rotulo+":", font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=i, column=0, sticky='w', pady=2)
            var_e = tk.StringVar(value="")
            entradas_vars[key] = var_e
            e = tk.Entry(left, textvariable=var_e, font=("Arial",10))
            e.grid(row=i, column=1, sticky='ew', pady=2)
            left.grid_columnconfigure(1, weight=1)

            tk.Label(right, text=rotulo+":", font=label_font, bg=bg_base, fg=CORES["texto"]).grid(row=i, column=0, sticky='w', pady=2)
            var_s = tk.StringVar(value="")
            saidas_vars[key] = var_s
            s = tk.Entry(right, textvariable=var_s, font=("Arial",10))
            s.grid(row=i, column=1, sticky='ew', pady=2)
            right.grid_columnconfigure(1, weight=1)

        # Botões
        btns = tk.Frame(dlg, bg=bg_base)
        btns.pack(fill='x', padx=24, pady=(8, 16))

        def parse_val(txt: str) -> float:
            if not txt:
                return 0.0
            t = txt.strip().replace("R$"," ").replace(".", "").replace(",", ".")
            try:
                return float(t)
            except Exception:
                return 0.0

        def on_confirm():
            # Monta dicionário contados
            contados = {
                'entradas': {k: parse_val(v.get()) for k,v in entradas_vars.items()},
                'saidas': {k: parse_val(v.get()) for k,v in saidas_vars.items()},
            }
            try:
                fc = self._get_financeiro_controller()
                resultado = fc.conferir_fechamento(contados)
                if not resultado:
                    messagebox.showerror("Conferência", "Não há sessão aberta para conferir.")
                    return
                # Após registrar a conferência, fecha o caixa e exibe relatório
                resumo = fc.fechar_caixa(
                    usuario_id=getattr(self.controller, 'usuario_id', None),
                    usuario_nome=getattr(self.controller, 'usuario_nome', None)
                )
                if not resumo:
                    messagebox.showerror("Fechar Caixa", "Não há sessão aberta para fechar.")
                    return
                dlg.destroy()
                # Mostra primeiro o comparativo lado a lado conforme solicitado
                self._show_comparativo_dialog(resumo, resultado)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha na conferência/fechamento: {e}")
            finally:
                self._refresh_caixa_state()

        def on_cancel():
            dlg.destroy()

        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 15,
        }
        btn_ok = tk.Button(btns, text="Confirmar e Fechar", command=on_confirm, **btn_style)
        btn_ok.pack(side='right', padx=5)
        btn_cancel = tk.Button(btns, text="Cancelar", command=on_cancel, **btn_style)
        btn_cancel.pack(side='right', padx=5)
