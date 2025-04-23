import os.path  # 导入os.path模块，用于处理文件路径
from functools import reduce  # 导入reduce函数，用于对序列进行累积操作
from typing import List  # 导入List类型提示

from loguru import logger  # 导入日志记录工具

from utils import SimpleLLM, prefix_with, ChatCompletionSettings, TaskDispatcher, llm_thread_pool, Task  # 导入LLM和任务分发相关工具
from . import EvaContext  # 导入评估上下文
from .doc import ModuleDoc  # 导入模块文档类
from .metric import Metric  # 导入度量基类

modules_summarize_prompt = '''
You are an expert in software architecture analysis. 
Your task is to review function descriptions from a code repository and organize them into multiple functional modules based on their purpose and interrelations. 
You need to output a structured summary for each identified functional module.

The standard format is in the Markdown reference paragraph below, and you shouldn't write the reference symbols `>` when you output:

> ### Module Name
> #### Description
> A concise paragraph summarizing the module's purpose, how it contributes to solving specific problems, and which functions work together within the module.
> #### Functions
> - Function1
> - Function2

You'd better consider the following workflow:
1. Identify Core Functionality. Start by reading through all function descriptions to get a broad understanding of the available functionalities and think about the core tasks or operations that these functions enable.
2. Define Functional Modules. Based on the core functionalities, define initial functional modules that encapsulate related tasks or operations. Use your expertise to determine logical groupings of functions that contribute to similar outcomes or processes.
3. Analyze Function Interdependencies. Examine how functions interact with one another. Consider whether they are called in sequence, share data, or serve complementary purposes. Recognize that a single function can be part of multiple modules if it serves different roles or contexts.
4. Refine Module Definitions. Review and adjust the boundaries of the modules as needed to ensure they accurately reflect the relationships between functions. Ensure that each module's summary clearly articulates its unique value and contribution to the overall system.
5. Generate Documentation. Write a summary for each module using the provided format you finally decide and put them together. Don't include any other content in the output. 

Please Note:
- #### Functions is a list of function names included in this module. Please use the full function name with the return type and parameters, not the abbreviation.
- Try to put every function into at least one module unless the function is really useless.
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them. Don't add new Level 3 or Level 4 headings. Do not write anything outside the format

Now a list of function descriptions are provided as follows, you can start working.
{api_docs}
'''  # 模块总结提示模板，指导LLM如何根据函数列表生成模块概要

modules_enhance_prompt = '''
You are an expert in software architecture analysis. 
Your task is to read the module documentation of a project and improve it.
There are two key points for improvement:
1. This module contains some functions, but these functions may not be appropriate, and you need to remove these functions.
2. Design a usage scenario for this module. You need to mock a use case that combines as many functions as possible from the module to solve a specific problem in this scenario. The use case should be realistic and demonstrate the functionality of the module.'

The improved README should keep the same format as before. To ensure the same format, you should follow the standard format in the Markdown reference paragraph below. You do not need to write the reference symbols `>` when you output:

> ### Module Name
> #### Description
> A concise paragraph summarizing the module's purpose, how it contributes to solving specific problems, and which functions work together within the module.
> #### Functions
> - Function1
> - Function2
> #### Use Case
> ```{lang}
> Mock possible usage examples of the Module with codes.
> ```

You'd better consider the following workflow:
1. Understand the Module. Read through the function descriptions and the module summary to gain a comprehensive understanding of the module's purpose and functionality. Identify the key functions that contribute to the module's core operations and remove any irrelevant functions.
2. Define the Use Case. Based on the functions available in the module, define a specific problem or scenario that the module can address. Consider how multiple functions can work together to achieve a desired outcome or solve a particular issue.
3. Rewrite the Module Summary. Update the module summary to reflect the refined list of functions and the use case you have designed. 

Please Note:
- If all functions are related to the module tightly, you don't need to remove any functions.
- #### Functions is a list of function names included in this module. Please use the full function name with the return type and parameters, not the abbreviation.
- You can revise the content in #### Description if it's not consistent with the answers to the questions.
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them. 
- Don't write new Level 3 or Level 4 headings. Don't write anything outside the format. 
- Do not output descriptions of improvements.


Here is the documentation of the module you need to enhance:

{module_doc}

Here is the documentation of the functions referenced in the module:

{functions_doc}
'''  # 模块增强提示模板，指导LLM如何优化模块文档并添加用例


