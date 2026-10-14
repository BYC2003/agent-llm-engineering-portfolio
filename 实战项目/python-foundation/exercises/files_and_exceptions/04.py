from pathlib import Path

path = Path("data") / "quiz.txt"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("第一行\n第二行\n", encoding="utf-8")

print("文件内容：", path.read_text(encoding="utf-8"))