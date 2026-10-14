# 这个模块只提供共同需要的功能，不导入 A 或 B。
def format_source_name(letter: str) -> str:
    # 根据字母生成统一格式的说明。
    return f"数据来自模块 {letter}"