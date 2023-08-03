from __future__ import annotations
from _typeshed import Self
from .tokenizer import BINARY_OPERATORS, OPERATORS, PRE_UNARY_OPERATORS, Token
from abc import ABC, abstractmethod

class SyntaxError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TokenTypeMismatch(Exception):
    def __init__(self, expectedTypes: tuple[str, ...], input: Token) -> None:
        super().__init__(f"Expected one of {', '.join(expectedTypes)} Token type, but got {input.type}")
        self.expected_types = expectedTypes
        self.input = input

class TokenMismatch(Exception):
    def __init__(self, expectedTokens: tuple[str, ...], input: Token) -> None:
        super().__init__(f"Expected one of {', '.join(expectedTokens)} toeken, but got {input.token}")
        self.expected_tokens = expectedTokens
        self.input = input


class Node(ABC):
    type: str
    children: list['Node']
    def __init__(self):
        self.children = []
    @abstractmethod
    def __str__(self) -> str:
        ...

class Expression(Node):
    children: list['Expression']



class Identifier(Expression):
    type = "identifier"
    def __init__(self, *, nameSymbol: Token):
        super().__init__()
        if nameSymbol.type != "nameSymbol":
            raise TokenTypeMismatch(("nameSymbol",), nameSymbol)
        self.name = nameSymbol.token
    def __str__(self) -> str:
        return self.name


class Operator(Node):
    type = "operator"
    opetator: str
    text: str
    def __init__(self, *, operator: Token):
        super().__init__()
        if operator.type not in OPERATORS and operator.type != "keyword":
            raise TokenTypeMismatch((*OPERATORS, "keywords"), operator)
        if operator.type == "keyword" and operator.token not in ("and", "or", "not", "in"):
            raise TokenMismatch(("and", "or", "not", "in"), operator)
        self.opetator = operator.type
        self.text = operator.token

    def __str__(self) -> str:
        return self.text

class Path(Node):
    type = "path"
    def __init__(self, *, path: tuple[Identifier | Operator, ...]):
        super().__init__()
        for token in path:
            if isinstance(token, Operator) and token.text != ".":
                raise TokenMismatch((".",), Token(token.type, token.text))
            self.children.append(token)

    def __str__(self) -> str:
        return "".join(str(child) for child in self.children)
        


class Import(Node):
    type = "import"
    children: tuple[Path, Identifier | None]
    def __init__(self, *, path: Path, alias: Identifier | None = None):
        super().__init__()
        self.children = (path, alias)


    @property
    def path(self) -> Path:
        return self.children[0]
    @property
    def alias(self) -> Identifier | None:
        return self.children[1]


    def __str__(self) -> str:
        return f"import {' as '.join(str(child) for child in self.children if child is not None)}"


class ImportListItem(Node):
    type = "importListItem"
    children: tuple[Identifier, Identifier | None]

    def __init__(self, *, name: Identifier, alias: Identifier | None = None):
        super().__init__()
        self.children = (name, alias)
    
    @property
    def name(self) -> Identifier:
        return self.children[0]
    @property
    def alias(self) -> Identifier | None:
        return self.children[1]

    def __str__(self) -> str:
        return f"{' as '.join(str(child) for child in self.children if child is not None)}"

class ImportList(Node):
    type = "importList"
    children: list[ImportListItem]
    def __init__(self, *, imports: list[ImportListItem]):
        super().__init__()
        self.children = imports

    @property
    def imports(self) -> list[ImportListItem]:
        return self.children

    def __str__(self) -> str:
        return ", ".join(str(child) for child in self.children)

class FromImport(Node):
    type = "fromImport"
    children: tuple[Path, ImportList]
    def __init__(self, *, path: Path, imports: ImportList):
        super().__init__()
        self.children = (path, imports)
    
    @property
    def path(self) -> Path:
        return self.children[0]
    @property
    def imports(self) -> ImportList:
        return self.children[1]

    def __str__(self) -> str:
        return f"from {self.path} import {self.imports}"

class Number(Expression):
    type = "number"
    text: str
    def __init__(self, *, token: Token):
        super().__init__()
        if token.type != "number":
            raise TokenTypeMismatch(("number",), token)
        self.text = token.token

    def __str__(self) -> str:
        return self.text

class Bool(Expression):
    type = "bool"
    text: str
    def __init__(self, *, token: Token):
        super().__init__()
        if token.type != "keyword":
            raise TokenTypeMismatch(("keyword",), token)
        if token.token not in ("true", "false"):
            raise TokenMismatch(("true", "false"), token)
        self.text = token.token

    def __str__(self) -> str:
        return self.text
class String(Expression):
    type = "string"
    text: str
    def __init__(self, *, tokens: list[Token]):
        super().__init__()
        self.text = "".join(token.token for token in tokens)

    def __str__(self) -> str:
        return f'"{self.text}"'



