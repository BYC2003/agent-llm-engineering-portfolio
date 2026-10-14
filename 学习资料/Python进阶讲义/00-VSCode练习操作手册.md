# 00：先学会在 VS Code 里练 Python

这一册不讲 Python 语法，先解决一个更基础的问题：

> 代码写在哪里，怎么运行，怎么找错，怎么调试，怎么测试，怎么提交？

如果这些操作没有理顺，明明是代码问题，也会被误以为是 VS Code 坏了。先把工具用明白，后面的 Python 学习会轻松很多。

## 一句话理解 VS Code

可以把 VS Code 想成一个“代码工作台”：

| 名称 | 通俗理解 |
|---|---|
| 项目文件夹 | 整个工作台 |
| 编辑器 | 写字和改代码的纸 |
| 资源管理器 | 查看工作台里有哪些文件 |
| 终端 | 给电脑下命令的窗口 |
| Python 解释器 | 真正执行 Python 代码的大脑 |
| `.venv` | 这个项目专用的工具箱 |
| 调试器 | 让程序停下来，逐行观察的放大镜 |
| Testing 面板 | 自动检查代码是否正确的质检台 |
| Source Control | 保存代码历史的地方 |

先分清它们，后面就不会把“路径错”“解释器错”“代码错”混在一起。

---

# 一、打开正确的项目

## 1. 这台电脑有两层目录

```text
E:\Project\0基础学agent
```

这是整个学习平台，里面放着讲义、实战项目和 Git 仓库。

```text
E:\Project\0基础学agent\实战项目\python-foundation
```

这是 Python 练习项目，里面有 `.venv`、`exercises`、`data` 和 pytest 配置。

不同的任务要打开不同层：

- 看讲义、管理整个平台：打开 `E:\Project\0基础学agent`。
- 写 Python、运行、调试、测试：打开 `E:\Project\0基础学agent\实战项目\python-foundation`。

## 2. 用 VS Code 打开练习项目

操作步骤：

1. 菜单栏选择“文件 -> 打开文件夹”。
2. 选择：

```text
E:\Project\0基础学agent\实战项目\python-foundation
```

3. 如果询问在当前窗口还是新窗口打开，选择“打开新窗口”。
4. 如果询问是否信任文件夹，选择“是，我信任作者”。

不要只双击打开一个单独的 `.py` 文件。只打开文件时，VS Code 不知道项目根目录在哪里，可能导致：

- `.venv` 找不到。
- 自定义模块导入失败。
- pytest 找不到测试。
- 相对路径指向错误位置。

## 3. 判断工作区根目录是否正确

资源管理器最上方应该显示：

```text
PYTHON-FOUNDATION
```

下面是 `.venv`、`.vscode`、`exercises`、`data` 等目录。

如果最上方显示的是 `0基础学agent`，说明你打开的是平台根目录。它适合看讲义，但不适合直接练习 Python。

---

# 二、认识 VS Code 最重要的区域

## 1. 左侧活动栏

| 图标 | 名称 | 快捷键 | 用途 |
|---|---|---|---|
| 两张纸 | 资源管理器 | `Ctrl+Shift+E` | 新建、打开、重命名文件 |
| 放大镜 | 搜索 | `Ctrl+Shift+F` | 在整个项目中找文字 |
| 分支 | Source Control | `Ctrl+Shift+G` | 查看改动、提交、切换分支 |
| 三角形加虫子 | 运行和调试 | `Ctrl+Shift+D` | 启动调试、管理断点 |
| 方块 | 扩展 | `Ctrl+Shift+X` | 安装 Python 插件 |
| 圆点/烧瓶 | Testing | 点击打开 | 运行 pytest |

## 2. 常用快捷键

