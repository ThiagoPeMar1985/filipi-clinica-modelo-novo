import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from src.controllers.financeiro_controller import FinanceiroController

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
            {"nome": "Relatórios", "acao": "relatorios"}
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
        else:
            self._show_default()
            
        self.frame.pack(fill='both', expand=True)
        return self.frame
    
    def _show_default(self):
        # Tela inicial do módulo financeiro
        label = ttk.Label(
            self.frame, 
            text="Selecione uma opção financeira no menu lateral", 
            font=('Arial', 12)
        )
        label.pack(pady=20)
    
    def _show_caixa(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Caixa", font=('Arial', 14, 'bold')).pack(pady=10, anchor='w')

        # Área de status e ações
        status_bar = ttk.Frame(frame)
        status_bar.pack(fill='x', padx=5, pady=(0, 10))

        self.lbl_status = ttk.Label(status_bar, text="Status: verificando...", font=('Arial', 10))
        self.lbl_status.pack(side='left')

        self.btn_abrir = ttk.Button(status_bar, text="Abrir Caixa", command=self._on_abrir_caixa)
        self.btn_abrir.pack(side='right', padx=5)

        # Área de lançamentos
        lanc_frame = ttk.LabelFrame(frame, text="Lançamentos")
        lanc_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(lanc_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.tipo_var = tk.StringVar(value='recebimento')
        self.cmb_tipo = ttk.Combobox(lanc_frame, textvariable=self.tipo_var, values=['recebimento', 'pagamento'], state='readonly', width=14)
        self.cmb_tipo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(lanc_frame, text="Forma:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.forma_var = tk.StringVar(value='dinheiro')
        self.cmb_forma = ttk.Combobox(lanc_frame, textvariable=self.forma_var, values=['dinheiro', 'cartao', 'pix', 'outro'], state='readonly', width=14)
        self.cmb_forma.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(lanc_frame, text="Valor:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.valor_var = tk.StringVar()
        self.ent_valor = ttk.Entry(lanc_frame, textvariable=self.valor_var, width=12)
        self.ent_valor.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        ttk.Label(lanc_frame, text="Descrição:").grid(row=0, column=6, padx=5, pady=5, sticky='w')
        self.desc_var = tk.StringVar()
        self.ent_desc = ttk.Entry(lanc_frame, textvariable=self.desc_var, width=30)
        self.ent_desc.grid(row=0, column=7, padx=5, pady=5, sticky='w')

        self.btn_lancar = ttk.Button(lanc_frame, text="Lançar", command=self._on_lancar)
        self.btn_lancar.grid(row=0, column=8, padx=5, pady=5, sticky='w')

        for i in range(9):
            lanc_frame.grid_columnconfigure(i, weight=0)

        # Lista de movimentos
        list_frame = ttk.LabelFrame(frame, text="Movimentos do Caixa")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        cols = ("data_hora", "tipo", "forma", "descricao", "valor")
        self.mov_tree = ttk.Treeview(list_frame, columns=cols, show='headings', height=12)
        self.mov_tree.heading("data_hora", text="Data/Hora")
        self.mov_tree.heading("tipo", text="Tipo")
        self.mov_tree.heading("forma", text="Forma")
        self.mov_tree.heading("descricao", text="Descrição")
        self.mov_tree.heading("valor", text="Valor (R$)")
        self.mov_tree.column("data_hora", width=140)
        self.mov_tree.column("tipo", width=110)
        self.mov_tree.column("forma", width=110)
        self.mov_tree.column("descricao", width=300)
        self.mov_tree.column("valor", width=100, anchor='e')
        self.mov_tree.pack(fill='both', expand=True, side='left')

        scb = ttk.Scrollbar(list_frame, orient='vertical', command=self.mov_tree.yview)
        self.mov_tree.configure(yscroll=scb.set)
        scb.pack(side='right', fill='y')

        # Resumo e fechar
        bottom = ttk.Frame(frame)
        bottom.pack(fill='x', padx=5, pady=10)

        self.lbl_resumo = ttk.Label(bottom, text="")
        self.lbl_resumo.pack(side='left')

        self.btn_fechar = ttk.Button(bottom, text="Fechar Caixa", command=self._on_fechar_caixa)
        self.btn_fechar.pack(side='right')

        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame

        # Carrega estado atual
        self._refresh_caixa_state()

    # ----------------- Handlers e Helpers do Caixa -----------------
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
        return self.financeiro_controller

    def _refresh_caixa_state(self):
        fc = self._get_financeiro_controller()
        sessao = fc.get_sessao_aberta()
        aberto = bool(sessao)
        if aberto:
            self.lbl_status.config(text=f"Status: Caixa ABERTO (Sessão #{sessao['id']})")
            # habilita lançamentos e fechar
            for w in [self.cmb_tipo, self.cmb_forma, self.ent_valor, self.ent_desc, self.btn_lancar, self.btn_fechar]:
                w.state(['!disabled']) if hasattr(w, 'state') else w.config(state='normal')
            # Abrir desabilitado
            self.btn_abrir.config(state='disabled')
            # Carrega movimentos e resumo
            self._carregar_movimentos()
            self._atualizar_resumo()
        else:
            self.lbl_status.config(text="Status: Caixa FECHADO")
            # desabilita lançamentos e fechar
            for w in ['cmb_tipo','cmb_forma','ent_valor','ent_desc','btn_lancar','btn_fechar']:
                if hasattr(self, w):
                    obj = getattr(self, w)
                    try:
                        obj.state(['disabled'])
                    except Exception:
                        obj.config(state='disabled')
            self.btn_abrir.config(state='normal')
            # limpa lista e resumo
            if hasattr(self, 'mov_tree'):
                for i in self.mov_tree.get_children():
                    self.mov_tree.delete(i)
            if hasattr(self, 'lbl_resumo'):
                self.lbl_resumo.config(text="")

    def _on_abrir_caixa(self):
        try:
            valor = simpledialog.askfloat("Abrir Caixa", "Informe o valor no fundo de caixa (R$):", minvalue=0.0)
            if valor is None:
                return
            fc = self._get_financeiro_controller()
            sessao_id = fc.abrir_caixa(valor_inicial=valor, usuario_id=getattr(self.controller, 'usuario_id', None))
            if sessao_id:
                messagebox.showinfo("Caixa", f"Caixa aberto. Sessão #{sessao_id}")
            else:
                messagebox.showerror("Caixa", "Não foi possível abrir o caixa.")
            self._refresh_caixa_state()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao abrir caixa: {e}")

    def _on_lancar(self):
        try:
            valor_str = (self.valor_var.get() or '').replace(',', '.').strip()
            try:
                valor = float(valor_str)
            except Exception:
                messagebox.showwarning("Lançamento", "Informe um valor numérico válido.")
                return
            if valor <= 0:
                messagebox.showwarning("Lançamento", "O valor deve ser maior que zero.")
                return
            tipo = self.tipo_var.get()
            forma = self.forma_var.get()
            desc = self.desc_var.get().strip()
            fc = self._get_financeiro_controller()
            mid = fc.registrar_movimento(tipo=tipo, forma=forma, valor=valor, descricao=desc, usuario_id=getattr(self.controller, 'usuario_id', None))
            if mid:
                # limpa campos e atualiza lista
                self.valor_var.set("")
                self.desc_var.set("")
                self._carregar_movimentos()
                self._atualizar_resumo()
            else:
                messagebox.showerror("Lançamento", "Falha ao registrar movimento. Certifique-se de que o caixa está aberto.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no lançamento: {e}")

    def _carregar_movimentos(self):
        fc = self._get_financeiro_controller()
        movimentos = fc.listar_movimentos() or []
        # limpa
        for i in self.mov_tree.get_children():
            self.mov_tree.delete(i)
        # adiciona
        for m in movimentos:
            data_txt = str(m.get('data_hora'))[:19]
            valor_txt = f"{float(m.get('valor', 0)):.2f}"
            self.mov_tree.insert('', 'end', values=(data_txt, m.get('tipo'), m.get('forma'), m.get('descricao') or '', valor_txt))

    def _atualizar_resumo(self):
        fc = self._get_financeiro_controller()
        resumo = fc.resumo_sessao()
        if not resumo:
            self.lbl_resumo.config(text="")
            return
        texto = (
            f"Fundo inicial: R$ {resumo['valor_inicial']:.2f}  |  "
            f"Entradas: R$ {resumo['total_entradas']:.2f}  |  "
            f"Saídas: R$ {resumo['total_saidas']:.2f}  |  "
            f"Saldo: R$ {resumo['saldo_final']:.2f}"
        )
        self.lbl_resumo.config(text=texto)

    def _on_fechar_caixa(self):
        if not messagebox.askyesno("Fechar Caixa", "Deseja fechar o caixa e gerar o relatório desta sessão?"):
            return
        try:
            fc = self._get_financeiro_controller()
            resumo = fc.fechar_caixa(usuario_id=getattr(self.controller, 'usuario_id', None))
            if not resumo:
                messagebox.showerror("Fechar Caixa", "Não há sessão aberta para fechar.")
                return
            relatorio = [
                f"Fundo inicial: R$ {resumo['valor_inicial']:.2f}",
                f"Total Entradas: R$ {resumo['total_entradas']:.2f}",
                f"Total Saídas: R$ {resumo['total_saidas']:.2f}",
                f"Saldo Final: R$ {resumo['saldo_final']:.2f}",
                "",
                "Entradas por forma:" 
            ]
            for forma, total in (resumo.get('entradas_por_forma') or {}).items():
                relatorio.append(f"  - {forma}: R$ {total:.2f}")
            relatorio.append("Saídas por forma:")
            for forma, total in (resumo.get('saidas_por_forma') or {}).items():
                relatorio.append(f"  - {forma}: R$ {total:.2f}")
            messagebox.showinfo("Relatório de Caixa", "\n".join(relatorio))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao fechar caixa: {e}")
        finally:
            self._refresh_caixa_state()
    
    def _show_contas_pagar(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Contas a Pagar", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o gerenciamento de contas a pagar aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_contas_receber(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Contas a Receber", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione o gerenciamento de contas a receber aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
    
    def _show_relatorios(self):
        frame = ttk.Frame(self.frame)
        ttk.Label(frame, text="Relatórios Financeiros", font=('Arial', 14, 'bold')).pack(pady=10)
        # Adicione os relatórios financeiros aqui
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        self.current_view = frame
