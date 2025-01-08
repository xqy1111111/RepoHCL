from __future__ import annotations

import os.path
import re
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


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


class SymbolNote(BaseModel):
    name: str
    description: str
    detail: str
    example: Optional[str]

    @classmethod
    def from_doc(cls, s: str) -> List[SymbolNote]:
        function_pattern = re.compile(r'(###.*?)(?=###|\Z)', re.DOTALL)
        res: List[SymbolNote] = []
        for match in function_pattern.finditer(s):
            res.append(cls.from_chapter(match.group(1)))
        return res

    @classmethod
    def from_chapter(cls, s: str):
        module_pattern = re.search(r'### (.*?)\n(.*?)\n(.*?)(?=###|\Z)', s, re.DOTALL)
        block = module_pattern.group(3)
        name = module_pattern.group(1).strip()
        description = module_pattern.group(2).strip()
        detail_match = re.search(r'\*\*Code Details\*\*(.*?)\*\*', block, re.DOTALL)
        details = detail_match.group(1).strip()
        output_example_match = re.search(r'\*\*Example\*\*(.*?)(?=\*\*|\Z)', block, re.DOTALL)
        output_example = output_example_match.group(1).strip()
        return SymbolNote(name=name, description=description,
                          example=output_example, detail=details)


class APINote(SymbolNote):
    parameters: Optional[str]

    @classmethod
    def from_chapter(cls, s: str) -> APINote:
        n = SymbolNote.from_chapter(s)
        module_pattern = re.search(r'### (.*?)\n(.*?)\n(.*?)(?=###|\Z)', s, re.DOTALL)
        block = module_pattern.group(3)
        parameter_matches = re.search(r'\*\*Parameters\*\*(.*?)\*\*', block, re.DOTALL)
        return APINote(name=n.name, description=n.description, detail=n.detail, example=n.example,
                       parameters=parameter_matches.group(1).strip() if parameter_matches else None)


class ClassNote(SymbolNote):
    attributes: Optional[str]

    @classmethod
    def from_chapter(cls, s: str) -> ClassNote:
        n: SymbolNote = SymbolNote.from_chapter(s)
        module_pattern = re.search(r'### (.*?)\n(.*?)\n(.*?)(?=###|\Z)', s, re.DOTALL)
        block = module_pattern.group(3)
        attributes_matches = re.search(r'\*\*Attributes\*\*(.*?)\*\*', block, re.DOTALL)
        return ClassNote(name=n.name, description=n.description, detail=n.detail, example=n.example,
                         attributes=attributes_matches.group(1).strip() if attributes_matches else None)


class ModuleNote(BaseModel):
    name: str = ''
    description: str = ''
    example: str = ''
    functions: str = ''

    @classmethod
    def from_doc(cls, s: str) -> List[ModuleNote]:
        chapter_pattern = re.compile(r'(###.*?)(?=###|\Z)', re.DOTALL)
        res: List[ModuleNote] = []
        for match in chapter_pattern.finditer(s):
            chapter = match.group(1)
            res.append(ModuleNote.from_chapter(chapter))
        return res

    @classmethod
    def from_chapter(cls, s: str) -> ModuleNote:
        module_pattern = re.compile(r'### (.*?)\n(.*?)\n(.*?)(?=###|\Z)', re.DOTALL)
        match = re.search(module_pattern, s)
        n = ModuleNote()
        n.name = match.group(1).strip()
        n.description = match.group(2).strip()
        content = match.group(3)
        function_match = re.search(r'\*\*Functions List\*\*(.*?)(?=\Z|\*\*)', content, re.DOTALL)
        n.functions = function_match.group(1).strip()
        example_match = re.search(r'\*\*Example\*\*(.*?)(?=\Z|\*\*)', content, re.DOTALL)
        if example_match:
            n.example = example_match.group(1).strip()
        return n

    def to_md(self) -> str:
        return '''
### {name}
{desc}

**Functions List**
{functions}
{example}
'''.format(name=self.name, desc=self.description, functions=self.functions,
           example=("\n**Example**\n" + self.example) if len(self.example) else "").strip()