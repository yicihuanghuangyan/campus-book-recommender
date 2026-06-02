"""
模拟校园书籍评分数据集生成脚本
===================================
生成三类数据：
  1. users.csv    - 模拟校园用户（计算机/软件相关专业学生）
  2. books.csv    - 计算机类专业书籍
  3. ratings.csv  - 用户对书籍的评分记录（用于协同过滤算法）

运行方式: python data/generate_data.py
输出目录: data/
"""

import csv
import random
import os
from datetime import datetime, timedelta

# 设置随机种子，确保每次生成结果一致
random.seed(42)

# 输出目录
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. 生成用户数据（模拟校园学生）
# ============================================================
DEPARTMENTS = [
    "计算机科学与技术学院",
    "软件学院",
    "人工智能学院",
    "信息与通信工程学院",
    "数据科学与大数据学院",
    "网络空间安全学院",
    "电子信息工程学院",
]

GRADES = ["2022级", "2023级", "2024级", "2025级"]

NUM_USERS = 200  # 生成200个用户


def generate_users():
    """生成校园用户数据"""
    users = []
    for i in range(1, NUM_USERS + 1):
        dept = random.choice(DEPARTMENTS)
        grade = random.choice(GRADES)
        username = f"student{i:04d}"
        # 模拟不同学院有不同侧重的阅读偏好（用户聚类）
        users.append({
            "user_id": i,
            "username": username,
            "nickname": f"同学{i:04d}",
            "department": dept,
            "grade": grade,
        })
    return users


