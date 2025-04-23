import os.path  # 导入os.path模块，用于文件路径操作
from functools import reduce  # 导入reduce函数，用于对序列进行累积操作
from typing import List  # 导入List类型，用于类型注解

import networkx as nx  # 导入networkx库，用于处理图结构
from loguru import logger  # 导入loguru的logger，用于日志记录

from utils import SimpleLLM, ChatCompletionSettings, prefix_with, TaskDispatcher, llm_thread_pool  # 导入工具函数和类
from .doc import ApiDoc  # 导入API文档类
from .metric import Metric, FieldDef, FuncDef  # 导入度量相关类和数据结构

documentation_guideline = (
    "Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know "
    "you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation "
    "for the target object in a professional way."
)  # 文档生成指南，指导大模型如何生成专业的文档

# 为函数生成文档V2
class FunctionV2Metric(Metric):
    """函数文档生成器V2版本
    
    负责为函数生成详细的文档，包括功能描述、参数说明、代码细节分析等
    采用两阶段策略：草稿生成和修订优化
    """

    @classmethod
    def get_v2_draft_filename(cls, ctx, file: str) -> str:
        """获取函数文档草稿的文件名
        
        Args:
            ctx: 评估上下文对象
            file: 源文件名
            
        Returns:
            函数文档草稿的完整路径
        """
        return os.path.join(f'{ctx.doc_path}', f'{file}.{ApiDoc.doc_type()}.v2_draft.md')

    def eva(self, ctx):
        """执行函数文档生成流程
        
        先生成草稿文档，然后进行修订优化
        
        Args:
            ctx: 评估上下文对象
        """
        self._draft(ctx)  # 生成草稿文档
        self._revise(ctx)  # 修订优化文档

    @classmethod
    def _draft(cls, ctx):
        """生成函数文档草稿
        
        根据函数代码和被调用的函数信息生成初步文档
        
        Args:
            ctx: 评估上下文对象
        """
        callgraph = ctx.callgraph  # 获取调用图
        # 逆拓扑排序callgraph
        logger.info(f'[FunctionV2Metric] gen doc for functions, functions count: {len(callgraph)}')

        # 生成文档
        def gen(symbol: str):
            """为单个函数生成文档草稿
            
            Args:
                symbol: 函数符号名称
            """
            f: FuncDef = ctx.func(symbol)  # 获取函数定义
            if ctx.load_doc(symbol, cls.get_v2_draft_filename(ctx, f.filename), ApiDoc):
                # 如果文档已存在，则跳过生成
                logger.info(f'[FunctionV2Metric] load {symbol}')
                return
            # 获取当前函数调用的所有函数的文档
            referenced = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_function_doc(s), callgraph.successors(symbol)))
            )
            # 构建提示模板
            prompt = _FunctionPromptBuilder().parameters(f.params).code(f.code).referenced(
                referenced).lang(ctx.lang.markdown).name(symbol).build()
            # 使用大模型生成文档
            res = SimpleLLM(ChatCompletionSettings()).add_system_msg(prompt).add_user_msg(documentation_guideline).ask()
            res = f'### {symbol}\n' + res  # 添加函数标题
            doc = ApiDoc.from_chapter(res)  # 将文本转换为ApiDoc对象
            doc.code = f'```{ctx.lang.markdown}\n{f.code}\n```'  # 添加代码部分
            ctx.save_doc(cls.get_v2_draft_filename(ctx, f.filename), doc)  # 保存文档草稿
            logger.info(f'[FunctionV2Metric] parse {symbol}')

        # 使用任务分发器并行处理所有函数
        TaskDispatcher(llm_thread_pool).map(callgraph, gen).run()

    @classmethod
    def _revise(cls, ctx):
        """修订函数文档
        
        根据调用当前函数的其他函数的信息来优化文档质量
        
        Args:
            ctx: 评估上下文对象
        """
        callgraph = ctx.callgraph  # 获取调用图
        logger.info(f'[FunctionV2Metric] revise doc for functions, functions count: {len(callgraph)}')

        # 生成文档
        def gen(symbol: str):
            """为单个函数修订文档
            
            Args:
                symbol: 函数符号名称
            """
            if ctx.load_function_doc(symbol):
                # 如果最终文档已存在，则跳过修订
                logger.info(f'[FunctionV2Metric] load revised {symbol}')
                return
            f: FuncDef = ctx.func(symbol)  # 获取函数定义
            # 获取调用当前函数的所有函数的文档
            referencer: List[ApiDoc] = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_function_doc(s), callgraph.predecessors(symbol)))
            )
            # 加载文档草稿
            draft_doc = ctx.load_doc(symbol, cls.get_v2_draft_filename(ctx, f.filename), ApiDoc)
            if len(referencer) == 0:
                # 如果没有调用当前函数的其他函数，直接使用草稿文档
                ctx.save_function_doc(symbol, draft_doc)
                return
            # 构建修订提示模板
            prompt = doc_revised_prompt.format(referencer=reduce(
                lambda x, y: x + y,
                map(lambda r: f'**Function**: `{r.name}`\n\n**Document**:\n\n{prefix_with(r.markdown(), "> ")}\n---\n',
                    referencer)),
                lang = ctx.lang.markdown,
                parameters = prefix_with(
                    '#### Parameters\n'
                    '- Parameter1: XXX\n'
                    '- Parameter2: XXX\n'
                    '- ...', '> ' if len(f.params) else '\n').strip(),
                function_doc=prefix_with(draft_doc.markdown(), '> '))
            # 使用大模型修订文档
            res = SimpleLLM(ChatCompletionSettings()).add_system_msg(prompt).add_user_msg(documentation_guideline).ask(
                lambda x: x[x.find('#### Description'):] # 去除标题
            )
            res = f'### {symbol}\n' + res  # 添加函数标题
            doc: ApiDoc = ApiDoc.from_chapter(res)  # 将文本转换为ApiDoc对象
            doc.code = f'```{ctx.lang.markdown}\n{f.code}\n```'  # 添加代码部分
            ctx.save_function_doc(symbol, doc)  # 保存最终文档
            logger.info(f'[FunctionV2Metric] revise {symbol}')

        # 使用任务分发器并行处理所有函数，注意这里使用反向调用图
        TaskDispatcher(llm_thread_pool).map(nx.reverse(callgraph), gen).run()