class TemplateStringStart(Node):
    type = "templateStringStart"
    text: str
    def __init__(self, *, tokens: list[Token]):
        super().__init__()
        self.text = "".join(token.token for token in tokens)

    def __str__(self) -> str:
        return f'"{self.text}{"{"}'


class TemplateStringMiddlePart(Node):
    type = "templateStringMiddlePart"
    text: str
    def __init__(self, *, tokens: list[Token]):
        super().__init__()
        self.text = "".join(token.token for token in tokens)
    def __str__(self) -> str:
        return f'{"}"}{self.text}{"{"}'

class TemplateStringMiddleWithExpression(Node):
    type = "templateStringMiddleWithExpression"
    children: tuple[Expression, TemplateStringMiddlePart]
    def __init__(self, *, expressionPart: Expression, stringPart: TemplateStringMiddlePart): 
        super().__init__()
        self.children = (expressionPart, stringPart)

    @property
    def expressionPart(self) -> Expression:
        return self.children[0]
    @property
    def stringPart(self) -> TemplateStringMiddlePart:
        return self.children[1]

    def __str__(self) -> str:
        return "".join(str(child) for child in self.children)

class TemplateStringMiddle(Node):
    type = "templateStringMiddle"
    children: tuple[TemplateStringMiddleWithExpression, ...]
    def __init__(self, *, parts: tuple[TemplateStringMiddleWithExpression, ...]): 
        super().__init__()
        self.children = parts

    def __str__(self) -> str:
        return "".join(str(child) for child in self.children)


class TemplateStringEndStringPart(Node):
    type = "templateStringEnd"
    text: str
    def __init__(self, *, tokens: list[Token]):
        super().__init__()
        self.text = "".join(token.token for token in tokens)
    def __str__(self) -> str:
        return f'{"}"}{self.text}"'

class TemplateStringEnd(Node):
    type = "templateStringEnd"
    children: tuple[Expression, TemplateStringEndStringPart]
    def __init__(self, *, expressionPart: Expression, stringPart: TemplateStringEndStringPart): 
        super().__init__()
        self.children = (expressionPart, stringPart)

    @property
    def expressionPart(self) -> Expression:
        return self.children[0]
    @property
    def stringPart(self) -> TemplateStringEndStringPart:
        return self.children[1]

    def __str__(self) -> str:
        return "".join(str(child) for child in self.children)


class TemplateString(Expression):
    type = "TemplateString"
    children: tuple[TemplateStringStart, TemplateStringMiddle, TemplateStringEnd]
    def __init__(self, *, start: TemplateStringStart, middle: TemplateStringMiddle, end: TemplateStringEnd):
        super().__init__()
        self.children = (start, middle, end)

    @property
    def start(self) -> TemplateStringStart:
        return self.children[0]
    @property
    def middle(self) -> TemplateStringMiddle:
        return self.children[1]
    @property
    def end(self) -> TemplateStringEnd:
        return self.children[2]

    def __str__(self) -> str:
        return "".join(str(child) for child in self.children)

class List(Expression):
    type = "list"
    children: list[Expression]
    def __init__(self, *, expressions: list[Expression]):
        super().__init__()
        self.children = expressions

    def __str__(self) -> str:
        return f"[{', '.join(str(child) for child in self.children)}]"

class Tuple(Expression):
    type = "tuple"
    children: tuple[Expression]
    def __init__(self, *, expressions: tuple[Expression]):
        super().__init__()
        self.children = expressions

    def __str__(self) -> str:
        return f"({', '.join(str(child) for child in self.children)})"


class DictItem(Node):
    type = "dictItem"
    children: tuple[Expression, Expression]
    def __init__(self, *, key: Expression, value: Expression):
        super().__init__()
        self.children = (key, value)

    @property
    def key(self) -> Expression:
        return self.children[0]
    @property
    def value(self) -> Expression:
        return self.children[1]

    def __str__(self) -> str:
        return f"{self.key}: {self.value}"

class Dict(Expression):
    type = "dict"
    children: list[DictItem]
    def __init__(self, *, items: list[DictItem]):
        super().__init__()
        self.children = items

    def __str__(self) -> str:
        return f"{'{'} {', '.join(str(child) for child in self.children)} {'}'}"

class DictTuple(Expression):
    type = "dictTuple"
    children: list[DictItem]
    def __init__(self, *, items: list[DictItem]):
        super().__init__()
        self.children = items

    def __str__(self) -> str:
        return f"( {', '.join(str(child) for child in self.children)} )"


