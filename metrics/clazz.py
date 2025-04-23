from typing import List  # 导入List类型提示

from loguru import logger  # 导入日志记录工具

from utils import SimpleLLM, ChatCompletionSettings, prefix_with, TaskDispatcher, llm_thread_pool  # 导入LLM、设置、前缀工具和任务分发相关工具
from .doc import ApiDoc, ClazzDoc  # 导入API文档和类文档
from .function import documentation_guideline  # 导入文档生成指南
from .metric import Metric, FieldDef, ClazzDef  # 导入度量基类和字段、类定义类


# 为类生成文档
class ClazzMetric(Metric):
    """
    类度量类，用于为项目中的类生成文档
    
    继承自Metric抽象基类，实现了eva方法
    """
    def eva(self, ctx):
        """
        评估方法，为所有类生成文档
        
        Args:
            ctx: 评估上下文对象，包含类调用图等信息
        """
        callgraph = ctx.clazz_callgraph  # 获取类调用图
        logger.info(f'[ClazzMetric] gen doc for class, class count: {len(callgraph)}')  # 记录类数量

        # 生成文档
        def gen(symbol: str):
            """
            为单个类生成文档的内部函数
            
            Args:
                symbol: 类符号名
            """
            if ctx.load_clazz_doc(symbol):  # 如果文档已存在
                logger.info(f'[ClazzMetric] load {symbol}')  # 记录加载信息
                return  # 跳过生成
            c: ClazzDef = ctx.clazz(symbol)  # 获取类定义
            referenced = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_clazz_doc(s), callgraph.predecessors(symbol)))
            )  # 获取引用此类的其他类的文档
            functions = list(
                filter(lambda s: s is not None,
                       map(lambda s: ctx.load_function_doc(s.symbol), c.functions))
            )  # 获取此类中的函数文档
            prompt = ClazzPromptBuilder().attributes(c.fields).code(c.code).functions(
                functions).referenced(referenced).lang(ctx.lang.markdown).name(symbol).build()  # 构建提示
            llm = SimpleLLM(ChatCompletionSettings())  # 创建LLM客户端
            res = llm.add_system_msg(prompt).add_user_msg(documentation_guideline).ask()  # 调用LLM生成文档
            res = f'### {symbol}\n' + res  # 添加标题
            doc = ClazzDoc.from_chapter(res)  # 从Markdown文本解析生成ClazzDoc对象
            ctx.save_clazz_doc(symbol, doc)  # 保存类文档
            logger.info(f'[ClazzMetric] parse {symbol}')  # 记录解析信息

        TaskDispatcher(llm_thread_pool).map(callgraph, gen).run()  # 使用任务分发器并行处理所有类


doc_generation_instruction = (
    "You are an AI documentation assistant, and your task is to generate documentation based on the given code of an object. "
    "The purpose of the documentation is to help developers and beginners understand the function and specific usage of the code.\n\n"
    'Now you need to generate a document for a Class, whose name is `{code_name}`.\n\n'
    "The code of the Class is as follows:\n\n"
    "```{lang}\n"
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
    "- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format\n")  # 类文档生成指令模板，定义了类文档的格式和内容要求


class ClazzPromptBuilder:
    """
    类提示构建器，用于构建发送给LLM的提示
    
    使用链式调用模式，每个方法都返回self以便连续调用
    """
    _prompt: str = doc_generation_instruction  # 初始化提示为文档生成指令模板

    _tag_referenced = False  # 是否有被引用类的标记
    _tag_functions = False  # 是否有函数的标记

    def name(self, name: str):
        """
        设置类名称
        
        Args:
            name: 类名称
            
        Returns:
            self，用于链式调用
        """
        self._prompt = self._prompt.replace('{code_name}', name)  # 替换模板中的类名占位符
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

    def referenced(self, referenced: List[ClazzDoc]):
        """
        设置引用当前类的其他类文档
        
        Args:
            referenced: 引用当前类的文档列表
            
        Returns:
            self，用于链式调用
        """
        if len(referenced) == 0:  # 如果没有引用当前类的类
            self._prompt = self._prompt.replace('{referenced}', '')  # 清空相关占位符
            return self  # 返回self用于链式调用
        prompt = 'As you can see, the class holds the following class as attributes, their docs and code are as following:\n\n'  # 创建引用类的提示起始文本
        for reference_item in referenced:  # 遍历每个引用类
            prompt += f'**Class**: `{reference_item.name}`\n\n' + '**Document**:\n\n' + '\n'.join(
                list(map(lambda t: '> ' + t, reference_item.markdown()))) + '\n---\n'  # 添加每个引用类的信息
        self._prompt = self._prompt.replace('{referenced}', prompt)  # 替换模板中的引用类占位符
        self._tag_referenced = True  # 设置引用标记为真
        return self  # 返回self用于链式调用

    def functions(self, functions: List[ApiDoc]):
        """
        设置类中的函数文档
        
        Args:
            functions: 类中的函数文档列表
            
        Returns:
            self，用于链式调用
        """
        if len(functions) == 0:  # 如果没有函数
            self._prompt = self._prompt.replace('{functions}', '')  # 清空相关占位符
            return self  # 返回self用于链式调用
        prompt = 'The class have some relative methods, their descriptions are as following:\n'  # 创建函数列表的提示起始文本
        for f in functions:  # 遍历每个函数
            prompt += f'**Method**: `{f.name}`\n\n**Description**:{f.description}\n' + '\n---\n'  # 添加每个函数的信息
        self._prompt = self._prompt.replace('{functions}', prompt)  # 替换模板中的函数列表占位符
        self._tag_functions = True  # 设置函数标记为真
        return self  # 返回self用于链式调用

    def build(self) -> str:
        """
        构建最终的提示字符串
        
        根据之前设置的标记和内容，完成所有占位符替换
        
        Returns:
            完整的提示字符串
        """
        if self._tag_referenced or self._tag_functions:  # 如果有引用关系或函数
            self._prompt = self._prompt.replace('{has_relationship}',
                                                'And please include the reference relationship with its methods or callees in the project from a functional perspective')  # 添加引用关系说明
        else:  # 如果没有引用关系或函数
            self._prompt = self._prompt.replace('{has_relationship}', '')  # 清空相关占位符
        return self._prompt  # 返回完整的提示字符串

    def attributes(self, params: List[FieldDef]):
        """
        设置类属性
        
        Args:
            params: 属性定义列表
            
        Returns:
            self，用于链式调用
        """
        if len(params):  # 如果有属性
            self._prompt = self._prompt.replace('{attributes}', prefix_with((
                "#### Attributes\n"
                "- Attribute1: XXX\n"
                "- Attribute2: XXX\n"
                "- ...\n"), '> '))  # 添加属性部分的格式
        else:  # 如果没有属性
            self._prompt = self._prompt.replace('{attributes}', '')  # 清空属性占位符
        return self  # 返回self用于链式调用

    def code(self, code: str):
        """
        设置类源代码
        
        Args:
            code: 类源代码
            
        Returns:
            self，用于链式调用
        """
        self._prompt = self._prompt.replace('{code}', code)  # 替换模板中的代码占位符
        return self  # 返回self用于链式调用
