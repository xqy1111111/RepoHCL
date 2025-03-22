import json
from typing import Callable

from loguru import logger
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk

from .settings import ProjectSettings, ChatCompletionSettings


class SimpleLLM:
    def __init__(self, setting: ChatCompletionSettings):
        self._setting = setting
        self._llm = OpenAI(
            api_key=self._setting.openai_api_key,
            base_url=self._setting.openai_base_url,
            timeout=self._setting.request_timeout,
            max_retries=5,
        )
        self._history = []

    def add_system_msg(self, content: str):
        self._history.append({'role': 'system', 'content': content})
        return self

    def add_user_msg(self, content: str):
        self._history.append({'role': 'user', 'content': content})
        return self

    def _add_response(self, content: str):
        self._history.append({'role': 'assistant', 'content': content})
        return self

    def _add_language_msg(self):
        self.add_user_msg(f'You must output in {self._setting.language} though the prompt is written in English.'
                          "You can write with some English words in the analysis and description "
                          "to enhance the document's readability because you do not need to translate the function name or variable name into the target language.\n")

    def ask(self, post_processor: Callable[[str], str] = None) -> str:
        try:
            self._add_language_msg()
            response = self._llm.chat.completions.create(
                model=self._setting.model,
                messages=self._history,
                temperature=self._setting.temperature,
                stream=True
            )
            res = self._get_stream_response(response)
            if post_processor:
                res = post_processor(res)
            self._add_response(res)
            return res
        except Exception as e:
            logger.error(f"[SimpleLLM] Error in chat call: {e}")
            raise e

    def _get_stream_response(self, response: Stream[ChatCompletionChunk]) -> str:
        is_thinking = False
        answer_content = ''
        for chunk in response:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                if not ProjectSettings().is_debug():
                    continue
                # 打印思考过程
                if not is_thinking:
                    print('=' * 10 + 'thinking' + '=' * 10)
                    is_thinking = True
                print(delta.reasoning_content, end='', flush=True)
            else:
                answer_content += delta.content
                if not ProjectSettings().is_debug():
                    continue
                # 打印回复过程
                if is_thinking:
                    print('\n' + '=' * 10 + 'answering' + '=' * 10)
                    is_thinking = False
                print(delta.content, end='', flush=True)

        if ProjectSettings().is_debug():
            print()
            with open('prompt.md', 'a') as d:
                d.write('\n'.join(list(map(lambda s: s.get('content'), self._history))) + '\n\n---\n\n')
        return answer_content

    def add_file(self, path: str):
        try:
            # TODO file-extract 可能是qwen-long专用
            response = self._llm.files.create(file=open(path, 'rb'), purpose='file-extract')
            self.add_system_msg(f'fileid://{response.id}')
            return self
        except Exception as e:
            logger.error(f"[SimpleLLM] Error in add file: {e}")
            raise e


class ToolsLLM(SimpleLLM):
    def __init__(self, setting: ChatCompletionSettings, tools, tools_map):
        self._tools = tools
        self._toolsMap = tools_map
        super().__init__(setting)

    def ask(self, post_processor: Callable[[str], str] = None) -> str:
        try:
            response = self._llm.chat.completions.create(
                model=self._setting.model,
                messages=self._history,
                temperature=self._setting.temperature,
                tools=self._tools
            )
            logger.info(
                f'[ToolsLLM] chat {response.id}: token usage(prompt {response.usage.prompt_tokens}, response {response.usage.completion_tokens})')
            if response.choices[0].message.tool_calls:
                logger.info(f'[ToolsLLM] chat {response.id}: tool call{response.choices[0].message.tool_calls}')
                for tool_call in response.choices[0].message.tool_calls:
                    self._history.append(response.choices[0].message)
                    f = self._toolsMap.get(tool_call.function.name)
                    arguments = json.loads(tool_call.function.arguments)
                    r = f(**arguments)
                    self._history.append({'role': 'tool', 'content': r})
                    logger.info(
                        f"[ToolsLLM] chat {response.id}: tool call(name {f}, arguments {arguments}), result {r}")
                return self.ask()
            res = response.choices[0].message.content
            if post_processor:
                res = post_processor(res)
            self._add_response(res)
            return res
        except Exception as e:
            logger.error(f"[ToolsLLM] Error in chat call: {e}")
            raise e

    def debug(self) -> str:
        raise NotImplementedError
