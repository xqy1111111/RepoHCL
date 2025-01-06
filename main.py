import json
import os.path
import re
import shutil
import subprocess
import threading
from collections import defaultdict
from itertools import islice
from typing import Dict, Set, List

import click
import networkx as nx
import pydot
from loguru import logger

from ast_generator import gen_sh
from chat_engine import ClassEngine, FunctionEngine
from doc import FunctionItem, DocItem, ClassItem, ModuleNote
from llm_helper import SimpleLLM
from project_manager import ProjectManager
from prompt import modules_summarize_prompt, modules_enhance_prompt
from settings import SettingsManager


# 编译项目，生成中间文件（函数列表、调用图）
def make(path: str, output: str):
    def cmd(command: str, path: str = path):
        subprocess.run(command, shell=True, cwd=path)
        logger.info('command executed: ' + command)

    os.environ['CC'] = 'clang-9'
    os.environ['CXX'] = 'clang++-9'
    # 生成makefile文件
    logger.info(f'{path} content:{str(os.listdir(path))}')
    if os.path.exists(f'{path}/configure'):
        cmd('./configure')
    elif os.path.exists(f'{path}/CMakeLists.txt'):
        cmd('cmake -DCMAKE_BUILD_TYPE=Release -DLLVM_PREFIX=/lib/llvm-9 .')
    if not os.path.exists(f'{path}/Makefile'):
        raise Exception('Makefile not found in root')
    # 基于makefile生成compile_commands.json
    cmd('bear make -j`nproc`')
    gen_sh(path)
    cmd('chmod +x buildast.sh')
    cmd('./buildast.sh')
    cmd(f'lib/cge {path}/astList.txt', path='.')
    os.makedirs(output, exist_ok=True)
    shutil.move('functions.json', output)
    shutil.move('records.json', output)
    shutil.move('cg.dot', output)


# 读取函数列表
def read_functions(path: str, resource_path: str) -> Dict[str, Dict]:
    # 调整functions.json
    with open(f'{path}/functions.json', 'r') as f:
        functions = json.loads(f.read())
        to_remove = []
        for k, v in functions.items():
            file: str = v.get('filename')
            # 不是绝对路径说明已经处理过了，跳过
            if not file.startswith('/'):
                continue
            # 仅保留resource下的文件
            i = file.find(resource_path)
            if i == -1:
                to_remove.append(k)
                continue
            v['filename'] = file[i + len(resource_path) + 1:]
            # file = file.replace('/root/', '')
            with open(file, 'r') as code:
                lines = list(islice(code, int(v.get('beginLine')) - 1, int(v.get('endLine'))))
                v.setdefault('code', ''.join(lines).strip())
        for k in to_remove:
            del functions[k]
    with open(f'{path}/functions.json', 'w') as f:
        f.write(json.dumps(functions, indent=4))
    return functions


# 读取类列表
def read_records(path: str, resource_path: str) -> Dict[str, Dict]:
    functions = read_functions(path, resource_path)
    with open(f'{path}/records.json', 'r') as f:
        records = json.loads(f.read())
        to_remove = []
        for k, v in records.items():
            file = v.get('filename')
            # 不是绝对路径说明已经处理过了，跳过
            if not file.startswith('/'):
                continue
            # 仅保留resource下的文件
            # 仅保留resource下的文件
            i = file.find(resource_path)
            if i == -1:
                to_remove.append(k)
                continue
            v['filename'] = file[i + len(resource_path):]
            # file = file.replace('/root/', '')
            # 查找类的方法对应的实现
            methods = []
            for m in v['methods']:
                m_name = m['name']
                # 忽略没有实现的方法
                if m_name not in functions:
                    logger.warning(f'class methods not found {m_name}')
                    continue
                m['filename'] = functions[m_name]['filename']
                methods.append(m)
            v['methods'] = methods
        for k in to_remove:
            del records[k]

    with open(f'{path}/records.json', 'w') as f:
        f.write(json.dumps(records, indent=4))
    return records


# 筛选外部可见的函数
def read_extern_functions(path: str, resource_path: str) -> Dict[str, Dict]:
    functions = read_functions(path, resource_path)
    to_analyze = set(functions.keys())
    # callgraph = read_callgraph(path, to_analyze)
    # zero_indegree_nodes = set(node for node in callgraph.nodes if callgraph.in_degree[node] == 0)
    extern_functions = {}
    for k, v in functions.items():
        if bool(v.get('visible')):
            extern_functions[k] = v
    return extern_functions