| 快捷键 | 作用 |
|---|---|
| `Ctrl+S` | 保存当前文件 |
| `Ctrl+反引号` | 打开或关闭底部终端 |
| `Ctrl+Shift+P` | 打开命令面板 |
| `Ctrl+P` | 按文件名快速打开 |
| `Ctrl+F5` | 运行当前 Python 文件，不进入调试 |
| `F5` | 启动调试 |
| `Shift+F5` | 停止调试 |
| `F9` | 在当前行设置或取消断点 |
| `F10` | 调试时执行下一行，不进入函数 |
| `F11` | 调试时进入函数 |
| `Shift+Alt+F` | 格式化当前文件 |

反引号键通常在数字 `1` 左边，和 `~` 是同一个键。

## 3. 一个容易误解的现象

按 `Ctrl+F5` 后，终端可能出现和 `debugpy` 有关的文字。这不一定是按错了 `F5`。Python 扩展可能通过调试启动器来执行程序，但没有真正进入调试状态。

如果不想看到它，可以：

- 右键编辑器，选择 `Run Python File in Terminal`。
- 或者在终端显式执行：

```powershell
& ".\.venv\Scripts\python.exe" .\exercises\files_and_exceptions\01_io.py
```

---

# 三、安装必要的扩展

按 `Ctrl+Shift+X` 打开扩展面板，搜索并安装：

1. `Python`，发布者是 Microsoft。
2. `Pylance`，通常随 Python 扩展安装。
3. `Ruff`，可选用来自动检查和整理代码。

只需要 Python 扩展就能完成基础练习。不要一上来安装几十个扩展。

---

# 四、确认虚拟环境和解释器

## 1. 虚拟环境是什么

`.venv` 可以理解成“这个项目的专用工具箱”。

假设项目 A 需要旧版本库，项目 B 需要新版本库。如果都装在全局 Python 里，就会互相冲突。每个项目使用独立 `.venv`，依赖就不会串在一起。

目录通常是：

```text
python-foundation\
├─ .venv\
├─ .vscode\
├─ exercises\
└─ data\
```

`.venv` 不提交到 Git；项目依赖清单应该提交。

## 2. 先检查，不要急着重建

打开 `python-foundation` 的集成终端，确认终端提示符类似：

```text
PS E:\Project\0基础学agent\实战项目\python-foundation>
```

执行：

```powershell
& ".\.venv\Scripts\python.exe" -c "import sys; print(sys.executable)"
```

如果输出包含：

```text
python-foundation\.venv\Scripts\python.exe
```

说明已有虚拟环境可以正常使用。

## 3. 如果 `.venv` 不存在才重建

在新电脑上或者确认 `.venv` 已被删除时，执行：

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install pydantic httpx pytest
& ".\.venv\Scripts\python.exe" -c "import sys; print(sys.executable)"
```

逐条含义：

- `python -m venv .venv`：创建项目专用环境。
- `-m pip install --upgrade pip`：升级安装工具。
- `-m pip install pydantic httpx pytest`：安装后续要用的库。
- 最后一行：确认真的在使用 `.venv`。

## 4. 可以选择不激活环境

推荐始终使用明确路径：

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q
```

这样即使终端没有出现 `(.venv)`，执行的也是项目环境。

也可以临时激活：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

激活成功后，提示符通常会出现：

```text
(.venv) PS E:\Project\0基础学agent\实战项目\python-foundation>
```

如果激活脚本被系统阻止，不要因此乱运行全局 `pip install`。直接用 `.\.venv\Scripts\python.exe` 即可。

## 5. 选择 VS Code 解释器

操作步骤：

1. 按 `Ctrl+Shift+P`。
2. 输入并选择 `Python: Select Interpreter`。
3. 选择：

```text
E:\Project\0基础学agent\实战项目\python-foundation\.venv\Scripts\python.exe
```

如果列表中没有，选择“输入解释器路径”，粘贴完整路径。

解释器和终端为什么都要检查？

- 终端里运行的是某一版 Python。
- VS Code 运行、补全和调试也会选择一个解释器。
- 两边都指向 `.venv`，环境才一致。

