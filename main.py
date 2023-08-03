from src.tokenizer import Tokenizer

code = """
import whatever
a = b
c = d
a
b
a()
b()
c()
"""

tokens = [*Tokenizer(code)]

print(code)

print(tokens)
