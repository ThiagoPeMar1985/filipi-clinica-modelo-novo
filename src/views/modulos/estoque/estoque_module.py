import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.config.estilos import CORES, FONTES
from src.controllers.estoque_controller import EstoqueController


class EstoqueModule:
    """Tela de Estoque com listagem e ação de Adicionar Estoque."""

    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        bg_base = CORES.get("fundo", "#f0f2f5")
        self.frame = tk.Frame(parent, bg=bg_base)

        tk.Label(
            self.frame,
            text="Estoque",
            font=FONTES.get("subtitulo", ("Arial", 16, "bold")),
            bg=bg_base,
            fg=CORES.get("texto", "#000")
        ).pack(pady=(10, 5), anchor='w')

        body = tk.Frame(self.frame, bg=bg_base)
        body.pack(fill='both', expand=True)

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
        tk.Button(left_col, text="Editar", command=self._abrir_editar, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Excluir", command=self._excluir_selecionado, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Recarregar", command=self._recarregar, **btn_style).pack(fill='x', pady=4)
        tk.Button(left_col, text="Definir Qtd. Mínima", command=self._abrir_definir_min, **btn_style).pack(fill='x', pady=4)
        
        right = tk.Frame(body, bg=bg_base)
        right.pack(side='left', fill='both', expand=True, padx=(10, 10), pady=(5, 10))

        # Treeview
        style = ttk.Style()
        try:
            style.configure("EST.Treeview", background='white', fieldbackground='white', foreground=CORES.get('texto', '#000'))
            style.configure("EST.Treeview.Heading", font=FONTES.get('tabela_cabecalho', ('Arial', 10, 'bold')))
        except Exception:
            pass
        cols = ("id", "nome", "qtd_atual", "qtd_minima", "valor_ultima_compra", "atualizado_em")
        self.tree = ttk.Treeview(right, columns=cols, show='headings', height=16, style='EST.Treeview')
        self.tree.pack(fill='both', expand=True, pady=(10, 0))

        headers = {
            'id': 'ID',
            'nome': 'Produto',
            'qtd_atual': 'Quantidade',
            'qtd_minima': 'Qtd Mínima',
            'valor_ultima_compra': 'Custo',
            'atualizado_em': 'Atualizado em',
        }
        widths = {
            'id': 0,
            'nome': 280,
            'qtd_atual': 110,
            'qtd_minima': 110,
            'valor_ultima_compra': 120,
            'atualizado_em': 160,
        }
        for c in cols:
            self.tree.heading(c, text=headers[c])
            # ID oculto
            if c == 'id':
                self.tree.column(c, width=0, minwidth=0, stretch=False)
            else:
                self.tree.column(c, width=widths[c], anchor='w')

        # Carrega listagem e checa estoque baixo
        self._carregar_lista()
        self._alertar_estoque_baixo()

    def _get_selec(self):
        sel = self.tree.selection()
        if not sel:
            return None
        item = self.tree.item(sel[0])
        vals = item.get('values') or []
        if not vals:
            return None
        # values: [id, nome, qtd_atual, qtd_minima, valor, atualizado_em]
        return {
            'id': vals[0],
            'nome': vals[1],
            'qtd_atual': vals[2],
            'qtd_minima': vals[3],
            'valor_ultima_compra': None if vals[4] in ('-', '') else float(str(vals[4]).replace(',', '.')),
            'atualizado_em': vals[5],
        }

    def _recarregar(self):
        self._carregar_lista()
        # não alertar sempre ao recarregar para não incomodar

    # ------- Controller helper -------
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

    def _carregar_lista(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        ec = self._ctrl()
        if not ec:
            return
        rows = ec.listar()
        for r in rows:
            atualizado = r.get('atualizado_em')
            att_txt = atualizado.strftime('%d/%m/%Y %H:%M') if atualizado and hasattr(atualizado, 'strftime') else (str(atualizado) if atualizado else '-')
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

    def _alertar_estoque_baixo(self):
        ec = self._ctrl()
        if not ec:
            return
        baixos = ec.baixo() or []
        if baixos:
            nomes = ", ".join([str(x.get('nome')) for x in baixos])
            messagebox.showwarning("Estoque baixo", f"Produtos com estoque baixo: {nomes}")

    # ------- Actions -------
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

        self._ed_nome = tk.Entry(body, font=('Arial', 10))
        add("Produto:", self._ed_nome)

        self._ed_qtd = tk.Entry(body, font=('Arial', 10))
        self._ed_qtd.insert(0, '1')
        add("Quantidade:", self._ed_qtd)

        self._ed_valor = tk.Entry(body, font=('Arial', 10))
        add("Valor (R$):", self._ed_valor)

        self._cmb_forma = ttk.Combobox(body, values=['dinheiro','pix','cartao_credito','cartao_debito','outro'])
        self._cmb_forma.current(0)
        add("Forma de pagamento:", self._cmb_forma)

        self._ed_data = tk.Entry(body, font=('Arial', 10))
        self._ed_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        add("Data da compra (dd/mm/aaaa):", self._ed_data)

        self._ed_min = tk.Entry(body, font=('Arial', 10))
        self._ed_min.insert(0, '0')
        add("Qtd mínima:", self._ed_min)

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
        tk.Button(btn_bar, text="Salvar", command=lambda: self._salvar_adicao(win), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))

        try:
            top = win.winfo_toplevel(); top.update_idletasks()
            sw = top.winfo_screenwidth(); sh = top.winfo_screenheight()
            w = 520; h = 340
            x = (sw - w) // 2; y = (sh - h) // 2
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _salvar_adicao(self, win: tk.Toplevel):
        nome = (self._ed_nome.get() or '').strip()
        if not nome:
            messagebox.showwarning("Adicionar Estoque", "Informe o nome do produto.")
            return
        try:
            qtd = int((self._ed_qtd.get() or '0').strip())
            if qtd <= 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Adicionar Estoque", "Quantidade inválida (use número inteiro > 0).")
            return
        valor = None
        val_str = (self._ed_valor.get() or '').strip().replace(',', '.')
        if val_str:
            try:
                valor = float(val_str)
            except Exception:
                messagebox.showwarning("Adicionar Estoque", "Valor inválido.")
                return
        forma = (self._cmb_forma.get() or '').strip() or None
        data_compra = None
        data_str = (self._ed_data.get() or '').strip()
        if data_str:
            try:
                data_compra = datetime.strptime(data_str, '%d/%m/%Y').date()
            except Exception:
                messagebox.showwarning("Adicionar Estoque", "Data inválida (use dd/mm/aaaa).")
                return
        try:
            qtd_min = int((self._ed_min.get() or '0').strip())
            if qtd_min < 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Adicionar Estoque", "Qtd mínima inválida (use número inteiro >= 0).")
            return

        ec = self._ctrl()
        if not ec:
            return
        try:
            ec.adicionar(nome=nome, quantidade=qtd, valor=valor, forma_pagamento=forma, data_compra=data_compra, qtd_minima=qtd_min)
        except Exception as e:
            messagebox.showerror("Adicionar Estoque", f"Falha ao salvar: {e}")
            return
        try:
            win.destroy()
        except Exception:
            pass
        self._carregar_lista()
        self._alertar_estoque_baixo()

    def _abrir_definir_min(self):
        win = tk.Toplevel(self.frame)
        win.title("Definir Quantidade Mínima")
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

        self._ed_nome2 = tk.Entry(body, font=('Arial', 10))
        add("Produto:", self._ed_nome2)

        self._ed_min2 = tk.Entry(body, font=('Arial', 10))
        self._ed_min2.insert(0, '0')
        add("Qtd mínima:", self._ed_min2)

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
        tk.Button(btn_bar, text="Salvar", command=lambda: self._salvar_min(win), **dialog_btn_style).pack(side='right')
        tk.Button(btn_bar, text="Cancelar", command=win.destroy, **dialog_btn_style).pack(side='right', padx=(0,8))

        try:
            top = win.winfo_toplevel(); top.update_idletasks()
            sw = top.winfo_screenwidth(); sh = top.winfo_screenheight()
            w = 520; h = 200
            x = (sw - w) // 2; y = (sh - h) // 2
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _salvar_min(self, win: tk.Toplevel):
        nome = (self._ed_nome2.get() or '').strip()
        if not nome:
            messagebox.showwarning("Qtd Mínima", "Informe o nome do produto.")
            return
        try:
            qtd_min = int((self._ed_min2.get() or '0').strip())
            if qtd_min < 0:
                raise ValueError()
        except Exception:
            messagebox.showwarning("Qtd Mínima", "Qtd mínima inválida (use número inteiro >= 0).")
            return
        ec = self._ctrl()
        if not ec:
            return
        try:
            ec.definir_minima(nome, qtd_min)
        except Exception as e:
            messagebox.showerror("Qtd Mínima", f"Falha ao salvar: {e}")
            return
        try:
            win.destroy()
        except Exception:
            pass
        self._carregar_lista()
        self._alertar_estoque_baixo()
