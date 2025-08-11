from __future__ import annotations
from datetime import datetime
from typing import List, Tuple, Dict, Any


class RelatoriosController:
    """Controller responsável por obter dados para relatórios financeiros.

    Centraliza o acesso ao banco (db_connection) e expõe métodos de consulta
    específicos para cada relatório, deixando o módulo de view apenas com UI.
    """

    def __init__(self, db_connection):
        self.db = db_connection

    def listar_contas(self, dt_ini: datetime, dt_fim: datetime, tipo: str, situacao: str) -> Tuple[List[Dict[str, Any]], int, float]:
        """Retorna as contas (pagar/receber) conforme período, tipo e situação.

        - tipo: 'Contas a Pagar' ou 'Contas a Receber'
        - situacao: 'Quitadas/Recebidas', 'Em aberto', 'Em atraso'
        - dt_ini/dt_fim: intervalo de filtro (dt_fim já deve vir com hora 23:59:59)
        """
        cur = self.db.cursor(dictionary=True, buffered=True)
        rows: List[Dict[str, Any]] = []
        total = 0.0
        try:
            if 'Pagar' in tipo:
                if situacao.startswith('Quitadas'):
                    cur.execute(
                        """
                        SELECT id, descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em
                        FROM contas_pagar
                        WHERE pago_em IS NOT NULL AND pago_em BETWEEN %s AND %s
                        ORDER BY pago_em ASC, id ASC
                        """,
                        (dt_ini, dt_fim)
                    )
                elif situacao.startswith('Em aberto'):
                    cur.execute(
                        """
                        SELECT id, descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em
                        FROM contas_pagar
                        WHERE pago_em IS NULL AND (status IS NULL OR status='aberto')
                          AND (
                                vencimento BETWEEN %s AND %s OR vencimento IS NULL
                          )
                        ORDER BY COALESCE(vencimento, '9999-12-31') ASC, id ASC
                        """,
                        (dt_ini, dt_fim)
                    )
                else:  # Em atraso
                    cur.execute(
                        """
                        SELECT id, descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em
                        FROM contas_pagar
                        WHERE pago_em IS NULL AND (status IS NULL OR status<>'pago')
                          AND vencimento IS NOT NULL
                          AND vencimento < NOW()
                          AND vencimento BETWEEN %s AND %s
                        ORDER BY vencimento ASC, id ASC
                        """,
                        (dt_ini, dt_fim)
                    )
            else:
                if situacao.startswith('Quitadas'):
                    cur.execute(
                        """
                        SELECT id, descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em
                        FROM contas_receber
                        WHERE pago_em IS NOT NULL AND pago_em BETWEEN %s AND %s
                        ORDER BY pago_em ASC, id ASC
                        """,
                        (dt_ini, dt_fim)
                    )
                elif situacao.startswith('Em aberto'):
                    cur.execute(
                        """
                        SELECT id, descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em
                        FROM contas_receber
                        WHERE pago_em IS NULL AND (status IS NULL OR status='aberto')
                          AND (
                                vencimento BETWEEN %s AND %s OR vencimento IS NULL
                          )
                        ORDER BY COALESCE(vencimento, '9999-12-31') ASC, id ASC
                        """,
                        (dt_ini, dt_fim)
                    )
                else:  # Em atraso
                    cur.execute(
                        """
                        SELECT id, descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em
                        FROM contas_receber
                        WHERE pago_em IS NULL AND (status IS NULL OR status<>'recebido')
                          AND vencimento IS NOT NULL
                          AND vencimento < NOW()
                          AND vencimento BETWEEN %s AND %s
                        ORDER BY vencimento ASC, id ASC
                        """,
                        (dt_ini, dt_fim)
                    )
            rows = cur.fetchall() or []
            # total: somatório do valor_atual (quando existir) senão valor_previsto
            for r in rows:
                vp = r.get('valor_previsto') or 0.0
                va = r.get('valor_atual') or 0.0
                total += float(va or vp or 0.0)
            return rows, len(rows), total
        finally:
            try:
                cur.close()
            except Exception:
                pass
