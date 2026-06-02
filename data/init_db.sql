-- ============================================================
-- 校园书籍推荐系统 - 数据库建表 SQL
-- 数据库名称: campus_book_recommend
-- 使用方式: 在 MySQL 中执行 source init_db.sql
-- ============================================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS campus_book_recommend
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE campus_book_recommend;

-- ============================================================
-- 1. 用户表 (users)
-- 存储系统用户的基本信息，模拟校园学生用户
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户唯一ID',
    username      VARCHAR(50)  NOT NULL UNIQUE    COMMENT '用户名，用于登录',
    password_hash VARCHAR(255) NOT NULL           COMMENT '密码哈希值（生产环境使用 bcrypt）',
    nickname      VARCHAR(50)  DEFAULT NULL       COMMENT '昵称/显示名',
    department    VARCHAR(100) DEFAULT NULL       COMMENT '院系，如：计算机学院、软件学院',
    grade         VARCHAR(20)  DEFAULT NULL       COMMENT '年级，如：2023级、2024级',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',

    INDEX idx_department (department),
    INDEX idx_grade (grade)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';


-- ============================================================
-- 2. 书籍表 (books)
-- 存储书籍基本信息，以计算机/软件类专业书籍为主
-- ============================================================
CREATE TABLE IF NOT EXISTS books (
    book_id       INT AUTO_INCREMENT PRIMARY KEY COMMENT '书籍唯一ID',
    title         VARCHAR(200) NOT NULL           COMMENT '书名',
    author        VARCHAR(200) DEFAULT NULL       COMMENT '作者',
    publisher     VARCHAR(200) DEFAULT NULL       COMMENT '出版社',
    category      VARCHAR(100) DEFAULT NULL       COMMENT '分类，如：编程语言、算法、人工智能、数据库等',
    isbn          VARCHAR(20)  DEFAULT NULL       COMMENT 'ISBN 号',
    description   TEXT         DEFAULT NULL       COMMENT '书籍简介/摘要',
    cover_url     VARCHAR(500) DEFAULT NULL       COMMENT '封面图片URL',
    publish_year  INT          DEFAULT NULL       COMMENT '出版年份',
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',

    INDEX idx_category (category),
    INDEX idx_author (author),
    INDEX idx_title (title)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='书籍表';


-- ============================================================
-- 3. 评分表 (ratings)
-- 存储用户对书籍的评分记录（1-5分），是协同过滤算法的核心数据
-- ============================================================
CREATE TABLE IF NOT EXISTS ratings (
    rating_id     INT AUTO_INCREMENT PRIMARY KEY COMMENT '评分唯一ID',
    user_id       INT      NOT NULL              COMMENT '用户ID，外键关联 users.user_id',
    book_id       INT      NOT NULL              COMMENT '书籍ID，外键关联 books.book_id',
    score         TINYINT  NOT NULL              COMMENT '评分，范围 1-5，1最低5最高',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '评分时间',

    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,

    -- 每个用户对每本书只能评分一次
    UNIQUE KEY uk_user_book (user_id, book_id),

    -- 评分值约束
    CONSTRAINT chk_score CHECK (score >= 1 AND score <= 5),

    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_score (score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评分表';


-- ============================================================
-- 4. 用户相似度缓存表 (user_similarity_cache) - 可选优化
-- 预计算用户相似度，避免每次推荐时重复计算，提升性能
-- ============================================================
CREATE TABLE IF NOT EXISTS user_similarity_cache (
    user_id_1     INT          NOT NULL           COMMENT '用户1的ID',
    user_id_2     INT          NOT NULL           COMMENT '用户2的ID',
    similarity    DOUBLE       NOT NULL           COMMENT '相似度值（余弦相似度 / 皮尔逊相关系数）',
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',

    PRIMARY KEY (user_id_1, user_id_2),
    FOREIGN KEY (user_id_1) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id_2) REFERENCES users(user_id) ON DELETE CASCADE,

    INDEX idx_similarity (similarity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户相似度缓存表（可选，用于优化推荐速度）';
