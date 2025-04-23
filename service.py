import os.path  # 导入os.path模块，用于处理文件路径
import time  # 导入time模块，用于处理时间相关操作
import uuid  # 导入uuid模块，用于生成唯一标识符
from enum import Enum  # 导入Enum类，用于创建枚举类型
from typing import Optional, List, Dict  # 导入类型提示工具

import requests  # 导入requests库，用于发送HTTP请求
from fastapi import FastAPI, BackgroundTasks  # 导入FastAPI框架和后台任务功能
from loguru import logger  # 导入loguru库的logger，用于日志记录
from pydantic import BaseModel  # 导入pydantic的BaseModel，用于数据验证和序列化

from main import eva  # 导入主模块中的eva函数
from metrics import EvaContext, ModuleDoc, RepoDoc  # 导入度量分析相关类
from utils import resolve_archive, prefix_with, SimpleLLM, ChatCompletionSettings, LangEnum  # 导入工具函数和类

app = FastAPI()  # 创建FastAPI应用实例


class RATask(BaseModel):
    """
    仓库分析任务模型，定义了分析任务的参数
    """
    id: str  # ID
    repo: str  # 仓库OSS地址
    callback: str  # 回调URL
    language: str = LangEnum.cpp.render  # 语言，默认为C++


class RAStatus(Enum):
    """
    仓库分析状态枚举类，表示任务的不同状态
    """
    received = 0  # 任务已接收
    success = 1  # 任务成功完成
    fail = 2  # 任务失败


class RAResult(BaseModel):
    """
    仓库分析结果模型，用于返回分析结果
    """
    id: str  # 任务ID
    status: int  # 任务状态码
    message: str = ''  # 状态消息
    score: Optional[int] = None  # 可选的分数
    result: Optional[str] = None  # 可选的结果数据


class EvaResult(BaseModel):
    """
    评估结果模型，包含各种分析结果的集合
    """
    functions: List[Dict]  # 函数分析结果列表
    classes: List[Dict]  # 类分析结果列表
    modules: List[Dict]  # 模块分析结果列表
    repo: List[Dict]  # 仓库分析结果列表


def fetch_repo(repo: str) -> str:
    """
    获取远程代码仓库并解压到本地
    
    Args:
        repo: 仓库URL地址
        
    Returns:
        str: 保存路径的唯一标识符
        
    Raises:
        Exception: 请求失败时抛出异常
    """
    save_path = uuid.uuid4().hex  # 生成唯一的保存路径
    response = requests.get(repo)  # 发送GET请求获取仓库内容
    if response.status_code == 403:  # 如果返回403禁止访问
        raise Exception(response.text)  # 抛出异常
    logger.info(f'fetch repo {response.status_code} {len(response.content)}')  # 记录请求状态和内容长度
    archive = resolve_archive(response.content)  # 解析归档文件
    archive.decompress(os.path.join('resource', save_path))  # 解压到指定目录
    return save_path  # 返回保存路径


@app.post('/tools/hcl')
async def hcl(req: RATask, background_tasks: BackgroundTasks) -> RAResult:
    """
    代码仓库分析API接口，接收分析请求并在后台执行分析任务
    
    Args:
        req: RATask对象，包含任务参数
        background_tasks: FastAPI的后台任务对象
        
    Returns:
        RAResult: 包含任务状态的结果对象
    """
    logger.info(f'hcl, req={req}')  # 记录请求信息
    try:
        path = fetch_repo(req.repo)  # 获取并解压仓库
        # path = 'md5'
        logger.info(f'fetch repo {req.repo} to {path}')  # 记录仓库获取结果
    except Exception as e:  # 捕获异常
        logger.error(f'fail to get `{req.repo}`, err={e}')  # 记录错误
        return RAResult(id=req.id, status=RAStatus.fail.value, message=str(e))  # 返回失败结果
    background_tasks.add_task(run_with_response, path=path, req=req)  # 添加后台任务
    return RAResult(id=req.id, status=RAStatus.received.value, message='task received')  # 返回任务已接收状态


@app.post('/tools/callback')
def test(req: RAResult):
    """
    回调测试接口，用于测试回调功能
    
    Args:
        req: RAResult对象
        
    Returns:
        str: 确认信息
    """
    logger.info(req.model_dump_json())  # 记录请求的JSON表示
    return 'ok'  # 返回确认信息


