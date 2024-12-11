import os

from openai import OpenAI

from log import logger
from prompt import structure_trimmer
from settings import SettingsManager


class ProjectManager:
    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._setting = SettingsManager.get_setting()

        self._llm = OpenAI(
            api_key=self._setting.chat_completion.openai_api_key.get_secret_value(),
            base_url=self._setting.chat_completion.openai_base_url,
            timeout=self._setting.chat_completion.request_timeout,
            max_retries=1,
        )
        self._structure = []
        self._traverse(self._repo_path)
        # self._trim()

    def get_project_structure(self) -> str:
        return '\n'.join(self._structure)

    def _traverse(self, root, prefix=""):
        self._structure.append(prefix + os.path.basename(root))
        new_prefix = prefix + "  "
        for name in sorted(os.listdir(root)):
            if name.startswith("."):  # 忽略隐藏文件和目录
                continue
            path = os.path.join(root, name)
            if os.path.isdir(path):
                self._traverse(path, new_prefix)
            elif os.path.isfile(path) and (
                    path.endswith('.c') or
                    path.endswith('.cpp') or
                    path.endswith('.h')):
                self._structure.append(new_prefix + name)

    def _trim(self):
        messages = [
            {'role': 'system', 'content': structure_trimmer},
            {'role': 'user', 'content': f'[{self._structure}]'}
        ]
        response = self._llm.chat.completions.create(
            model=self._setting.chat_completion.model,
            messages=messages,
            temperature=self._setting.chat_completion.temperature
        )
        logger.debug(response)
        self.structure = response.choices[0].message.content


if __name__ == "__main__":
    project_manager = ProjectManager(repo_path="resource/libxml2-2.9.9")
    print(project_manager.get_project_structure())
