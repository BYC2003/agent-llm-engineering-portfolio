# B 模块也只依赖 shared 模块。
from .fixed_shared import format_source_name


def get_name_from_b() -> str:
    # 调用共享模块中的函数，不需要导入 A。
    return format_source_name("B")