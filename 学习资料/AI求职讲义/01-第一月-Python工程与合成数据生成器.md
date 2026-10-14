# 第一月讲义：Python 工程与合成数据生成器

> 目标：从“会写 Python 小练习”过渡到“能交付一个别人可运行的小项目”。
> 本月不需要学深度学习，不需要显卡。
> 核心交付：工业质量合成数据生成器。

## 一、本月目标

完成后你应该能独立做到：

- 用类型注解写函数和类。
- 用 `Path` 管理目录和文件。
- 用 `json`、`csv` 生成结构化数据。
- 用 `try/except` 给出清晰错误信息。
- 用 pytest 写至少 5 个测试。
- 用 `argparse` 接受命令行参数。
- 用 Git 提交一个完整项目。
- 把项目代码、README、测试和数据说明书整理到独立仓库。

暂不要求：

- 深入继承、元类、装饰器和异步原理。
- 训练大模型。
- 学 CUDA、分布式训练或算法论文。

## 二、本月学习顺序

### 第 1 周：工程收口

- 类型注解：`name: str`、`count: int`、`items: list[str]`。
- 函数返回类型：`-> str`、`-> None`。
- 类、`self`、`__init__` 的复习。
- `pathlib.Path` 创建目录和读写文件。
- Git 提交和 README 基础。

### 第 2 周：JSON、CSV 和异常

- `json.dumps()`、`json.loads()`。
- `csv.DictWriter` 写入表格。
- JSONL 每行一条记录。
- 参数校验和 `ValueError`。
- 写合成数据 schema。

### 第 3 周：测试和配置

- pytest 测试函数、类、文件和边界条件。
- `tmp_path` 临时目录。
- 命令行参数 `argparse`。
- 日志和错误信息。
- `requirements.txt`。

### 第 4 周：交付第一个数据生成器

- 生成批次数据 CSV。
- 生成模拟 SOP、8D、FMEA 文档。
- 生成评测问题 JSONL。
- 写出 manifest。
- README 写清运行和复现步骤。
- 用 Git 提交。

## 三、工业质量合成数据生成器

项目路径：

```text
E:\Project\0基础学agent\industrial-quality-agent
```

### 数据字段

批次数据至少包含：

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `batch_id` | 批次编号 | `B20261004-0001` |
| `product` | 模拟产品 | `光学模组-A` |
| `process_step` | 工序 | `点胶` |
| `equipment_id` | 设备编号 | `EQ-03` |
| `temperature_c` | 温度 | `25.3` |
| `pressure_kpa` | 压力 | `101.2` |
| `dispense_mg` | 点胶量 | `12.4` |
| `thickness_um` | 厚度 | `248.6` |
| `defect_type` | 缺陷类型 | `点胶不良` |
| `defect_count` | 缺陷数量 | `6` |
| `yield_rate` | 模拟良率 | `0.91` |
| `data_source` | 数据来源 | `synthetic` |

### 必须生成的目录

```text
data/synthetic_demo/
├─ batches.csv
├─ manifest.json
├─ eval_questions.jsonl
├─ knowledge/
│  ├─ sop_cleaning.md
│  ├─ sop_dispensing.md
│  ├─ case_dirty_nozzle.md
│  └─ fmea_dispensing.md
└─ README.md
```

### 项目验收条件

- `python generate_data.py` 能生成全部文件。
- 相同 `--seed` 生成相同结果。
- CSV 行数和 `--batches` 一致。
- `yield_rate` 在 `0` 到 `1` 之间。
- pytest 全部通过。
- README 写清楚数据是合成的，不能用于生产决策。
- 仓库里没有公司数据、客户名称和真实工艺参数。

## 四、每天 1-2 小时的节奏

| 时间 | 动作 |
| --- | --- |
| 10 分钟 | 看昨天的代码和报错 |
| 60-80 分钟 | 写代码、运行、修错 |
| 10-20 分钟 | 写测试、README 和提交 |

每天结束时必须有一个可运行的小结果，不要只停留在“看懂”。

## 五、第一月结束后的简历表述

可以写：

```text
工业质量合成数据生成器｜Python / CSV / JSON / pytest
- 设计制造质量数据 schema，生成批次参数、缺陷记录和良率数据。
- 构建可复现的合成数据集，支持异常注入、随机种子和批量配置。
- 为 RAG/Agent 准备模拟 SOP、FMEA、8D 文档和评测问题集。
- 使用 pytest 覆盖数据范围、文件生成和确定性复现。
```

不能写：

- 使用过公司真实数据。
- 生成了公司真实良率。
- 已在公司上线生产系统。

## 六、本节总结问题

1. 为什么合成数据能让 AI 项目继续推进，同时不触碰公司保密数据？
2. 数据生成器为什么要设计 `seed`、输出目录和批次数量这些参数？
3. 为什么生成数据后还要写 pytest、manifest 和 README，而不是只保存一个 CSV？


## 七、生成器主流程拆解（2026-10-04）

### 本节目标

不重学 Python 基础，只解决一个工程问题：看懂数据生成器如何把“参数”变成“可复现的数据集”。

### 代码主线

1. `generate_data.py` 负责命令行参数，`generator.py` 负责数据生成。
2. `__init__()` 先检查 `batch_count` 和 `seed`，再保存配置并创建独立的随机数生成器。
3. `generate()` 只做总调度：创建目录、生成数据、写文件、生成 manifest、返回 manifest。
4. `_generate_batches()` 用固定规则和随机数生成每一行批次数据。
5. `_write_batches()`、`_write_documents()`、`_write_questions()` 分别写出 CSV、Markdown 和 JSONL。

### 本节练习

打开 `industrial-quality-agent\tests\test_generator.py`，在文件末尾独立增加一个测试：

- 测试名称：`test_negative_seed_raises_value_error`
- 输入：`batch_count=1`、`seed=-1`
- 预期：创建 `SyntheticQualityGenerator` 时抛出 `ValueError`
- 提示：参考现有的 `test_invalid_batch_count_raises_value_error`
- 完成后运行：`python -m pytest -q`
- 验收：现有 4 项测试加新测试共 5 项全部通过

### 本节总结问题

1. 为什么生成器使用 `random.Random(seed)`，而不是直接调用全局 `random`？
2. 为什么 `generate()` 要把“在内存中生成数据”和“写入磁盘”分成两步？
3. 相同 `seed` 测试和非法参数测试分别保护了生成器的什么能力？

## 八、讲解复述批改（2026-10-05）

### 正确部分

1. `random.Random(seed)` 使用独立的随机数状态，不会与调用全局 `random` 的其他代码共享状态，因此可以减少外部代码和执行顺序对结果的影响。
2. `generate()` 是总调度方法。它自己不负责所有细节，而是按顺序调用生成和写入方法，让“生成数据”和“写文件”的职责保持分离。

### 需要纠正

“相同 seed 是为了防止数据雷同过多”不正确。

- 相同 seed 的目标是**可复现**：相同代码、相同参数、相同 seed 会得到完全相同的结果。
- 不同 seed 才会产生不同的随机序列，用于生成不同版本的数据。
- 负 seed 在 Python 的 `random.Random(-1)` 中实际上可以运行，并不会天然生成“异常数据”。
- 项目在 `__init__()` 中拒绝负 seed，是为了定义清楚的参数契约，让允许范围和非法输入边界保持一致。

### 本节追问

1. 两次运行都使用 `seed=42`，哪些内容应该完全相同，为什么？
2. 如果另一个模块也调用全局 `random`，为什么可能破坏数据生成实验的可复现性？
3. `random.Random(-1)` 能够运行，为什么本项目仍然选择拒绝负 seed？

### 第二轮回答批改（2026-10-05）

1. “相同 seed 会得到相同随机数据，因为代码、参数和 seed 相同”：正确。
2. “其他模块调用随机数函数会改变生成结果”：只在一个前提下正确，即生成器和外部代码共用全局 `random`。当前生成器使用独立的 `self.rng`，所以其他模块调用全局 `random` 不会影响它。
3. “项目把 seed 的合法范围定义为非负整数”：正确。这是项目自己的参数契约，不是因为 Python 无法接受负数 seed。

## 九、为什么不能直接运行测试文件（2026-10-05）

### 现象

直接执行：

```powershell
python tests/test_generator.py
```

出现：

```text
ModuleNotFoundError: No module named 'quality_data'
```

### 根因

- 直接执行普通 Python 脚本时，Python 会把“脚本所在目录”放到 `sys.path[0]`。
- 本例中脚本位于 `tests`，所以 Python 主要从 `tests` 目录寻找模块。
- `quality_data` 包实际位于项目根目录 `industrial-quality-agent`，因此直接执行时找不到它。
- 测试文件是交给 pytest 发现和执行的，不应该当作普通应用程序入口直接运行。

### 正确命令

在项目根目录执行：

```powershell
# -m pytest：让 Python 以模块方式启动 pytest。
# 从项目根目录启动后，quality_data 可以被正确导入。
python -m pytest -q
```

### 本节总结问题

1. 直接执行 `python tests/test_generator.py` 时，Python 会把哪个目录放到 `sys.path[0]`？
2. 为什么从项目根目录执行 `python -m pytest -q` 可以导入 `quality_data`？
3. 测试文件为什么应该交给 pytest 运行，而不是直接当作程序执行？

### 零基础补充：Python 如何寻找模块（2026-10-05）

可以把 `sys.path` 理解成 Python 的“模块地址簿”。执行：

```python
from quality_data.generator import SyntheticQualityGenerator
```

Python 会按照 `sys.path` 中的目录逐个查找：

```text
有没有 quality_data 这个文件夹？
有没有 quality_data/generator.py 这个文件？
```

直接执行：

```powershell
python tests/test_generator.py
```

此时 Python 把 `tests` 目录放在地址簿第一位，地址簿中没有项目根目录，因此找不到根目录下的 `quality_data`。

从项目根目录执行：

```powershell
python -m pytest -q
```

`-m` 表示把 pytest 当成模块运行。此时当前目录就是项目根目录，Python 能在当前目录找到 `quality_data`。此外，pytest 会负责发现 `test_` 开头的函数、提供 `tmp_path` 等工具，并报告测试结果。

测试文件不能直接运行还有一个原因：它只“定义”了测试函数，没有在末尾主动调用这些函数。直接执行通常不会自动运行测试。

### 更基础的总结问题

1. `sys.path` 可以理解成什么？
2. 从项目根目录运行 `python -m pytest -q` 时，Python 为什么能找到 `quality_data`？
3. 为什么测试文件应交给 pytest 运行，而不是直接当作普通程序运行？

### 再简化：把文件夹当成房间（2026-10-05）

```text
industrial-quality-agent/   ← 项目大楼
├─ quality_data/            ← 房间 A
│  └─ generator.py
└─ tests/                   ← 房间 B
   └─ test_generator.py
```

- 项目根目录下有 `quality_data`，检查结果是 `True`。
- `tests` 目录下没有 `quality_data`，检查结果是 `False`。
- 直接运行 `python tests/test_generator.py`，相当于站在房间 B 里找房间 A，找不到。
- 从项目根目录运行 `python -m pytest -q`，相当于站在项目大楼入口，再让 pytest 去房间 B 找测试，因此能找到房间 A。
- 测试函数需要由 pytest 发现和调用。直接把测试文件当普通程序运行，并不会自动执行全部 `test_` 函数。

### 最简单的三个问题

1. `quality_data` 文件夹在项目根目录，还是在 `tests` 文件夹里面？
2. 正确的测试命令是 `python tests/test_generator.py`，还是 `python -m pytest -q`？
3. 为什么应该让 pytest 去找并运行测试函数？

### 回答批改（2026-10-05）

1. `quality_data` 在 `industrial-quality-agent` 项目根目录：正确。
2. 测试命令是 `python -m pytest -q`：正确。
3. pytest 自动寻找以 `test` 开头的测试函数：正确。

当前状态：能用文件夹类比区分“直接运行测试文件”和“用 pytest 运行测试”，标记为基本掌握并继续巩固。

## 十、pytest.mark.parametrize 参数化测试（2026-10-05）

### 本节目标

把三个结构相同、只有参数不同的非法参数测试，合并成一个参数化测试。

### 原理

普通测试函数只有一组参数：

```python
# 这个函数只会检查 batch_count=0 这一种情况。
def test_invalid_batch_count_raises_value_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        SyntheticQualityGenerator(tmp_path, batch_count=0, seed=1)
```

参数化测试把多组数据放入一个列表，pytest 会逐行取出数据，并用同一段测试逻辑重复执行。

```python
# parametrize 把每组参数转换成一次独立测试。
@pytest.mark.parametrize(
    # 参数名要和测试函数的参数名一一对应。
    ("batch_count", "seed"),
    [
        (0, 1),       # batch_count 小于下界
        (10001, 1),   # batch_count 大于上界
        (1, -1),      # seed 为负数
    ],
)
def test_invalid_parameters_raise_value_error(
    tmp_path: Path,
    batch_count: int,
    seed: int,
) -> None:
    # 每组参数都必须触发 ValueError。
    with pytest.raises(ValueError):
        SyntheticQualityGenerator(
            tmp_path,
            batch_count=batch_count,
            seed=seed,
        )
```

### 运行结果怎样理解

原来的三个测试函数被替换后，pytest 仍然会执行三组非法参数，所以总测试数量仍然是 6：

```text
......                                                                   [100%]
6 passed
```

pytest 输出中还会看到三个参数化编号，例如：

```text
test_invalid_parameters_raise_value_error[0-1]
test_invalid_parameters_raise_value_error[10001-1]
test_invalid_parameters_raise_value_error[1--1]
```

### 本节练习

打开：

`E:\Project\0基础学agent\industrial-quality-agent\tests\test_generator.py`

完成以下步骤：

1. 删除末尾三个独立测试函数。
2. 用一个 `@pytest.mark.parametrize(...)` 测试替换它们。
3. 参数行包含 `(0, 1)`、`(10001, 1)`、`(1, -1)`。
4. 保留中文注释。
5. 从项目根目录运行 `python -m pytest -q`。
6. 验收标准仍然是 `6 passed`。

### 本节总结问题

1. `pytest.mark.parametrize` 的作用是什么？
2. 为什么三个参数组合合并到一个函数后，pytest 仍然会执行三个测试用例？
3. `tmp_path` 为什么不需要写进 `parametrize` 的参数列表？

### 回答批改与保存检查（2026-10-05）

1. “参数化测试避免重复复制函数”：正确。
2. “提供三组参数，所以执行三个测试用例”：正确。
3. “`tmp_path` 由 pytest 自动生成”：方向正确，更准确地说，`tmp_path` 是 pytest 提供的 fixture；它和 `parametrize` 是两套独立机制。参数表只变化 `batch_count` 和 `seed`，`tmp_path` 由 pytest 为每组测试单独提供。

截图中的参数化代码是正确的，但编辑器标签仍显示未保存圆点，说明磁盘文件还是旧版。必须先按 `Ctrl+S` 保存，再从项目根目录运行：

```powershell
# 保存后再运行，确保参数化版本真正生效。
python -m pytest -q
```

预期结果：

```text
......                                                                   [100%]
6 passed
```

### 保存后的确认问题

1. `parametrize` 控制测试函数中的哪两个参数？
2. `tmp_path` 由 `parametrize` 提供，还是由 pytest fixture 提供？
3. 为什么看到编辑器标签有圆点时，必须先保存再运行测试？

### 完成确认（2026-10-05）

参数化测试已经保存并生效：

```text
test_invalid_parameters_raise_value_error[0-1]
test_invalid_parameters_raise_value_error[10001-1]
test_invalid_parameters_raise_value_error[1--1]
6 tests collected
6 passed
```

三个确认问题均回答正确：

1. 参数表控制 `batch_count` 和 `seed`。
2. `tmp_path` 由 pytest fixture 提供。
3. 未保存的代码只存在于编辑器，不能用来证明磁盘版本已经生效。

下一节：修改生成器参数或缺陷规则，重新生成数据并检查 CSV 变化。

## 十一、修改异常间隔并验证 CSV（2026-10-05）

### 原规则

生成器中当前写的是：

```python
# index 能被 13 整除时，把该批次视为异常。
anomaly = index % 13 == 0
```

`%` 表示取余数。`13 % 13` 的结果是 `0`，所以这些批次会成为点胶不良：

```text
13、26、39、52……
```

从现有 CSV 查询到的结果正是：

```text
B20261004-0013
B20261004-0026
B20261004-0039
B20261004-0052
```

### 本节修改

打开：

`E:\Project\0基础学agent\industrial-quality-agent\quality_data\generator.py`

找到第 77 行：

```python
anomaly = index % 13 == 0
```

修改为：

```python
# 改成每 10 个批次注入一次异常。
anomaly = index % 10 == 0
```

然后按 `Ctrl+S` 保存。

### 单独生成新数据

不要覆盖原来的 `synthetic_demo`，而是在项目根目录执行：

```powershell
# 把修改后的 30 条数据生成到独立目录，便于和原数据对比。
python generate_data.py --output data/anomaly_interval_10 --batches 30 --seed 42
```

### 检查异常批次

