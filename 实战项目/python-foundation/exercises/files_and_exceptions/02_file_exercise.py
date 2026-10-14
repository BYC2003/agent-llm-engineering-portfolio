from pathlib import Path

path = Path("data") / "notes.txt"

path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("今天学习文件读写\n编码使用utf-8\n", encoding="utf-8")

print("文件已生成：", path.resolve())
print("内容已生成：", path.read_text(encoding="utf-8"))
