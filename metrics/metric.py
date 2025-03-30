import os
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, TypeVar, Optional, Type

import networkx as nx

from .doc import ApiDoc, ClazzDoc, ModuleDoc, Doc, RepoDoc


# 函数、类的唯一标识符
@dataclass
class Symbol:
    # 去除*/&等符号后的基础类型
    base: str
    # 原始类型
    literal: str

    def __init__(self, base: str, literal: str = None):
        self.base = base
        if literal is None:
            literal = base
        self.literal = literal

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return self.base == other.base

    def __hash__(self):
        return hash(self.base)


@dataclass
class FieldDef:
    name: str
    # 终态类型
    symbol: Symbol
    access: str


@dataclass
class FuncDef:
    symbol: Symbol
    # 函数可见性，仅在C/C++中存在
    visible: bool = True
    # 访问权限，public/protected/private
    access: str = 'private'
    code: str = ''
    params: List[FieldDef] = field(default_factory=list)
    filename: str = ''
    beginLine: int = 0
    endLine: int = 0
    declFile: str = ''
    # return_type: FieldDef


@dataclass
class ClazzDef:
    symbol: Symbol
    fields: List[FieldDef]
    functions: List[FuncDef]
    filename: str = ''
    beginLine: int = 0
    endLine: int = 0

    @property
    def code(self) -> str:
        def make_code(access: str) -> str:
            filter_fields = list(filter(lambda x: x.access == access, self.fields))
            filter_functions = list(filter(lambda x: x.access == access, self.functions))
            if len(filter_fields) == 0 and len(filter_functions) == 0:
                return ''
            s = f'{access}:\n'
            for f in filter_fields:
                s += f'  {f.symbol.literal} {f.name};\n'
            if len(filter_fields) > 0:
                s += '\n'
            for f in filter_functions:
                s += f'  {f.symbol.base};\n'
            return s

        code = 'class ' + self.symbol.base + ' {\n'
        code += make_code('public')
        code += make_code('protected')
        code += make_code('private')
        code += '};'
        return code


T = TypeVar('T', bound=Doc)


@dataclass
class EvaContext:
    doc_path: str
    resource_path: str
    output_path: str
    clazz_map: Dict[Symbol, ClazzDef] = None
    function_map: Dict[Symbol, FuncDef] = None
    callgraph: nx.DiGraph = None
    clazz_callgraph: nx.DiGraph = None
    structure: str = None

    @staticmethod
    def save_doc(filename: str, doc: Doc):
        _dir = os.path.dirname(filename)
        if _dir:
            os.makedirs(_dir, exist_ok=True)
        with open(filename, 'a') as t:
            t.write(doc.markdown() + '\n')

    @staticmethod
    def load_docs(filename: str, doc_type: Type[Doc]) -> List[T]:
        if not os.path.exists(filename):
            return []
        with open(filename, 'r') as t:
            docs = doc_type.from_doc(t.read())
            return docs

    @staticmethod
    def load_doc(symbol: Symbol, filename: str, doc: Type[Doc]) -> Optional[Doc]:
        docs = EvaContext.load_docs(filename, doc)
        for d in docs:
            if d.name == symbol.base:
                return d
        return None

    def save_function_doc(self, symbol: Symbol, doc: ApiDoc):
        func_def = self.function_map.get(symbol)
        self.save_doc(f'{self.doc_path}/{func_def.filename}.{ApiDoc.doc_type()}.md', doc)

    def load_function_doc(self, symbol: Symbol) -> Optional[ApiDoc]:
        func_def = self.function_map.get(symbol)
        return self.load_doc(symbol, f'{self.doc_path}/{func_def.filename}.{ApiDoc.doc_type()}.md', ApiDoc)

    def save_clazz_doc(self, symbol: Symbol, doc: ClazzDoc):
        clazz_def = self.clazz_map.get(symbol)
        self.save_doc(f'{self.doc_path}/{clazz_def.filename}.{ClazzDoc.doc_type()}.md', doc)

    def load_clazz_doc(self, symbol: Symbol) -> Optional[ClazzDoc]:
        clazz_def = self.clazz_map.get(symbol)
        return self.load_doc(symbol, f'{self.doc_path}/{clazz_def.filename}.{ClazzDoc.doc_type()}.md', ClazzDoc)

    def save_module_doc(self, doc: ModuleDoc):
        self.save_doc(f'{self.doc_path}/modules.md', doc)

    def load_module_docs(self) -> List[ModuleDoc]:
        return self.load_docs(f'{self.doc_path}/modules.md', ModuleDoc)

    def save_repo_doc(self, doc):
        self.save_doc(f'{self.doc_path}/repo.md', doc)

    def load_repo_doc(self) -> Optional[RepoDoc]:
        docs = self.load_docs(f'{self.doc_path}/repo.md', RepoDoc)
        if len(docs) == 0:
            return None
        return docs[0]


class Metric(metaclass=ABCMeta):
    @abstractmethod
    def eva(self, ctx: EvaContext):
        pass
