"""
Modelo de Usuário do sistema
"""
from datetime import datetime
from src.db.base_model import BaseModel

class Usuario(BaseModel):
    """Classe que representa um usuário do sistema"""
    
    # Nome da tabela no banco de dados
    TABLE_NAME = 'usuarios'
    
    # Lista de campos que podem ser atualizados
    UPDATABLE_FIELDS = ['nome', 'login', 'senha', 'nivel', 'telefone']
    
    def __init__(self, id=None, nome=None, login=None, senha=None, 
                 nivel='usuario', telefone=None, **kwargs):
        """Inicializa um novo usuário"""
        super().__init__(**kwargs)
        self.id = id
        self.nome = nome
        self.login = login
        self.senha = senha
        self.nivel = nivel  # 'admin', 'gerente', 'caixa', 'garcom', 'usuario'
        self.telefone = telefone
    
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância de Usuario a partir de um dicionário"""
        return cls(
            id=data.get('id'),
            nome=data.get('nome'),
            login=data.get('login'),
            senha=data.get('senha'),
            nivel=data.get('nivel', 'usuario'),
            telefone=data.get('telefone')
        )
    
    def to_dict(self):
        """Retorna os dados do usuário como um dicionário"""
        data = super().to_dict()
        # Remove a senha por segurança
        data.pop('senha', None)
        return data
    
    
        
     
    
    @classmethod
    def autenticar(cls, login: str, senha: str):
        """
        Autentica um usuário com base no login e senha
        
        Args:
            login (str): Login do usuário
            senha (str): Senha em texto puro
            
        Returns:
            Usuario: Instância do usuário autenticado ou None se falhar
        """
        from src.db.database import get_db
        
        # Busca o usuário pelo login
        db = get_db()
        cursor = db.get_connection().cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM usuarios WHERE login = %s", (login,))
            result = cursor.fetchone()
            
            if not result:
                return None
                
            # Cria uma instância do usuário
            usuario = cls.from_dict(result)
            
            # Verifica a senha (comparação direta pois não há hash no banco)
            if senha == usuario.senha:
                return usuario
                
            return None
            
        finally:
            cursor.close()
    
    def alterar_senha(self, nova_senha: str):
        """
        Altera a senha do usuário
        
        Args:
            nova_senha (str): Nova senha em texto puro (será convertida para hash)
        """
        from src.utils.security import gerar_hash_senha
        self.senha_hash = gerar_hash_senha(nova_senha)
        self.save()
    
    @classmethod
    def buscar_por_login(cls, login: str):
        """
        Busca um usuário pelo login
        
        Args:
            login (str): Login do usuário a ser buscado
            
        Returns:
            Usuario: Instância do usuário ou None se não encontrado
        """
        db = cls.get_db()
        query = "SELECT * FROM usuarios WHERE login = %s"
        result = db.execute_query(query, (login,), fetch_all=False)
        
        if result:
            return cls.from_dict(result)
        return None
