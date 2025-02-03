from __future__ import annotations
from dataclasses import dataclass, field
from collections import OrderedDict
from itertools import islice
from typing import ClassVar

from .tokenizer import Token, TokenType, tokenize
from ..utils.mem_iter import MemIter
from ..utils.var_map import VarMap



@dataclass(slots=True)
class DataType:
    name: ClassVar[str] = ""
    c_name: ClassVar[str] = ""
    def __hash__(self):
        return hash(self.name)
    def final_type(self) -> DataType:
        return self

@dataclass(slots=True)
class Infer(DataType):
    name = "infer"
    c_name = ""
    infered_type: DataType | None = None
    def __eq__(self, other: object):
        if not isinstance(other, DataType): return False
        self.infered_type = other
        return True
    def final_type(self):
        if self.infered_type is None:
            raise TypeError("No type was infered")
        return self.infered_type

@dataclass(slots=True)
class Str(DataType):
    name = "str"
    c_name = "char[]"
@dataclass(slots=True)
class Void(DataType):
    name = "void"
    c_name = "void"
    
@dataclass(slots=True)
class Function(DataType):
    c_fn_name: str = field(default="c_fn")
    args: OrderedDict[str, VariableData] = field(default_factory=OrderedDict)
    return_type: DataType = field(default_factory=Void)
    @property
    def name(self): #type: ignore
        return f"({", ".join([f"{self.args[arg].symbol}: {self.args[arg].data_type.name}" for arg in self.args])}) -> {self.return_type}"
    @property
    def c_name(self): #type: ignore
        return f"{self.return_type} (*{self.c_fn_name})({", ".join([self.args[arg].data_type.c_name for arg in self.args])})"



    
@dataclass(slots=True)
class VariableData:
    symbol: str
    data_type: DataType = field(hash=False)

@dataclass(slots=True)
class AstContext:
    nonlocal_vars: dict[str, VariableData] = field(default_factory=dict)
    local_vars: dict[str, VariableData] = field(default_factory=dict)
    whitespace: int = 0
    module_name: str = "main"

std_globals: dict = {
    "printf": VariableData(
        symbol="printf",
        data_type=Function(
            args=OrderedDict([(
                "message",
                VariableData(symbol="message", data_type=Str())
            )]),
            c_fn_name="printf_t"
        )
    )

}


@dataclass(slots=True)
class Node:
    children: list[Node] = field(default_factory=list)
    vars_in_scope: list[VariableData] = field(default_factory=list)
    def compile(self, indent: int = 0) -> str:
        raise NotImplementedError

@dataclass
class Statement(Node):
    data_type: DataType = field(default_factory=Infer)
    standalone_subclasses: ClassVar[list[type[Statement]]] = []
    def __init_subclass__(cls, standalone = False):
        if standalone:
            cls.standalone_subclasses.append(cls)


    @classmethod
    def parse(cls, tokens: MemIter[Token], context: AstContext = AstContext()):
        for sub_class in cls.standalone_subclasses:
            result = sub_class.parse(tokens, context)
            if result is None: continue
            return result

@dataclass
class Block(Node):
    @classmethod
    def parse(cls, tokens: MemIter[Token], context: AstContext = AstContext()):
        self = cls()
        for token in tokens:
            curr_whitespace = 0
            no_statement = False
            if token.value.value == ")":
                return
            for tok in token.split():
                if tok.value.type == TokenType.NEW_LINE:
                    no_statement = True
                    tok.update_parent()
                    break
                if tok.value.type != TokenType.WHITESPACE:
                    tok.go_back_by(1)
                    tok.update_parent()
                    break
                curr_whitespace += 1
            if no_statement: continue
            if context.whitespace != curr_whitespace:
                return
            statement = Statement.parse(token, context)
            if statement is not None:
                token.update_parent()
                self.children.append(statement)
                continue
            for tok in token.split():
                if tok.value.type == TokenType.NEW_LINE:
                    tok.update_parent()
                    break
                if tok.value.type != TokenType.WHITESPACE:
                    return
        return self
    def compile(self, indent: int = 0):
        indent += 4
        code = ""
        for child in self.children:
            code += " " * indent
            code += child.compile(indent)
            code += ";\n"
        return code



@dataclass
class Root(Block):
    @classmethod
    def parse(cls, tokens: MemIter[Token], context = AstContext()):
        if context.module_name == "main":
            context.nonlocal_vars = std_globals
        return super().parse(tokens, context)
    def compile(self, indent: int = 0):
        code = """typedef char* str;\n
int main() {\n"""
        code += super().compile(indent)
        code += """return 0;
}\n"""
        return code

