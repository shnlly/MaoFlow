import os
from typing import Tuple
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from .config import Settings

def _get_encryption_key() -> bytes:
    """获取加密密钥"""
    # 从环境变量或配置中获取密钥，如果没有则使用默认值
    key = getattr(Settings, 'ENCRYPTION_KEY', None)
    if not key:
        # 使用 UUID 作为默认密钥的一部分
        key = getattr(Settings, 'SECRET_KEY', 'your-secret-key-please-change-in-production')
    
    # 确保密钥长度为32字节(256位)
    key_bytes = key.encode('utf-8')
    return key_bytes[:32].ljust(32, b'\0')

def encrypt_text(text: str) -> Tuple[str, str]:
    """
    加密文本
    
    Args:
        text: 要加密的文本
    
    Returns:
        Tuple[str, str]: (加密后的文本, IV)，都是base64编码的字符串
    """
    if not text:
        return "", ""
    
    # 生成随机IV
    iv = os.urandom(16)
    key = _get_encryption_key()
    
    # 创建加密器
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # 添加填充
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(text.encode('utf-8')) + padder.finalize()
    
    # 加密
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # 转换为base64
    encrypted_text = b64encode(encrypted_data).decode('utf-8')
    iv_text = b64encode(iv).decode('utf-8')
    
    return encrypted_text, iv_text

def decrypt_text(encrypted_text: str, iv_text: str) -> str:
    """
    解密文本
    
    Args:
        encrypted_text: base64编码的加密文本
        iv_text: base64编码的IV
    
    Returns:
        str: 解密后的文本
    """
    if not encrypted_text or not iv_text:
        return ""
    
    try:
        # 解码base64
        encrypted_data = b64decode(encrypted_text)
        iv = b64decode(iv_text)
        key = _get_encryption_key()
        
        # 创建解密器
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # 解密
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode('utf-8')
    except Exception as e:
        # 记录错误但返回空字符串，避免在解密失败时暴露错误详情
        print(f"Decryption error: {str(e)}")  # 在生产环境中应该使用proper logging
        return "" 