---

# 五、写完代码后怎么运行

## 1. 标准步骤

1. 在资源管理器中新建文件，例如：

```text
exercises/files_and_exceptions/01_io.py
```

2. 输入或敲入代码。
3. 按 `Ctrl+S` 保存。
4. 点击该文件的编辑器标签，确保它是当前文件。
5. 按 `Ctrl+F5`。
6. 看底部 `TERMINAL`，不要只看编辑器有没有波浪线。

## 2. 为什么必须先保存

VS Code 运行的是磁盘上的文件。未保存的修改只存在于编辑器中，运行时可能仍是旧代码，表现就是“我明明改了，怎么没变化”。

## 3. 为什么路径按项目根目录计算

如果当前工作区根目录是 `python-foundation`，代码写：

```python
path = Path("data") / "notes.txt"
```

它通常指向：

```text
python-foundation\data\notes.txt
```

如果换了启动目录，同一个相对路径可能指向别处。最稳定的写法是：

```python
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "notes.txt"
```

意思是：先找到当前脚本所在目录，再从那里拼接 `data/notes.txt`。

---

# 六、怎样用断点调试

## 1. 正常运行和调试的区别

正常运行：

- 程序从头跑到结束。
- 你只能看打印结果。
- 出错后程序通常会停止。

调试：

- 可以指定某一行停下。
- 可以查看每个变量的当前值。
- 可以一行一行执行。
- 可以进入函数内部看问题。
- 不会只靠 `print()` 猜。

## 2. 第一次断点练习

准备代码：

```python
def add(a: int, b: int) -> int:
    result = a + b
    return result


x = 10
y = 20
answer = add(x, y)
print(answer)
```

操作：

1. 点击第 2 行行号左边，设置红色断点；也可按 `F9`。
2. 按 `F5` 启动调试。
3. 程序停在第 2 行。
4. 在左侧 `VARIABLES` 中查看 `a`、`b`。
5. 按 `F10` 执行下一行。
6. 查看 `result` 是否变成 `30`。
7. 按 `F5` 或继续按钮，让程序执行完。

以后代码没有按预期运行时，先判断：

- 这一行为什么没有执行？
- 执行到这里时变量的值到底是什么？

---

# 七、在 VS Code 中运行 pytest

## 1. pytest 是什么

pytest 是自动检查代码的工具。你写好规则，它自动运行并告诉你哪些规则通过、哪些失败。

例如：

```python
def add(a: int, b: int) -> int:
    return a + b


def test_add() -> None:
    assert add(1, 2) == 3
```

`test_add()` 就是一条自动检查规则。

## 2. 测试文件放在哪里

约定：

```text
python-foundation/
├─ ledger/
│  └─ service.py
└─ tests/
   └─ test_service.py
```

- 源码放在业务包里。
- 测试放在 `tests/`。
- 测试文件名使用 `test_*.py`。
- 测试函数名使用 `test_*`。

## 3. 用终端运行

