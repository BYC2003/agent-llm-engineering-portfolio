# 1. 变量：把值保存到一个名字里
name = "小明"
age = 18
is_student = True
skills = ["Python", "Git", "JSON"]

print("姓名：", name)
print("年龄：", age)
print("是否学生：", is_student)
print("技能：", skills)
print()

# 2. 条件：根据条件选择一条分支
if age >= 18:
    print(name, "已成年")
else:
    print(name, "未成年")
print()

# 3. 循环：对列表中的每一项重复执行
for skill in skills:
    print("正在学习：", skill)
print()

# 4. def：定义一个可重复使用的动作
def greet(person_name):
    return f"你好，{person_name}"

message = greet(name)
print(message)
print("greet 的类型：", type(greet).__name__)
print()

# 5. class：定义一个对象的模板
class Student:
    def __init__(self, student_name, student_age):
        self.name = student_name
        self.age = student_age

    def introduce(self):
        return f"我叫{self.name}，今年{self.age}岁"

student = Student("小红", 20)
print("student 的类型：", type(student).__name__)
print(student.introduce())