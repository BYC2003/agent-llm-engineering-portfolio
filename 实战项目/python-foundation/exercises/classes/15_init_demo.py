# 这个程序用于观察：__init__ 什么时候执行，以及它做了什么。

print("1. 程序开始")

class Student:
    def __init__(self, name, age):
        # 创建 Student 对象时，__init__ 会自动执行。
        # self 就是“当前正在创建的这个 Student 对象”。
        print("3. __init__ 被自动调用")
        print("   收到的 name =", name)
        self.name = name  # 把参数 name 保存为当前对象的 name 属性
        self.age = age    # 把参数 age 保存为当前对象的 age 属性
        print("4. 已把 name 和 age 保存到当前对象")

print("2. 准备创建 Student 对象")

# 执行这一行时，Python 会创建一个对象，并自动调用 Student.__init__。
student = Student("小明", 18)

print("5. 对象创建完成，并赋值给 student")
print("student.name =", student.name)
print("student.age =", student.age)