# ============================================================
# 2. 生成书籍数据（计算机类专业书籍）
# ============================================================
BOOKS_DATA = [
    # (书名, 作者, 出版社, 分类, ISBN, 出版年份, 简介)
    ("算法导论（第3版）", "Thomas H. Cormen", "机械工业出版社", "算法与数据结构",
     "978-7-111-40701-0", 2013,
     "算法领域的经典教材，全面介绍了算法设计、分析和实现的基础知识与高级技术。"),
    ("深入理解计算机系统（第3版）", "Randal E. Bryant", "机械工业出版社", "计算机基础",
     "978-7-111-54493-7", 2016,
     "从程序员视角深入剖析计算机系统的工作原理，涵盖处理器架构、存储器层次、链接、异常控制流等核心主题。"),
    ("Python编程：从入门到实践（第3版）", "Eric Matthes", "人民邮电出版社", "编程语言",
     "978-7-115-61383-7", 2023,
     "全球畅销的Python入门书，通过项目驱动的方式帮助读者快速掌握Python编程。"),
    ("计算机网络：自顶向下方法（第8版）", "James F. Kurose", "机械工业出版社", "计算机网络",
     "978-7-111-71958-0", 2022,
     "以自顶向下的方式讲解计算机网络，从应用层开始逐步深入，适合初学者理解网络原理。"),
    ("数据库系统概念（第7版）", "Abraham Silberschatz", "机械工业出版社", "数据库",
     "978-7-111-62383-0", 2019,
     "数据库领域的权威教材，涵盖关系模型、SQL、数据库设计、事务管理、存储引擎等核心内容。"),
    ("机器学习", "周志华", "清华大学出版社", "人工智能",
     "978-7-302-42328-7", 2016,
     "国内最著名的机器学习教材之一（西瓜书），系统讲解监督学习、无监督学习、集成学习等经典算法。"),
    ("深度学习", "Ian Goodfellow", "人民邮电出版社", "人工智能",
     "978-7-115-46147-6", 2017,
     "深度学习领域的奠基性著作（花书），由三位领域先驱合著，全面覆盖深度学习的数学基础与前沿技术。"),
    ("C Primer Plus（第6版）", "Stephen Prata", "人民邮电出版社", "编程语言",
     "978-7-115-39059-2", 2015,
     "C语言经典入门教材，内容详尽，适合编程初学者打好C语言基础。"),
    ("JavaScript高级程序设计（第4版）", "Matt Frisbie", "人民邮电出版社", "编程语言",
     "978-7-115-54588-1", 2020,
     "前端开发必读的红宝书，深入讲解JavaScript语言核心概念与Web开发技术。"),
    ("操作系统概念（第10版）", "Abraham Silberschatz", "机械工业出版社", "操作系统",
     "978-7-111-65541-1", 2020,
     "操作系统领域的经典教材（恐龙书），涵盖进程管理、内存管理、文件系统、I/O系统等核心主题。"),
    ("设计模式：可复用面向对象软件的基础", "Erich Gamma 等", "机械工业出版社", "软件工程",
     "978-7-111-07575-2", 2000,
     "GoF四人帮经典之作，介绍23种经典设计模式，是面向对象设计的必读书。"),
    ("剑指Offer：数据结构与算法名企面试题精讲", "何海涛", "电子工业出版社", "算法与数据结构",
     "978-7-121-41369-8", 2021,
     "面试算法刷题必备，涵盖经典算法面试题，帮助读者系统提升算法能力和面试技巧。"),
    ("Go语言程序设计", "Alan A. A. Donovan", "机械工业出版社", "编程语言",
     "978-7-111-55841-5", 2017,
     "Go语言圣经，由Google工程师撰写，系统讲解Go语言的语法、并发模型和工程实践。"),
    ("计算机组成与设计：硬件/软件接口（第5版）", "David A. Patterson", "机械工业出版社", "计算机基础",
     "978-7-111-50482-5", 2015,
     "体系结构经典教材，以RISC-V架构为主讲解计算机硬件与软件的交互设计。"),
    ("统计学习方法（第3版）", "李航", "清华大学出版社", "人工智能",
     "978-7-302-49723-3", 2019,
     "机器学习领域经典中文教材，系统介绍监督学习的主要方法及其数学原理。"),
    ("MySQL必知必会", "Ben Forta", "人民邮电出版社", "数据库",
     "978-7-115-19112-0", 2009,
     "SQL快速入门经典，短小精悍，帮助读者快速掌握MySQL查询和管理的基础知识。"),
    ("Spring实战（第6版）", "Craig Walls", "人民邮电出版社", "软件工程",
     "978-7-115-58703-3", 2022,
     "Spring框架权威指南，涵盖Spring Boot、Spring MVC等核心组件的实战应用。"),
    ("编译原理（第2版）", "Alfred V. Aho", "机械工业出版社", "计算机基础",
     "978-7-111-25121-7", 2008,
     "龙书——编译原理领域的绝对经典，涵盖词法分析、语法分析、代码生成等编译全流程。"),
    ("Linux命令行与shell脚本编程大全（第4版）", "Richard Blum", "人民邮电出版社", "操作系统",
     "978-7-115-55583-6", 2021,
     "Linux运维与Shell编程实战指南，覆盖从基础命令到高级脚本开发的全面内容。"),
    ("图解HTTP", "上野宣", "人民邮电出版社", "计算机网络",
     "978-7-115-35153-1", 2014,
     "HTTP协议图解入门书，用大量图示帮助读者轻松理解HTTP/HTTPS协议的工作原理。"),
    ("数据结构（C语言版）", "严蔚敏", "清华大学出版社", "算法与数据结构",
     "978-7-302-14751-0", 2007,
     "国内高校数据结构课程的经典教材，用C语言实现各类基础数据结构。"),
    ("集体智慧编程", "Toby Segaran", "电子工业出版社", "人工智能",
     "978-7-121-25892-2", 2015,
     "通俗易懂地讲解推荐系统、协同过滤、聚类等智能算法，适合入门学习推荐系统开发。"),
    ("Redis设计与实现", "黄健宏", "机械工业出版社", "数据库",
     "978-7-111-52501-8", 2016,
     "深入解析Redis内部数据结构与实现原理，是掌握Redis底层机制的必读书。"),
    ("流畅的Python", "Luciano Ramalho", "人民邮电出版社", "编程语言",
     "978-7-115-48216-6", 2017,
     "帮助有Python基础的开发者写出更地道、更高效的Python代码，深入Python数据模型。"),
    ("鸟哥的Linux私房菜：基础学习篇（第4版）", "鸟哥", "人民邮电出版社", "操作系统",
     "978-7-115-47946-4", 2018,
     "Linux入门首选读物，内容从基础到实战，手把手带读者掌握Linux系统管理。"),
    ("数据结构与算法分析：C语言描述（第2版）", "Mark Allen Weiss", "机械工业出版社", "算法与数据结构",
     "978-7-111-40541-2", 2013,
     "强调算法分析的严谨性，用C语言实现数据结构，适合打好算法分析基础。"),
    ("网络是怎样连接的", "户根勤", "人民邮电出版社", "计算机网络",
     "978-7-115-45040-1", 2017,
     "以探索之旅的形式讲解网络通信全过程，从浏览器输入URL到服务器响应，图解每一步。"),
    ("大话设计模式", "程杰", "清华大学出版社", "软件工程",
     "978-7-302-16206-3", 2007,
     "用生动有趣的故事讲解设计模式，降低学习门槛，适合设计模式入门。"),
    ("图解TCP/IP（第6版）", "竹下隆史", "人民邮电出版社", "计算机网络",
     "978-7-115-51016-6", 2019,
     "TCP/IP协议族的图解入门书，覆盖从物理层到应用层各层协议的工作原理。"),
    ("Kubernetes实战", "Brendan Burns", "电子工业出版社", "软件工程",
     "978-7-121-43435-2", 2022,
     "Kubernetes实战指南，从容器基础到集群管理，全面讲解云原生应用部署。"),
]

