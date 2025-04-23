from typing import List  # 导入List类型提示

from loguru import logger  # 导入日志记录工具

from utils import SimpleLLM, ChatCompletionSettings, prefix_with, TaskDispatcher  # 导入LLM、聊天设置、前缀工具和任务分发器
from utils.settings import llm_thread_pool  # 导入LLM线程池设置
from .doc import ApiDoc  # 导入API文档类
from .metric import Metric, FieldDef, FuncDef  # 导入度量基类和字段、函数定义类

documentation_guideline = (
    "Keep in mind that your audience is document readers, so use a deterministic tone to generate precise content and don't let them know "
    "you're provided with code snippet and documents. AVOID ANY SPECULATION and inaccurate descriptions! Now, provide the documentation "
    "for the target object in a professional way."
)  # 文档生成指导，告诉LLM以专业的方式生成精确的文档


# 为函数生成文档
class FunctionMetric(Metric):
    """
    函数度量类，用于为项目中的函数生成文档
    
    继承自Metric抽象基类，实现了eva方法
    """

    def eva(self, ctx):
        """
        评估方法，为所有函数生成文档
        
        Args:
            ctx: 评估上下文对象，包含函数调用图等信息
        """
        callgraph = ctx.callgraph  # 获取函数调用图
        logger.info(f'[FunctionMetric] gen doc for functions, functions count: {len(callgraph)}')  # 记录函数数量

        # 生成文档
        def gen(symbol: str):
            """
            为单个函数生成文档的内部函数
            
            Args:
                symbol: 函数符号名
            """
            if ctx.load_function_doc(symbol):  # 如果文档已存在
                logger.info(f'[FunctionMetric] load {symbol}')  # 记录加载信息
                return  # 跳过生成
            f: FuncDef = ctx.func(symbol)  # 获取函数定义
            referencer = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_function_doc(s), callgraph.successors(symbol)))
            )  # 获取此函数调用的其他函数的文档（被引用的函数）
            referenced = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_function_doc(s), callgraph.predecessors(symbol)))
            )  # 获取调用此函数的其他函数的文档（引用此函数的函数）
            prompt = _FunctionPromptBuilder().parameters(f.params).code(f.code).referencer(
                referencer).referenced(referenced).lang(ctx.lang.markdown).name(symbol).build()  # 构建提示
            res = SimpleLLM(ChatCompletionSettings()).add_system_msg(prompt).add_user_msg(documentation_guideline).ask()  # 调用LLM生成文档
            res = f'### {symbol}\n' + res  # 添加标题
            doc = ApiDoc.from_chapter(res)  # 从Markdown文本解析生成ApiDoc对象
            ctx.save_function_doc(symbol, doc)  # 保存函数文档
            logger.info(f'[FunctionMetric] parse {symbol}')  # 记录解析信息

        TaskDispatcher(llm_thread_pool).map(callgraph, gen).run()  # 使用任务分发器并行处理所有函数


doc_generation_instruction = '''
You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object.
The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.
Now you need to generate a document for a Function, whose name is `{code_name}`.

The code of the Function is as follows:
```{lang}
{code}
```

{referenced}
{referencer}

Please generate a detailed explanation document for this Function based on the code of the target Function itself and combine it with its calling situation in the project.
Please write out the function of this Function briefly followed by a detailed analysis (including all details) to serve as the documentation for this part of the code.
The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:
> #### Description
> Briefly describe the Function in one sentence.
{parameters}
> #### Code Details
> Detailed and CERTAIN code analysis of the Function. {has_relationship}
> #### Example
> ```{lang}
> Mock possible usage examples of the Function with codes. {example}
> ```
Please note:
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format.
'''  # 文档生成指令模板，定义了函数文档的格式和内容要求


