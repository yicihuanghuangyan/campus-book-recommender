"""
后端配置模块
============
管理数据库连接、应用参数等配置项。
支持 MySQL（生产）和 SQLite（开发/离线演示）两种模式。

使用 pydantic-settings 管理配置，可通过环境变量覆盖默认值。
"""

import os

# ---- 项目根路径 ----
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- 数据库配置 ----
# MySQL 配置（生产环境）
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "campus_book_recommend")

# 数据库模式: "mysql" | "sqlite"（默认 sqlite，方便开发测试）
DB_MODE = os.getenv("DB_MODE", "sqlite")

# MySQL 连接 URL
MYSQL_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    "?charset=utf8mb4"
)

# SQLite 连接 URL（开发/离线模式）
SQLITE_URL = f"sqlite:///{os.path.join(PROJECT_ROOT, 'data', 'book_recommend.db')}"

# 根据模式选择数据库 URL
DATABASE_URL = MYSQL_URL if DB_MODE == "mysql" else SQLITE_URL

# ---- 推荐算法配置 ----
DEFAULT_TOP_N = 10          # 默认推荐数量
DEFAULT_METHOD = "hybrid"   # 默认推荐方法: user_based | item_based | hybrid
DEFAULT_K_NEIGHBORS = 30    # 默认邻居数

# ---- CSV 数据文件路径 ----
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
BOOKS_CSV = os.path.join(DATA_DIR, "books.csv")
RATINGS_CSV = os.path.join(DATA_DIR, "ratings.csv")