# 读取调用图
def read_callgraph(path: str, nodes: Set[str] = None) -> nx.DiGraph:
    if nodes is None:
        nodes = {}
    # 解析.dot转为DiGraph
    (dot,) = pydot.graph_from_dot_file(f'{path}/cg.dot')
    digraph = nx.DiGraph()
    name_map = {}
    # 添加节点
    for node in dot.get_nodes():
        if isinstance(node, pydot.Node):
            label = node.get('label')[1:-1]
            name_map[node.get_name()] = label
            if label in nodes:
                digraph.add_node(label)

    # 添加边
    for edge in dot.get_edges():
        source = name_map[edge.get_source()]
        destination = name_map[edge.get_destination()]
        if source in nodes and destination in nodes:
            digraph.add_edge(source, destination)

    # 去除环
    def remove_cycles(g: nx.DiGraph):
        while not nx.is_directed_acyclic_graph(g):
            cycle = list(nx.find_cycle(g))
            edge_to_remove = cycle[0]
            logger.debug(f'remove {edge_to_remove}')
            g.remove_edge(*edge_to_remove)

    remove_cycles(digraph)

    return digraph


def response_with_gitbook(doc_path):
    summary = '# Summary\n'
    for root, _, files in os.walk(doc_path):
        root = root[len(doc_path) + 1:]
        if len(root) > 0:
            summary += f'{(len(root.split("/")) - 1) * "  "}* [{root}]\n'
        for f in files:
            if '.prompt' not in f:
                if len(root) > 0:
                    summary += f'{len(root.split("/")) * "  "}* [{f[:-3]}]({root}/{f})\n'
                else:
                    summary += f'* [{f[:-3]}]({f})\n'
    with open(f'{doc_path}/SUMMARY.md', 'w') as f:
        f.write(summary)
    with open(f'{doc_path}/README.md', 'w') as f:
        f.write(f'### {os.path.basename(doc_path)}\n')


threadlocal = threading.local()


def get_doc_manager() -> Dict[str, DocItem]:
    if not hasattr(threadlocal, 'doc_manager'):
        threadlocal.doc_manager = {}
    return threadlocal.doc_manager


# 为函数生成文档
def gen_doc_for_functions(output_path: str, resource_path: str, doc_path: str):
    functions = read_functions(output_path, resource_path)
    to_analyze = set(functions.keys())
    callgraph = read_callgraph(output_path, to_analyze)
    # 拓扑排序callgraph，排除不需要分析的函数
    sorted_functions = list(reversed(list(nx.topological_sort(callgraph))))
    logger.info(f'gen doc for functions, functions count: {len(sorted_functions)}')
    ce = FunctionEngine(ProjectManager(repo_path=resource_path))
    doc_manager = get_doc_manager()
    # 生成文档
    for i in range(len(sorted_functions)):
        f = sorted_functions[i]
        doc_item = FunctionItem()
        doc_item.name = f
        if f not in to_analyze:
            continue
        doc_item.code = functions.get(f).get('code')
        doc_item.file = functions.get(f).get('filename')
        doc_item.has_return = True
        doc_item.who_reference_me = list(
            filter(lambda s: s is not None, map(lambda s: doc_manager[s] if s in doc_manager else None,
                                                callgraph.predecessors(f))))
        doc_item.reference_who = list(
            filter(lambda s: s is not None, map(lambda s: doc_manager[s] if s in doc_manager else None,
                                                callgraph.successors(f))))
        if not doc_item.imports(doc_path):
            doc_item.md_content = ce.generate_doc(doc_item)
            # 文档生成失败，先跳过
            if doc_item.md_content is None:
                continue
            doc_item.exports(doc_path)
            logger.info(f'parse {doc_item.name}: {i + 1}/{len(sorted_functions)}')
        else:
            logger.info(f'load {doc_item.name}: {i + 1}/{len(sorted_functions)}')
        doc_manager[f] = doc_item
    # 生成gitbook所需文档
    response_with_gitbook(doc_path)
    # 后置清理
    del threadlocal.doc_manager


def spelling_name(fullname: str) -> str:
    k = fullname.find('(')
    if k == -1:
        k = len(fullname)
    i = fullname.rfind('::', 0, k)
    if i != -1:
        fullname = fullname[i + 2:]
    return fullname


def _simplify_functions_md(content: str) -> str:
    return re.search(r'###.*?\n(.*?)\n', content, re.DOTALL).group(1)


