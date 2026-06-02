"""
SQLAlchemy ORM 模型定义
=======================
映射数据库中的 users、books、ratings 三张表。
与 data/init_db.sql 中的表结构一一对应。
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# SQLAlchemy 声明式基类
Base = declarative_base()


class User(Base):
    """用户模型 —— 对应 users 表"""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="用户唯一ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, default="", comment="密码哈希值")
    nickname = Column(String(50), nullable=True, comment="昵称")
    department = Column(String(100), nullable=True, comment="院系")
    grade = Column(String(20), nullable=True, comment="年级")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")

    # 关联：一个用户有多条评分记录
    ratings = relationship("Rating", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.user_id}, name={self.username}, dept={self.department})>"


class Book(Base):
    """书籍模型 —— 对应 books 表"""
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, autoincrement=True, comment="书籍唯一ID")
    title = Column(String(200), nullable=False, comment="书名")
    author = Column(String(200), nullable=True, comment="作者")
    publisher = Column(String(200), nullable=True, comment="出版社")
    category = Column(String(100), nullable=True, comment="分类")
    isbn = Column(String(20), nullable=True, comment="ISBN号")
    description = Column(Text, nullable=True, comment="书籍简介")
    cover_url = Column(String(500), nullable=True, comment="封面URL")
    publish_year = Column(Integer, nullable=True, comment="出版年份")
    created_at = Column(DateTime, default=datetime.now, comment="入库时间")

    # 关联：一本书有多条评分记录
    ratings = relationship("Rating", back_populates="book", lazy="dynamic")

    # 索引
    __table_args__ = (
        Index("idx_books_category", "category"),
        Index("idx_books_title", "title"),
    )

    def __repr__(self):
        return f"<Book(id={self.book_id}, title={self.title}, category={self.category})>"


class Rating(Base):
    """评分模型 —— 对应 ratings 表"""
    __tablename__ = "ratings"

    rating_id = Column(Integer, primary_key=True, autoincrement=True, comment="评分唯一ID")
    user_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    book_id = Column(
        Integer,
        ForeignKey("books.book_id", ondelete="CASCADE"),
        nullable=False,
        comment="书籍ID",
    )
    score = Column(Integer, nullable=False, comment="评分 1-5")
    created_at = Column(DateTime, default=datetime.now, comment="评分时间")

    # 关联
    user = relationship("User", back_populates="ratings")
    book = relationship("Book", back_populates="ratings")

    # 约束：每个用户对每本书只能评分一次
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uk_user_book"),
        Index("idx_ratings_user", "user_id"),
        Index("idx_ratings_book", "book_id"),
    )

    def __repr__(self):
        return f"<Rating(user={self.user_id}, book={self.book_id}, score={self.score})>"