class BinaryOperationExpression(Expression):
    type = "binaryOperationExpression"
    children: tuple[Expression, Operator, Expression]
    def __init__(self, *, left: Expression, operator: Operator, right: Expression):
        super().__init__()
        if operator.text not in BINARY_OPERATORS:
            raise TokenMismatch(BINARY_OPERATORS, Token("operator", operator.text))
        self.children = (left, operator, right)

    @property
    def left(self) -> Expression:
        return self.children[0]
    @property
    def operator(self) -> Operator:
        return self.children[1]
    @property
    def right(self) -> Expression:
        return self.children[2]

    def __str__(self) -> str:
        return f"{self.left} {self.operator} {self.right}"


class PreUnaryOperation(Expression):
    type = "preUnaryOperation"
    children: tuple[Operator, Expression]
    def __init__(self, *, operator: Operator, right: Expression):
        super().__init__()
        if operator.text not in PRE_UNARY_OPERATORS:
            raise TokenMismatch(PRE_UNARY_OPERATORS, Token("operator", operator.text))
        self.children = (operator, right)

    @property
    def operator(self) -> Operator:
        return self.children[0]
    @property
    def right(self) -> Expression:
        return self.children[1]

    def __str__(self) -> str:
        return f"{self.operator}{self.right}"

class PostUnaryOperation(Expression):
    type = "postUnaryOperation"
    children: tuple[Expression, Operator]
    def __init__(self, *, operator: Operator, left: Expression):
        if operator.text not in PRE_UNARY_OPERATORS:
            raise TokenMismatch(PRE_UNARY_OPERATORS, Token("operator", operator.text))
        self.children = (left, operator)

    @property
    def operator(self) -> Operator:
        return self.children[1]
    @property
    def left(self) -> Expression:
        return self.children[0]

    def __str__(self) -> str:
        return f"{self.left}{self.operator}"

class AttrAccess(Expression):
    type = "attrAccess"
    children: tuple[Expression, Expression]
    def __init__(self, *, expression: Expression, attr: Expression):
        super().__init__()
        self.children = (expression, attr)

    @property
    def expression(self) -> Expression:
        return self.children[0]
    @property
    def attr(self) -> Expression:
        return self.children[1]
    def __str__(self) -> str:
        return f"{self.expression}[{self.attr}]"

class AttributeAccess(Expression):
    type = "attributeAccess"
    children: tuple[Expression, Identifier]
    def __init__(self, *, expression: Expression, attribute: Identifier):
        super().__init__()
        self.children = (expression, attribute)

    @property
    def expression(self) -> Expression:
        return self.children[0]
    @property
    def attribute(self) -> Identifier:
        return self.children[1]

    def __str__(self) -> str:
        return f"{self.expression}.{self.attribute}"

class KWArgsItem(Node):
    type = "kwArgsItem"
    children: tuple[Identifier, Expression]
    def __init__(self, *, key: Identifier, value: Expression):
        super().__init__()
        self.children = (key, value)
    
    @property
    def key(self) -> Identifier:
        return self.children[0]
    @property
    def value(self) -> Expression:
        return self.children[1]

    def __str__(self) -> str:
        return f"{self.key}={self.value}"

class KWArgs(Node):
    type = "kwArgs"
    children: list[KWArgsItem]
    def __init__(self, *, items: list[KWArgsItem]):
        super().__init__()
        self.children = items

    def __len__(self) -> int:
        return len(self.children)
    def __str__(self) -> str:
        return ", ".join(str(child) for child in self.children)

class Call(Expression):
    type = "call"
    children: tuple[Expression, tuple[Expression, ...], KWArgs]
    def __init__(self, *, expression: Expression, args: tuple[Expression, ...], kwargs: KWArgs):
        super().__init__()
        self.children = (expression, args, kwargs)

    @property
    def expression(self) -> Expression:
        return self.children[0]
    @property
    def args(self) -> tuple[Expression, ...]:
        return self.children[1]
    @property
    def kwargs(self) -> KWArgs:
        return self.children[2]

    def __str__(self) -> str:
        if len(self.kwargs) == 0:
            return f"{self.expression}({', '.join(str(arg) for arg in self.args)})"
        return f"{self.expression}({', '.join(str(arg) for arg in self.args)}, {self.kwargs})"

class TypeAnnotation(Node):
    type = "typeAnnotation"
    children: tuple[Identifier | TypeAnnotation | Number | Bool | String]
    def __init__(self, *, name: Identifier | TypeAnnotation):
        super().__init__()
        self.children = (name,)

    @property
    def name(self) -> Identifier | TypeAnnotation | Number | Bool | String:
        return self.children[0]

    def __str__(self) -> str:
        return f"{self.name}"

