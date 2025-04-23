import os  # 导入os模块，提供与操作系统交互的功能
from functools import reduce  # 导入reduce函数，用于对序列进行累积操作
from typing import List  # 导入List类型，用于类型注解

from loguru import logger  # 导入loguru的logger，用于日志记录

from utils import SimpleLLM, prefix_with, ChatCompletionSettings, SimpleRAG, RagSettings, TaskDispatcher, \
    llm_thread_pool, Task  # 导入各种工具函数和类
from . import ModuleMetric  # 导入ModuleMetric基类
from .doc import ModuleDoc  # 导入模块文档类
from .metric import EvaContext  # 导入评估上下文类

modules_prompt = '''
You are an expert in software architecture analysis. 
Your task is to review function descriptions from a code repository and organize them into one or more functional module based on their purpose and interrelations. 

The following will provide you with the documentation of each function in the software in turn:
{api_doc}

Please organize these functions into one or more functional module and output each module documentation in the following format. 
You shouldn't write the reference symbols `>` when you output.

> ### Module Name
> #### Description
> A concise paragraph summarizing the module's purpose, how it contributes to solving specific problems, and which functions work together within the module.
> #### Functions
> - Function1
> - Function2

You'd better consider the following workflow:
1. Identify Core Functionality. Start by reading through all function descriptions to get a broad understanding of the available functionalities and think about the core tasks or operations that these functions enable. 
2. Filter Functions. Based on the core functionalities, filter out the functions that are not appropriate for the module. Consider whether they are called in sequence, share data, or serve complementary purposes. 
3. Name the Module in the required language. Review the core functionalities and the use case to come up with a suitable name for the module to replace the placeholder "Module Name" in the template. Remember that this is just a module of the software. Don't make it too broad.

Please Note:
- #### Functions is a list of function names included in this module. Please use the full function name with the return type and parameters, not the abbreviation.
- The Level 4 headings in the format like `#### Description` are fixed, don't change or translate them. Don't add new Level 3 or Level 4 headings. Do not write anything outside the format.
- Don't add divider lines like `---` between multiple modules.
'''  # 模块生成提示模板，指导大模型如何组织函数到模块中

modules_merge_prompt = '''
You are an expert in software architecture analysis.
You have reviewed the function descriptions from a code repository and organized them into functional modules based on their purpose and interrelations.
Now you need to merge the modules to make the documentation more concise and clear.

The following are the documentation of the modules you have organized:
{module_doc}

Please merge modules with similar functions and output the merged module documentation in the same format.
The correct format of each module documentation is as follows and you shouldn't write the reference symbols `>` when you output:

> ### Module Name
> #### Description
> A concise paragraph summarizing the module's purpose, how it contributes to solving specific problems, and which functions work together within the module.
> #### Functions
> - Function1
> - Function2

You'd better consider the following workflow:
1. Review Module Descriptions. Read through the descriptions of each module to understand the core functionalities of the software.
2. Merge Modules. Identify modules with similar functions or that can be combined to form a more comprehensive module. Consider how the functions in each module can work together to solve a specific problem or address a particular use case.
3. Remove useless modules. If there are modules that are not related to the software's core functionalities, consider removing them from the documentation to make it more concise.
4. Name the Merged Module in the required language. Based on the functions and use cases of the merged modules, come up with a suitable name for the merged module to replace the placeholder "Module Name" in the template. Remember that this is just a module of the software. Don't make it too broad.

Please Note:
- #### Functions is a list of function names included in this module. Please use the full function name with the return type and parameters, not the abbreviation.
- The Level 4 headings in the format like `#### Description` are fixed, don't change or translate them. Don't add new Level 3 or Level 4 headings. Do not write anything outside the format.
- Don't omit any modules related to the software's core functionalities. If they cannot be merged, keep them.
- Don't add divider lines like `---` between multiple modules.

'''  # 模块合并提示模板，指导大模型如何合并相似的模块


