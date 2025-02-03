from src.main.ast import parse
test_str = "printf('Hello World')"
test_result = "char[] var = \"Hello World\""

print(parse(test_str).compile())