```powershell
# 读取新生成的 CSV，只显示点胶不良批次。
Import-Csv -LiteralPath '.\data\anomaly_interval_10\batches.csv' -Encoding UTF8 |
    Where-Object { $_.defect_type -eq '点胶不良' } |
    Select-Object batch_id, process_step, defect_type, defect_count, dispense_mg |
    Format-Table -AutoSize
```

预期异常批次编号：

```text
B20261004-0010
B20261004-0020
B20261004-0030
```

### 本节总结问题

1. `index % 10 == 0` 会让哪些批次的 `anomaly` 变成 `True`？
2. 为什么要把新数据生成到 `anomaly_interval_10`，而不是覆盖 `synthetic_demo`？
3. 修改异常间隔后，现有 6 项测试可能仍然通过，这说明了测试覆盖方面存在什么问题？

## 十二、检查新 CSV 并与原 CSV 对比（2026-10-05）

### 先明确比较目标

不要直接把两份 CSV 从头到尾逐行比较，因为：

- 原文件：120 条。
- 新文件：30 条。
- 行数不同，直接比较会得到大量无意义差异。

本节比较的是：

1. 两份 CSV 的列是否一致。
2. `defect_type` 为“点胶不良”的批次编号。
3. 异常规则是否从 13 的倍数变成 10 的倍数。

### 方法一：直接查看

在 VS Code 中打开：

`E:\Project\0基础学agent\industrial-quality-agent\data\anomaly_interval_10\batches.csv`

也可以直接用 Excel 打开，然后筛选 `defect_type` 列中的“点胶不良”。

### 方法二：用 PowerShell 筛选异常批次

```powershell
# 读取新生成的 CSV。
$newRows = Import-Csv -LiteralPath '.\data\anomaly_interval_10\batches.csv' -Encoding UTF8

# 查看总行数，预期是 30。
$newRows.Count

# 只筛选点胶不良批次。
$newRows |
    Where-Object { $_.defect_type -eq '点胶不良' } |
    Select-Object batch_id, process_step, defect_type, defect_count, dispense_mg |
    Format-Table -AutoSize
```

实际结果是：

```text
B20261004-0010
B20261004-0020
B20261004-0030
```

### 方法三：比较新旧异常批次

```powershell
# 读取原数据和新数据。
$oldRows = Import-Csv -LiteralPath '.\data\synthetic_demo\batches.csv' -Encoding UTF8
$newRows = Import-Csv -LiteralPath '.\data\anomaly_interval_10\batches.csv' -Encoding UTF8

# 先取原数据前 30 条，保证和新数据范围一致。
$oldAnomalies = $oldRows |
    Select-Object -First 30 |
    Where-Object { $_.defect_type -eq '点胶不良' }

# 取出新数据的全部异常批次。
$newAnomalies = $newRows |
    Where-Object { $_.defect_type -eq '点胶不良' }

# 比较异常批次编号。
Compare-Object `
    -ReferenceObject $oldAnomalies.batch_id `
    -DifferenceObject $newAnomalies.batch_id `
    -PassThru
```

实际对比结果：

```text
NEW_ONLY=B20261004-0010
NEW_ONLY=B20261004-0020
NEW_ONLY=B20261004-0030
OLD_ONLY=B20261004-0013
OLD_ONLY=B20261004-0026
```

含义：

- 新规则增加了 10、20、30 这三个异常批次。
- 原来前 30 条中的 13、26 不再异常。
- 原文件共 120 条，所以其完整异常集合还有 39、52、65 等。

### 方法四：快速比较表头

```powershell
# 把两份 CSV 的列名转换成字符串，再比较是否相同。
$oldColumns = $oldRows[0].PSObject.Properties.Name -join ','
$newColumns = $newRows[0].PSObject.Properties.Name -join ','
$oldColumns -eq $newColumns
```

预期结果是：

```text
True
```

### 为什么后面的随机字段可能也不同

异常分支会调用不同数量的随机操作。更改异常间隔后，从第 10 条开始，后续随机序列可能整体偏移。因此不能只要求异常批次编号变化，其他数值可能也发生变化。

### 本节总结问题

1. 为什么 120 条的原 CSV 和 30 条的新 CSV 不适合直接逐行比较？
2. 如何只筛选出 `defect_type` 为“点胶不良”的记录？
3. 新规则下前 30 条中的异常批次编号是什么？

## 十三、完整数据集与筛选结果的区别（2026-10-05）

### 为什么新 CSV 里还有外观检查等数据

`anomaly_interval_10` 是“异常间隔改成 10 后生成的完整数据集”，不是“只包含点胶不良的数据集”。

生成器会对每一批数据生成一行完整记录：

```python
# anomaly 决定这一行是否走异常分支。
anomaly = index % 10 == 0

# 异常批次固定为点胶工序和点胶不良。
if anomaly:
    process_step = "点胶"
    defect_type = "点胶不良"

# 非异常批次仍然会随机选择其他工序和轻微缺陷。
else:
    process_step = self.rng.choice(steps)
    defect_type = self.rng.choice(normal_defects)
```

因此，非异常批次仍可能出现：

- `process_step = 点胶`
- `process_step = 清洗`
- `process_step = 厚度检测`
- `process_step = 外观检查`
- `defect_type = 正常`
- `defect_type = 轻微脏污`
- `defect_type = 轻微划伤`

新 CSV 的实际统计是：

```text
工序统计：
点胶 12
厚度检测 6
清洗 5
外观检查 7

缺陷统计：
点胶不良 3
轻微划伤 11
轻微脏污 5
正常 11
```

### 两个字段不能混淆

- `process_step`：这一批经过什么工序，例如 `点胶` 或 `外观检查`。
- `defect_type`：这一批记录了什么缺陷，例如 `点胶不良`、`轻微划伤` 或 `正常`。

所以一行完全可能是：

```text
process_step = 点胶
defect_type = 正常
```

它的意思是“经过点胶工序，但没有异常缺陷”，不代表这行是异常数据。

### 筛选不会修改源文件

下面的命令只是读取并临时筛选，不会改变 `batches.csv`：

```powershell
# 只查看点胶不良异常批次，不修改源 CSV。
$rows = Import-Csv -LiteralPath '.\data\anomaly_interval_10\batches.csv' -Encoding UTF8
$rows |
    Where-Object { $_.defect_type -eq '点胶不良' } |
    Format-Table batch_id, process_step, defect_type
```

如果希望真正生成一份只包含异常记录的 CSV：

```powershell
# Export-Csv 会创建一份新的筛选结果文件，原 CSV 保持不变。
$rows |
    Where-Object { $_.defect_type -eq '点胶不良' } |
    Export-Csv -LiteralPath '.\data\anomaly_interval_10\anomalies_only.csv' -NoTypeInformation -Encoding UTF8
```

### 本节总结问题

1. `anomaly_interval_10` 保存的是完整数据集，还是只保存点胶不良？
2. `process_step` 和 `defect_type` 分别表示什么？
3. 为什么一行可以同时是“点胶工序”和“正常缺陷类型”？

## 十四、批次数量与异常间隔不是同一个参数（2026-10-05）

### 两个参数分别控制什么

`--batches` 控制要生成多少行：

```powershell
# 生成 120 行。
python generate_data.py --output data/synthetic_demo --batches 120 --seed 42

# 生成 30 行。
python generate_data.py --output data/anomaly_interval_10 --batches 30 --seed 42
```

`index % 10 == 0` 控制哪些行属于异常，不控制总行数：

```python
# 在已经生成的批次范围内，每 10 条注入一次异常。
anomaly = index % 10 == 0
```

### 为什么原数据 120 行，新数据 30 行

- 原数据的 manifest 记录：`"batch_count": 120`。
- 新数据的 manifest 记录：`"batch_count": 30`。
- 新数据生成命令使用了 `--batches 30`。
- 这个 30 是为了做小规模验证，不是为了筛选异常。

### 如果两份数据都要 120 行

使用同样的批次数量：

```powershell
# 新规则也生成 120 行。
python generate_data.py --output data/anomaly_interval_10_120 --batches 120 --seed 42
```

此时：

- 原规则 `% 13 == 0`：异常批次为 13、26、39……117，共 9 条。
- 新规则 `% 10 == 0`：异常批次为 10、20、30……120，共 12 条。

### 本节总结问题

1. `--batches 30` 控制 CSV 总行数，还是控制异常频率？
2. `index % 10 == 0` 控制 CSV 总行数，还是控制异常频率？
3. 如果原数据和新数据都要 120 行，新数据命令中的 `--batches` 应填写多少？

## 十五、相同 seed 为什么不保证不同配置结果相同（2026-10-05）

### 新数据确实是一次重新生成

每次创建生成器都会执行：

```python
# 每次运行都创建一套新的随机状态。
self.rng = random.Random(seed)
```

相同 seed 只能保证：

```text
相同代码
+ 相同参数
+ 相同随机调用顺序
= 相同结果
```

本次新旧数据有两个配置差异：

```text
异常间隔：13 -> 10
总批次数：120 -> 30
```

所以不能把新数据理解成原数据的简单副本或筛选结果。

### 实际比较结果

比较原数据的前 30 条和新数据：

- 第 1 到第 9 条相同。
- 第 10 条开始出现差异。
- 一个新数据运行中，不同行是否相同可能受后续随机序列影响。

第 10 条是第一条关键差异：

```text
原规则：10 % 13 != 0，属于普通批次
新规则：10 % 10 == 0，属于异常批次
```

新异常分支会调用不同数量的随机操作，因此从第 10 条以后，随机序列可能发生偏移。

### 受控实验原则

如果目标是只比较“异常间隔”这一个变化：

```text
保持 seed 相同
保持 batch_count 相同
只把 13 改成 10
```

例如：

```powershell
# 新规则仍生成 120 条，便于和原数据同范围比较。
python generate_data.py --output data/anomaly_interval_10_120 --batches 120 --seed 42
```

### 本节总结问题

1. 相同 seed 为什么不能保证不同代码或不同参数得到相同结果？
2. 为什么新旧数据从第 10 条开始出现差异？
3. 如果只想比较异常间隔变化，应该保持哪些条件相同？

## 十六、如何判断点胶不良：index、Excel 行号和参数值（2026-10-05）

### 判断顺序

生成器先判断循环编号，再决定是否设置异常：

```python
# index 是循环编号：1、2、3……10……
for index in range(1, self.batch_count + 1):
    # 只判断 index 能否被 10 整除。
    anomaly = index % 10 == 0

    # 判断为异常后，直接指定工序和缺陷类型。
    if anomaly:
        process_step = "点胶"
        defect_type = "点胶不良"
```

它不会判断 `temperature_c`、`pressure_kpa`、`dispense_mg` 或 `thickness_um` 是否满足某个阈值。

### Excel 行号和循环编号的关系

CSV 第一行是表头：

```text
Excel 第 1 行：列名
Excel 第 2 行：第 1 个数据记录，batch_id = B20261004-0001，index = 1
Excel 第 3 行：第 2 个数据记录，batch_id = B20261004-0002，index = 2
...
Excel 第 11 行：第 10 个数据记录，batch_id = B20261004-0010，index = 10
```

所以图中看似“第 11 行”的数据，对应的是循环编号 `index = 10`。

```python
# 10 能被 10 整除，余数为 0。
anomaly = 10 % 10 == 0
# anomaly 的结果是 True。
```

### 四个数值分别是什么

图中数值：

```text
26.44, 99.88, 14.89, 250.15
```

对应字段是：

```text
temperature_c = 26.44   # 温度
pressure_kpa = 99.88   # 压力
dispense_mg = 14.89    # 点胶量
thickness_um = 250.15  # 厚度
```

这些数值不是异常判定条件，而是异常判定完成后生成的参数。

### 异常后为什么这些数值会变化

```python
# 先判定异常。
if anomaly:
    process_step = "点胶"
    defect_type = "点胶不良"

    # 异常发生后，再让温度和点胶量偏离正常范围。
    temperature += self.rng.uniform(1.5, 3.0)
    dispense += self.rng.uniform(2.0, 4.0)
```

因此：

- `temperature_c = 26.44` 是异常处理后的结果。
- `dispense_mg = 14.89` 也是异常处理后的结果。
- 它们不是“因为等于 26.44 或 14.89 才异常”。
- 真正的判断依据是 `batch_id` 最后的编号或循环变量 `index`。

### 判断异常最简单的方法

优先查看这两个字段：

```text
process_step = 点胶
defect_type = 点胶不良
```

不要通过 `temperature_c`、`dispense_mg` 等参数反推异常。

### 本节总结问题

1. `index % 10 == 0` 判断的是 CSV 中的哪个字段？
2. Excel 第 11 行对应第几个数据记录，对应的 `index` 是多少？
3. `26.44` 和 `14.89` 是异常判断条件，还是异常发生后生成的参数结果？

### 回答批改（2026-10-05）

1. “判断的是序号 `batch_id`”：基本正确，但更准确地说，代码直接判断的是循环变量 `index`。`batch_id` 是之后用 `index` 拼出来的，例如 `index=10` 生成 `B20261004-0010`。
2. “第 10 个数据记录，`index=10`”：正确。Excel 表头占第 1 行，所以 Excel 第 11 行是第 10 个数据记录。
3. “温度和点胶量是异常后生成的参数结果”：正确。异常先由 `index % 10 == 0` 判定，参数偏移发生在判定之后。

## 十七、生成规则与参数检测的区别（2026-10-05）

### 生成器中的真实判定顺序

```python
# 第一步：用循环编号判断是否为异常。
anomaly = index % 10 == 0

# 第二步：异常时直接设置缺陷标签。
if anomaly:
    process_step = "点胶"
    defect_type = "点胶不良"

    # 第三步：异常确定后再调整温度和点胶量。
    temperature += self.rng.uniform(1.5, 3.0)
    dispense += self.rng.uniform(2.0, 4.0)
```

所以：

- 生成数据的真实规则：`index % 10 == 0`。
- 数据中的真实标签：`defect_type = 点胶不良`。
- 温度和点胶量：异常确定后生成的观测特征。

### 统计结果

对新数据按 `defect_type` 分组后：

```text
缺陷类型   数量   平均温度   平均点胶量
点胶不良     3     27.31      13.97
轻微划伤    11     24.91      11.76
轻微脏污     5     25.02      12.00
正常       11     24.96      11.99
```

可以看出，点胶不良组的温度和点胶量整体偏高。

### 为什么“看温度、点胶量判断异常”也有道理

这个过程叫“异常检测”：

- 温度、点胶量是模型可以使用的特征。
- `defect_type` 是已知的真实标签，可以用于评估检测结果。
- 真实生产中未必有可靠标签，因此需要用参数阈值、统计控制或模型估计异常。

但要区分：

```text
生成数据的规则：先由 index 决定异常，再生成参数。
分析数据的规则：根据已有参数推测某条记录是否异常。
```

前者是“原因”，后者是“检测”。

### 终端命令不要写进 Python 文件

错误做法：把 PowerShell 命令粘贴到 `generator.py`，然后运行 Python，会出现 `SyntaxError`。

正确做法：

- 上半部分编辑器：写 Python 代码。
- 下方终端：运行 PowerShell 命令。
- 终端提示符应以 `PS E:\...>` 开头。

```powershell
# 这段命令应粘贴到 VS Code 的终端，而不是 generator.py。
$rows = Import-Csv -LiteralPath '.\data\anomaly_interval_10\batches.csv' -Encoding UTF8
$rows |
    Where-Object { $_.defect_type -eq '点胶不良' } |
    Export-Csv -LiteralPath '.\data\anomaly_interval_10\anomalies_only.csv' -NoTypeInformation -Encoding UTF8
```

### 本节总结问题

1. 生成器中最早决定异常的是 `index`、温度，还是点胶量？
2. 温度和点胶量可以作为异常检测的什么？
3. PowerShell 命令应该写在编辑器代码区，还是 VS Code 终端？

## 十八、为什么生成器先用 index，而不是先看参数（2026-10-05）

### 关键区别

当前生成器做的是“异常注入”，不是“异常检测”。

```text
生成数据：
先决定这一条是否异常，再生成对应的温度和点胶量。

检测异常：
先取得温度和点胶量，再推测这一条是否异常。
```

两者方向相反。

### 为什么生成器先用 index

生成器需要一组确定的“真实答案”，也就是标签：

```python
# 每 10 条指定一条异常，标签是确定的。
anomaly = index % 10 == 0

if anomaly:
    # 真实答案：这条属于点胶不良。
    defect_type = "点胶不良"

    # 再制造与点胶不良一致的异常参数。
    temperature += self.rng.uniform(1.5, 3.0)
    dispense += self.rng.uniform(2.0, 4.0)
```

这样做的目的：

1. 保证数据集中一定有异常样本。
2. 控制异常比例，例如每 10 条有 1 条。
3. 生成已知真值的标签，方便后续评测检测算法。
4. 让异常样本的参数具有明显偏移，便于分析。

这和工业生产中的 DOE 类似：先设计试验条件，再得到试验结果。

### 真实生产中的方向

真实生产时通常没有提前写好的 `defect_type` 标签，只能采集：

```text
温度
压力
点胶量
厚度
设备编号
工序数据
```

检测系统需要使用这些参数推测：

```text
这条数据是否异常？
可能属于哪类异常？
置信度是多少？
```

所以在实际检测阶段，你的想法是正确的：应该看参数。参数叫“特征”，异常类别叫“标签”。

### 完整流程

```text
阶段一：合成数据生成
index 决定真实标签
→ 再根据标签调整参数
→ 得到已知答案的数据集

