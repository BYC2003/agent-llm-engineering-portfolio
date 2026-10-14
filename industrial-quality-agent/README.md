# 工业质量合成数据生成器

> 仅用于学习、演示和作品集，不包含任何公司真实数据，也不可用于生产决策。

## 为什么需要它

公司工艺数据保密，不能上传到个人电脑、云平台、GitHub 或大模型。
这个项目用 Python 生成结构相似但完全合成的数据，用来开发和评测后续的 RAG/Agent。

## 生成内容

```text
data/synthetic_demo/
├─ batches.csv
├─ eval_questions.jsonl
├─ manifest.json
├─ README.md
└─ knowledge/
   ├─ sop_cleaning.md
   ├─ sop_dispensing.md
   ├─ case_dirty_nozzle.md
   └─ fmea_dispensing.md
```

## 环境

可以直接使用 `python-foundation` 的虚拟环境：

```powershell
# 回到 python-foundation 工作区
cd ..\实战项目\python-foundation

# 运行生成器
& ".\.venv\Scripts\python.exe" "..\..\industrial-quality-agent\generate_data.py" --output "..\..\industrial-quality-agent\data\synthetic_demo" --batches 120 --seed 42
```

## 运行 FastAPI 服务

当前已实现：

- `GET /health`：检查服务是否启动。
- `POST /generate`：生成合成数据，输出到 `data/api_generated`。

```powershell
# 在项目根目录使用已有虚拟环境。
cd E:\Project\0基础学agent\industrial-quality-agent

# 启动 API 服务，按 Ctrl+C 停止。
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

另开一个终端检查健康状态：

```powershell
# 正常情况下应返回 status、service 和 version。
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

发送 JSON 请求体，生成 30 条合成数据：

```powershell
# 准备请求体并转换为 JSON。
$body = @{ batch_count = 30; seed = 42 } | ConvertTo-Json

# 调用 POST /generate。
Invoke-RestMethod -Uri "http://127.0.0.1:8000/generate" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## 统一错误响应

错误响应统一包含：

```json
{
  "error_code": "REQUEST_VALIDATION_ERROR",
  "message": "请求参数校验失败",
  "details": {
    "field": "batch_count",
    "reason": "Input should be greater than or equal to 1"
  }
}
```

当前行为：

- `POST /generate` 参数不合法：HTTP 422。
- 访问不存在的路径：HTTP 404，`error_code=NOT_FOUND`。
- 未处理的服务器异常：HTTP 500，`error_code=INTERNAL_SERVER_ERROR`；异常详情只写日志，不返回客户端。

## RAG 文档加载、清洗与切分

`rag/documents.py` 负责把知识目录中的 Markdown 读取为文档对象，并继续生成可检索片段：

```python
from pathlib import Path

from rag.documents import load_markdown_documents, split_document_into_chunks

documents = load_markdown_documents(Path("data/synthetic_demo/knowledge"))
chunks = [
    chunk
    for document in documents
    for chunk in split_document_into_chunks(document)
]
```

当前流程：

```text
Markdown 文件
→ KnowledgeDocument
→ 清洗固定声明和多余空行
→ KnowledgeChunk
```

每份文档包含：

```text
doc_id      稳定文档编号
title       Markdown 一级标题
content     原始 Markdown 内容
source_path 来源文件路径
```

每个片段包含：

```text
chunk_id    片段编号，例如 sop_dispensing#0
doc_id      所属文档编号
title       所属文档标题
content     清洗并切分后的正文
source_path 来源文件路径
```

当前已实现文档加载、清洗和按子标题切分。下一阶段实现 embedding 和本地向量检索。

## 运行测试

> 不要直接执行 `python tests/test_generator.py`。测试文件应交给 pytest 运行，否则 Python 会把 `tests` 目录作为模块搜索起点，导致找不到 `quality_data`。

在项目根目录执行：

```powershell
# 让 pytest 从项目根目录开始导入模块并运行全部测试。
python -m pytest -q
```

```powershell
# 在 python-foundation 虚拟环境中运行本项目测试
& ".\.venv\Scripts\python.exe" -m pytest -q "..\..\industrial-quality-agent\tests"
```

## 验收标准

- 相同 seed 生成相同数据。
- CSV 行数等于 `--batches`。
- `yield_rate` 在 0 到 1 之间。
- 每份文档都带“合成演示”标记。
- 测试全部通过。

## 数据边界

- 不接入公司数据库。
- 不复制内网 CSV。
- 不截图公司系统。
- 不上传真实参数、客户名称和良率。
- 真实内网适配器以后单独实现，不进入公开仓库。