# 为类生成文档
def gen_doc_for_classes(output_path: str, resource_path: str, doc_path: str):
    records = read_records(output_path, resource_path)
    logger.info(f'gen doc for classes, class count: {len(records)}')
    ce = ClassEngine(ProjectManager(repo_path=resource_path))
    i = 0
    for clazz, v in records.items():
        clazz_item = ClassItem()
        name = spelling_name(clazz)
        clazz_item.code = 'class ' + name + ' {\n'
        clazz_item.name = clazz
        clazz_item.file = v.get('filename')
        clazz_item.reference_who = []

        def _group_by_access(vs: List[Dict]) -> Dict[str, List[Dict]]:
            res = defaultdict(list)
            for v in vs:
                res[v.get('access')].append(v)
            return res

        methods = _group_by_access(v.get('methods'))
        fields = _group_by_access(v.get('fields'))

        def _load(access: str):
            fs = fields.get(access, [])
            ms = methods.get(access, [])
            if len(fs) == 0 and len(ms) == 0:
                return
            if len(fs):
                clazz_item.has_attrs = True
            clazz_item.code += f'{access}:\n'
            # 根据类的成员变量拼接类的代码
            for f in fs:
                clazz_item.code += f'  ' + f.get('type') + ' ' + spelling_name(f.get('name')) + ';\n'
            # 将类的成员方法载入
            for m in ms:
                method_item = FunctionItem()
                method_item.name = m.get('name')
                method_item.file = m.get('filename')
                if method_item.imports(doc_path):
                    method_item.md_content = _simplify_functions_md(method_item.md_content)
                    clazz_item.reference_who.append(method_item)
                    clazz_item.code += '  ' + spelling_name(method_item.name) + ';\n'
                else:
                    logger.error(f'fail to load method {method_item.name}')

        _load('private')
        _load('protected')
        _load('public')
        clazz_item.code = clazz_item.code.strip()

        if not clazz_item.imports(doc_path):
            clazz_item.md_content = ce.generate_doc(clazz_item)
            # 文档生成失败，先跳过
            if clazz_item.md_content is not None:
                clazz_item.exports(doc_path)
                logger.info(f'parse {clazz_item.name}: {i + 1}/{len(records)}')
        else:
            logger.info(f'load {clazz_item.name}: {i + 1}/{len(records)}')
        i += 1


def extract_all_modules(doc_path):
    pass


def gen_doc_for_modules(output_path: str, resource_path: str, doc_path: str):
    apis = read_extern_functions(output_path, resource_path)
    logger.info(f'gen doc for modules, apis count: {len(apis)}')
    api_docs = ''
    for name, v in apis.items():
        method_item = FunctionItem()
        method_item.name = name
        method_item.file = v.get('filename')
        if method_item.imports(doc_path):
            desc = _simplify_functions_md(method_item.md_content)
            apis[name]['desc'] = desc
            api_docs += (f'- {name}\n'
                         f' > {desc}\n')
        else:
            logger.error(f'fail to load method {method_item.name}')
    prompt = modules_summarize_prompt.format(language='English', function_list=api_docs)
    llm = SimpleLLM(SettingsManager.get_setting())
    res = llm.ask([{'role': 'system', 'content': prompt}])
    with open(f'{doc_path}/modules.prompt.md', 'w') as f:
        f.write('### Summary\n' + prompt)
    module_doc = []
    modules = ModuleNote.from_doc(res)
    logger.info(f'gen doc for modules, modules count: {len(modules)}')
    i = 0
    for m in modules:
        m.functions = '\n'.join(
            list(map(lambda x: x + f'\n\n  {apis[x.strip("- ")].get("desc")}\n', m.functions.split('\n'))))
        prompt2 = modules_enhance_prompt.format(language='English', module_doc='\n'.join(
            list(map(lambda k: '> ' + k, m.to_md().split('\n')))))
        with open(f'{doc_path}/modules.prompt.md', 'a') as f:
            f.write(f'### {m.name}\n' + prompt2)
        res = llm.ask([{'role': 'system', 'content': prompt2}])
        m.example = res
        module_doc.append(m.to_md())
        i += 1
        logger.info(f'gen doc for modules {i}: {m.name}')
    with open(f'{doc_path}/modules.md', 'w') as f:
        f.write('\n'.join(module_doc))


# export OPENAI_API_KEY={KEY}
def run(path: str):
    resource_path = f'resource/{path}'
    output_path = f'output/{path}'
    doc_path = f'docs/{path}'
    make(resource_path, output_path)
    gen_doc_for_functions(output_path, resource_path, doc_path)
    gen_doc_for_classes(output_path, resource_path, doc_path)
    gen_doc_for_modules(output_path, resource_path, doc_path)
    shutil.rmtree(resource_path)
    shutil.rmtree(output_path)


@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    path = click.format_filename(path).strip('/')
    basename = os.path.basename(path)
    # 移动到工作路径
    shutil.copytree(path, f'resource/{basename}', dirs_exist_ok=True)
    run(basename)


if __name__ == '__main__':
    main('Vanguard-V2-StaticChecker')