# 从同一个 modules 包导入 name_main_demo 模块。
# 需要用模块方式运行：python -m exercises.modules.import_name_demo
from . import name_main_demo

# 打印导入完成后自己的提示。
print("导入 name_main_demo 完成")
