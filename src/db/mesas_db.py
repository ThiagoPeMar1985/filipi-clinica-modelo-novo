"""
Módulo para operações de banco de dados do módulo de Mesas.
e pode vai usar essas tabelas que estão no banco de dados 

Tabela: mesas
Columns:
id int AI PK 
numero int 
status varchar(20) 
capacidade int 
pedido_id int 
pedido_atual_id int

Tabela: pedidos
Columns:
id int AI PK 
mesa_id int 
data_abertura datetime 
data_fechamento datetime 
status varchar(20) 
total decimal(10,2) 
garcom_id int 
tipo enum('MESA','AVULSO','DELIVERY') 
cliente_id int 
cliente_nome varchar(255) 
cliente_telefone varchar(20) 
cliente_endereco text 
entregador_id int 
tipo_cliente varchar(20) 
regiao_id int 
taxa_entrega decimal(10,2) 
observacao text 
previsao_entrega datetime 
data_entrega datetime 
status_entrega varchar(50) 
processado_estoque tinyint(1)

"""
from typing import Dict, List, Any, Optional

class MesasDB:
    """Classe para operações de banco de dados do módulo de Mesas."""
    
    def __init__(self, db_connection):
        """Inicializa com uma conexão de banco de dados."""
        self.db = db_connection
