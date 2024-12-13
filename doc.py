from __future__ import annotations

import os.path
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DocItemStatus(Enum):
    initial = 1
    finished = 2
    pre = 3


@dataclass
class DocItem:
    item_status: DocItemStatus = DocItemStatus.initial
    code_type = ''
    file: str = ''
    name: str = ''
    code: str = ''
    md_content: str = ''
    children: List[DocItem] = field(default_factory=list)
    father: DocItem = None
    reference_who: List[DocItem] = field(default_factory=list)
    who_reference_me: List[DocItem] = field(default_factory=list)

    def imports(self, path: str):
        f = f'{path}/{self.file}/{self.name}.md'
        if not os.path.exists(f):
            return False
        with open(f, 'r') as t:
            self.md_content = t.read()
        return True

    def exports(self, path: str):
        p = f'{path}/{self.file}'
        f = f'{p}/{self.name}.md'
        if os.path.exists(f):
            return
        if not os.path.exists(p):
            os.makedirs(path)
        with open(f, 'w') as t:
            t.write(self.md_content)


@dataclass
class FunctionItem(DocItem):
    code_type = 'Function'
    parameters: List[str] = field(default_factory=list)
    has_return: bool = False


@dataclass
class ClassItem(DocItem):
    code_type = 'ClassDef'