@app.get('/tools/test')
def test2():
    """
    简单的测试接口
    
    Returns:
        str: 测试信息
    """
    print('hello')  # 打印问候信息
    return 'hello'  # 返回问候信息


def requests_with_retry(url: str, content: str, retry: int = 5):
    """
    发送HTTP请求并支持重试机制
    
    Args:
        url: 请求URL
        content: 请求内容
        retry: 重试次数，默认为5
        
    Raises:
        Exception: 所有重试都失败后抛出异常
    """
    err = None  # 初始化错误变量
    while retry > 0:  # 当还有重试次数时循环
        retry -= 1  # 减少重试次数
        try:
            res = requests.post(url,
                                data=content,
                                headers={'Content-Type': 'application/json'})  # 发送POST请求
            logger.info(f'requests send, status:{res.status_code}, message:{res.text}')  # 记录请求结果
            return  # 成功则返回
        except Exception as e:  # 捕获异常
            err = e  # 记录错误
            logger.error(f'request fail, err={e}')  # 记录错误信息
            time.sleep(1)  # 等待1秒后重试
    raise Exception(f'Request Failed, err={err}')  # 所有重试失败后抛出异常


def run_with_response(path: str, req: RATask):
    """
    执行仓库分析并发送回调响应
    
    Args:
        path: 仓库路径
        req: 任务请求对象
    """
    try:
        lang = LangEnum.from_render(req.language)  # 从请求获取语言类型
        ctx = EvaContext(doc_path=os.path.join('docs', path), resource_path=os.path.join('resource', path),
                         output_path=os.path.join('output', path), lang=lang)  # 创建评估上下文
        eva(ctx, lang)  # 执行评估
        data = EvaResult(functions=list(map(lambda x: ctx.load_function_doc(x.symbol).model_dump(), filter(lambda x: x.visible, ctx.func_iter()))),
                         classes=list(map(lambda x: ctx.load_clazz_doc(x.symbol).model_dump(), filter(lambda x: x.visible, ctx.clazz_iter()))),
                         modules=list(map(lambda x: x.model_dump(), ctx.load_module_docs())),
                         repo=[ctx.load_repo_doc().model_dump()])  # 构建评估结果数据

        # 回调传结果，重试几次
        requests_with_retry(req.callback,
                            content=RAResult(id=req.id,
                                             status=RAStatus.success.value,
                                             message='ok',
                                             result=data.model_dump_json())
                            .model_dump_json(exclude_none=True, exclude_unset=True))  # 发送成功回调
    except Exception as e:  # 捕获异常
        logger.error(f'fail to generate doc for {path}, err={e}')  # 记录错误
        requests_with_retry(req.callback,
                            content=RAResult(id=req.id, status=RAStatus.fail.value, message=str(e)).model_dump_json(
                                exclude_none=True, exclude_unset=True))  # 发送失败回调
    # 清扫工作路径
    # shutil.rmtree(f'resource/{path}')
    # shutil.rmtree(f'output/{path}')
    # shutil.rmtree(f'docs/{path}')


# run_with_response('md5', RATask(id='8', callback='127.0.0.1:8000/tools/callback', repo='1'))

class CompReq(BaseModel):
    """
    比较请求模型，用于软件比较功能
    """
    results: List[str]  # 结果列表
    requestId: str  # 请求ID
    callback: str  # 回调URL


class CompResult(BaseModel):
    """
    比较结果模型，用于返回软件比较的结果
    """
    requestId: str  # 请求ID
    status: int  # 状态码
    message: str  # 状态消息
    result: Optional[str] = None  # 可选的比较结果


