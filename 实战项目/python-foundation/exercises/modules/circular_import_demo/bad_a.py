# A 模块在顶层导入 B 模块。
# 顶层导入表示：Python 一开始加载 A，就立刻去加载 B。
from .bad_b import get_name_from_b


def get_name_from_a() -> str:
    # 返回 A 模块自己的名字。
    return "A"


def call_b() -> str:
    # 通过 B 模块提供的函数取得名字。
    return get_name_from_b()