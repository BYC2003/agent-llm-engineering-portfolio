# 演示可变默认值陷阱：列表不能直接写成函数的默认参数。

print("=== 错误写法：items=[] ===")

class BadBasket:
    def __init__(self, items=[]):
        # 这个默认列表在定义函数时创建一次。
        # 没有传入 items 的对象都会拿到同一个列表。
        self.items = items

bad1 = BadBasket()
bad2 = BadBasket()

# 只给 bad1 的列表加入苹果
bad1.items.append("苹果")
print("bad1.items =", bad1.items)
print("bad2.items =", bad2.items)  # 也被影响了

print()
print("=== 正确写法：items=None ===")

class GoodBasket:
    def __init__(self, items=None):
        # None 表示“调用者没有传入列表”。
        if items is None:
            # 每次创建对象时，单独创建一个新列表。
            items = []
        self.items = items

good1 = GoodBasket()
good2 = GoodBasket()

# 只给 good1 的列表加入香蕉
good1.items.append("香蕉")
print("good1.items =", good1.items)
print("good2.items =", good2.items)  # 保持独立
