import json
import shutil
import time
import uuid
from enum import Enum
from typing import Optional

import requests
from fastapi import FastAPI, BackgroundTasks
from loguru import logger
from pydantic import BaseModel

from main import eva
from metrics import EvaContext
from utils import resolve_archive

app = FastAPI()


class RATask(BaseModel):
    id: str  # ID
    repo: str  # 仓库OSS地址
    callback: str  # 回调URL


class RAStatus(Enum):
    received = 0
    success = 1
    fail = 2


class RAResult(BaseModel):
    id: str
    status: int
    message: str = ''
    score: Optional[int] = None
    result: Optional[str] = None


def fetch_repo(repo: str) -> str:
    save_path = uuid.uuid4().hex
    response = requests.get(repo)
    if response.status_code == 403:
        raise Exception(response.text)
    logger.info(f'fetch repo {response.status_code} {len(response.content)}')
    archive = resolve_archive(response.content)
    archive.decompress(f'resource/{save_path}')
    return save_path


@app.post('/tools/hcl')
async def hcl(req: RATask, background_tasks: BackgroundTasks) -> RAResult:
    try:
        # path = fetch_repo(req.repo)
        path = 'md5'
        logger.info(f'fetch repo {req.repo} to {path}')
    except Exception as e:
        logger.error(f'fail to get `{req.repo}`, err={e}')
        return RAResult(id=req.id, status=RAStatus.fail.value, message=str(e))
    background_tasks.add_task(run_with_response, path=path, req=req)
    return RAResult(id=req.id, status=RAStatus.received.value, message='task received')


@app.post('/tools/callback')
def test(req: RAResult):
    logger.info(req.model_dump_json())
    return 'ok'


@app.get('/tools/test')
def test2():
    print('hello')
    return 'hello'


def run_with_response(path: str, req: RATask):
    try:
        ctx = EvaContext(doc_path=f'docs/{path}', resource_path=f'resource/{path}', output_path=f'output/{path}')
        eva(ctx)
        data = {
            'functions': list(map(lambda x: ctx.load_function_doc(x).model_dump(), ctx.function_map.keys())),
            'classes': list(map(lambda x: ctx.load_clazz_doc(x).model_dump(), ctx.clazz_map.keys())),
            'modules': list(map(lambda x: x.model_dump(), ctx.load_module_docs())),
            'repo': [ctx.load_repo_doc().model_dump()]
        }
        # 回调传结果，重试几次
        retry = 5
        while retry > 0:
            retry -= 1
            try:
                res = requests.post(req.callback,
                                    data=RAResult(id=req.id,
                                                  status=RAStatus.success.value,
                                                  message='ok',
                                                  result=json.dumps(data, ensure_ascii=False)).model_dump_json(exclude_none=True,
                                                                                           exclude_unset=True),
                                    headers={'Content-Type': 'application/json'})
                logger.info(f'callback send, status:{res.status_code}, message:{res.text}')
                break
            except Exception as e:
                logger.error(f'request fail, err={e}')
                time.sleep(1)
    except Exception as e:
        logger.error(f'fail to generate doc for {path}, err={e}')
        requests.post(req.callback,
                      data=RAResult(id=req.id, status=RAStatus.fail.value, message=str(e)).model_dump_json(
                          exclude_none=True, exclude_unset=True),
                      headers={'Content-Type': 'application/json'})
    # 清扫工作路径
    # shutil.rmtree(f'resource/{path}')
    # shutil.rmtree(f'output/{path}')
    # shutil.rmtree(f'docs/{path}')

# run_with_response('md5', RATask(id='8', callback='127.0.0.1:8000/tools/callback', repo='1'))