NUM_BOOKS = len(BOOKS_DATA)


def generate_books():
    """将书籍数据标准化为字典列表"""
    books = []
    for idx, (title, author, publisher, category, isbn, year, desc) in enumerate(BOOKS_DATA, start=1):
        books.append({
            "book_id": idx,
            "title": title,
            "author": author,
            "publisher": publisher,
            "category": category,
            "isbn": isbn,
            "publish_year": year,
            "description": desc,
            "cover_url": f"/static/covers/book_{idx:03d}.jpg",
        })
    return books


# ============================================================
# 3. 生成评分数据（模拟用户对书籍的评分）
# ============================================================
# 核心思路：模拟真实场景中的评分行为
#   - 同一学院的学生对相同领域的书有相似的评分偏好（模拟协同过滤场景）
#   - 热门书籍评分多，冷门书籍评分少
#   - 评分集中在 3-5 分（学生通常对教材给分中等偏上）
#   - 每位用户大约评分 15-50 本书

# 为不同学院定义偏好的书籍类别（用于制造用户聚类效果）
DEPARTMENT_CATEGORY_PREFERENCE = {
    "计算机科学与技术学院": ["算法与数据结构", "计算机基础", "操作系统", "编程语言"],
    "软件学院":             ["软件工程", "编程语言", "数据库", "算法与数据结构"],
    "人工智能学院":         ["人工智能", "算法与数据结构", "编程语言"],
    "信息与通信工程学院":   ["计算机网络", "编程语言", "操作系统"],
    "数据科学与大数据学院": ["数据库", "人工智能", "算法与数据结构"],
    "网络空间安全学院":     ["计算机网络", "操作系统", "算法与数据结构"],
    "电子信息工程学院":     ["计算机基础", "编程语言", "计算机网络"],
}


def get_book_category(book_id):
    """根据 book_id 获取书籍分类"""
    idx = book_id - 1
    if 0 <= idx < len(BOOKS_DATA):
        return BOOKS_DATA[idx][3]
    return None


# 基础评分概率分布：偏向 3-5 分
SCORE_WEIGHTS = [0.02, 0.08, 0.20, 0.35, 0.35]  # 1分概率2%，2分8%，3分20%，4分35%，5分35%


def weighted_random_score():
    """按权重随机生成评分（1-5）"""
    return random.choices([1, 2, 3, 4, 5], weights=SCORE_WEIGHTS, k=1)[0]


