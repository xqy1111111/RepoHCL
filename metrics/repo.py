import os.path
import re

from loguru import logger

from utils import SimpleLLM, prefix_with, ChatCompletionSettings, ToolsLLM, TaskDispatcher, Task
from utils.settings import ProjectSettings, llm_thread_pool
from .doc import RepoDoc
from .metric import Metric

repo_summarize_prompt = '''
You are a senior software engineer. You have developed a C/C++ software. 
Now you need to write a Github README.md for it to help users understand your software.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> ### README
> #### Description
> A concise paragraph summarizing the software.
> #### Features
> - Feature1
> - Feature2

Please Note:
- #### Features is a list of main features that the software providing to users. Each feature should be described in 1~2 sentences. Don't mention specific function names. Don't make up unverified features. 
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them. 
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format. Don't output descriptions out of the format.

Here is the documentation of main modules of your software. You should refer it to write the README.md:

{modules_doc}
'''

questions_prompt = '''
You are a senior software engineer.

Your aim is to improve a C/C++ software you developed.
In order to find room for improvement in the software, you decide to refer to the focus of excellent software and design some questions to help you improve the software.

The summary of your software is as follows:

{repo_doc}

You'd better consider the following workflow:
1. Refer excellent software. You should find and analyze some widely-used software which provide similar functions to yours as benchmarks. 
2. Check out the concerns. If you're working on XML serialization software, you might find different software supports different protocols like XML 1.0, XPath, and DOM/SAX. Similarly, when focusing on software designed for serialization and deserialization tasks, the format in which data is produced becomes a significant consideration. Protobuf, for example, excels in compressing objects into a binary format for superior compression ratios, whereas JSON offers a human-readable representation with greater ease of manipulation.
3. Ask some questions. You should check that whether your software meets the above concerns so ask some questions to your software first. You may question 'What format is the software product in?'.
4. Check the questions. You should check the questions again and make sure they are meaningful. Specifically, you should provide a basis for these questions by answering how excellent software you have found solve these questions.

The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> - Q1: question 
> - A1: how software X solve the question
> - Q2: question
> - ...

Please Note:
- Strictly follow the above format for output. Don't output any information outside the QA list. 
- Questions should only focus on the functionality of the software, not on performance, documentations, community maintenance, etc. that cannot be obtained from the software source code and documentation.
- Questions are meant to guide you in improving your software, so don’t get away from the field your software work for.

'''

qa_prompt = '''
You are an expert on software engineering. 
You have found a software that meets your requirements. But you still have some questions about the software.
Luckily, the documentation of the software is available with a document query tool.

The software you found is summarized as follows:

{repo_doc}

The software have the following core modules:

{modules_doc}

Please answer the questions based on the documentation of the software.

Please Note:
- When answering a question, you should first draw your conclusion in one sentence.
- Each question should be answered in only one paragraph.
'''

repo_enhance_prompt = '''
You are an expert in software. 
Your task is to read the README documentation of a C++ project and improve it.

The README is as follows:

{repo_doc}

You suspect that there is fraud in this README. 
In order to learn more about the software, you asked the software developer some questions and got answers. 
The questions are as follows.

{qa}

Now you have the confidence to improve this README based on the above QA.

The improved README should keep the same format as before. To ensure the same format, you should follow the standard format in the Markdown reference paragraph below. You do not need to write the reference symbols `>` when you output:

> ### README
> #### Description
> A concise paragraph summarizing the software.
> #### Features
> - Feature1
> - Feature2


Please Note:
- #### Features is a list of main features that the software providing to users. Each feature should be described in 1~2 sentences. Don't mention specific function names. Don't make up unverified features. 
- The Level 4 headings in the format like `#### xxx` are fixed, don't change or translate them. 
- You can revise the content in #### Description and #### Features sections if they are not consistent with the answers to the questions.
- Don't add new Level 3 or Level 4 headings. Do not write anything outside the format. Do not output descriptions of improvements or summary in the end.
'''

# 为仓库生成文档，使用大模型的tool调用能力回答问题，验证文档的准确性
class RepoMetric(Metric):
    def eva(self, ctx):
        existed_repo_doc = ctx.load_repo_doc()
        if existed_repo_doc:
            logger.info(f'[RepoMetric] load repo')
            return
        # 使用模块文档组织上下文
        modules = ctx.load_module_docs()
        logger.info(f'[RepoMetric] gen doc for repo, modules count: {len(modules)}')
        if len(modules) == 0:
            logger.warning(f'[RepoMetric] no module found, cannot generate repo doc')
            return
        modules_doc = '\n\n---\n\n'.join(map(lambda m: m.markdown(), modules))
        prompt = repo_summarize_prompt.format(modules_doc=prefix_with(modules_doc, '> '))
        res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt).ask()
        doc = RepoDoc.from_chapter(res)
        # 保存仓库文档初稿
        if ProjectSettings().is_debug():
            with open(os.path.join(ctx.doc_path, 'repo-draft.md'), 'w') as f:
                f.write(doc.markdown())
        logger.info(f'[RepoMetric] gen doc for repo, doc inited')
        prompt2 = questions_prompt.format(repo_doc=doc.markdown())
        questions_doc = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt2).ask()
        # 保存仓库文档QA
        if ProjectSettings().is_debug():
            with open(os.path.join(ctx.doc_path, 'repo-q.md'), 'w') as f:
                f.write(questions_doc)
        logger.info(f'[RepoMetric] gen doc for repo, questions inited')
        question_pattern = re.compile(r'- Q\d+: (.*?)\n- A\d+: (.*?)(?=\n|\Z)', re.DOTALL)

        questions = list(
            map(lambda x: f'**Question**: {x.group(2)}. {x.group(1)}', question_pattern.finditer(questions_doc)))

        def read_functions_md(name: str):
            return ctx.load_function_doc(name).markdown()

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_functions_md",
                    "description": "Useful when you need to know the details of a function.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "whole name of the Function with arguments and return type",
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        ]
        tools_map = {'read_functions_md': read_functions_md}
        # 回答每个问题
        toolLLM = (ToolsLLM(ChatCompletionSettings(), tools, tools_map)
                   .add_system_msg(qa_prompt.format(repo_doc=prefix_with(doc.markdown(), '> '),
                                                    modules_doc=prefix_with(modules_doc, '> '))))
        questions_with_answer = []

        def answer_qa(i: int, q: str):
            answer = toolLLM.add_user_msg(q).ask()
            questions_with_answer.append(f'- {q}\n > **Answer**: {answer}')
            logger.info(f'[RepoMetric] answer question {i + 1}')

        TaskDispatcher(llm_thread_pool).adds(
            list(map(lambda args: Task(f=answer_qa, args=args), enumerate(questions)))).run()

        qa_doc = '\n'.join(questions_with_answer)
        # 保存仓库文档QA-Answer
        if ProjectSettings().is_debug():
            with open(os.path.join(ctx.doc_path, 'repo-qa.md'), 'w') as f:
                f.write(qa_doc)
        prompt3 = repo_enhance_prompt.format(repo_doc=prefix_with(doc.markdown(), '> '), qa=prefix_with(qa_doc, '> '))
        res = SimpleLLM(ChatCompletionSettings()).add_user_msg(prompt3).ask()
        doc = RepoDoc.from_chapter(res)
        ctx.save_repo_doc(doc)
        logger.info(f'[RepoMetric] gen doc for repo, doc saved')
