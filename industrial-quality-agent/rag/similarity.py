from math import sqrt


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """计算两个非零向量之间的余弦相似度。"""
    if len(left) != len(right):
        raise ValueError("两个向量的维度必须相同")

    if not left:
        raise ValueError("向量不能为空")

    # 点积衡量两个向量在方向上有多一致。
    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))

    # 向量的长度用于把点积归一化，避免长度本身影响相似度。
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))

    if left_norm == 0.0 or right_norm == 0.0:
        raise ValueError("零向量无法计算余弦相似度")

    return dot_product / (left_norm * right_norm)
