# 02B：类型校验、HTTP、异步、pytest 和 Git 冲突

这一册看起来主题很多，其实都在解决四个问题：

1. 怎样保证数据形状正确？——类型注解和 pydantic。
2. 怎样向外部网站要数据？——HTTP、requests、httpx。
3. 怎样同时等待很多慢操作？——async / await。
4. 怎样确认代码没坏、改动可追踪？——pytest 和 Git。

不要试图一次记完所有 API。先理解每个工具“为什么存在”，再抄最小例子运行。

---

# 一、类型注解：给代码贴标签

## 1. 类型注解是什么

看这个函数：

```python
def add(a: int, b: int) -> int:
    return a + b
```

含义：

- `a: int`：希望 `a` 是整数。
- `b: int`：希望 `b` 是整数。
- `-> int`：函数打算返回整数。

它像快递箱上的标签，告诉人和编辑器：这里应该放什么。

类型注解的好处：

- 看函数签名就知道输入输出。
- VS Code 的补全和提示更准确。
- pyright / mypy 等工具可以提前找潜在问题。
- FastAPI、pydantic 等框架可以利用注解做校验和文档。

## 2. 注解默认只是提醒，不是强制

下面的代码在普通 Python 里仍然能运行：

```python
def add(a: int, b: int) -> int:
    return a + b


print(add("1", "2"))  # 12
```

为什么？因为普通函数注解默认不会在运行时拦住错误。

一句话区分：

```text
typing 注解：告诉别人“应该是”
pydantic：在运行时真的检查“是不是”
```

## 3. Python 3.10 常见写法

```python
name: str
age: int | None
scores: list[int]
mapping: dict[str, int]
```

含义：

- `str`：字符串。
- `int | None`：整数或空值 `None`。
- `list[int]`：装着整数的列表。
- `dict[str, int]`：键是字符串、值是整数的字典。

更多类型工具：

```python
from collections.abc import Iterable
from typing import Any, Callable, Literal

items: list[dict[str, object]]
callback: Callable[[int], str]
kind: Literal["income", "expense"]
anything: Any
```

- `Literal["income", "expense"]`：只能选这两个固定字符串。
- `Callable[[int], str]`：接收整数并返回字符串的函数。
- `Any`：放弃类型检查，尽量少用。

---

# 二、pydantic：门口的数据安检

## 1. 为什么需要校验

外部数据包括：

- 用户输入。
- 从 JSON 文件读出的内容。
- 网站 API 返回的数据。
- 大语言模型输出的 JSON。

这些数据不能默认相信。它们可能缺字段、类型错误或完全不是 JSON。

pydantic 像一道安检门：

```text
外部数据
-> pydantic 检查字段和类型
-> 正确：变成 Python 模型对象
-> 错误：抛出 ValidationError，指出哪里不对
```

## 2. 定义数据模型

```python
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    amount_cents: int = Field(gt=0, description="金额，单位分")
    note: str = Field(min_length=1, max_length=100)
    kind: Literal["income", "expense"] = "expense"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("note")
    @classmethod
    def strip_note(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("备注不能为空")
        return value
```

逐段理解：

- `BaseModel`：pydantic 数据模型的基础。
- `amount_cents: int`：金额应该是整数。
- `Field(gt=0)`：必须大于 0。
- `note: str`：备注是字符串。
- `Field(min_length=1, max_length=100)`：长度范围。
- `Literal[...]`：只能收入或支出。
- `default_factory`：创建新对象时生成默认时间。
- `@field_validator`：某个字段的额外检查。
- `value.strip()`：去掉前后空格。
- `raise ValueError`：校验不通过。

## 3. 使用模型

```python
raw = {
    "amount_cents": "3000",
    "note": "  午餐  ",
}

try:
    transaction = Transaction.model_validate(raw)
except Exception:
    raise
```

这里故意先不捕获，只观察正常结果。

```python
print(transaction.amount_cents)  # 3000
print(repr(transaction.note))    # '午餐'
```

pydantic 默认可能把 `"3000"` 转成整数 `3000`。这叫“宽松转换”。

严格模式：

```python
transaction = Transaction.model_validate(raw, strict=True)
```

严格模式下，字符串 `"3000"` 可能不再自动变成整数。

## 4. 捕获字段错误

```python
from pydantic import ValidationError

try:
    Transaction.model_validate({"amount_cents": -1, "note": ""})
except ValidationError as exc:
    for error in exc.errors():
        print(error["loc"])
        print(error["msg"])
```

