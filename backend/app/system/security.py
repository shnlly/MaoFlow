# import os
# from typing import Tuple, Optional
# from datetime import datetime, timedelta
# from base64 import b64encode, b64decode
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import padding
# from passlib.context import CryptContext
# from jose import JWTError, jwt
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
#
# from core.config import get_settings
# settings = get_settings()
# from core.exceptions import UnauthorizedError, ForbiddenError
# from .schemas.user import TokenPayload
#
# # 密码加密上下文
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
#
# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """验证密码"""
#     return pwd_context.verify(plain_password, hashed_password)
#
# def get_password_hash(password: str) -> str:
#     """获取密码哈希"""
#     return pwd_context.hash(password)
#
# def create_access_token(
#     subject: str,
#     is_superuser: bool = False,
#     roles: list = None,
#     permissions: list = None,
#     expires_delta: Optional[timedelta] = None
# ) -> str:
#     """创建访问令牌"""
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(
#             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#         )
#
#     to_encode = {
#         "sub": subject,
#         "exp": expire.timestamp(),
#         "is_superuser": is_superuser,
#         "roles": roles or [],
#         "permissions": permissions or []
#     }
#     encoded_jwt = jwt.encode(
#         to_encode,
#         settings.SECRET_KEY,
#         algorithm="HS256"
#     )
#     return encoded_jwt
#
# async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
#     """获取当前用户"""
#     try:
#         payload = jwt.decode(
#             token,
#             settings.SECRET_KEY,
#             algorithms=["HS256"]
#         )
#         token_data = TokenPayload(**payload)
#
#         # 检查令牌是否过期
#         if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
#             raise UnauthorizedError("Token has expired")
#
#         return {
#             "user_id": token_data.sub,
#             "is_superuser": token_data.is_superuser,
#             "roles": token_data.roles,
#             "permissions": token_data.permissions
#         }
#     except JWTError:
#         raise UnauthorizedError("Could not validate credentials")
#
# async def require_super_admin(current_user: dict = Depends(get_current_user)) -> dict:
#     """要求超级管理员权限"""
#     if not current_user.get("is_superuser"):
#         raise ForbiddenError("Super admin privileges required")
#     return current_user
#
# async def check_permission(permission: str, current_user: dict = Depends(get_current_user)) -> dict:
#     """检查特定权限"""
#     if current_user.get("is_superuser"):
#         return current_user
#
#     if permission not in current_user.get("permissions", []):
#         raise ForbiddenError(f"Permission {permission} required")
#     return current_user
#
# async def check_role(role: str, current_user: dict = Depends(get_current_user)) -> dict:
#     """检查特定角色"""
#     if current_user.get("is_superuser"):
#         return current_user
#
#     if role not in current_user.get("roles", []):
#         raise ForbiddenError(f"Role {role} required")
#     return current_user
#
# # 加密相关函数（保持原有实现）
# def _get_encryption_key() -> bytes:
#     """获取加密密钥"""
#     key = getattr(settings, 'ENCRYPTION_KEY', None)
#     if not key:
#         key = getattr(settings, 'SECRET_KEY', 'your-secret-key-please-change-in-production')
#
#     key_bytes = key.encode('utf-8')
#     return key_bytes[:32].ljust(32, b'\0')
#
# def encrypt_text(text: str) -> Tuple[str, str]:
#     """加密文本"""
#     if not text:
#         return "", ""
#
#     iv = os.urandom(16)
#     key = _get_encryption_key()
#
#     cipher = Cipher(
#         algorithms.AES(key),
#         modes.CBC(iv),
#         backend=default_backend()
#     )
#     encryptor = cipher.encryptor()
#
#     padder = padding.PKCS7(128).padder()
#     padded_data = padder.update(text.encode('utf-8')) + padder.finalize()
#
#     encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
#
#     encrypted_text = b64encode(encrypted_data).decode('utf-8')
#     iv_text = b64encode(iv).decode('utf-8')
#
#     return encrypted_text, iv_text
#
# def decrypt_text(encrypted_text: str, iv_text: str) -> str:
#     """解密文本"""
#     if not encrypted_text or not iv_text:
#         return ""
#
#     try:
#         encrypted_data = b64decode(encrypted_text)
#         iv = b64decode(iv_text)
#         key = _get_encryption_key()
#
#         cipher = Cipher(
#             algorithms.AES(key),
#             modes.CBC(iv),
#             backend=default_backend()
#         )
#         decryptor = cipher.decryptor()
#
#         padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
#
#         unpadder = padding.PKCS7(128).unpadder()
#         data = unpadder.update(padded_data) + unpadder.finalize()
#
#         return data.decode('utf-8')
#     except Exception as e:
#         print(f"Decryption error: {str(e)}")
#         return ""