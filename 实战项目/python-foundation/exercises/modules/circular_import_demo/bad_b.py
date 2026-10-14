# B 模块也在顶层导入 A 模块。
# 这样 A 等 B，B 又等 A，就形成了循环导入。
from .bad_a import get_name_from_a


def get_name_from_b() -> str:
    # 返回 B 模块自己的名字。
    return "B"


def call_a() -> str:
    # 通过 A 模块提供的函数取得名字。
    return get_name_from_a()