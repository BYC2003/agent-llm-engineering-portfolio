# A 模块只依赖 shared 模块。
from .fixed_shared import format_source_name


def get_name_from_a() -> str:
    # 调用共享模块中的函数，不需要导入 B。
    return format_source_name("A")