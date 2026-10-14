# Python 练习目录

这个目录按知识点分类，所有命令都建议在 `python-foundation` 根目录执行。
`data/` 只放输入数据和生成文件，`tests/` 放自动化测试，不把练习代码放进去。

## 目录结构

```text
exercises/
├─ basics/                   # Python 基础语法
├─ files_and_exceptions/     # 文件读写与异常处理
├─ json/                     # JSON 数据与文件读写
├─ modules/                  # 模块、包、__name__、循环导入
└─ classes/                  # 类和对象、self、__init__、默认值陷阱
```

## 1. 基础语法

```powershell
# 运行变量、条件、循环、函数和类的基础复习
& ".\.venv\Scripts\python.exe" "exercises\basics\11_basic_syntax.py"
```

## 2. 文件与异常

目录：`exercises/files_and_exceptions/`

- `01_io.py`：最小文件写入和读取
- `02_file_exercise.py`：Path、mkdir、write_text、read_text
- `03_exception.py`：正常路径和 FileNotFoundError
- `04.py`：文件读写小测试
- `10_custom_exception.py`：自定义异常
- `12_exception_exit_code.py`：退出码

```powershell
# 运行文件读写示例
& ".\.venv\Scripts\python.exe" "exercises\files_and_exceptions\01_io.py"

# 运行退出码示例；这里传入合法金额，避免触发失败退出码
& ".\.venv\Scripts\python.exe" "exercises\files_and_exceptions\12_exception_exit_code.py" "100"
```

## 3. JSON

目录：`exercises/json/`

- `05_json_basics.py`：Python 对象和 JSON 字符串
- `06_json_file.py`：JSON 文件读写
- `07_json_error.py`：字符串坏 JSON
- `08_json_file_error.py`：文件坏 JSON
- `09_json_safe_write.py`：临时文件和安全替换

```powershell
# 运行 JSON 转换示例
& ".\.venv\Scripts\python.exe" "exercises\json\05_json_basics.py"
```

## 4. 模块与包

目录：`exercises/modules/`

- `name_main_demo.py`：观察 `__name__`
- `import_name_demo.py`：观察导入后的模块名
- `module_demo/`：包内相对导入
- `circular_import_demo/`：循环导入和修复示例

```powershell
# 直接运行 name_main_demo，观察 __name__ == "__main__"
& ".\.venv\Scripts\python.exe" "exercises\modules\name_main_demo.py"

# 按模块方式运行，观察被导入时不会自动执行 main()
& ".\.venv\Scripts\python.exe" "-m" "exercises.modules.import_name_demo"

# 运行包内相对导入示例
& ".\.venv\Scripts\python.exe" "-m" "exercises.modules.module_demo.main"

# 运行循环导入修复后的示例
& ".\.venv\Scripts\python.exe" "-m" "exercises.modules.circular_import_demo.fixed_main"
```

`circular_import_demo/bad_a.py` 和 `bad_b.py` 是故意保留的错误示例，单独运行会触发 `ImportError`，用来观察循环导入问题。

## 5. 类与对象

目录：`exercises/classes/`

- `13_class_independent.py`：独立完成函数和类
- `14_self_value_trace.py`：观察参数传入和 `self`
- `15_init_demo.py`：观察 `__init__` 自动执行
- `16_mutable_default_demo.py`：观察可变默认值陷阱
- `17_inheritance_demo.py`：观察继承、`super()` 和方法复用
- `18_composition_demo.py`：观察组合关系 `has-a`

```powershell
# 运行类和对象练习
& ".\.venv\Scripts\python.exe" "exercises\classes\13_class_independent.py"

# 运行 self 和 __init__ 的观察示例
& ".\.venv\Scripts\python.exe" "exercises\classes\14_self_value_trace.py"
& ".\.venv\Scripts\python.exe" "exercises\classes\15_init_demo.py"
& ".\.venv\Scripts\python.exe" "exercises\classes\17_inheritance_demo.py"
& ".\.venv\Scripts\python.exe" "exercises\classes\18_composition_demo.py"
```



