"""查询当前 fastembed 版本支持哪些 Embedding 模型（离线，不下载任何东西）。

运行方式（在 industrial-quality-agent 目录下）：
    & "..\实战项目\python-foundation\.venv\Scripts\python.exe" check_embedding_models.py
"""

from fastembed import TextEmbedding  # fastembed 的文本向量类


def main() -> None:
    models = TextEmbedding.list_supported_models()  # 读取内置的模型清单
    print(f"支持的模型总数：{len(models)}")
    print()
    print("--- 名字里带 zh 或 multilingual 的候选 ---")
    for info in models:
        # 不同版本字段名可能是 model 或 model_name，这里两个都试
        name = info.get("model") or info.get("model_name") or ""
        if "zh" in name.lower() or "multilingual" in name.lower():
            dim = info.get("dim")          # 向量维度
            size = info.get("size_in_GB")  # 模型体积（GB）
            license_name = info.get("license")  # 许可
            print(f"{name:60s} dim={dim} 体积={size}GB 许可={license_name}")


if __name__ == "__main__":
    main()  # 只有直接运行本文件时才执行
