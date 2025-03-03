from typing import List

import networkx as nx
from loguru import logger

from .metric import Metric, FieldDef, ClazzDef, Symbol
from .function import documentation_guideline
from .doc import ApiDoc, ClazzDoc
from utils import SimpleLLM, ChatCompletionSettings, prefix_with


class ClazzMetric(Metric):
    def eva(self, ctx):
        clazz = ctx.clazz_map
        callgraph = ctx.clazz_callgraph
        sorted_clazz = list(reversed(list(nx.topological_sort(callgraph))))
        # 逆拓扑排序callgraph
        logger.info(f'[ClazzMetric] gen doc for class, class count: {len(ctx.clazz_map)}')
        # 生成文档
        for i in range(len(sorted_clazz)):
            symbol = Symbol(base=sorted_clazz[i])
            if ctx.load_clazz_doc(symbol):
                logger.info(f'[ClazzMetric] load {symbol.base}: {i + 1}/{len(sorted_clazz)}')
                continue
            c: ClazzDef = clazz.get(symbol)
            referenced = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_clazz_doc(Symbol(base=s)), callgraph.predecessors(symbol.base)))
            )
            functions = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_function_doc(s.symbol), c.functions))
            )
            prompt = ClazzPromptBuilder().structure(ctx.structure).attributes(c.fields).code(c.code).functions(
                functions).referenced(referenced).file_path(c.filename).name(symbol.base).build()
            llm = SimpleLLM(ChatCompletionSettings())
            res = llm.add_system_msg(prompt).add_user_msg(documentation_guideline).ask()
            res = f'### {symbol.base}\n' + res
            doc = ClazzDoc.from_chapter(res)
            ctx.save_clazz_doc(symbol, doc)
            logger.info(f'[ClazzMetric] parse {symbol.base}: {i + 1}/{len(sorted_clazz)}')


doc_generation_instruction = (
    "You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. "
    "The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.\n\n"
    "Currently, you are in a project and the related hierarchical structure of this project is as follows\n"
    "{project_structure}\n\n"
    "The path of the document you need to generate in this project is {file_path}.\n"
    'Now you need to generate a document for a Class, whose name is `{code_name}`.\n\n'
    "The code of the Class is as follows:\n\n"
    "```C++\n"
    "{code}\n"
    "```\n\n"
    "{functions}\n"
    "{referenced}\n\n"
    "Please generate a detailed explanation document for this Class based on the code of the target Class itself and combine it with its calling situation in the project.\n\n"
    "Please write out the function of this Class briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.\n\n"
    "The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:\n\n"
    "> #### Description\n"
    "> Briefly describe the Class in one sentence\n"
    "{attributes}"
    "> #### Code Details\n"
    "> Detailed and CERTAIN code analysis of the Class. {has_relationship}\n\n"
    "Please note:\n"
    "- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.\n"
    "- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format\n")


class ClazzPromptBuilder:
    _prompt: str = doc_generation_instruction

    _tag_referenced = False
    _tag_functions = False

    def structure(self, structure: str):
        self._prompt = self._prompt.replace('{project_structure}', structure)
        return self

    def name(self, name: str):
        self._prompt = self._prompt.replace('{code_name}', name)
        return self

    def file_path(self, file_path: str):
        self._prompt = self._prompt.replace('{file_path}', file_path)
        return self

    def referenced(self, referenced: List[ClazzDoc]):
        if len(referenced) == 0:
            self._prompt = self._prompt.replace('{referenced}', '')
            return self
        prompt = 'As you can see, the class holds the following class as attributes, their docs and code are as following:\n\n'
        for reference_item in referenced:
            prompt += f'**Class**: `{reference_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                list(map(lambda t: '> ' + t, reference_item.markdown()))) + '\n---\n'
        self._prompt = self._prompt.replace('{referenced}', prompt)
        self._tag_referenced = True
        return self

    def functions(self, functions: List[ApiDoc]):
        if len(functions) == 0:
            self._prompt = self._prompt.replace('{functions}', '')
            return self
        prompt = 'The class have some relative methods, their descriptions are as following:\n'
        for f in functions:
            prompt += f'**Method**: `{f.name}`\n\n**Description**:{f.description}\n' + '\n---\n'
        self._prompt = self._prompt.replace('{functions}', prompt)
        self._tag_functions = True
        return self

    def build(self) -> str:
        if self._tag_referenced or self._tag_functions:
            self._prompt = self._prompt.replace('{has_relationship}',
                                                'And please include the reference relationship with its methods or callees in the project from a functional perspective')
        else:
            self._prompt = self._prompt.replace('{has_relationship}', '')
        return self._prompt

    def attributes(self, params: List[FieldDef]):
        if len(params):
            self._prompt = self._prompt.replace('{attributes}', prefix_with((
                "#### Attributes\n"
                "- Attribute1: XXX\n"
                "- Attribute2: XXX\n"
                "- ...\n"), '> '))
        else:
            self._prompt = self._prompt.replace('{attributes}', '')
        return self

    def code(self, code: str):
        self._prompt = self._prompt.replace('{code}', code)
        return self