# 为模块生成文档V2，
# 本质上是先分解再合并，分解时使用聚类算法，合并时使用大模型。V2的效果并不比V1更好，但减少了上下文量。当具备1000个API时，V1的上下文量达到64+K。V2的上下文量则在10K以内。
class ModuleV2Metric(ModuleMetric):
    """模块文档生成器V2版本
    
    使用聚类算法和大模型相结合的方式生成模块文档
    相比V1版本，降低了上下文的数据量，适用于大型项目
    整个流程分为三步：草稿生成、模块合并和文档增强
    """

    @classmethod
    def get_v2_draft_filename(cls, ctx):
        """获取模块文档草稿的文件名
        
        Args:
            ctx: 评估上下文对象
            
        Returns:
            模块文档草稿的完整路径
        """
        return os.path.join(ctx.doc_path, 'modules-v2-draft.md')

    def eva(self, ctx):
        """执行模块文档生成流程
        
        使用三阶段策略：草稿生成、模块合并和文档增强
        
        Args:
            ctx: 评估上下文对象
        """
        if not self._check(ctx):
            return
        # 使用聚类算法初步划分模块，并由大模型总结模块文档
        drafts = self._draft_v2(ctx)
        # 由大模型合并模块文档
        drafts = self._merge(ctx, drafts)
        # 由大模型增强模块文档
        self._enhance(ctx, drafts)

    # 将API分组，对每组API生成模块初稿
    @classmethod
    def _draft_v2(cls, ctx: EvaContext) -> List[ModuleDoc]:
        """生成模块文档草稿
        
        使用聚类算法将相似功能的API分组，然后为每组生成模块文档
        
        Args:
            ctx: 评估上下文对象
            
        Returns:
            模块文档草稿列表
        """
        existed_draft_doc = ctx.load_docs(cls.get_v2_draft_filename(ctx), ModuleDoc)
        if len(existed_draft_doc):
            # 如果草稿文档已存在，则直接加载使用
            logger.info(f'[ModuleV2Metric] load module drafts, modules count: {len(existed_draft_doc)}')
            return existed_draft_doc
        # 提取所有用户可见的函数
        apis: List[str] = list(map(lambda x: x.symbol, filter(lambda x: x.visible, ctx.func_iter())))
        rag = SimpleRAG(RagSettings())
        logger.info('[ModuleV2Metric] clustering...')
        # 使用K-means聚类算法对函数进行分组，基于函数名称和描述
        cluster = rag.kmeans(
            list(map(lambda x: x.name + ': ' + x.description, map(lambda x: ctx.load_function_doc(x), apis))))
        logger.info(f'[ModuleV2Metric] cluster to {len(cluster)} groups')

        drafts = []  # 用于存储生成的模块文档草稿

        def gen(g: List[int]):
            """为单个函数组生成模块文档
            
            Args:
                g: 函数索引列表，表示一个聚类组
            """
            # 使用函数描述组织上下文
            api_docs = reduce(lambda x, y: x + y,
                              map(lambda x: f'- {apis[x]}\n > {ctx.load_function_doc(apis[x]).description}\n\n',
                                  g))
            # 构建提示模板
            prompt2 = modules_prompt.format(api_doc=prefix_with(api_docs, '>'))
            # 使用大模型生成模块文档
            res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt2).ask(lambda x: x.replace('---', '').strip())
            # 将文本转换为ModuleDoc对象列表
            docs = ModuleDoc.from_doc(res)
            # 保存模块文档草稿
            for doc in docs:
                ctx.save_doc(cls.get_v2_draft_filename(ctx), doc)
                logger.info(f'[ModuleV2Metric] gen draft for module {doc.name}')
            # 由于GIL锁，多线程下，extend是原子操作，线程安全
            drafts.extend(docs)

        # 使用任务分发器并行处理所有聚类组
        TaskDispatcher(llm_thread_pool).adds(list(map(lambda args: Task(f=gen, args=(args,)), cluster))).run()
        return drafts

    # 合并模块初稿
    @classmethod
    def _merge(cls, ctx: EvaContext, drafts: List[ModuleDoc]) -> List[ModuleDoc]:
        """合并模块文档草稿
        
        使用大模型分析并合并功能相似的模块，生成更加凝聚的模块组织
        
        Args:
            ctx: 评估上下文对象
            drafts: 模块文档草稿列表
            
        Returns:
            合并后的模块文档列表
        """
        existed_draft_doc = ctx.load_docs(cls.get_draft_filename(ctx), ModuleDoc)
        if len(existed_draft_doc):
            # 如果合并文档已存在，则直接加载使用
            logger.info(f'[ModuleV2Metric] load modules, modules count: {len(existed_draft_doc)}')
            return existed_draft_doc
        # 构建合并提示模板
        prompt = modules_merge_prompt.format(
            module_doc=prefix_with('\n'.join(map(lambda x: x.markdown(), drafts)), '>'))
        # 使用大模型执行合并
        res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt).ask(lambda x: x.replace('---', '').strip())
        # 将文本转换为ModuleDoc对象列表
        docs = ModuleDoc.from_doc(res)
        # 保存模块文档初稿，若模块中只有一个函数，则舍弃（除非只有一个模块）
        docs = list(filter(lambda x: len(docs) == 1 or len(x.functions) > 1, docs))
        for doc in docs:
            ctx.save_doc(cls.get_draft_filename(ctx), doc)
        logger.info(f'[ModuleV2Metric] merge modules: {len(drafts)} -> {len(docs)}')
        return docs