阶段二：异常检测
读取温度、点胶量等参数
→ 不读取真实标签
→ 模型预测是否异常

阶段三：评测
比较预测结果和真实标签
→ 计算准确率、召回率等指标
```

生成器中的 `index` 就像考试答案，检测模型在正式考试时看不到答案，只能用参数推断答案。

### 本节总结问题

1. 当前生成器的目标是制造已知异常标签，还是检测未知异常？
2. 真实生产中的温度、点胶量等参数在检测任务里称为什么？
3. 为什么不能把生成时的 `index` 直接当作未来检测模型的输入特征？

## 十九、用参数做简单异常检测（2026-10-05）

### 本节目标

不看 `index`、`batch_id` 和 `defect_type`，只使用两个参数进行预测：

```text
temperature_c
dispense_mg
```

然后用真实的 `defect_type` 检查预测是否正确。

### 特征和标签

```text
特征：temperature_c、dispense_mg
真实标签：defect_type
预测结果：normal 或 dispensing_defect
```

规则暂时定义为：

```text
temperature_c >= 26.0
并且
dispense_mg >= 13.0
```

满足条件就预测为“点胶不良”。

### 完整练习代码

新建文件：

`E:\Project\0基础学agent\industrial-quality-agent\analyze_anomalies.py`

```python
from __future__ import annotations

import csv
from pathlib import Path


def load_rows(path: Path) -> list[dict[str, str]]:
    """读取 CSV，并返回字典列表。"""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        # DictReader 会把第一行表头作为字典键。
        return list(csv.DictReader(file))


def predict_anomaly(row: dict[str, str]) -> bool:
    """只使用参数预测是否为点胶不良。"""
    # 特征一：温度。
    temperature = float(row["temperature_c"])

    # 特征二：点胶量。
    dispense = float(row["dispense_mg"])

    # 两个阈值同时满足时，预测为异常。
    return temperature >= 26.0 and dispense >= 13.0


def main() -> None:
    """运行规则检测，并和真实标签比较。"""
    path = Path("data/anomaly_interval_10/batches.csv")
    rows = load_rows(path)

    # 四个计数用于评估检测结果。
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for row in rows:
        # 真实标签：CSV 中预先记录的答案。
        actual = row["defect_type"] == "点胶不良"

        # 预测结果：只看温度和点胶量。
        predicted = predict_anomaly(row)

        if actual and predicted:
            true_positive += 1
        elif not actual and predicted:
            false_positive += 1
        elif not actual and not predicted:
            true_negative += 1
        else:
            false_negative += 1

    total = len(rows)
    accuracy = (true_positive + true_negative) / total

    print(f"TP 实际异常且预测异常：{true_positive}")
    print(f"FP 实际正常但预测异常：{false_positive}")
    print(f"TN 实际正常且预测正常：{true_negative}")
    print(f"FN 实际异常但预测正常：{false_negative}")
    print(f"准确率：{accuracy:.2%}")


if __name__ == "__main__":
    # 直接运行本文件时执行检测。
    main()
```

### 运行命令

在项目根目录执行：

```powershell
# 运行参数阈值检测器。
python analyze_anomalies.py
```

预期结果：

```text
TP 实际异常且预测异常：3
FP 实际正常但预测异常：0
TN 实际正常且预测正常：27
FN 实际异常但预测正常：0
准确率：100.00%
```

### 重要限制

- 当前阈值是根据这 30 条小样本挑出来的，不能证明在真实生产中也能达到 100%。
- `defect_type` 只能用于评估，不能作为检测特征。
- `batch_id` 也不能作为检测特征，因为它携带了人工注入的序号。
- 后续应该把数据分成训练集和测试集，再评价检测方法。

### 本节总结问题

1. 检测器使用了哪些特征，哪些字段不能作为特征？
2. `defect_type` 在检测和评估阶段分别有什么作用？
3. 为什么 30 条小样本上的 100% 准确率不能直接代表真实生产性能？

## 二十、AND 与 OR 阈值规则对比（2026-10-07）

### 本节目标

理解阈值规则变严格或变宽松时，TP、FP、TN、FN 会怎样变化。

原来的规则：

```text
temperature_c >= 26.0 and dispense_mg >= 13.0
```

表示两个条件必须同时满足，才预测为“点胶不良”。这是较严格的规则。

对照规则：

```text
temperature_c >= 26.0 or dispense_mg >= 13.0
```

表示任意一个条件满足，就预测为“点胶不良”。这是较宽松的规则。

### 实验结果

先在 `data/anomaly_interval_10/batches.csv` 的 30 条数据上比较：

| 规则 | TP | FP | TN | FN | 准确率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `and` | 3 | 0 | 27 | 0 | 100.00% |
| `or` | 3 | 0 | 27 | 0 | 100.00% |

两种规则在这 30 条数据上结果相同。原因是这批合成数据中，正常批次的温度和点胶量都低于阈值，异常批次都高于阈值，两种规则没有产生差异。

再用 `data/synthetic_demo/batches.csv` 的 120 条数据比较：

| 规则 | TP | FP | TN | FN | 准确率 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `and` | 9 | 0 | 111 | 0 | 100.00% |
| `or` | 9 | 2 | 109 | 0 | 98.33% |

`or` 检查的是“任意一个条件满足”，比 `and` 更容易报警，因此出现了 2 个误报 FP。

### 结论

- 规则变宽松通常会提高召回能力，也就是减少漏报 FN。
- 但规则变宽松也可能增加误报 FP。
- “变小样本结果相同”不代表两条规则在更大数据上也相同。
- 是否选择 `and` 或 `or`，要比较“漏报带来的损失”和“误报带来的检查成本”。
- 在工业质量场景中，通常不能只看准确率，还要分别关注 FP 和 FN。

### 本节总结问题

1. `and` 和 `or` 哪个规则更严格？为什么？
2. 为什么 30 条数据上两种规则结果相同，而 120 条数据上出现了差异？
3. 如果漏掉一个真实缺陷的代价远高于一次误报警，通常应该更倾向减少 FN 还是 FP？

## 二十一、FastAPI `/health` 最小接口（2026-10-07）

### 本节目标

理解一个最小后端的完整链路：

```text
浏览器或其他程序发送 HTTP 请求
→ FastAPI 根据方法和路径找到函数
→ 函数返回 Python 字典
→ FastAPI 把字典转换成 JSON
→ 客户端收到状态码和响应内容
```

本节只实现健康检查接口，不连接数据库，也不读取公司数据。

### 先理解四个词

| 名称 | 零基础解释 |
| --- | --- |
| API | 程序给其他程序提供功能的入口 |
| HTTP | 客户端和服务器交换请求、响应的通信规则 |
| FastAPI | 负责定义路由、解析请求和生成响应的 Python 框架 |
| Uvicorn | 真正启动 HTTP 服务并监听端口的服务器 |

`/health` 不是业务结果，而是服务自检入口。调用方看到 HTTP 200 和 `status=ok`，就知道服务已经启动并能响应。

### 应用代码

文件：`E:\Project\0基础学agent\industrial-quality-agent\api\main.py`

```python
from fastapi import FastAPI


# 创建 FastAPI 应用对象，uvicorn 启动服务时会加载这个变量。
app = FastAPI(
    title="工业质量 Agent API",
    version="0.1.0",
    description="仅使用合成数据的工业质量分析服务。",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """返回服务健康状态，供调用方确认服务是否可用。"""
    return {
        "status": "ok",
        "service": "industrial-quality-agent",
        "version": "0.1.0",
    }
```

关键点：

- `app = FastAPI(...)` 创建一个 Web 应用对象。
- `@app.get("/health")` 表示接收 `GET /health` 请求。
- `health_check()` 是处理该请求的函数。
- 返回 Python 字典后，FastAPI 会自动转换成 JSON。
- 函数没有写 `status_code=200`，FastAPI 默认成功响应就是 200。

### 测试代码

文件：`E:\Project\0基础学agent\industrial-quality-agent\tests\test_health.py`

```python
from fastapi.testclient import TestClient

from api.main import app


# TestClient 可以在不真正启动服务器的情况下调用 FastAPI 接口。
client = TestClient(app)


def test_health_check_returns_ok() -> None:
    """健康检查应返回 HTTP 200 和稳定的 JSON 内容。"""
    response = client.get("/health")

    # 检查 HTTP 状态码和响应正文。
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "industrial-quality-agent",
        "version": "0.1.0",
    }
```

测试分为两步：

1. 发送 `GET /health`。
2. 检查状态码和 JSON 内容是否符合接口约定。

### 运行测试

在项目根目录执行：

```powershell
# 进入 API 项目目录。
cd E:\Project\0基础学agent\industrial-quality-agent

# 使用项目虚拟环境运行全部测试。
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m pytest -q tests
```

当前结果：

```text
7 passed
```

测试通过说明接口逻辑符合预期，但还不能证明服务真的能监听端口。

### 启动真实服务

```powershell
# api.main:app 表示从 api/main.py 中加载名为 app 的对象。
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

参数解释：

- `api.main:app`：模块名 `api.main`，对象名 `app`。
- `127.0.0.1`：只允许本机访问。
- `8000`：服务监听端口。

服务启动后，另开一个终端执行：

```powershell
# 向健康检查接口发送 GET 请求。
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

实际返回：

```json
{
  "status": "ok",
  "service": "industrial-quality-agent",
  "version": "0.1.0"
}
```

### 本节限制

- `/health` 没有请求参数，也没有业务计算。
- 当前没有 `/generate` 接口。
- 当前服务只应使用合成数据。
- 接口测试虽然有依赖弃用警告，但功能验证和真实 HTTP 请求均已成功。
- 浏览器自动请求 `/favicon.ico` 时可能出现 404，因为项目没有配置网站图标；这不是 `/health` 接口失败。
- FastAPI 默认提供 `/docs` 交互式接口文档和 `/openapi.json` 机器可读接口描述，可用于核对请求方法、路径和响应结构。
- 后续需要学习请求模型、参数校验、错误响应和业务逻辑分层。

### 本节总结问题

1. `GET /health` 请求最终由哪个 Python 函数处理？正常情况下状态码和返回内容是什么？
2. FastAPI 和 Uvicorn 各自负责什么？
3. 为什么既要做接口测试，又要真正启动服务请求一次？


### 零基础重讲：把接口想成一家餐厅（2026-10-07）

前面的讲法术语太多。换成一个生活例子：

| FastAPI 项目 | 餐厅 |
| --- | --- |
| Uvicorn | 餐厅的大门和服务员，负责在 8000 号门口接收客人 |
| FastAPI | 餐厅的菜单和调度规则 |
| `@app.get("/health")` | 菜单上写着“GET /health”这道菜 |
| `health_check` 函数 | 真正制作这道菜的厨师 |
| 返回的字典 | 厨师做出的菜 |
| FastAPI 转成 JSON | 把菜装盘后交给客人 |
| HTTP 200 | 服务员告诉客人：这次下单成功 |

#### 请求发生了什么

你在浏览器或 PowerShell 发出：

```text
GET http://127.0.0.1:8000/health
```

整个过程是：

1. Uvicorn 在 `127.0.0.1:8000` 这个地址等请求。
2. 它收到 `GET /health`。
3. FastAPI 查看菜单，发现 `/health` 由 `health_check` 处理。
4. FastAPI 调用 `health_check()`。
5. 函数返回一个字典。
6. FastAPI 把字典变成 JSON。
7. 客户端收到 HTTP 200 和 JSON。

因此第一个问题的简单答案是：

```text
处理函数：health_check
请求：GET /health
状态码：200
返回：status、service、version 组成的 JSON
```

#### FastAPI 和 Uvicorn 分工

FastAPI 负责：

- 定义哪个路径由哪个函数处理。
- 解析请求。
- 把 Python 返回值转换成 JSON。
- 生成 `/docs` 和 `/openapi.json`。

Uvicorn 负责：

- 真正启动一个网络服务。
- 监听 `127.0.0.1:8000`。
- 接收浏览器发来的 HTTP 请求。
- 把请求交给 FastAPI，再把响应发回浏览器。

只写 `app = FastAPI()` 时，它只是程序里的一个 Python 对象。没有 Uvicorn，浏览器无法连接这个对象。

#### 为什么既做测试又启动服务

`TestClient` 测试像是在车间里检查零件：

- 速度快。
- 不需要占用端口。
- 能检查 `/health` 是否返回正确的状态码和 JSON。

真实 Uvicorn 请求像是在道路上试车：

- 能检查 8000 端口是否能监听。
- 能检查服务是否真的启动。
- 能检查浏览器、网络和 HTTP 请求是否能走通。

测试通过但 Uvicorn 启动失败，通常说明问题在服务器启动、端口或环境，而不是 `/health` 函数逻辑。

#### 重讲后的检查问题

1. 用餐厅类比说，Uvicorn 负责什么？FastAPI 负责什么？
2. 收到 `GET /health` 后，哪一个 Python 函数会执行？它返回哪三个字段？
3. `TestClient` 测试已经通过时，为什么还要启动 Uvicorn 再请求一次？

### 简化复述批改（2026-10-07）

用户回答：

1. Uvicorn 像服务员，负责接待和传递请求；FastAPI 像菜单和调度规则。回答正确。
2. `GET /health` 由 `health_check()` 处理，返回 `status`、`service`、`version`。回答正确。
3. `TestClient` 只是模拟并检查接口逻辑，启动 Uvicorn 才是真正打开接口。方向正确，但表述需纠正。

准确表述：

```text
TestClient 会真实调用 FastAPI 应用和路由函数并得到响应，
但它没有启动 Uvicorn，也没有通过网络端口接收请求。
```

因此测试覆盖的是“应用和路由逻辑”，真实 Uvicorn 覆盖的是“服务器启动、端口监听和网络请求”。

当前状态：`/health` 基本掌握，继续巩固。下一步进入 `/generate`，先学习 GET 查询参数和 POST 请求体的区别。

## 二十二、GET 与 POST 的最小区分（2026-10-07）

### 先用生活例子理解

| 动作 | 类似生活场景 | HTTP 方法 |
| --- | --- | --- |
| 查看菜单、查询状态 | 只看，不改变餐厅 | GET |
| 提交订单、让后厨开始制作 | 会触发实际操作 | POST |

### GET

GET 通常用于读取数据。

```text
GET /health
```

特点：

- 参数通常放在 URL 查询字符串中，例如 `/items?limit=10`。
- 主要用于查询。
- 不应该因为调用一次就偷偷修改服务器文件。

### POST

POST 通常用于提交数据或触发一个操作。

```text
POST /generate
```

请求正文可以写成 JSON：

```json
{
  "batch_count": 30,
  "seed": 42
}
```

特点：

- 复杂参数通常放在请求体 JSON 中。
- 适合创建、生成、提交或修改服务器状态。
- 当前 `/generate` 会写出 CSV、JSONL、知识文档等文件，因此会产生服务器端变化。

### 为什么 `/generate` 更适合 POST

数据生成接口会：

```text
接收批次数和随机种子
→ 生成一批新文件
→ 改变服务器上的数据目录
```

它不是单纯读取数据，而是触发“生成”这个动作，所以接口设计上更适合使用 POST。

### 本节总结问题

1. GET 通常用于读取数据，还是触发创建和修改操作？
2. POST 的复杂参数通常放在 URL 查询字符串还是 JSON 请求体中？
3. 为什么 `/generate` 会写出文件，因此更适合使用 POST？

## 二十三、实现 `POST /generate`（2026-10-07）

### 本节目标

让 API 接收 JSON 参数，调用已有的 `SyntheticQualityGenerator`，生成合成数据并返回 manifest。

请求：

```http
POST /generate
Content-Type: application/json
```

请求体：

```json
{
  "batch_count": 3,
  "seed": 7
}
```

响应包含：

- 提示信息 `message`。
- 实际输出目录 `output_dir`。
- 数据生成器返回的 `manifest`。

### 请求模型

```python
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """定义 POST /generate 的 JSON 请求体。"""

    # Field 负责在校验层限制范围，明显错误的参数不会进入生成器。
    batch_count: int = Field(default=120, ge=1, le=10000)
    seed: int = Field(default=42, ge=0)
```

Pydantic 模型可以理解为 API 的“参数表格”：

- 字段必须有正确的类型，例如 `batch_count` 必须是整数。
- `ge=1` 表示大于等于 1。
- `le=10000` 表示小于等于 10000。
- 非法请求会在进入函数前被 FastAPI 拒绝，并返回 HTTP 422。

### 接口函数

```python
@app.post("/generate")
def generate_dataset(request: GenerateRequest) -> dict[str, Any]:
    """接收 JSON 参数，生成合成数据并返回 manifest。"""
    try:
        # 复用已有生成器，不在 API 里重复写数据生成逻辑。
        generator = SyntheticQualityGenerator(
            output_dir=GENERATED_DATA_DIR,
            batch_count=request.batch_count,
            seed=request.seed,
        )
        manifest = generator.generate()
    except ValueError as exc:
        # 把业务参数错误转换成标准 HTTP 422。
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "message": "合成数据生成完成",
        "output_dir": str(GENERATED_DATA_DIR.resolve()),
        "manifest": manifest,
    }