输出会告诉你哪个字段出错、错误原因是什么。

## 5. 模型转回普通数据

```python
transaction.model_dump()
transaction.model_dump(mode="json")
transaction.model_dump_json()
```

区别：

- `model_dump()`：变成 Python 常见的字典。
- `model_dump(mode="json")`：变成适合 JSON 的简单值。
- `model_dump_json()`：直接变成 JSON 字符串。

从 JSON 字符串直接校验：

```python
text = '{"amount_cents": 100, "note": "测试"}'
transaction = Transaction.model_validate_json(text)
```

## 6. dataclass 和 pydantic 怎么选

| 场景 | 推荐 |
|---|---|
| 程序内部、数据可信、主要用来装数据 | dataclass |
| 用户输入、文件数据、API 返回、LLM 输出 | pydantic |
| 字段需要校验和自动转换 | pydantic |
| 不需要校验，想更轻量 | dataclass |

实用规则：

```text
数据刚进程序：先用 pydantic 检查
进入内部以后：可以转换成 dataclass 或普通对象
```

---

# 三、HTTP：程序怎样访问网站

## 1. HTTP 是什么

浏览器打开网页，程序调用 API，本质上都在发 HTTP 请求。

可以把 HTTP 想成去餐厅点餐：

- 请求：你告诉服务器要什么。
- 响应：服务器把结果送回来。

一个请求通常包含：

| 部分 | 例子 | 含义 |
|---|---|---|
| 方法 | GET | 查询 |
| URL | `https://api.example.com/posts/1` | 找谁要什么 |
| 查询参数 | `?page=1&limit=20` | 筛选条件 |
| 请求头 | `Accept: application/json` | 附加说明 |
| 请求体 | JSON 数据 | POST 时要发送的内容 |

常见方法：

- `GET`：读取。
- `POST`：创建。
- `PUT` / `PATCH`：更新。
- `DELETE`：删除。

响应通常包含：

- 状态码。
- 响应头。
- 响应体，常见格式是 JSON。

## 2. 状态码怎么看

| 状态码 | 通俗解释 |
|---|---|
| `200` | 成功 |
| `201` | 创建成功 |
| `400` | 请求内容有问题 |
| `401` | 没有认证或认证失败 |
| `403` | 已识别身份，但没有权限 |
| `404` | 找不到资源 |
| `429` | 请求太频繁，被限流 |
| `500` | 服务器内部错误 |
| `502/503/504` | 网关、服务暂时不可用或超时 |

状态码是服务器的一句话答复，不是每次都代表程序语法错误。

## 3. 用 requests 发起请求

```python
import requests

try:
    response = requests.get(
        "https://jsonplaceholder.typicode.com/posts/1",
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    print(data["title"])

except requests.Timeout:
    print("请求超时")

except requests.HTTPError as exc:
    print("HTTP 错误：", exc.response.status_code)

except requests.RequestException as exc:
    print("请求失败：", exc)
```

逐行解释：

- `requests.get(...)`：发一个 GET 请求。
- `timeout=10`：最多等 10 秒，不能无限等。
- `response.raise_for_status()`：如果状态码表示失败，主动抛出异常。
- `response.json()`：把响应体解析成 Python 对象。
- `Timeout`：等太久。
- `HTTPError`：状态码失败。
- `RequestException`：requests 各类网络错误的常见父类。

重要事实：

- 一定要设置超时。
- `404`、`500` 默认不一定自动抛异常，`raise_for_status()` 才会。
- `response.json()` 也可能失败，因为返回的不一定是 JSON。

## 4. 给请求添加参数

```python
response = requests.get(
    "https://jsonplaceholder.typicode.com/posts",
    params={"userId": 1},
    headers={"Accept": "application/json"},
    timeout=10,
)
response.raise_for_status()
posts = response.json()
```

- `params`：自动拼成查询参数。
- `headers`：附加请求说明。

POST：

```python
created = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "hello", "body": "world", "userId": 1},
    timeout=10,
)
created.raise_for_status()
```

`json=` 会帮你把 Python 字典转成 JSON 并设置内容类型。

## 5. httpx：更现代的选择

`requests` 主要是同步库。`httpx` 同时支持同步和异步。

同步写法：