class UnionTypeAnnotation(TypeAnnotation):
    type = "unionTypeAnnotation"
    children: tuple[TypeAnnotation, TypeAnnotation]
    def __init__(self, *, left: TypeAnnotation, right: TypeAnnotation):
        super().__init__(name=left)
        self.children = (left, right)

    @property
    def left(self) -> TypeAnnotation:
        return self.children[0]
    @property
    def right(self) -> TypeAnnotation:
        return self.children[1]

    def __str__(self) -> str:
        return f"{self.left} | {self.right}"

class GenericTypeAnnotation(TypeAnnotation):
    type = "genericTypeAnnotation"
    children: tuple[TypeAnnotation, ...]
    def __init__(self, *, name: TypeAnnotation, args: tuple[TypeAnnotation, ...]):
        super().__init__(name=name)
        self.children = (name, *args)

    @property
    def name(self) -> TypeAnnotation:
        return self.children[0]
    @property
    def args(self) -> tuple[TypeAnnotation, ...]:
        return self.children[1:]

    def __str__(self) -> str:
        return f"{self.name}[{', '.join(str(arg) for arg in self.args)}]"

class ParameterListItem(Node):
    type = "parameterListItem"
    children: tuple[Identifier, TypeAnnotation | None, Expression | None]
    def __init__(self, *, name: Identifier, anotation: TypeAnnotation | None, default: Expression | None):
        super().__init__()
        if default is None and annotations is None:
            raise SyntaxError("annotations must be provided if default is not defined")
        self.children = (name, anotation, default)
    @property
    def name(self) -> Identifier:
        return self.children[0]
    @property
    def anotation(self) -> TypeAnnotation | None:
        return self.children[1]
    @property
    def default (self) -> Expression | None:
        return self.children[2]

    def __str__(self) -> str:
        if self.default is None:
            return f"{self.name}"
        return f"{self.name}={self.default}"

class ParameterList(Node):
    type = "parameterList"
    children: tuple[list[ParameterListItem] | None, list[ParameterListItem] | None, list[ParameterListItem] | None]
    def __init__(self, *,
        pos_only_params: list[ParameterListItem] | None,
        params: list[ParameterListItem] | None,
        kw_only_param: list[ParameterListItem] | None,
    ):
        super().__init__()
        self.children = (pos_only_params, params, kw_only_param)
    
    @property
    def pos_only_params(self) -> list[ParameterListItem] | None:
        return self.children[0]
    @property
    def params(self) -> list[ParameterListItem] | None:
        return self.children[1]
    @property
    def kw_only_param(self) -> list[ParameterListItem] | None:
        return self.children[2]
    def __len__(self) -> int:
        length = 0
        if self.pos_only_params is not None:
            length += len(self.pos_only_params)
        if self.params is not None:
            length += len(self.params)
        if self.kw_only_param is not None:
            length += len(self.kw_only_param)
        return length

    def __str__(self) -> str:
        params_list_str = ""
        if self.pos_only_params is not None:
            params_list_str += ", ".join(str(param) for param in self.pos_only_params)
        if self.params is not None:
            params_list_str += ", ".join(str(param) for param in self.params)
        if self.kw_only_param is not None:
            params_list_str += ", ".join(str(param) for param in self.kw_only_param)
        return params_list_str
class Lambda(Expression):
    type = "lambda"
    children: tuple[ParameterList, TypeAnnotation | None, Expression]
    def __init__(self, *, params: ParameterList, returnAnnotation: TypeAnnotation | None, returns: Expression):
        super().__init__()
        self.children = (params, returnAnnotation, returns)

    @property
    def params(self) -> ParameterList:
        return self.children[0]
    @property
    def returnAnnotation(self) -> TypeAnnotation | None:
        return self.children[1]
    @property
    def returns(self) -> Expression:
        return self.children[2]

    def __str__(self) -> str:
        if self.returnAnnotation is None:
            return f"lambda ({self.params}): {self.returns}"
        return f"lambda ({self.params}) -> {self.returnAnnotation}: {self.returns}"

class Statement(Node):
    type = "statement"

class Block(Node):
    type = "block"
    children: list[Statement]
    def __init__(self, *, statements: list[Statement]):
        super().__init__()
        self.children = statements

    def __str__(self) -> str:
        return "\n".join(str(child) for child in self.children)

class ExpressionStatement(Statement):
    type = "expressionStatement"
    children: tuple[Expression]
    def __init__(self, *, expression: Expression):
        super().__init__()
        self.children = (expression, )

    @property
    def expression(self) -> Expression:
        return self.children[0]

    def __str__(self) -> str:
        return f"{self.expression}"

class InnitialisationStateMent(Statement):
    type = "initialisationStateMent"
    children: tuple[Key]
    def __init__(self, *, expression: Expression):
        super().__init__()
        self.children = (expression, )

    @property
    def expression(self) -> Expression:
        return self.children[0]

    def __str__(self) -> str:
        return f"{self.expression}"