```

关键分工：

```text
HTTP 参数校验：GenerateRequest
业务生成逻辑：SyntheticQualityGenerator
HTTP 响应转换：FastAPI
```

### 测试

```python
def test_generate_creates_dataset(tmp_path: Path, monkeypatch) -> None:
    """POST /generate 应生成文件并返回 manifest。"""
    # 使用临时目录，避免测试污染真实项目数据。
    output_dir = tmp_path / "api_generated"
    monkeypatch.setattr(api_main, "GENERATED_DATA_DIR", output_dir)

    response = client.post(
        "/generate",
        json={"batch_count": 3, "seed": 7},
    )

    assert response.status_code == 200
    assert response.json()["manifest"]["batch_count"] == 3
    assert (output_dir / "batches.csv").exists()
```

非法参数测试：

```python
def test_generate_rejects_invalid_batch_count(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """batch_count=0 应在请求校验阶段返回 HTTP 422。"""
    output_dir = tmp_path / "api_generated"
    monkeypatch.setattr(api_main, "GENERATED_DATA_DIR", output_dir)

    response = client.post(
        "/generate",
        json={"batch_count": 0, "seed": 7},
    )

    assert response.status_code == 422
    assert not output_dir.exists()
```

### 实际验证

pytest：

```text
9 passed
```

真实 Uvicorn 请求：

```text
POST /generate
batch_count = 3
seed = 7
```

实际输出目录：

```text
E:\Project\0基础学agent\industrial-quality-agent\data\api_generated
```

生成文件：

```text
batches.csv
eval_questions.jsonl
manifest.json
README.md
knowledge/
```

非法参数 `batch_count=0` 实际返回：

```text
HTTP 422
```

### 本节限制

- 当前输出目录固定为 `data/api_generated`。
- 同名目录会被下一次生成覆盖。
- 还没有为请求添加身份验证、权限和任务队列。
- 当前生成是同步操作，大文件生成可能占用较长时间。
- 后续需要补接口错误说明和更完整的响应模型。

### 本节总结问题

1. 为什么 `/generate` 使用 POST 和 JSON 请求体？
2. `GenerateRequest` 负责什么？`SyntheticQualityGenerator` 负责什么？
3. 为什么 `batch_count=0` 应该在进入生成器前就返回 HTTP 422？

### `/generate` 复述批改（2026-10-07）

三个问题均回答正确：

1. 生成数据会新建或覆盖文件，属于服务器端状态变化，因此使用 POST；参数通过 JSON 请求体传入。
2. `GenerateRequest` 负责请求参数的类型和范围校验；`SyntheticQualityGenerator` 负责真正的数据生成业务逻辑。
3. `batch_count: int = Field(default=120, ge=1, le=10000)` 要求批次数至少为 1，因此 `batch_count=0` 在进入生成器前就被 FastAPI/Pydantic 拒绝并返回 HTTP 422。

当前 `/generate` 标记为基本掌握。下一步学习 HTTP 200 与 422 的含义，并为接口补充更明确的响应模型。

## 二十四、HTTP 状态码：200、422、404 和 500（2026-10-07）

### 状态码是什么

HTTP 响应由两部分组成：

```text
状态码：说明请求大致结果
响应正文：具体返回的数据或错误说明
```

例如：

```text
HTTP 200
{"status": "ok", ...}
```

其中：

- `200` 说明请求成功。
- JSON 是响应正文，说明具体内容。

### 常见状态码

| 状态码 | 简单含义 | 当前例子 |
| --- | --- | --- |
| 200 | 请求成功 | `GET /health`、正常 `POST /generate` |
| 404 | 找不到请求的路径 | 访问未定义的 `/favicon.ico` |
| 422 | 请求格式能理解，但参数校验失败 | `batch_count=0` |
| 500 | 服务器代码发生未处理异常 | 代码突然报错时的通用服务器错误 |

### 200 和 422 的区别

正常生成：

```json
{
  "batch_count": 3,
  "seed": 7
}
```

返回：

```text
HTTP 200
```

因为参数合法，生成完成。

非法生成：

```json
{
  "batch_count": 0,
  "seed": 7
}
```

返回：

```text
HTTP 422
```

因为 `batch_count` 要求大于等于 1。

### 404 不一定是程序坏了

浏览器会自动请求 `/favicon.ico`。项目没有定义这个路径，所以返回 404。

这不影响：

```text
GET /health
```

健康检查仍然可以返回 200。

### 500 通常表示代码问题

如果服务器代码抛出未处理异常，FastAPI/Uvicorn 通常会返回 500。

实际项目中需要：

- 记录错误日志。
- 给调用方返回稳定的错误格式。
- 不把密码、路径、数据库信息等内部细节直接返回。

### 本节总结问题

1. HTTP 200 和 HTTP 422 分别代表什么？
2. 为什么 `/favicon.ico` 返回 404，不代表 `/health` 失败？
3. HTTP 状态码和响应正文有什么区别？

### 状态码复述批改（2026-10-07）

第 1 题正确：

```text
200：请求成功
422：请求格式能理解，但参数校验失败
```

第 2 题方向正确但不完整。准确表述：

```text
/favicon.ico 和 /health 是两个独立请求、两个不同路径。
浏览器请求 /favicon.ico 得到 404，只说明“这个路径没有定义”，
不会改变 /health 这条请求的结果；/health 仍然是独立的 200。
```

第 3 题方向正确但不完整。准确表述：

```text
状态码：告诉客户端这次请求的结果类别，例如成功、参数错误或找不到路径。
响应正文：提供更具体的数据，例如 JSON 字段或错误详情。
```

例如：

```text
状态码：200
响应正文：{"status":"ok","service":"industrial-quality-agent","version":"0.1.0"}
```

当前状态码知识标记为“需要巩固”。请先补答第 2、3 题。

## 二十五、请求模型与响应模型（2026-10-07）

### 本节目标

理解 API 的两个方向：

```text
请求模型：规定客户端必须传什么
响应模型：规定服务端成功时返回什么
```

### 请求模型

```python
class GenerateRequest(BaseModel):
    """定义 POST /generate 的 JSON 请求体。"""

    batch_count: int = Field(default=120, ge=1, le=10000)
    seed: int = Field(default=42, ge=0)
```

它负责：

- 接收客户端 JSON。
- 检查字段类型。
- 检查数值范围。
- 参数不合法时返回 HTTP 422。

### 响应模型

```python
class GenerateManifest(BaseModel):
    """定义合成数据 manifest 的成功响应结构。"""

    dataset_name: str
    dataset_version: str
    is_synthetic: bool
    seed: int
    batch_count: int
    document_count: int
    question_count: int
    files: list[str]
    notice: str


class GenerateResponse(BaseModel):
    """定义 POST /generate 的成功响应结构。"""

    message: str
    output_dir: str
    manifest: GenerateManifest
```

它负责：

- 规定成功响应的字段。
- 规定字段类型。
- 让 `/docs` 和 `/openapi.json` 自动展示返回结构。
- 如果返回数据缺少必要字段或类型错误，FastAPI 会把它作为服务器错误处理。

### 模型和业务逻辑的分工

```text
GenerateRequest：检查进入 API 的参数
SyntheticQualityGenerator：生成业务数据
GenerateResponse：检查并描述离开 API 的响应
FastAPI：连接请求、函数和响应，并生成接口文档
```

### 验证结果

新增测试检查 `/openapi.json` 是否包含：

```text
GenerateRequest
GenerateResponse
```

完整测试结果：

```text
10 passed
```

真实 Uvicorn 请求仍然正常返回：

```text
message
output_dir
manifest
```

### 本节限制

- 响应模型只规定成功响应，不代表已经定义了所有错误响应。
- HTTP 422 的错误结构目前由 FastAPI/Pydantic 自动生成。
- 后续需要补明确的错误响应模型和错误示例。

### 本节总结问题

1. 请求模型和响应模型分别规定哪个方向的数据？
2. `GenerateManifest` 和 `GenerateResponse` 的关系是什么？
3. 为什么增加响应模型后，还需要继续定义错误响应模型？

## 二十六、`manifest` 是什么（2026-10-07）

### 一句话解释

`manifest` 是数据集的“装箱单”或“说明书”。

```text
batches.csv、知识文档、评测问题：真正的内容
manifest：说明这批内容是什么、有多少、如何复现、包含哪些文件
```

它不是原始数据本身，而是描述数据的元数据。

### 实际例子

文件：`data\api_generated\manifest.json`

```json
{
  "dataset_name": "industrial-quality-synthetic-demo",
  "dataset_version": "0.1.0",
  "is_synthetic": true,
  "seed": 7,
  "batch_count": 3,
  "document_count": 4,
  "question_count": 30,
  "files": [
    "batches.csv",
    "eval_questions.jsonl",
    "knowledge/",
    "manifest.json",
    "README.md"
  ],
  "notice": "仅用于学习和演示，不得用于真实生产决策。"
}
```

### 字段含义

| 字段 | 含义 |
| --- | --- |
| `dataset_name` | 数据集名称 |
| `dataset_version` | 数据集版本 |
| `is_synthetic` | 是否全部为合成数据 |
| `seed` | 复现这次生成使用的随机种子 |
| `batch_count` | 生成了多少条批次记录 |
| `document_count` | 生成了多少份知识文档 |
| `question_count` | 生成了多少条评测问题 |
| `files` | 数据集包含的文件和目录 |
| `notice` | 数据使用限制和安全声明 |

### API 响应里的 `manifest`

`POST /generate` 的成功响应：

```json
{
  "message": "合成数据生成完成",
  "output_dir": "E:\\...\\data\\api_generated",
  "manifest": {
    "dataset_name": "industrial-quality-synthetic-demo",
    "seed": 7,
    "batch_count": 3,
    "notice": "仅用于学习和演示，不得用于真实生产决策。"
  }
}
```

这里的 `manifest` 是一个嵌套 JSON 对象。

它同时有另一种保存形式：

```text
data\api_generated\manifest.json
```

两者表达的是同一份数据集说明，只是一个随 API 响应返回，另一个保存成文件。

### 三个容易混淆的名字

```text
manifest.json
实际保存的数据集说明文件。

manifest
API 响应中的一个 JSON 字段，值是数据集说明。

GenerateManifest
Python 类，规定 manifest 字段应该有哪些、类型是什么。
```

类比：

```text
manifest.json = 装箱单文件
manifest      = 装箱单内容
GenerateManifest = 装箱单模板
```

### 更正“为什么要错误响应模型”

“保证严谨”方向正确，但不够具体。

成功响应模型只规定 HTTP 200 返回什么。错误响应通常有不同的结构和字段，例如：

```json
{
  "error_code": "INVALID_BATCH_COUNT",
  "message": "batch_count 必须大于等于 1",
  "details": {
    "field": "batch_count"
  }
}
```

定义错误响应模型的目的是：

- 让不同接口返回稳定、统一的错误格式。
- 让客户端程序知道应该读取哪些错误字段。
- 让 `/docs` 展示失败响应结构。
- 避免每个错误都依赖 FastAPI 自动生成的不同格式。

### 本节总结问题

1. `manifest` 保存的是全部批次原始记录，还是描述数据集的元数据？
2. `manifest.json`、API 响应中的 `manifest`、`GenerateManifest` 各是什么？
3. 为什么错误响应需要单独定义结构，不能只依赖成功响应模型？

## 二十七、统一错误响应（2026-10-07）

### 本节目标

让成功响应和错误响应都有稳定、可预测的结构。

成功响应：

```json
{
  "message": "合成数据生成完成",
  "output_dir": "...",
  "manifest": {}
}
```

错误响应：

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

### 错误响应模型

```python
class ErrorResponse(BaseModel):
    """定义统一错误响应结构。"""

    error_code: str
    message: str
    details: dict[str, Any] | None = None
```

三个字段的作用：

| 字段 | 作用 |
| --- | --- |
| `error_code` | 给程序读取的稳定错误编号 |
| `message` | 给用户或日志阅读的简要说明 |
| `details` | 保存字段名、失败原因等补充信息 |

### 请求参数错误

```python
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """把 FastAPI/Pydantic 的请求参数错误转换成统一格式。"""
    first_error = exc.errors()[0]
    field = ".".join(str(item) for item in first_error["loc"] if item != "body")
    content = ErrorResponse(
        error_code="REQUEST_VALIDATION_ERROR",
        message="请求参数校验失败",
        details={
            "field": field,
            "reason": first_error["msg"],
        },
    )
    return JSONResponse(status_code=422, content=content.model_dump())
```

`batch_count=0` 实际返回：

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

### 路径不存在错误

```json
{
  "error_code": "NOT_FOUND",
  "message": "请求的路径不存在",
  "details": null
}
```

### 验证结果

完整测试：

```text
11 passed
```

真实 Uvicorn：

- 非法参数返回 HTTP 422 和统一错误结构。
- 不存在的路径返回 HTTP 404 和统一错误结构。
- 端口 8000 已停止监听。

### 本节限制

- 还没有为未处理的 500 异常统一格式。
- `details` 现在只展示第一条参数错误。
- 还没有把错误码整理成集中管理的枚举。
- 后续可以补日志、请求 ID 和真实生产错误处理。

### 本节总结问题

1. `error_code`、`message`、`details` 分别适合给谁使用？
2. 为什么请求参数错误返回 422，而不是 400 或 500？
3. 为什么错误响应需要稳定结构，而不能每次都让框架自动生成不同内容？

### 统一错误响应复述批改（2026-10-07）

第 2 题方向正确：

```text
请求到达了正确的接口，路径和请求格式可以识别，
但请求体中的参数没有通过校验，因此返回 422。
```

需要补充：

```text
400：一般表示请求本身存在更宽泛的错误。
422：请求格式可理解，但具体字段的内容不符合约束。
500：服务器内部代码或依赖发生未处理异常，不是客户端参数问题。
```

第 1 题需要更精确：

```text
error_code：主要给客户端程序读取和判断错误类型。
message：主要给用户阅读，也用于日志中的简要说明。
details：主要给开发人员、调试工具和客户端显示具体字段问题。
```

第 3 题不能只回答“维护效率高”。稳定错误结构的收益包括：

- 客户端可以用同一套代码解析所有错误。
- 接口文档可以列出稳定的失败响应。
- 测试可以断言固定字段，减少脆弱匹配。
- 日志和监控可以按 `error_code` 聚合统计。
- 后续改版时更容易保持兼容。

当前统一错误响应标记为“需要巩固”，请先补答第 1、3 题。

## 二十八、500 异常与日志（2026-10-07）

### 本节目标

处理服务器内部没有预料到的异常：

```text
真实异常 → 写入日志，供开发人员排查
客户端响应 → 只返回统一、安全的 500 信息
```

### 为什么不能把异常原文返回客户端

假设生成器抛出：

```text
RuntimeError: 模拟生成器内部错误
```

如果直接返回给客户端，可能泄露：

- 内部文件路径。
- 数据库或服务地址。
- 代码结构。
- 依赖版本。
- 业务实现细节。

因此客户端只看到：

```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "服务器内部错误",
  "details": null
}
```

真实异常写入服务端日志。

### 日志记录器

```python
import logging


# 创建模块级日志记录器，用于记录服务器内部异常。
logger = logging.getLogger("industrial_quality_api")
```

`logger` 比 `print` 更适合服务器，因为它支持：

- 日志级别。
- 时间、模块、行号等格式化信息。
- 异常堆栈。
- 统一写入控制台或日志文件。
- 后续接入监控系统。

### 未处理异常处理器

```python
@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """记录未处理异常，并返回不泄露内部细节的统一 500 响应。"""
    # 日志中保留真实异常，便于开发人员排查问题。
    logger.exception(
        "未处理异常：method=%s path=%s",
        request.method,
        request.url.path,
    )
    content = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        message="服务器内部错误",
    )
    return JSONResponse(status_code=500, content=content.model_dump())
```

`logger.exception(...)` 会记录：

- 当前日志消息。
- 异常类型。
- 异常内容。
- 完整 traceback 堆栈。

### 测试方式

测试时不能用真实错误去破坏项目，而是替换成故意失败的生成器：

```python
class FailingGenerator:
    """用于测试的失败生成器。"""

    def __init__(self, output_dir: Path, batch_count: int, seed: int) -> None:
        self.output_dir = output_dir
        self.batch_count = batch_count
        self.seed = seed

    def generate(self) -> dict[str, object]:
        """模拟未处理的服务器内部异常。"""
        raise RuntimeError("模拟生成器内部错误")
