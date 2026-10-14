# 演示组合：Course 拥有一个 Teacher 对象。

class Teacher:
    def __init__(self, name, subject):
        # 保存老师自己的属性。
        self.name = name
        self.subject = subject

    def describe(self):
        # 老师负责描述自己的信息。
        return f"{self.name}老师，教授{self.subject}"


class Course:
    def __init__(self, name, hours, teacher):
        # 保存课程自己的属性。
        self.name = name
        self.hours = hours
        # 组合：把 teacher 对象作为 Course 的一个属性。
        self.teacher = teacher

    def describe(self):
        # 课程不自己拼接老师细节，而是委托 teacher.describe()。
        teacher_description = self.teacher.describe()
        return f"课程：{self.name}，共 {self.hours} 小时；{teacher_description}"


teacher = Teacher("王明", "Python")
course = Course("Python 基础", 12, teacher)

print(course.describe())

# 修改老师对象后，课程读取到的老师信息也会变化。
teacher.subject = "Agent"
print(course.describe())

