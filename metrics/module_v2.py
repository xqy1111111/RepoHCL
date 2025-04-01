from functools import reduce
from typing import List

from loguru import logger

from utils import SimpleLLM, prefix_with, ChatCompletionSettings, SimpleRAG, RagSettings
from . import ModuleMetric
from .doc import ModuleDoc
from .metric import Symbol, EvaContext

modules_prompt = '''
You are an expert in software architecture analysis. 
Your task is to review function descriptions from a C++ code repository and organize them into one or more functional module based on their purpose and interrelations. 

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
'''

modules_merge_prompt = '''
You are an expert in software architecture analysis.
You have reviewed the function descriptions from a C++ code repository and organized them into functional modules based on their purpose and interrelations.
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

'''

# V2本质上是先分解再合并，分解时使用聚类算法，合并时使用大模型。V2的效果并不比V1更好，但减少了上下文量。当具备1000个API时，V1的上下文量达到64+K。V2的上下文量则在10K以内。
class ModuleV2Metric(ModuleMetric):
    _v2_draft: str = 'modules-v2-draft.md'

    def eva(self, ctx):
        # 使用聚类算法初步划分模块，并由大模型总结模块文档
        self._draft(ctx)
        # 由大模型合并模块文档
        self._merge(ctx)
        # 由大模型增强模块文档
        self._enhance(ctx)

    def _draft(self, ctx):
        existed_modules_doc = ctx.load_docs(f'{ctx.doc_path}/{self._v2_draft}', ModuleDoc)
        if len(existed_modules_doc):
            logger.info(f'[FunctionMetric] load module drafts, modules count: {len(existed_modules_doc)}')
            return
        # 提取所有用户可见的函数
        apis: List[Symbol] = list(filter(lambda x: ctx.function_map.get(x).visible
                                                   and ctx.function_map.get(x).declFile.endswith('.h'),
                                         ctx.function_map.keys()))
        if len(apis) == 0:
            logger.warning(f'[ModuleV2Metric] no apis found, cannot generate modules docs')
            return
        logger.info(f'[ModuleV2Metric] gen draft for modules, apis count: {len(apis)}')
        rag = SimpleRAG(RagSettings())
        logger.info('[ModuleV2Metric] clustering...')
        cluster = rag.kmeans(
            list(map(lambda x: x.name + ': ' + x.description, map(lambda x: ctx.load_function_doc(x), apis))))
        logger.info(f'[ModuleV2Metric] cluster to {len(cluster)} groups')
        i = 1
        for g in cluster:
            # 使用函数描述组织上下文
            api_docs = reduce(lambda x, y: x + y,
                              map(lambda x: f'- {apis[x].base}\n > {ctx.load_function_doc(apis[x]).description}\n\n',
                                  g))
            prompt2 = modules_prompt.format(api_doc=prefix_with(api_docs, '>'))
            # 生成模块文档
            res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt2).ask(lambda x: x.replace('---', '').strip())
            docs = ModuleDoc.from_doc(res)
            # 保存模块文档
            for doc in docs:
                ctx.save_doc(f'{ctx.doc_path}/{self._v2_draft}', doc)
                logger.info(f'[ModuleV2Metric] gen draft for module {i}: {doc.name}')
                i += 1

    def _merge(self, ctx: EvaContext):
        existed_modules_doc = ctx.load_docs(f'{ctx.doc_path}/{self._v1_draft}', ModuleDoc)
        if len(existed_modules_doc):
            logger.info(f'[ModuleV2Metric] load modules, modules count: {len(existed_modules_doc)}')
            return
        drafts = ctx.load_docs(f'{ctx.doc_path}/modules-v2-draft.md', ModuleDoc)
        if len(drafts) == 0:
            return
        prompt = modules_merge_prompt.format(
            module_doc=prefix_with('\n'.join(map(lambda x: x.markdown(), drafts)), '>'))
        res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt).ask(lambda x: x.replace('---', '').strip())
        docs = ModuleDoc.from_doc(res)
        for doc in docs:
            ctx.save_doc(f'{ctx.doc_path}/{self._v1_draft}', doc)
        logger.info(f'[ModuleV2Metric] merge modules: {len(drafts)} -> {len(docs)}')
