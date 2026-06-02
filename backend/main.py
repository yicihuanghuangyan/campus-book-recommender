"""
FastAPI 应用主入口
==================
校园书籍推荐系统后端 API 服务。

启动方式:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

API 文档:
    启动后访问 http://localhost:8000/docs (Swagger UI)
    或 http://localhost:8000/redoc (ReDoc)

核心接口:
    GET  /api/recommend/{user_id}  为用户推荐书籍
    GET  /api/books                获取书籍列表
    GET  /api/users/{user_id}      获取用户信息
    GET  /api/stats                系统统计信息
"""

import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager
from typing import Optional

from .config import (
    DEFAULT_TOP_N, DEFAULT_METHOD, DEFAULT_K_NEIGHBORS,
    RATINGS_CSV, PROJECT_ROOT,
)
from .database import init_db, get_db
from .models import User, Book, Rating
from .schemas import (
    UserResponse, BookResponse, RatingCreate, RatingResponse,
    RecommendResponse, RecommendItem, StatsResponse, MessageResponse,
)

# ---- 全局推荐器实例（应用启动时初始化）----
recommender = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - startup: 初始化数据库、加载推荐模型
    - shutdown: 清理资源
    """
    global recommender

    # ---- 启动时 ----
    print("[App] 初始化数据库...")
    init_db()

    print("[App] 加载协同过滤推荐模型...")
    # 从数据库或 CSV 加载评分数据，初始化推荐器
    from algorithm.collaborative_filtering import CollaborativeFiltering

    try:
        # 优先从 CSV 加载（数据更完整，避免依赖数据库状态）
        ratings_df = pd.read_csv(RATINGS_CSV)
        recommender = CollaborativeFiltering(ratings_df)
        print(f"[App] 推荐模型加载成功，评分矩阵: "
              f"{recommender.user_item_matrix.shape[0]} 用户 x "
              f"{recommender.user_item_matrix.shape[1]} 书籍")
    except Exception as e:
        print(f"[App] 推荐模型加载失败: {e}")
        # 尝试从数据库加载
        db = next(get_db())
        try:
            ratings = db.query(Rating).all()
            if ratings:
                df = pd.DataFrame([{
                    "user_id": r.user_id,
                    "book_id": r.book_id,
                    "score": r.score,
                } for r in ratings])
                recommender = CollaborativeFiltering(df)
                print(f"[App] 从数据库加载推荐模型成功")
            else:
                print("[App] 警告: 无评分数据，推荐功能不可用")
        finally:
            db.close()

    yield  # 应用运行中...

    # ---- 关闭时 ----
    print("[App] 应用关闭")


# ---- 创建 FastAPI 应用 ----
app = FastAPI(
    title="校园书籍推荐系统 API",
    description="""
基于协同过滤算法的校园书籍推荐系统。

## 功能
- **用户管理**: 查询用户信息
- **书籍管理**: 浏览、搜索校园书籍
- **评分系统**: 用户对书籍打分（1-5分）
- **智能推荐**: 基于协同过滤算法推荐个性化书单

## 推荐方法
- **User-Based CF**: 找到相似用户，推荐他们喜欢的书
- **Item-Based CF**: 基于书籍内容相似度进行推荐
- **Hybrid**: 融合以上两种方法，综合推荐
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# ---- CORS 跨域配置 ----
# 允许前端页面（任何来源）调用后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],           # 允许所有 HTTP 方法
    allow_headers=["*"],           # 允许所有请求头
    expose_headers=["*"],
)


# ============================================================
#  根路由 & 健康检查
# ============================================================

