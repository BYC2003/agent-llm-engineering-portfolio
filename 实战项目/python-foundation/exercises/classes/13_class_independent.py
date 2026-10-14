# 练习目标：不看 11_basic_syntax.py，独立完成函数、类和对象的代码。
# 完成后在 python-foundation 根目录运行：
# python exercises/classes/13_class_independent.py


# 第 1 题：函数
# 要求：接收 name，返回字符串 “学员：小明”。
def build_label(name):
    # TODO：删除 raise，并用 f-string 返回 “学员：” 加 name。
    return f"学员：{name}"


# 第 2 题：类
# 要求：Course("Python 基础", 12) 能创建对象，并保存 name 和 hours。
class Course:
    def __init__(self, name, hours):
        # self 表示“当前正在创建的这个 Course 对象”。
        # TODO：把参数 name 保存到 self.name，把 hours 保存到 self.hours。
        self.name = name
        self.hours = hours

    def describe(self):
        # TODO：返回 “课程：Python 基础，共 12 小时”。
        # 提示：在方法内部用 self.name 和 self.hours 读取对象自己的数据。
        return f"课程：{self.name}, 共{self.hours}小时"


# 第 3 题：程序入口
if __name__ == "__main__":
    # 下面代码用于运行你完成的函数和类，不需要修改。
    print(build_label("小明"))
    course = Course("Python 基础", 12)
    print(course.describe())

# 期望输出：
# 学员：小明
# 课程：Python 基础，共 12 小时

