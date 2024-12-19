from typing import Dict, List

from loguru import logger
from openai import OpenAI

import settings


class SimpleLLM:
    def __init__(self, setting: settings.Setting):
        self._setting = setting
        self._llm = OpenAI(
            api_key=self._setting.chat_completion.openai_api_key.get_secret_value(),
            base_url=self._setting.chat_completion.openai_base_url,
            timeout=self._setting.chat_completion.request_timeout,
            max_retries=5,
        )

    def ask(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = self._llm.chat.completions.create(
                model=self._setting.chat_completion.model,
                messages=messages,
                temperature=self._setting.chat_completion.temperature,
            )
            logger.info(f'chat {response.id}: token usage(prompt {response.usage.prompt_tokens}, response {response.usage.completion_tokens})')
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat call: {e}")
            raise e