# 为模块生成文档
class ModuleMetric(Metric):
    """
    模块度量类，用于根据函数文档生成模块文档
    
    继承自Metric抽象基类，实现了eva方法和一系列辅助方法
    """

    @classmethod
    def get_draft_filename(cls, ctx):
        """
        获取模块草稿文件名
        
        Args:
            ctx: 评估上下文对象
            
        Returns:
            模块草稿文件的完整路径
        """
        return os.path.join(ctx.doc_path, 'modules.v1_draft.md')  # 返回草稿文件路径

    @classmethod
    def _draft(cls, ctx) -> List[ModuleDoc]:
        """
        生成模块文档草稿
        
        首先尝试加载已有草稿，如果没有则根据函数文档生成新的模块草稿
        
        Args:
            ctx: 评估上下文对象
            
        Returns:
            模块文档草稿列表
        """
        existed_draft_doc = ctx.load_docs(cls.get_draft_filename(ctx), ModuleDoc)  # 尝试加载已有草稿
        if len(existed_draft_doc):  # 如果存在草稿
            logger.info(f'[ModuleMetric] load drafts, modules count: {len(existed_draft_doc)}')  # 记录加载信息
            return existed_draft_doc  # 返回已有草稿
        # 提取所有用户可见的函数
        apis: List[str] = list(map(lambda x: x.symbol, filter(lambda x: x.visible, ctx.func_iter())))  # 获取所有可见函数
        # 使用函数描述组织上下文
        api_docs = reduce(lambda x, y: x + y,
                          map(lambda a: f'- {a}\n > {ctx.load_function_doc(a).description}\n\n', apis))  # 构建函数列表文本
        prompt = modules_summarize_prompt.format(api_docs=api_docs)  # 格式化提示模板
        # 生成模块文档
        res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt).ask()  # 调用LLM生成文档
        modules = ModuleDoc.from_doc(res)  # 从结果解析模块文档
        # 保存模块文档初稿，若模块中只有一个函数，则舍弃
        modules = list(filter(lambda x: len(modules) == 1 or len(x.functions) > 1, modules))  # 过滤掉只有一个函数的模块
        for m in modules:  # 遍历模块
            ctx.save_doc(cls.get_draft_filename(ctx), m)  # 保存模块草稿
        logger.info(f'[ModuleMetric] gen drafts for modules, modules count: {len(modules)}')  # 记录生成信息
        return modules  # 返回生成的模块草稿

    @classmethod
    def _enhance(cls, ctx, drafts: List[ModuleDoc]):
        """
        增强模块文档，为草稿添加用例并优化
        
        Args:
            ctx: 评估上下文对象
            drafts: 模块文档草稿列表
        """
        existed_modules_doc = ctx.load_module_docs()  # 尝试加载已有的模块文档
        if len(existed_modules_doc):  # 如果已有模块文档
            logger.info(f'[ModuleMetric] load docs, modules count: {len(existed_modules_doc)}')  # 记录加载信息
            return  # 直接返回，不进行增强

        # 优化模块文档
        def gen(i: int, m: ModuleDoc):
            """
            为单个模块生成增强文档的内部函数
            
            Args:
                i: 模块索引
                m: 模块文档草稿
            """
            # 使用完整函数文档组织上下文
            functions_doc = []  # 初始化函数文档列表
            for f in m.functions:  # 遍历模块中的函数
                try:
                    functions_doc.append(ctx.load_function_doc(f).markdown())  # 加载函数文档
                except KeyError:  # 如果函数文档不存在
                    logger.warning(f'[ModuleMetric] function doc not found: {f}')  # 记录警告
            functions_doc = prefix_with('\n---\n'.join(functions_doc), '> ')  # 合并函数文档并添加前缀
            # 使用原模块文档组织上下文
            module_doc = prefix_with(m.markdown(), '> ')  # 为模块文档添加前缀
            prompt2 = modules_enhance_prompt.format(module_doc=module_doc, functions_doc=functions_doc, lang=ctx.lang.markdown)  # 格式化提示模板
            # 生成模块文档
            res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt2).ask()  # 调用LLM生成增强文档
            doc = ModuleDoc.from_chapter(res)  # 从结果解析模块文档
            # 保存模块文档
            ctx.save_module_doc(doc)  # 保存增强后的模块文档
            logger.info(f'[ModuleMetric] gen doc for module {i + 1}/{len(drafts)}: {m.name}')  # 记录生成信息

        TaskDispatcher(llm_thread_pool).adds(list(map(lambda args: Task(f=gen, args=args), enumerate(drafts)))).run()  # 使用任务分发器并行处理所有模块

    @classmethod
    def _check(cls, ctx: EvaContext) -> bool:
        """
        检查是否有足够的API函数用于生成模块文档
        
        Args:
            ctx: 评估上下文对象
            
        Returns:
            是否有足够的API函数
        """
        apis: List[str] = list(map(lambda x: x.symbol, filter(lambda x: x.visible, ctx.func_iter())))  # 获取所有可见函数
        if len(apis) == 0:  # 如果没有API函数
            logger.warning(f'[ModuleMetric] no apis found, cannot generate modules docs')  # 记录警告
            return False  # 返回False
        logger.info(f'[ModuleMetric] apis count: {len(apis)}')  # 记录API数量
        return True  # 返回True

    def eva(self, ctx):
        """
        评估方法，为所有模块生成文档
        
        Args:
            ctx: 评估上下文对象
        """
        if not self._check(ctx):  # 如果检查不通过
            return  # 直接返回
        drafts = self._draft(ctx)  # 生成模块草稿
        self._enhance(ctx, drafts)  # 增强模块文档
