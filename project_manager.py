import os

from llm_helper import SimpleLLM
from prompt import structure_trimmer
from settings import SettingsManager


class ProjectManager:
    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._setting = SettingsManager.get_setting()
        self._llm = SimpleLLM(self._setting)
        self._structure = self._traverse(self._repo_path)
        self._trim()

    def get_project_structure(self) -> str:
        return self._structure

    # 递归遍历目录结构
    def _traverse(self, root, prefix="") -> [str]:
        children = []
        new_prefix = prefix + ' ' * 2
        for name in sorted(os.listdir(root)):
            if name.startswith('.'):  # 忽略隐藏文件和目录
                continue
            path = os.path.join(root, name)
            if os.path.isdir(path):
                children.extend(self._traverse(path, new_prefix))
            elif os.path.isfile(path) and (
                    path.endswith('.c') or
                    path.endswith('.cpp') or
                    path.endswith('.h') or
                    path.endswith('.hpp')):
                children.append(new_prefix + name)
        if len(children) > 0:
            children = [prefix + os.path.basename(root), *children]
        return children

    # 委托LLM精简目录结构，排除文档、测试类型的代码文件
    def _trim(self):
        messages = [
            {'role': 'system', 'content': structure_trimmer},
            {'role': 'user', 'content': f'['
                                        f'{self._structure}'
                                        f']'}
        ]
        self._structure = self._llm.ask(messages)


if __name__ == "__main__":
    project_manager = ProjectManager(repo_path="resource/libxml2-2.9.9")
    print(project_manager.get_project_structure())
