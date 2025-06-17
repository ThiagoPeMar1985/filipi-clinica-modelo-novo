# Módulo de Banco de Dados

Este módulo fornece uma camada de abstração para interação com o banco de dados MySQL do sistema PDV.

## Estrutura

- `__init__.py`: Torna o diretório um pacote Python
- `config.py`: Configurações de conexão com o banco de dados
- `database.py`: Classe principal para gerenciamento de conexões e execução de consultas
- `base_model.py`: Classe base para todos os modelos de banco de dados
- `init_db.py`: Script para inicialização do banco de dados e criação das tabelas

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis de ambiente:

```ini
# Configurações do Banco de Dados
DB_HOST=localhost
DB_PORT=3306
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=pdv_aquarius

# Configurações do Pool de Conexões
DB_POOL_NAME=pdv_pool
DB_POOL_SIZE=5
```

## Inicialização do Banco de Dados

Para criar o banco de dados e as tabelas necessárias, execute:

```bash
python -m src.db.init_db
```

## Uso Básico

### Classe BaseModel

Todas as classes de modelo devem herdar de `BaseModel`:

```python
from src.db.base_model import BaseModel

class MeuModelo(BaseModel):
    TABLE_NAME = 'minha_tabela'
    PRIMARY_KEY = 'id'
    UPDATABLE_FIELDS = ['campo1', 'campo2']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.campo1 = kwargs.get('campo1')
        self.campo2 = kwargs.get('campo2')
```

### Operações CRUD

```python
# Criar instância
modelo = MeuModelo(campo1='valor1', campo2='valor2')

# Salvar (INSERT ou UPDATE)
modelo.save()

# Buscar por ID
modelo = MeuModelo.get_by_id(1)

# Buscar todos os registros
registros = MeuModelo.get_all()

# Deletar
modelo.delete()
```

### Executando Consultas Personalizadas

```python
from src.db.database import get_db

db = get_db()

# Consulta com parâmetros
resultados = db.execute_query(
    "SELECT * FROM minha_tabela WHERE campo1 = %s AND ativo = %s",
    ('valor1', True),
    fetch_all=True
)

# Inserir/Atualizar/Deletar
db.execute_query("UPDATE minha_tabela SET campo1 = %s WHERE id = %s", ('novo_valor', 1))
```

## Boas Práticas

1. Sempre use parâmetros em consultas SQL para evitar injeção SQL
2. Utilize transações para operações que envolvam múltiplas consultas
3. Feche sempre as conexões após o uso (usando `with` ou chamando `close()`)
4. Use os métodos fornecidos pela `BaseModel` sempre que possível
5. Mantenha as migrações de banco de dados versionadas

## Migrações

Para alterações no esquema do banco de dados, cire scripts de migração numerados:

```
db/
  migrations/
    0001_initial_schema.sql
    0002_add_novo_campo.sql
```

Execute as migrações em ordem para atualizar o esquema do banco de dados.
