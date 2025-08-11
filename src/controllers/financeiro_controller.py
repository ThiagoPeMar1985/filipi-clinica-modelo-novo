"""
Controlador para o módulo Financeiro.
"""
from src.db.financeiro_db import FinanceiroDB
from typing import Optional

class FinanceiroController:
    """Controlador para operações do módulo Financeiro."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa o controlador com a conexão de banco de dados.
        
        Args:
            db_connection: Conexão com o banco de dados
        """
        self.db_connection = db_connection
        if db_connection:
            self.financeiro_db = FinanceiroDB(db_connection)
        self._sessao_id = None
        # Contexto de usuário padrão (usado quando não for passado na chamada)
        self.usuario_id: Optional[int] = None
        self.usuario_nome: Optional[str] = None
        # Armazena dados da última conferência cega realizada antes do fechamento
        self._ultima_conferencia: Optional[dict] = None
        # Armazena o id da última sessão fechada para permitir salvar observação após o fechamento
        self._ultima_sessao_fechada_id: Optional[int] = None
        
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
    
    def _resolver_usuario(self, uid: Optional[int], uname: Optional[str]):
        """Retorna (usuario_id, usuario_nome) usando fallbacks nesta ordem:
        1) Parâmetros explícitos
        2) Atributos já definidos no controller (set_usuario)
        3) Atributos do controller da view vinculada (self.view.controller),
           cobrindo formatos comuns: usuario_id, usuario_dict['id'], usuario.id, usuario.get_id()
        """
        u_id = uid if uid is not None else self.usuario_id
        u_name = uname if uname is not None else self.usuario_nome
        if (u_id is None or u_name is None) and hasattr(self, 'view') and getattr(self, 'view', None) is not None:
            try:
                vc = getattr(self.view, 'controller', None)
                if vc is not None:
                    # 3.1: atributos diretos
                    if u_id is None:
                        u_id = getattr(vc, 'usuario_id', None)
                    if u_name is None:
                        u_name = getattr(vc, 'usuario_nome', None)

                    # 3.2: dicionário de usuário
                    if (u_id is None or u_name is None):
                        try:
                            ud = getattr(vc, 'usuario_dict', None)
                            if isinstance(ud, dict):
                                if u_id is None:
                                    raw = ud.get('id')
                                    try:
                                        u_id = int(raw) if raw is not None else None
                                    except Exception:
                                        u_id = None
                                if u_name is None:
                                    u_name = ud.get('nome') or ud.get('name') or u_name
                        except Exception:
                            pass

                    # 3.3: objeto usuário
                    if (u_id is None or u_name is None):
                        try:
                            user_obj = getattr(vc, 'usuario', None)
                            if user_obj is not None:
                                if u_id is None:
                                    try:
                                        u_id = int(getattr(user_obj, 'id'))
                                    except Exception:
                                        try:
                                            u_id = int(user_obj.get_id())
                                        except Exception:
                                            pass
                                if u_name is None:
                                    u_name = (
                                        getattr(user_obj, 'nome', None)
                                        or getattr(user_obj, 'name', None)
                                        or u_name
                                    )
                        except Exception:
                            pass
            except Exception:
                pass
        # Atualiza o contexto padrão para próximas operações
        if u_id is not None:
            self.usuario_id = u_id
        if u_name is not None:
            self.usuario_nome = u_name
        return u_id, u_name
    
    def set_db_connection(self, db_connection):
        """Permite configurar/trocar a conexão de DB após a criação."""
        self.db_connection = db_connection
        self.financeiro_db = FinanceiroDB(db_connection)
        self._sessao_id = None

    def set_usuario(self, usuario_id: Optional[int], usuario_nome: Optional[str] = None):
        """Define o usuário padrão a ser usado nas operações do caixa."""
        self.usuario_id = usuario_id
        self.usuario_nome = usuario_nome

    # ----- Caixa (Sessão) -----
    def get_sessao_aberta(self):
        if not hasattr(self, 'financeiro_db'):
            return None
        sessao = self.financeiro_db.get_caixa_aberto()
        if sessao:
            self._sessao_id = sessao['id']
        return sessao

    def abrir_caixa(self, valor_inicial: float, usuario_id: Optional[int] = None, usuario_nome: Optional[str] = None, observacao: Optional[str] = None) -> int:
        if not hasattr(self, 'financeiro_db'):
            return 0
        # Resolve usuário com fallback da view.controller
        usuario_id, usuario_nome = self._resolver_usuario(usuario_id, usuario_nome)
        # Normaliza e valida usuário
        try:
            usuario_id = int(usuario_id) if usuario_id is not None else None
        except Exception:
            usuario_id = None
        if usuario_id is None:
            # Sem usuário válido, não abrir caixa para evitar registros órfãos
            return 0
        sessao_id = self.financeiro_db.abrir_caixa(valor_inicial, usuario_id, observacao)
        self._sessao_id = sessao_id
        # Log na tabela financeiro: abertura do caixa
        try:
            self.financeiro_db.registrar_movimento_financeiro(
                valor=valor_inicial or 0.0,
                tipo='caixa_abertura',
                descricao='Abertura de caixa',
                usuario_id=usuario_id,
                tipo_pagamento=None,
                paciente_id=None,
                consulta_id=None,
                medico_id=None,
                status='aberto',
                fundo_caixa=valor_inicial or 0.0,
                aberto_por=usuario_nome,
                sessao_id=sessao_id
            )
        except Exception:
            # Não interrompe a abertura do caixa por falha de log
            pass
        return sessao_id

    def registrar_movimento(
        self,
        tipo: str,  # 'recebimento' | 'pagamento' (caixa)
        tipo_pagamento: str,  # 'dinheiro' | 'pix' | 'cartao_credito' | 'cartao_debito' | 'outro'
        valor: float,
        descricao: str = "",
        usuario_id: Optional[int] = None,
        paciente_id: Optional[int] = None,
        consulta_id: Optional[int] = None,
        medico_id: Optional[int] = None,
        status: str = 'pago',  # 'pago' | 'aberto'
    ) -> int:
        if not hasattr(self, 'financeiro_db'):
            return 0
        # Resolve usuário com fallback da view.controller
        usuario_id, _ = self._resolver_usuario(usuario_id, None)
        # Garante uma sessão aberta
        if not self._sessao_id:
            sessao = self.get_sessao_aberta()
            if not sessao:
                return 0
        # Grava somente na tabela 'financeiro'
        mov_id = self.financeiro_db.registrar_movimento_financeiro(
            valor=valor,
            tipo='entrada' if tipo in ('recebimento','entrada') else 'saida',
            descricao=descricao,
            usuario_id=usuario_id,
            tipo_pagamento=tipo_pagamento,
            paciente_id=paciente_id,
            consulta_id=consulta_id,
            medico_id=medico_id,
            status=status,
            sessao_id=self._sessao_id,
        )
        # Sincroniza imediatamente o status de pagamento/chegada na agenda
        try:
            if (tipo in ('recebimento','entrada')) and (str(status).lower() == 'pago'):
                from src.controllers.agenda_controller import AgendaController
                agenda = AgendaController(db_connection=self.financeiro_db.db)
                if consulta_id:
                    try:
                        agenda.sincronizar_status_pagamento(int(consulta_id))
                    except Exception:
                        pass
                elif paciente_id:
                    # Sincroniza todas as consultas do paciente no dia atual
                    try:
                        from datetime import datetime
                        hoje = datetime.now().strftime('%Y-%m-%d')
                        # Buscar consultas do dia para o paciente
                        cur = self.financeiro_db.db.cursor()
                        cur.execute(
                            """
                            SELECT id FROM consultas
                            WHERE paciente_id = %s AND data = %s
                            """,
                            (paciente_id, hoje)
                        )
                        ids = [r[0] for r in cur.fetchall()]
                        cur.close()
                        for cid in ids:
                            try:
                                agenda.sincronizar_status_pagamento(int(cid))
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pass

        return mov_id

    def listar_movimentos(self):
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return []
        return self.financeiro_db.listar_movimentos(self._sessao_id)

    def fechar_caixa(self, usuario_id: Optional[int] = None, usuario_nome: Optional[str] = None):
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return None
        # Resolve usuário com fallback da view.controller
        usuario_id, usuario_nome = self._resolver_usuario(usuario_id, usuario_nome)
        # Normaliza e valida usuário
        try:
            usuario_id = int(usuario_id) if usuario_id is not None else None
        except Exception:
            usuario_id = None
        if usuario_id is None:
            # Sem usuário válido, não fechar caixa para evitar registros órfãos
            return None
        # Resumo antes de fechar
        resumo = self.financeiro_db.resumo_sessao(self._sessao_id)
        # Antes de efetivar o fechamento, persiste o resumo do dia na tabela de fechamentos
        # usando as diferenças da última conferência (se houver)
        try:
            dif_ent = 0.0
            dif_sai = 0.0
            if isinstance(getattr(self, '_ultima_conferencia', None), dict):
                d = self._ultima_conferencia.get('diferencas', {})
                dif_ent = float(d.get('total_entradas', 0.0) or 0.0)
                dif_sai = float(d.get('total_saidas', 0.0) or 0.0)
            self.financeiro_db.salvar_fechamento_resumo(
                sessao_id=self._sessao_id,
                usuario_id=usuario_id,
                resumo=resumo or {},
                dif_total_entradas=dif_ent,
                dif_total_saidas=dif_sai,
                observacao=None,
            )
        except Exception:
            # Não impede o fechamento do caixa caso o resumo não seja salvo
            pass

        # Guarda id da sessão que está sendo fechada
        _sessao_encerrada = self._sessao_id
        self.financeiro_db.fechar_caixa(self._sessao_id, usuario_id)
        # Log de fechamento (opcional)
        try:
            self.financeiro_db.registrar_movimento_financeiro(
                valor=resumo.get('saldo_final', 0.0) if resumo else 0.0,
                tipo='caixa_fechamento',
                descricao='Fechamento de caixa',
                usuario_id=usuario_id,
                tipo_pagamento=None,
                paciente_id=None,
                consulta_id=None,
                medico_id=None,
                status='pago',
                sessao_id=self._sessao_id,
            )
        except Exception:
            pass
        self._sessao_id = None
        # Limpa última conferência após fechar
        self._ultima_conferencia = None
        # Mantém referência da última sessão fechada para salvar observação pelo operador
        self._ultima_sessao_fechada_id = _sessao_encerrada
        return resumo

    def resumo_sessao(self):
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return None
        return self.financeiro_db.resumo_sessao(self._sessao_id)

    def conferir_fechamento(self, contados: dict, usuario_id: Optional[int] = None):
        """Compara valores contados (entradas/saídas por forma) com o esperado na sessão aberta,
        registra a conferência e retorna o payload com diferenças.

        contados esperado:
          {
            'entradas': {'dinheiro': x, 'cartao_credito': y, 'cartao_debito': z, 'pix': w, 'outro': k},
            'saidas':   {'dinheiro': x, 'cartao_credito': y, 'cartao_debito': z, 'pix': w, 'outro': k}
          }
        """
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return None
        if usuario_id is None:
            usuario_id = self.usuario_id

        esperado = self.financeiro_db.resumo_sessao(self._sessao_id) or {}
        # Mapear esperado para as chaves exigidas
        e_ent = {
            'dinheiro': float(esperado.get('entradas_por_forma', {}).get('dinheiro', 0.0)),
            'cartao_credito': float(esperado.get('entradas_por_forma', {}).get('cartao_credito', 0.0) or esperado.get('entradas_por_forma', {}).get('cartao', 0.0)),
            'cartao_debito': float(esperado.get('entradas_por_forma', {}).get('cartao_debito', 0.0)),
            'pix': float(esperado.get('entradas_por_forma', {}).get('pix', 0.0)),
            'outro': float(esperado.get('entradas_por_forma', {}).get('outro', 0.0)),
        }
        e_sai = {
            'dinheiro': float(esperado.get('saidas_por_forma', {}).get('dinheiro', 0.0)),
            'cartao_credito': float(esperado.get('saidas_por_forma', {}).get('cartao_credito', 0.0) or esperado.get('saidas_por_forma', {}).get('cartao', 0.0)),
            'cartao_debito': float(esperado.get('saidas_por_forma', {}).get('cartao_debito', 0.0)),
            'pix': float(esperado.get('saidas_por_forma', {}).get('pix', 0.0)),
            'outro': float(esperado.get('saidas_por_forma', {}).get('outro', 0.0)),
        }

        cont_e = contados.get('entradas', {})
        cont_s = contados.get('saidas', {})
        totais_cont = {
            'total_entradas': sum(float(cont_e.get(k, 0.0) or 0.0) for k in ['dinheiro','cartao_credito','cartao_debito','pix','outro']),
            'total_saidas': sum(float(cont_s.get(k, 0.0) or 0.0) for k in ['dinheiro','cartao_credito','cartao_debito','pix','outro'])
        }
        totais_esp = {
            'total_entradas': float(esperado.get('total_entradas', 0.0)),
            'total_saidas': float(esperado.get('total_saidas', 0.0))
        }

        payload_cont = {'entradas': {k: float(cont_e.get(k, 0.0) or 0.0) for k in ['dinheiro','cartao_credito','cartao_debito','pix','outro']},
                        'saidas': {k: float(cont_s.get(k, 0.0) or 0.0) for k in ['dinheiro','cartao_credito','cartao_debito','pix','outro']},
                        **totais_cont}
        payload_esp  = {'entradas': e_ent, 'saidas': e_sai, **totais_esp}

        # Registrar na tabela de conferências e manter em memória para uso no fechamento
        self.financeiro_db.registrar_conferencia(
            sessao_id=self._sessao_id,
            usuario_id=usuario_id,
            contados=payload_cont,
            esperados=payload_esp,
            observacao=None,
        )

        # Retornar diferenças para eventual destaque em relatório
        dif = {
            'entradas': {k: payload_cont['entradas'][k] - e_ent.get(k, 0.0) for k in e_ent},
            'saidas': {k: payload_cont['saidas'][k] - e_sai.get(k, 0.0) for k in e_sai},
            'total_entradas': totais_cont['total_entradas'] - totais_esp['total_entradas'],
            'total_saidas': totais_cont['total_saidas'] - totais_esp['total_saidas'],
        }
        self._ultima_conferencia = {'contados': payload_cont, 'esperados': payload_esp, 'diferencas': dif}
        return self._ultima_conferencia

    # ----- Consultas do dia para facilitar lançamento -----
    def listar_consultas_do_dia(self, data_str: Optional[str] = None):
        """Lista consultas do dia (ou de uma data AAAA-MM-DD se informada)"""
        if not hasattr(self, 'financeiro_db'):
            return []
        return self.financeiro_db.listar_consultas_do_dia(data_str)

    # ----- Observação do fechamento (pós-fechamento pelo operador) -----
    def salvar_observacao_fechamento(self, observacao: Optional[str]) -> bool:
        """Salva a observação no resumo de fechamento para a última sessão fechada.
        Retorna True se atualizou, False caso não haja sessão fechada para associar."""
        try:
            if not self._ultima_sessao_fechada_id:
                return False
            self.financeiro_db.atualizar_observacao_fechamento(self._ultima_sessao_fechada_id, observacao)
            return True
        except Exception:
            return False

    def registrar_entrada(self, valor, descricao, tipo_entrada, **kwargs):
        """
        Registra um pagamento no sistema.
        
        Args:
            valor: Valor do pagamento
            descricao: Descrição do pagamento (opcional, apenas para log)
            tipo_entrada: Forma de pagamento (ex: 'dinheiro', 'cartao', 'pix')
            **kwargs: Argumentos adicionais (usuario_id, pedido_id, etc.)
            
        Returns:
            int: ID do pagamento registrado ou 0 em caso de erro
        """
        # Inicialização do registro de pagamento
        
        if not hasattr(self, 'financeiro_db') or not self.financeiro_db:
            error_msg = "Erro: Conexão com o banco de dados não configurada"
            pass
            return 0
            
        if 'pedido_id' not in kwargs:
            pass
            return 0
        
        try:
            pagamento_id = self.financeiro_db.registrar_entrada(
                valor=valor,
                descricao=descricao,
                tipo_entrada=tipo_entrada,
                **kwargs
            )
            
            if not pagamento_id:
                pass
                return 0
                
            pass
            return pagamento_id
            
        except Exception as e:
            pass
            import traceback
            traceback.print_exc()
            return 0