```python
import httpx

with httpx.Client(timeout=10) as client:
    response = client.get("https://jsonplaceholder.typicode.com/posts/1")
    response.raise_for_status()
    data = response.json()
    print(data["title"])
```

`with` 的作用：

- 进入代码块时创建客户端。
- 离开时自动关闭。
- 多次请求可以复用连接，效率更好。

## 6. 用 pydantic 检查 API 响应

```python
from pydantic import BaseModel, Field, ValidationError


class Post(BaseModel):
    id: int
    user_id: int = Field(alias="userId")
    title: str
    body: str


try:
    post = Post.model_validate(response.json())
except ValidationError as exc:
    print("API 返回结构不符合预期：", exc)
```

API 的字段叫 `userId`，Python 内部想叫 `user_id`。`alias` 负责把两者对应起来。

## 7. 重试不是无脑循环

只对这些情况考虑重试：

- 连接超时、读取超时。
- HTTP `429` 请求太频繁。
- HTTP `502`、`503`、`504` 临时故障。

适合重试的通常是“查询”，不安全的是随意重试 POST。比如付款请求重试两次，可能扣两次钱。

指数退避的意思：

```text
第一次失败，等 0.5 秒
第二次失败，等 1 秒
第三次失败，等 2 秒
```

最小例子：

```python
import time
import httpx


def get_with_retry(url: str, attempts: int = 3) -> httpx.Response:
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            response = httpx.get(url, timeout=10)

            if response.status_code in {429, 502, 503, 504} and attempt < attempts:
                wait_seconds = 0.5 * 2 ** (attempt - 1)
                time.sleep(wait_seconds)
                continue

            response.raise_for_status()
            return response

        except httpx.TransportError as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(0.5 * 2 ** (attempt - 1))

    raise RuntimeError("请求多次失败") from last_error
```

生产代码还要限制总耗时，并加入随机等待，避免很多请求同时重试。

---

# 四、异步：等待的时候别干站着

## 1. 同步和异步的区别

同步像：

```text
点一杯咖啡 -> 站着等做好 -> 再点下一杯 -> 再等
```

异步像：

```text
一次提交 10 杯订单 -> 谁先做好谁先取
```

网络请求、数据库查询、文件读写等经常需要等待，适合异步。

CPU 密集任务例如大量数学计算，异步帮助不大，通常需要多进程。

## 2. async 和 await

```python
import asyncio


async def hello() -> str:
    await asyncio.sleep(1)
    return "hello"


async def main() -> None:
    result = await hello()
    print(result)


asyncio.run(main())
```

关键点：

- `async def` 定义协程函数。
- 调用 `hello()` 得到“协程对象”，不会立刻执行完。
- `await` 表示等待结果，也允许其他任务在这一刻继续运行。
- `await` 只能放在 `async def` 里面。
- 脚本入口使用 `asyncio.run(main())`。

## 3. 顺序等待和并发等待

顺序：

```python
async def sequential() -> None:
    await asyncio.sleep(1)
    await asyncio.sleep(1)
    await asyncio.sleep(1)
```

大约耗时 3 秒，因为第二件事等第一件结束。

并发：

```python
async def concurrent() -> None:
    await asyncio.gather(
        asyncio.sleep(1),
        asyncio.sleep(1),
        asyncio.sleep(1),
    )
```

大约耗时 1 秒，因为三个等待一起进行。

`asyncio.gather()` 的作用：

- 同时启动多个可等待任务。
- 收集它们的结果。
- 返回结果的顺序和输入顺序一致。

## 4. 异步 HTTP

```python
import asyncio
import httpx


async def fetch_post(
    client: httpx.AsyncClient,
    post_id: int,
) -> dict:
    response = await client.get(f"/posts/{post_id}")
    response.raise_for_status()
    return response.json()


async def main() -> None:
    async with httpx.AsyncClient(
        base_url="https://jsonplaceholder.typicode.com",
        timeout=10,
    ) as client:
        posts = await asyncio.gather(
            fetch_post(client, 1),
            fetch_post(client, 2),
            fetch_post(client, 3),
        )

        for post in posts:
            print(post["id"], post["title"])


asyncio.run(main())
```

注意：

- 异步 HTTP 使用 `httpx.AsyncClient`。
- 创建异步客户端使用 `async with`。
- 发请求使用 `await client.get(...)`。

绝不要在异步函数里使用 `requests.get()` 或 `time.sleep()`。它们会卡住整个事件循环，让其他异步任务也无法运行。

