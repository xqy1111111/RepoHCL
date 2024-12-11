from __future__ import annotations
from enum import Enum
from typing import List, Dict
from dataclasses import dataclass, field


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
    fullname: str = ''
    code: str = ''
    md_content: List[str] = field(default_factory=list)
    children: List[DocItem] = field(default_factory=list)
    father: DocItem = None
    reference_who: List[DocItem] = field(default_factory=list)
    who_reference_me: List[DocItem] = field(default_factory=list)


@dataclass
class FunctionItem(DocItem):
    code_type = 'Function'
    parameters: List[str] = field(default_factory=list)
    has_return: bool = False


@dataclass
class ClassItem(DocItem):
    code_type = 'ClassDef'
