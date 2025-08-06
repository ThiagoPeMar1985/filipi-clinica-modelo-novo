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
        
        # Tabela de usuários (mantida para autenticação do sistema)
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

        # Tabela: pacientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            nome TEXT NOT NULL,
            data_nascimento DATE,
            cpf VARCHAR(14) UNIQUE,
            telefone VARCHAR(20),
            email VARCHAR(255),
            endereco TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_paciente_cpf (cpf(14)),
            INDEX idx_paciente_nome (nome(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Tabela: medicos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT,
            crm VARCHAR(20) UNIQUE,
            telefone VARCHAR(20),
            email VARCHAR(255),
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_medico_crm (crm(20)),
            INDEX idx_medico_nome (nome(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Tabela: consultas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            paciente_id INTEGER NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL,
            status VARCHAR(50) DEFAULT 'agendada',
            observacoes TEXT,
            medico_id INTEGER NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medicos(id) ON DELETE CASCADE,
            INDEX idx_consulta_data (data),
            INDEX idx_consulta_medico (medico_id),
            INDEX idx_consulta_paciente (paciente_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Tabela: financeiro
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            consulta_id INTEGER,
            paciente_id INTEGER NOT NULL,
            data DATETIME NOT NULL,
            valor DECIMAL(10,2) NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            descricao TEXT,
            status VARCHAR(50) DEFAULT 'pendente',
            medico_id INTEGER,
            tipo_pagamento VARCHAR(50),
            data_pagamento DATETIME,
            FOREIGN KEY (consulta_id) REFERENCES consultas(id) ON DELETE SET NULL,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
            FOREIGN KEY (medico_id) REFERENCES medicos(id) ON DELETE SET NULL,
            INDEX idx_financeiro_data (data),
            INDEX idx_financeiro_paciente (paciente_id),
            INDEX idx_financeiro_consulta (consulta_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Tabela: modelos_texto (mantida para templates de documentos)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos_texto (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            nome VARCHAR(255) NOT NULL UNIQUE,
            conteudo TEXT NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_modelo_nome (nome(100))
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Tabela: prontuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prontuarios (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            paciente_id INTEGER NOT NULL,
            consulta_id INTEGER,
            data DATETIME NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            conteudo TEXT,
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE,
            FOREIGN KEY (consulta_id) REFERENCES consultas(id) ON DELETE SET NULL,
            INDEX idx_prontuario_paciente (paciente_id),
            INDEX idx_prontuario_consulta (consulta_id),
            INDEX idx_prontuario_data (data)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        connection.commit()
        print("Tabelas criadas com sucesso!")
        
    except Error as e:
        print(f"Erro ao criar tabelas: {e}")
        connection.rollback()
    finally:
        if cursor:
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
