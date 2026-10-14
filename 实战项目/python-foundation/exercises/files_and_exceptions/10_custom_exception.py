class InvalidAmountError(Exception):
    """金额不合法。"""


def parse_amount(text: str) -> int:
    try:
        cents = int(text)
    except ValueError as exc:
        raise InvalidAmountError("金额必须是整数分") from exc

    if cents <= 0:
        raise InvalidAmountError("金额必须大于 0")

    return cents


for value in ["100", "abc", "-5"]:
    try:
        result = parse_amount(value)
    except InvalidAmountError as exc:
        print("输入", repr(value), "-> 业务错误：", exc)
        if exc.__cause__ is not None:
            print("底层原因：", type(exc.__cause__).__name__)
    else:
        print("输入", repr(value), "-> 成功：", result, "分")
    finally:
        print("检查结束")