import json
import os.path
import sys
from itertools import islice

import networkx as nx
import subprocess
from typing import Dict

import pydot
import tqdm

from chat_engine import ChatEngine
from doc import FunctionItem
from ast_generator import gen_sh
from project_manager import ProjectManager



def procedure(path: str):
    subprocess.run('./configure', cwd=path)
    subprocess.run('bear make -j`nproc`', shell=True, cwd=path)
    gen_sh(path)
    subprocess.run('chmod +x ./buildast.sh', shell=True, cwd=path)
    subprocess.run('./buildast.sh', shell=True, cwd=path)
    subprocess.run(f'lib/cge {path}/astList.txt', shell=True)
    # lib.gen(path.encode())


def read_functions() -> Dict[str, Dict[str, str]]:
    with open('output/functions.json', 'r') as f:
        functions = json.loads(f.read())
        to_remove = []
        for k, v in functions.items():
            file = v.get('filename')
            if not file.startswith('/'):
                continue
            if not file.startswith('/root/') :
                to_remove.append(k)
                continue
            file = file.replace('/root/', 'resource/')
            v['filename'] = file.removeprefix('resource/')
            with open(file, 'r') as code:
                lines = list(islice(code, int(v.get('beginLine')) - 1, int(v.get('endLine'))))
                v.setdefault('code', ''.join(lines))
        for k in to_remove:
            del functions[k]
    with open('output/functions.json', 'w') as f:
        f.write(json.dumps(functions, indent=4))
    return functions


def read_callgraph() -> nx.DiGraph:
    # 解析.dot转为DiGraph
    (dot, ) = pydot.graph_from_dot_file('output/cg1.dot')
    digraph = nx.DiGraph()
    name_map = {}
    # 添加节点
    for node in dot.get_nodes():
        if isinstance(node, pydot.Node):
            label = node.get('label')[1:-1]
            name_map[node.get_name()] = label
            digraph.add_node(label)

    # 添加边
    for edge in dot.get_edges():
        source = edge.get_source()
        destination = edge.get_destination()
        digraph.add_edge(name_map[source], name_map[destination])

    def remove_cycles(g: nx.DiGraph):
        while not nx.is_directed_acyclic_graph(g):
            cycle = list(nx.find_cycle(g))
            edge_to_remove = cycle[0]
            print('remove', edge_to_remove)
            g.remove_edge(*edge_to_remove)

    # def remove_cycles(g: nx.DiGraph):
    #     # 获取所有强连通分量
    #     sccs = list(nx.strongly_connected_components(g))
    #     # 遍历每一个强连通分量
    #     for scc in sccs:
    #         if len(scc) > 1:  # 只处理非平凡的强连通分量
    #             subgraph = g.subgraph(scc)
    #             edges_in_cycle = list(subgraph.edges())
    #             if edges_in_cycle:
    #                 # 移除第一条边以打破循环
    #                 g.remove_edge(*edges_in_cycle[0])
    remove_cycles(digraph)

    return digraph


doc_manager = {}

if __name__ == '__main__':
    # export OPENAI_API_KEY={KEY}
    path = 'resource/libxml2-2.9.9'
    # procedure(path)
    functions = read_functions()
    to_analyze = set(functions.keys())
    callgraph = read_callgraph()

    # 拓扑排序callgraph d  f
    sorted_functions = list(reversed(list(nx.topological_sort(callgraph))))
    ce = ChatEngine(ProjectManager(repo_path=path))
    for f in tqdm.tqdm(sorted_functions, desc='docs generating', total=len(sorted_functions)):
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
        md = ce.generate_doc(doc_item)
        doc_manager[f] = doc_item
        d = f'docs/{doc_item.file}'
        if not os.path.exists(d):
            os.makedirs(d)
        with open(f'{d}/{f}.md', 'w') as f:
            f.write(md)