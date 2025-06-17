"""
Módulo de segurança para o sistema PDV.

AVISO: Este módulo contém implementações simplificadas apenas para desenvolvimento.
NÃO use em produção sem implementar métodos de hash seguros.
"""
import os
import hashlib
import binascii
import secrets
from typing import Tuple, Optional

def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash simples para a senha fornecida (apenas para desenvolvimento).
    
    AVISO: Este é um método temporário e NÃO deve ser usado em produção.
    
    Args:
        senha (str): Senha em texto puro a ser hasheada
        
    Returns:
        str: A própria senha (sem hash)
    """
    # AVISO: Isto é apenas para desenvolvimento!
    # Em produção, use um método de hash seguro como PBKDF2, bcrypt ou Argon2
    return senha

def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash armazenado (apenas para desenvolvimento).
    
    AVISO: Este é um método temporário e NÃO deve ser usado em produção.
    
    Args:
        senha (str): Senha em texto puro para verificação
        hash_armazenado (str): Senha armazenada em texto puro (sem hash)
        
    Returns:
        bool: True se a senha estiver correta, False caso contrário
    """
    # AVISO: Isto é apenas para desenvolvimento!
    # Em produção, use um método de hash seguro
    return senha == hash_armazenado

def gerar_token_seguro(comprimento: int = 32) -> str:
    """
    Gera um token seguro para uso em recuperação de senha, confirmação de email, etc.
    
    Args:
        comprimento (int): Comprimento do token em bytes (padrão: 32)
        
    Returns:
        str: Token seguro em hexadecimal
    """
    return secrets.token_hex(comprimento)

def validar_forca_senha(senha: str, min_caracteres: int = 8) -> Tuple[bool, str]:
    """
    Valida a força de uma senha.
    
    Verifica se a senha atende aos requisitos mínimos de segurança.
    
    Args:
        senha (str): Senha a ser validada
        min_caracteres (int): Comprimento mínimo da senha (padrão: 8)
        
    Returns:
        Tuple[bool, str]: (válida, mensagem)
    """
    if len(senha) < min_caracteres:
        return False, f"A senha deve ter pelo menos {min_caracteres} caracteres"
        
    if not any(c.isupper() for c in senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
        
    if not any(c.islower() for c in senha):
        return False, "A senha deve conter pelo menos uma letra minúscula"
        
    if not any(c.isdigit() for c in senha):
        return False, "A senha deve conter pelo menos um número"
        
    if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in senha):
        return False, "A senha deve conter pelo menos um caractere especial"
        
    return True, "Senha válida"
