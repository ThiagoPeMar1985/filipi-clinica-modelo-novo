"""
Controlador para o módulo Financeiro.
"""
from db.financeiro_db import FinanceiroDB

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
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
    
    def set_db_connection(self, db_connection):
        """Permite configurar/trocar a conexão de DB após a criação."""
        self.db_connection = db_connection
        self.financeiro_db = FinanceiroDB(db_connection)
        self._sessao_id = None

    # ----- Caixa (Sessão) -----
    def get_sessao_aberta(self):
        if not hasattr(self, 'financeiro_db'):
            return None
        sessao = self.financeiro_db.get_caixa_aberto()
        if sessao:
            self._sessao_id = sessao['id']
        return sessao

    def abrir_caixa(self, valor_inicial: float, usuario_id: int | None = None, observacao: str | None = None) -> int:
        if not hasattr(self, 'financeiro_db'):
            return 0
        sessao_id = self.financeiro_db.abrir_caixa(valor_inicial, usuario_id, observacao)
        self._sessao_id = sessao_id
        return sessao_id

    def registrar_movimento(self, tipo: str, forma: str, valor: float, descricao: str = "", usuario_id: int | None = None) -> int:
        if not hasattr(self, 'financeiro_db'):
            return 0
        # Garante uma sessão aberta
        if not self._sessao_id:
            sessao = self.get_sessao_aberta()
            if not sessao:
                return 0
        return self.financeiro_db.registrar_movimento(self._sessao_id, tipo, forma, valor, descricao, usuario_id)

    def listar_movimentos(self):
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return []
        return self.financeiro_db.listar_movimentos(self._sessao_id)

    def fechar_caixa(self, usuario_id: int | None = None):
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return None
        # Resumo antes de fechar
        resumo = self.financeiro_db.resumo_sessao(self._sessao_id)
        self.financeiro_db.fechar_caixa(self._sessao_id, usuario_id)
        self._sessao_id = None
        return resumo

    def resumo_sessao(self):
        if not hasattr(self, 'financeiro_db') or not self._sessao_id:
            return None
        return self.financeiro_db.resumo_sessao(self._sessao_id)
        
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