@app.get("/", tags=["系统"])
def root():
    """API 根路径，返回服务信息"""
    return {
        "name": "校园书籍推荐系统 API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {"status": "healthy", "recommender_ready": recommender is not None}


# ============================================================
#  用户接口
# ============================================================

@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["用户"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    根据 ID 获取用户信息

    - **user_id**: 用户ID
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
    return user


@app.get("/api/users", response_model=list[UserResponse], tags=["用户"])
def list_users(
    department: Optional[str] = Query(None, description="按院系筛选"),
    grade: Optional[str] = Query(None, description="按年级筛选"),
    skip: int = Query(0, ge=0, description="分页偏移"),
    limit: int = Query(50, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """
    获取用户列表，支持按院系和年级筛选

    - **department**: 可选，如"计算机科学与技术学院"
    - **grade**: 可选，如"2023级"
    """
    query = db.query(User)
    if department:
        query = query.filter(User.department == department)
    if grade:
        query = query.filter(User.grade == grade)
    users = query.offset(skip).limit(limit).all()
    return users


# ============================================================
#  书籍接口
# ============================================================

@app.get("/api/books", response_model=list[BookResponse], tags=["书籍"])
def list_books(
    category: Optional[str] = Query(None, description="按分类筛选"),
    keyword: Optional[str] = Query(None, description="书名关键词搜索"),
    skip: int = Query(0, ge=0, description="分页偏移"),
    limit: int = Query(50, ge=1, le=200, description="每页数量"),
    db: Session = Depends(get_db),
):
    """
    获取书籍列表，支持按分类筛选和书名搜索

    - **category**: 如"编程语言"、"人工智能"、"算法与数据结构"
    - **keyword**: 模糊搜索书名
    """
    query = db.query(Book)
    if category:
        query = query.filter(Book.category == category)
    if keyword:
        query = query.filter(Book.title.contains(keyword))
    books = query.offset(skip).limit(limit).all()
    return books


@app.get("/api/books/categories", tags=["书籍"])
def list_categories(db: Session = Depends(get_db)):
    """获取所有书籍分类列表"""
    categories = db.query(Book.category).distinct().all()
    return [c[0] for c in categories if c[0]]


@app.get("/api/books/{book_id}", response_model=BookResponse, tags=["书籍"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    """
    根据 ID 获取书籍详情

    - **book_id**: 书籍ID
    """
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"书籍 {book_id} 不存在")
    return book


# ============================================================
#  评分接口
# ============================================================

@app.get("/api/ratings/user/{user_id}", response_model=list[RatingResponse], tags=["评分"])
def get_user_ratings(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    获取用户的评分历史

    - **user_id**: 用户ID
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 附加书名信息
    result = []
    for r in ratings:
        book = db.query(Book).filter(Book.book_id == r.book_id).first()
        result.append(RatingResponse(
            rating_id=r.rating_id,
            user_id=r.user_id,
            book_id=r.book_id,
            score=r.score,
            book_title=book.title if book else None,
            created_at=r.created_at,
        ))
    return result


@app.post("/api/ratings", response_model=RatingResponse, tags=["评分"], status_code=201)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    """
    新增或更新评分

    - **user_id**: 用户ID
    - **book_id**: 书籍ID
    - **score**: 评分（1-5）
    """
    # 检查用户和书籍是否存在
    user = db.query(User).filter(User.user_id == rating.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {rating.user_id} 不存在")

    book = db.query(Book).filter(Book.book_id == rating.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail=f"书籍 {rating.book_id} 不存在")

    # 检查是否已评分过（是则更新）
    existing = (
        db.query(Rating)
        .filter(
            Rating.user_id == rating.user_id,
            Rating.book_id == rating.book_id,
        )
        .first()
    )

    if existing:
        existing.score = rating.score
        db.commit()
        db.refresh(existing)
        return RatingResponse(
            rating_id=existing.rating_id,
            user_id=existing.user_id,
            book_id=existing.book_id,
            score=existing.score,
            book_title=book.title,
            created_at=existing.created_at,
        )
    else:
        new_rating = Rating(
            user_id=rating.user_id,
            book_id=rating.book_id,
            score=rating.score,
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return RatingResponse(
            rating_id=new_rating.rating_id,
            user_id=new_rating.user_id,
            book_id=new_rating.book_id,
            score=new_rating.score,
            book_title=book.title,
            created_at=new_rating.created_at,
        )


# ============================================================
#  推荐接口（核心）
# ============================================================

@app.get("/api/recommend/{user_id}", response_model=RecommendResponse, tags=["推荐"])
def recommend_for_user(
    user_id: int,
    top_n: int = Query(default=DEFAULT_TOP_N, ge=1, le=50, description="推荐数量"),
    method: str = Query(
        default=DEFAULT_METHOD,
        pattern=r"^(user_based|item_based|hybrid)$",
        description="推荐方法",
    ),
    k: int = Query(default=DEFAULT_K_NEIGHBORS, ge=5, le=100, description="邻居数量"),
    db: Session = Depends(get_db),
):
    """
    **核心接口 —— 为用户推荐书籍**

    基于协同过滤算法，分析用户评分行为，智能推荐未读过的书籍。

    ---
    ### 推荐方法说明

    - **user_based (基于用户)**:
      找到评分偏好相似的用户，推荐他们喜欢的书。

    - **item_based (基于物品)**:
      分析书籍之间的相似度，推荐与已读高分书相似的书籍。

    - **hybrid (混合推荐，默认)**:
      融合以上两种方法，综合评分，推荐更准确。

    ### 参数
    - **user_id**: 目标用户ID（1-200）
    - **top_n**: 返回推荐数量（默认10，最大50）
    - **method**: 推荐方法
    - **k**: User-Based 的邻居数量（默认30）

    ### 示例
    - `GET /api/recommend/5?top_n=10&method=hybrid`
    """
    global recommender

    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="推荐引擎未就绪，请检查评分数据是否正确加载",
        )

    # 检查用户是否存在
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")

    # 调用推荐算法
    try:
        recs = recommender.recommend(user_id, top_n=top_n, method=method, k=k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐计算失败: {str(e)}")

    # 如果推荐结果为空，尝试降低 top_n 或切换方法
    if not recs and recommender is not None:
        # 回退：尝试用 item_based
        try:
            recs = recommender.recommend(user_id, top_n=top_n, method="item_based")
        except Exception:
            pass

    # 附加书籍详细信息
    book_ids = [r["book_id"] for r in recs]
    books_map = {}
    if book_ids:
        db_books = db.query(Book).filter(Book.book_id.in_(book_ids)).all()
        books_map = {b.book_id: b for b in db_books}

    recommendations = []
    for r in recs:
        book = books_map.get(r["book_id"])
        recommendations.append(RecommendItem(
            book_id=r["book_id"],
            book_title=book.title if book else f"书籍 #{r['book_id']}",
            book_author=book.author if book else None,
            book_category=book.category if book else None,
            predicted_score=r["predicted_score"],
            method=r["method"],
            reason=r["reason"],
        ))

    return RecommendResponse(
        user_id=user_id,
        recommendations=recommendations,
        method=method,
        total=len(recommendations),
    )


# ============================================================
#  统计接口
# ============================================================

@app.get("/api/stats", response_model=StatsResponse, tags=["系统"])
def get_stats(db: Session = Depends(get_db)):
    """
    获取系统统计数据

    返回用户总数、书籍总数、评分总数、平均分、矩阵稀疏度。
    """
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    total_ratings = db.query(Rating).count()
    avg_score = db.query(func.avg(Rating.score)).scalar() or 0.0

    # 计算稀疏度 = 1 - (评分数 / (用户数 * 书籍数))
    matrix_size = total_users * total_books
    sparsity = 1.0 - (total_ratings / matrix_size) if matrix_size > 0 else 1.0

    return StatsResponse(
        total_users=total_users,
        total_books=total_books,
        total_ratings=total_ratings,
        avg_score=round(float(avg_score), 2),
        sparsity=round(sparsity, 4),
    )
