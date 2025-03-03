from fastapi import HTTPException, status

class BaseException(HTTPException):
    """基础异常类"""
    def __init__(self, detail: str):
        super().__init__(status_code=self.status_code, detail=detail)

class ValidationError(BaseException):
    """验证错误"""
    status_code = status.HTTP_400_BAD_REQUEST

class NotFoundException(BaseException):
    """资源未找到错误"""
    status_code = status.HTTP_404_NOT_FOUND

class UnauthorizedError(BaseException):
    """未授权错误"""
    status_code = status.HTTP_401_UNAUTHORIZED

class ForbiddenError(BaseException):
    """禁止访问错误"""
    status_code = status.HTTP_403_FORBIDDEN

class DatabaseError(BaseException):
    """数据库错误"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR 