"""
Inicializador do banco de dados.

Este módulo contém as funções para criar e inicializar o banco de dados
e suas tabelas, caso não existam.
"""
import os
import mysql.connector
from mysql.connector import Error
from .config import get_db_config

def criar_tabelas(connection):
    """Cria as tabelas do banco de dados se não existirem.
    
    Args:
        connection: Conexão ativa com o banco de dados MySQL.
    """
    try:
        cursor = connection.cursor()
        
        # Tabela de usuários
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            login VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            nivel VARCHAR(50) NOT NULL,
            telefone VARCHAR(20)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de regiões de entrega
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS regioes_entrega (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            taxa_entrega DECIMAL(10,2) NOT NULL,
            tempo_medio_entrega INT NOT NULL,
            ativo TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de produtos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descricao TEXT,
            tipo VARCHAR(50) NOT NULL,
            preco_compra DECIMAL(10,2) NOT NULL,
            preco_venda DECIMAL(10,2) NOT NULL,
            unidade_medida VARCHAR(10) NOT NULL,
            quantidade_minima DECIMAL(10,2) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de receita dos produtos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS receita_produto (
            id INT AUTO_INCREMENT PRIMARY KEY,
            produto_id INT NOT NULL,
            ingrediente_id INT NOT NULL,
            quantidade DECIMAL(10,2) NOT NULL,
            unidade_medida VARCHAR(10) NOT NULL,
            custo_unitario DECIMAL(10,2) NOT NULL,
            custo_total DECIMAL(10,2) NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        
        # Tabela de pedidos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mesa_id INT,
            data_abertura DATETIME NOT NULL,
            data_fechamento DATETIME,
            status VARCHAR(20) NOT NULL,
            total DECIMAL(10,2) DEFAULT 0.00,
            usuario_id INT,
            tipo ENUM('MESA','AVULSO','DELIVERY') NOT NULL,
            cliente_id INT,
            cliente_nome VARCHAR(255),
            cliente_telefone VARCHAR(20),
            cliente_endereco TEXT,
            entregador_id INT,
            tipo_cliente VARCHAR(20),
            regiao_id INT,
            taxa_entrega DECIMAL(10,2) DEFAULT 0.00,
            observacao TEXT,
            previsao_entrega DATETIME,
            data_entrega DATETIME,
            status_entrega VARCHAR(50),
            processado_estoque TINYINT(1) DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de pagamentos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT NOT NULL,
            forma_pagamento VARCHAR(50) NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            data_hora DATETIME NOT NULL,
            tipo_venda ENUM('avulso', 'delivery', 'mesa'),
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de movimentações de caixa
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes_caixa (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50) NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            descricao TEXT,
            data_hora DATETIME NOT NULL,
            usuario_id INT NOT NULL,
            forma_pagamento VARCHAR(50),
            status VARCHAR(20) DEFAULT 'pendente',
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de mesas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero INT UNIQUE NOT NULL,
            status VARCHAR(20) DEFAULT 'livre',
            capacidade INT NOT NULL,
            pedido_id INT,
            pedido_atual_id INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de itens do pedido
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT NOT NULL,
            produto_id INT NOT NULL,
            quantidade INT NOT NULL,
            valor_unitario DECIMAL(10,2) NOT NULL,
            subtotal DECIMAL(10,2) NOT NULL,
            observacao TEXT,
            usuario_id INT,
            data_hora DATETIME NOT NULL,
            valor_total DECIMAL(10,2) NOT NULL,
            observacoes TEXT,
            status VARCHAR(20) DEFAULT 'pendente',
            data_hora_preparo DATETIME,
            data_hora_pronto DATETIME,
            data_hora_entregue DATETIME,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        
        # Tabela de funcionários
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            idade VARCHAR(10),
            cpf VARCHAR(14) UNIQUE,
            cargo VARCHAR(100) NOT NULL,
            telefone VARCHAR(20),
            endereco TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de fornecedores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            empresa VARCHAR(255) NOT NULL,
            vendedor VARCHAR(255),
            produtos TEXT,
            telefone VARCHAR(20),
            email VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de estoque
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INT AUTO_INCREMENT PRIMARY KEY,
            produto_id INT NOT NULL,
            quantidade DECIMAL(10,2) NOT NULL,
            data_entrada DATE NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de entregadores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entregadores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            telefone VARCHAR(20) NOT NULL,
            veiculo VARCHAR(100) NOT NULL,
            placa VARCHAR(15) NOT NULL,
            ativo TINYINT(1) DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de entradas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entradas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pedido_id INT,
            mesa_numero INT,
            usuario_id INT,
            usuario_nome VARCHAR(255),
            itens TEXT,
            valor DECIMAL(10,2) NOT NULL,
            data_hora DATETIME NOT NULL,
            tipo_pagamento VARCHAR(50),
            status VARCHAR(20) DEFAULT 'pendente',
            descricao TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de empresas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_fantasia VARCHAR(255) NOT NULL,
            razao_social VARCHAR(255) NOT NULL,
            cnpj VARCHAR(20) UNIQUE,
            inscricao_estadual VARCHAR(50),
            telefone VARCHAR(20),
            endereco TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de contas a receber
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_receber (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cliente_id INT NOT NULL,
            cliente_nome VARCHAR(255) NOT NULL,
            descricao TEXT,
            valor DECIMAL(10,2) NOT NULL,
            valor_pago DECIMAL(10,2) DEFAULT 0.00,
            data_vencimento DATE NOT NULL,
            data_pagamento DATE,
            status VARCHAR(20) DEFAULT 'pendente',
            forma_pagamento VARCHAR(50),
            observacoes TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_id INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # Tabela de contas a pagar
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_a_pagar (
            id INT AUTO_INCREMENT PRIMARY KEY,
            descricao TEXT,
            valor DECIMAL(10,2) NOT NULL,
            data_vencimento DATE NOT NULL,
            data_pagamento DATE,
            pago TINYINT(1) DEFAULT 0,
            tipo_pagamento VARCHAR(50),
            usuario_id INT,
            recorrente TINYINT(1) DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        
        # Tabela de clientes delivery
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_delivery (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            telefone VARCHAR(20) NOT NULL,
            telefone2 VARCHAR(20),
            email VARCHAR(255),
            endereco TEXT NOT NULL,
            numero VARCHAR(20) NOT NULL,
            complemento TEXT,
            bairro VARCHAR(100) NOT NULL,
            cidade VARCHAR(100) NOT NULL,
            uf CHAR(2) NOT NULL,
            cep VARCHAR(10),
            ponto_referencia TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            ativo TINYINT(1) DEFAULT 1,
            observacoes TEXT,
            regiao_entrega_id INT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        connection.commit()
        print("Banco de dados inicializado com sucesso!")
        
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")
        connection.rollback()
    finally:
        cursor.close()

def verificar_e_criar_banco():
    """Verifica se o banco de dados existe e o cria se necessário."""
    try:
        # Obtém as configurações de conexão sem especificar o banco de dados
        config = get_db_config('development')
        db_name = config['database']
        
        # Remove o nome do banco de dados da configuração para conectar ao servidor
        config_sem_db = config.copy()
        config_sem_db.pop('database', None)
        
        # Conecta ao servidor MySQL
        connection = mysql.connector.connect(**config_sem_db)
        cursor = connection.cursor()
        
        # Verifica se o banco de dados existe
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        resultado = cursor.fetchone()
        
        if not resultado:
            # Cria o banco de dados se não existir
            cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Banco de dados '{db_name}' criado com sucesso!")
        
        cursor.close()
        connection.close()
        
        # Agora conecta ao banco de dados específico
        connection = mysql.connector.connect(**config)
        
        # Cria as tabelas
        criar_tabelas(connection)
        
        return True
        
    except Error as e:
        print(f"Erro ao verificar/criar banco de dados: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    # Executa a verificação e criação do banco de dados quando o script é executado diretamente
    verificar_e_criar_banco()
