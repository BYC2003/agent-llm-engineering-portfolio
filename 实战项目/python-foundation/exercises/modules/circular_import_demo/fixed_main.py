# 导入两个不再互相依赖的模块。
from .fixed_a import get_name_from_a
from .fixed_b import get_name_from_b


def main() -> None:
    # 分别调用 A 和 B 的功能。
    print(get_name_from_a())
    print(get_name_from_b())


# 按模块方式直接运行时，执行 main()。
if __name__ == "__main__":
    main()