import json

student = {
    "name": "张小明",
    "age": 18,
    "skills": ["Python", "Git", "JSON"],
    "active": True,
    "nothing": None,
    "city": "杭州",
}

json_text = json.dumps(student, ensure_ascii=False, indent=2)

print("1. Python 对象：", student)
print("2. Python 对象类型：", type(student).__name__)
print("3. 转换后的 JSON 字符串：")
print(json_text)
print("4. JSON 字符串类型：", type(json_text).__name__)

python_object = json.loads(json_text)

print("5. 转回后的 Python 对象：", python_object)
print("6. 转回后的类型：", type(python_object).__name__)
print("7. 读取转回对象的 name：", python_object["name"])