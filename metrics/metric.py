import os
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, TypeVar, Type, Optional

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

    def _save_doc(self, filename: str, doc: Doc):
        f = f'{self.doc_path}/{filename}.{doc.doc_type()}.md'
        os.makedirs(os.path.dirname(f), exist_ok=True)
        with open(f, 'a') as t:
            t.write(doc.markdown() + '\n')

    def _load_doc(self, filename: str, doc: Type[Doc]) -> List[Doc]:
        f = f'{self.doc_path}/{filename}.{doc.doc_type()}.md'
        if not os.path.exists(f):
            return []
        with open(f, 'r') as t:
            return doc.from_doc(t.read())

    def save_function_doc(self, symbol: Symbol, doc: ApiDoc):
        func_def = self.function_map.get(symbol)
        self._save_doc(func_def.filename, doc)

    def load_function_doc(self, symbol: Symbol) -> Optional[ApiDoc]:
        func_def = self.function_map.get(symbol)
        chapters = self._load_doc(func_def.filename, ApiDoc)
        for c in chapters:
            doc: ApiDoc = c
            if doc.name == symbol.base:
                return doc
        return None

    def save_clazz_doc(self, symbol: Symbol, doc: ClazzDoc):
        clazz_def = self.clazz_map.get(symbol)
        self._save_doc(clazz_def.filename, doc)

    def load_clazz_doc(self, symbol: Symbol) -> Optional[ClazzDoc]:
        clazz_def = self.clazz_map.get(symbol)
        chapters = self._load_doc(clazz_def.filename, ClazzDoc)
        for c in chapters:
            doc: ClazzDoc = c
            if doc.name == symbol.base:
                return doc
        return None

    def save_module_doc(self, doc: ModuleDoc):
        with open(f'{self.doc_path}/modules.md', 'a') as t:
            t.write(doc.markdown() + '\n')

    def load_module_docs(self) -> Optional[List[ModuleDoc]]:
        if not os.path.exists(f'{self.doc_path}/modules.md'):
            return None
        with open(f'{self.doc_path}/modules.md', 'r') as t:
            return ModuleDoc.from_doc(t.read())

    def save_repo_doc(self, doc):
        with open(f'{self.doc_path}/repo.md', 'a') as t:
            t.write(doc.markdown() + '\n')

    def load_repo_doc(self) -> Optional[RepoDoc]:
        if not os.path.exists(f'{self.doc_path}/repo.md'):
            return None
        with open(f'{self.doc_path}/repo.md', 'r') as t:
            return RepoDoc.from_chapter(t.read())


class Metric(metaclass=ABCMeta):
    @abstractmethod
    def eva(self, ctx: EvaContext):
        pass
