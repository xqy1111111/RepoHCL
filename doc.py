from __future__ import annotations

import os.path
import re
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DocItemStatus(Enum):
    initial = 1
    finished = 2
    pre = 3


@dataclass
class DocItem(ABC):
    item_status: DocItemStatus = DocItemStatus.initial
    file: str = ''
    name: str = ''
    code: str = ''
    md_content: str = ''
    children: List[DocItem] = field(default_factory=list)
    father: DocItem = None
    reference_who: List[DocItem] = field(default_factory=list)
    who_reference_me: List[DocItem] = field(default_factory=list)

    @abstractmethod
    def doc_type(self) -> str:
        pass

    @staticmethod
    def _re_fix(s: str) -> str:
        return s.replace('(', r'\(').replace(')', r'\)').replace('[', r'\[').replace(']', r'\]').replace('*', r'\*')

    def imports(self, path: str) -> bool:
        f = f'{path}/{self.file}.{self.doc_type()}.md'
        if not os.path.exists(f):
            return False
        with open(f, 'r') as t:
            text = t.read()
            match = re.search('(### ' + self._re_fix(self.name) + r'.*?)(###|\Z)', text, re.DOTALL)
            if match:
                self.md_content = match.group(1)
        return len(self.md_content) > 0

    def exports(self, path: str):
        f = f'{path}/{self.file}.{self.doc_type()}.md'
        os.makedirs(os.path.dirname(f), exist_ok=True)
        # 追加到最后
        with open(f, 'a') as t:
            t.write(self.md_content)


@dataclass
class FunctionItem(DocItem):
    access: str = 'private'

    def doc_type(self) -> str:
        return 'function'

    # parameters: List[str] = field(default_factory=list)
    def has_return(self) -> bool:
        return 'return' in self.code

    def has_arg(self) -> bool:
        return self.file.find(' ') != -1


@dataclass
class ClassItem(DocItem):
    has_attrs: bool = False

    def doc_type(self) -> str:
        return 'class'


@dataclass
class ModuleItem(DocItem):

    def doc_type(self) -> str:
        return 'module'
