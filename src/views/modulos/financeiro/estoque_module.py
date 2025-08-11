import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.config.estilos import CORES, FONTES
from src.controllers.estoque_controller import EstoqueController

class EstoqueModule:
    """
    Tela de Estoque (baseada em ContasPagarModule), com os botões básicos:
    - Adicionar Estoque
    - Editar Produto
    - Excluir

    Listagem inicial com colunas padrão para produtos. Integração com DB será
    adicionada depois (stubs preparados).
    """
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller

        bg_base = CORES.get("fundo", "#f0f2f5")
        self.frame = tk.Frame(parent, bg=bg_base)

        # Título
        tk.Label(
            self.frame,
            text="Estoque",
            font=FONTES.get("subtitulo", ("Arial", 16, "bold")),
            bg=bg_base,
            fg=CORES.get("texto", "#000"),
        ).pack(pady=(10, 5), anchor='w')

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
        tk.Button(left_col, text="Adicionar Estoque", command=self._abrir_adicionar, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Editar Produto", command=self._abrir_editar, **btn_style).pack(fill='x', pady=4)
        btn_excluir_style = dict(btn_style); btn_excluir_style['bg'] = CORES.get('alerta', '#f44336')
        tk.Button(left_col, text="Excluir", command=self._excluir_selecionado, **btn_excluir_style).pack(fill='x', pady=4)

        # Área direita (filtros + lista)
        right = tk.Frame(body, bg=bg_base)
        right.pack(side='left', fill='both', expand=True, padx=(10, 10), pady=(5, 10))

        filtros = tk.Frame(right, bg=bg_base)
        filtros.pack(fill='x')

        tk.Label(filtros, text="Pesquisar:", font=('Arial', 10), bg=bg_base, fg=CORES.get('texto', '#000')).pack(side='left', padx=(0, 5))
        self.ed_busca = tk.Entry(filtros, font=('Arial', 10))
        self.ed_busca.pack(side='left', padx=(0, 10))

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
            style.configure("EST.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("EST.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass

        cols = ('id', 'nome', 'qtd_atual', 'qtd_minima', 'valor_ultima_compra', 'atualizado_em')
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=16, style='EST.Treeview')
        self.tree.pack(fill='both', expand=True, pady=(10, 0))

        headers = {
            'id': 'ID',
            'nome': 'Produto',
            'qtd_atual': 'Quantidade',
            'qtd_minima': 'Qtd Mínima',
            'valor_ultima_compra': 'Custo (R$)',
            'atualizado_em': 'Atualizado em',
        }
        widths = {
            'id': 0,
            'nome': 240,
            'qtd_atual': 100,
            'qtd_minima': 110,
            'valor_ultima_compra': 120,
            'atualizado_em': 160,
        }
        for c in cols:
            self.tree.heading(c, text=headers[c])
            if c == 'id':
                self.tree.column(c, width=0, minwidth=0, stretch=False)
            else:
                self.tree.column(c, width=widths[c], anchor='w')

        # Carregamento inicial (dados reais)
        self._carregar_lista()

    # ---------- Helpers ----------
    def _ctrl(self) -> EstoqueController | None:
        ec = getattr(self, '_estoque_controller', None)
        if ec is not None:
            return ec
        db_conn = getattr(self.controller, 'db_connection', None)
        if not db_conn:
            messagebox.showerror("Estoque", "Sem conexão com o banco de dados.")
            return None
        ec = EstoqueController(db_conn)
        setattr(self, '_estoque_controller', ec)
        return ec

    # ---------- Actions / DB ----------
    def _carregar_lista(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        ec = self._ctrl()
        if not ec:
            return
        rows = ec.listar()
        for r in rows:
            att = r.get('atualizado_em')
            att_txt = att.strftime('%d/%m/%Y %H:%M') if att and hasattr(att, 'strftime') else (str(att) if att else '-')
            val = r.get('valor_ultima_compra')
            val_txt = (f"{float(val):.2f}" if val is not None else '-')
            self.tree.insert('', 'end', values=(
                r.get('id') or '-',
                r.get('nome') or '-',
                int(r.get('qtd_atual') or 0),
                int(r.get('qtd_minima') or 0),
                val_txt,
                att_txt,
            ))

    def _aplicar_filtro(self):
        # TODO: aplicar filtro real
        termo = (self.ed_busca.get() or '').strip()
        if not termo:
            self._carregar_lista()
            return
        # Filtro simples em memória (nome contém termo)
        for i in self.tree.get_children():
            self.tree.delete(i)
        ec = self._ctrl()
        if not ec:
            return
        termo_low = termo.lower()
        for r in ec.listar():
            if termo_low in str(r.get('nome') or '').lower():
                att = r.get('atualizado_em')
                att_txt = att.strftime('%d/%m/%Y %H:%M') if att and hasattr(att, 'strftime') else (str(att) if att else '-')
                val = r.get('valor_ultima_compra')
                val_txt = (f"{float(val):.2f}" if val is not None else '-')
                self.tree.insert('', 'end', values=(
                    r.get('id') or '-',
                    r.get('nome') or '-',
                    int(r.get('qtd_atual') or 0),
                    int(r.get('qtd_minima') or 0),
                    val_txt,
                    att_txt,
                ))

    def _abrir_adicionar(self):
        win = tk.Toplevel(self.frame)
        win.title("Adicionar Estoque")
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

        ed_nome = tk.Entry(body, font=('Arial', 10))
        add("Produto:", ed_nome)

        ed_qtd = tk.Entry(body, font=('Arial', 10))
        ed_qtd.insert(0, '1')
        add("Quantidade:", ed_qtd)

        ed_valor = tk.Entry(body, font=('Arial', 10))
        add("Custo (R$):", ed_valor)

        ed_data = tk.Entry(body, font=('Arial', 10))
        ed_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        add("Data da compra (dd/mm/aaaa):", ed_data)

        ed_min = tk.Entry(body, font=('Arial', 10))
        ed_min.insert(0, '0')
        add("Qtd mínima:", ed_min)

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
        tk.Button(btn_bar, text="Salvar", command=lambda: self._salvar_adicao(win, ed_nome.get(), ed_qtd.get(), ed_valor.get(), ed_data.get(), ed_min.get()), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))
        # Centraliza a janela no centro da tela
        try:
            win.update_idletasks()
            top = win.winfo_toplevel()
            top.update_idletasks()
            sw = top.winfo_screenwidth()
            sh = top.winfo_screenheight()
            w = win.winfo_width() or 520
            h = win.winfo_height() or 360
            x = (sw - w) // 2
            y = (sh - h) // 2
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _salvar_adicao(self, win, nome, qtd, val_str, data_str, qtd_min_str):
        nome = (nome or '').strip()
        if not nome:
            messagebox.showwarning("Adicionar Estoque", "Informe o nome do produto.")
            return
        try:
            qtd_i = int((qtd or '0').strip())
            if qtd_i <= 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Adicionar Estoque", "Quantidade inválida (inteiro > 0).")
            return
        valor = None
        vs = (val_str or '').strip().replace(',', '.')
        if vs:
            try:
                valor = float(vs)
            except Exception:
                messagebox.showwarning("Adicionar Estoque", "Custo inválido.")
                return
        data_compra = None
        ds = (data_str or '').strip()
        if ds:
            try:
                data_compra = datetime.strptime(ds, '%d/%m/%Y').date()
            except Exception:
                messagebox.showwarning("Adicionar Estoque", "Data inválida (use dd/mm/aaaa).")
                return
        qtd_min = 0
        try:
            qtd_min = int((qtd_min_str or '0').strip());
            if qtd_min < 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Adicionar Estoque", "Qtd mínima inválida (inteiro >= 0).")
            return
        ec = self._ctrl()
        if not ec:
            return
        try:
            ec.adicionar(nome=nome, quantidade=qtd_i, valor=valor, forma_pagamento=None, data_compra=data_compra, qtd_minima=qtd_min)
        except Exception as e:
            messagebox.showerror("Adicionar Estoque", f"Falha ao salvar: {e}")
            return
        try:
            win.destroy()
        except Exception:
            pass
        self._carregar_lista()

    def _get_selec(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0]).get('values') or []
        if not vals:
            return None
        return {
            'id': vals[0],
            'nome': vals[1],
            'qtd_atual': vals[2],
            'qtd_minima': vals[3],
            'valor_ultima_compra': None if vals[4] in ('-', '') else float(str(vals[4]).replace(',', '.')),
            'atualizado_em': vals[5],
        }

    def _abrir_editar(self):
        dados = self._get_selec()
        if not dados:
            messagebox.showinfo('Estoque', 'Selecione um item para editar.')
            return
        win = tk.Toplevel(self.frame)
        win.title("Editar Produto do Estoque")
        win.transient(self.frame.winfo_toplevel())
        win.grab_set(); win.resizable(False, False)

        body = tk.Frame(win); body.pack(padx=16, pady=16, fill='both', expand=True)
        body.grid_columnconfigure(0, weight=0); body.grid_columnconfigure(1, weight=1)
        row = 0
        def add(label, widget):
            nonlocal row
            tk.Label(body, text=label, font=('Arial', 10, 'bold'), anchor='w').grid(row=row, column=0, sticky='w', padx=(0,8), pady=4)
            widget.grid(row=row, column=1, sticky='we', pady=4)
            row += 1
        tk.Label(body, text=f"ID: {dados['id']}", font=('Arial', 10)).grid(row=row, column=0, columnspan=2, sticky='w', pady=(0,6)); row += 1
        ed_nome = tk.Entry(body, font=('Arial', 10)); ed_nome.insert(0, str(dados['nome'] or '')); add('Produto:', ed_nome)
        ed_qtd = tk.Entry(body, font=('Arial', 10)); ed_qtd.insert(0, str(dados['qtd_atual'] or 0)); add('Quantidade:', ed_qtd)
        ed_min = tk.Entry(body, font=('Arial', 10)); ed_min.insert(0, str(dados['qtd_minima'] or 0)); add('Qtd mínima:', ed_min)
        ed_val = tk.Entry(body, font=('Arial', 10)); ed_val.insert(0, '-' if dados['valor_ultima_compra'] is None else f"{dados['valor_ultima_compra']:.2f}"); add('Custo (R$):', ed_val)
        ed_data = tk.Entry(body, font=('Arial', 10)); ed_data.insert(0, ''); add('Data da compra (dd/mm/aaaa):', ed_data)

        btn_bar = tk.Frame(win); btn_bar.pack(fill='x', padx=16, pady=(0, 14))
        dialog_btn_style = {
            'font': ('Arial', 10, 'bold'), 'bg': CORES.get('primaria', '#4a6fa5'), 'fg': CORES.get('texto_claro', '#ffffff'),
            'bd': 0, 'padx': 20, 'pady': 8, 'relief': 'flat', 'cursor': 'hand2', 'highlightthickness': 0,
        }
        tk.Button(btn_bar, text='Salvar', command=lambda: self._salvar_edicao(win, dados['id'], ed_nome.get(), ed_qtd.get(), ed_min.get(), ed_val.get(), ed_data.get()), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text='Cancelar', command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))

    def _salvar_edicao(self, win, produto_id, nome, qtd_atual, qtd_minima, val_str, data_str):
        try:
            qtd_i = int((qtd_atual or '0').strip()); min_i = int((qtd_minima or '0').strip())
        except Exception:
            messagebox.showwarning('Editar Estoque', 'Quantidade/Qtd mínima inválidas.'); return
        valor = None; vs = (val_str or '').strip().replace(',', '.')
        if vs and vs != '-':
            try: valor = float(vs)
            except Exception: messagebox.showwarning('Editar Estoque', 'Custo inválido.'); return
        data_compra = None; ds = (data_str or '').strip()
        if ds:
            try: data_compra = datetime.strptime(ds, '%d/%m/%Y').date()
            except Exception: messagebox.showwarning('Editar Estoque', 'Data inválida (dd/mm/aaaa).'); return
        ec = self._ctrl();
        if not ec: return
        try:
            ec.atualizar(int(produto_id), (nome or '').strip(), qtd_i, min_i, valor, None, data_compra)
        except Exception as e:
            messagebox.showerror('Editar Estoque', f'Falha ao salvar: {e}'); return
        try: win.destroy()
        except Exception: pass
        self._carregar_lista()

    def _excluir_selecionado(self):
        dados = self._get_selec()
        if not dados:
            messagebox.showinfo('Estoque', 'Selecione um item para excluir.'); return
        if not messagebox.askyesno('Excluir', f"Confirma excluir o produto '{dados['nome']}' (ID {dados['id']})?"):
            return
        ec = self._ctrl();
        if not ec: return
        try:
            ec.excluir(int(dados['id']))
        except Exception as e:
            messagebox.showerror('Excluir', f'Falha ao excluir: {e}'); return
        self._carregar_lista()
