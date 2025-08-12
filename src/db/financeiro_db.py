"""
Módulo para operações de banco de dados do módulo Financeiro.
"""
from typing import Dict, List, Any, Optional
import mysql.connector
from datetime import datetime

class FinanceiroDB:
    """Classe para operações de banco de dados do módulo Financeiro."""
    
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
        try:
            self.ensure_schema()
        except Exception:
            # Evita travar inicialização caso não tenha permissão para DDL
            pass

    def ensure_schema(self):
        """Garante o schema necessário: caixa_sessoes e migrações na tabela financeiro (sessao_id/usuario_id)."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS caixa_sessoes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    abertura_datahora DATETIME NOT NULL,
                    abertura_valor_inicial DECIMAL(10,2) NOT NULL DEFAULT 0,
                    abertura_usuario_id INT NULL,
                    fechamento_datahora DATETIME NULL,
                    fechamento_usuario_id INT NULL,
                    observacao VARCHAR(255) NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            # Conferências de fechamento cego
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS caixa_conferencias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sessao_id INT NOT NULL,
                    datahora DATETIME NOT NULL,
                    usuario_id INT NULL,
                    -- Contados (entradas)
                    cont_entr_dinheiro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_entr_cartao_credito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_entr_cartao_debito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_entr_pix DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_entr_outro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    -- Contados (saídas)
                    cont_sai_dinheiro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_sai_cartao_credito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_sai_cartao_debito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_sai_pix DECIMAL(10,2) NOT NULL DEFAULT 0,
                    cont_sai_outro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    -- Esperados (entradas)
                    esp_entr_dinheiro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_entr_cartao_credito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_entr_cartao_debito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_entr_pix DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_entr_outro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    -- Esperados (saídas)
                    esp_sai_dinheiro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_sai_cartao_credito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_sai_cartao_debito DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_sai_pix DECIMAL(10,2) NOT NULL DEFAULT 0,
                    esp_sai_outro DECIMAL(10,2) NOT NULL DEFAULT 0,
                    -- Totais e diferenças
                    total_cont_entradas DECIMAL(10,2) NOT NULL DEFAULT 0,
                    total_cont_saidas DECIMAL(10,2) NOT NULL DEFAULT 0,
                    total_esp_entradas DECIMAL(10,2) NOT NULL DEFAULT 0,
                    total_esp_saidas DECIMAL(10,2) NOT NULL DEFAULT 0,
                    dif_entradas DECIMAL(10,2) NOT NULL DEFAULT 0,
                    dif_saidas DECIMAL(10,2) NOT NULL DEFAULT 0,
                    observacao VARCHAR(255) NULL,
                    INDEX (sessao_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            self.db.commit()
            # Estoque (produtos)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS estoque (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(160) NOT NULL,
                    qtd_atual INT NOT NULL DEFAULT 0,
                    qtd_minima INT NOT NULL DEFAULT 0,
                    valor_ultima_compra DECIMAL(10,2) NULL,
                    forma_pagamento_ultima VARCHAR(30) NULL,
                    data_ultima_compra DATE NULL,
                    criado_em DATETIME NOT NULL,
                    atualizado_em DATETIME NOT NULL,
                    UNIQUE KEY uniq_estoque_nome (nome)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            self.db.commit()
            # Contas a pagar (recorrentes e variáveis)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contas_pagar (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    descricao VARCHAR(120) NOT NULL,
                    categoria VARCHAR(80) NULL,
                    dia_vencimento TINYINT NOT NULL,
                    valor_previsto DECIMAL(10,2) NULL,
                    valor_atual DECIMAL(10,2) NULL,
                    vencimento DATE NULL,
                    status ENUM('aberto','pago') NOT NULL DEFAULT 'aberto',
                    pago_em DATETIME NULL,
                    criado_em DATETIME NOT NULL,
                    atualizado_em DATETIME NOT NULL,
                    INDEX (status),
                    INDEX (vencimento),
                    INDEX (dia_vencimento)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            self.db.commit()
            # Contas a receber (estrutura espelhada de contas_pagar)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contas_receber (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    descricao VARCHAR(120) NOT NULL,
                    categoria VARCHAR(80) NULL,
                    dia_vencimento TINYINT NOT NULL,
                    valor_previsto DECIMAL(10,2) NULL,
                    valor_atual DECIMAL(10,2) NULL,
                    vencimento DATE NULL,
                    status ENUM('aberto','recebido') NOT NULL DEFAULT 'aberto',
                    pago_em DATETIME NULL,
                    criado_em DATETIME NOT NULL,
                    atualizado_em DATETIME NOT NULL,
                    INDEX (status),
                    INDEX (vencimento),
                    INDEX (dia_vencimento)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            self.db.commit()
            # Migrações na tabela 'financeiro' para colunas solicitadas (idempotentes)
            try:
                cursor.execute("SHOW TABLES LIKE 'financeiro';")
                if cursor.fetchone():
                    # fundo_caixa
                    cursor.execute("SHOW COLUMNS FROM financeiro LIKE 'fundo_caixa';")
                    if not cursor.fetchone():
                        try:
                            cursor.execute("ALTER TABLE financeiro ADD COLUMN fundo_caixa DECIMAL(10,2) NULL;")
                        except Exception:
                            pass
                    # data_pagamento
                    cursor.execute("SHOW COLUMNS FROM financeiro LIKE 'data_pagamento';")
                    if not cursor.fetchone():
                        try:
                            cursor.execute("ALTER TABLE financeiro ADD COLUMN data_pagamento DATETIME NULL;")
                        except Exception:
                            pass
                    # aberto_por
                    cursor.execute("SHOW COLUMNS FROM financeiro LIKE 'aberto_por';")
                    if not cursor.fetchone():
                        try:
                            cursor.execute("ALTER TABLE financeiro ADD COLUMN aberto_por VARCHAR(100) NULL;")
                        except Exception:
                            pass
                    # sessao_id
                    cursor.execute("SHOW COLUMNS FROM financeiro LIKE 'sessao_id';")
                    if not cursor.fetchone():
                        try:
                            cursor.execute("ALTER TABLE financeiro ADD COLUMN sessao_id INT NULL;")
                        except Exception:
                            pass
                    # usuario_id
                    cursor.execute("SHOW COLUMNS FROM financeiro LIKE 'usuario_id';")
                    if not cursor.fetchone():
                        try:
                            cursor.execute("ALTER TABLE financeiro ADD COLUMN usuario_id INT NULL;")
                        except Exception:
                            pass
                    # tipo_pagamento já existe no schema padrão; manter
                    self.db.commit()
            except Exception:
                # Ignora falhas de migração silenciosamente
                pass
        finally:
            cursor.close()

    # ---------------- Estoque ----------------
    def estoque_criar_ou_obter_produto(self, nome: str, qtd_minima: int = 0) -> int:
        """Cria o produto no estoque (tabela 'estoque') se não existir e retorna o id."""
        nome = (nome or '').strip()
        if not nome:
            raise ValueError('Nome do produto é obrigatório')
        cur = self.db.cursor()
        try:
            cur.execute("SELECT id FROM estoque WHERE nome=%s", (nome,))
            row = cur.fetchone()
            if row:
                return int(row[0])
            agora = datetime.now()
            cur.execute(
                """
                INSERT INTO estoque (nome, qtd_atual, qtd_minima, criado_em, atualizado_em)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (nome, 0, int(qtd_minima or 0), agora, agora)
            )
            self.db.commit()
            return cur.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cur.close()

    def estoque_adicionar(self, nome: str, quantidade: int, valor: float | None, forma_pagamento: str | None, data_compra) -> None:
        """Adiciona quantidade ao estoque e atualiza dados da última compra na tabela 'estoque'."""
        if quantidade is None:
            quantidade = 0
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        prod_id = self.estoque_criar_ou_obter_produto(nome)
        cur = self.db.cursor()
        try:
            agora = datetime.now()
            cur.execute(
                """
                UPDATE estoque
                   SET qtd_atual = qtd_atual + %s,
                       valor_ultima_compra = %s,
                       forma_pagamento_ultima = %s,
                       data_ultima_compra = %s,
                       atualizado_em = %s
                 WHERE id = %s
                """,
                (quantidade, valor, forma_pagamento, data_compra, agora, prod_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cur.close()

    def estoque_definir_qtd_minima(self, nome: str, qtd_minima: int) -> None:
        cur = self.db.cursor()
        try:
            agora = datetime.now()
            prod_id = self.estoque_criar_ou_obter_produto(nome)
            cur.execute("UPDATE estoque SET qtd_minima=%s, atualizado_em=%s WHERE id=%s", (int(qtd_minima or 0), agora, prod_id))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cur.close()

    def estoque_listar(self) -> list[dict]:
        cur = self.db.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM estoque ORDER BY nome ASC")
            return cur.fetchall() or []
        finally:
            cur.close()

    def estoque_baixo(self) -> list[dict]:
        """Retorna itens com qtd_atual <= qtd_minima na tabela 'estoque'."""
        cur = self.db.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM estoque WHERE qtd_atual <= qtd_minima ORDER BY nome ASC")
            return cur.fetchall() or []
        finally:
            cur.close()

    def estoque_excluir(self, produto_id: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM estoque WHERE id=%s", (int(produto_id),))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def estoque_atualizar(
        self,
        produto_id: int,
        nome: str,
        qtd_atual: int,
        qtd_minima: int,
        valor_ultima_compra: float | None,
        forma_pagamento_ultima: str | None,
        data_ultima_compra,
    ) -> None:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE estoque
                   SET nome=%s,
                       qtd_atual=%s,
                       qtd_minima=%s,
                       valor_ultima_compra=%s,
                       forma_pagamento_ultima=%s,
                       data_ultima_compra=%s,
                       atualizado_em=%s
                 WHERE id=%s
                """,
                (
                    (nome or '').strip(),
                    int(qtd_atual or 0),
                    int(qtd_minima or 0),
                    valor_ultima_compra,
                    forma_pagamento_ultima,
                    data_ultima_compra,
                    agora,
                    int(produto_id),
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()
    # ---------------- Contas a Pagar ----------------
    def criar_conta_pagar(self, descricao: str, categoria: str | None, dia_vencimento: int, valor_previsto: float | None,
                           valor_atual: float | None, vencimento: datetime | None, status: str = 'aberto') -> int:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                INSERT INTO contas_pagar (descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em, criado_em, atualizado_em)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, %s, %s)
                """,
                (descricao, categoria, int(dia_vencimento), valor_previsto, valor_atual, vencimento, status, agora, agora)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def listar_contas_pagar(self, status: str | None = None) -> list[dict]:
        cursor = self.db.cursor(dictionary=True)
        try:
            if status and status.lower() != 'todos':
                cursor.execute(
                    """
                    SELECT * FROM contas_pagar
                    WHERE status = %s
                    ORDER BY COALESCE(vencimento, DATE(CONCAT(YEAR(NOW()),'-',LPAD(dia_vencimento,2,'0'),'-01'))) ASC, id ASC
                    """,
                    (status,)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM contas_pagar
                    ORDER BY COALESCE(vencimento, DATE(CONCAT(YEAR(NOW()),'-',LPAD(dia_vencimento,2,'0'),'-01'))) ASC, id ASC
                    """
                )
            return cursor.fetchall() or []
        finally:
            cursor.close()

    def atualizar_conta_pagar_status(self, conta_id: int, status: str) -> None:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE contas_pagar
                SET status=%s, pago_em=CASE WHEN %s='pago' THEN %s ELSE NULL END, atualizado_em=%s
                WHERE id=%s
                """,
                (status, status, agora, agora, conta_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def atualizar_conta_pagar_valor(self, conta_id: int, valor_atual: float | None) -> None:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE contas_pagar
                SET valor_atual=%s, atualizado_em=%s
                WHERE id=%s
                """,
                (valor_atual, agora, conta_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def excluir_conta_pagar(self, conta_id: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM contas_pagar WHERE id=%s", (conta_id,))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def atualizar_conta_pagar_dados(
        self,
        conta_id: int,
        descricao: str,
        categoria: str | None,
        dia_vencimento: int,
        valor_previsto: float | None,
        vencimento: datetime | None,
    ) -> None:
        """Atualiza campos editáveis da conta a pagar."""
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE contas_pagar
                SET descricao=%s, categoria=%s, dia_vencimento=%s, valor_previsto=%s, vencimento=%s, atualizado_em=%s
                WHERE id=%s
                """,
                (descricao, categoria, int(dia_vencimento), valor_previsto, vencimento, agora, conta_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    # ---------------- Contas a Receber ----------------
    def criar_conta_receber(self, descricao: str, categoria: str | None, dia_vencimento: int, valor_previsto: float | None,
                             valor_atual: float | None, vencimento: datetime | None, status: str = 'aberto') -> int:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                INSERT INTO contas_receber (descricao, categoria, dia_vencimento, valor_previsto, valor_atual, vencimento, status, pago_em, criado_em, atualizado_em)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, %s, %s)
                """,
                (descricao, categoria, int(dia_vencimento), valor_previsto, valor_atual, vencimento, status, agora, agora)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def listar_contas_receber(self, status: str | None = None) -> list[dict]:
        cursor = self.db.cursor(dictionary=True)
        try:
            if status and status.lower() != 'todos':
                cursor.execute(
                    """
                    SELECT * FROM contas_receber
                    WHERE status = %s
                    ORDER BY COALESCE(vencimento, DATE(CONCAT(YEAR(NOW()),'-',LPAD(dia_vencimento,2,'0'),'-01'))) ASC, id ASC
                    """,
                    (status,)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM contas_receber
                    ORDER BY COALESCE(vencimento, DATE(CONCAT(YEAR(NOW()),'-',LPAD(dia_vencimento,2,'0'),'-01'))) ASC, id ASC
                    """
                )
            return cursor.fetchall() or []
        finally:
            cursor.close()

    def atualizar_conta_receber_status(self, conta_id: int, status: str) -> None:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE contas_receber
                SET status=%s, pago_em=CASE WHEN %s='recebido' THEN %s ELSE NULL END, atualizado_em=%s
                WHERE id=%s
                """,
                (status, status, agora, agora, conta_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def atualizar_conta_receber_valor(self, conta_id: int, valor_atual: float | None) -> None:
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE contas_receber
                SET valor_atual=%s, atualizado_em=%s
                WHERE id=%s
                """,
                (valor_atual, agora, conta_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def atualizar_conta_receber_dados(
        self,
        conta_id: int,
        descricao: str,
        categoria: str | None,
        dia_vencimento: int,
        valor_previsto: float | None,
        vencimento: datetime | None,
    ) -> None:
        """Atualiza campos editáveis da conta a receber."""
        cursor = self.db.cursor()
        try:
            agora = datetime.now()
            cursor.execute(
                """
                UPDATE contas_receber
                SET descricao=%s, categoria=%s, dia_vencimento=%s, valor_previsto=%s, vencimento=%s, atualizado_em=%s
                WHERE id=%s
                """,
                (descricao, categoria, int(dia_vencimento), valor_previsto, vencimento, agora, conta_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def excluir_conta_receber(self, conta_id: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM contas_receber WHERE id=%s", (conta_id,))
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def atualizar_observacao_fechamento(self, sessao_id: int, observacao: Optional[str]) -> None:
        """Atualiza a observação em caixa_fechamentos_resumo para a sessão informada."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "UPDATE caixa_fechamentos_resumo SET observacao=%s WHERE sessao_id=%s",
                (observacao, sessao_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()
    def salvar_fechamento_resumo(
        self,
        sessao_id: int,
        usuario_id: int | None,
        resumo: dict,
        dif_total_entradas: float = 0.0,
        dif_total_saidas: float = 0.0,
        observacao: str | None = None,
    ) -> int:
        """Insere registro de resumo de fechamento em caixa_fechamentos_resumo.
        Supõe que a tabela já exista (foi criada pelo usuário)."""
        # Buscar dados de abertura
        cur = self.db.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT abertura_datahora, abertura_valor_inicial FROM caixa_sessoes WHERE id=%s",
                (sessao_id,)
            )
            row = cur.fetchone() or {}
            data_abertura = row.get('abertura_datahora') or datetime.now()
            abertura_valor_inicial = float(row.get('abertura_valor_inicial') or 0.0)
        finally:
            cur.close()

        entradas = resumo.get('entradas_por_forma', {}) or {}
        saídas = resumo.get('saidas_por_forma', {}) or {}

        total_entradas = float(resumo.get('total_entradas', 0.0) or 0.0)
        total_saidas = float(resumo.get('total_saidas', 0.0) or 0.0)
        saldo_final = float(resumo.get('saldo_final', 0.0) or 0.0)

        campos = (
            'sessao_id','data_abertura','data_fechamento','abertura_valor_inicial',
            'total_entradas','total_saidas','saldo_final',
            'entr_dinheiro','entr_cartao_credito','entr_cartao_debito','entr_pix','entr_outro',
            'sai_dinheiro','sai_cartao_credito','sai_cartao_debito','sai_pix','sai_outro',
            'dif_total_entradas','dif_total_saidas','has_diferenca','usuario_fechamento_id','observacao'
        )

        values = (
            sessao_id,
            data_abertura,
            datetime.now(),
            abertura_valor_inicial,
            total_entradas,
            total_saidas,
            saldo_final,
            float(entradas.get('dinheiro', 0.0) or 0.0),
            float(entradas.get('cartao_credito', 0.0) or entradas.get('cartao', 0.0) or 0.0),
            float(entradas.get('cartao_debito', 0.0) or 0.0),
            float(entradas.get('pix', 0.0) or 0.0),
            float(entradas.get('outro', 0.0) or 0.0),
            float(saídas.get('dinheiro', 0.0) or 0.0),
            float(saídas.get('cartao_credito', 0.0) or saídas.get('cartao', 0.0) or 0.0),
            float(saídas.get('cartao_debito', 0.0) or 0.0),
            float(saídas.get('pix', 0.0) or 0.0),
            float(saídas.get('outro', 0.0) or 0.0),
            float(dif_total_entradas or 0.0),
            float(dif_total_saidas or 0.0),
            1 if (abs(float(dif_total_entradas or 0.0)) > 1e-6 or abs(float(dif_total_saidas or 0.0)) > 1e-6) else 0,
            usuario_id,
            observacao,
        )

        placeholders = ", ".join(["%s"] * len(values))
        cols = ", ".join(campos)

        cursor = self.db.cursor()
        try:
            cursor.execute(
                f"INSERT INTO caixa_fechamentos_resumo ({cols}) VALUES ({placeholders})",
                values
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def listar_consultas_do_dia(self, data: Optional[str] = None) -> list[dict]:
        """Lista consultas do dia (ou de uma data AAAA-MM-DD se informada),
        incluindo paciente e médico.
        Retorna: [{consulta_id, paciente_id, paciente_nome, medico_id, medico_nome, hora, data, tipo_atendimento, valor_exame}]
        """
        cursor = self.db.cursor(dictionary=True)
        try:
            if data:
                cursor.execute(
                    """
                    SELECT c.id AS consulta_id, c.paciente_id, p.nome AS paciente_nome,
                           c.medico_id, m.nome AS medico_nome, c.hora, c.data, c.tipo_atendimento,
                           ec.valor AS valor_exame
                    FROM consultas c
                    JOIN pacientes p ON p.id = c.paciente_id
                    JOIN medicos m ON m.id = c.medico_id
                    LEFT JOIN exames_consultas ec
                           ON ec.medico_id = c.medico_id
                          AND ec.nome = c.tipo_atendimento
                    WHERE DATE(c.data) = %s
                      AND COALESCE(c.status_pagameto, 0) = 0
                    ORDER BY c.hora ASC, c.id ASC
                    """,
                    (data,)
                )
            else:
                cursor.execute(
                    """
                    SELECT c.id AS consulta_id, c.paciente_id, p.nome AS paciente_nome,
                           c.medico_id, m.nome AS medico_nome, c.hora, c.data, c.tipo_atendimento,
                           ec.valor AS valor_exame
                    FROM consultas c
                    JOIN pacientes p ON p.id = c.paciente_id
                    JOIN medicos m ON m.id = c.medico_id
                    LEFT JOIN exames_consultas ec
                           ON ec.medico_id = c.medico_id
                          AND ec.nome = c.tipo_atendimento
                    WHERE DATE(c.data) = CURDATE()
                      AND COALESCE(c.status_pagameto, 0) = 0
                    ORDER BY c.hora ASC, c.id ASC
                    """
                )
            return cursor.fetchall() or []
        finally:
            cursor.close()

    def get_caixa_aberto(self) -> dict | None:
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT * FROM caixa_sessoes
                WHERE fechamento_datahora IS NULL
                ORDER BY abertura_datahora DESC
                LIMIT 1
                """
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def abrir_caixa(self, valor_inicial: float, usuario_id: int | None = None, observacao: str | None = None) -> int:
        """Abre uma nova sessão de caixa se não houver uma aberta. Retorna id da sessão."""
        existente = self.get_caixa_aberto()
        if existente:
            return existente['id']
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO caixa_sessoes (abertura_datahora, abertura_valor_inicial, abertura_usuario_id, observacao)
                VALUES (%s, %s, %s, %s)
                """,
                (datetime.now(), float(valor_inicial or 0), usuario_id, observacao)
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    # Removido: registrar_movimento em caixa_movimentos (não é mais usado)

    def registrar_movimento_financeiro(self, valor: float, tipo: str, descricao: str | None, usuario_id: int | None, tipo_pagamento: str | None,
                                       paciente_id: int | None = None, consulta_id: int | None = None, medico_id: int | None = None,
                                       status: str | None = 'pago', fundo_caixa: float | None = None, aberto_por: str | None = None,
                                       sessao_id: int | None = None) -> int:
        """Insere um registro correspondente na tabela 'financeiro'.
        - tipo: 'entrada' | 'saida' | 'caixa_abertura' | 'caixa_fechamento' etc.
        - tipo_pagamento: 'dinheiro' | 'pix' | 'cartao_credito' | 'cartao_debito' | None
        - status: 'pago' | 'aberto'
        - fundo_caixa: valor do fundo quando aplicável (abertura)
        - aberto_por: nome do usuário que abriu (quando aplicável)
        """
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO financeiro (consulta_id, paciente_id, data, valor, tipo, descricao, status, medico_id, tipo_pagamento, data_pagamento, fundo_caixa, aberto_por, sessao_id, usuario_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    consulta_id, paciente_id, datetime.now(), float(valor or 0.0), tipo, descricao,
                    status or 'pago', medico_id, tipo_pagamento, datetime.now() if (status or 'pago') == 'pago' else None,
                    fundo_caixa, aberto_por, sessao_id, usuario_id
                )
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def listar_movimentos(self, sessao_id: int) -> list[dict]:
        """Lista movimentos da sessão a partir da tabela financeiro."""
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT id, tipo, valor, descricao, data AS data_hora, usuario_id, tipo_pagamento
                FROM financeiro
                WHERE sessao_id = %s AND tipo IN ('entrada','saida')
                ORDER BY data ASC, id ASC
                """,
                (sessao_id,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def fechar_caixa(self, sessao_id: int, usuario_id: int | None = None):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                UPDATE caixa_sessoes
                SET fechamento_datahora = %s, fechamento_usuario_id = %s
                WHERE id = %s AND fechamento_datahora IS NULL
                """,
                (datetime.now(), usuario_id, sessao_id)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()

    def resumo_sessao(self, sessao_id: int) -> dict:
        """Calcula totais de entradas/saídas por forma e saldo."""
        cursor = self.db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT abertura_valor_inicial FROM caixa_sessoes WHERE id=%s", (sessao_id,))
            row = cursor.fetchone()
            valor_inicial = float(row['abertura_valor_inicial'] if row and row.get('abertura_valor_inicial') is not None else 0)

            # Somatórios a partir da tabela financeiro por tipo_pagamento
            cursor.execute(
                """
                SELECT tipo_pagamento, SUM(valor) AS total
                FROM financeiro
                WHERE sessao_id = %s AND tipo = 'entrada'
                GROUP BY tipo_pagamento
                """,
                (sessao_id,)
            )
            ent_rows = cursor.fetchall() or []

            cursor.execute(
                """
                SELECT tipo_pagamento, SUM(valor) AS total
                FROM financeiro
                WHERE sessao_id = %s AND tipo = 'saida'
                GROUP BY tipo_pagamento
                """,
                (sessao_id,)
            )
            sai_rows = cursor.fetchall() or []

            entradas = {}
            saidas = {}
            total_entradas = 0.0
            total_saidas = 0.0
            for r in ent_rows:
                forma = r['tipo_pagamento'] or 'outro'
                total = float(r['total'] or 0)
                entradas[forma] = entradas.get(forma, 0.0) + total
                total_entradas += total
            for r in sai_rows:
                forma = r['tipo_pagamento'] or 'outro'
                total = float(r['total'] or 0)
                saidas[forma] = saidas.get(forma, 0.0) + total
                total_saidas += total

            saldo_final = valor_inicial + total_entradas - total_saidas
            return {
                'valor_inicial': valor_inicial,
                'entradas_por_forma': entradas,
                'saidas_por_forma': saidas,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_final': saldo_final,
            }
        finally:
            cursor.close()

    def registrar_conferencia(
        self,
        sessao_id: int,
        usuario_id: int | None,
        contados: dict,
        esperados: dict,
        observacao: str | None = None,
    ) -> int:
        """Registra a conferência do fechamento cego na tabela caixa_conferencias.
        Espera chaves por forma: 'dinheiro', 'cartao_credito', 'cartao_debito', 'pix', 'outro'
        tanto para entradas quanto saídas nas estruturas:
          contados = {'entradas': {...}, 'saidas': {...}, 'total_entradas': x, 'total_saidas': y}
          esperados = {'entradas': {...}, 'saidas': {...}, 'total_entradas': x, 'total_saidas': y}
        """
        formas = ['dinheiro', 'cartao_credito', 'cartao_debito', 'pix', 'outro']
        c_e = contados.get('entradas', {})
        c_s = contados.get('saidas', {})
        e_e = esperados.get('entradas', {})
        e_s = esperados.get('saidas', {})

        total_cont_entradas = float(contados.get('total_entradas', 0.0))
        total_cont_saidas = float(contados.get('total_saidas', 0.0))
        total_esp_entradas = float(esperados.get('total_entradas', 0.0))
        total_esp_saidas = float(esperados.get('total_saidas', 0.0))
        dif_entradas = total_cont_entradas - total_esp_entradas
        dif_saidas = total_cont_saidas - total_esp_saidas

        cursor = self.db.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO caixa_conferencias (
                    sessao_id, datahora, usuario_id,
                    cont_entr_dinheiro, cont_entr_cartao_credito, cont_entr_cartao_debito, cont_entr_pix, cont_entr_outro,
                    cont_sai_dinheiro, cont_sai_cartao_credito, cont_sai_cartao_debito, cont_sai_pix, cont_sai_outro,
                    esp_entr_dinheiro, esp_entr_cartao_credito, esp_entr_cartao_debito, esp_entr_pix, esp_entr_outro,
                    esp_sai_dinheiro, esp_sai_cartao_credito, esp_sai_cartao_debito, esp_sai_pix, esp_sai_outro,
                    total_cont_entradas, total_cont_saidas, total_esp_entradas, total_esp_saidas, dif_entradas, dif_saidas,
                    observacao
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s
                )
                """,
                (
                    sessao_id, datetime.now(), usuario_id,
                    float(c_e.get('dinheiro', 0.0)), float(c_e.get('cartao_credito', 0.0)), float(c_e.get('cartao_debito', 0.0)), float(c_e.get('pix', 0.0)), float(c_e.get('outro', 0.0)),
                    float(c_s.get('dinheiro', 0.0)), float(c_s.get('cartao_credito', 0.0)), float(c_s.get('cartao_debito', 0.0)), float(c_s.get('pix', 0.0)), float(c_s.get('outro', 0.0)),
                    float(e_e.get('dinheiro', 0.0)), float(e_e.get('cartao_credito', 0.0)), float(e_e.get('cartao_debito', 0.0)), float(e_e.get('pix', 0.0)), float(e_e.get('outro', 0.0)),
                    float(e_s.get('dinheiro', 0.0)), float(e_s.get('cartao_credito', 0.0)), float(e_s.get('cartao_debito', 0.0)), float(e_s.get('pix', 0.0)), float(e_s.get('outro', 0.0)),
                    total_cont_entradas, total_cont_saidas, total_esp_entradas, total_esp_saidas, dif_entradas, dif_saidas,
                    observacao
                )
            )
            self.db.commit()
            return cursor.lastrowid
        except Exception:
            self.db.rollback()
            raise
        finally:
            cursor.close()
        
    def registrar_entrada(self, valor, descricao, tipo_entrada, usuario_id=None, usuario_nome=None, pedido_id=None):
        """
        Registra um pagamento no sistema.
        
        Args:
            valor: Valor do pagamento
            descricao: Descrição do pagamento
            tipo_entrada: Forma de pagamento (ex: 'dinheiro', 'cartao', 'pix')
            usuario_id: ID do usuário que registrou o pagamento
            usuario_nome: Nome do usuário que registrou o pagamento
            pedido_id: ID do pedido relacionado
            
        Returns:
            int: ID do pagamento registrado ou 0 em caso de erro
        """
        # Iniciando registro de pagamento
        
        if not pedido_id:
            print("[ERRO] ID do pedido não informado")
            return 0
            
        try:
            cursor = self.db.cursor()
            
            # Preparar dados para inserção
            dados = {
                'pedido_id': pedido_id,
                'forma_pagamento': tipo_entrada,
                'valor': valor,
                'data_hora': datetime.now()
            }
            
            # Construir a query dinamicamente baseada nas chaves fornecidas
            colunas = ", ".join(dados.keys())
            placeholders = ", ".join(["%s"] * len(dados))
            
            query = f"""
                INSERT INTO pagamentos ({colunas})
                VALUES ({placeholders})
            """
            
            # Executar a query
            cursor.execute(query, list(dados.values()))
            
            # Obter o ID do pagamento inserido
            pagamento_id = cursor.lastrowid
            self.db.commit()
            return pagamento_id
                
        except mysql.connector.Error as err:
            print(f"[ERRO] Erro ao registrar pagamento: {err}")
            print(f"[ERRO] SQL State: {err.sqlstate}")
            print(f"[ERRO] Código de erro: {err.errno}")
            print(f"[ERRO] Mensagem: {err.msg}")
            if 'cursor' in locals() and self.db:
                self.db.rollback()
            return 0
                
        except Exception as e:
            print(f"[ERRO CRÍTICO] Erro inesperado ao registrar pagamento: {str(e)}")
            import traceback
            traceback.print_exc()
            if 'cursor' in locals() and self.db:
                self.db.rollback()
            return 0
            
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
                pass
