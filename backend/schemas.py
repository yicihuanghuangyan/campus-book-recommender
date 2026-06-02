"""
Pydantic 数据校验模型（Schema）
===============================
定义 API 请求体和响应体的数据结构。
FastAPI 自动根据这些模型生成 API 文档（Swagger UI）。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ============================================================
#  用户相关 Schema
# ============================================================

class UserBase(BaseModel):
    """用户基本信息"""
    username: str
    nickname: Optional[str] = None
    department: Optional[str] = None
    grade: Optional[str] = None


class UserResponse(BaseModel):
    """用户信息响应"""
    user_id: int
    username: str
    nickname: Optional[str] = None
    department: Optional[str] = None
    grade: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # 允许从 ORM 对象自动转换


# ============================================================
#  书籍相关 Schema
# ============================================================

class BookBase(BaseModel):
    """书籍基本信息"""
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    category: Optional[str] = None


class BookResponse(BaseModel):
    """书籍详情响应"""
    book_id: int
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    category: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    publish_year: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================================
#  评分相关 Schema
# ============================================================

class RatingCreate(BaseModel):
    """新增评分请求"""
    user_id: int = Field(..., ge=1, description="用户ID")
    book_id: int = Field(..., ge=1, description="书籍ID")
    score: int = Field(..., ge=1, le=5, description="评分 1-5")


class RatingResponse(BaseModel):
    """评分记录响应"""
    rating_id: int
    user_id: int
    book_id: int
    score: int
    book_title: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
#  推荐相关 Schema
# ============================================================

class RecommendRequest(BaseModel):
    """推荐请求参数"""
    top_n: int = Field(default=10, ge=1, le=50, description="返回推荐数量")
    method: str = Field(
        default="hybrid",
        pattern=r"^(user_based|item_based|hybrid)$",
        description="推荐方法: user_based | item_based | hybrid",
    )


class RecommendItem(BaseModel):
    """单条推荐结果"""
    book_id: int
    book_title: Optional[str] = None
    book_author: Optional[str] = None
    book_category: Optional[str] = None
    predicted_score: float
    method: str
    reason: str


class RecommendResponse(BaseModel):
    """推荐响应"""
    user_id: int
    recommendations: list[RecommendItem]
    method: str
    total: int


# ============================================================
#  通用 Schema
# ============================================================

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


class StatsResponse(BaseModel):
    """系统统计信息"""
    total_users: int
    total_books: int
    total_ratings: int
    avg_score: float
    sparsity: float  # 评分矩阵稀疏度
