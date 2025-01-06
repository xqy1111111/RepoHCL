import json
import os.path
import time
import uuid
from enum import Enum
from typing import Optional

import requests
from fastapi import FastAPI, BackgroundTasks
from loguru import logger
from pydantic import BaseModel

from doc import APINote, ClassNote, ModuleNote
from file_helper import resolve_archive
from main import run
from settings import SettingsManager

app = FastAPI()
settings = SettingsManager.get_setting()


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
        data = {'functions': [], 'classes': [], 'modules': []}
        for f in os.listdir(doc_path):
            if '.prompt.' in f:
                continue
            with open(f'{doc_path}/{f}', 'r') as fr:
                if '.function.' in f:
                    data['functions'].extend(APINote.from_doc(fr.read()))
                elif '.class.' in f:
                    data['classes'].extend(ClassNote.from_doc(fr.read()))
                elif 'modules.' in f:
                    data['modules'].extend(ModuleNote.from_doc(fr.read()))
        data['functions'] = list(
            map(lambda x: x.model_dump_json(exclude_none=True, exclude_unset=True), data['functions']))
        data['classes'] = list(
            map(lambda x: x.model_dump_json(exclude_none=True, exclude_unset=True), data['classes']))
        data['modules'] = list(
            map(lambda x: x.model_dump_json(exclude_none=True, exclude_unset=True), data['modules']))
        # 回调传结果，重试几次
        retry = 5
        while retry > 0:
            retry -= 1
            try:
                res = requests.post(req.callback,
                                    data=RAResult(id=req.id,
                                                  status=RAStatus.success.value,
                                                  message='ok',
                                                  result=json.dumps(data)).model_dump_json(exclude_none=True,
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


# run_with_response('md5', RATask(id='8', callback='127.0.0.1:8000/tools/callback', repo='1'))
