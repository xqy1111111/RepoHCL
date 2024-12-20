import os
from typing import Optional

from loguru import logger

from doc import DocItem, FunctionItem
from llm_helper import SimpleLLM
from project_manager import ProjectManager
from prompt import doc_generation_instruction, documentation_guideline
from settings import SettingsManager


class ChatEngine:
    """
    ChatEngine is used to generate the doc of functions or classes.
    """

    def __init__(self, manager: ProjectManager):
        self._setting = SettingsManager.get_setting()
        self.project = manager
        self._llm = SimpleLLM(self._setting)

    def build_prompt(self, doc_item: DocItem):
        """Builds and returns the system and user prompts based on the DocItem."""
        referenced = len(doc_item.who_reference_me) > 0

        code_type = doc_item.code_type
        code_name = doc_item.name
        code_content = doc_item.code
        file_path = doc_item.file
        project_structure = self.project.get_project_structure()

        def get_referenced_prompt(doc_item: DocItem) -> str:
            if len(doc_item.reference_who) == 0:
                return ""
            prompt = 'As you can see, the code calls the following objects, their docs and code are as following:\n\n'
            for reference_item in doc_item.reference_who:
                prompt += f'**Obj**: `{reference_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                    list(map(lambda t: '> ' + t, reference_item.md_content.split('\n')))) + '\n---\n'
            return prompt

        def get_referencer_prompt(doc_item: DocItem) -> str:
            if len(doc_item.who_reference_me) == 0:
                return ""
            prompt = 'Also, the code has been called by the following objects, their code and docs are as following:\n'
            for referencer_item in doc_item.who_reference_me:
                prompt += f'**Obj**: `{referencer_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                    list(map(lambda t: '> ' + t, referencer_item.md_content.split('\n')))) + '\n---\n'
            return prompt

        def get_relationship_description(referencer_content, reference_letter):
            if referencer_content and reference_letter:
                return "And please include the reference relationship with its callers and callees in the project from a functional perspective"
            elif referencer_content:
                return "And please include the relationship with its callers in the project from a functional perspective."
            elif reference_letter:
                return "And please include the relationship with its callees in the project from a functional perspective."
            else:
                return ""

        code_type_tell = "Class" if code_type == "ClassDef" else "Function"

        parameters_or_attribute = "attribute" if code_type == "ClassDef" else "Parameter"
        parameters_note = (
            f"**{parameters_or_attribute}**\n"
            f"> The {parameters_or_attribute} of this {code_type_tell}.\n"
            f"> The {parameters_or_attribute} of this {code_type_tell}.\n"
            f"> - {code_type_tell}1: XXX\n"
            f"> - {code_type_tell}2: XXX\n"
            "> - ...\n>\n"
        ) if isinstance(doc_item, FunctionItem) and doc_item.has_arg else ''
        have_return_tell = (
            "> **Output Example**: \n"
            "> ```C++\n"
            "> (mock possible usage examples of this function with codes.)"
            "> ```"
            "\n>\n"
            if isinstance(doc_item, FunctionItem) and doc_item.has_return
            else ''
        )
        combine_ref_situation = (
            "and combine it with its calling situation in the project,"
            if referenced
            else ""
        )

        referencer_content = get_referencer_prompt(doc_item)
        reference_letter = get_referenced_prompt(doc_item)
        has_relationship = get_relationship_description(
            referencer_content, reference_letter
        )

        project_structure_prefix = ", and the related hierarchical structure of this project is as follows (The current object is marked with an *):"

        system_prompt = doc_generation_instruction.format(
            project_structure=project_structure,
            combine_ref_situation=combine_ref_situation,
            file_path=file_path,
            project_structure_prefix=project_structure_prefix,
            code_type_tell=code_type_tell,
            code_name=code_name,
            code_content=code_content,
            have_return_tell=have_return_tell,
            has_relationship=has_relationship,
            reference_letter=reference_letter,
            referencer_content=referencer_content,
            parameters_note=parameters_note,
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
