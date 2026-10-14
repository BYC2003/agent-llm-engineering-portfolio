from pathlib import Path

path = Path("data") / "missing.txt"

try:
    text = path.read_text(encoding="utf-8")
except FileNotFoundError as exc:
    print("文件不存在，无法读取")
    print(exc)
else:
    print(text)
finally:
    print("本次读取尝试结束")