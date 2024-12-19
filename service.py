import json
import os.path
import time
from enum import Enum
from typing import Optional

import requests
from fastapi import FastAPI, BackgroundTasks
from loguru import logger
from pydantic import BaseModel

from file_helper import resolve_archive
from main import run
from settings import SettingsManager

app = FastAPI()
settings = SettingsManager.get_setting()


class APINote(BaseModel):
    clazz: Optional[str]
    name: str
    parameters: Optional[str]
    description: str
    example: Optional[str]


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
    save_path = 'resource/'
    response = requests.get(repo)
    logger.info(f'fetch repo {response.status_code} {len(response.content)}')
    archive = resolve_archive(response.content)
    output_path = archive.decompress(save_path)
    if output_path is None:
        raise Exception('archive is empty')
    return output_path


@app.post('/tools/hcl')
async def hcl(req: RATask, background_tasks: BackgroundTasks) -> RAResult:
    try:
        path = fetch_repo(req.repo)
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
        run(path)
        doc_path = f'docs/{path}'
        data = []
        for f in os.listdir(doc_path):
            if '.prompt.' in f:
                continue
            with open(f'{doc_path}/{f}', 'r') as fr:
                example_start = False
                parameters_start = False
                for line in fr:
                    if line.startswith('### '):
                        line = line[4:].strip().replace('(anonymous namespace)::', '')
                        i = line.rfind('::')
                        if i == -1:
                            name = line
                            clazz = None
                        else:
                            name = line[i + 2:]
                            clazz = line[:i]
                        parameters = None
                        example = None
                        ignore = False
                        continue
                    if line.strip().startswith('**Parameter**'):
                        example_start = False
                        parameters_start = True
                        parameters = ''
                        continue
                    if line.strip().startswith('**Output Example**'):
                        example_start = True
                        parameters_start = False
                        example = ''
                        continue
                    if line.strip().startswith('**Code**'):
                        ignore = True
                        example_start = False
                        parameters_start = False
                        data.append(APINote(clazz=clazz, name=name, parameters=parameters, description=description,
                                            example=example).model_dump(exclude_none=True, exclude_unset=True))
                        continue
                    if parameters_start:
                        parameters += line
                        continue
                    if example_start:
                        example += line
                        continue
                    if not ignore:
                        description = line
        # 回调传结果，重试几次
        retry = 5
        while retry > 0:
            try:
                res = requests.post(req.callback,
                                    data=RAResult(id=req.id,
                                                  status=RAStatus.success.value,
                                                  message='ok',
                                                  result=json.dumps(data)).model_dump_json(exclude_none=True,
                                                                                           exclude_unset=True))
                logger.info(f'callback send, status:{res.status_code}, message:{res.text}')
                break
            except Exception as e:
                logger.error(f'request fail, err={e}')
                time.sleep(1)
    except Exception as e:
        logger.error(f'fail to generate doc for {path}, err={e}')
        requests.post(req.callback, data=RAResult(id=req.id, status=RAStatus.fail.value, message=str(e)))
