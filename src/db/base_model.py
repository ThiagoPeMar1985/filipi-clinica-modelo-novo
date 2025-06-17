"""
Classe base para modelos de banco de dados.

Fornece funcionalidades comuns para todos os modelos que interagem com o banco de dados.
"""
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic
from datetime import datetime
import json

from .database import get_db

T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """Classe base para todos os modelos de banco de dados."""
    
    # Nome da tabela no banco de dados (deve ser sobrescrito pelas classes filhas)
    TABLE_NAME: str = None
    
    # Nome da chave primária (padrão: 'id')
    PRIMARY_KEY: str = 'id'
    
    # Lista de colunas que podem ser atualizadas (protegidas por padrão)
    UPDATABLE_FIELDS: List[str] = []
    
    def __init__(self, **kwargs):
        """Inicializa o modelo com os valores fornecidos."""
        self._db = get_db()
        
        # Define os atributos com base nos kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Cria uma instância do modelo a partir de um dicionário."""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para um dicionário."""
        return {
            key: self._serialize_value(value)
            for key, value in self.__dict__.items()
            if not key.startswith('_')
        }
    
    def _serialize_value(self, value: Any) -> Any:
        """Serializa valores para formato compatível com JSON."""
        if isinstance(value, datetime):
            return value.isoformat()
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        return value
    
    def save(self) -> bool:
        """Salva o modelo no banco de dados (insere ou atualiza)."""
        data = self.to_dict()
        
        # Remove a chave primária se for None (para INSERT)
        if self.PRIMARY_KEY in data and data[self.PRIMARY_KEY] is None:
            del data[self.PRIMARY_KEY]
        
        if hasattr(self, self.PRIMARY_KEY) and getattr(self, self.PRIMARY_KEY) is not None:
            # Atualização
            pk_value = getattr(self, self.PRIMARY_KEY)
            return self.update(pk_value, data)
        else:
            # Inserção
            return self.insert(data)
    
    @classmethod
    def insert(cls, data: Dict[str, Any]) -> bool:
        """Insere um novo registro no banco de dados."""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME não definido para o modelo")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {cls.TABLE_NAME} ({columns}) VALUES ({placeholders})"
        
        try:
            db = get_db()
            result = db.execute_query(query, tuple(data.values()))
            return result is not None
        except Exception as e:
            print(f"Erro ao inserir registro: {e}")
            return False
    
    @classmethod
    def update(cls, pk_value: Any, data: Dict[str, Any]) -> bool:
        """Atualiza um registro existente no banco de dados."""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME não definido para o modelo")
        
        # Filtra apenas os campos atualizáveis
        if cls.UPDATABLE_FIELDS:
            data = {k: v for k, v in data.items() if k in cls.UPDATABLE_FIELDS}
        
        if not data:
            return False
            
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"""
            UPDATE {cls.TABLE_NAME}
            SET {set_clause}
            WHERE {cls.PRIMARY_KEY} = %s
        """
        
        try:
            db = get_db()
            params = list(data.values()) + [pk_value]
            result = db.execute_query(query, tuple(params))
            return result is not None
        except Exception as e:
            print(f"Erro ao atualizar registro: {e}")
            return False
    
    @classmethod
    def delete(cls, pk_value: Any) -> bool:
        """Remove um registro do banco de dados."""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME não definido para o modelo")
            
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE {cls.PRIMARY_KEY} = %s"
        
        try:
            db = get_db()
            result = db.execute_query(query, (pk_value,))
            return result is not None
        except Exception as e:
            print(f"Erro ao remover registro: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, pk_value: Any) -> Optional[T]:
        """Busca um registro pelo ID."""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME não definido para o modelo")
            
        query = f"SELECT * FROM {cls.TABLE_NAME} WHERE {cls.PRIMARY_KEY} = %s"
        
        try:
            db = get_db()
            result = db.execute_query(query, (pk_value,), fetch_all=False)
            return cls.from_dict(result) if result else None
        except Exception as e:
            print(f"Erro ao buscar registro: {e}")
            return None
    
    @classmethod
    def get_all(cls, limit: int = 100, offset: int = 0) -> List[T]:
        """Busca todos os registros da tabela."""
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME não definido para o modelo")
            
        query = f"SELECT * FROM {cls.TABLE_NAME} LIMIT %s OFFSET %s"
        
        try:
            db = get_db()
            results = db.execute_query(query, (limit, offset)) or []
            return [cls.from_dict(row) for row in results]
        except Exception as e:
            print(f"Erro ao buscar registros: {e}")
            return []
    
    def __str__(self) -> str:
        """Representação em string do modelo."""
        return f"<{self.__class__.__name__} {self.to_dict()}>"
    
    def __repr__(self) -> str:
        """Representação oficial do objeto."""
        return str(self)
