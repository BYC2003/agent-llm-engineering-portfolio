# 从当前包的 calculator 模块导入 add 函数。
# 开头的点号表示“从当前包中导入”。
from .calculator import add


def main() -> None:
    """运行模块演示。"""
    # 调用另一个模块中的函数，得到 2 + 3 的结果。
    result = add(2, 3)
    # 把结果打印出来。
    print(f"2 + 3 = {result}")


# 只有用模块方式直接运行本文件时，才执行 main()。
if __name__ == "__main__":
    main()