```

然后让 TestClient 不要直接把异常抛给测试代码，而是读取实际 HTTP 500 响应：

```python
error_client = TestClient(
    api_main.app,
    raise_server_exceptions=False,
)
```

### 验证结果

```text
12 passed
```

测试确认：

- 客户端得到 HTTP 500。
- 响应体不含内部异常原文。
- 日志包含“未处理异常”和“模拟生成器内部错误”。

### 本节限制

- 还没有请求 ID，无法把客户端错误与某一行业务日志快速关联。
- 还只有控制台日志，没有写入文件或日志平台。
- 通用 500 处理器不应该捕获并隐藏开发阶段所有异常细节；本地调试时仍需查看服务端日志。
- 下一步需要整理 Git 提交和 README。

### 本节总结问题

1. 为什么不把 `RuntimeError` 的原文直接返回给客户端？
2. `logger.exception()` 比 `print()` 多保留了哪些排查信息？
3. 为什么测试 500 时要使用故意失败的生成器和 `raise_server_exceptions=False`？

### 同一异常的实际对比（2026-10-07）

使用同一个内部异常：

```text
RuntimeError: 模拟生成器内部错误
```

服务端日志示例（traceback 省略中间框架，只保留关键片段）：

```text
ERROR industrial_quality_api 未处理异常：method=POST path=/generate

Traceback (most recent call last):
  ...
  File "E:\Project\0基础学agent\...\api\main.py", line 162, in generate_dataset
    manifest = generator.generate()
  File "<stdin>", line 22, in generate
    raise RuntimeError("模拟生成器内部错误")
RuntimeError: 模拟生成器内部错误
```

客户端收到的 HTTP 响应：

```text
HTTP 状态码：500
```

```json
{
  "error_code": "INTERNAL_SERVER_ERROR",
  "message": "服务器内部错误",
  "details": null
}
```

对比：

| 对象 | 能看到什么 | 主要用途 |
| --- | --- | --- |
| 服务端日志 | 异常类型、异常原文、文件路径、代码行、完整 traceback | 定位和修复问题 |
| 客户端响应 | 统一错误码、安全消息、空详情 | 稳定处理失败、不泄露内部信息 |

同一请求中：

```text
服务端：看到真实异常和完整技术细节
客户端：只看到安全、稳定的用户级错误
```

## 二十九、Git 工作区、暂存区和本地提交（2026-10-07）

### Git 的三层模型

```text
工作区：你现在看到的项目文件
暂存区：准备放进下一次提交的改动
提交历史：已经保存成一次版本快照的记录
```

可以类比成发快递：

```text
工作区 = 桌子上要寄的物品
暂存区 = 已经装进箱子的物品
提交历史 = 已经封箱并编号入库的包裹
```

### 本次使用的命令

查看当前状态：

```powershell
# 查看当前分支、已修改文件和未跟踪文件。
git status --short --branch
```

创建专用分支：

```powershell
# 从当前分支创建并切换到 codex 分支。
git switch -c codex/industrial-quality-agent-api
```

只暂存项目文件：

```powershell
# 只把 industrial-quality-agent 的项目文件放入暂存区。
git add -- industrial-quality-agent/.gitignore industrial-quality-agent/README.md industrial-quality-agent/analyze_anomalies.py industrial-quality-agent/api industrial-quality-agent/generate_data.py industrial-quality-agent/quality_data industrial-quality-agent/requirements.txt industrial-quality-agent/tests
```

检查暂存区：

```powershell
# 查看暂存区与 HEAD 的差异统计。
git diff --cached --stat

# 检查空白错误、文件格式等明显问题。
git diff --cached --check
```

创建提交：

```powershell
# 创建本地提交，不自动推送到远程。
git commit -m "feat: add industrial quality FastAPI service"
```

### 本次实际结果

```text
分支：codex/industrial-quality-agent-api
提交：c126e89
消息：feat: add industrial quality FastAPI service
文件数：12
新增行数：816
```

提交内容：

```text
industrial-quality-agent/.gitignore
industrial-quality-agent/README.md
industrial-quality-agent/analyze_anomalies.py
industrial-quality-agent/api/
industrial-quality-agent/generate_data.py
industrial-quality-agent/quality_data/
industrial-quality-agent/requirements.txt
industrial-quality-agent/tests/
```

### 提交前的检查发现

`git diff --cached --check` 发现 3 个文件末尾有多余空行：

```text
README.md: new blank line at EOF.
analyze_anomalies.py: new blank line at EOF.
api/main.py: new blank line at EOF.
```

清理空行后重新运行测试：

```text
12 passed
```

### 未提交和未推送的内容

- `13.0`` 是之前误建的 0 字节文件，没有加入暂存区，也没有提交。
- 远程仓库暂时没有收到这次提交。
- 下一节可以学习：

```powershell
# 把本地分支推送到远程仓库。
git push -u origin codex/industrial-quality-agent-api
```

推送后可以在 GitHub 发起 Pull Request，让改动进入 `main` 前先经过审查。

### 本节总结问题

1. 工作区、暂存区、提交历史分别保存什么？
2. `git status`、`git add`、`git diff --cached`、`git commit` 各自做什么？
3. 为什么提交前要先查看暂存区，而不是直接执行 `git commit`？


## 三十、远程分支与 Pull Request（2026-10-07）

### 本地分支和远程分支

```text
本地分支：codex/industrial-quality-agent-api
提交 c126e89 当前保存在这台电脑上。

远程分支：origin-https/codex/industrial-quality-agent-api
同名提交被上传到 GitHub。
```

本地分支与远程分支建立 tracking 关系后，Git 可以知道：

```text
本地分支对应哪个远程仓库、哪个远程分支
本地是否领先或落后远程
git pull / git push 默认操作哪里
```

### 推送命令

```powershell
# 把本地分支推送到 origin-https，并建立 tracking 关系。
git push -u origin-https codex/industrial-quality-agent-api
```

参数含义：

- `git push`：把本地提交发送到远程。
- `-u`：建立 upstream/tracking 关系。
- `origin-https`：远程名称，指向 GitHub HTTPS 地址。
- `codex/industrial-quality-agent-api`：要推送的分支。

推送结果：

```text
remote: Create a pull request for 'codex/industrial-quality-agent-api'
remote: https://github.com/BYC2003/agent-learning-platform/pull/new/codex/industrial-quality-agent-api
```

### SSH 失败和 HTTPS 成功

第一次尝试使用 SSH 远程：

```text
origin git@github.com:BYC2003/agent-learning-platform.git
```

失败：

```text
Connection closed by 198.18.0.131 port 443
fatal: Could not read from remote repository.
```

改用 HTTPS 远程：

```text
origin-https https://github.com/BYC2003/agent-learning-platform.git
```

成功。

这说明一个 Git 仓库可以配置多个远程地址，名称不同：

```text
origin       = SSH 地址，本次推送失败
origin-https = HTTPS 地址，本次推送成功
```

### Pull Request 是什么

Pull Request（PR）可以理解为：

```text
“我已经把一组改动推送到分支，
请项目维护者审查这些改动，
决定是否合并到 main。”
```

PR 通常包含：

- 改动说明。
- 文件差异。
- 测试结果。
- 审查评论。
- 合并按钮。
- 合并后的分支处理。

推送分支不会自动修改 `main`。只有创建 PR、完成审查并执行合并后，改动才可能进入主分支。

PR 链接：

`https://github.com/BYC2003/agent-learning-platform/pull/new/codex/industrial-quality-agent-api`

### 当前状态

```text
本地提交：完成
分支推送：完成
远程跟踪：完成
Pull Request：尚未创建
main 合并：尚未发生
误建文件 13.0`：未跟踪、未提交、未推送
```

### 本节总结问题

1. 本地分支 `codex/industrial-quality-agent-api` 和远程分支 `origin-https/codex/industrial-quality-agent-api` 有什么区别？
2. `git push -u origin-https codex/industrial-quality-agent-api` 中，`push`、`-u`、远程名和分支名分别做什么？
3. 推送分支后，为什么 `main` 不会自动获得这些改动？Pull Request 的作用是什么？

### 远程协作复述批改（2026-10-07）

第 1 题正确：

```text
本地分支保存在电脑上。
远程分支保存在 GitHub 上。
```

第 2 题只答了 `-u`，需要补齐整条命令：

```text
git push -u origin-https codex/industrial-quality-agent-api
```

| 部分 | 作用 |
| --- | --- |
| `git push` | 把本地提交上传到远程仓库 |
| `-u` | 建立本地分支和远程分支的 tracking 关系 |
| `origin-https` | 选择使用哪个远程地址 |
| `codex/industrial-quality-agent-api` | 指定要推送的分支 |

第 3 题表述需要纠正：

```text
错误：Pull Request 的作用是推送分支。
正确：git push 负责推送分支；Pull Request 负责请求审查和合并。
```

正确顺序：

```text
1. git push 把分支推送到 GitHub。
2. 创建 Pull Request。
3. 查看代码差异、测试结果和审查评论。
4. 维护者决定是否合并到 main。
```

Pull Request 不会自动修改 `main`，这一点回答正确。

当前状态：远程协作需要补答第 2、3 题。

## 三十一、Pull Request 全流程（2026-10-07）

### 当前状态

```text
本地分支：codex/industrial-quality-agent-api
远程分支：origin-https/codex/industrial-quality-agent-api
提交：c126e89
```

GitHub CLI `gh` 未安装，因此本节使用网页创建 PR。

比较页面：

https://github.com/BYC2003/agent-learning-platform/pull/new/codex/industrial-quality-agent-api

### PR 的两个核心分支

```text
base：main
head：codex/industrial-quality-agent-api
```

含义：

```text
把 head 分支的改动提交给 base 分支审查。
```

注意：

```text
创建 PR 不会立刻修改 main。
只有完成审查并点击合并后，改动才可能进入 main。
```

### PR 标题

建议：

```text
feat: add industrial quality FastAPI service
```

### PR 说明模板

```markdown
## 变更内容

- 添加工业质量合成数据生成器。
- 添加 FastAPI `/health` 健康检查接口。
- 添加 FastAPI `/generate` 数据生成接口。
- 添加统一 422、404、500 错误响应。
- 添加日志记录，客户端不暴露内部异常细节。
- 添加 12 项 pytest 测试。

## 测试

```powershell
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m pytest -q tests
```

测试结果：

```text
12 passed
```
```

### PR 审查流程

1. 打开比较页面。
2. 确认 base 是 `main`。
3. 确认 head 是 `codex/industrial-quality-agent-api`。
4. 查看 Files changed 中的代码差异。
5. 填写标题和说明。
6. 创建 PR。
7. 查看自动检查、评论和审查意见。
8. 根据审查意见继续提交到同一分支。
9. 审查通过后选择合并策略。
10. 合并后同步 `main` 并删除已合并分支。

### 常见合并方式

```text
Create a merge commit
保留分支历史，并生成一个合并提交。

Squash and merge
把 PR 中多个提交压成一个提交后进入 main。

Rebase and merge
把提交逐个放到 main 最新历史后面。
```

学习阶段可以先使用默认方式，不必一开始深入比较三种策略。

### 合并后的同步命令

```powershell
# 切换到 main。
git switch main

# 从远程拉取最新 main。
git pull

# 查看已合并分支。
git branch --merged

# 删除本地已合并分支。
git branch -d codex/industrial-quality-agent-api
```

### 重要边界

- 本次尚未创建 PR。
- 本次尚未合并到 `main`。
- 误建文件 `13.0`` 没有推送。
- 不要在 PR 中提交公司真实数据、截图、日志或工艺参数。
- 真实审查中发现问题时，不要直接修改远程压缩包，要继续提交到原分支。

### 本节总结问题

1. Pull Request 中的 base 分支和 head 分支分别是什么？
2. PR 说明中至少应该写清哪些内容？
3. 合并 PR 后，为什么还需要切换 `main`、执行 `git pull` 并删除旧分支？

### PR #1 创建结果（2026-10-07）

PR 地址：

https://github.com/BYC2003/agent-learning-platform/pull/1

页面状态：

```text
状态：Open
base：main
head：codex/industrial-quality-agent-api
提交：1
文件：12
新增：816 行
GitHub Checks：0
```

GitHub 没有自动测试，因为当前仓库尚未配置 CI。本地已经运行：

```text
12 passed
```

### 合并前检查清单

打开 PR 的 `Files changed` 页面，确认：

- 只包含 `industrial-quality-agent` 项目文件。
- 包含 README、依赖、生成器、FastAPI 代码和测试。
- 不包含 `13.0`` 误建文件。
- 不包含 `data/`、`__pycache__/`、`.pytest_cache/`、`.vscode/`。
- 不包含公司真实数据、截图、日志或工艺参数。
- 文件数量是 12。
- 新增行数约 816 行。

### 合并策略学习

当前只有一个提交，可以选择：

```text
Squash and merge
把 PR 的提交压缩成一个新提交进入 main。
适合当前只有一个目标清晰的提交。

Create a merge commit
保留分支历史，并额外创建一个合并提交。
历史更完整，但提交图更复杂。

Rebase and merge
把提交逐个放到 main 最新历史后面。
适合希望历史接近线性时使用。
```

本项目当前推荐先使用：

```text
Squash and merge
```

### 合并后的操作

```powershell
# 切换到 main。
git switch main

# 拉取远程最新 main。
git pull

# 删除已经合并的本地分支。
git branch -d codex/industrial-quality-agent-api

# 删除已经合并的远程跟踪分支。
git push origin-https --delete codex/industrial-quality-agent-api
```

注意：删除远程分支前要确认 GitHub PR 已经成功合并。

### 当前待办

1. 打开 `Files changed` 检查文件。
2. 确认无误后选择合并方式。
3. 合并后同步 `main`。
4. 删除已合并分支。
5. 检查误建文件未被合并。

### PR #1 合并完成（2026-10-07）

GitHub 状态：

```text
PR：#1
状态：Merged
合并策略：Squash and merge
合并提交：9f630e2
远程分支：已删除
```

本地同步结果：

```text
当前分支：main
HEAD：9f630e2
上游：origin-https/main
旧本地分支：已删除
远程跟踪旧分支：已清理
```

本地 main 测试：

```text
12 passed
```

Squash 合并后的一个重要区别：

```text
GitHub 生成了一个全新的合并提交 9f630e2。
原来的本地提交 c126e89 不是这个新提交的祖先。
```

因此 `git branch -d` 可能会拒绝删除旧分支。确认 main 与旧分支的项目内容一致后，可以使用：

```powershell
git branch -D codex/industrial-quality-agent-api
```

这里不是盲目强删，而是先执行：

```powershell
git diff --stat codex/industrial-quality-agent-api main -- industrial-quality-agent
```

确认没有差异，再删除。

合并和清理完成后的状态：

```text
远程 main：包含项目
本地 main：包含项目
远程功能分支：已删除
本地功能分支：已删除
误建文件 13.0`：仍然未跟踪
```

### PR 全流程复述批改（2026-10-07）

第 1 题正确：

```text
base = main，目标分支
head/compare = codex/industrial-quality-agent-api，要合并的功能分支
```

第 2 题回答成了 PR 合并后的状态：

```text
状态 Merged、合并方式、提交号、分支删除
```

这不是 PR 合并前需要填写的说明。PR 说明至少应包含：

```text
1. 本次改了什么
2. 为什么这样改
3. 如何运行测试和测试结果
4. 数据与安全边界
5. 已知限制、风险或迁移要求
```

例如本次 PR 说明：

```text
添加工业质量合成数据生成器、FastAPI 接口、统一错误响应和日志。
运行 pytest，结果为 12 passed。
只使用合成数据，不包含公司真实数据、截图和工艺参数。
当前没有 CI、身份验证和任务队列。
```

第 3 题需要纠正：

```text
分支默认与 main 隔离，不会直接“干扰 main”。
```

合并后同步 main 的原因：

```text
GitHub 的合并发生在远程仓库。
本地 main 不会自动出现这个合并提交。
需要 fetch/pull 才能把远程合并结果同步到本地。
```

删除旧分支的原因：

```text
避免以后误在过期分支继续开发。
避免重复合并或产生冲突。
减少已经完成分支造成的仓库混乱。
```

当前状态：需要补答第 2、3 题。

## 三十二、RAG 第一步：加载 Markdown 文档（2026-10-07）

### RAG 总体流程

```text
加载文档
→ 清洗
→ 切分 chunk
→ 生成 embedding
→ 写入向量库
→ 收到问题后检索
→ Rerank
→ 带引用生成回答
→ 评测
```

本节只完成第一步：

```text
Markdown 文件
→ KnowledgeDocument 对象
```

暂不生成向量，不调用大模型。

### 为什么要转换成文档对象

原始文件路径不能直接用于 RAG。每份文档至少需要稳定标识和来源：

```python
@dataclass(frozen=True)
class KnowledgeDocument:
    """表示一份已经加载的知识文档。"""

    doc_id: str
    title: str
    content: str
    source_path: Path
```

| 字段 | 作用 |
| --- | --- |
| `doc_id` | 稳定标识文档，后续引用和去重 |
| `title` | 展示文档标题 |
| `content` | 后续清洗和切分的正文来源 |
| `source_path` | 追溯文件来源 |

### 标题提取

```python
def extract_title(markdown: str, fallback: str) -> str:
    """提取 Markdown 的第一个一级标题，找不到时使用回退标题。"""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback
```

如果文件没有一级标题，就使用文件名作为标题。

### 加载全部 Markdown

```python
def load_markdown_documents(directory: Path) -> list[KnowledgeDocument]:
    """读取目录中的全部 Markdown 文件，并转换为文档对象。"""
    if not directory.exists():
        raise FileNotFoundError(f"知识目录不存在：{directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"知识路径不是目录：{directory}")

    documents: list[KnowledgeDocument] = []

    # 按文件名排序，确保每次加载顺序稳定。
    for path in sorted(directory.glob("*.md"), key=lambda item: item.name):
        content = path.read_text(encoding="utf-8-sig")
        documents.append(
            KnowledgeDocument(
                doc_id=path.stem,
                title=extract_title(content, fallback=path.stem),
                content=content,
                source_path=path,
            )
        )

    return documents
```