## 5. 限制并发

同时发一千个请求可能被网站封禁。用信号量限制同时运行的数量：

```python
semaphore = asyncio.Semaphore(5)


async def limited_fetch(
    client: httpx.AsyncClient,
    post_id: int,
) -> dict:
    async with semaphore:
        response = await client.get(f"/posts/{post_id}")
        response.raise_for_status()
        return response.json()
```

可以把 `Semaphore(5)` 想成只有 5 个车位。前 5 个任务能进入，其余任务在外面等。

## 6. 超时和错误隔离

给单个任务设置超时：

```python
try:
    result = await asyncio.wait_for(fetch_post(client, 1), timeout=3)
except asyncio.TimeoutError:
    print("单次请求超时")
```

让一条失败不影响整批：

```python
results = await asyncio.gather(
    fetch_post(client, 1),
    fetch_post(client, 2),
    return_exceptions=True,
)

for result in results:
    if isinstance(result, Exception):
        print("失败：", result)
    else:
        print("成功：", result["id"])
```

`return_exceptions=True` 表示异常也作为结果返回，而不是立刻中断整批。

Python 3.10 主要使用：

- `asyncio.gather`
- `asyncio.wait_for`
- `asyncio.Semaphore`

Python 3.11+ 还可以使用 `TaskGroup` 和 `asyncio.timeout`。

## 7. 异步常见错误

1. 以为写了 `async def` 就自动并发；其实还要创建多个任务并等待。
2. 调用协程却忘记 `await`，得到 `coroutine was never awaited`。
3. 在异步代码里使用阻塞函数。
4. 不设超时。
5. 不限制并发。
6. 不检查 `gather` 结果里是否混入异常。

---

# 五、pytest：自动质检

## 1. pytest 是什么

pytest 会找到测试函数，自动运行它们，并告诉你哪些通过、哪些失败。

测试函数像给程序写规则：

```python
def test_add() -> None:
    assert add(1, 2) == 3
```

`assert` 后面的条件为真，测试通过；为假，测试失败。

## 2. 安装和发现规则

安装：

```powershell
& ".\.venv\Scripts\python.exe" -m pip install pytest
```

运行：

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q
```

pytest 通常会发现：

- `test_*.py` 文件。
- `*_test.py` 文件。
- 文件里的 `test_*()` 函数。
- `Test*` 开头的测试类。

## 3. 一个测试的三步

顺序通常是：

```text
Arrange：准备数据
Act：执行要测试的函数
Assert：检查结果
```

```python
from ledger.service import calculate_total


def test_calculate_total_adds_expenses() -> None:
    transactions = [100, 250, 300]  # Arrange

    total = calculate_total(transactions)  # Act

    assert total == 650  # Assert
```

## 4. 测试异常

有些函数“正确行为”就是抛出异常：

```python
import pytest


def test_invalid_amount_raises() -> None:
    with pytest.raises(ValueError, match="金额"):
        parse_amount("abc")
```

含义：

- `pytest.raises(ValueError)`：期待这里抛 `ValueError`。
- `match="金额"`：错误信息里还应包含“金额”。

## 5. 参数化：同一规则测多组数据

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1", 100),
        ("30", 3000),
        ("12.5", 1250),
    ],
)
def test_parse_amount(raw: str, expected: int) -> None:
    assert parse_amount(raw) == expected
```

这相当于自动重复写三套测试，减少复制粘贴。

## 6. 临时文件和 fixture

不要用真实账本做测试。`tmp_path` 会给每个测试一个独立临时目录：

```python
from pathlib import Path


def test_write_and_read(tmp_path: Path) -> None:
    path = tmp_path / "items.json"
    save_items(path, ["a", "b"])
    assert load_items(path) == ["a", "b"]
```

fixture 用来准备多份测试共用的数据：

```python
import pytest


@pytest.fixture
def empty_storage(tmp_path: Path) -> Path:
    path = tmp_path / "transactions.json"
    save_transactions(path, [])
    return path


def test_empty_storage(empty_storage: Path) -> None:
    assert load_transactions(empty_storage) == []
```

可以把 fixture 想成“测试开始前的布置工作”。

## 7. Mock HTTP：不访问真实网络

真实网络会慢、会超时、会变化，不适合每次测试都访问。使用 `MockTransport` 模拟服务器：