class Assignment(Statement, standalone = True):
    @classmethod
    def parse(cls, tokens: MemIter[Token], context = AstContext()):
        for tokens in tokens.split():
            assignee = Assignee.parse(tokens, context)
            if assignee is None: return
            operator: Token | None = None
            for token in tokens.split(1):
                if token.value.type == TokenType.OPERATOR and token.value.value == "=":
                    token.update_parent()
                    operator = token.value
                    break
                if token.value.type != TokenType.WHITESPACE: break
            if operator is None: return
            for token in tokens.split(1):
                if token.value.type == TokenType.WHITESPACE: continue
                token.go_back_by(1)
                token.update_parent()
                break
            assigner = ValueStatement.parse(tokens, context)
            if assigner is None: return
            if assignee.variable.data_type != assigner.data_type: return
            assignee.variable.data_type = assignee.variable.data_type.final_type()
            if assignee.variable.symbol not in context.local_vars:
                context.local_vars[assignee.variable.symbol] = assignee.variable
            tokens.update_parent()
            return cls([assignee, assigner])
    @property
    def assignee(self):
        return self.children[0]
    @property
    def assigner(self):
        return self.children[1]
    def compile(self, indent: int = 0):
        return f"{self.assignee.compile()} = {self.assigner.compile()}"
    



@dataclass
class Assignee(Node):
    variable: VariableData = field(kw_only=True)
    token: Token = field(kw_only=True)
    is_declaration: bool = False
    @classmethod
    def parse(cls, tokens: MemIter[Token], context = AstContext()):
        for token in tokens.split():
            if token.value.type == TokenType.VAR_NAME:
                symbol = token.value.value
                is_declaration = symbol not in context.local_vars
                variable_data = VariableData(symbol=symbol, data_type=Infer())
                if not is_declaration:
                    variable_data = context.local_vars[symbol]
                token.update_parent()
                return cls(token=tokens.value, variable=variable_data, is_declaration=is_declaration)
            return None
    def compile(self, indent: int = 0) -> str:
        result = ""
        if self.is_declaration:

            result += self.variable.data_type.c_name
            result += " "
        result += self.variable.symbol
        return result
@dataclass
class ValueStatement(Statement, standalone = True):
    sub_classes: ClassVar[list[type[ValueStatement]]] = []

    def __init_subclass__(cls) -> None:
        cls.sub_classes.append(cls)
        return super().__init_subclass__()

    @classmethod
    def parse(cls, tokens: MemIter[Token], context = AstContext()) -> ValueStatement | None:
        for sub_class in cls.sub_classes:
            result = sub_class.parse(tokens, context)
            if result is None: continue
            return result

@dataclass
class StringLiteral(ValueStatement):
    data_type: DataType = field(default_factory=Str)
    token: Token = field(kw_only=True)

    @classmethod
    def parse(cls, tokens: MemIter[Token], context = AstContext()):
        for token in tokens.split():
            if token.value.type == TokenType.STRING_LITERAL:
                token.update_parent()
                return cls(token=token.value)
            return

    def compile(self, indent: int = 0) -> str:
        return f'"{self.token.value}"'

@dataclass
class CallStatement(ValueStatement):
    function: VariableData = field(kw_only=True) 
    args: OrderedDict = field(default_factory=OrderedDict)
    @classmethod
    def parse(cls, tokens: MemIter[Token], context = AstContext()):
        for token in tokens.split():
            if token.value.type != TokenType.VAR_NAME:
                return
            symbol = token.value.value
            variable = context.local_vars.get(symbol, context.nonlocal_vars.get(symbol))
            if variable is None:
                return
            if not isinstance(variable.data_type, Function):
                return
            arguments = variable.data_type.args
            args = OrderedDict.fromkeys(arguments.keys())
            for tok in token.split(1):
                if tok.value.type == TokenType.WHITESPACE: continue
                if tok.value.value == "(":
                    tok.update_parent()
                    break
                return
            i = 0
            for tok in token.split(1):
                if tok.value.type == TokenType.WHITESPACE: continue
                arg = Statement.parse(tok, context)
                if arg is None:
                    return
                arg_var = next(islice(arguments.items(), i, None))[1]
                if arg_var.data_type != arg.data_type:
                    return
                args[arg_var.symbol] = arg
                for t in tok.split(1):
                    if t.value.type == TokenType.WHITESPACE: continue
                    if t.value.value == ",":
                        i += 1
                        t.update_parent()
                        break
                    if t.value.value == ")":
                        t.update_parent()
                        tok.update_parent()
                        token.update_parent()
                        return CallStatement(function=variable, args=args)
    def compile(self, indent: int = 0):
        return f"{self.function.symbol}({', '.join([arg.compile(indent) for arg in self.args.values()])})"





def parse(source: str) -> Root | None:
    tokens = MemIter(tokenize(source))
    return Root.parse(tokens)
