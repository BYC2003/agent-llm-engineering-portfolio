import json

bad_json = '''{
  "name": "张小明",
  "age": 18
}'''

try:
    student = json.loads(bad_json)
except json.JSONDecodeError as exc:
    print("读取失败")
    print("错误原因：", exc.msg)
    print("出错行号：", exc.lineno)
    print("出错列号：", exc.colno)
    print("字符位置：", exc.pos)
else:
    print("读取成功：", student)
finally:
    print("本次 JSON 读取尝试结束")