### 实际加载结果

目录：

```text
data/synthetic_demo/knowledge/
```

加载结果：

```text
文档数: 4
case_dirty_nozzle: 8D 案例：喷嘴脏污
fmea_dispensing: FMEA：点胶工序
sop_cleaning: 清洗作业指导书
sop_dispensing: 点胶作业指导书
```

测试：

```text
14 passed
```

### 本节限制

- 当前 `content` 保留完整 Markdown，包括合成数据声明。
- 还没有拆分为 chunk。
- `doc_id` 暂时使用文件名，还没有内容哈希。
- 没有解析 PDF、Word 或网页。
- 没有生成 embedding，也没有向量库。

### 本节总结问题

1. `KnowledgeDocument` 为什么需要 `doc_id` 和 `source_path`？
2. 为什么加载文件时要按文件名排序？
3. 为什么加载文档后还要进行清洗和切分，不能直接把整份文档交给后续检索？

## 三十三、RAG 第二步：文档清洗与切分（2026-10-08 至 2026-10-10）

### 为什么加载后还要处理

上一节已经把 Markdown 文件变成 `KnowledgeDocument` 对象，但对象里的 `content` 仍然是完整文本。完整文本可能包含：

- 与问题无关的声明、页眉页脚和导航文字。
- 多余的空白行和重复内容。
- 一篇文档中的多个不同主题。

如果直接把整篇文档作为一个检索单位，检索时容易带入无关内容，回答也更容易被噪声干扰。

### 清洗做什么

清洗就是去掉不适合进入知识库的噪声，例如：

- 去掉固定的合成数据声明。
- 统一换行和空白。
- 保留标题、正文和必要的业务信息。
- 不要把有业务含义的引用、注意事项和警告误删。

清洗后的文本仍然属于同一份文档，只是内容更干净。

### chunk 是什么

chunk 是文档被切分后的一段可检索文本。可以把一份文档想成一本书，把 chunk 想成书中的索引卡片。

一个最小的 chunk 至少要保留：

```python
# 每个知识片段应该带上自己的身份和来源信息
chunk_id      # 片段编号，例如 sop_dispensing#0
doc_id        # 所属文档编号，例如 sop_dispensing
title         # 所属文档标题
content       # 这一段正文
source_path   # 原文件路径，便于引用和排查
```

### 常见切分方式

| 方式 | 优点 | 风险 |
| --- | --- | --- |
| 按标题切分 | 结构清楚，适合 SOP、FMEA、案例文档 | 某些标题下内容可能仍然太长 |
| 按段落切分 | 简单，适合短文档 | 段落很长时仍然不方便检索 |
| 按固定长度切分 | 容易控制大小 | 可能把一句话或一个完整意思切断 |
| 标题 + 长度 + 重叠 | 兼顾结构和大小 | 实现更复杂，需要测试 |

当前项目的合成文档很短，适合先采用“去声明 + 按标题/段落切分”的简单方案。以后文档变长，再增加最大长度和重叠窗口。

### 清洗与切分后的流程

```text
KnowledgeDocument
→ 清洗 content
→ 切分 chunk
→ list[KnowledgeChunk]
```

注意：清洗和切分还没有生成 embedding，也还没有写入向量库。

### 2026-10-10 实现与验证

代码新增在 `industrial-quality-agent/rag/documents.py`。

首先给 chunk 定义明确的数据结构：

```python
@dataclass(frozen=True)
class KnowledgeChunk:
    """表示一份可被检索和引用的知识片段。"""

    chunk_id: str      # 片段编号，例如 sop_dispensing#0
    doc_id: str        # 所属文档编号，例如 sop_dispensing
    title: str         # 所属文档标题
    content: str       # 清洗并切分后的正文
    source_path: Path  # 原文件路径，用于引用和排查
```

清洗函数采用确定性规则，核心逻辑可以简化为：

```python
def clean_markdown(markdown: str) -> str:
    """移除固定演示声明，并统一换行和多余空行。"""
    # 统一不同操作系统产生的换行符，避免 Windows 和 Linux 文件结果不一致。
    normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")

    # 删除固定合成演示声明，后续再统一处理空白。
    lines = []
    for line in normalized.splitlines():
        if line.strip().startswith("> 本文档为合成演示内容"):
            continue
        lines.append(line)

    return "\n".join(lines).strip()
```

实际实现还做了连续空行压缩、行尾空格清理和首尾空白清理。清洗不是“看到像噪声就随便删”，警告、数字、否定词和业务条件必须保留。

切分函数把清洗和生成 chunk 串起来：

```python
def split_document_into_chunks(document: KnowledgeDocument) -> list[KnowledgeChunk]:
    """把一份知识文档清洗后切分为检索片段。"""
    # 先清洗整篇文档，去掉演示声明和多余空白。
    cleaned_content = clean_markdown(document.content)

    # 再按子标题划分主题；没有子标题时整篇保留为一个 chunk。
    sections = _split_markdown_sections(cleaned_content)

    chunks = []
    for index, section in enumerate(sections):
        chunks.append(
            KnowledgeChunk(
                # 索引从 0 开始，表示片段在文档中的先后顺序。
                chunk_id=f"{document.doc_id}#{index}",
                doc_id=document.doc_id,
                title=document.title,
                content=section,
                source_path=document.source_path,
            )
        )

    return chunks
```

当前切分规则：

1. 没有二级或更深标题时，整篇清洗后的文档保留为一个 chunk。
2. 有 `##`、`###` 等子标题时，每个子标题及其正文成为一个 chunk。
3. 后续 chunk 会补充一级文档标题，避免离开原文档后失去上下文。
4. 这一版还没有最大长度和重叠窗口；等文档变长后再增加。

运行测试：

```powershell
# 进入项目根目录后，使用 python-foundation 的虚拟环境运行全部测试。
& "E:\Project\0基础学agent\实战项目\python-foundation\.venv\Scripts\python.exe" -m pytest -q
```

实际结果：

```text
17 passed, 1 warning
```

加载 `data/synthetic_demo/knowledge` 后的实际结果：

```text
文档数: 4
片段数: 4
```

示例片段：

```text
chunk_id: sop_dispensing#0
doc_id: sop_dispensing
title: 点胶作业指导书
content: # 点胶作业指导书
         确认胶量、压力、温度和点胶路径，首件确认通过后再批量生产。
source_path: data/synthetic_demo/knowledge/sop_dispensing.md
```

当前 4 份合成文档都没有子标题，所以每篇只生成一个 chunk。后续测试使用带 `##` 的模拟长文档，验证了多主题切分和上下文补充逻辑。
### 本节总结问题

1. 为什么不能把整份文档直接作为一个检索单位？清洗和切分分别解决什么问题？
2. 一个 chunk 至少应保留哪些元数据？为什么已经加载了文档，还要保留 `doc_id` 和 `source_path`？
3. 按标题切分和按固定长度切分各有什么优缺点？当前的小型文档为什么适合先按标题或段落切分？

## 三十四、RAG 第三步：Embedding（概念预习，2026-10-10）

### 为什么只靠关键词不够

假设知识文档写的是：

```text
失效模式：出胶量过大。
```

用户却问：

```text
为什么点胶时胶量偏多？
```

“出胶量过大”和“胶量偏多”意思很接近，但字面没有完全相同的关键词。只做关键词匹配时，系统可能找不到这段内容。

Embedding 的目标就是把“意思接近的文字”放到语义空间中相近的位置。

### Embedding 是什么

Embedding 可以理解成一条转换规则：

```text
一段文字
→ embedding 模型
→ 一串数字，也就是向量
```

例如：

```text
“点胶压力异常” → [0.12, -0.38, 0.77, ...]
“清洗喷嘴”     → [0.91, 0.07, -0.21, ...]
```

这串数字叫向量。单独看 `0.12` 或 `-0.38` 没有直接可读含义，真正有用的是：

- 相似文字生成的向量方向接近。
- 不相似文字生成的向量方向较远。

真实 embedding 通常有几百到上千个数字，例如 384 维、768 维或 1536 维。不同模型维度和坐标含义不同。

### 用“语义地图”理解

可以把 embedding 想成一张很大的地图：

- 每个 chunk 是地图上的一个地点。
- 用户问题是地图上的另一个地点。
- 距离近，说明意思比较接近。
- 距离远，说明主题可能无关。

注意不能再用“字面看起来像不像”判断距离，而是比较它们生成的向量。

### 余弦相似度是什么

RAG 常用余弦相似度比较两个向量。

可以先用方向理解：

| 情况 | 含义 |
| --- | --- |
| 两个向量方向接近 | 文字意思相似度较高 |
| 两个向量方向垂直 | 相似度接近 0 |
| 两个向量方向相反 | 相似度接近 -1 |

余弦相似度只负责给出相对分数，不代表“这句话一定是事实”。它解决的是排序问题：哪个 chunk 与问题更相关。

### Embedding 在 RAG 中怎样使用

知识侧：

```text
KnowledgeChunk.content
→ 同一个 embedding 模型
→ chunk 向量
→ 写入向量库
```

用户提问时：

```text
用户问题
→ 同一个 embedding 模型
→ 问题向量
→ 与向量库中的 chunk 向量比较
→ 取最相近的前 k 个 chunk
→ 把这些 chunk 的正文和来源交给大模型
```

`k` 是检索数量，例如前 3 个或前 5 个。

需要特别区分：

- 向量库负责找到相关 chunk。
- 大模型负责根据 chunk 生成回答。
- 向量本身不是答案，不能直接给人阅读。

### 为什么必须使用同一个模型

不同 embedding 模型使用不同的向量空间，可以理解为使用不同的地图坐标。

同一个模型生成的 chunk 向量和问题向量可以比较；不同模型生成的向量通常不能直接比较。

### 当前项目状态

当前已经完成：

```text
Markdown 文件
→ KnowledgeDocument
→ 清洗
→ KnowledgeChunk
```

还没有完成：

```text
KnowledgeChunk
→ Embedding
→ 向量库
→ 相似度检索
```

下一步会先选择 CPU 可运行的 embedding 方案，再实现本地检索。下载模型或依赖前必须先核对 D 盘空间、目标路径和预计体积。

### 本节总结问题

1. Embedding 把文字转换成了什么？为什么只靠关键词匹配可能找不到同义表达？
2. 余弦相似度解决什么问题？向量库检索到 chunk 后，为什么还要把 chunk 正文交给大模型？
3. 文档 chunk 和用户问题为什么必须使用同一个 embedding 模型？
## 三十五、余弦相似度纯 Python 实践（2026-10-10）

### 不下载模型先学什么

Embedding 模型负责把文字变成向量，余弦相似度负责比较向量。两者是不同步骤。

在下载真实模型前，先用普通数字练习向量比较，可以避免把“模型下载问题”和“相似度计算问题”混在一起。

### 余弦相似度的直觉

公式可以先不背，先记住三件事：

1. 点积看两个向量在方向上有多一致。
2. 向量长度用于把结果归一化，避免长向量天然得到更大分数。
3. 最后的分数只表示方向相似程度。

方向结果：

```text
同方向    → 1
垂直      → 0
反方向    → -1
```

### 代码实现

文件位置：

`industrial-quality-agent/rag/similarity.py`

```python
from math import sqrt


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """计算两个非零向量之间的余弦相似度。"""
    # 维度不同就不能逐项相乘，因此直接报错。
    if len(left) != len(right):
        raise ValueError("两个向量的维度必须相同")

    if not left:
        raise ValueError("向量不能为空")

    # 点积：对应位置相乘，再把所有结果相加。
    dot_product = sum(
        left_value * right_value
        for left_value, right_value in zip(left, right)
    )

    # 向量长度：各元素平方和再开平方。
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))

    # 零向量没有明确方向，不能计算方向相似度。
    if left_norm == 0.0 or right_norm == 0.0:
        raise ValueError("零向量无法计算余弦相似度")

    # 余弦相似度 = 点积 / 两个向量长度的乘积。
    return dot_product / (left_norm * right_norm)
```

### 实际运行结果

```text
同方向: 1.0000
方向接近: 0.9939
垂直: 0.0000
反方向: -1.0000
```

新增 6 项测试后，完整测试结果：

```text
23 passed, 1 warning
```

测试覆盖：

- 同方向等于 1。
- 方向接近时大于 0.99。
- 垂直等于 0。
- 反方向等于 -1。
- 维度不同时报错。
- 零向量时报错。

### 重要边界

这些二维数字只是教学示例，不是真正的文字 Embedding。

真实文字向量可能有一千多个数字，而且每个数字通常没有可直接解释的中文含义。它们由训练好的 Embedding 模型生成。

当前项目已经具备比较向量的基础函数，但还没有真实文字向量，所以暂时不能做语义检索。

### 本节总结问题

1. 余弦相似度中，点积和向量长度分别负责什么？
2. 为什么同方向是 1、垂直是 0、反方向是 -1？
3. 为什么两个向量维度必须相同，零向量又不能计算余弦相似度？
## 三十六、RAG 第四步：Top-K 检索排序（概念预习，2026-10-10）

### Top-K 是什么

Embedding 和余弦相似度只能得到“一个问题和一个 chunk 有多相似”的分数。

向量库中通常有很多 chunk，因此需要：

1. 计算问题向量与每个 chunk 向量的相似度。
2. 按相似度从高到低排序。
3. 取前 K 个 chunk。

K 是检索数量的意思。

### 一个简单例子

假设问题与四个 chunk 的相似度是：

```text
chunk A: 0.93
chunk B: 0.71
chunk C: 0.20
chunk D: 0.15
```

如果设置 `K = 2`：

```text
最终返回：chunk A、chunk B
```

如果设置 `K = 1`：

```text
最终返回：chunk A
```

如果设置 `K = 4`：

```text
最终返回：chunk A、chunk B、chunk C、chunk D
```

### K 取得太小或太大

K 太小：

- 返回内容少。
- 如果正确 chunk 排在后面，就会漏掉。
- 大模型可能缺少回答依据。

K 太大：

- 容易把弱相关内容一起交给大模型。
- 上下文变长，增加成本和延迟。
- 无关内容可能干扰回答。

所以 K 不是越大越好，需要在召回率、准确度和成本之间取舍。

### Top-K 不等于最终答案

完整关系是：

```text
问题向量
→ 与所有 chunk 向量比较
→ 按相似度排序
→ 取前 K 个 chunk
→ 把 chunk 正文交给大模型
→ 大模型生成答案
```

Top-K 负责“选出候选资料”，大模型负责“阅读资料并回答”。

### 为什么要保持顺序稳定

如果有两个 chunk 的相似度完全相同，排序结果需要采用稳定、可预测的规则，例如保持原始插入顺序。

否则同一份数据可能每次返回不同结果，后续评测就难以复现。

### 当前项目状态

当前已有：

```text
KnowledgeChunk
cosine_similarity()
```

还没有：

```text
真实文字向量
内存向量库
Top-K 排序函数
持久化索引
```

下一步可以先实现一个纯 Python 的内存向量检索器，再用真实 embedding 模型替换测试向量。

### 2026-10-10 实现与验证

新增文件：

- `industrial-quality-agent/rag/vector_store.py`
- `industrial-quality-agent/tests/test_vector_store.py`

检索结果的数据结构：

```python
@dataclass(frozen=True)
class SearchResult:
    """表示一次向量检索命中的 chunk 和相似度分数。"""

    chunk: KnowledgeChunk  # 命中的知识片段及来源元数据
    score: float           # 查询向量与该片段的余弦相似度
```

内存向量库的核心逻辑：

```python
class InMemoryVectorStore:
    """把 chunk 和向量保存在内存中，并按余弦相似度检索。"""

    def add(self, chunk: KnowledgeChunk, vector: list[float]) -> None:
        """把一个 chunk 及其向量加入内存向量库。"""
        # 维度必须统一，避免库中出现无法互相比较的向量。
        if self._vector_size is not None and len(vector) != self._vector_size:
            raise ValueError("向量维度与向量库现有记录不一致")

        # tuple 是不可变类型，保存后不会被外部代码意外修改。
        self._records.append((chunk, tuple(vector)))

    def search(self, query_vector: list[float], top_k: int = 3) -> list[SearchResult]:
        """返回与查询向量最相似的前 K 个 chunk。"""
        # 逐个计算查询向量与 chunk 向量的余弦相似度。
        scored_records = [
            (chunk, cosine_similarity(query_vector, list(vector)))
            for chunk, vector in self._records
        ]

        # 从高到低排序；分数相同时保持原插入顺序，保证结果可复现。
        scored_records.sort(key=lambda item: item[1], reverse=True)

        # 只返回前 K 个候选，不在这里生成最终回答。
        return [
            SearchResult(chunk=chunk, score=score)
            for chunk, score in scored_records[:top_k]
        ]
```

教学数据使用二维向量，只用于验证代码，不代表真实文字 Embedding。

查询向量 `[1.0, 0.0]`，设置 `top_k=2`：