class _FunctionPromptBuilder:
    """
    函数提示构建器，用于构建发送给LLM的提示
    
    使用链式调用模式，每个方法都返回self以便连续调用
    """
    _prompt: str = doc_generation_instruction  # 初始化提示为文档生成指令模板

    _tag_referenced = False  # 是否有被引用函数的标记
    _tag_referencer = False  # 是否有引用函数的标记

    def name(self, name: str):
        """
        设置函数名称
        
        Args:
            name: 函数名称
            
        Returns:
            self，用于链式调用
        """
        self._prompt = self._prompt.replace('{code_name}', name)  # 替换模板中的函数名占位符
        return self  # 返回self用于链式调用

    # def structure(self, structure: str):
    #     self._prompt = self._prompt.replace('{project_structure}', structure)
    #     return self
    #
    # def file_path(self, file_path: str):
    #     self._prompt = self._prompt.replace('{file_path}', file_path)
    #     return self

    def lang(self, lang: str):
        """
        设置编程语言
        
        Args:
            lang: 编程语言名称
            
        Returns:
            self，用于链式调用
        """
        self._prompt = self._prompt.replace('{lang}', lang)  # 替换模板中的语言占位符
        return self  # 返回self用于链式调用

    def referenced(self, referenced: List[ApiDoc]):
        """
        设置被当前函数引用的其他函数文档
        
        Args:
            referenced: 被引用函数的文档列表
            
        Returns:
            self，用于链式调用
        """
        if len(referenced) == 0:  # 如果没有被引用的函数
            self._prompt = self._prompt.replace('{referenced}', '')  # 清空相关占位符
            return self  # 返回self用于链式调用
        prompt = 'As you can see, the code calls the following methods, their docs and code are as following:\n\n'  # 创建被引用函数的提示起始文本
        for reference_item in referenced:  # 遍历每个被引用函数
            prompt += f'**Method**: `{reference_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                list(map(lambda t: '> ' + t, reference_item.markdown()))) + '\n---\n'  # 添加每个被引用函数的信息
        self._prompt = self._prompt.replace('{referenced}', prompt)  # 替换模板中的被引用函数占位符
        self._tag_referenced = True  # 设置被引用标记为真
        return self  # 返回self用于链式调用

    def referencer(self, referencer: List[ApiDoc]):
        """
        设置引用当前函数的其他函数文档
        
        Args:
            referencer: 引用当前函数的文档列表
            
        Returns:
            self，用于链式调用
        """
        if len(referencer) == 0:  # 如果没有引用当前函数的函数
            self._prompt = self._prompt.replace('{referencer}', '')  # 清空相关占位符
            return self  # 返回self用于链式调用
        prompt = 'Also, the code has been called by the following methods, their code and docs are as following:\n'  # 创建引用函数的提示起始文本
        for referencer_item in referencer:  # 遍历每个引用函数
            prompt += f'**Method**: `{referencer_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                list(map(lambda t: '> ' + t, referencer_item.markdown().split('\n')))) + '\n---\n'  # 添加每个引用函数的信息
        self._prompt = self._prompt.replace('{referencer}', prompt)  # 替换模板中的引用函数占位符
        self._tag_referencer = True  # 设置引用标记为真
        return self  # 返回self用于链式调用

    def build(self) -> str:
        """
        构建最终的提示字符串
        
        根据之前设置的标记和内容，完成所有占位符替换
        
        Returns:
            完整的提示字符串
        """
        if self._tag_referenced or self._tag_referencer:  # 如果有引用关系
            self._prompt = self._prompt.replace('{has_relationship}',
                                                'And please include the reference relationship with its callers or callees in the project from a functional perspective')  # 添加引用关系说明
        else:  # 如果没有引用关系
            self._prompt = self._prompt.replace('{has_relationship}', '')  # 清空相关占位符
            self._prompt = self._prompt.replace('{example}', '')  # 清空示例占位符
        if self._tag_referencer:  # 如果有引用当前函数的函数
            self._prompt = self._prompt.replace('{example}', 'You can refer to the use of this Function in the caller.')  # 添加示例参考说明
        return self._prompt  # 返回完整的提示字符串

    def parameters(self, params: List[FieldDef]):
        """
        设置函数参数
        
        Args:
            params: 参数定义列表
            
        Returns:
            self，用于链式调用
        """
        if len(params):  # 如果有参数
            self._prompt = self._prompt.replace('{parameters}', prefix_with(
                '#### Parameters\n'
                '- Parameter1: XXX\n'
                '- Parameter2: XXX\n'
                '- ...\n', '> '))  # 添加参数部分的格式
        else:  # 如果没有参数
            self._prompt = self._prompt.replace('{parameters}', '')  # 清空参数占位符
        return self  # 返回self用于链式调用

    def code(self, code: str):
        """
        设置函数源代码
        
        Args:
            code: 函数源代码
            
        Returns:
            self，用于链式调用
        """
        self._prompt = self._prompt.replace('{code}', code)  # 替换模板中的代码占位符
        return self  # 返回self用于链式调用
