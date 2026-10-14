import json
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)

target_path = data_dir / "student_safe.json"
temp_path = data_dir / "student_safe.json.tmp"

student = {
    "name": "李安全",
    "age": 20,
    "skills": ["Python", "JSON"],
    "active": True,
}

try:
    # 第一步：先在内存中生成完整 JSON 字符串。
    # 如果对象不能转换成 JSON，目标文件不会被碰。
    json_text = json.dumps(student, ensure_ascii=False, indent=2)

    # 第二步：先写临时文件，不直接覆盖目标文件。
    temp_path.write_text(json_text, encoding="utf-8")

    # 第三步：从临时文件读回，确认它是可解析的 JSON。
    with temp_path.open("r", encoding="utf-8") as file:
        checked_student = json.load(file)

    # 第四步：确认成功后再替换目标文件。
    temp_path.replace(target_path)
except (OSError, json.JSONDecodeError, TypeError) as exc:
    print("安全写入失败：", exc)
else:
    print("安全写入成功：", target_path)
    print("读回 name：", checked_student["name"])
finally:
    # 如果中途失败，尽量清理临时文件。
    if temp_path.exists():
        temp_path.unlink()