```text
A: 0.9986 | 喷嘴脏污导致点胶不均
B: 0.9487 | 压力漂移导致胶量过大
```

新增 7 项测试后，完整测试结果：

```text
30 passed, 1 warning
```

测试覆盖：

- 按相似度从高到低排序。
- `top_k` 限制返回数量。
- 分数相同时保持插入顺序。
- 拒绝混合不同维度。
- 拒绝零向量。
- 拒绝小于 1 的 `top_k`。
- 拒绝维度不匹配的查询向量。

内存向量库只负责“选候选”，不负责：

- 把文字变成向量。
- 持久化保存到磁盘。
- 调用大模型生成答案。
### 内存向量库总结问题

1. `InMemoryVectorStore` 保存的两样东西分别是什么？为什么向量要用不可变的 tuple 保存？
2. `search()` 完成哪些步骤？为什么分数相同时要保持插入顺序？
3. 内存向量库为什么不能替代 Embedding 模型，也不能替代大模型生成回答？
### 本节总结问题

1. Top-K 中的 K 表示什么？为什么不能默认把所有 chunk 都交给大模型？
2. K 取得太小和太大分别有什么风险？
3. Top-K 排序完成后，返回的为什么是 chunk 正文和来源，而不是最终回答？
## 三十七、内存向量库零基础重讲（2026-10-11）

### 为什么重讲

2026-10-11 复述检查：第三十六节的“内存向量库总结问题”三题全部回答“不会”。说明代码能跑、30 项测试能过，但职责边界还没有真正理解。因此本节改为零基础重讲，并换成 3 个可以直接对照程序输出回答的问题。

### 类比：一排储物柜

| 概念 | 类比 | 作用 |
| --- | --- | --- |
| chunk | 一个包裹 | 里面装着一小段正文 |
| 向量 | 包裹的“意思坐标” | 一串数字，表示这段文字的意思在哪个方向 |
| 向量库 | 一排储物柜 | 把所有包裹和坐标放在一起 |
| 一条记录 | 一个格子 | 同时放：包裹 + 它的坐标 |
| `search()` | 拿问题坐标挨个格子比 | 最像的排最前，只取前 K 个 |

### 关键点 1：为什么“正文 + 向量”必须一起存

- 只存向量：能知道哪个格子最像，但不知道里面写的什么，拿不出正文交给大模型。
- 只存正文：无法快速比较相似度。
- 所以一条记录 = `KnowledgeChunk`（含 `content` 正文、`source_path` 来源）+ 向量。
- 向量用 `tuple` 保存：`tuple` 不可变，避免存进去之后被别的代码改掉。

### 关键点 2：`search()` 只做三步

1. **算分**：拿问题向量和每条记录的向量做余弦相似度。
2. **排序**：按分数从高到低排。
3. **截取**：取前 `top_k` 个，包装成 `SearchResult(chunk, score)` 返回。

容易记错的细节：

- `sort(..., reverse=True)`：Python 默认从小到大排（升序），`reverse=True` 反成从大到小，最像的排最前。
- 分数完全相同时：Python 排序是**稳定排序**，谁先进库谁排前面，保证结果可复现、测试可以断言。
- `top_k` 小于 1 会被拒绝，因为“取前 0 个候选”没有意义。

### 关键点 3：职责边界（谁干什么活）

| 事情 | 谁负责 | 现在做了吗 |
| --- | --- | --- |
| 文字 → 向量 | Embedding 模型 | 还没有 |
| 保存 chunk + 向量 | 向量库 `add()` | 已做 |
| 算相似度、选前 K 个候选 | 向量库 `search()` | 已做 |
| 读正文、组织语言写答案 | 大模型 | 还没有 |
| 存到磁盘、重启后还在 | 持久化向量库 | 还没有 |

一句话总结：**向量库只负责“选候选”，既不做 Embedding，也不写答案，也不做持久化。**

### 关键点 4：`add()` 会拒绝的三种向量

- 空向量 `[]`：连坐标都没有。
- 零向量 `[0.0, 0.0]`：长度为 0，没有方向，算不出夹角。
- 维度不一致：库里存的是 2 维，又塞进来 3 维，无法逐项相乘。

### 演示脚本与真实运行输出

2026-10-11 新增 `industrial-quality-agent\rag_demo_vector_store.py`（带中文注释，只读演示，不改动项目逻辑）。

运行命令（在 `industrial-quality-agent` 目录下）：

```powershell
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" rag_demo_vector_store.py
```

实际输出：

```text
=== 第 1 步：向量库里一条记录存了哪两样东西 ===
  chunk_a | 向量=(1.0, 0.0) | 正文=点胶量偏高容易溢胶和拉丝。
  chunk_b | 向量=(0.6, 0.8) | 正文=清洗喷嘴可以恢复点胶一致性。
  chunk_c | 向量=(0.0, 1.0) | 正文=设备点检表需要每天签字确认。

=== 第 2 步：拿问题向量和每条记录的向量逐个算余弦相似度 ===
  问题 与 chunk_a 的相似度 = 1.0000
  问题 与 chunk_b 的相似度 = 0.6000
  问题 与 chunk_c 的相似度 = 0.0000

=== 第 3 步：按分数从高到低排序，取前 top_k 个 ===
  第1名 | chunk_a | 分数=1.0000 | 交给大模型的正文=点胶量偏高容易溢胶和拉丝。
  第2名 | chunk_b | 分数=0.6000 | 交给大模型的正文=清洗喷嘴可以恢复点胶一致性。
  （注意：只返回了候选，答案还没有生成；写答案是大模型的事）

=== 第 4 步：不合法的向量会被拒绝 ===
  拒绝 空向量 -> 向量不能为空
  拒绝 零向量（长度为 0，没有方向） -> 零向量不能写入向量库
  拒绝 维度与库中已有记录不一致 -> 向量维度与向量库现有记录不一致
```

### 本节总结问题（更容易版，2026-10-11）

1. 看演示输出的第 1 步：`chunk_b` 那一行里，它的向量是什么？它的正文是什么？
2. 演示输出第 2 步给出三个分数：1.0000、0.6000、0.0000。分数越大表示“越像”还是“越不像”？为什么 `top_k=2` 时第 2 名是 `chunk_b`，而不是 `chunk_c`？
3. 这个向量库**不会**做哪两件事？（提示：看第 3 步括号里那句话；另一件是下一步才要做的“把文字变成向量”）

## 三十八、Embedding 模型选型（2026-10-11）

### 先回答：为什么必须单独有一个 Embedding 模型

内存向量库的 `add()` 只接受“已经算好的向量”，它自己不会把文字变成向量。所以整条链路上还缺一个角色：

```text
文字（chunk 正文 / 用户问题） → [Embedding 模型] → 向量 → 向量库
```

这个角色就是 Embedding 模型。它是一份**训练好的权重文件**（一堆数字），不是会聊天的“大模型”。它只干一件事：把一段文字稳定地映射成一串固定长度的数字。

### 选型四条标准（针对当前处境：无显卡、中文文档、纯 CPU）

1. **中文能力**：知识文档是中文，优先选明确支持中文、或用中文语料训练过的模型。
2. **体积与速度**：没有显卡只能用 CPU，目标 < 500 MB，最好 < 150 MB。
3. **向量维度**：维度就是向量的数字个数（384 / 512 / 768）。维度越高通常越准，但也越慢、越占内存。中小任务 512 维够用。
4. **许可与来源**：优先 Apache-2.0 / MIT，来源以 Hugging Face 官方模型页或可信镜像为准。

### 三条技术路线（依赖体积差别巨大）

| 路线 | 需要安装 | 预计新增体积 | 特点 |
| --- | --- | --- | --- |
| A. `sentence-transformers`（PyTorch） | torch + transformers | 约 2–2.5 GB | 教程最多，但对纯 CPU 环境太重 |
| B. `fastembed`（ONNX Runtime） | onnxruntime + tokenizers | 约 150–300 MB | 轻、快、为 CPU 优化，代码少 |
| C. `onnxruntime` + `tokenizers` 手动组合 | 同上，模型需自己下 | 约 150–250 MB | 控制最细，步骤最多，适合理解原理 |

当前建议：**先走 B**，等整条 RAG 链路跑通、原理理解之后，再决定要不要换 A。

### 候选模型对比

| 模型 | 维度 | 体积（约） | 语言 | 许可 |
| --- | --- | --- | --- | --- |
| `BAAI/bge-small-zh-v1.5` | 512 | 约 95 MB | 中文 | MIT |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | 约 470 MB | 50+ 语言（含中文） | Apache-2.0 |
| `shibing624/text2vec-base-chinese` | 768 | 约 400 MB | 中文 | Apache-2.0 |

首推 `BAAI/bge-small-zh-v1.5`：中文、约 95 MB、512 维、MIT 许可，CPU 速度可接受。

### 落盘位置（遵守全局磁盘规则）

| 内容 | 位置 |
| --- | --- |
| pip 缓存 | `D:\AI-Cache\pip` |
| 模型文件 | `D:\AI-Models\hf`（用 `HF_HOME` 或缓存目录参数指定） |
| Python 依赖 | 现有项目虚拟环境 `.venv`（在 E 盘项目内，约 +200 MB） |
| C 盘 | 不使用 |

2026-10-11 实测磁盘：C 剩余 33.7 GB，D 剩余 150.3 GB，E 剩余 55.2 GB。D 盘空间充足。

### 一个必须先知道的坑

国内直连 `huggingface.co` 经常失败，需要镜像：`HF_ENDPOINT=https://hf-mirror.com`；Python 包可以用清华或阿里 PyPI 镜像。因此实际下载前要先做小文件测速，选最快的源，再开始下载。

### 本节总结问题

1. 为什么内存向量库不能自己把文字变成向量？这个洞由谁来补？
2. 当前环境是“只有 CPU + 中文文档”。下面两个模型选哪个，为什么？A. `all-MiniLM-L6-v2`（英文、约 80 MB、384 维）；B. `BAAI/bge-small-zh-v1.5`（中文、约 95 MB、512 维）。
3. 同样都能算向量，为什么先不建议装 `sentence-transformers` + torch？

## 三十九、用真实模型把文字变成向量（2026-10-11）

### 已完成的事

| 项目 | 结果 |
| --- | --- |
| 依赖 | `fastembed 0.9.0` + `onnxruntime 1.23.2` + `tokenizers 0.23.3` 等，安装在项目 `.venv` |
| 依赖体积 | `.venv` 从 43.2 MB → 233.2 MB（增加 189.9 MB） |
| 模型 | `BAAI/bge-small-zh-v1.5`（fastembed 实际拉取的是 `Qdrant/bge-small-zh-v1.5` 的 ONNX 版本） |
| 模型位置 | `D:\AI-Models\fastembed`，占 **90.8 MB** |
| pip 缓存 | `D:\AI-Cache\pip` |
| 新代码 | `industrial-quality-agent\rag\embeddings.py`（`EmbeddingModel` 类，中文注释） |
| 查询脚本 | `industrial-quality-agent\check_embedding_models.py`（离线列出 fastembed 支持的模型） |

### 代码结构

```python
class EmbeddingModel:
    def __init__(self, model_name=DEFAULT_MODEL_NAME, cache_dir=DEFAULT_CACHE_DIR): ...
    @property
    def dimension(self) -> int: ...
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
```

关键设计：

- **延迟导入**：`from fastembed import TextEmbedding` 写在 `__init__` 里，只有真正创建对象时才加载 onnxruntime。
- **返回普通 list**：fastembed 内部用 numpy，这里统一转成 `list[float]`，好处是向量库代码不依赖 numpy 类型。
- **缓存目录指向 D 盘**：`D:\AI-Models\fastembed`，第一次自动下载，之后离线可用。

### 真实运行输出

```text
模型：BAAI/bge-small-zh-v1.5
向量维度：512
问题的前 5 个数字：[-0.0153, -0.0297, -0.0138, 0.0335, -0.0197]

问题：点胶量偏高会有什么问题？
  第1名 分数=0.8360  点胶量偏高容易溢胶和拉丝。
  第2名 分数=0.5800  清洗喷嘴可以恢复点胶一致性。
  第3名 分数=0.4200  设备点检表需要每天签字确认。
```

这一步的意义：**检索第一次跑在真实语义上**。问题里没有出现"溢胶""拉丝"这些词，但模型仍然把正确的那句排到第一，因为它是按"意思"而不是"字面"算相似的。

### 三个注意点

1. **512 维 ≠ 之前的 2 维**：以前手写的 `[1.0, 0.0]` 是教学数据；现在每段文字都会变成 512 个数字。接口没变（都是 `list[float]`），所以向量库不用改。
2. **第一次联网、之后离线**：第一次运行会把模型下载到 `D:\AI-Models\fastembed`，之后直接用本地文件。
3. **Windows 符号链接警告可以忽略**：`huggingface_hub` 提示这台机器不支持符号链接，只是缓存会多占一点空间，不影响运行；想关掉警告可以设置环境变量 `HF_HUB_DISABLE_SYMLINKS_WARNING=1`。

### 磁盘说明（避免误会）

`D:\AI-Models` 当时显示占用 1,018 MB，明细如下：

| 目录 | 体积 | 说明 |
| --- | --- | --- |
| `fastembed` | 90.8 MB | 本次下载的 Embedding 模型 |
| `rembg` | 927.6 MB | 之前别的工具（抠图）留下的，与本次无关 |

### 本节总结问题

1. 这个 Embedding 模型产出多少维的向量？它负责的是"文字 → 向量"，还是"向量 → 答案"？
2. 演示里问题"点胶量偏高会有什么问题？"排第一的是哪一句、分数多少？这说明检索是按"字面相同"还是按"意思相近"排序的？
3. 为什么第一次运行需要联网、之后可以离线？模型文件放在哪个盘、大约多大？

## 四十、端到端检索：把真向量接进向量库（2026-10-11）

### 这一节把链路接通了

```text
4 份 Markdown 知识文档
   ↓ load_markdown_documents()      加载 + 提取标题 + 稳定 doc_id
   ↓ clean_markdown()               去掉“合成演示内容”声明、压掉多余空行
   ↓ split_document_into_chunks()   按小标题切分，保留 doc_id / title / source_path
   ↓ EmbeddingModel.embed_texts()   真实模型转成 512 维向量
   ↓ InMemoryVectorStore.add()      一个格子 = chunk + 向量
问题 → embed_texts() → store.search() → 前 K 个候选（含来源）+ 分数
```

### 新增文件

| 文件 | 作用 |
| --- | --- |
| `rag/pipeline.py` | `KnowledgeBase` 类：`build()` 建索引，`search()` 检索；文件末尾有真实演示 |
| `tests/test_pipeline.py` | 6 项测试：4 份文档入库、正文交给模型、声明被清洗、两个语义命中、未建索引时报错 |

### 关键设计：允许注入向量模型

```python
def __init__(self, knowledge_dir: Path, embedder: EmbeddingModel | None = None) -> None:
    self.embedder = embedder or EmbeddingModel()
```

- 正式运行：不传 `embedder`，内部创建真实模型。
- 测试：传入 `FakeEmbedder`（返回固定 2 维向量并记录输入），于是测试跑得很快，还能断言“到底把哪段文字交给了模型”。

这就是“依赖注入”的实际用途：**同一套流程，既能接真模型，也能接假模型做测试。**

### 运行命令

```powershell
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m rag.pipeline
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m pytest -q tests
```

### 真实输出（3 个问题全部命中正确文档）

```text
知识目录：data\synthetic_demo\knowledge
入库片段数：4

问题：胶量偏多可能是什么原因？
  第1名 分数=0.6732 来源=fmea_dispensing.md
        正文预览：# FMEA：点胶工序  失效模式：胶量偏多。可能原因：压力漂移、胶筒温度异常。...
  第2名 分数=0.6074 来源=case_dirty_nozzle.md

问题：喷嘴脏了要怎么处理？
  第1名 分数=0.6864 来源=case_dirty_nozzle.md
  第2名 分数=0.6060 来源=sop_cleaning.md

问题：点胶前要确认哪些参数？
  第1名 分数=0.7075 来源=sop_dispensing.md
  第2名 分数=0.6291 来源=fmea_dispensing.md
```

测试结果：**36 passed**（原 30 项 + 新增 6 项）。

### 当前边界（别高估现在的水平）

| 已经有 | 还没有 |
| --- | --- |
| 加载、清洗、切分、真实向量、向量库、排序、返回来源 | 生成自然语言答案（需要大模型） |
| 每份文档一个片段（文档很短） | 持久化（每次启动都重新算向量） |
| 关键词外还能按语义命中 | Rerank、引用格式、无答案拒答、召回率评测 |

### 本节总结问题

1. `build()` 依次做了哪四步？最后返回的是什么？
2. 为什么检索时，问题也必须用**同一个** Embedding 模型转成向量？
3. 现在 `search()` 返回的是"候选片段 + 分数 + 来源"。要让它变成"能回答问题的 RAG"，还缺哪一步？谁来做？

## 四十一、RAG 第七步：答案生成与拒答（概念预习，2026-10-12）

### 现在缺的是最后一步

检索已经能返回“候选片段 + 分数 + 来源”，但用户要的是一句话答案。这一步必须由大模型完成，因为只有它能把资料读成通顺的中文。

