from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from ..utils.mem_iter import MemIter
import re

class TokenType(StrEnum):
    OPERATOR = auto()
    STRING_LITERAL = auto()
    WHITESPACE = auto()
    VAR_NAME = auto()
    UNKNOWN = auto()
    NEW_LINE = auto()

operators = {
    "=",
}
operators_max_size = max(len(x) for x in operators)
@dataclass(slots=True)
class Token:
    type: TokenType
    value: str

type Tokenizer = Callable[[MemIter[str]], Token | None]
tokenizers: list[Tokenizer] = []
def register_tokenizer(tokenizer: Tokenizer):
    tokenizers.append(tokenizer)

string_quotes = ['"', "'", "`"]
@register_tokenizer
def tokenize_string_literal(code: MemIter[str]):
    for char in code.split():
        if not char.value in string_quotes:
            return
        char.update_parent()
        break
    string_value = ""
    for char in code.split(1):
        if char.value == "\\":
            string_value += "\\"
            next(char)
            string_value += char.value
            continue
        if char.value in string_quotes:
            char.update_parent()
            return Token(TokenType.STRING_LITERAL, string_value)
        string_value += char.value
@register_tokenizer
def tokenize_whitespace(code: MemIter[str]):
    for code in code.split():
        if re.match(r"\s", code.value):
            code.update_parent()
            return Token(TokenType.WHITESPACE, code.value)
        break

@register_tokenizer
def tokenize_operator(code: MemIter[str]):
    operator = ""
    for _, char in zip(range(operators_max_size), code.split()):
        operator += char.value
        if operator in operators:
            char.update_parent()
            return Token(TokenType.OPERATOR, operator)
@register_tokenizer
def tokenize_var_name(code: MemIter[str]):
    for char in code.split():
        if not re.match("[a-zA-Z_$]", char.value):
            return None
        char.update_parent()
        break
    var_name = ""
    for char in code.split():
        if re.match(r"[a-zA-Z0-9$\_]", char.value):
            var_name += char.value
            continue
        char.go_back_by(1)
        char.update_parent()
        return Token(TokenType.VAR_NAME, var_name)

@register_tokenizer
def tokenize_new_line(code: MemIter[str]):
    for code in code.split():
        if code.value == "\n":
            return Token(TokenType.NEW_LINE, code.value)
        break

@register_tokenizer
def tokenize_unknown(code: MemIter[str]):
    for code in code.split():
        return Token(TokenType.UNKNOWN, code.value)
def tokenize(code: str):
    for char in MemIter(iter(code)):
        print(char.value)
        for tokenizer in tokenizers:
            token = tokenizer(char)
            if token is None: continue
            yield token
            break
