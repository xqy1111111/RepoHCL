import os
import sys
from abc import ABC, abstractmethod
from typing import Optional

from loguru import logger

from doc import DocItem, FunctionItem, ClassItem
from llm_helper import SimpleLLM
from project_manager import ProjectManager
from prompt import doc_generation_instruction, documentation_guideline
from settings import SettingsManager


class ChatEngine(ABC):
    def __init__(self, manager: ProjectManager):
        self._setting = SettingsManager.get_setting()
        self.project = manager
        self._llm = SimpleLLM(self._setting)

    @abstractmethod
    def _get_referenced_prompt(self, doc_item: DocItem) -> str:
        pass

    @abstractmethod
    def _get_referencer_prompt(self, doc_item: DocItem) -> str:
        pass

    @abstractmethod
    def _get_relationship_description(self, doc_item: DocItem):
        pass

    @abstractmethod
    def _get_code(self, doc_item):
        pass

    @abstractmethod
    def _get_attributes(self, doc_item):
        pass

    @abstractmethod
    def _get_example(self, doc_item):
        pass

    def build_prompt(self, doc_item: DocItem):
        system_prompt = doc_generation_instruction.format(
            project_structure=self.project.get_project_structure(),
            file_path=doc_item.file,
            code_type_tell=doc_item.doc_type(),
            code_name=doc_item.name,
            code_content=self._get_code(doc_item),
            example=self._get_example(doc_item),
            has_relationship=self._get_relationship_description(doc_item),
            reference_letter=self._get_referenced_prompt(doc_item),
            referencer_content=self._get_referencer_prompt(doc_item),
            parameters_note=self._get_attributes(doc_item),
            language=self._setting.project.language,
        )

        # debug
        f = f'docs/{doc_item.file}.prompt.md'
        os.makedirs(os.path.dirname(f), exist_ok=True)
        with open(f, 'a') as c:
            c.write((
                f'### {doc_item.name}\n'
                f'{system_prompt}\n'
            ))
        return [
            {'role': 'system', 'content': system_prompt},
            {
                'role': 'user',
                'content': documentation_guideline.format(
                    language=self._setting.project.language)
            }
        ]

    def generate_doc(self, doc_item: DocItem) -> Optional[str]:
        """Generates documentation for a given DocItem."""
        try:
            messages = self.build_prompt(doc_item)
            md = self._llm.ask(messages)
            md += f'''
**Code**:
```C++
{doc_item.code}
```
'''
            return md
        except Exception as e:
            logger.error(f'fail to generate doc for {doc_item.name}, err={e}')
            return None


class FunctionEngine(ChatEngine):
    def _get_referenced_prompt(self, doc_item: DocItem) -> str:
        if len(doc_item.reference_who) == 0:
            return ''
        prompt = 'As you can see, the code calls the following objects, their docs and code are as following:\n\n'
        for reference_item in doc_item.reference_who:
            prompt += f'**Obj**: `{reference_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                list(map(lambda t: '> ' + t, reference_item.md_content.split('\n')))) + '\n---\n'
        return prompt

    def _get_referencer_prompt(self, doc_item: DocItem) -> str:
        if len(doc_item.who_reference_me) == 0:
            return ''
        prompt = 'Also, the code has been called by the following objects, their code and docs are as following:\n'
        for referencer_item in doc_item.who_reference_me:
            prompt += f'**Obj**: `{referencer_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                list(map(lambda t: '> ' + t, referencer_item.md_content.split('\n')))) + '\n---\n'
        return prompt

    def _get_relationship_description(self, doc_item: DocItem):
        if len(doc_item.reference_who) and len(doc_item.who_reference_me):
            return "And please include the reference relationship with its callers and callees in the project from a functional perspective"
        elif len(doc_item.who_reference_me):
            return "And please include the relationship with its callers in the project from a functional perspective."
        elif len(doc_item.reference_who):
            return "And please include the relationship with its callees in the project from a functional perspective."
        else:
            return ''

    def _get_attributes(self, doc_item: DocItem):
        return (
            f"> **Parameters**\n"
            f"> - Parameter1: XXX\n"
            f"> - Parameter2: XXX\n"
            "> - ...\n>\n"
        ) if isinstance(doc_item, FunctionItem) and doc_item.has_arg else ''

    def _get_example(self, doc_item: DocItem):
        return ("> ```C++\n" +
                "> (mock possible usage examples of this Function with codes.)"
                ) + 'You can refer to the use of this Function in the caller.' if len(
            doc_item.who_reference_me) else '' + '> ```\n'

    def _get_code(self, doc_item: DocItem):
        return ("The code of the Function is as follows:\n"
                "```C++\n"
                f"{doc_item.code}\n"
                "```")


class ClassEngine(ChatEngine):
    # 类的调用方设置为其所有的函数
    def _get_referenced_prompt(self, doc_item: DocItem) -> str:
        prompt = ''
        if isinstance(doc_item, ClassItem):
            prompt = 'The Class actually contains the following functions:\n\n'
            for method in doc_item.reference_who:
                if isinstance(method, FunctionItem):
                    prompt += (f'**Method**: `{method.access} {method.name}`\n\n' +
                               f'> Description:{method.md_content}\n---\n')
        return prompt

    # 类暂时不设置使用案例
    def _get_referencer_prompt(self, doc_item: DocItem) -> str:
        return ''

    def _get_relationship_description(self, doc_item: DocItem):
        return 'You should summarize the functionality of the class based on its functions but never list them.' if len(
            doc_item.reference_who) else ''

    def _get_attributes(self, doc_item: DocItem):
        return (
            f"> **Attributes**\n"
            f"> - Attribute1: XXX\n"
            f"> - Attribute2: XXX\n"
            "> - ...\n>\n"
        ) if isinstance(doc_item, ClassItem) and doc_item.has_attrs else ''

    def _get_example(self, doc_item: DocItem):
        return ('> ```C++\n' +
                '> (mock possible usage examples of this Class combining the public methods it provides.)\n'
                '> ```\n')

    def _get_code(self, doc_item: DocItem):
        return ('The part of code of the Class is as follows. '
                'For ease of understanding, only the code about attributes are retained. '
                'And each method owned by the Class will be provided afterward with a brief description in one sentence.\n'
                '```C++\n'
                f'{doc_item.code}\n'
                '```')