# Currently, you are in a project and the related hierarchical structure of this project is as follows:
# {project_structure}
# The path of the document you need to generate in this project is {file_path}.
doc_generation_instruction = '''
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object.
The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.
Now you need to generate a document for a Function, whose name is `{code_name}`.

The code of the Function is as follows:
```{lang}
{code}
```

{referenced}

Please generate a detailed explanation document for this Function based on the code of the target Function itself and combine it with its calling situation in the project.
Please write out the function of this Function briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.
The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Function in one sentence.
> #### Parameters
> - Parameter1
> #### Code Details
> Detailed and CERTAIN code analysis of the Function. {details_supplement}
> #### Example
> ```{lang}
> Mock possible usage examples of the Function with codes. 
> ```

Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format.
'''  # 函数文档生成提示模板

doc_revised_prompt = '''
You are an AI documentation assistant tasked with revising and enhancing the documentation for a given Function based on its usage examples. 
Your goal is to ensure that the documentation accurately reflects the Function's functionality without any speculation or inaccuracies.

The following Function documentation is what you need to revise:
{function_doc}

As you can see, the Function is called by the following Functions, their docs and code are as following. Please revise the above documentation by incorporating insights from them:
{referencer}

The previous documentation is written by a robot, and it may not be accurate or detailed enough. You should give it a major revision.
There are some points you need to pay attention to:
1. Ensure that the Description is concise and accurate.
2. Ensure that the Function is called correctly in Example.

The improved README should keep the same format as before. To ensure the same format, you should follow the standard format in the Markdown reference paragraph below. You do not need to write the reference symbols `>` when you output:

> #### Description
> Briefly describe the Function in one sentence.
{parameters}
> #### Code Details
> Detailed and CERTAIN code analysis of the Function. 
> #### Example
> ```{lang}
> Mock possible usage examples of the Function with codes. 
> ```

Please note:
- The improved documentation should keep the same format as before. That is, you should keep the headings in the documentation and only revise the content under each heading. 
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format.
- You do not need to write the reference symbols `>` when you output.
'''  # 函数文档修订提示模板


class _FunctionPromptBuilder:
    """函数提示构建器
    
    用于构建函数文档生成的提示模板，支持链式调用
    """
    _prompt: str = doc_generation_instruction  # 初始化提示模板


    def name(self, name: str):
        """设置函数名称
        
        Args:
            name: 函数名
            
        Returns:
            构建器自身，支持链式调用
        """
        self._prompt = self._prompt.replace('{code_name}', name)
        return self

    # def structure(self, structure: str):
    #     self._prompt = self._prompt.replace('{project_structure}', structure)
    #     return self
    #
    # def file_path(self, file_path: str):
    #     self._prompt = self._prompt.replace('{file_path}', file_path)
    #     return self

    def lang(self, lang: str):
        """设置编程语言
        
        Args:
            lang: 编程语言标识
            
        Returns:
            构建器自身，支持链式调用
        """
        self._prompt = self._prompt.replace('{lang}', lang)
        return self

    def referenced(self, referenced: List[ApiDoc]):
        """设置被引用的函数文档列表
        
        Args:
            referenced: 被引用的函数文档列表
            
        Returns:
            构建器自身，支持链式调用
        """
        if len(referenced) == 0:
            # 如果没有被引用的函数，则移除相关占位符
            self._prompt = self._prompt.replace('{referenced}', '').replace('{details_supplement}', '')
            return self
        # 构建被引用函数的文档信息
        prompt = 'As you can see, the code calls the following Functions, their docs and code are as following:\n\n'
        for reference_item in referenced:
            reference_item.code = None
            prompt += f'**Function**: `{reference_item.name}`\n\n' + '**Document**:\n\n' + prefix_with(
                reference_item.markdown(), '> ') + '\n---\n'
        # 替换占位符
        self._prompt = self._prompt.replace('{referenced}', prompt).replace('{details_supplement}',
                                                                            'You should refer to the documentation of the called Functions to analyze the code details.')
        return self

    def build(self) -> str:
        """构建最终的提示模板
        
        Returns:
            构建好的提示模板字符串
        """
        return self._prompt

    def parameters(self, params: List[FieldDef]):
        """设置函数参数列表
        
        Args:
            params: 参数定义列表
            
        Returns:
            构建器自身，支持链式调用
        """
        if len(params):
            # 如果有参数，则使用参数模板
            self._prompt = self._prompt.replace('{parameters}', prefix_with(
                '#### Parameters\n'
                '- Parameter1: XXX\n'
                '- Parameter2: XXX\n'
                '- ...', '> ').strip())
        else:
            # 如果没有参数，则使用空行
            self._prompt = self._prompt.replace('{parameters}', '>\n')
        return self

    def code(self, code: str):
        """设置函数代码
        
        Args:
            code: 函数代码字符串
            
        Returns:
            构建器自身，支持链式调用
        """
        self._prompt = self._prompt.replace('{code}', code)
        return self
