import socket
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple


class ChatDB:
    """
    Acesso ao banco para recursos do Chat:
    - Presença (usuários online via heartbeat)
    - Mensagens
    - Conversas e não lidas
    """

    def __init__(self, db_connection):
        self.conn = db_connection
        self.conn.row_factory = getattr(self.conn, 'row_factory', None)
        self.ensure_schema()

    # --- Schema ---
    def ensure_schema(self):
        cur = self.conn.cursor()
        
        # Verifica se a tabela chat_sessoes já existe
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'chat_sessoes'
        """)
        tabela_sessoes_existe = cur.fetchone()[0] > 0
        
        # Verifica se a tabela chat_mensagens já existe
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'chat_mensagens'
        """)
        tabela_mensagens_existe = cur.fetchone()[0] > 0
        
        # Cria a tabela de sessões/heartbeat (presença) se não existir
        if not tabela_sessoes_existe:
            try:
                cur.execute(
                    """
                    CREATE TABLE chat_sessoes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT,
                        usuario_nome VARCHAR(255),
                        dispositivo VARCHAR(255),
                        ultimo_heartbeat DATETIME,
                        UNIQUE(usuario_id, dispositivo)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
               
            except Exception as e:
                print(f"Erro ao criar tabela chat_sessoes: {e}")
        
        # Cria a tabela de mensagens se não existir
        if not tabela_mensagens_existe:
            try:
                cur.execute(
                    """
                    CREATE TABLE chat_mensagens (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        remetente_id INT,
                        remetente_nome VARCHAR(255),
                        remetente_dispositivo VARCHAR(255),
                        destinatario_id INT,
                        destinatario_nome VARCHAR(255),
                        destinatario_dispositivo VARCHAR(255),
                        texto TEXT,
                        criado_em DATETIME,
                        lido_em DATETIME
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )
                print("Tabela chat_mensagens criada com sucesso.")
            except Exception as e:
                print(f"Erro ao criar tabela chat_mensagens: {e}")
        
        self.conn.commit()

    # --- Presença ---
    def heartbeat(self, usuario_id: Optional[int], usuario_nome: str, dispositivo: Optional[str] = None):
        import socket
        disp = dispositivo or socket.gethostname()
        cur = self.conn.cursor()
        
        # Garante que temos valores válidos
        if usuario_id is None:
            print("Aviso: usuario_id é None no heartbeat")
            return
            
        if not isinstance(usuario_nome, str):
            print(f"Aviso: usuario_nome não é string: {usuario_nome}")
            usuario_nome = str(usuario_nome)  # Tenta converter para string
        
        try:
            cur.execute(
                """
                INSERT INTO chat_sessoes (usuario_id, usuario_nome, dispositivo, ultimo_heartbeat)
                VALUES (%s, %s, %s, NOW()) AS new_vals
                ON DUPLICATE KEY UPDATE
                    ultimo_heartbeat = NOW(),
                    usuario_nome = new_vals.usuario_nome
                """,
                (usuario_id, usuario_nome, disp)
            )
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao registrar heartbeat: {e}")
            self.conn.rollback()
            raise

    def obter_sessao_id(self, usuario_id: Optional[int] = None, usuario_nome: Optional[str] = None, dispositivo: Optional[str] = None) -> Optional[int]:
        """Obtém o id da sessão atual em chat_sessoes.
        Prioriza busca por (usuario_id, dispositivo); em seguida (usuario_nome, dispositivo); por fim apenas por nome.
        Retorna None se não encontrar.
        """
        try:
            cur = self.conn.cursor()
            if usuario_id is not None and dispositivo:
                cur.execute(
                    """
                    SELECT id FROM chat_sessoes
                    WHERE usuario_id = %s AND dispositivo = %s
                    ORDER BY ultimo_heartbeat DESC
                    LIMIT 1
                    """,
                    (usuario_id, dispositivo)
                )
            elif usuario_nome and dispositivo:
                cur.execute(
                    """
                    SELECT id FROM chat_sessoes
                    WHERE usuario_nome = %s AND dispositivo = %s
                    ORDER BY ultimo_heartbeat DESC
                    LIMIT 1
                    """,
                    (usuario_nome, dispositivo)
                )
            elif usuario_nome:
                cur.execute(
                    """
                    SELECT id FROM chat_sessoes
                    WHERE usuario_nome = %s
                    ORDER BY ultimo_heartbeat DESC
                    LIMIT 1
                    """,
                    (usuario_nome,)
                )
            else:
                return None
            row = cur.fetchone()
            sess_id = row[0] if row else None
            return sess_id
        except Exception as e:
            print(f"[ChatDB] Erro ao buscar sessão id: {e}")
            return None

    def remover_sessao_por_id(self, sessao_id: Optional[int]) -> int:
        """Remove uma sessão pelo id. Retorna número de linhas afetadas."""
        if not sessao_id:
            print("[ChatDB] remover_sessao_por_id chamado com id vazio")
            return 0
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM chat_sessoes WHERE id = %s", (sessao_id,))
            afetadas = cur.rowcount
            self.conn.commit()
            return afetadas
        except Exception as e:
            print(f"[ChatDB] Erro ao remover sessão por id: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise

    def listar_online(self) -> List[Dict[str, Any]]:
        """Lista todas as sessões presentes em chat_sessoes (sem filtro de tempo)."""
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT usuario_id, COALESCE(usuario_nome,'Usuário') AS usuario_nome, dispositivo, ultimo_heartbeat
            FROM chat_sessoes
            ORDER BY usuario_nome ASC
            """
        )
        rows = cur.fetchall() or []
        return rows
    
    def listar_interlocutores(self, me_id: Optional[int], me_nome: str, me_disp: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna a lista de usuários com quem o usuário atual já teve conversa (remetente ou destinatário).
        Não depende de estarem online.
        """
        try:
            cur = self.conn.cursor(dictionary=True)
            params = []
            where_a = []
            where_b = []
            # Mensagens onde EU sou remetente -> pega destinatários
            if me_id is not None:
                where_a.append("remetente_id = %s")
                params.append(me_id)
            else:
                where_a.append("remetente_nome = %s")
                params.append(me_nome)
            # Mensagens onde EU sou destinatário -> pega remetentes
            if me_id is not None:
                where_b.append("destinatario_id = %s")
                params.append(me_id)
            else:
                where_b.append("destinatario_nome = %s")
                params.append(me_nome)

            sql = f"""
                SELECT DISTINCT destinatario_id AS usuario_id, COALESCE(destinatario_nome,'Usuário') AS usuario_nome
                FROM chat_mensagens
                WHERE {' AND '.join(where_a)}
                UNION
                SELECT DISTINCT remetente_id AS usuario_id, COALESCE(remetente_nome,'Usuário') AS usuario_nome
                FROM chat_mensagens
                WHERE {' AND '.join(where_b)}
                ORDER BY usuario_nome ASC
            """
            cur.execute(sql, tuple(params))
            rows = cur.fetchall() or []
            # Remove possíveis autorreferências
            filtrados = []
            for r in rows:
                uid = r.get('usuario_id')
                nome = r.get('usuario_nome')
                if me_id is not None and uid == me_id:
                    continue
                if me_id is None and isinstance(nome, str) and nome == me_nome:
                    continue
                filtrados.append(r)
            return filtrados
        except Exception as e:
            print(f"[ChatDB] Erro ao listar interlocutores: {e}")
            return []
    
    def remover_sessao_por_nome_dispositivo(self, usuario_nome: Optional[str], dispositivo: Optional[str] = None):
        """Remove uma sessão pelo nome do usuário e (opcionalmente) dispositivo.
        OBS: o esquema tem UNIQUE(usuario_id, dispositivo), então nome pode não ser único.
        Este método atende ao requisito de remoção por nome + dispositivo.
        """
        try:
            cur = self.conn.cursor()
            if usuario_nome is None:
                return 0
            if dispositivo:
                cur.execute(
                    """
                    DELETE FROM chat_sessoes
                    WHERE usuario_nome = %s AND dispositivo = %s
                    """,
                    (usuario_nome, dispositivo)
                )
            else:
                cur.execute(
                    """
                    DELETE FROM chat_sessoes
                    WHERE usuario_nome = %s
                    """,
                    (usuario_nome,)
                )
            afetadas = cur.rowcount
            self.conn.commit()
            return afetadas
        except Exception as e:
            print(f"[ChatDB] Erro ao remover sessão por nome/dispositivo: {e}")
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise

    # --- Mensagens ---
    def enviar_mensagem(
        self,
        remetente_id: Optional[int],
        remetente_nome: str,
        remetente_dispositivo: Optional[str],
        destinatario_id: Optional[int],
        destinatario_nome: str,
        destinatario_dispositivo: Optional[str],
        texto: str,
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO chat_mensagens (
                remetente_id, remetente_nome, remetente_dispositivo,
                destinatario_id, destinatario_nome, destinatario_dispositivo,
                texto, criado_em, lido_em
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NULL)
            """,
            (
                remetente_id, remetente_nome, remetente_dispositivo,
                destinatario_id, destinatario_nome, destinatario_dispositivo,
                texto
            )
        )
        self.conn.commit()
        return cur.lastrowid

    def _match_clause(self, id_val: Optional[int], nome: str, disp: Optional[str], prefix: str) -> Tuple[str, tuple]:
        # Permite casar por id OU (nome + dispositivo)
        if id_val is not None:
            return (f"{prefix}_id = %s", (id_val,))
        # Se não houver id, usa nome+dispositivo (se houver)
        if disp:
            return (f"{prefix}_nome = %s AND {prefix}_dispositivo = %s", (nome, disp))
        return (f"{prefix}_nome = %s", (nome,))

    def listar_conversa(
        self,
        a_id: Optional[int], a_nome: str, a_disp: Optional[str],
        b_id: Optional[int], b_nome: str, b_disp: Optional[str],
        limite: int = 200
    ) -> List[Dict[str, Any]]:
        # Monta where: (A->B) OR (B->A)
        a_to_b_clause, a_to_b_vals = self._match_clause(a_id, a_nome, a_disp, 'remetente')
        a_to_b_dest_clause, a_to_b_dest_vals = self._match_clause(b_id, b_nome, b_disp, 'destinatario')
        b_to_a_clause, b_to_a_vals = self._match_clause(b_id, b_nome, b_disp, 'remetente')
        b_to_a_dest_clause, b_to_a_dest_vals = self._match_clause(a_id, a_nome, a_disp, 'destinatario')

        where = f"(({a_to_b_clause}) AND ({a_to_b_dest_clause})) OR (({b_to_a_clause}) AND ({b_to_a_dest_clause}))"
        params = a_to_b_vals + a_to_b_dest_vals + b_to_a_vals + b_to_a_dest_vals

        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT id, remetente_nome, texto, criado_em
            FROM chat_mensagens
            WHERE {where}
            ORDER BY criado_em ASC
            LIMIT %s
            """,
            (*params, limite)
        )
        rows = cur.fetchall() or []
        return rows

    def listar_nao_lidas_para(self, dest_id: Optional[int], dest_nome: str, dest_disp: Optional[str]) -> List[Dict[str, Any]]:
        dest_clause, dest_vals = self._match_clause(dest_id, dest_nome, dest_disp, 'destinatario')
        cur = self.conn.cursor(dictionary=True)
        cur.execute(
            f"""
            SELECT id, remetente_nome, texto, criado_em
            FROM chat_mensagens
            WHERE {dest_clause} AND lido_em IS NULL
            ORDER BY criado_em ASC
            """,
            dest_vals
        )
        rows = cur.fetchall() or []
        return rows

    def marcar_lidas(self, ids: List[int]):
        if not ids:
            return
        cur = self.conn.cursor()
        placeholders = ",".join(["%s"] * len(ids))
        sql = f"UPDATE chat_mensagens SET lido_em = NOW() WHERE id IN ({placeholders})"
        cur.execute(sql, tuple(ids))
        self.conn.commit()