```python
import httpx


def test_response_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"id": 1, "title": "hello"},
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
        transport=transport,
        base_url="https://fake.test",
    ) as client:
        response = client.get("/posts/1")

        assert response.json()["title"] == "hello"
```

`handler` 是“假服务器”。测试里请求它，不访问互联网。

## 8. 至少覆盖哪些测试

一个可靠的小项目至少检查：

1. 正常功能。
2. 空数据。
3. 边界值。
4. 非法输入。
5. 文件不存在。
6. 文件损坏。
7. 保存后能读回。
8. 统计结果正确。
9. 单条失败不会拖垮整批。
10. Mock API 的成功与失败响应。

核心原则：

```text
成功路径 + 边界路径 + 错误路径
```

只测“一切正常”远远不够。

---

# 六、Git 分支与冲突

## 1. 分支是什么

提交是历史存档，分支是指向某个存档的标签。

可以把 `main` 想成主线剧情，`feature/xxx` 想成支线任务：

- `main`：保持可运行、可发布。
- `feature/xxx`：开发某个新功能。
- 开发完成后，把支线合并回主线。

常用命令：

```powershell
git status
git branch
git switch main
git switch -c feature/ledger
git add .
git commit -m "feat: add ledger storage"
git push -u origin feature/ledger
```

推荐流程：

```text
更新 main
-> 新建功能分支
-> 小步修改、小步提交
-> 运行测试
-> push
-> 创建 Pull Request
-> 审查并合并
```

## 2. 冲突为什么发生

如果两个分支改了同一个文件的同一片区域，Git 不知道应该保留哪一份，于是把决定权交给你。

冲突区像这样：

```text
<<<<<<< HEAD
当前分支的内容
=======
准备合并分支的内容
>>>>>>> feature-a
```

- `HEAD`：你当前所在分支。
- `=======`：两边内容的分界线。
- `>>>>>>> feature-a`：另一半来自哪个分支。

## 3. 亲手制造一次冲突

创建实验目录：

```powershell
mkdir git-conflict-demo
cd git-conflict-demo
git init

Set-Content -Path hello.txt -Value "version: base" -Encoding utf8
git add hello.txt
git commit -m "chore: initial hello"
```

创建 `feature-a`：

```powershell
git switch -c feature-a
Set-Content -Path hello.txt -Value "version: A" -Encoding utf8
git commit -am "feat: version A"
```

回到 `main`，再创建 `feature-b`：

```powershell
git switch main
git switch -c feature-b
Set-Content -Path hello.txt -Value "version: B" -Encoding utf8
git commit -am "feat: version B"
```

尝试合并：

```powershell
git merge feature-a
```

这会冲突，因为两边都改了 `hello.txt`。

打开文件，会看到冲突标记。假设最终想要：

```text
version: A+B
```

就把冲突标记和不需要的内容全部删掉，只留最终版本。

继续合并：

```powershell
git add hello.txt
git commit -m "merge: resolve hello version conflict"
git log --oneline --graph --all
```

想放弃这次合并：

```powershell
git merge --abort
```

## 4. 解决冲突的标准步骤

1. 用 `git status` 找到冲突文件。
2. 阅读两边内容，理解各自想做什么。
3. 编辑成最终正确版本。
4. 删除 `<<<<<<<`、`=======`、`>>>>>>>`。
5. 运行测试，确认没有破坏功能。
6. `git add <文件>`。
7. `git commit`。
8. 再检查一次有没有冲突标记残留。

## 5. 初学阶段不要乱用的命令

```powershell
git reset --hard
git clean -fd
git push --force
```

风险：

- `reset --hard`：可能丢掉未提交修改。
- `clean -fd`：可能删除未跟踪文件。
- `push --force`：可能覆盖远程别人的提交。

不是永远不能用，而是必须先理解后果，并有明确目标。

---

# 七、本册练习

1. 给一个金额解析函数写至少 10 个测试。
2. 用 `httpx.MockTransport` 模拟 `200`、`404`、`429`。
3. 用 `asyncio.gather` 并发 20 个请求，并限制并发为 5。
4. 用 pydantic 校验 API 返回，缺字段时捕获 `ValidationError`。
5. 亲手制造一次 Git 冲突，解决、提交，并用一句话解释为什么冲突。
6. 在 README 写下：

```text
我理解的类型注解：
我理解的 pydantic：
我理解的同步与异步：
我理解的 pytest：
我理解的 Git 冲突：
```

不能用自己的话说清楚时，不要急着继续下一节。