"""
数据库连接与初始化模块
======================
- 支持 MySQL（生产）和 SQLite（开发）双模式
- SQLite 模式下自动从 CSV 文件导入数据
- 提供 get_db() 依赖注入获取数据库会话
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from .config import DATABASE_URL, DB_MODE, USERS_CSV, BOOKS_CSV, RATINGS_CSV
from .models import Base

# ---- 创建数据库引擎 ----
# echo=False 不打印SQL日志; pool_pre_ping=True 自动重连检测
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# ---- 创建会话工厂 ----
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    初始化数据库表结构
    - 创建所有 ORM 模型对应的表（仅首次）
    - SQLite 模式下自动从 CSV 导入数据
    """
    # 创建表
    Base.metadata.create_all(bind=engine)

    # SQLite 模式下检查是否需要导入 CSV 数据
    if DB_MODE == "sqlite":
        _import_csv_to_sqlite()


def _import_csv_to_sqlite():
    """将 CSV 数据导入 SQLite 数据库（仅当表为空时）"""
    from .models import User, Book, Rating

    db = SessionLocal()
    try:
        # 检查用户表是否已有数据
        if db.query(User).count() == 0 and os.path.exists(USERS_CSV):
            users_df = pd.read_csv(USERS_CSV)
            for _, row in users_df.iterrows():
                db.add(User(
                    user_id=int(row["user_id"]),
                    username=row["username"],
                    password_hash="pbkdf2:sha256:placeholder",  # 开发环境占位密码
                    nickname=row.get("nickname", ""),
                    department=row.get("department", ""),
                    grade=row.get("grade", ""),
                ))
            db.commit()
            print(f"[DB] 已导入 {len(users_df)} 条用户数据")

        # 检查书籍表是否已有数据
        if db.query(Book).count() == 0 and os.path.exists(BOOKS_CSV):
            books_df = pd.read_csv(BOOKS_CSV)
            for _, row in books_df.iterrows():
                db.add(Book(
                    book_id=int(row["book_id"]),
                    title=row["title"],
                    author=row.get("author", ""),
                    publisher=row.get("publisher", ""),
                    category=row.get("category", ""),
                    isbn=str(row.get("isbn", "")),
                    description=row.get("description", ""),
                    cover_url=row.get("cover_url", ""),
                    publish_year=(
                        int(row["publish_year"])
                        if not pd.isna(row.get("publish_year"))
                        else None
                    ),
                ))
            db.commit()
            print(f"[DB] 已导入 {len(books_df)} 条书籍数据")

        # 检查评分表是否已有数据
        if db.query(Rating).count() == 0 and os.path.exists(RATINGS_CSV):
            ratings_df = pd.read_csv(RATINGS_CSV)
            batch_size = 500
            for i in range(0, len(ratings_df), batch_size):
                batch = ratings_df.iloc[i:i + batch_size]
                for _, row in batch.iterrows():
                    db.add(Rating(
                        user_id=int(row["user_id"]),
                        book_id=int(row["book_id"]),
                        score=int(row["score"]),
                    ))
                db.commit()
            print(f"[DB] 已导入 {len(ratings_df)} 条评分数据")

    except Exception as e:
        db.rollback()
        print(f"[DB] CSV 导入失败: {e}")
        raise
    finally:
        db.close()


def get_db():
    """
    获取数据库会话（FastAPI 依赖注入）

    使用方式:
        @app.get("/api/users")
        def get_users(db: Session = Depends(get_db)):
            ...

    每次请求自动创建新会话，请求结束后自动关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