class CompareMetric:
    """
    比较度量类，用于比较不同软件的功能和特性
    """
    _prompt = '''
You are an expert in software development.
Below are multiple software with similar functions. 
They may have different solutions to the same problem, for example, zip and tar are different methods for decompression.
They may be old and latest versions of the same software and therefore differ in capabilities.

Your task is to distinguish the similarities and differences between the functions of the software and tell me which should be used in which scenarios.

{software}

Please compare the two software and write a comparison report with the help of a table
The standard format is in the Markdown reference paragraph below, and you do not need to write the reference symbols `>` when you output:

> | FEATURE POINTS | Software 1 | Software 2 | ... |
> | ---- | ---- | ---- | ... |
> | point1 | How Software 1 perform on point1 | How Software 2 perform on point1 | ... |
> | point2 | **How Software 1 perform on point2** | How Software 2 perform on point2 | ... |
> | point3 | How Software 1 perform on point3 | X  | ... |
> | point4 | X | How Software 2 perform on point4 | ... |
> | ... | ... | ... | ... |
>
> Summary
> - Software 1 is better because ...
> - Software 2 should be used in XXX scenarios because ...
> ...

You'd better consider the following workflow:
1. Understand the Software. Read through the documents of each software to understand their core functionalities.
2. Summarize the Feature Points. Identify the key feature points of each software from the modules documentation.
3. Find the same Feature Points. Compare the performance of the same Feature Points in the two software. 
4. Find the different Feature Points. Identify the Feature Points that only one software has.
5. Write a Summary. Summarize the comparison and give your suggestions.

Please Note:
- For a feature point, if one software performs better, use **bold** to highlight its performance.
- For a feature point, if one of the software doesn't show the feature point, output X.
- Give a summary of the comparison behind the table showing which software is better and why. 
- Don't mention all the functions the software have, summarize the most important ones.
'''  # 比较提示模板，指导LLM如何进行软件比较

    @staticmethod
    def _sprompt(ctx: EvaResult):
        """
        生成软件比较的提示内容
        
        Args:
            ctx: 评估结果对象
            
        Returns:
            str: 格式化的提示内容
        """
        s = ''
        if len(ctx.repo):  # 如果有仓库数据
            r = ctx.repo[0]
            r['features'] = list(map(lambda x: x.strip('- '), r['features'].splitlines()))  # 处理特性列表
            r['standards'] = list(map(lambda x: x.strip('- '), r['standards'].splitlines()))  # 处理标准列表
            r['scenarios'] = list(map(lambda x: x.strip('- '), r['scenarios'].splitlines()))  # 处理场景列表
            s = RepoDoc.model_validate(r).markdown() + '\n'  # 转换为Markdown格式
        for m in ctx.modules:  # 遍历模块
            m['functions'] = list(map(lambda x: x.strip('- '), m['functions'].splitlines()))  # 处理函数列表
            m = ModuleDoc.model_validate(m)  # 验证模块文档
            m.example = None  # 清除示例
            m.functions = []  # 清除函数列表
            s += m.markdown() + '\n'  # 添加模块Markdown
        return s  # 返回格式化内容

    def eva(self, results: List[EvaResult]) -> str:
        """
        执行软件比较评估
        
        Args:
            results: 评估结果列表
            
        Returns:
            str: 比较结果
        """
        s = ''
        for i, r in enumerate(results):  # 遍历结果列表
            s += f'## Software {i + 1}\n'  # 添加软件标题
            s += self._sprompt(r)  # 添加软件提示内容
            s += '---'  # 添加分隔线
        p = self._prompt.format(software=prefix_with(s, '> '))  # 格式化完整提示
        llm = SimpleLLM(ChatCompletionSettings())  # 创建LLM客户端
        res = llm.add_user_msg(p).ask()  # 发送提示并获取响应
        with open('compare.md', 'w') as f:  # 保存比较结果
            f.write(res)
        return res  # 返回比较结果


@app.post('/tools/comp')
async def comp(req: CompReq, background_tasks: BackgroundTasks) -> CompResult:
    """
    软件比较API接口，接收比较请求并在后台执行比较任务
    
    Args:
        req: 比较请求对象
        background_tasks: 后台任务对象
        
    Returns:
        CompResult: 比较结果对象
    """
    background_tasks.add_task(do_comp, req=req)  # 添加比较任务到后台
    return CompResult(requestId=req.requestId, status=RAStatus.received.value, message='task received')  # 返回任务已接收状态


def do_comp(req: CompReq):
    """
    执行软件比较任务并发送回调
    
    Args:
        req: 比较请求对象
    """
    try:
        res = CompareMetric().eva(list(map(lambda x: EvaResult.model_validate_json(x), req.results)))  # 执行比较
        requests_with_retry(url=req.callback, content=CompResult(requestId=req.requestId, result=res, message='ok',
                                                                 status=RAStatus.success.value).model_dump_json())  # 发送成功回调
    except Exception as e:  # 捕获异常
        logger.error(f'fail to compare doc for {req.requestId}, err={e}')  # 记录错误
        requests_with_retry(req.callback, content=CompResult(requestId=req.requestId, result=None, message=str(e),
                                                             status=RAStatus.fail.value).model_dump_json())  # 发送失败回调
