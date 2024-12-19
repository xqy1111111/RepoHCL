import json
import os.path
import shutil
import subprocess
import sys
import threading
from itertools import islice
from typing import Dict, Set

import networkx as nx
import pydot
from loguru import logger

from ast_generator import gen_sh
from chat_engine import ChatEngine
from doc import FunctionItem, DocItem
from project_manager import ProjectManager


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
    # 基于makefile生成compile_commands.json
    cmd('bear make -j`nproc`')
    gen_sh(path)
    cmd('chmod +x buildast.sh')
    cmd('./buildast.sh')
    cmd(f'lib/cge {path}/astList.txt', path='.')
    os.makedirs(output, exist_ok=True)
    shutil.move('functions.json', output)
    shutil.move('cg.dot', output)


# 读取函数列表
def read_functions(path: str) -> Dict[str, Dict[str, str]]:
    # 调整functions.json
    with open(f'{path}/functions.json', 'r') as f:
        functions = json.loads(f.read())
        to_remove = []
        for k, v in functions.items():
            file = v.get('filename')
            # 不是绝对路径说明已经处理过了，跳过
            if not file.startswith('/'):
                continue
            # 仅保留resource下的文件
            if not file.startswith('/root/'):
                to_remove.append(k)
                continue
            # 转相对路径
            file = os.path.relpath(file)
            # functions中去除路径前缀
            v['filename'] = file[9:] if file.startswith('resource/') else file
            with open(file, 'r') as code:
                lines = list(islice(code, int(v.get('beginLine')) - 1, int(v.get('endLine'))))
                v.setdefault('code', ''.join(lines).strip())
        for k in to_remove:
            del functions[k]
    with open(f'{path}/functions.json', 'w') as f:
        f.write(json.dumps(functions, indent=4))
    return functions


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


threadlocal = threading.local()


def get_doc_manager() -> Dict[str, DocItem]:
    if not hasattr(threadlocal, 'doc_manager'):
        threadlocal.doc_manager = {}
    return threadlocal.doc_manager


def run(path: str):
    resource_path = f'resource/{path}'
    output_path = f'output/{path}'
    doc_path = 'docs'
    make(resource_path, output_path)
    functions = read_functions(output_path)
    to_analyze = set(functions.keys())
    callgraph = read_callgraph(output_path, to_analyze)
    # 拓扑排序callgraph，排除不需要分析的函数
    sorted_functions = list(reversed(list(nx.topological_sort(callgraph))))
    logger.info(f'functions count: {len(sorted_functions)}')
    ce = ChatEngine(ProjectManager(repo_path=resource_path))
    doc_manager = get_doc_manager()
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
            logger.info(f'parse {doc_item.name}: {i}/{len(sorted_functions)}')
        else:
            logger.info(f'load {doc_item.name}: {i}/{len(sorted_functions)}')
        doc_manager[f] = doc_item
    del threadlocal.doc_manager
    shutil.rmtree(resource_path)
    shutil.rmtree(output_path)


if __name__ == '__main__':
    # export OPENAI_API_KEY={KEY}
    path = sys.argv[1] if len(sys.argv) > 1 else 'resource/libxml2-2.9.9'
    basename = os.path.basename(path)
    shutil.copytree(path, f'resource/{basename}')
    run(basename)