def generate_ratings(users, books):
    """
    生成评分数据
    策略：
      1. 对每位用户，随机评 15~50 本书
      2. 用户所属学院 → 更倾向评分对应领域的书（偏好类别 60% 概率，非偏好 40%）
      3. 偏好类别中的书给分更高（期望 +0.5 分）
      4. 热门书（高 book_id）有更高概率被评分
      5. 评分时间在过去 2 年内随机分布
    """
    ratings = []
    rating_id = 1

    # 热门书籍评分概率权重（模拟长尾分布：前几本书更多人看）
    book_popularity = [max(1.0, (NUM_BOOKS - b["book_id"]) / NUM_BOOKS * 10) for b in books]

    base_time = datetime(2026, 5, 1)

    for user in users:
        dept = user["department"]
        preferred_categories = DEPARTMENT_CATEGORY_PREFERENCE.get(dept, [])

        # 每位用户评分的书籍数量（最多评 NUM_BOOKS-2 本，确保有未读的可推荐）
        max_ratings_per_user = min(28, NUM_BOOKS - 3)
        num_rated = random.randint(10, max_ratings_per_user)

        # 为用户选择要评分的书籍
        candidate_books = list(range(1, NUM_BOOKS + 1))
        random.shuffle(candidate_books)

        rated_count = 0
        # 构建偏好书单和非偏好书单
        preferred_books = [i + 1 for i in range(NUM_BOOKS)
                           if get_book_category(i + 1) in preferred_categories]
        non_preferred_books = [i + 1 for i in range(NUM_BOOKS)
                               if get_book_category(i + 1) not in preferred_categories]

        random.shuffle(preferred_books)
        random.shuffle(non_preferred_books)

        # 60% 评分来自偏好类别，40% 来自非偏好类别
        num_preferred = min(len(preferred_books), int(num_rated * 0.6))
        num_non_preferred = min(len(non_preferred_books), num_rated - num_preferred)

        selected = preferred_books[:num_preferred] + non_preferred_books[:num_non_preferred]
        random.shuffle(selected)

        for book_id in selected:
            # 偏好书给分偏高
            if get_book_category(book_id) in preferred_categories:
                score = min(5, max(1, weighted_random_score() + random.randint(0, 1)))
            else:
                score = weighted_random_score()

            # 生成评分时间（过去 2 年内随机）
            days_ago = random.randint(1, 730)
            rating_time = base_time - timedelta(days=days_ago)

            ratings.append({
                "rating_id": rating_id,
                "user_id": user["user_id"],
                "book_id": book_id,
                "score": score,
                "created_at": rating_time.strftime("%Y-%m-%d %H:%M:%S"),
            })
            rating_id += 1

        # 确保最低评分数量（至少10条，且不超过总数-2）
        min_ratings = min(10, NUM_BOOKS - 2)
        actual_count = num_preferred + num_non_preferred
        while actual_count < min_ratings and len(candidate_books) > actual_count:
            extra_book = candidate_books[actual_count]
            if extra_book not in selected:
                selected.append(extra_book)
                cat = get_book_category(extra_book)
                if cat in preferred_categories:
                    score = min(5, max(1, weighted_random_score() + random.randint(0, 1)))
                else:
                    score = weighted_random_score()
                days_ago = random.randint(1, 730)
                rating_time = base_time - timedelta(days=days_ago)
                ratings.append({
                    "rating_id": rating_id,
                    "user_id": user["user_id"],
                    "book_id": extra_book,
                    "score": score,
                    "created_at": rating_time.strftime("%Y-%m-%d %H:%M:%S"),
                })
                rating_id += 1
                actual_count += 1

    return ratings


# ============================================================
# 4. 写入 CSV 文件
# ============================================================
def write_csv(filename, data, fieldnames):
    """将数据写入 CSV 文件"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"[OK] 已生成: {filepath} ({len(data)} 条记录)")


def main():
    print("=" * 60)
    print("  校园书籍推荐系统 - 模拟数据集生成器")
    print("=" * 60)

    # 生成用户数据
    print("\n[1/3] 生成用户数据...")
    users = generate_users()
    write_csv("users.csv", users, ["user_id", "username", "nickname", "department", "grade"])
    print(f"      └─ {len(users)} 名用户, 来自 {len(DEPARTMENTS)} 个学院")

    # 生成书籍数据
    print("\n[2/3] 生成书籍数据...")
    books = generate_books()
    write_csv("books.csv", books, ["book_id", "title", "author", "publisher",
                                      "category", "isbn", "publish_year", "description", "cover_url"])
    print(f"      └─ {len(books)} 本书, 覆盖 {len(set(b['category'] for b in books))} 个分类")

    # 统计各分类书籍数量
    from collections import Counter
    cat_counts = Counter(b["category"] for b in books)
    for cat, count in cat_counts.most_common():
        print(f"         · {cat}: {count}本")

    # 生成评分数据
    print("\n[3/3] 生成评分数据...")
    ratings = generate_ratings(users, books)
    write_csv("ratings.csv", ratings, ["rating_id", "user_id", "book_id", "score", "created_at"])
    print(f"      └─ {len(ratings)} 条评分记录")
    print(f"      └─ 稀疏度: {len(ratings) / (len(users) * len(books)):.2%}")

    # 数据统计
    print("\n" + "=" * 60)
    print("  数据集统计信息")
    print("=" * 60)
    print(f"  用户数:     {len(users)}")
    print(f"  书籍数:     {len(books)}")
    print(f"  评分数:     {len(ratings)}")
    print(f"  评分均值:   {sum(r['score'] for r in ratings) / len(ratings):.2f}")
    print(f"  用户均评分: {len(ratings) / len(users):.1f} 本/人")
    print(f"  书籍均评分: {len(ratings) / len(books):.1f} 人/本")
    print("=" * 60)
    print("[DONE] 数据集生成完毕！可用于协同过滤算法测试。")
    print("=" * 60)


if __name__ == "__main__":
    main()
