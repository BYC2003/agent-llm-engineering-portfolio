import json
from pathlib import Path

data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)
bad_path = data_dir / "bad_student.json"

bad_path.write_text(
    '{\n  "name": "张小明",\n  "age": 18\n}\n',
    encoding="utf-8",
)

print("已创建坏 JSON 文件：", bad_path)

try:
    with bad_path.open("r", encoding="utf-8") as file:
        student = json.load(file)
except json.JSONDecodeError as exc:
    print("读取失败：文件中不是合法 JSON")
    print("错误原因：", exc.msg)
    print("出错行号：", exc.lineno)
    print("出错列号：", exc.colno)
else:
    print("读取成功：", student)
finally:
    print("文件读取尝试结束")