from loguru import logger

from utils import SimpleLLM, ChatCompletionSettings, prefix_with
from .metric import Metric

prompt = '''
You are a software expert and you find a C++ software with good functions documentation.

You need to sort through these functions and figure out which ones are provided to users and which ones are used by developers themselves.

The following will provide you with the documentation of each function in the software in turn. 

If you think it is a function that the user can use, output 1, otherwise output 0.

Please note:
- Only output 1 or 0, and don't explain the reason.

'''

class APIMetric(Metric):
    def eva(self, ctx):
        functions = ctx.function_map
        apis = []
        llm = SimpleLLM(ChatCompletionSettings()).add_system_msg(prompt)
        for s in functions.keys():
            doc = ctx.load_function_doc(s)
            res = llm.add_user_msg(prefix_with(doc.markdown(), '> ')).ask(lambda x: x.strip().splitlines()[0])
            logger.info(f'[APIMetric] check {s.base} is api? {res}')
            if res == '1':
                apis.append(s)
        logger.info(f'[APIMetric] find {len(apis)}/{len(functions)} apis')