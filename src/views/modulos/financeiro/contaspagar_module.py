import tkinter as tk
from tkinter import ttk, messagebox
from src.config.estilos import CORES, FONTES
from datetime import datetime, timedelta
from src.db.financeiro_db import FinanceiroDB

class ContasPagarModule:
    """
    Tela de Contas a Pagar (mensais e variáveis), com suporte a:
    - Cadastro de contas com dia fixo de vencimento e valor previsto (opcional)
    - Marcar como Paga/Em Aberto
    - Listagem com destaque para atrasos
    - Filtros por mês/status
    
    Nota: Nesta primeira versão estático/GUI. Integração com DB virá em seguida
    (criação da tabela e métodos no FinanceiroDB/Controller).
    """
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        # Fundo da tela deve ser exatamente a mesma cor usada pelo fundo/borda do app
        # Usamos CORES['fundo'] para combinar 1:1 com a moldura externa
        bg_base = CORES.get("fundo", "#f0f2f5")

        self.frame = tk.Frame(parent, bg=bg_base)

        # Título no padrão do sistema (Cadastro > Usuários)
        tk.Label(
            self.frame,
            text="Contas a Pagar",
            font=FONTES.get("subtitulo", ("Arial", 16, "bold")),
            bg="#f0f2f5",
            fg=CORES.get("texto", "#000")
        ).pack(pady=(10, 5), anchor='w')

        # Esta tela não exibe status do caixa por padrão do sistema

        try:
            body = tk.Frame(self.frame, bg=bg_base)
            body.pack(fill='both', expand=True)

            # Coluna esquerda (ações)
            left_col = tk.Frame(body, bg=bg_base, width=230)
            left_col.pack(side='left', anchor='n', padx=10, pady=5, fill='y')
            # Garante largura fixa para aparecer mesmo sem conteúdo dinâmico
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

            tk.Button(left_col, text="Nova Conta", command=self._nova_conta_fixa, **btn_style).pack(fill='x', pady=4)
            tk.Button(left_col, text="Editar", command=self._editar, **btn_style).pack(fill='x', pady=4)
            tk.Button(left_col, text="Pagar", command=self._pagar_selecionada, **btn_style).pack(fill='x', pady=4)
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
            self.cmb_status = ttk.Combobox(filtros, values=['Todos','Aberto','Pago','Atrasado'], width=12)
            self.cmb_status.current(0)
            self.cmb_status.pack(side='left')

            # Botão de filtro no mesmo padrão visual dos demais botões
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
            # Deixar a tabela com fundo branco e o resto cinza (bg_base)
            style = ttk.Style()
            try:
                style.configure("CP.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
                style.configure("CP.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
            except Exception:
                # Se o tema não suportar, ignora silenciosamente
                pass
            cols = (
                'descricao','categoria','valor_prev','valor_atual','status','vencimento','dias_atraso'
            )
            self.tree = ttk.Treeview(right, columns=cols, show='headings', height=16, style='CP.Treeview')
            self.tree.pack(fill='both', expand=True, pady=(10, 0))

            # Menu de contexto (clique direito): apenas Cancelar Pagamento
            self._ctx_menu = tk.Menu(self.tree, tearoff=0)
            self._ctx_menu.add_command(label="Cancelar Pagamento", command=self._cancelar_pagamento)

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
            self.tree.bind('<Button-3>', _on_right_click)

            headers = {
                'descricao': 'Descrição',
                'categoria': 'Categoria',
                'valor_prev': 'Va.Previsto',
                'valor_atual': 'Va.Atual',
                'status': 'Status',
                'vencimento': 'Vencimento',
                'dias_atraso': 'Dias Atraso',
            }
            widths = {
                'descricao': 130,
                'categoria': 60,
                'valor_prev': 30,
                'valor_atual': 30,
                'status': 20,
                'vencimento': 40,
                'dias_atraso': 20,
            }
            for c in cols:
                self.tree.heading(c, text=headers[c])
                self.tree.column(c, width=widths[c], anchor='w')

            # Carregamento inicial a partir do banco de dados
            self._carregar_dados_db()
        except Exception as e:
            try:
                import traceback
                traceback.print_exc()
            except Exception:
                pass
            messagebox.showerror("Contas a Pagar", f"Falha ao montar a tela: {e}")

    # ------------- UI helpers -------------

    def _carregar_dados_db(self, status_filtro: str | None = None, mes_filtro: int | None = None, apenas_atrasados: bool = False):
        """Carrega as contas a pagar do banco e popula a Treeview.
        - status_filtro: 'aberto' | 'pago' | None
        - mes_filtro: 1..12 para filtrar por mês de vencimento (quando houver), senão por dia_vencimento no mês corrente
        - apenas_atrasados: quando True, mostra somente contas em aberto com vencimento passado
        """
        # Limpa a lista
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Obtém conexão
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return
        db = FinanceiroDB(db_conn)
        # Busca do banco por status
        linhas = db.listar_contas_pagar(status_filtro) or []

        hoje = datetime.now().date()
        for row in linhas:
            # Filtro por mês (quando mes_filtro fornecido)
            if mes_filtro:
                venc = row.get('vencimento')
                if venc:
                    try:
                        if hasattr(venc, 'month'):
                            if venc.month != mes_filtro:
                                continue
                        else:
                            # Se vier string 'YYYY-MM-DD'
                            if int(str(venc)[5:7]) != mes_filtro:
                                continue
                    except Exception:
                        pass
                else:
                    # Sem data específica, tenta estimar pela coluna dia_vencimento dentro do mês atual
                    if int(row.get('dia_vencimento') or 0) <= 0:
                        continue
            # Filtro de atrasados (aberto e vencimento < hoje)
            if apenas_atrasados:
                if (row.get('status') != 'aberto'):
                    continue
                venc = row.get('vencimento')
                try:
                    if venc:
                        vdate = venc if hasattr(venc, 'toordinal') else datetime.strptime(str(venc), '%Y-%m-%d').date()
                        if vdate >= hoje:
                            continue
                    else:
                        # Sem data definida não consideramos atrasado
                        continue
                except Exception:
                    continue

            valores = (
                row.get('descricao') or '',
                row.get('categoria') or '', 
                (f"{float(row.get('valor_previsto') or 0):.2f}" if row.get('valor_previsto') is not None else '-'),
                (f"{float(row.get('valor_atual') or 0):.2f}" if row.get('valor_atual') is not None else '-'),
                ('Pago' if (row.get('status') == 'pago') else 'Aberto'),
                (row.get('vencimento').strftime('%d/%m/%Y') if row.get('vencimento') else '-'),
                self._calc_dias_atraso(row.get('vencimento')),
            )
            # Usa o id do registro como iid para facilitar ações (excluir)
            try:
                iid = str(row.get('id'))
            except Exception:
                iid = ''
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

    # ------------- Ações (stubs) -------------
    def _nova_conta_fixa(self):
        """Abre o diálogo para cadastro de nova conta (fixa/variável) e opção de repetir 12 meses."""
        try:
            self._abrir_dialog_nova_conta()
        except Exception as e:
            try:
                import traceback
                traceback.print_exc()
            except Exception:
                pass
            messagebox.showerror("Contas a Pagar", f"Falha ao abrir cadastro: {e!r}")

    def _nova_conta_variavel(self):
        messagebox.showinfo("Contas a Pagar", "Cadastro de conta variável - em breve")

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Pagar", "Selecione um registro para editar.")
            return
        item_id = sel[0]
        if not item_id:
            return
        try:
            self._abrir_dialog_editar_pagar(int(item_id))
        except Exception as e:
            messagebox.showerror("Contas a Pagar", f"Falha ao abrir edição: {e}")

    def _abrir_dialog_editar_pagar(self, conta_id: int):
        # Coleta valores atuais da linha
        vals = self.tree.item(str(conta_id), 'values') if self.tree.exists(str(conta_id)) else None
        desc_atual = vals[0] if vals else ''
        cat_atual = vals[1] if vals else ''
        dia_venc_atual = int(vals[2]) if vals and str(vals[2]).isdigit() else 1
        valor_prev_atual = vals[3] if vals else '-'
        venc_atual_str = vals[6] if vals else '-'

        win = tk.Toplevel(self.frame)
        win.title("Editar Conta a Pagar")
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

        self._ed_desc = tk.Entry(body, font=('Arial', 10))
        self._ed_desc.insert(0, desc_atual)
        add("Descrição:", self._ed_desc)

        self._ed_cat = tk.Entry(body, font=('Arial', 10))
        self._ed_cat.insert(0, cat_atual)
        add("Categoria:", self._ed_cat)

        self._ed_valor_prev = tk.Entry(body, font=('Arial', 10))
        if valor_prev_atual and valor_prev_atual != '-':
            self._ed_valor_prev.insert(0, str(valor_prev_atual))
        add("Valor previsto:", self._ed_valor_prev)

        self._ed_venc = tk.Entry(body, font=('Arial', 10))
        if venc_atual_str and venc_atual_str != '-':
            self._ed_venc.insert(0, venc_atual_str)
        add("Vencimento (dd/mm/aaaa):", self._ed_venc)

        self._ed_dia = tk.Entry(body, font=('Arial', 10), width=6)
        self._ed_dia.insert(0, str(dia_venc_atual or 1))
        add("Dia de vencimento:", self._ed_dia)

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
        tk.Button(btn_bar, text="Salvar", command=lambda: self._salvar_edicao_pagar(win, conta_id), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))

        try:
            top = win.winfo_toplevel(); top.update_idletasks()
            sw = top.winfo_screenwidth(); sh = top.winfo_screenheight()
            w = 520; h = 260
            x = (sw - w) // 2; y = (sh - h) // 2
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _salvar_edicao_pagar(self, win: tk.Toplevel, conta_id: int):
        desc = (self._ed_desc.get() or '').strip()
        if not desc:
            messagebox.showwarning("Editar", "Informe a descrição.")
            return
        categoria = (self._ed_cat.get() or '').strip() or None
        valor_str = (self._ed_valor_prev.get() or '').strip().replace(',', '.')
        valor_prev = None
        if valor_str != '':
            try:
                valor_prev = float(valor_str)
            except Exception:
                messagebox.showwarning("Editar", "Valor previsto inválido.")
                return
        venc_str = (self._ed_venc.get() or '').strip()
        venc_date = None
        if venc_str:
            try:
                venc_date = datetime.strptime(venc_str, '%d/%m/%Y').date()
            except Exception:
                messagebox.showwarning("Editar", "Data de vencimento inválida (use dd/mm/aaaa).")
                return
        try:
            dia_venc = int((self._ed_dia.get() or '1').strip())
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
            db.atualizar_conta_pagar_dados(
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
            messagebox.showinfo("Contas a Pagar", "Selecione um registro para excluir.")
            return
        item_id = sel[0]
        if not item_id:
            return
        if not messagebox.askyesno("Excluir", "Confirma excluir esta conta? Esta ação não pode ser desfeita."):
            return
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Contas a Pagar", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)
        try:
            db.excluir_conta_pagar(int(item_id))
        except Exception as e:
            messagebox.showerror("Contas a Pagar", f"Falha ao excluir: {e}")
            return
        # Recarrega lista mantendo filtro atual
        self._aplicar_filtro()

    def _cancelar_pagamento(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Pagar", "Selecione uma conta para cancelar o pagamento.")
            return
        item_id = sel[0]
        if not item_id:
            return
        vals = self.tree.item(item_id, 'values') if self.tree.exists(item_id) else None
        if not vals:
            return
        status_txt = (vals[5] or '').strip().lower()
        if status_txt != 'pago':
            messagebox.showinfo("Contas a Pagar", "A conta selecionada não está paga.")
            return
        # Valor pago: usar valor_atual quando disponível, senão tentar valor_prev
        valor = 0.0
        try:
            if vals[4] and vals[4] != '-':
                valor = float(str(vals[4]).replace(',', '.'))
            elif vals[3] and vals[3] != '-':
                valor = float(str(vals[3]).replace(',', '.'))
        except Exception:
            valor = 0.0
        if valor <= 0:
            if not messagebox.askyesno("Cancelar Pagamento", "Valor pago não identificado. Cancelar mesmo assim (sem estorno no caixa)?"):
                return

        if not messagebox.askyesno("Cancelar Pagamento", "Confirma cancelar o pagamento desta conta? O valor será estornado no caixa." ):
            return

        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Cancelar Pagamento", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)

        # Verifica sessão de caixa aberta para lançar estorno
        sessao = db.get_caixa_aberto()
        if not sessao:
            messagebox.showerror("Cancelar Pagamento", "Não há caixa aberto. Abra o caixa para estornar o pagamento.")
            return
        sessao_id = sessao.get('id')

        desc = vals[0] if vals else f"Conta #{item_id}"

        try:
            # 1) Estorna no caixa/financeiro (entrada com mesmo valor)
            if valor > 0:
                db.registrar_movimento_financeiro(
                    valor=valor,
                    tipo='entrada',
                    descricao=f"Estorno pagamento de conta: {desc}",
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

            # 2) Reabre a conta: zera valor_atual e status='aberto'
            db.atualizar_conta_pagar_valor(int(item_id), None)
            db.atualizar_conta_pagar_status(int(item_id), 'aberto')
        except Exception as e:
            messagebox.showerror("Cancelar Pagamento", f"Falha ao cancelar pagamento: {e}")
            return

        self._aplicar_filtro()

    def _pagar_selecionada(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Contas a Pagar", "Selecione uma conta para pagar.")
            return
        item_id = sel[0]
        if not item_id:
            return
        try:
            self._abrir_dialog_pagar(int(item_id))
        except Exception as e:
            messagebox.showerror("Contas a Pagar", f"Falha ao abrir pagamento: {e}")

    def _abrir_dialog_pagar(self, conta_id: int):
        # Busca dados básicos da linha selecionada para preencher o diálogo
        vals = self.tree.item(str(conta_id), 'values') if self.tree.exists(str(conta_id)) else None
        desc = vals[0] if vals else ''
        valor_sugerido = 0.0
        try:
            # valor_prev (índice 3) quando disponível; senão valor_atual (índice 4)
            if vals and vals[3] != '-' and str(vals[3]).strip() != '':
                valor_sugerido = float(str(vals[3]).replace(',', '.'))
            elif vals and vals[4] != '-' and str(vals[4]).strip() != '':
                valor_sugerido = float(str(vals[4]).replace(',', '.'))
        except Exception:
            valor_sugerido = 0.0

        win = tk.Toplevel(self.frame)
        win.title("Pagar Conta")
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

        self._pg_valor = tk.Entry(body, font=('Arial', 10))
        self._pg_valor.insert(0, f"{valor_sugerido:.2f}")
        add("Valor a pagar:", self._pg_valor)

        self._pg_forma = ttk.Combobox(body, values=['dinheiro','cartao_debito','pix'], width=18, state='readonly')
        self._pg_forma.current(0)
        add("Forma de pagamento:", self._pg_forma)

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
        tk.Button(btn_bar, text="Lançar Pagamento", command=lambda: self._confirmar_pagamento(win, conta_id), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))
        self._center_window(win)

    def _confirmar_pagamento(self, win: tk.Toplevel, conta_id: int):
        # Lê e valida
        try:
            valor = float((self._pg_valor.get() or '0').replace(',', '.'))
        except Exception:
            messagebox.showwarning("Pagamento", "Informe um valor válido.")
            return
        forma = (self._pg_forma.get() or '').strip() or 'dinheiro'
        if valor <= 0:
            messagebox.showwarning("Pagamento", "Valor deve ser maior que zero.")
            return

        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Pagamento", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)

        # Verifica sessão de caixa aberta
        sessao = db.get_caixa_aberto()
        if not sessao:
            messagebox.showerror("Pagamento", "Não há caixa aberto. Abra o caixa para lançar saídas.")
            return
        sessao_id = sessao.get('id')

        # Descrição do movimento financeiro
        vals = self.tree.item(str(conta_id), 'values') if self.tree.exists(str(conta_id)) else None
        desc = (vals[0] if vals else f"Conta #{conta_id}")

        try:
            # 1) Registra saída no financeiro
            db.registrar_movimento_financeiro(
                valor=valor,
                tipo='saida',
                descricao=f"Pagamento de conta: {desc}",
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

            # 2) Atualiza conta: valor_atual e status=pago
            db.atualizar_conta_pagar_valor(conta_id, valor)
            db.atualizar_conta_pagar_status(conta_id, 'pago')
        except Exception as e:
            messagebox.showerror("Pagamento", f"Falha ao lançar pagamento: {e}")
            return

        try:
            win.destroy()
        except Exception:
            pass
        self._aplicar_filtro()

    def _marcar_paga(self):
        messagebox.showinfo("Contas a Pagar", "Marcar como paga - em breve")

    def _marcar_aberta(self):
        messagebox.showinfo("Contas a Pagar", "Marcar como aberta - em breve")

    def _recarregar(self):
        messagebox.showinfo("Contas a Pagar", "Recarregar lista - em breve")

    def _aplicar_filtro(self):
        # Lê filtros e recarrega a lista a partir do banco
        mes_val = None
        status_val = None
        apenas_atrasados = False
        try:
            # Mês (mapear índice 0..11 -> 1..12)
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
            elif st == 'pago':
                status_val = 'pago'
            elif st == 'atrasado':
                status_val = 'aberto'
                apenas_atrasados = True
            else:
                status_val = None
        except Exception:
            status_val = None
        self._carregar_dados_db(status_filtro=status_val, mes_filtro=mes_val, apenas_atrasados=apenas_atrasados)

    # ------------- Diálogo de Nova Conta -------------
    def _abrir_dialog_nova_conta(self):
        # Diálogo limpo, layout em grid 2 colunas, sem estilos de bg para compatibilidade
        win = tk.Toplevel(self.frame)
        win.title("Nova Conta a Pagar")
        win.transient(self.frame.winfo_toplevel())
        win.grab_set()
        win.resizable(False, False)

        body = tk.Frame(win)
        body.pack(padx=16, pady=16, fill='both', expand=True)

        # Configura grid: 2 colunas (0=labels, 1=inputs)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)

        row = 0
        def add(label, widget):
            nonlocal row
            tk.Label(body, text=label, font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
            widget.grid(row=row, column=1, sticky='we', pady=4)
            row += 1

        self._nc_descricao = tk.Entry(body, font=('Arial', 10))
        add("Descrição:", self._nc_descricao)

        self._nc_categoria = tk.Entry(body, font=('Arial', 10))
        add("Categoria:", self._nc_categoria)

        self._nc_valor = tk.Entry(body, font=('Arial', 10))
        add("Valor previsto:", self._nc_valor)

        self._nc_vencimento = tk.Entry(body, font=('Arial', 10))
        add("Vencimento (dd/mm/aaaa):", self._nc_vencimento)

        # Linha de opções (checkboxes) alinhadas na coluna 1
        self._nc_repetir = tk.IntVar(value=0)
        self._nc_var_valor = tk.IntVar(value=0)
        opts = tk.Frame(body)
        tk.Checkbutton(opts, text="Repetir por 12 meses", variable=self._nc_repetir, anchor='w').pack(side='left', padx=(0, 16))
        tk.Checkbutton(opts, text="Valor variável", variable=self._nc_var_valor, anchor='w').pack(side='left')
        tk.Label(body, text="Opções:", font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=(6,4))
        opts.grid(row=row, column=1, sticky='w', pady=(6,4))
        row += 1

        # Barra de botões alinhados à direita
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
        # Centraliza a janela no centro da tela (ou do parent)
        self._center_window(win)

    def _nc_salvar(self, win):
        # Validações básicas
        desc = (self._nc_descricao.get() or '').strip()
        if not desc:
            messagebox.showwarning("Nova Conta", "Informe a descrição.")
            return
        categoria = (self._nc_categoria.get() or '').strip() or None
        valor_str = (self._nc_valor.get() or '').replace(',', '.').strip()
        valor_prev = None if self._nc_var_valor.get() == 1 or valor_str == '' else self._safe_float(valor_str)
        if valor_prev is False:
            messagebox.showwarning("Nova Conta", "Valor previsto inválido.")
            return

        venc_str = (self._nc_vencimento.get() or '').strip()
        repetir = (self._nc_repetir.get() == 1)

        # Exige data de vencimento. Geraremos repetições a partir dela.
        try:
            base_date = datetime.strptime(venc_str, '%d/%m/%Y').date()
        except Exception:
            messagebox.showwarning("Nova Conta", "Informe a data de vencimento válida (dd/mm/aaaa).")
            return

        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Nova Conta", "Sem conexão com o banco de dados.")
            return
        db = FinanceiroDB(db_conn)

        # Gera lançamentos (1 ou 12)
        total = 12 if repetir else 1
        criados = 0
        for i in range(total):
            try:
                vdate = self._add_months(base_date, i)
                dia = vdate.day
                db.criar_conta_pagar(
                    descricao=desc,
                    categoria=categoria,
                    dia_vencimento=int(dia),
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
            # Recarrega lista respeitando filtros atuais
            self._aplicar_filtro()

    def _safe_float(self, txt: str):
        try:
            return float(txt)
        except Exception:
            return False

    def _add_months(self, dt, months):
        # Avança meses preservando o dia, ajustando para fim do mês quando necessário
        year = dt.year + (dt.month - 1 + months) // 12
        month = (dt.month - 1 + months) % 12 + 1
        day = dt.day
        # Ajusta para último dia do novo mês quando o dia não existir
        last_day = self._last_day_of_month(year, month)
        if day > last_day:
            day = last_day
        return datetime(year, month, day).date()

    def _center_window(self, win: tk.Toplevel):
        """Centraliza uma janela Toplevel em relação à janela principal.
        Usa medidas calculadas após layout para definir a geometria +x+y.
        """
        try:
            win.update_idletasks()
            w = win.winfo_width() or win.winfo_reqwidth()
            h = win.winfo_height() or win.winfo_reqheight()
            parent = win.master.winfo_toplevel() if win.master else win.winfo_toplevel()
            # Dimensões do parent; se falhar, usa tela inteira
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
            # fallback: central na tela
            try:
                sw = win.winfo_screenwidth()
                sh = win.winfo_screenheight()
                win.geometry(f"+{(sw - 400)//2}+{(sh - 300)//2}")
            except Exception:
                pass

    def _date_from_month_offset(self, dia: int, offset: int):
        base = datetime.now()
        year = base.year + (base.month - 1 + offset) // 12
        month = (base.month - 1 + offset) % 12 + 1
        last_day = self._last_day_of_month(year, month)
        if dia > last_day:
            dia = last_day
        return datetime(year, month, dia).date()

    def _last_day_of_month(self, year, month):
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        return (next_month - timedelta(days=1)).day
