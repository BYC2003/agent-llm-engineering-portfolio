# 导入 sys，用来读取命令行参数。
import sys


# 定义账本业务的异常基类。
class LedgerError(Exception):
    """账本业务错误的基类。"""


# 定义更具体的异常：只表示金额不合法。
class InvalidAmountError(LedgerError):
    """金额不符合业务规则。"""


def parse_amount(text: str) -> int:
    """把文本金额转换成正整数；失败时抛出自定义异常。"""
    try:
        # int() 可能因为文本不是整数而抛出 ValueError。
        cents = int(text)
    except ValueError as exc:
        # 捕获能处理的 ValueError，并转换成更明确的业务异常。
        # from exc 会保留原始错误，方便后续排查根因。
        raise InvalidAmountError("金额必须是整数分") from exc

    # 金额是整数但小于等于 0 时，也属于业务规则错误。
    if cents <= 0:
        raise InvalidAmountError("金额必须大于 0")

    # 只有通过以上检查，才把整数金额返回给调用者。
    return cents


def main() -> int:
    """程序的入口：返回 0 表示成功，返回 1 表示失败。"""
    # 没有传入命令行参数时，默认使用 "abc" 触发错误分支。
    text = sys.argv[1] if len(sys.argv) > 1 else "abc"

    try:
        # 调用可能抛出自定义异常的函数。
        amount = parse_amount(text)
    except InvalidAmountError as exc:
        # 只捕获当前层能够处理的业务异常。
        print(f"操作失败：{exc}")
        # 非 0 退出码表示程序失败。
        return 1
    else:
        # try 没有异常时才会执行这里。
        print(f"操作成功：{amount} 分")
        # 0 退出码表示程序成功。
        return 0


# 只有直接运行这个文件时，才执行 main()。
if __name__ == "__main__":
    # 把 main() 的返回值交给系统作为退出码。
    raise SystemExit(main())