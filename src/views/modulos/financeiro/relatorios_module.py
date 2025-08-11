import tkinter as tk
from tkinter import ttk, messagebox
from src.config.estilos import CORES, FONTES
from datetime import datetime, date
from src.db.financeiro_db import FinanceiroDB

class RelatoriosModule:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        # Fundo base igual ao ContasPagarModule
        bg_base = CORES.get("fundo", "#f0f2f5")
        self.frame = tk.Frame(parent, bg=bg_base)

        # Título no mesmo padrão
        tk.Label(
            self.frame,
            text="Relatórios",
            font=FONTES.get("subtitulo", ("Arial", 16, "bold")),
            bg=bg_base,
            fg=CORES.get("texto", "#000")
        ).pack(pady=(10, 5), anchor='w')

        # Corpo com duas colunas (esquerda: botões | direita: área de conteúdo)
        body = tk.Frame(self.frame, bg=bg_base)
        body.pack(fill='both', expand=True)

        # Coluna esquerda fixa para botões
        left_col = tk.Frame(body, bg=bg_base, width=230)
        left_col.pack(side='left', anchor='n', padx=10, pady=5, fill='y')
        left_col.pack_propagate(False)

        # Estilo dos botões igual ao Contas a Pagar
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

        tk.Button(left_col, text="Relatório financeiro", command=self._on_relatorio_entradas_saidas, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Relatórios médicos", command=self._on_relatorio_medicos, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Relatório de Caixa", command=self._on_relatorio_caixa, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Relatório de Contas", command=self._on_relatorio_contas, **btn_style).pack(fill='x', pady=4)

        # Área direita para futuros filtros/preview, mantendo o mesmo fundo
        right = tk.Frame(body, bg=bg_base)
        right.pack(side='left', fill='both', expand=True, padx=(10, 10), pady=(5, 10))


    def _get_bg(self):
        # Mantido por compatibilidade, mas o bg da tela é o bg_base acima (CORES['fundo'])
        try:
            return self.parent.cget("bg")
        except Exception:
            return CORES.get("fundo", "#f0f2f5")

    # --- Handlers de Relatórios (stubs com pontos de integração) ---
    def _on_relatorio_entradas_saidas(self):
        """Abre o relatório financeiro (entradas/saídas) por período com totais."""
        self._abrir_relatorio_financeiro()

    def _on_relatorio_medicos(self):
        """Abre o relatório de faturamento por médico (período + médico)."""
        self._abrir_relatorio_medicos()

    def _on_relatorio_caixa(self):
        """Relatório de conferência do caixa (entradas, saídas, saldo, diferenças)."""
        self._abrir_relatorio_caixa()

    def abrir_relatorio_contas(self):
        """Abre a janela do Relatório de Contas (Pagar/Receber)."""
        self._abrir_relatorio_contas()

    def _abrir_relatorio_contas(self):
        import tkinter as tk
        from tkinter import ttk, messagebox
        from datetime import datetime, timedelta
        CORES = getattr(self, 'CORES', {'bg': '#f5f6fa', 'texto': '#222'})
        FONTES = getattr(self, 'FONTES', {'tabela_cabecalho': ('Arial', 10, 'bold')})

        dlg = tk.Toplevel(self.frame)
        dlg.title("Relatório de Contas (Pagar/Receber)")
        dlg.configure(bg=CORES.get('bg', '#f5f6fa'))
        # Usa o toplevel raiz para transiência/centralização corretas
        dlg.transient(self.frame.winfo_toplevel())
        try:
            dlg.grab_set()
        except Exception:
            pass

        bg_base = CORES.get('bg', '#f5f6fa')
        topo = tk.Frame(dlg, bg=bg_base)
        topo.pack(fill='x', padx=16, pady=16)

        tk.Label(topo, text="Período:", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left')
        ent_ini = tk.Entry(topo, width=12)
        ent_fim = tk.Entry(topo, width=12)
        hoje = datetime.now().date()
        ent_ini.insert(0, (hoje - timedelta(days=hoje.weekday())).strftime('%d/%m/%Y'))
        ent_fim.insert(0, (hoje + timedelta(days=(6 - hoje.weekday()))).strftime('%d/%m/%Y'))
        ent_ini.pack(side='left', padx=(6, 8))
        tk.Label(topo, text="até", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left')
        ent_fim.pack(side='left', padx=(6, 16))

        tk.Label(topo, text="Tipo:", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left')
        cmb_tipo = ttk.Combobox(topo, state='readonly', width=20)
        cmb_tipo['values'] = ['Contas a Pagar', 'Contas a Receber']
        cmb_tipo.current(0)
        cmb_tipo.pack(side='left', padx=(6, 16))

        tk.Label(topo, text="Situação:", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left')
        cmb_status = ttk.Combobox(topo, state='readonly', width=18)
        # Opções genéricas mapeadas por tipo selecionado
        cmb_status['values'] = ['Quitadas/Recebidas', 'Em aberto', 'Em atraso']
        cmb_status.current(0)
        cmb_status.pack(side='left', padx=(6, 16))

        btn_filtrar = tk.Button(topo, text="Filtrar", font=('Arial', 10, 'bold'), bg='#4a6fa5', fg='white', bd=0, padx=16, pady=4, relief='flat', cursor='hand2')
        btn_filtrar.pack(side='left')

        tabela_wrap = tk.Frame(dlg, bg=bg_base)
        tabela_wrap.pack(fill='both', expand=True, padx=16, pady=(10, 0))

        style = ttk.Style()
        try:
            style.configure("RC2.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("RC2.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass

        cols = ('id', 'descricao', 'categoria', 'vencimento', 'pago_em', 'valor_previsto', 'valor_atual', 'status')
        headers = {
            'id': 'ID', 'descricao': 'Descrição', 'categoria': 'Categoria', 'vencimento': 'Vencimento',
            'pago_em': 'Pago/Recebido em', 'valor_previsto': 'Valor Previsto', 'valor_atual': 'Valor Atual', 'status': 'Status'
        }
        widths = {'id': 70, 'descricao': 320, 'categoria': 160, 'vencimento': 120, 'pago_em': 150, 'valor_previsto': 120, 'valor_atual': 120, 'status': 100}

        tree = ttk.Treeview(tabela_wrap, columns=cols, show='headings', height=18, style='RC2.Treeview')
        tree.pack(fill='both', expand=True)
        for c in cols:
            tree.heading(c, text=headers[c])
            tree.column(c, width=widths[c], anchor='w')

        totals = tk.Frame(dlg, bg=bg_base)
        totals.pack(fill='x', padx=16, pady=(8, 16))
        lbl_qtd = tk.Label(totals, text="Quantidade: 0", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_tot = tk.Label(totals, text="Total: R$ 0,00", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_qtd.pack(side='left')
        lbl_tot.pack(side='left', padx=(20,0))

        def parse_date_br(d: str):
            try:
                return datetime.strptime(d.strip(), '%d/%m/%Y')
            except Exception:
                return None

        def acao_filtrar(event=None):
            dt_i = parse_date_br(ent_ini.get())
            dt_f = parse_date_br(ent_fim.get())
            if not dt_i or not dt_f:
                messagebox.showinfo("Relatório de Contas", "Informe o período em formato DD/MM/AAAA.")
                return
            # inclui final do dia
            dt_f = dt_f.replace(hour=23, minute=59, second=59)
            self._carregar_contas_para_tree(tree, lbl_qtd, lbl_tot, dt_i, dt_f, cmb_tipo.get(), cmb_status.get())

        btn_filtrar.config(command=acao_filtrar)
        cmb_tipo.bind('<<ComboboxSelected>>', acao_filtrar)
        cmb_status.bind('<<ComboboxSelected>>', acao_filtrar)

        # Primeira carga
        acao_filtrar()

        # Centraliza
        try:
            dlg.update_idletasks()
            w = 1100
            h = 560
            sw = dlg.winfo_screenwidth()
            sh = dlg.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _carregar_contas_para_tree(self, tree, lbl_qtd, lbl_tot, dt_ini, dt_fim, tipo: str, situacao: str):
        # Formatter local para valores em BRL
        def brl(x: float) -> str:
            try:
                return f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            except Exception:
                return str(x)

        # Obtém controller de relatórios
        try:
            from src.controllers.relatorios_controller import RelatoriosController
        except Exception:
            try:
                from controllers.relatorios_controller import RelatoriosController
            except Exception:
                RelatoriosController = None  # will raise below if not found

        if not RelatoriosController:
            from tkinter import messagebox
            messagebox.showerror("Relatório de Contas", "RelatoriosController não encontrado.")
            return

        rc = getattr(self, "_relatorios_controller", None)
        if rc is None:
            db_conn = getattr(self.controller, 'db_connection', None)
            if not db_conn:
                return
            rc = RelatoriosController(db_conn)
            setattr(self, "_relatorios_controller", rc)

        # Busca dados via controller
        try:
            rows, qtd, total = rc.listar_contas(dt_ini, dt_fim, tipo, situacao)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Relatório de Contas", f"Falha ao consultar dados: {e}")
            rows, qtd, total = [], 0, 0.0

        for i in tree.get_children():
            tree.delete(i)
        for r in rows:
            vp = r.get('valor_previsto') or 0.0
            va = r.get('valor_atual') or 0.0
            ven = r.get('vencimento')
            pago = r.get('pago_em')
            ven_txt = ven.strftime('%d/%m/%Y') if ven and hasattr(ven, 'strftime') else (str(ven) if ven else '-')
            pago_txt = pago.strftime('%d/%m/%Y %H:%M') if pago and hasattr(pago, 'strftime') else (str(pago) if pago else '-')
            tree.insert('', 'end', values=(
                r.get('id'), r.get('descricao') or '', r.get('categoria') or '', ven_txt, pago_txt,
                brl(float(vp or 0.0)), brl(float(va or 0.0)), r.get('status')
            ))

        if qtd == 0:
            tree.insert('', 'end', values=("-", "Sem registros no período/filtro", "-", "-", "-", "-", "-", "-"))
        # Rodapé
        if 'Pagar' in tipo:
            if situacao.startswith('Quitadas'):
                lbl_qtd.config(text=f"Quantidade pagas: {qtd}")
                lbl_tot.config(text=f"Total pago: R$ {brl(total)}")
            elif situacao.startswith('Em aberto'):
                lbl_qtd.config(text=f"Quantidade em aberto: {qtd}")
                lbl_tot.config(text=f"Total em aberto: R$ {brl(total)}")
            else:
                lbl_qtd.config(text=f"Quantidade em atraso: {qtd}")
                lbl_tot.config(text=f"Total em atraso: R$ {brl(total)}")
        else:
            if situacao.startswith('Quitadas'):
                lbl_qtd.config(text=f"Quantidade recebidas: {qtd}")
                lbl_tot.config(text=f"Total recebido: R$ {brl(total)}")
            elif situacao.startswith('Em aberto'):
                lbl_qtd.config(text=f"Quantidade em aberto: {qtd}")
                lbl_tot.config(text=f"Total em aberto: R$ {brl(total)}")
            else:
                lbl_qtd.config(text=f"Quantidade em atraso: {qtd}")
                lbl_tot.config(text=f"Total em atraso: R$ {brl(total)}")
    def _on_relatorio_contas(self):
        """Abre o Relatório de Contas (Pagar/Receber)."""
        try:
            self.abrir_relatorio_contas()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Relatório de Contas", f"Falha ao abrir: {e}")
        # Integração futura:
        # - Consultar contas_pagar e contas_receber por intervalo de datas, status e categoria

    # ----------------- Relatório de Caixa (por período/usuário/sessão) -----------------
    def _abrir_relatorio_caixa(self):
        bg_base = CORES.get("fundo", "#f0f2f5")
        dlg = tk.Toplevel(self.frame)
        dlg.title("Relatório de Caixa")
        dlg.configure(bg=bg_base)
        dlg.transient(self.frame.winfo_toplevel())
        dlg.grab_set()

        # Header
        tk.Label(
            dlg, text="Relatório de Caixa (diferenças por sessão)",
            font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000')
        ).pack(padx=16, pady=(16, 8), anchor='w')

        # Filtros
        filtros = tk.Frame(dlg, bg=bg_base)
        filtros.pack(fill='x', padx=16)

        tk.Label(filtros, text="Início (dd/mm/aaaa):", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0,6))
        ent_ini = tk.Entry(filtros, width=12)
        ent_ini.pack(side='left', padx=(0,14))

        tk.Label(filtros, text="Fim (dd/mm/aaaa):", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0,6))
        ent_fim = tk.Entry(filtros, width=12)
        ent_fim.pack(side='left', padx=(0,14))

        # Sugestão: mês atual
        from datetime import date
        hoje = date.today()
        mes_ini = hoje.replace(day=1)
        ent_ini.insert(0, mes_ini.strftime('%d/%m/%Y'))
        ent_fim.insert(0, hoje.strftime('%d/%m/%Y'))

        tk.Label(filtros, text="Usuário:", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(10,6))
        cmb_usuario = ttk.Combobox(filtros, width=35, state='readonly')
        cmb_usuario.pack(side='left', padx=(0,14))

        tk.Label(filtros, text="Caixa/Sessão:", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(10,6))
        cmb_sessao = ttk.Combobox(filtros, width=28, state='readonly')
        cmb_sessao.pack(side='left', padx=(0,14))

        btn_filtrar = tk.Button(
            filtros, text="Filtrar",
            font=('Arial', 10, 'bold'), bg='#4a6fa5', fg='white', bd=0, padx=16, pady=4, relief='flat', cursor='hand2'
        )
        btn_filtrar.pack(side='left')

        # Tabela
        tabela_wrap = tk.Frame(dlg, bg=bg_base)
        tabela_wrap.pack(fill='both', expand=True, padx=16, pady=(10, 0))

        style = ttk.Style()
        try:
            style.configure("RC.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("RC.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass

        # Mostrar somente erros (diferenças) por forma e tipo (entrada/saída)
        cols = ('sessao', 'abertura', 'fechamento', 'usuario', 'tipo', 'forma', 'esperado', 'contado', 'diferenca', 'obs')
        headers = {
            'sessao': 'Sessão', 'abertura': 'Abertura', 'fechamento': 'Fechamento', 'usuario': 'Usuário',
            'tipo': 'Tipo', 'forma': 'Forma', 'esperado': 'Esperado', 'contado': 'Contado', 'diferenca': 'Diferença', 'obs': 'Observação'
        }
        widths = {'sessao': 80, 'abertura': 140, 'fechamento': 140, 'usuario': 160,
                  'tipo': 90, 'forma': 140, 'esperado': 110, 'contado': 110, 'diferenca': 110, 'obs': 260}

        tree = ttk.Treeview(tabela_wrap, columns=cols, show='headings', height=16, style='RC.Treeview')
        tree.pack(fill='both', expand=True)
        for c in cols:
            tree.heading(c, text=headers[c])
            tree.column(c, width=widths[c], anchor='w')

        # Rodapé de totais das diferenças
        totals = tk.Frame(dlg, bg=bg_base)
        totals.pack(fill='x', padx=16, pady=(8, 16))
        lbl_tot_dif_e = tk.Label(totals, text="Σ Dif. Entradas: R$ 0,00", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_tot_dif_s = tk.Label(totals, text="Σ Dif. Saídas: R$ 0,00", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_tot_dif_e.pack(side='left')
        lbl_tot_dif_s.pack(side='left', padx=(20,0))

        # Ações dos filtros
        def acao_filtrar():
            usuarios = self._carregar_usuarios_caixa(ent_ini.get(), ent_fim.get())
            exib = [f"{u['nome']} ({u['id']})" for u in usuarios]
            cmb_usuario['values'] = ["(Todos)"] + exib
            if exib:
                cmb_usuario.current(0)
            # Carrega sessões com base em período e usuário atual (se houver)
            self._preencher_sessoes_combo(cmb_sessao, ent_ini.get(), ent_fim.get(), usuarios, cmb_usuario.get())
            # Carrega dados da sessão selecionada (se houver)
            self._carregar_conferencias_para_tree(tree, lbl_tot_dif_e, lbl_tot_dif_s, ent_ini.get(), ent_fim.get(), usuarios, cmb_usuario.get(), cmb_sessao.get())

        def acao_usuario_changed(event=None):
            usuarios = self._carregar_usuarios_caixa(ent_ini.get(), ent_fim.get())
            self._preencher_sessoes_combo(cmb_sessao, ent_ini.get(), ent_fim.get(), usuarios, cmb_usuario.get())
            self._carregar_conferencias_para_tree(tree, lbl_tot_dif_e, lbl_tot_dif_s, ent_ini.get(), ent_fim.get(), usuarios, cmb_usuario.get(), cmb_sessao.get())

        def acao_sessao_changed(event=None):
            usuarios = self._carregar_usuarios_caixa(ent_ini.get(), ent_fim.get())
            self._carregar_conferencias_para_tree(tree, lbl_tot_dif_e, lbl_tot_dif_s, ent_ini.get(), ent_fim.get(), usuarios, cmb_usuario.get(), cmb_sessao.get())

        btn_filtrar.config(command=acao_filtrar)
        cmb_usuario.bind('<<ComboboxSelected>>', acao_usuario_changed)
        cmb_sessao.bind('<<ComboboxSelected>>', acao_sessao_changed)

        # Primeira carga
        acao_filtrar()

        # Centraliza
        try:
            dlg.update_idletasks()
            w = 1130
            h = 560
            sw = dlg.winfo_screenwidth()
            sh = dlg.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _preencher_sessoes_combo(self, cmb_sessao: ttk.Combobox, dt_ini: str, dt_fim: str, usuarios: list, usuario_exib: str):
        cmb_sessao.set("")
        cmb_sessao['values'] = []
        sessoes = self._carregar_sessoes_caixa(dt_ini, dt_fim, usuarios, usuario_exib)
        exib = [f"ID {s['id']} - {s['abertura']}" for s in sessoes]
        # Adiciona opção (Todas) para listar todas as conferências do período/usuário
        cmb_sessao['values'] = ["(Todas)"] + exib if exib else ["(Nenhuma)"]
        if exib:
            cmb_sessao.current(0)

    def _carregar_usuarios_caixa(self, dt_ini_str: str, dt_fim_str: str) -> list:
        dt_ini = self._parse_date_br(dt_ini_str)
        dt_fim = self._parse_date_br(dt_fim_str)
        if not dt_ini or not dt_fim:
            return []
        from datetime import datetime as _dt
        inicio = _dt.combine(dt_ini, _dt.min.time())
        fim = _dt.combine(dt_fim, _dt.max.time())
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return []
        cur = db_conn.cursor()
        ids = set()
        try:
            try:
                cur.execute(
                    """
                    SELECT DISTINCT abertura_usuario_id AS uid
                    FROM caixa_sessoes
                    WHERE abertura_datahora BETWEEN %s AND %s AND abertura_usuario_id IS NOT NULL
                    UNION
                    SELECT DISTINCT fechamento_usuario_id AS uid
                    FROM caixa_sessoes
                    WHERE fechamento_datahora BETWEEN %s AND %s AND fechamento_usuario_id IS NOT NULL
                    UNION
                    SELECT DISTINCT usuario_id AS uid
                    FROM caixa_conferencias
                    WHERE datahora BETWEEN %s AND %s AND usuario_id IS NOT NULL
                    """,
                    (inicio, fim, inicio, fim, inicio, fim)
                )
                rows = cur.fetchall() or []
                for r in rows:
                    uid = r[0]
                    if uid is not None:
                        ids.add(int(uid))
            except Exception:
                return []
        finally:
            try:
                cur.close()
            except Exception:
                pass
        # Resolver nomes
        id_list = sorted(list(ids))
        nomes = self._resolver_nomes_usuarios(id_list)
        return [{ 'id': i, 'nome': nomes.get(i, f'Usuário {i}') } for i in id_list]

    def _resolver_nomes_usuarios(self, ids: list[int]) -> dict[int, str]:
        if not ids:
            return {}
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return {i: str(i) for i in ids}
        nomes = {i: str(i) for i in ids}
        cur = db_conn.cursor()
        try:
            in_clause = ",".join(["%s"] * len(ids))
            # Tenta várias estruturas conhecidas, acumulando resultados
            consultas = [
                (f"SELECT id, nome FROM usuarios WHERE id IN ({in_clause})", tuple(ids)),
                (f"SELECT id, usuario FROM usuarios WHERE id IN ({in_clause})", tuple(ids)),
                (f"SELECT id, nome_completo FROM usuarios WHERE id IN ({in_clause})", tuple(ids)),
                (f"SELECT id, nome FROM pessoas WHERE id IN ({in_clause})", tuple(ids)),
                (f"SELECT id, nome FROM usuarios_sistema WHERE id IN ({in_clause})", tuple(ids)),
                (f"SELECT id, nome FROM users WHERE id IN ({in_clause})", tuple(ids)),
            ]
            for sql, params in consultas:
                try:
                    cur.execute(sql, params)
                    for r in cur.fetchall() or []:
                        try:
                            uid = int(r[0])
                            nome = r[1]
                            if nome and str(nome).strip():
                                nomes[uid] = str(nome)
                        except Exception:
                            continue
                except Exception:
                    continue
            return nomes
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def _carregar_sessoes_caixa(self, dt_ini_str: str, dt_fim_str: str, usuarios: list, usuario_exib: str) -> list:
        dt_ini = self._parse_date_br(dt_ini_str)
        dt_fim = self._parse_date_br(dt_fim_str)
        if not dt_ini or not dt_fim:
            return []
        # Resolve usuário
        usuario_id = None
        if usuario_exib and usuario_exib not in ("(Todos)", "") and '(' in usuario_exib and usuario_exib.endswith(')'):
            try:
                usuario_id = int(usuario_exib.split('(')[-1][:-1])
            except Exception:
                usuario_id = None
        from datetime import datetime as _dt
        inicio = _dt.combine(dt_ini, _dt.min.time())
        fim = _dt.combine(dt_fim, _dt.max.time())
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return []
        cur = db_conn.cursor(dictionary=True)
        try:
            if usuario_id:
                cur.execute(
                    """
                    SELECT id, abertura_datahora, fechamento_datahora, abertura_usuario_id
                    FROM caixa_sessoes
                    WHERE (abertura_datahora BETWEEN %s AND %s OR (fechamento_datahora IS NOT NULL AND fechamento_datahora BETWEEN %s AND %s))
                      AND (abertura_usuario_id = %s OR fechamento_usuario_id = %s)
                    ORDER BY id DESC
                    """,
                    (inicio, fim, inicio, fim, usuario_id, usuario_id)
                )
            else:
                cur.execute(
                    """
                    SELECT id, abertura_datahora, fechamento_datahora, abertura_usuario_id
                    FROM caixa_sessoes
                    WHERE abertura_datahora BETWEEN %s AND %s OR (fechamento_datahora IS NOT NULL AND fechamento_datahora BETWEEN %s AND %s)
                    ORDER BY id DESC
                    """,
                    (inicio, fim, inicio, fim)
                )
            rows = cur.fetchall() or []
        except Exception:
            rows = []
        finally:
            try:
                cur.close()
            except Exception:
                pass
        # Formatar
        sessoes = []
        for r in rows:
            aid = r.get('id')
            ab = r.get('abertura_datahora')
            fe = r.get('fechamento_datahora')
            try:
                ab_txt = ab.strftime('%d/%m/%Y %H:%M') if hasattr(ab, 'strftime') else str(ab)
                fe_txt = fe.strftime('%d/%m/%Y %H:%M') if fe and hasattr(fe, 'strftime') else (str(fe) if fe else '-')
            except Exception:
                ab_txt, fe_txt = str(ab), (str(fe) if fe else '-')
            sessoes.append({'id': aid, 'abertura': ab_txt, 'fechamento': fe_txt})
        return sessoes

    def _carregar_conferencias_para_tree(self, tree: ttk.Treeview, lbl_tot_e: tk.Label, lbl_tot_s: tk.Label,
                                         dt_ini_str: str, dt_fim_str: str, usuarios: list,
                                         usuario_exib: str, sessao_exib: str):
        # Limpa tabela
        for iid in tree.get_children():
            tree.delete(iid)

        # Resolve sessão
        sessao_id = None
        if sessao_exib and sessao_exib not in ("(Todas)", "(Nenhuma)", ""):
            # formato: "ID 12 - 01/02/2025 09:00"
            try:
                sessao_id = int(sessao_exib.split()[1])
            except Exception:
                sessao_id = None

        # Resolve usuário
        usuario_id = None
        if usuario_exib and usuario_exib not in ("(Todos)", "") and '(' in usuario_exib and usuario_exib.endswith(')'):
            try:
                usuario_id = int(usuario_exib.split('(')[-1][:-1])
            except Exception:
                usuario_id = None

        # Datas
        dt_ini = self._parse_date_br(dt_ini_str)
        dt_fim = self._parse_date_br(dt_fim_str)
        if not dt_ini or not dt_fim:
            return
        from datetime import datetime as _dt
        inicio = _dt.combine(dt_ini, _dt.min.time())
        fim = _dt.combine(dt_fim, _dt.max.time())

        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return

        # Carrega conferências conforme filtros
        cur = db_conn.cursor(dictionary=True)
        rows = []
        try:
            if sessao_id:
                cur.execute(
                    """
                    SELECT c.*, s.abertura_datahora, s.fechamento_datahora, s.abertura_usuario_id, s.fechamento_usuario_id
                    FROM caixa_conferencias c
                    JOIN caixa_sessoes s ON s.id = c.sessao_id
                    WHERE c.sessao_id = %s
                    ORDER BY c.datahora ASC, c.id ASC
                    """,
                    (sessao_id,)
                )
                rows = cur.fetchall() or []
            else:
                if usuario_id:
                    cur.execute(
                        """
                        SELECT c.*, s.abertura_datahora, s.fechamento_datahora, s.abertura_usuario_id, s.fechamento_usuario_id
                        FROM caixa_conferencias c
                        JOIN caixa_sessoes s ON s.id = c.sessao_id
                        WHERE c.datahora BETWEEN %s AND %s
                          AND (c.usuario_id = %s OR s.abertura_usuario_id = %s)
                        ORDER BY c.datahora ASC, c.id ASC
                        """,
                        (inicio, fim, usuario_id, usuario_id)
                    )
                else:
                    cur.execute(
                        """
                        SELECT c.*, s.abertura_datahora, s.fechamento_datahora, s.abertura_usuario_id, s.fechamento_usuario_id
                        FROM caixa_conferencias c
                        JOIN caixa_sessoes s ON s.id = c.sessao_id
                        WHERE c.datahora BETWEEN %s AND %s
                        ORDER BY c.datahora ASC, c.id ASC
                        """,
                        (inicio, fim)
                    )
                rows = cur.fetchall() or []
        except Exception:
            rows = []
        finally:
            try:
                cur.close()
            except Exception:
                pass

        # Resolver nomes usuários para exibição
        ids = set()
        for r in rows:
            if r.get('usuario_id') is not None:
                try:
                    ids.add(int(r['usuario_id']))
                except Exception:
                    pass
            if r.get('abertura_usuario_id') is not None:
                try:
                    ids.add(int(r['abertura_usuario_id']))
                except Exception:
                    pass
            if r.get('fechamento_usuario_id') is not None:
                try:
                    ids.add(int(r['fechamento_usuario_id']))
                except Exception:
                    pass
        nomes = self._resolver_nomes_usuarios(sorted(list(ids)))

        # Preencher tabela somente com diferenças por forma
        tot_dif_e = 0.0
        tot_dif_s = 0.0
        inserted = 0
        formas = ['dinheiro', 'cartao_credito', 'cartao_debito', 'pix', 'outro']
        def _f(v):
            try:
                return float(v or 0.0)
            except Exception:
                return 0.0
        def brl(x):
            return f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        for r in rows:
            # Datas sessão
            s_id = r.get('sessao_id')
            ab = r.get('abertura_datahora')
            fe = r.get('fechamento_datahora')
            try:
                ab_txt = ab.strftime('%d/%m/%Y %H:%M') if hasattr(ab, 'strftime') else str(ab)
                fe_txt = fe.strftime('%d/%m/%Y %H:%M') if fe and hasattr(fe, 'strftime') else (str(fe) if fe else '-')
            except Exception:
                ab_txt, fe_txt = str(ab), (str(fe) if fe else '-')
            # Usuário responsável: prioriza ABERTURA; se vazio, usa FECHAMENTO
            uid = r.get('abertura_usuario_id')
            if uid is None:
                uid = r.get('fechamento_usuario_id')
            try:
                uid_int = int(uid) if uid is not None else None
            except Exception:
                uid_int = None
            u_nome = f"Usuário {uid}"  # fallback textual com ID
            if uid_int is not None:
                u_nome = nomes.get(uid_int) or f"Usuário {uid_int}"
            obs = r.get('observacao') or ''

            # Entradas por forma
            for fkey in formas:
                esp = _f(r.get(f'esp_entr_{fkey}'))
                cont = _f(r.get(f'cont_entr_{fkey}'))
                dif = cont - esp
                if abs(dif) > 1e-6:
                    tot_dif_e += dif
                    tree.insert('', 'end', values=(
                        s_id, ab_txt, fe_txt, u_nome, 'entrada', fkey.replace('_', ' ').title(),
                        brl(esp), brl(cont), brl(dif), obs
                    ))
                    inserted += 1
            # Saídas por forma
            for fkey in formas:
                esp = _f(r.get(f'esp_sai_{fkey}'))
                cont = _f(r.get(f'cont_sai_{fkey}'))
                dif = cont - esp
                if abs(dif) > 1e-6:
                    tot_dif_s += dif
                    tree.insert('', 'end', values=(
                        s_id, ab_txt, fe_txt, u_nome, 'saída', fkey.replace('_', ' ').title(),
                        brl(esp), brl(cont), brl(dif), obs
                    ))
                    inserted += 1

        if inserted == 0:
            # Sem diferenças: mostra linha única indicando OK
            tree.insert('', 'end', values=(
                '-', '-', '-', '-', '-', '-', 'R$ 0,00', 'R$ 0,00', 'R$ 0,00', 'OK: sem diferenças no período/filtros.'
            ))

        lbl_tot_e.config(text=f"Σ Dif. Entradas: R$ {tot_dif_e:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        lbl_tot_s.config(text=f"Σ Dif. Saídas: R$ {tot_dif_s:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    # ----------------- Relatório Financeiro (Entradas/Saídas) -----------------
    def _abrir_relatorio_financeiro(self):
        bg_base = CORES.get("fundo", "#f0f2f5")
        dlg = tk.Toplevel(self.frame)
        dlg.title("Relatório financeiro")
        dlg.configure(bg=bg_base)
        dlg.transient(self.frame.winfo_toplevel())
        dlg.grab_set()

        # Header
        tk.Label(
            dlg, text="Relatório financeiro (Entradas e Saídas)",
            font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000')
        ).pack(padx=16, pady=(16, 8), anchor='w')

        # Filtros de período
        filtros = tk.Frame(dlg, bg=bg_base)
        filtros.pack(fill='x', padx=16)

        tk.Label(filtros, text="Início (dd/mm/aaaa):", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0,6))
        ent_ini = tk.Entry(filtros, width=12)
        ent_ini.pack(side='left', padx=(0,14))

        tk.Label(filtros, text="Fim (dd/mm/aaaa):", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0,6))
        ent_fim = tk.Entry(filtros, width=12)
        ent_fim.pack(side='left', padx=(0,14))

        # Sugere mês atual
        hoje = date.today()
        mes_ini = hoje.replace(day=1)
        ent_ini.insert(0, mes_ini.strftime('%d/%m/%Y'))
        ent_fim.insert(0, hoje.strftime('%d/%m/%Y'))

        btn_filtrar = tk.Button(
            filtros, text="Filtrar", command=lambda: self._carregar_financeiro_periodo(
                dlg, tree, lbl_tot_entradas, lbl_tot_saidas, ent_ini.get(), ent_fim.get()
            ),
            font=('Arial', 10, 'bold'), bg='#4a6fa5', fg='white', bd=0, padx=16, pady=4, relief='flat', cursor='hand2'
        )
        btn_filtrar.pack(side='left')

        # Tabela
        tabela_wrap = tk.Frame(dlg, bg=bg_base)
        tabela_wrap.pack(fill='both', expand=True, padx=16, pady=(10, 0))

        style = ttk.Style()
        try:
            style.configure("RF.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("RF.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass

        cols = ('data', 'descricao', 'tipo', 'forma', 'valor')
        tree = ttk.Treeview(tabela_wrap, columns=cols, show='headings', height=16, style='RF.Treeview')
        tree.pack(fill='both', expand=True)

        headers = {
            'data': 'Data/Hora',
            'descricao': 'Descrição',
            'tipo': 'Tipo',
            'forma': 'Forma',
            'valor': 'Valor (R$)'
        }
        widths = {'data': 160, 'descricao': 320, 'tipo': 100, 'forma': 140, 'valor': 120}
        for c in cols:
            tree.heading(c, text=headers[c])
            tree.column(c, width=widths[c], anchor='w')

        # Tag de cor somente para saídas (entradas permanecem com fundo branco)
        tree.tag_configure('saida', background='#ffebee')    # vermelho claro

        # Totais
        totals = tk.Frame(dlg, bg=bg_base)
        totals.pack(fill='x', padx=16, pady=(8, 16))
        lbl_tot_entradas = tk.Label(totals, text="Total Entradas: R$ 0,00", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_tot_saidas = tk.Label(totals, text="Total Saídas: R$ 0,00", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_tot_entradas.pack(side='left')
        lbl_tot_saidas.pack(side='left', padx=(20,0))

        # Primeira carga
        self._carregar_financeiro_periodo(dlg, tree, lbl_tot_entradas, lbl_tot_saidas, ent_ini.get(), ent_fim.get())

        # Tenta centralizar
        try:
            dlg.update_idletasks()
            w = 900
            h = 520
            sw = dlg.winfo_screenwidth()
            sh = dlg.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _parse_date_br(self, s: str) -> date | None:
        s = (s or '').strip()
        if not s:
            return None
        try:
            return datetime.strptime(s, '%d/%m/%Y').date()
        except Exception:
            return None

    def _carregar_financeiro_periodo(self, win: tk.Toplevel, tree: ttk.Treeview,
                                     lbl_tot_e: tk.Label, lbl_tot_s: tk.Label,
                                     dt_ini_str: str, dt_fim_str: str):
        dt_ini = self._parse_date_br(dt_ini_str)
        dt_fim = self._parse_date_br(dt_fim_str)
        if not dt_ini or not dt_fim:
            messagebox.showwarning("Período", "Informe datas válidas no formato dd/mm/aaaa.")
            return
        if dt_ini > dt_fim:
            messagebox.showwarning("Período", "Data inicial não pode ser maior que a final.")
            return

        # Limpa tabela
        for iid in tree.get_children():
            tree.delete(iid)

        # Conexão DB
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Relatório", "Sem conexão com o banco de dados.")
            return

        # Busca no banco: tabela 'financeiro' somente entradas/saídas por período
        inicio = datetime.combine(dt_ini, datetime.min.time())
        fim = datetime.combine(dt_fim, datetime.max.time())

        cursor = db_conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, data, descricao, tipo, tipo_pagamento, valor
                FROM financeiro
                WHERE data BETWEEN %s AND %s
                  AND tipo IN ('entrada','saida')
                ORDER BY data ASC, id ASC
                """,
                (inicio, fim)
            )
            rows = cursor.fetchall() or []
        except Exception as e:
            messagebox.showerror("Relatório", f"Falha ao consultar: {e}")
            try:
                cursor.close()
            except Exception:
                pass
            return
        finally:
            try:
                cursor.close()
            except Exception:
                pass

        total_e = 0.0
        total_s = 0.0
        for r in rows:
            dt_txt = ''
            try:
                d = r.get('data')
                if hasattr(d, 'strftime'):
                    dt_txt = d.strftime('%d/%m/%Y %H:%M')
                else:
                    dt_txt = str(d)
            except Exception:
                dt_txt = ''
            tipo = (r.get('tipo') or '').strip().lower()
            forma = r.get('tipo_pagamento') or '-'
            valor = float(r.get('valor') or 0.0)
            desc = r.get('descricao') or ''
            # Acumula totais
            if tipo == 'entrada':
                total_e += valor
            elif tipo == 'saida':
                total_s += valor
            # Entradas: sem tag (fundo branco). Saídas: tag 'saida' (fundo vermelho claro)
            row_tags = ('saida',) if tipo == 'saida' else ()
            tree.insert('', 'end', values=(dt_txt, desc, tipo, forma, f"{valor:,.2f}"), tags=row_tags)

        lbl_tot_e.config(text=f"Total Entradas: R$ {total_e:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        lbl_tot_s.config(text=f"Total Saídas: R$ {total_s:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

    # ----------------- Relatórios Médicos (por período e médico) --------------
    def _abrir_relatorio_medicos(self):
        bg_base = CORES.get("fundo", "#f0f2f5")
        dlg = tk.Toplevel(self.frame)
        dlg.title("Relatórios médicos")
        dlg.configure(bg=bg_base)
        dlg.transient(self.frame.winfo_toplevel())
        dlg.grab_set()

        tk.Label(
            dlg, text="Relatórios médicos (período e médico)",
            font=("Arial", 12, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000')
        ).pack(padx=16, pady=(16, 8), anchor='w')

        # Filtros
        filtros = tk.Frame(dlg, bg=bg_base)
        filtros.pack(fill='x', padx=16)

        tk.Label(filtros, text="Início (dd/mm/aaaa):", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0,6))
        ent_ini = tk.Entry(filtros, width=12)
        ent_ini.pack(side='left', padx=(0,14))

        tk.Label(filtros, text="Fim (dd/mm/aaaa):", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0,6))
        ent_fim = tk.Entry(filtros, width=12)
        ent_fim.pack(side='left', padx=(0,14))

        # Sugestão mês atual
        hoje = date.today()
        mes_ini = hoje.replace(day=1)
        ent_ini.insert(0, mes_ini.strftime('%d/%m/%Y'))
        ent_fim.insert(0, hoje.strftime('%d/%m/%Y'))

        tk.Label(filtros, text="Médico:", bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(10,6))
        cmb_medico = ttk.Combobox(filtros, width=40, state='readonly')
        cmb_medico.pack(side='left', padx=(0,14))

        btn_filtrar = tk.Button(
            filtros, text="Filtrar", font=('Arial', 10, 'bold'),
            bg='#4a6fa5', fg='white', bd=0, padx=16, pady=4, relief='flat', cursor='hand2'
        )
        btn_filtrar.pack(side='left')

        # Tabela
        tabela_wrap = tk.Frame(dlg, bg=bg_base)
        tabela_wrap.pack(fill='both', expand=True, padx=16, pady=(10, 0))

        style = ttk.Style()
        try:
            style.configure("RM.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("RM.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass

        cols = ('data', 'descricao', 'forma', 'valor')
        tree = ttk.Treeview(tabela_wrap, columns=cols, show='headings', height=16, style='RM.Treeview')
        tree.pack(fill='both', expand=True)

        headers = {
            'data': 'Data/Hora',
            'descricao': 'Descrição',
            'forma': 'Forma',
            'valor': 'Valor (R$)'
        }
        widths = {'data': 160, 'descricao': 420, 'forma': 180, 'valor': 120}
        for c in cols:
            tree.heading(c, text=headers[c])
            tree.column(c, width=widths[c], anchor='w')

        # Total
        totals = tk.Frame(dlg, bg=bg_base)
        totals.pack(fill='x', padx=16, pady=(8, 16))
        lbl_total = tk.Label(totals, text="Total: R$ 0,00", font=('Arial', 10, 'bold'), bg=bg_base, fg=CORES.get('texto', '#000'))
        lbl_total.pack(side='left')

        # Carregar médicos e conectar ação do botão
        medicos = self._carregar_medicos()
        # Lista exibida como "Nome (ID)" para manter referência
        exib = [f"{m['nome']} ({m['id']})" for m in medicos]
        cmb_medico['values'] = exib
        if exib:
            cmb_medico.current(0)

        btn_filtrar.config(command=lambda: self._carregar_medicos_periodo(
            tree, lbl_total, ent_ini.get(), ent_fim.get(), medicos, cmb_medico.get()
        ))

        # Primeira tentativa de carga (se houver médico)
        if exib:
            self._carregar_medicos_periodo(tree, lbl_total, ent_ini.get(), ent_fim.get(), medicos, cmb_medico.get())

        # Centraliza
        try:
            dlg.update_idletasks()
            w = 900
            h = 520
            sw = dlg.winfo_screenwidth()
            sh = dlg.winfo_screenheight()
            x = (sw - w) // 2
            y = (sh - h) // 2
            dlg.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _carregar_medicos(self):
        """Tenta carregar lista de médicos do banco.
        Espera tabela 'medicos' com colunas (id, nome). Se não houver, tenta 'pessoas' com tipo 'MEDICO'.
        Retorna lista de dicts: {'id': id, 'nome': nome}
        """
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            return []
        cursor = db_conn.cursor()
        try:
            try:
                cursor.execute("SELECT id, nome FROM medicos ORDER BY nome ASC")
                rows = cursor.fetchall() or []
                return [{'id': r[0], 'nome': r[1]} for r in rows]
            except Exception:
                # fallback possível
                try:
                    cursor.execute("SELECT id, nome FROM pessoas WHERE tipo = 'MEDICO' ORDER BY nome ASC")
                    rows = cursor.fetchall() or []
                    return [{'id': r[0], 'nome': r[1]} for r in rows]
                except Exception:
                    return []
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def _carregar_medicos_periodo(self, tree: ttk.Treeview, lbl_total: tk.Label,
                                  dt_ini_str: str, dt_fim_str: str,
                                  medicos: list, medico_exibicao: str):
        dt_ini = self._parse_date_br(dt_ini_str)
        dt_fim = self._parse_date_br(dt_fim_str)
        if not dt_ini or not dt_fim:
            messagebox.showwarning("Período", "Informe datas válidas no formato dd/mm/aaaa.")
            return
        if dt_ini > dt_fim:
            messagebox.showwarning("Período", "Data inicial não pode ser maior que a final.")
            return

        # Resolve médico selecionado
        medico_id = None
        if medico_exibicao:
            # pega o conteúdo dentro de parênteses
            if '(' in medico_exibicao and medico_exibicao.endswith(')'):
                try:
                    medico_id = int(medico_exibicao.split('(')[-1][:-1])
                except Exception:
                    medico_id = None
        if not medico_id:
            messagebox.showwarning("Médico", "Selecione um médico válido.")
            return

        # Limpar tabela
        for iid in tree.get_children():
            tree.delete(iid)

        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Relatório", "Sem conexão com o banco de dados.")
            return

        inicio = datetime.combine(dt_ini, datetime.min.time())
        fim = datetime.combine(dt_fim, datetime.max.time())

        total = 0.0
        cursor = db_conn.cursor(dictionary=True)
        try:
            # Tenta um cenário comum: coluna medico_id dentro de financeiro para entradas de consultas/exames
            cursor.execute(
                """
                SELECT f.data, COALESCE(c.tipo_atendimento, f.descricao) AS descricao, f.tipo_pagamento, f.valor
                FROM financeiro f
                LEFT JOIN consultas c ON c.id = f.consulta_id
                WHERE f.tipo = 'entrada'
                  AND c.medico_id = %s
                  AND f.data BETWEEN %s AND %s
                ORDER BY f.data ASC
                """,
                (medico_id, inicio, fim)
            )
            rows = cursor.fetchall() or []
        except Exception as e1:
            # Caso a coluna não exista, informa o usuário e não quebra a app
            try:
                cursor.close()
            except Exception:
                pass
            messagebox.showinfo(
                "Relatórios médicos",
                "Não encontrei a coluna medico_id na tabela financeiro.\n"
                "Posso ajustar a consulta quando você me indicar onde fica a relação entre pagamento e médico (ex.: tabela de consultas/exames)."
            )
            return
        finally:
            try:
                cursor.close()
            except Exception:
                pass

        for r in rows:
            d = r.get('data')
            if hasattr(d, 'strftime'):
                dt_txt = d.strftime('%d/%m/%Y %H:%M')
            else:
                dt_txt = str(d)
            desc = r.get('descricao') or ''
            forma = r.get('tipo_pagamento') or '-'
            valor = float(r.get('valor') or 0.0)
            total += valor
            tree.insert('', 'end', values=(dt_txt, desc, forma, f"{valor:,.2f}"))

        lbl_total.config(text=f"Total: R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