### 提示词怎么拼（三段式）

RAG 的提示词不是随便聊，而是固定三段：

1. **系统指令**（定角色和规矩）：你是工业质量助手；只能依据资料回答；资料里没有就说“知识库中没有相关内容”；每句话标注来源编号。
2. **资料区**：把检索到的前 K 个 chunk 正文和来源拼进去。
3. **用户问题**。

示例：

```text
[系统指令]
你是工业质量知识库助手。只能依据【资料】回答，不得编造。
如果【资料】中没有答案，必须回答：知识库中没有相关内容。
回答时请在句末标注来源编号，如 [1]。

[资料]
[1] 来源：fmea_dispensing.md
失效模式：胶量偏多。可能原因：压力漂移、胶筒温度异常。建议：监控压力并设置报警阈值。

[用户问题]
胶量偏多可能是什么原因？
```

### 为什么必须要求“带来源”

- 让人能核对：没有来源的回答无法判断真假。
- 让幻觉可发现：答案里出现资料中没有的词，一眼就能看出。
- 面试可讲：引用准确率是可以量化的指标。

### 无答案拒答的两种做法（关键概念）

| 做法 | 怎么做 | 优点 | 缺点 |
| --- | --- | --- | --- |
| 靠分数阈值 | 检索最高分低于阈值（例如 0.5）就直接回“知识库中没有相关内容” | 便宜、快，不调用大模型 | 阈值需要调；语义相近但无关时可能误拒 |
| 靠提示词 | 把资料交给大模型，要求它“资料里没有就说不知道” | 更灵活，能分辨细微差别 | 大模型仍可能硬答（幻觉） |

工程上通常**两者都用**：先看分数，再让模型复核。

### 接口设计：为什么先写“假模型”

和 `EmbeddingModel` 一样，大模型也必须能替换、能测试：

```python
class AnswerGenerator:                    # 只规定“长什么样”，不写具体实现
    def generate(self, question: str, contexts: list[SearchResult]) -> str: ...
```

- 正式实现：调用真实大模型。
- 测试实现：`FakeGenerator` 直接返回固定字符串，让测试跑得快、不花钱、不联网。

这就是上一节学过的“依赖注入”的第二次应用：**流程不变，模型可换。**

### 候选大模型方案（待用户拍板；涉及费用与数据边界）

| 方案 | 费用 | 速度 | 数据边界 | 需要下载 |
| --- | --- | --- | --- | --- |
| A. 国内大模型 API（DeepSeek / 智谱 GLM / 通义等） | 按量计费，通常有免费额度，单价低 | 秒级 | 文本发往服务商 | 只需 `requests` |
| B. OpenAI 或兼容网关 API | 按量计费，需绑卡 | 秒级 | 数据出境 | 只需 `requests` |
| C. 本地 Ollama + 小模型（如 `qwen2.5:1.5b`） | 完全免费 | 慢（无显卡时每段回答数秒到数十秒） | 数据不出本机 | 约 1–2 GB（放 D 盘） |

价格与免费额度经常变动，接入前必须联网核对，本节不写死具体数字。选定方案前不得安装、不得注册、不得产生费用。

### 本节总结问题

1. RAG 的提示词为什么必须包含“检索到的资料”？不把资料给大模型、直接问它，会有什么风险？
2. 为什么要求回答必须标注来源？
3. 知识库里没有答案时，有哪两种拒答做法？各自的优缺点是什么？

## 四十二、本地部署大模型：Ollama 绿色版（2026-10-12）

### 目标

让“答案生成”这一步在**本地**完成：0 元费用、数据不出本机、断网也能用。

### 为什么用绿色版而不是安装版

| 方式 | 体积 | 风险 |
| --- | --- | --- |
| `OllamaSetup.exe` 安装版 | 1505 MB | 默认装到 `C:\Users\<用户>\AppData\Local\Programs\Ollama`，必须靠 `/DIR` 参数纠正，**万一不生效就会占用 C 盘** |
| **`ollama-windows-amd64.zip` 绿色版** | 1400 MB | 只需解压到 D 盘，**不存在“装到 C 盘”的可能** |

用户明确要求“所有安装目录必须检查、必须落在 D 盘”，因此选绿色版。

### 落盘清单（全部在 D 盘）

| 内容 | 位置 | 体积 |
| --- | --- | --- |
| Ollama 程序 | `D:\AI-Tools\Ollama`（`ollama.exe` + `lib\` 含 CUDA 运行库） | 1851.8 MB |
| 下载的压缩包 | `D:\Downloads\ollama-windows-amd64.zip` | 1400 MB |
| 模型文件 | `D:\AI-Models\ollama`（blobs + manifests） | 940.4 MB |
| 环境变量 | `OLLAMA_MODELS=D:\AI-Models\ollama`；用户 PATH 追加 `D:\AI-Tools\Ollama` | 只写注册表项 |
| C 盘 | **未写入**（安装前后 C 盘剩余从 33.9 GB 变为 34.1 GB） | — |

### 下载与校验过程

1. 测速：GitHub 直链 691 KB/s > ollama.com 379 KB/s，选 GitHub 直链。
2. 实际下载 1400.0 MB，用时约 7 分钟（平均约 3.3 MB/s，比测速时快很多）。
3. 用官方 `sha256sum.txt` 校验：`E5ECFF02...DBBBD5`，**通过**。
4. `Expand-Archive` 解压到 `D:\AI-Tools\Ollama`，用时 5 秒。

### 遇到的坑一：Ollama 内置下载器被代理挡住

```text
Error: redirect target not allowed: ...r2.cloudflarestorage.com resolves to non-public 198.18.0.20
```

`198.18.0.0/15` 是代理软件（Clash 之类）的 **fake-IP 段**。Ollama 出于安全考虑拒绝“重定向到非公网 IP”。解决办法：**改用 curl 手动下载**（curl 不做这个检查），步骤是：

1. `curl` 取 manifest：`https://registry.ollama.ai/v2/library/qwen2.5/manifests/1.5b`
2. 按 manifest 里每个 layer 的 `digest` 与 `size`，用 curl 下载 `.../blobs/sha256-<digest>`
3. 逐个校验 SHA256，放进 `D:\AI-Models\ollama\blobs\`
4. 把 manifest 放到 `D:\AI-Models\ollama\manifests\registry.ollama.ai\library\qwen2.5\1.5b`

### 遇到的坑二：`-partial` 文件“大小对了”不代表下载完成

Ollama 会**按最终大小预分配**文件，所以 `sha256-xxx-partial` 显示 940.4 MB 时，里面大部分还是空数据：

```text
文件大小 986048512 字节（和模型层完全一致）
SHA256   d1bb1fa6... ≠ 183715c4...   ← 内容其实不完整
```

结论：**判断下载是否完成只能看哈希，不能看大小**。这也是为什么每一步都要校验 SHA256。

### 最终结果

```text
$ ollama list
NAME            ID              SIZE      MODIFIED
qwen2.5:1.5b    ba02c0e8e90e    986 MB    7 minutes ago
```

实测一次问答（调用本地 HTTP 接口 `POST http://127.0.0.1:11434/api/generate`）：

```text
问题：用一句话说明点胶工艺中“胶量偏多”可能带来什么问题。

回答："胶量偏多"可能导致产品粘合效果不佳，可能产生气泡、脱层等问题。

总耗时     6.30 s（其中首次加载模型 5.02 s）
生成 tokens 23
生成速度   83.1 tokens/s
$ ollama ps
PROCESSOR  100% GPU      ← 用的是 GTX 1650，不是 CPU
```

83 tokens/s 意味着：**本地回答一秒能写八十多个汉字级 token**，做 RAG 演示完全够用，而且 0 费用、数据不出本机。

### 本节总结问题

1. 选绿色版而不是安装版，主要是为了避开什么风险？Ollama 程序和模型分别放在哪个目录？
2. 为什么“`-partial` 文件大小和官方一致”不能说明下载完成？应该用什么判断？
3. 这次模型跑在 CPU 还是 GPU 上？你是从哪里看出来的？

## 四十三、RAG 第八步：答案生成与拒答（代码落地，2026-10-14）

第四十一节讲的是“概念”，这一节把概念变成能跑的代码：三段式提示词、来源编号、分数阈值拒答。

本阶段先用 `FakeGenerator`（假生成器）把流程和测试跑通；接真实 Ollama 是阶段 1 的事。

### 一、先看结果：这条流程现在长什么样

运行 `python -m rag.answer`，真实输出：

```text
[系统指令]
你是工业质量知识库助手，只依据【资料】回答问题，不得编造。
如果【资料】中没有答案，必须回答：知识库中没有相关内容。
回答时请在句末标注来源编号，例如 [1]。

[资料]
[1] 来源：fmea_dispensing.md
失效模式：胶量偏多。可能原因：压力漂移、胶筒温度异常。建议：监控压力并设置报警阈值。

[2] 来源：case_dirty_nozzle.md
现象：局部点胶不均。根因：喷嘴残留物导致出胶受阻。措施：清洁喷嘴并增加首件检查。

[用户问题]
胶量偏多可能是什么原因？

============================================================
[回答] 胶量偏多可能是什么原因？
        最高分=0.6732  回答=【假模型】根据资料，这里应该是真实回答。
[拒答] 公司年假有多少天？
        最高分=0.3079  回答=知识库中没有相关内容。
```

三件事一次看全：

1. 提示词确实是**三段**：系统指令、资料、用户问题。
2. 相关问题最高分 **0.6732**，过了阈值 → 调用生成器。
3. 无关问题最高分 **0.3079**，没过阈值 → **直接拒答，连模型都没调用**。

### 二、为什么分成“检索”和“生成”两层

| 类 | 只负责一件事 | 换掉它会怎样 |
| --- | --- | --- |
| `KnowledgeBase` | 找资料：把问题变成向量、检索出前 K 个片段 | 检索策略要升级（加 BM25、Rerank）时，只改它 |
| `AnswerGenerator` | 写答案：根据资料生成中文回答 | 换大模型（假模型 → Ollama → 云 API）时，只改它 |
| `RagAnswerer` | 串流程 + 拒答判断 | 这条流水线本身很少变 |

一句话：**一层只干一件事，换模型不影响检索，换检索不影响生成。**

### 三、为什么先写“假生成器”

类比：拍戏先让替身演员走位，把机位和灯光调好，主角最后才上场。

`FakeGenerator` 就是替身，它有三个好处：

1. **快**：整个测试 5 秒跑完，不用等模型。
2. **不花钱、不联网**：本地模型或云 API 都不碰。
3. **能做断言**：它会记录“每次被调用时收到的问题和资料”，测试才能检查“资料到底有没有传进去”。

这是“依赖注入”的第二次应用（第一次是 `EmbeddingModel`）：**流程不变，模型可换。**

### 四、代码逐段讲解

文件：`industrial-quality-agent\rag\answer.py`

**第 1 段：把拒答文案写成常量**

```python
REFUSAL_MESSAGE = "知识库中没有相关内容。"
```

理由：业务代码和测试引用同一个字符串，将来改文案只改一处，不会出现两处不一致。

**第 2 段：三段式提示词由两个函数拼出来**

```python
def build_context_block(contexts: list[SearchResult]) -> str:
    """把检索结果拼成提示词里的【资料】区：每段带编号和来源文件名。"""
    blocks: list[str] = []
    for index, result in enumerate(contexts, start=1):
        # 只显示文件名，不把完整本地路径交给模型，避免泄露无关信息。
        source_name = result.chunk.source_path.name
        content = result.chunk.content.strip()
        blocks.append(f"[{index}] 来源：{source_name}\n{content}")
    return "\n\n".join(blocks)
```

`enumerate(..., start=1)` 让编号从 1 开始（给人看的编号从 1 起更自然），它就是回答里 `[1]`、`[2]` 的来源。

```python
def build_prompt(question: str, contexts: list[SearchResult]) -> str:
    return (
        "[系统指令]\n" + SYSTEM_INSTRUCTION
        + "\n\n[资料]\n" + build_context_block(contexts)
        + "\n\n[用户问题]\n" + question.strip()
    )
```

拆成两个函数的好处：测试可以单独检查“资料区格式对不对”，不用关心整段提示词。

**第 3 段：接口用抽象基类，禁止直接实例化**

```python
class AnswerGenerator(ABC):
    """答案生成器接口：只规定“长什么样”，不规定“怎么实现”。"""

    @abstractmethod
    def generate(self, question: str, contexts: list[SearchResult]) -> str:
        raise NotImplementedError
```

`ABC` + `@abstractmethod` 的效果：`AnswerGenerator()` 会直接抛 `TypeError`。这是在用代码表达“**这是接口，不是实现**”，避免有人误用。

**第 4 段：假生成器要记录每次调用**

```python
class FakeGenerator(AnswerGenerator):
    def __init__(self, answer: str = "【假模型】根据资料，这里应该是真实回答。") -> None:
        self._answer = answer
        # 每次调用的入参都存下来，测试才能检查“到底有没有被调用”“传了什么进去”。
        self.calls: list[tuple[str, list[SearchResult]]] = []

    def generate(self, question: str, contexts: list[SearchResult]) -> str:
        self.calls.append((question, list(contexts)))
        return self._answer
```

关键在 `self.calls`：测试靠它断言“拒答时一次都没调用”。

**第 5 段：拒答发生在调用模型之前**

```python
    def answer(self, question: str) -> AnswerResult:
        contexts = self.retriever.search(question, top_k=self.top_k)            # 第 1 步：找资料
        top_score = max((result.score for result in contexts), default=0.0)     # 第 2 步：看最高分

        # 第 3 步：资料不够相关就直接拒答。注意这里连大模型都不调用：
        # 既省钱，也不给幻觉留任何机会。
        if not contexts or top_score < self.min_score:
            return AnswerResult(..., refused=True, ...)

        # 第 4 步：资料够相关，才拼提示词并调用生成器。
        answer = self.generator.generate(question, contexts)
        return AnswerResult(..., refused=False, ...)
```

`max(..., default=0.0)` 处理“一条都没检索到”的情况：此时 `max()` 没有输入，给个默认 0.0，代码不会崩。

### 五、8 个测试分别在保护什么

| 测试 | 保护的点 |
| --- | --- |
| `test_answer_generator_cannot_be_instantiated` | 接口不能被直接实例化 |
| `test_prompt_has_three_sections` | 提示词三段齐全，系统指令原文在 |
| `test_context_block_numbers_sources` | 资料从 `[1]` 开始编号，并带来源文件名 |
| `test_answer_calls_generator_and_returns_sources` | 高分时调用生成器，且**资料真的传进去了** |
| `test_low_score_refuses_without_calling_generator` | 低分时拒答，且**一次模型都不调用** |
| `test_score_equal_to_threshold_is_not_refused` | 边界：分数正好等于阈值算通过 |
| `test_empty_contexts_refuses` | 空资料也拒答，不许拿空资料问模型 |
| `test_top_k_limits_contexts` | `top_k` 真的传到了检索器 |

完整测试：**44 passed**（原有 36 项 + 新增 8 项）。

### 六、怎么运行

```powershell
# 进入项目目录
cd E:\Project\0基础学agent\industrial-quality-agent

# 运行全部测试
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m pytest -q tests

# 运行演示（打印三段式提示词 + 走一遍回答和拒答）
& "..\实战项目\python-foundation\.venv\Scripts\python.exe" -m rag.answer
```

**踩坑记录**：直接运行 `python rag\answer.py` 会报

```text
ModuleNotFoundError: No module named 'rag'
```

原因和 2026-10-05 那次完全一样：Python 会把**脚本所在目录**放进模块搜索路径。脚本在 `rag\` 里，它就只在 `rag\` 里找名叫 `rag` 的包，当然找不到。正确做法是用 `-m 包名.模块名` 从项目根目录运行。

### 七、这个 0.5 阈值靠谱吗（重要提醒）

**0.5 只是起步值，不是结论。**

- 阈值太高 → **误拒**：本来知识库里有答案，却回答“没有相关内容”。
- 阈值太低 → **放开幻觉**：不相关的内容也被送去生成，模型只能硬编。

本次观测：正确答案 0.6732、无关问题 0.3079，在当前 4 份小文档下 0.5 能把两者分开。但文档一多，分数分布会重叠，必须用评测集重新校准。这就是阶段 2（11 月 1 日至 10 日）要做的事。

### 八、遗留与下一步

- **阶段 1**：把 `FakeGenerator` 换成真实 Ollama（`http://127.0.0.1:11434`，OpenAI 兼容接口 `/v1`），必须处理三种异常：模型没启动、请求超时、返回格式不是预期。
- **阶段 2**：建 30 条评测集（含 10 条拒答题），用数据校准 `min_score`。
- **还没做**：现在只要求模型“标注来源编号”，但还没有校验它是否真的标了、标得对不对——引用准确率要在评测阶段才能算出来。

### 本节总结问题

1. 为什么 `RagAnswerer` 在分数不够时选择“连大模型都不调用”，而不是“先问一下大模型、让它自己说不知道”？
2. `AnswerGenerator` 和 `FakeGenerator` 是什么关系？为什么测试里要用假的那个？
3. 现在的 0.5 阈值能直接信吗？要凭什么把它调准？调太高和调太低分别会出什么问题？