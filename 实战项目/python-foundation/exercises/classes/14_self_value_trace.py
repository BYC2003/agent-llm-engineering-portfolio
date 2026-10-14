# 这个小程序用于观察：值如何进入函数，以及 self 到底代表谁。

print("=== 演示 1：函数参数 ===")

def build_label(name):
    # 调用者传入的 "小明" 会绑定到函数内部的局部变量 name。
    print("进入函数后，name =", name)
    result = f"学员：{name}"  # 使用收到的 name 拼出结果
    print("函数准备返回：", result)
    return result  # 把结果交还给调用者

returned = build_label("小明")
print("调用者收到返回值：", returned)
print()


print("=== 演示 2：类和 self ===")

class Course:
    def __init__(self, name, hours):
        # self 表示“当前正在创建的这个 Course 对象”。
        print("执行 __init__ 时，收到的 name =", name)
        self.name = name       # 把 name 保存到当前对象的 name 属性
        self.hours = hours     # 把 hours 保存到当前对象的 hours 属性
        print("已保存到 self.name =", self.name)

    def describe(self):
        # 调用 course1.describe() 时，Python 会把 course1 自动传给 self。
        # 调用 course2.describe() 时，Python 会把 course2 自动传给 self。
        return f"课程：{self.name}，共 {self.hours} 小时"


course1 = Course("Python 基础", 12)
print("course1 的属性：", course1.name, course1.hours)
print()

course2 = Course("Git 基础", 6)
print("course2 的属性：", course2.name, course2.hours)
print()

# 两个对象调用同一个方法，但因为 self 不同，读取到的属性也不同。
print(course1.describe())
print(course2.describe())
