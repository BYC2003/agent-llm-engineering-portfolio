import json
from pathlib import Path

student = {
    "name": "张小明",
    "age": 18,
    "skills": ["Python", "Git", "JSON"],
    "active": True,
    "nothing": None,
    "city": "杭州",
    "email": "xiaoming@example.com",
}

data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)
json_path = data_dir / "student.json"

with json_path.open("w", encoding="utf-8") as file:
    json.dump(student, file, ensure_ascii=False, indent=2)

with json_path.open("r", encoding="utf-8") as file:
    loaded_student = json.load(file)

print("保存文件：", json_path)
print("读回类型：", type(loaded_student).__name__)
print("读取 name：", loaded_student["name"])
print("读取 city：", loaded_student["city"])
print("文件内容：")
print(json_path.read_text(encoding="utf-8"))