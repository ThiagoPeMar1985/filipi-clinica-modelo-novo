from __future__ import annotations
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from src.db.financeiro_db import FinanceiroDB


class EstoqueController:
    """Controller do módulo de Estoque.

    Mantém a lógica de negócio e orquestra chamadas ao FinanceiroDB
    para a tabela 'estoque'. A View não acessa o DB diretamente.
    """

    def __init__(self, db_connection):
        self.db = FinanceiroDB(db_connection)

    # ---------- Consultas ----------
    def listar(self) -> List[Dict[str, Any]]:
        return self.db.estoque_listar()

    def baixo(self) -> List[Dict[str, Any]]:
        return self.db.estoque_baixo()

    # ---------- Ações ----------
    def adicionar(
        self,
        nome: str,
        quantidade: int,
        valor: Optional[float],
        forma_pagamento: Optional[str],
        data_compra: Optional[date | datetime],
        qtd_minima: Optional[int] = None,
    ) -> None:
        nome = (nome or '').strip()
        if not nome:
            raise ValueError('Nome do produto é obrigatório')
        if qtd_minima is not None and int(qtd_minima) >= 0:
            self.db.estoque_definir_qtd_minima(nome, int(qtd_minima))
        self.db.estoque_adicionar(nome, int(quantidade), valor, forma_pagamento, data_compra)

    def definir_minima(self, nome: str, qtd_minima: int) -> None:
        nome = (nome or '').strip()
        if not nome:
            raise ValueError('Nome do produto é obrigatório')
        self.db.estoque_definir_qtd_minima(nome, int(qtd_minima))

    def excluir(self, produto_id: int) -> None:
        self.db.estoque_excluir(int(produto_id))

    def atualizar(
        self,
        produto_id: int,
        nome: str,
        qtd_atual: int,
        qtd_minima: int,
        valor_ultima_compra: Optional[float],
        forma_pagamento_ultima: Optional[str],
        data_ultima_compra: Optional[date | datetime],
    ) -> None:
        nome = (nome or '').strip()
        if not nome:
            raise ValueError('Nome do produto é obrigatório')
        self.db.estoque_atualizar(
            int(produto_id), nome, int(qtd_atual), int(qtd_minima),
            valor_ultima_compra, forma_pagamento_ultima, data_ultima_compra
        )
