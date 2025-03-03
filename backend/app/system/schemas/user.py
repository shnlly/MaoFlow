from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict

class UserBase(BaseModel):
    """用户基础信息"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")
    is_active: bool = Field(True, description="是否激活")
    avatar: Optional[str] = Field(None, description="头像URL")

class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=8, description="密码")

    @validator('password')
    def password_complexity(cls, v):
        """验证密码复杂度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

class UserUpdate(BaseModel):
    """更新用户信息"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    avatar: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class UserSettings(BaseModel):
    """用户设置"""
    theme: str = Field("light", description="主题")
    language: str = Field("zh-CN", description="语言")
    notifications_enabled: bool = Field(True, description="是否启用通知")
    custom_settings: Dict[str, Any] = Field(
        default_factory=lambda: {
            "font_size": 14,
            "color": "blue"
        }
    )

class UserStats(BaseModel):
    """用户统计信息"""
    conversation_count: int = Field(0, description="会话数")
    message_count: int = Field(0, description="消息数")
    total_tokens: int = Field(0, description="总token数")
    last_active_at: Optional[datetime] = Field(None, description="最后活动时间")

class SystemStats(BaseModel):
    """系统统计信息"""
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    total_conversations: int = Field(..., description="总会话数")
    total_messages: int = Field(..., description="总消息数")
    total_tokens: int = Field(..., description="总token数")

class UserInDB(UserBase):
    """数据库中的用户信息"""
    id: str
    is_superuser: bool = False
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[str] = None
    last_login_ip: Optional[str] = None
    settings: UserSettings
    stats: UserStats

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # 创建统计信息
        stats = UserStats(
            conversation_count=obj.conversation_count,
            message_count=obj.message_count,
            total_tokens=obj.total_tokens,
            last_active_at=obj.last_active_at
        )

        # 创建设置信息
        settings = UserSettings(**obj.settings)

        # 创建用户信息
        return super().from_orm(obj)

class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）
    user: UserInDB   # 包含用户信息

class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: str  # user_id
    exp: int  # expiration time
    is_superuser: bool = False
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)

class PasswordReset(BaseModel):
    """密码重置"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=8, description="新密码")

    @validator('new_password')
    def password_complexity(cls, v):
        """验证密码复杂度"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    settings: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)