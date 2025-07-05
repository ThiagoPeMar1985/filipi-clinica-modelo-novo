"""
Controlador para o módulo de Delivery.
"""
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path para importações
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

class DeliveryController:
    """Controlador para operações do módulo de Delivery."""
    
    def __init__(self, view=None):
        """Inicializa o controlador com a view opcional."""
        self.view = view
        # Inicializar o banco de dados
        from src.db.database import DatabaseConnection
        self.db = DatabaseConnection().get_connection()
        
        # Criar a tabela de regiões de entrega se não existir
        self._criar_tabela_regioes_entrega()
    
    def _criar_tabela_regioes_entrega(self):
        """Cria a tabela de regiões de entrega se não existir."""
        query = """
        CREATE TABLE IF NOT EXISTS regioes_entrega (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            taxa_entrega DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            tempo_medio_entrega INT NOT NULL DEFAULT 30,
            ativo TINYINT(1) NOT NULL DEFAULT 1,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(query)
        self.db.commit()
        cursor.close()
    
    def listar_regioes_entrega(self, ativo=None):
        """Lista todas as regiões de entrega.
        
        Args:
            ativo (bool, optional): Filtrar por status ativo/inativo. Defaults to None.
            
        Returns:
            list: Lista de dicionários com as regiões de entrega
        """
        query = "SELECT * FROM regioes_entrega"
        params = []
        
        if ativo is not None:
            query += " WHERE ativo = %s"
            params.append(1 if ativo else 0)
            
        query += " ORDER BY nome"
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def obter_regiao_por_id(self, regiao_id):
        """Obtém uma região de entrega pelo ID.
        
        Args:
            regiao_id (int): ID da região de entrega
            
        Returns:
            dict or None: Dados da região ou None se não encontrada
        """
        query = "SELECT * FROM regioes_entrega WHERE id = %s"
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(query, (regiao_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def salvar_regiao_entrega(self, dados):
        """Salva uma nova região de entrega ou atualiza uma existente.
        
        Args:
            dados (dict): Dados da região de entrega
            
        Returns:
            int: ID da região salva
        """
        if 'id' in dados and dados['id']:
            # Atualizar região existente
            query = """
            UPDATE regioes_entrega 
            SET nome = %s, 
                taxa_entrega = %s, 
                tempo_medio_entrega = %s, 
                ativo = %s,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            params = (
                dados['nome'],
                float(dados['taxa_entrega']),
                int(dados['tempo_medio_entrega']),
                1 if dados.get('ativo', True) else 0,
                dados['id']
            )
            cursor = self.db.cursor()
            cursor.execute(query, params)
            self.db.commit()
            cursor.close()
            return dados['id']
        else:
            # Inserir nova região
            query = """
            INSERT INTO regioes_entrega (nome, taxa_entrega, tempo_medio_entrega, ativo)
            VALUES (%s, %s, %s, %s)
            """
            params = (
                dados['nome'],
                float(dados['taxa_entrega']),
                int(dados['tempo_medio_entrega']),
                1 if dados.get('ativo', True) else 0
            )
            cursor = self.db.cursor()
            cursor.execute(query, params)
            self.db.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
    
    def excluir_regiao_entrega(self, regiao_id):
        """Exclui uma região de entrega.
        
        Args:
            regiao_id (int): ID da região a ser excluída
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        try:
            query = "DELETE FROM regioes_entrega WHERE id = %s"
            cursor = self.db.cursor()
            cursor.execute(query, (regiao_id,))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Erro ao excluir região de entrega: {e}")
            return False
    
    def obter_regiao_por_bairro(self, bairro):
        """Obtém a região de entrega com base no bairro.
        
        Args:
            bairro (str): Nome do bairro
            
        Returns:
            dict or None: Dados da região ou None se não encontrada
        """
        if not bairro:
            return None
            
        # Aqui você pode implementar a lógica para mapear bairros para regiões
        # Por enquanto, vamos retornar a primeira região ativa
        regioes = self.listar_regioes_entrega(ativo=True)
        return regioes[0] if regioes else None
    
    def configurar_view(self, view):
        """Configura a view para este controlador."""
        self.view = view
