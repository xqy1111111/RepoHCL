from __future__ import annotations

import json
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

    def imports(self, path: str) -> bool:
        f = f'{path}/{self.file}.md'
        if not os.path.exists(f):
            return False
        with open(f, 'r') as t:
            ok = False
            for line in t:
                # 检查是否是当前函数
                if line.startswith('### '):
                    # 当前函数已经处理完，结束处理
                    if ok:
                        return True
                    # 是当前函数
                    if line[4:].strip('* \n\r') == self.name:
                        ok = True
                        continue
                    ok = False
                if ok:
                    self.md_content += line
        return len(self.md_content) > 0

    def exports(self, path: str):
        f = f'{path}/{self.file}.md'
        os.makedirs(os.path.dirname(f), exist_ok=True)
        # 追加到最后
        with open(f, 'a') as t:
            t.write(self.md_content)

@dataclass
class FunctionItem(DocItem):
    code_type = 'Function'

    # parameters: List[str] = field(default_factory=list)
    def has_return(self) -> bool:
        return 'return' in self.code

    def has_arg(self) -> bool:
        return self.file.find(' ') != -1


@dataclass
class ClassItem(DocItem):
    code_type = 'ClassDef'
