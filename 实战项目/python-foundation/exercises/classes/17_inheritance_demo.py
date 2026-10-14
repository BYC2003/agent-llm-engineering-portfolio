# 演示继承：OnlineCourse 复用 Course 的公共属性和方法。

print("=== 父类 Course ===")

class Course:
    def __init__(self, name, hours):
        # 保存所有课程都需要的公共属性。
        self.name = name
        self.hours = hours

    def describe(self):
        # 所有课程都可以使用这段公共描述。
        return f"课程：{self.name}，共 {self.hours} 小时"


print("=== 子类 OnlineCourse ===")

class OnlineCourse(Course):
    def __init__(self, name, hours, platform):
        # 括号里的 Course 表示：OnlineCourse 继承 Course。
        # super() 指向父类 Course，调用父类初始化方法。
        super().__init__(name, hours)
        # 再保存子类特有的平台属性。
        self.platform = platform

    def describe(self):
        # super().describe() 调用父类版本的 describe()，复用公共描述。
        base_description = super().describe()
        # 在父类结果后面追加子类特有信息。
        return f"{base_description}，平台：{self.platform}"


base_course = Course("Python 基础", 12)
online_course = OnlineCourse("Python 基础", 12, "录播平台")

print(base_course.describe())
print(online_course.describe())
print("online_course 是 Course 的实例吗：", isinstance(online_course, Course))
print("online_course 是 OnlineCourse 的实例吗：", isinstance(online_course, OnlineCourse))
