from typing import Literal, NamedTuple
from collections.abc import Iterator
import re
class Token(NamedTuple):
    type: str
    token: str


def TokenizeCharacter(type: str, token: str, input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return (1, Token(type, token)) if input[current] == token else (0, None)

def TokenizeSpace(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("space", " ", input, current)

def TokenizeTab(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("tab", "\t", input, current)

def TokenizeOpenParen(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("openParen", "(", input, current)

def TokenizeCloseParen(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("closeParen", ")", input, current)

def TokenizeOpenBoxParen(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("openBoxParen", "[", input, current)

def TokenizeCloseBoxParen(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("closeBoxParen", "]", input, current)

def TokenizeOpenCurlyParen(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("openCurlyParen", "{", input, current)

def TokenizeCloseCurlyParen(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("closeCurlyParen", "}", input, current)

OPERATORS = (
    "equal",
    "plus",
    "minus",
    "star",
    "slash",
    "percent",
    "pipe",
    "exclamation",
    "dot",
    "lessThan",
    "greaterThan",
    "equalTo",
    "lessThanEqual",
    "greaterThanEqual",
    "doubleQuestion",
    "questionDot",
    "doubleAnd",
    "doublePipe",
)

OPERATOR_SYMBOLS = (
    "=",
    "and",
    "or",
    "not",
    "in",
    "is",
    "+",
    "*",
    "-",
    "/",
    "%",
    "|",
    "!",
    ".",
    "<",
    ">",
    "<=",
    ">=",
    "==",
    "??",
    "?.",
    "&&",
    "||",
)

BINARY_OPERATORS = (
    "and",
    "or",
    "in",
    "is",
    "+",
    "-",
    "*",
    "/",
    "%",
    "|",
    "!",
    ".",
    "<",
    ">",
    "<=",
    ">=",
    "==",
    "??",
    "?.",
    "&&",
    "||",
)

PRE_UNARY_OPERATORS = (
    "!",
    "not",
    "+",
    "-",
)

def TokenizeEqual(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("equal", "=", input, current)

def TokenizePlus(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("plus", "+", input, current)

def TokenizeMinus(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("minus", "-", input, current)

def TokenizeStar(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("star", "*", input, current)

def TokenizeSlash(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("slash", "/", input, current)

def TokenizeBackSlash(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("backSlash", "\\", input, current)

def TokenizePercent(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("percent", "%", input, current)

def TokenizeComma(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("comma", ",", input, current)

def TokenizeColon(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("colon", ":", input, current)

def TokenizeHash(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("hash", "#", input, current)

def TokenizePipe(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("pipe", "|", input, current)

def TokenizeExclamation(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("exclamation", "!", input, current)

def TokenizeDot(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("dot", ".", input, current)

def TokenizeLessThan(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("lessThan", "<", input, current)

def TokenizeGreaterThan(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("greaterThan", ">", input, current)

def TokenizeQuote(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("quote", "'", input, current)

def TokenizeDoubleQuote(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("doubleQuote", '"', input, current)

def TokenizeNewLine(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeCharacter("newLine", "\n", input, current)

def TokenizeMultiCharacter(type: str, token: str, input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    
    return (len(token), Token(type, token)) if input[current : current + len(token)] == token else (0, None)



def TokenizeGreaterThanEqualTo(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("greaterThanEqualTo", ">=", input, current)

def TokenizeLessThanEqualTo(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("lessThanEqualTo", "<=", input, current)

def TokenizeDoubleQuestionMark(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("doubleQuestionMark", "??", input, current)

def TokenizeQuestionDot(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("questionDot", "?.", input, current)

def TokenizeDoubleAnd(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("doubleAnd", "&&", input, current)

def TokenizeDoublePipe(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("doublePipe", "||", input, current)

def TokenizeEqualTo(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizeMultiCharacter("equalTo", "==", input, current)




def TokenizePattern(type: str, token: str, input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    match = re.search(token, input[current:])
    if match is None:
        return (0, None)
    if match.start() != 0:
        return (0, None)
    return (match.end(), Token(type, input[current : current + match.end()]))

def TokenizeNameSymbol(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizePattern("nameSymbol", "[a-zA-Z_$][a-zA-Z0-9_$]*", input, current)

def TokenizeNumber(input: str, current: int) -> tuple[0, None] | tuple[int, Token]:
    return TokenizePattern("number", "[0-9]*\\.?[0-9]+([eE][+-][0-9])?", input, current)


KEY_WORDS = (
        "as",
        "not",
        "and",
        "or",
        "if",
        "else",
        "while",
        "for",
        "return",
        "break",
        "continue",
        "true",
        "false",
        "null",
        "undefined",
        "export",
        "import",
        "from",
        "class",
        "def",
        "yield",
        "async",
        "await",
        "try",
        "catch",
        "finally",
        "throw",
        "mut",
        "with",
        )

def TokenizeKeywords(input: str, current: int) -> tuple[Literal[0], None] | tuple[int, Token]:
    for keyword in KEY_WORDS:
        if (result := TokenizeMultiCharacter("keyword", keyword, input, current))[0] > 0:
            
            symbol_result = TokenizeNameSymbol(input, current)
            return result if result[0] >= symbol_result[0] else symbol_result
    return (0, None)



TOKENiZERS = (
    TokenizeOpenParen,
    TokenizeCloseParen,
    TokenizeOpenBoxParen,
    TokenizeCloseBoxParen,
    TokenizeOpenCurlyParen,
    TokenizeCloseCurlyParen,
    TokenizeEqualTo,
    TokenizeGreaterThanEqualTo,
    TokenizeLessThanEqualTo,
    TokenizeDoubleAnd,
    TokenizeDoublePipe,
    TokenizeDoubleQuestionMark,
    TokenizeQuestionDot,
    TokenizePlus,
    TokenizeStar,
    TokenizeHash,
    TokenizePipe,
    TokenizeEqual,
    TokenizeMinus,
    TokenizeSlash,
    TokenizeComma,
    TokenizeColon,
    TokenizeQuote,
    TokenizeSpace,
    TokenizeTab,
    TokenizeNewLine,
    TokenizePercent,
    TokenizeLessThan,
    TokenizeGreaterThan,
    TokenizeBackSlash,
    TokenizeExclamation,
    TokenizeNumber,
    TokenizeDot,
    TokenizeKeywords,
    TokenizeNameSymbol,
)




def Tokenizer(input: str) -> Iterator[Token]:
    current = 0
    while current < len(input):
        isDone = False
        for tokenizer in TOKENiZERS:
            length, token = tokenizer(input, current)
            
            if length != 0 and token is not None:
                current += length
                yield token
                isDone = True
                break
        if not isDone:
            yield Token("Unknown", input[current])
            current += 1

