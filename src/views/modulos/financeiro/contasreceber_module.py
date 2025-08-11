import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.config.estilos import CORES, FONTES
from src.db.financeiro_db import FinanceiroDB

class ContasReceberModule:
    """
    Tela de Contas a Receber com o MESMO layout/estilo do Contas a Pagar, adaptada para recebimentos.
    - Cadastro de contas a receber, com opção de repetir por 12 meses
    - Receber pagamento (entrada no caixa) e cancelar recebimento (estorno)
    - Filtros por mês/status
    """
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        bg_base = CORES.get("fundo", "#f0f2f5")

        self.frame = tk.Frame(parent, bg=bg_base)

        # Título
        tk.Label(
            self.frame,
            text="Contas a Receber",
            font=FONTES.get("subtitulo", ("Arial", 16, "bold")),
            bg="#f0f2f5",
            fg=CORES.get("texto", "#000")
        ).pack(pady=(10, 5), anchor='w')

        # Corpo
        body = tk.Frame(self.frame, bg=bg_base)
        body.pack(fill='both', expand=True)

        # Coluna esquerda (ações)
        left_col = tk.Frame(body, bg=bg_base, width=230)
        left_col.pack(side='left', anchor='n', padx=10, pady=5, fill='y')
        left_col.pack_propagate(False)

        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 18,
        }

        tk.Button(left_col, text="Nova Conta", command=self._nova_conta, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Editar", command=self._editar, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Receber", command=self._receber_selecionada, **btn_style).pack(fill='x', pady=4)
        btn_excluir_style = dict(btn_style)
        btn_excluir_style['bg'] = CORES.get('alerta', '#f44336')
        tk.Button(left_col, text="Excluir", command=self._excluir, **btn_excluir_style).pack(fill='x', pady=4)

        # Área direita (filtros + lista)
        right = tk.Frame(body, bg=bg_base)
        right.pack(side='left', fill='both', expand=True, padx=(10, 10), pady=(5, 10))

        filtros = tk.Frame(right, bg=bg_base)
        filtros.pack(fill='x')

        tk.Label(filtros, text="Mês:", font=('Arial', 10), bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0, 5))
        self.cmb_mes = ttk.Combobox(filtros, values=[
            'Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'], width=18)
        self.cmb_mes.pack(side='left', padx=(0, 15))

        tk.Label(filtros, text="Status:", font=('Arial', 10), bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0, 5))
        self.cmb_status = ttk.Combobox(filtros, values=['Todos','Aberto','Recebido','Atrasado'], width=12)
        # Padrão: mostrar somente contas em aberto (oculta recebidos da lista por padrão)
        try:
            self.cmb_status.set('Aberto')
        except Exception:
            try:
                self.cmb_status.current(1)
            except Exception:
                self.cmb_status.current(0)
        self.cmb_status.pack(side='left')

        btn_style_filtro = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#4a6fa5',
            'fg': 'white',
            'bd': 0,
            'padx': 20,
            'pady': 6,
            'relief': 'flat',
            'cursor': 'hand2',
            'width': 12,
        }
        tk.Button(filtros, text='Filtrar', command=self._aplicar_filtro, **btn_style_filtro).pack(side='left', padx=(10, 0))

        # Lista (Treeview)
        style = ttk.Style()
        try:
            style.configure("CR.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("CR.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass

        cols = (
            'descricao','categoria','dia_venc','valor_prev','valor_atual','status','vencimento','dias_atraso'
        )
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=16, style='CR.Treeview')
        self.tree.pack(fill='both', expand=True, pady=(10, 0))

        headers = {
            'descricao': 'Descrição',
            'categoria': 'Categoria',
            'dia_venc': 'Dia Venc.',
            'valor_prev': 'Valor Previsto',
            'valor_atual': 'Valor Atual',
            'status': 'Status',
            'vencimento': 'Vencimento',
            'dias_atraso': 'Dias Atraso',
        }
        widths = {
            'descricao': 220,
            'categoria': 120,
            'dia_venc': 80,
            'valor_prev': 120,
            'valor_atual': 120,
            'status': 100,
            'vencimento': 120,
            'dias_atraso': 100,
        }
        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c], anchor='w')

        # Menu de contexto: somente Cancelar Recebimento
        self._ctx_menu = tk.Menu(self.tree, tearoff=0)
        self._ctx_menu.add_command(label="Cancelar Recebimento", command=self._cancelar_recebimento)

        def _on_right_click(event):
            try:
                iid = self.tree.identify_row(event.y)
                if iid:
                    self.tree.selection_set(iid)
                    self._ctx_menu.tk_popup(event.x_root, event.y_root)
            finally:
                try:
                    self._ctx_menu.grab_release()
                except Exception:
                    pass

        # Aplica o filtro inicial (Aberto) para ocultar recebidos na lista do caixa
        try:
            self._aplicar_filtro()
        except Exception:
            pass
        self.tree.bind('<Button-3>', _on_right_click)

        # Carregar dados
        self._carregar_dados_db()

    # ---------- Dados ----------
    def _carregar_dados_db(self, status_filtro: str | None = None, mes_filtro: int | None = None, atrasados: bool = False):
        for i in self.tree.get_children():
            self.tree.delete(i)
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return
        db = FinanceiroDB(db_conn)
        linhas = db.listar_contas_receber(status_filtro) or []
        hoje = datetime.now().date()
        for row in linhas:
            if mes_filtro:
                venc = row.get('vencimento')
                try:
                    if venc:
                        vmonth = venc.month if hasattr(venc, 'month') else int(str(venc)[5:7])
                        if vmonth != mes_filtro:
                            continue
                    else:
                        if int(row.get('dia_vencimento') or 0) <= 0:
                            continue
                except Exception:
                    pass
            if atrasados:
                if (row.get('status') != 'aberto'):
                    continue
                venc = row.get('vencimento')
                try:
                    if venc:
                        vdate = venc if hasattr(venc, 'toordinal') else datetime.strptime(str(venc), '%Y-%m-%d').date()
                        if vdate >= hoje:
                            continue
                    else:
                        continue
                except Exception:
                    continue
            valores = (
                row.get('descricao') or '',
                row.get('categoria') or '',
                int(row.get('dia_vencimento') or 0),
                (f"{float(row.get('valor_previsto') or 0):.2f}" if row.get('valor_previsto') is not None else '-'),
                (f"{float(row.get('valor_atual') or 0):.2f}" if row.get('valor_atual') is not None else '-'),
                ('Recebido' if (row.get('status') == 'recebido') else 'Aberto'),
                (row.get('vencimento').strftime('%d/%m/%Y') if row.get('vencimento') else '-'),
                self._calc_dias_atraso(row.get('vencimento')),
            )
            iid = str(row.get('id')) if row.get('id') is not None else ''
            self.tree.insert('', 'end', iid=iid, values=valores)

    def _calc_dias_atraso(self, vencimento):
        try:
            if not vencimento:
                return 0
            vdate = vencimento if hasattr(vencimento, 'toordinal') else datetime.strptime(str(vencimento), '%Y-%m-%d').date()
            delta = (datetime.now().date() - vdate).days
            return delta if delta > 0 else 0
        except Exception:
            return 0

    # ---------- Ações ----------
    def _nova_conta(self):
        try:
            self._abrir_dialog_nova_conta()
        except Exception as e:
            messagebox.showerror("Contas a Receber", f"Falha ao abrir cadastro: {e}")

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Receber", "Selecione um registro para editar.")
            return
        item_id = sel[0]
        if not item_id:
            return
        try:
            self._abrir_dialog_editar_receber(int(item_id))
        except Exception as e:
            messagebox.showerror("Contas a Receber", f"Falha ao abrir edição: {e}")

    def _abrir_dialog_editar_receber(self, conta_id: int):
        vals = self.tree.item(str(conta_id), 'values') if self.tree.exists(str(conta_id)) else None
        desc_atual = vals[0] if vals else ''
        cat_atual = vals[1] if vals else ''
        dia_venc_atual = int(vals[2]) if vals and str(vals[2]).isdigit() else 1
        valor_prev_atual = vals[3] if vals else '-'
        venc_atual_str = vals[6] if vals else '-'

        win = tk.Toplevel(self.frame)
        win.title("Editar Conta a Receber")
        win.transient(self.frame.winfo_toplevel())
        win.grab_set()
        win.resizable(False, False)

        body = tk.Frame(win)
        body.pack(padx=16, pady=16, fill='both', expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)

        row = 0
        def add(label, widget):
            nonlocal row
            tk.Label(body, text=label, font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
            widget.grid(row=row, column=1, sticky='we', pady=4)
            row += 1

        self._edr_desc = tk.Entry(body, font=('Arial', 10))
        self._edr_desc.insert(0, desc_atual)
        add("Descrição:", self._edr_desc)

        self._edr_cat = tk.Entry(body, font=('Arial', 10))
        self._edr_cat.insert(0, cat_atual)
        add("Categoria:", self._edr_cat)

        self._edr_valor_prev = tk.Entry(body, font=('Arial', 10))
        if valor_prev_atual and valor_prev_atual != '-':
            self._edr_valor_prev.insert(0, str(valor_prev_atual))
        add("Valor previsto:", self._edr_valor_prev)

        self._edr_venc = tk.Entry(body, font=('Arial', 10))
        if venc_atual_str and venc_atual_str != '-':
            self._edr_venc.insert(0, venc_atual_str)
        add("Vencimento (dd/mm/aaaa):", self._edr_venc)

        self._edr_dia = tk.Entry(body, font=('Arial', 10), width=6)
        self._edr_dia.insert(0, str(dia_venc_atual or 1))
        add("Dia de vencimento:", self._edr_dia)

        btn_bar = tk.Frame(win)
        btn_bar.pack(fill='x', padx=16, pady=(0, 14))
        dialog_btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': CORES.get('primaria', '#4a6fa5'),
            'fg': CORES.get('texto_claro', '#ffffff'),
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'highlightthickness': 0,
        }
        tk.Button(btn_bar, text="Salvar", command=lambda: self._salvar_edicao_receber(win, conta_id), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))
        self._center_window(win)

    def _salvar_edicao_receber(self, win: tk.Toplevel, conta_id: int):
        desc = (self._edr_desc.get() or '').strip()
        if not desc:
            messagebox.showwarning("Editar", "Informe a descrição.")
            return
        categoria = (self._edr_cat.get() or '').strip() or None
        valor_str = (self._edr_valor_prev.get() or '').strip().replace(',', '.')
        valor_prev = None
        if valor_str != '':
            try:
                valor_prev = float(valor_str)
            except Exception:
                messagebox.showwarning("Editar", "Valor previsto inválido.")
                return
        venc_str = (self._edr_venc.get() or '').strip()
        venc_date = None
        if venc_str:
            try:
                venc_date = datetime.strptime(venc_str, '%d/%m/%Y').date()
            except Exception:
                messagebox.showwarning("Editar", "Data de vencimento inválida (use dd/mm/aaaa).")
                return
        try:
            dia_venc = int((self._edr_dia.get() or '1').strip())
            if dia_venc < 1 or dia_venc > 31:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Editar", "Dia de vencimento deve ser entre 1 e 31.")
            return

        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Editar", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)
        try:
            db.atualizar_conta_receber_dados(
                conta_id=conta_id,
                descricao=desc,
                categoria=categoria,
                dia_vencimento=dia_venc,
                valor_previsto=valor_prev,
                vencimento=venc_date,
            )
        except Exception as e:
            messagebox.showerror("Editar", f"Falha ao salvar alterações: {e}")
            return
        try:
            win.destroy()
        except Exception:
            pass
        self._aplicar_filtro()

    def _excluir(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Receber", "Selecione um registro para excluir.")
            return
        item_id = sel[0]
        if not messagebox.askyesno("Excluir", "Confirma excluir esta conta? Esta ação não pode ser desfeita."):
            return
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Contas a Receber", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)
        try:
            db.excluir_conta_receber(int(item_id))
        except Exception as e:
            messagebox.showerror("Contas a Receber", f"Falha ao excluir: {e}")
            return
        self._aplicar_filtro()

    def _receber_selecionada(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Receber", "Selecione uma conta para receber.")
            return
        item_id = sel[0]
        self._abrir_dialog_receber(int(item_id))

    def _cancelar_recebimento(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Receber", "Selecione uma conta para cancelar o recebimento.")
            return
        item_id = sel[0]
        vals = self.tree.item(item_id, 'values') if self.tree.exists(item_id) else None
        if not vals:
            return
        status_txt = (vals[5] or '').strip().lower()
        if status_txt != 'recebido':
            messagebox.showinfo("Contas a Receber", "A conta selecionada não está recebida.")
            return
        valor = 0.0
        try:
            if vals[4] and vals[4] != '-':
                valor = float(str(vals[4]).replace(',', '.'))
            elif vals[3] and vals[3] != '-':
                valor = float(str(vals[3]).replace(',', '.'))
        except Exception:
            valor = 0.0
        if not messagebox.askyesno("Cancelar Recebimento", "Confirma cancelar o recebimento desta conta? Será lançada uma saída (estorno) no caixa."):
            return
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Cancelar Recebimento", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)
        sessao = db.get_caixa_aberto()
        if not sessao:
            messagebox.showerror("Cancelar Recebimento", "Não há caixa aberto. Abra o caixa para estornar.")
            return
        sessao_id = sessao.get('id')
        desc = vals[0] if vals else f"Conta #{item_id}"
        try:
            if valor > 0:
                db.registrar_movimento_financeiro(
                    valor=valor,
                    tipo='saida',
                    descricao=f"Estorno recebimento de conta: {desc}",
                    usuario_id=getattr(self.controller, 'usuario_id', None),
                    tipo_pagamento='outro',
                    paciente_id=None,
                    consulta_id=None,
                    medico_id=None,
                    status='pago',
                    fundo_caixa=None,
                    aberto_por=None,
                    sessao_id=sessao_id,
                )
            db.atualizar_conta_receber_valor(int(item_id), None)
            db.atualizar_conta_receber_status(int(item_id), 'aberto')
        except Exception as e:
            messagebox.showerror("Cancelar Recebimento", f"Falha ao cancelar recebimento: {e}")
            return
        self._aplicar_filtro()

    # ---------- Filtros ----------
    def _aplicar_filtro(self):
        mes_val = None
        status_val = None
        atrasados = False
        try:
            meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
            mes_sel = self.cmb_mes.get() if hasattr(self, 'cmb_mes') else ''
            if mes_sel in meses:
                mes_val = meses.index(mes_sel) + 1
        except Exception:
            mes_val = None
        try:
            st = (self.cmb_status.get() or '').strip().lower()
            if st == 'aberto':
                status_val = 'aberto'
            elif st == 'recebido':
                status_val = 'recebido'
            elif st == 'atrasado':
                status_val = 'aberto'
                atrasados = True
            else:
                status_val = None
        except Exception:
            status_val = None
        self._carregar_dados_db(status_filtro=status_val, mes_filtro=mes_val, atrasados=atrasados)

    # ---------- Diálogo Nova Conta ----------
    def _abrir_dialog_nova_conta(self):
        win = tk.Toplevel(self.frame)
        win.title("Nova Conta a Receber")
        win.transient(self.frame.winfo_toplevel())
        win.grab_set()
        win.resizable(False, False)

        body = tk.Frame(win)
        body.pack(padx=16, pady=16, fill='both', expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)

        row = 0
        def add(label, widget):
            nonlocal row
            tk.Label(body, text=label, font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
            widget.grid(row=row, column=1, sticky='we', pady=4)
            row += 1

        self._nc_desc = tk.Entry(body, font=('Arial', 10))
        add("Descrição:", self._nc_desc)

        self._nc_cat = tk.Entry(body, font=('Arial', 10))
        add("Categoria:", self._nc_cat)

        self._nc_valor = tk.Entry(body, font=('Arial', 10))
        add("Valor previsto:", self._nc_valor)

        self._nc_venc = tk.Entry(body, font=('Arial', 10))
        add("Vencimento (dd/mm/aaaa):", self._nc_venc)

        # Opções
        self._nc_repetir = tk.IntVar(value=0)
        self._nc_var_valor = tk.IntVar(value=0)
        opts = tk.Frame(body)
        tk.Checkbutton(opts, text="Repetir por 12 meses", variable=self._nc_repetir, anchor='w').pack(side='left', padx=(0, 16))
        tk.Checkbutton(opts, text="Valor variável", variable=self._nc_var_valor, anchor='w').pack(side='left')
        tk.Label(body, text="Opções:", font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=(6,4))
        opts.grid(row=row, column=1, sticky='w', pady=(6,4))
        row += 1

        # Barra de botões
        btn_bar = tk.Frame(win)
        btn_bar.pack(fill='x', padx=16, pady=(0, 14))
        dialog_btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': CORES.get('primaria', '#4a6fa5'),
            'fg': CORES.get('texto_claro', '#ffffff'),
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'highlightthickness': 0,
        }
        tk.Button(btn_bar, text="Salvar", command=lambda: self._nc_salvar(win), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))
        self._center_window(win)

    def _nc_salvar(self, win):
        desc = (self._nc_desc.get() or '').strip()
        if not desc:
            messagebox.showwarning("Nova Conta", "Informe a descrição.")
            return
        categoria = (self._nc_cat.get() or '').strip() or None
        valor_str = (self._nc_valor.get() or '').replace(',', '.').strip()
        valor_prev = None if self._nc_var_valor.get() == 1 or valor_str == '' else self._safe_float(valor_str)
        if valor_prev is False:
            messagebox.showwarning("Nova Conta", "Valor previsto inválido.")
            return
        venc_str = (self._nc_venc.get() or '').strip()
        try:
            base_date = datetime.strptime(venc_str, '%d/%m/%Y').date()
        except Exception:
            messagebox.showwarning("Nova Conta", "Informe a data de vencimento válida (dd/mm/aaaa).")
            return
        repetir = (self._nc_repetir.get() == 1)
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Nova Conta", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)
        total = 12 if repetir else 1
        criados = 0
        for i in range(total):
            try:
                vdate = self._add_months(base_date, i)
                db.criar_conta_receber(
                    descricao=desc,
                    categoria=categoria,
                    dia_vencimento=int(vdate.day),
                    valor_previsto=(None if valor_prev is None else float(valor_prev)),
                    valor_atual=None,
                    vencimento=vdate,
                    status='aberto'
                )
                criados += 1
            except Exception as e:
                messagebox.showerror("Nova Conta", f"Falha ao criar lançamento: {e}")
                break
        if criados > 0:
            messagebox.showinfo("Nova Conta", f"{criados} lançamento(s) criado(s) com sucesso.")
            try:
                win.destroy()
            except Exception:
                pass
            self._aplicar_filtro()

    # ---------- Diálogo Receber ----------
    def _abrir_dialog_receber(self, conta_id: int):
        vals = self.tree.item(str(conta_id), 'values') if self.tree.exists(str(conta_id)) else None
        desc = vals[0] if vals else ''
        valor_sugerido = 0.0
        try:
            if vals and vals[4] and vals[4] != '-':
                valor_sugerido = float(str(vals[4]).replace(',', '.'))
            elif vals and vals[3] and vals[3] != '-':
                valor_sugerido = float(str(vals[3]).replace(',', '.'))
        except Exception:
            valor_sugerido = 0.0

        win = tk.Toplevel(self.frame)
        win.title("Receber Conta")
        win.transient(self.frame.winfo_toplevel())
        win.grab_set()
        win.resizable(False, False)

        body = tk.Frame(win)
        body.pack(padx=16, pady=16, fill='both', expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)

        row = 0
        def add(label, widget):
            nonlocal row
            tk.Label(body, text=label, font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
            widget.grid(row=row, column=1, sticky='we', pady=4)
            row += 1

        add("Descrição:", tk.Label(body, text=desc, font=('Arial', 10), anchor='w'))

        self._rc_valor = tk.Entry(body, font=('Arial', 10))
        self._rc_valor.insert(0, f"{valor_sugerido:.2f}")
        add("Valor a receber:", self._rc_valor)

        self._rc_forma = ttk.Combobox(body, values=['dinheiro','cartao_debito','pix'], width=18, state='readonly')
        self._rc_forma.current(0)
        add("Forma de recebimento:", self._rc_forma)

        btn_bar = tk.Frame(win)
        btn_bar.pack(fill='x', padx=16, pady=(0, 14))
        dialog_btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': CORES.get('primaria', '#4a6fa5'),
            'fg': CORES.get('texto_claro', '#ffffff'),
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'relief': 'flat',
            'cursor': 'hand2',
            'highlightthickness': 0,
        }
        tk.Button(btn_bar, text="Lançar Recebimento", command=lambda: self._confirmar_recebimento(win, conta_id), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))
        self._center_window(win)

    def _confirmar_recebimento(self, win: tk.Toplevel, conta_id: int):
        try:
            valor = float((self._rc_valor.get() or '0').replace(',', '.'))
        except Exception:
            messagebox.showwarning("Receber", "Informe um valor válido.")
            return
        forma = (self._rc_forma.get() or '').strip() or 'dinheiro'
        if valor <= 0:
            messagebox.showwarning("Receber", "Valor deve ser maior que zero.")
            return
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Receber", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)
        sessao = db.get_caixa_aberto()
        if not sessao:
            messagebox.showerror("Receber", "Não há caixa aberto. Abra o caixa para lançar entradas.")
            return
        sessao_id = sessao.get('id')
        vals = self.tree.item(str(conta_id), 'values') if self.tree.exists(str(conta_id)) else None
        desc = (vals[0] if vals else f"Conta #{conta_id}")
        try:
            db.registrar_movimento_financeiro(
                valor=valor,
                tipo='entrada',
                descricao=f"Recebimento de conta: {desc}",
                usuario_id=getattr(self.controller, 'usuario_id', None),
                tipo_pagamento=forma,
                paciente_id=None,
                consulta_id=None,
                medico_id=None,
                status='pago',
                fundo_caixa=None,
                aberto_por=None,
                sessao_id=sessao_id,
            )
            db.atualizar_conta_receber_valor(conta_id, valor)
            db.atualizar_conta_receber_status(conta_id, 'recebido')
        except Exception as e:
            messagebox.showerror("Receber", f"Falha ao lançar recebimento: {e}")
            return
        try:
            win.destroy()
        except Exception:
            pass
        self._aplicar_filtro()

    # ---------- Utils ----------
    def _safe_float(self, txt: str):
        try:
            return float(txt)
        except Exception:
            return False

    def _add_months(self, dt, months):
        year = dt.year + (dt.month - 1 + months) // 12
        month = (dt.month - 1 + months) % 12 + 1
        day = dt.day
        # Ajuste para fim do mês
        last_day = self._last_day_of_month(year, month)
        if day > last_day:
            day = last_day
        return datetime(year, month, day).date()

    def _last_day_of_month(self, year, month):
        if month == 12:
            return 31
        import calendar
        return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days

    def _center_window(self, win: tk.Toplevel):
        try:
            win.update_idletasks()
            w = win.winfo_width() or win.winfo_reqwidth()
            h = win.winfo_height() or win.winfo_reqheight()
            parent = win.master.winfo_toplevel() if win.master else win.winfo_toplevel()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            if pw <= 1 or ph <= 1:
                sw = win.winfo_screenwidth()
                sh = win.winfo_screenheight()
                x = (sw - w) // 2
                y = (sh - h) // 2
            else:
                x = px + (pw - w) // 2
                y = py + (ph - h) // 2
            win.geometry(f"+{x}+{y}")
        except Exception:
            try:
                sw = win.winfo_screenwidth()
                sh = win.winfo_screenheight()
                win.geometry(f"+{(sw - 400)//2}+{(sh - 300)//2}")
            except Exception:
                pass
