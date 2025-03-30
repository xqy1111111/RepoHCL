from __future__ import annotations

import re
from abc import abstractmethod, ABC
from typing import List, Optional

from pydantic import BaseModel, field_serializer


class Doc(ABC, BaseModel):
    name: str
    description: str

    @classmethod
    def from_doc(cls, s: str) -> List[Doc]:
        function_pattern = re.compile(r'(###.*?)(?=\n### |\Z)', re.DOTALL)
        res: List[Doc] = []
        for match in function_pattern.finditer(s):
            res.append(cls.from_chapter(match.group(1)))
        return res

    @classmethod
    def from_chapter(cls, s: str):
        module_pattern = re.search(r'### (.*?)\n(.*?)(?=\n### |\Z)', s, re.DOTALL)
        name = module_pattern.group(1).strip()
        block = module_pattern.group(2)
        return cls.from_chapter_hook(cls(name=name, description=cls.from_block(block, 'Description')), block)

    @classmethod
    @abstractmethod
    def from_chapter_hook(cls, doc, block: str):
        pass

    @classmethod
    def from_block(cls, block: str, header: str) -> Optional[str]:
        match = re.search(f'#### {header}'+r'(.*?)(?=####|\Z)', block, re.DOTALL)
        content = match.group(1).strip() if match else None
        return content

    def markdown(self) -> str:
        md = f'### {self.name}\n#### Description\n{self.description}\n\n'
        return md + self._markdown_hook()

    @abstractmethod
    def _markdown_hook(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def doc_type(cls) -> str:
        pass


class ApiDoc(Doc):
    detail: Optional[str] = None
    example: Optional[str] = None
    parameters: Optional[str] = None
    code: Optional[str] = None

    @classmethod
    def from_chapter_hook(cls, doc: ApiDoc, block: str) -> ApiDoc:
        doc.detail = cls.from_block(block, 'Code Details')
        doc.example = cls.from_block(block, 'Example')
        doc.parameters = cls.from_block(block, 'Parameters')
        doc.code = cls.from_block(block, 'Source Code')
        return doc

    def _markdown_hook(self) -> str:
        md = ''
        if self.parameters is not None:
            md += f'#### Parameters\n{self.parameters}\n\n'
        if self.detail is not None:
            md += '#### Code Details\n{details}\n\n'.format(details=self.detail)
        if self.example is not None:
            md += f'#### Example\n{self.example}\n\n'
        if self.code is not None:
            md += f'#### Source Code\n{self.code}\n\n'
        return md.strip()

    @classmethod
    def doc_type(cls) -> str:
        return 'function'


class ClazzDoc(Doc):
    detail: Optional[str] = None
    attributes: Optional[str] = None

    @classmethod
    def from_chapter_hook(cls, doc: ClazzDoc, block: str) -> ClazzDoc:
        doc.detail = cls.from_block(block, 'Code Details')
        doc.attributes = cls.from_block(block, 'Attributes')
        return doc

    def _markdown_hook(self) -> str:
        md = ''
        if self.attributes is not None:
            md += f'#### Attributes\n{self.attributes}\n\n'
        md += '#### Code Details\n{details}\n\n'.format(details=self.detail)
        return md.strip()

    @classmethod
    def doc_type(cls) -> str:
        return 'class'


class ModuleDoc(Doc):
    example: Optional[str] = None
    functions: List[str] = None

    @field_serializer('functions')
    def functions_serializer(self, v: List[str], _info) -> str:
        return '\n'.join(map(lambda x: f'- {x}', v))

    @classmethod
    def from_chapter_hook(cls, doc: ModuleDoc, block: str) -> ModuleDoc:
        function_doc = cls.from_block(block, 'Functions')
        doc.functions = list(filter(lambda x: len(x), map(lambda x: x.strip('- '), function_doc.splitlines())))
        doc.example = cls.from_block(block, 'Use Case')
        return doc

    def _markdown_hook(self) -> str:
        md = ''
        if self.functions:
            md += '#### Functions\n{}\n\n'.format('\n'.join(map(lambda x: f'- {x}', self.functions)))
        if self.example:
            md += f'#### Use Case\n{self.example}\n\n'
        return md.strip()

    @classmethod
    def doc_type(cls) -> str:
        return 'module'

class RepoDoc(Doc):
    features: List[str] = None

    @field_serializer('features')
    def features_serializer(self, v: List[str], _info) -> str:
        return '\n'.join(map(lambda x: f'- {x}', v))

    @classmethod
    def from_chapter_hook(cls, doc: ModuleDoc, block: str) -> ModuleDoc:
        features_doc = cls.from_block(block, 'Features')
        doc.features = list(filter(lambda x: len(x), map(lambda x: x.strip('- '), features_doc.splitlines())))
        return doc

    def _markdown_hook(self) -> str:
        md = '#### Features\n{}\n\n'.format('\n'.join(map(lambda x: f'- {x}', self.features)))
        return md.strip()

    @classmethod
    def doc_type(cls) -> str:
        return 'repo'
