from enum import Enum, auto
from dataclasses import dataclass
from typing import *


class DataType(Enum):
    Int = auto()


@dataclass
class GenericType:
    ident: str

    
class OpType(Enum):
    PushInt = auto()   # (value)
    DefConst = auto()  # (name, value)
    FuncCall = auto()  # (name)
    Intrinsic = auto() # (intrinsic, ...)


class Intrinsic(Enum):
    Add = auto()
    Sub = auto()
    Mul = auto()
    Div = auto()
    Drop = auto()


@dataclass
class Op:
    type: OpType
    operand: tuple[Any, ...] = ()


STACK_MUTATIONS: dict[Intrinsic, DataType | GenericType] = {
    Intrinsic.Add: ([DataType.Int]*2, [DataType.Int]),
    Intrinsic.Sub: ([DataType.Int]*2, [DataType.Int]),
    Intrinsic.Mul: ([DataType.Int]*2, [DataType.Int]),
    Intrinsic.Div: ([DataType.Int]*2, [DataType.Int]),
    Intrinsic.Drop: ([GenericType('T')], []),
}

    
class Function:
    def __init__(self, name: str, parent, args, rets):
        self.name = name
        self.args = args
        self.rets = rets
        self.tstack = []
        self.ops = []

        self.parent = parent
        self.isfinished = False

    def add_op(self, op: Op):
        if op.type == OpType.PushInt:
            self.tstack.append(DataType.Int)
            self.ops.append(op)
        elif op.type == OpType.Intrinsic:
            intrinsic = op.operand[0]
            args, rets = STACK_MUTATIONS.get(intrinsic)
            generics:dict[str, DataType] = {}
            for arg in reversed(args):
                if isinstance(arg, GenericType):
                    if arg.name in generics.keys():
                        if self.tstack.pop() != generics[arg.name]:
                            assert False, "type error"
                    else:
                        generics[arg.name] = self.tstack.pop()
                else:
                    if self.tstack.pop() != arg:
                        assert False, "type error"

            (self.tstack.append(x) for x in rets)
            self.ops.append(op)
                

    def finish(self):
        assert len(self.tstack) == len(self.rets), "type error"
        for a, b in zip(self.tstack, self.rets):
            assert a == b, "type error"
        self.isfinished = True
    

class Program:
    def __init__(self, src: str):
        self.src = src
        self.funcs = {}

    def lookup_func(self, name: str):
        if name in self.funcs.keys():
            return self.funcs[name]

    def define_func(self, name: str, args: list, rets: list):
        assert name not in self.funcs.keys(), "redefinition of function"
        self.funcs[name] = Function(name, self, args, rets)

