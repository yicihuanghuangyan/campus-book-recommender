"""
协同过滤推荐算法模块
====================
实现两种经典的协同过滤算法：
  1. User-Based CF：基于用户相似度的协同过滤
     - 找到与目标用户相似度最高的 K 个邻居
     - 用邻居的评分加权预测目标用户对未评分书籍的评分
     - 返回预测评分最高的 N 本书

  2. Item-Based CF：基于物品相似度的协同过滤
     - 找到与用户已评分书籍最相似的书籍
     - 基于物品相似度预测评分
     - 返回预测评分最高的 N 本书

评分预测公式（User-Based）:
  pred(u, i) = mean(u) + Σ[sim(u, v) * (rating(v, i) - mean(v))] / Σ|sim(u, v)|

  其中:
    mean(u) = 用户 u 的所有评分均值
    sim(u, v) = 用户 u 和 v 的相似度（余弦相似度）

数据类型:
  - ratings_df: pandas DataFrame, 列: [user_id, book_id, score]
  - user_item_matrix: 行=user_id, 列=book_id, 值=score
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeFiltering:
    """
    协同过滤推荐器

    使用方式:
        cf = CollaborativeFiltering(ratings_df)
        recommendations = cf.recommend(user_id=5, top_n=10, method="hybrid")
    """

    def __init__(self, ratings_df: pd.DataFrame):
        """
        初始化推荐器

        参数:
            ratings_df: 评分数据，必须包含 user_id, book_id, score 三列
        """
        self.ratings = ratings_df.copy()

        # ---- 1. 构建用户-物品评分矩阵 ----
        # 行索引=user_id, 列=book_id, 值=score
        self.user_item_matrix = self.ratings.pivot_table(
            index="user_id",
            columns="book_id",
            values="score",
            aggfunc="mean"  # 如果同一用户对同一书有多次评分，取均值
        )

        # ---- 2. 计算用户均值（用于中心化）----
        self.user_means = self.user_item_matrix.mean(axis=1)

        # ---- 3. 中心化评分矩阵（减去用户均值）----
        self.centered_matrix = self.user_item_matrix.sub(self.user_means, axis=0)

        # ---- 4. 计算用户-用户相似度矩阵 ----
        # 用 0 填充 NaN（未评分项视为 0，即认为用户对该书评分等于其均值）
        centered_filled = self.centered_matrix.fillna(0)
        user_sim_array = cosine_similarity(centered_filled)
        self.user_similarity = pd.DataFrame(
            user_sim_array,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.index,
        )

        # ---- 5. 计算物品-物品相似度矩阵（物品视角）----
        item_centered = self.centered_matrix.T.fillna(0)
        item_sim_array = cosine_similarity(item_centered)
        self.item_similarity = pd.DataFrame(
            item_sim_array,
            index=self.user_item_matrix.columns,
            columns=self.user_item_matrix.columns,
        )

        # ---- 6. 缓存：已评分集合（加速查找）----
        self.rated_by_user = {
            uid: set(self.ratings[self.ratings["user_id"] == uid]["book_id"].values)
            for uid in self.user_item_matrix.index
        }

        # 全部书籍ID
        self.all_books = set(self.user_item_matrix.columns)

    # ================================================================
    #  User-Based CF: 基于用户的协同过滤
    # ================================================================

    def recommend_user_based(self, user_id: int, top_n: int = 10, k: int = 30) -> list[dict]:
        """
        基于用户相似度进行推荐

        步骤:
          1. 找到与目标用户最相似的 K 个邻居
          2. 对目标用户未评分的每本书，用邻居评分加权预测
          3. 返回预测分最高的 top_n 本书

        参数:
            user_id: 目标用户ID
            top_n:  返回推荐数量
            k:      邻居数量

        返回:
            [{book_id, predicted_score, reason}, ...]
        """
        # 用户不存在
        if user_id not in self.user_similarity.index:
            return []

        rated = self.rated_by_user.get(user_id, set())
        candidates = self.all_books - rated

        if not candidates:
            return []

        # 获取与目标用户相似度最高的 K 个邻居（排除自己）
        sim_scores = self.user_similarity.loc[user_id].drop(user_id, errors="ignore")
        neighbors = sim_scores.nlargest(k)
        # 过滤掉相似度 <= 0 的邻居
        neighbors = neighbors[neighbors > 0]

        if neighbors.empty:
            return []

        # 对每个候选书预测评分
        user_mean = self.user_means[user_id]
        predictions = []

        for book_id in candidates:
            # 收集邻居对该书的评分
            neighbor_scores = []
            neighbor_sims = []

            for neighbor_id, sim in neighbors.items():
                if book_id in self.user_item_matrix.columns:
                    score = self.user_item_matrix.loc[neighbor_id, book_id]
                    if not np.isnan(score):
                        neighbor_scores.append(score)
                        neighbor_sims.append(sim)

            if not neighbor_scores:
                continue

            # 预测公式: pred = mean(u) + Σ(sim * (r_vi - mean(v))) / Σ|sim|
            sim_sum = sum(abs(s) for s in neighbor_sims)
            if sim_sum == 0:
                continue

            weighted_sum = sum(
                s * (r - self.user_means[neighbor_id])
                for s, r in zip(neighbor_sims, neighbor_scores)
                if neighbor_id in self.user_means.index
            )
            pred_score = user_mean + weighted_sum / sim_sum

            # 限制评分范围 1-5
            pred_score = max(1.0, min(5.0, pred_score))

            predictions.append({
                "book_id": int(book_id),
                "predicted_score": round(pred_score, 2),
                "method": "user_based",
                "reason": f"{len(neighbor_scores)} 位相似用户也读过此书",
            })

        # 按预测分降序，取 top_n
        predictions.sort(key=lambda x: x["predicted_score"], reverse=True)
        return predictions[:top_n]

    # ================================================================
    #  Item-Based CF: 基于物品的协同过滤
    # ================================================================

    def recommend_item_based(self, user_id: int, top_n: int = 10) -> list[dict]:
        """
        基于物品相似度进行推荐

        步骤:
          1. 找到用户已评分且高分的书籍
          2. 对每本候选书（未评分），计算与已评分书的加权相似度
          3. 返回预测分最高的 top_n 本

        参数:
            user_id: 目标用户ID
            top_n:  返回推荐数量

        返回:
            [{book_id, predicted_score, reason}, ...]
        """
        if user_id not in self.user_item_matrix.index:
            return []

        rated = self.rated_by_user.get(user_id, set())
        candidates = self.all_books - rated

        if not candidates:
            return []

        # 获取用户评分过的书及其评分
        user_row = self.user_item_matrix.loc[user_id].dropna()
        user_rated_books = user_row.index.tolist()

        if not user_rated_books:
            return []

        predictions = []

        for book_id in candidates:
            if book_id not in self.item_similarity.index:
                continue

            # 计算候选书与已评分书的相似度加权评分
            sim_sum = 0.0
            weighted_sum = 0.0
            similar_books = []

            for rated_book in user_rated_books:
                if rated_book not in self.item_similarity.columns:
                    continue
                sim = self.item_similarity.loc[book_id, rated_book]
                if sim > 0:
                    score = user_row[rated_book]
                    weighted_sum += sim * score
                    sim_sum += abs(sim)
                    similar_books.append(rated_book)

            if sim_sum == 0:
                continue

            pred_score = weighted_sum / sim_sum
            pred_score = max(1.0, min(5.0, pred_score))

            predictions.append({
                "book_id": int(book_id),
                "predicted_score": round(pred_score, 2),
                "method": "item_based",
                "reason": f"与您读过的 {len(similar_books)} 本书相似",
            })

        predictions.sort(key=lambda x: x["predicted_score"], reverse=True)
        return predictions[:top_n]

    # ================================================================
    #  Hybrid CF: 混合推荐（融合 User-Based + Item-Based）
    # ================================================================

    def recommend(self, user_id: int, top_n: int = 10,
                  method: str = "hybrid", k: int = 30) -> list[dict]:
        """
        混合推荐 —— 融合两种协同过滤结果

        混合策略:
          1. 分别计算 User-Based 和 Item-Based 的预测
          2. 对同一本书的预测分取加权平均（user权重0.6, item权重0.4）
          3. 返回综合分最高的 top_n 本

        参数:
            user_id: 目标用户ID
            top_n:   返回推荐数量
            method:  "user_based" | "item_based" | "hybrid"
            k:       邻居数量（仅 User-Based 使用）

        返回:
            [{book_id, predicted_score, method, reason}, ...]
        """
        if method == "user_based":
            return self.recommend_user_based(user_id, top_n, k)

        if method == "item_based":
            return self.recommend_item_based(user_id, top_n)

        # ---- Hybrid 混合：融合两种结果 ----
        user_preds = self.recommend_user_based(user_id, top_n * 2, k)
        item_preds = self.recommend_item_based(user_id, top_n * 2)

        # 合并预测结果
        merged = {}

        for pred in user_preds:
            bid = pred["book_id"]
            merged[bid] = {
                "book_id": bid,
                "user_score": pred["predicted_score"],
                "item_score": 0.0,
                "weight": 1.0,
            }

        for pred in item_preds:
            bid = pred["book_id"]
            if bid in merged:
                merged[bid]["item_score"] = pred["predicted_score"]
                merged[bid]["weight"] = 2.0  # 两种方法都推荐
            else:
                merged[bid] = {
                    "book_id": bid,
                    "user_score": 0.0,
                    "item_score": pred["predicted_score"],
                    "weight": 0.6,
                }

        # 计算加权综合分
        # 两种方法都命中的书更可信，给更高权重
        results = []
        for bid, info in merged.items():
            if info["weight"] >= 1.0:
                # 两种方法都推荐：User-Based 0.6, Item-Based 0.4
                hybrid_score = info["user_score"] * 0.6 + info["item_score"] * 0.4
                method_desc = "hybrid"
                reason = "基于相似用户和相似书籍的综合推荐"
            else:
                hybrid_score = info["item_score"]
                method_desc = "item_based"
                reason = "基于相似书籍推荐"

            results.append({
                "book_id": int(bid),
                "predicted_score": round(hybrid_score, 2),
                "method": method_desc,
                "reason": reason,
            })

        results.sort(key=lambda x: x["predicted_score"], reverse=True)
        return results[:top_n]

    # ================================================================
    #  辅助方法
    # ================================================================

    def get_similar_users(self, user_id: int, top_n: int = 10) -> list[dict]:
        """获取与目标用户最相似的 N 个用户"""
        if user_id not in self.user_similarity.index:
            return []
        sim_scores = self.user_similarity.loc[user_id].drop(user_id, errors="ignore")
        top_users = sim_scores.nlargest(top_n)
        return [
            {"user_id": int(uid), "similarity": round(sim, 4)}
            for uid, sim in top_users.items()
        ]

    def get_similar_books(self, book_id: int, top_n: int = 10) -> list[dict]:
        """获取与目标书籍最相似的 N 本书"""
        if book_id not in self.item_similarity.index:
            return []
        sim_scores = self.item_similarity.loc[book_id].drop(book_id, errors="ignore")
        top_books = sim_scores.nlargest(top_n)
        return [
            {"book_id": int(bid), "similarity": round(sim, 4)}
            for bid, sim in top_books.items()
        ]
