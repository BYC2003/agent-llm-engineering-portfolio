from pathlib import Path

path = Path("data") / "hello.txt"

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("你好，Python\n", encoding="utf-8")

print("文件已生成：", path.resolve())
print("文件内容：", path.read_text(encoding="utf-8"))