在项目根目录执行：

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q
```

`-q` 表示简洁输出。

## 4. 用 Testing 面板运行

1. 按 `Ctrl+Shift+P`。
2. 输入 `Python: Configure Tests`。
3. 选择 `pytest`。
4. 选择 `tests` 目录。
5. 等待左侧测试图标出现。
6. 点击测试旁边的运行按钮。

如果看不到 Testing 面板，先确认打开的是 `python-foundation`，再重新配置测试。

---

# 八、用 Source Control 提交代码

Git 可以理解为“游戏存档”：一次提交保存项目在某一刻的状态。

## 1. 查看有哪些改动

点击左侧分支图标，或按 `Ctrl+Shift+G`。改动文件会显示在 `Changes` 中。

## 2. 提交步骤

1. 确认文件已保存。
2. 打开 Source Control。
3. 检查每个改动是不是你想要的。
4. 点击文件旁边的 `+`，把它加入暂存区。
5. 输入提交说明，例如：

```text
feat: practice file io
```

6. 点击 `Commit`。

提交只保存到本地 Git 仓库，不等于上传 GitHub。

## 3. 提交前检查

- 代码能不能运行？
- 测试有没有通过？
- 有没有把密码、API Key 或 `.venv` 提交进去？
- 提交说明是否能看懂？

---

# 九、每天的标准练习流程

以文件读写为例：

1. 打开 `python-foundation` 工作区。
2. 确认终端在项目根目录。
3. 确认解释器来自 `.venv`。
4. 新建 `exercises/files_and_exceptions/01_io.py`。
5. 先照敲最小例子并运行。
6. 故意改错一次，阅读 traceback。
7. 关掉示例，自己重写一遍。
8. 写一个测试验证结果。
9. 用 `F9` 和 `F5` 观察变量。
10. 提交 Git。

每节至少做三遍：

```text
照着写 -> 独立重写 -> 故意改错再修好
```

---

# 十、常见问题速查

## 1. 终端里的 Python 不是 `.venv`

执行：

```powershell
& ".\.venv\Scripts\python.exe" -c "import sys; print(sys.executable)"
```

参数含义：

- `&`：告诉 PowerShell，引号里的内容是一条要执行的程序路径。
- `-c`：让 Python 执行后面这段代码。
- `sys.executable`：打印当前 Python 程序的位置。

输出应包含 `.venv`。

## 2. 报 `ModuleNotFoundError`

先检查解释器，再检查是否在此环境中安装了依赖：

```powershell
& ".\.venv\Scripts\python.exe" -m pip show pydantic httpx pytest
```

如果缺包：

```powershell
& ".\.venv\Scripts\python.exe" -m pip install pydantic httpx pytest
```

如果是自己的包，要在项目根目录用 `python -m 包名.模块名` 运行。

## 3. `Ctrl+F5` 没有反应

检查：

- 文件是否保存。
- 当前焦点是否在要运行的 `.py` 文件。
- 是否选择了 Python 解释器。
- 底部 `TERMINAL` 是否有输出。

## 4. 中文乱码

读写文件统一写明：

```python
path.write_text(text, encoding="utf-8")
text = path.read_text(encoding="utf-8")
```

不要依赖电脑的默认编码。

## 5. 终端像卡住了

先看终端最左边有没有 `>>>`。

如果看到：

```text
>>>
```

说明你进入了 Python 交互模式，程序在等你输入 Python 代码。输入：

```python
exit()
```

再按回车即可退出。

## 6. 粘贴完整 Python 路径后卡住

下面这种命令只启动 Python，不会检查环境：

```powershell
E:\Project\0基础学agent\实战项目\python-foundation\.venv\Scripts\python.exe
```

它看起来像卡住，实际是进入了等待输入的 Python。

正确做法是附加 `-c`：

```powershell
& ".\.venv\Scripts\python.exe" -c "import sys; print(sys.executable)"
```

## 7. 测试终端卡住

按 `Ctrl+C` 停止当前命令，再重新执行：

```powershell
& ".\.venv\Scripts\python.exe" -m pytest -q
```

## 8. 找不到 Testing 面板

按 `Ctrl+Shift+P`，执行：

```text
Testing: Focus on Test Explorer View
```

如果仍然没有，重新执行 `Python: Configure Tests`。

---

# 十一、只记住这一套判断顺序

遇到问题时，不要立刻重装 Python。按下面顺序检查：

1. 我打开的文件夹对不对？
2. 终端是不是在项目根目录？
3. 当前解释器是不是来自 `.venv`？
4. 文件有没有保存？
5. 我运行的是不是当前文件？
6. 报错最后一行的异常类型和文件行号是什么？
7. 这个错误发生在代码运行前、运行中，还是测试时？

只要这七件事分清，大多数 VS Code 问题都能快速定位。