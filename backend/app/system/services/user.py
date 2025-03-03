# from typing import Optional, Tuple, List, Dict, Any
# from datetime import datetime
# from sqlalchemy import select, or_, func
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.exc import IntegrityError
#
# from core.exceptions import ValidationError, NotFoundException
# # from app.system.security import get_password_hash, verify_password, create_access_token
# from ..models.user import User
# from ..schemas.user import (
#     UserCreate, UserUpdate, Token, UserInDB,
#     UserSettings, SystemStats
# )
#
# class UserService:
#     def __init__(self, session: AsyncSession):
#         self.session = session
#
#     async def create(self, data: UserCreate) -> User:
#         """创建用户"""
#         # 检查用户名和邮箱是否已存在
#         existing = await self.session.execute(
#             select(User).where(
#                 or_(
#                     User.username == data.username,
#                     User.email == data.email
#                 )
#             )
#         )
#         if existing.scalar_one_or_none():
#             raise ValidationError("Username or email already exists")
#
#         # 创建用户
#         user = User(
#             **data.model_dump(exclude={'password'}),
#             hashed_password=get_password_hash(data.password)
#         )
#         self.session.add(user)
#         try:
#             await self.session.commit()
#         except IntegrityError:
#             await self.session.rollback()
#             raise ValidationError("Failed to create user")
#
#         return user
#
#     async def authenticate(self, username: str, password: str) -> Optional[Token]:
#         """用户认证"""
#         # 查找用户
#         user = await self.session.execute(
#             select(User).where(
#                 or_(
#                     User.username == username,
#                     User.email == username
#                 )
#             )
#         )
#         user = user.scalar_one_or_none()
#
#         if not user or not verify_password(password, user.hashed_password):
#             return None
#
#         if not user.is_active:
#             raise ValidationError("User is inactive")
#
#         # 更新登录信息
#         user.last_login_at = datetime.utcnow().isoformat()
#         await self.session.commit()
#
#         # 创建访问令牌
#         access_token = create_access_token(
#             subject=str(user.id),
#             is_superuser=user.is_superuser,
#             roles=user.roles,
#             permissions=user.permissions
#         )
#
#         return Token(
#             access_token=access_token,
#             token_type="bearer",
#             expires_in=3600 * 24,  # 24小时
#             user=UserInDB.model_validate(user)
#         )
#
#     async def get(self, user_id: str) -> User:
#         """获取用户"""
#         user = await self.session.get(User, user_id)
#         if not user:
#             raise NotFoundException(f"User {user_id} not found")
#         return user
#
#     async def list(
#         self,
#         skip: int = 0,
#         limit: int = 10,
#         is_active: Optional[bool] = None
#     ) -> Tuple[List[User], int]:
#         """获取用户列表"""
#         query = select(User)
#
#         if is_active is not None:
#             query = query.filter(User.is_active == is_active)
#
#         # 获取总数
#         total = await self.session.scalar(
#             select(func.count()).select_from(query.subquery())
#         )
#
#         # 获取分页数据
#         query = query.order_by(User.created_at.desc())
#         query = query.offset(skip).limit(limit)
#         result = await self.session.execute(query)
#         users = result.scalars().all()
#
#         return list(users), total
#
#     async def update(self, user_id: str, data: UserUpdate) -> User:
#         """更新用户"""
#         user = await self.get(user_id)
#
#         # 更新密码
#         if data.password:
#             data.hashed_password = get_password_hash(data.password)
#             delattr(data, 'password')
#
#         # 更新设置
#         if data.settings:
#             user.update_settings(data.settings)
#             delattr(data, 'settings')
#
#         # 更新其他字段
#         update_data = data.model_dump(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(user, key, value)
#
#         try:
#             await self.session.commit()
#         except IntegrityError:
#             await self.session.rollback()
#             raise ValidationError("Username or email already exists")
#
#         return user
#
#     async def delete(self, user_id: str) -> None:
#         """删除用户"""
#         user = await self.get(user_id)
#         await self.session.delete(user)
#         await self.session.commit()
#
#     async def update_password(
#         self,
#         user_id: str,
#         old_password: str,
#         new_password: str
#     ) -> None:
#         """更新密码"""
#         user = await self.get(user_id)
#
#         # 验证旧密码
#         if not verify_password(old_password, user.hashed_password):
#             raise ValidationError("Invalid old password")
#
#         # 更新密码
#         user.hashed_password = get_password_hash(new_password)
#         await self.session.commit()
#
#     async def get_by_username_or_email(self, username_or_email: str) -> Optional[User]:
#         """通过用户名或邮箱获取用户"""
#         result = await self.session.execute(
#             select(User).where(
#                 or_(
#                     User.username == username_or_email,
#                     User.email == username_or_email
#                 )
#             )
#         )
#         return result.scalar_one_or_none()
#
#     async def get_settings(self, user_id: str) -> UserSettings:
#         """获取用户设置"""
#         user = await self.get(user_id)
#         return UserSettings(**user.settings)
#
#     async def update_settings(
#         self,
#         user_id: str,
#         settings: Dict[str, Any]
#     ) -> UserSettings:
#         """更新用户设置"""
#         user = await self.get(user_id)
#         user.update_settings(settings)
#         await self.session.commit()
#         return UserSettings(**user.settings)
#
#     async def update_stats(
#         self,
#         user_id: str,
#         messages_count: int = 0,
#         tokens: int = 0
#     ) -> None:
#         """更新用户统计信息"""
#         user = await self.get(user_id)
#         user.update_conversation_stats(messages_count, tokens)
#         await self.session.commit()
#
#     async def get_system_stats(self) -> SystemStats:
#         """获取系统统计信息"""
#         stats = await User.get_system_stats(self.session)
#         return SystemStats(**stats)
#
#     async def get_or_create_test_user(self) -> User:
#         """获取或创建测试用户"""
#         return await User.get_or_create_test_user(self.session)