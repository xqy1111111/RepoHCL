import json
import os
import re
import shutil
import subprocess
from itertools import islice
from typing import List, Dict

import networkx as nx
import pydot

from loguru import logger

from utils import gen_sh
from .metric import Metric, Symbol, FuncDef, FieldDef, EvaContext, ClazzDef


class ClangParser(Metric):

    @staticmethod
    def _flush_file(path: str, records: Dict) -> None:
        with open(path, 'w') as f:
            f.write(json.dumps(records, indent=4))

    @staticmethod
    def _read_file(path: str, resource_path: str) -> Dict:
        to_remove = []
        with open(path, 'r') as f:
            records = json.loads(f.read())
            for k, v in records.items():
                file: str = v.get('filename')
                # 不是绝对路径说明已经处理过了，跳过
                if not file.startswith('/'):
                    continue
                # 仅保留resource下的文件
                # resource_path = 'resource/libxml2/'
                i = file.find(resource_path)
                if i == -1:
                    to_remove.append(k)
                    continue
                v['filename'] = file[i + len(resource_path):].strip('/')
            for k in to_remove:
                del records[k]
        if len(to_remove):
            ClangParser._flush_file(path, records)
        return records

    @staticmethod
    def _trim_type(t: str) -> str:
        return re.sub(r'[*&]|(\[\d*])|const|volatile|restrict', '', t).strip()

    @staticmethod
    def _load_clazz_typedefs(output_path: str, resource_path: str) -> Dict[str, Symbol]:
        clazz_typedefs_map = {}
        records = ClangParser._read_file(f'{output_path}/typedefs.json', resource_path)
        for k, v in records.items():
            source_type = v.get('sourceType')
            if source_type not in ('struct', 'other') or v.get('source').get('literal') == k:
                continue
            literal = v.get('source').get('literal')
            clazz_typedefs_map[k] = Symbol(base=ClangParser._trim_type(literal), literal=literal)
        simplified_map = {}
        for t in clazz_typedefs_map:
            init_t = final_value = t
            while t in clazz_typedefs_map:
                next_t = clazz_typedefs_map[t].literal
                final_value = final_value.replace(t, next_t)
                t = ClangParser._trim_type(next_t)
            simplified_map[init_t] = Symbol(base=t, literal=final_value)
        return simplified_map

    @staticmethod
    def _load_functions(output_path: str, resource_path: str, typedefs: Dict[str, Symbol]) -> Dict[Symbol, FuncDef]:
        function_map = {}
        records = ClangParser._read_file(f'{output_path}/functions.json', resource_path)
        for k, v in records.items():
            params = []
            for p in v.get('parameters'):
                literal = p.get('literal')
                symbol = ClangParser._field_symbol_to_final(
                    Symbol(base=ClangParser._trim_type(literal), literal=literal), typedefs)
                params.append(FieldDef(name=p.get('name'),
                                       symbol=symbol,
                                       access=p.get('access')))
            with open(resource_path + '/' + v.get('filename'), 'r') as f:
                lines = list(islice(f, int(v.get('beginLine')) - 1, int(v.get('endLine'))))
                code = ''.join(lines).strip()
            function_map[Symbol(base=k)] = FuncDef(symbol=Symbol(base=k), access='', params=params, declFile=v.get('declFilename'),
                                                   filename=v.get('filename'), code=code, visible=v.get('visible'),
                                                   beginLine=v.get('beginLine'), endLine=v.get('endLine'))

        return function_map

    @staticmethod
    def _field_symbol_to_final(symbol: Symbol, typedefs: Dict[str, Symbol]) -> Symbol:
        base: str = symbol.base
        literal: str = symbol.literal
        # 获得field的终态类型
        final_symbol: Symbol = typedefs.get(base, Symbol(base=base))
        # 修改field的类型字面量
        literal = literal.replace(base, final_symbol.literal)
        # 修改field的基础类型为终态类型
        base = final_symbol.base
        return Symbol(base=base, literal=literal)

    @staticmethod
    def _load_clazz(output_path: str, resource_path: str, functions: Dict[Symbol, FuncDef],
                    typedefs: Dict[str, Symbol]) -> Dict[Symbol, ClazzDef]:
        clazz_map = {}

        def _load_clazz(r: Dict):
            for k, v in r.items():
                s = Symbol(base=k)
                fields = []
                for f in v.get('fields'):
                    literal = f.get('literal')
                    symbol = ClangParser._field_symbol_to_final(
                        Symbol(base=ClangParser._trim_type(literal), literal=literal), typedefs)
                    fields.append(FieldDef(name=f.get('name'),
                                           symbol=symbol,
                                           access=f.get('access')))

                if 'functions' in v:
                    clazz_functions = list(map(lambda x: FuncDef(symbol=Symbol(base=x.get('name')),
                                                                 access=x.get('access')), v.get('functions')))
                else:
                    clazz_functions = ClangParser._find_related_functions(s, functions)

                clazz_map[s] = ClazzDef(symbol=s, fields=fields, functions=clazz_functions,
                                        filename=v.get('filename'),
                                        beginLine=v.get('beginLine'), endLine=v.get('endLine'))

        records = ClangParser._read_file(f'{output_path}/structs.json', resource_path)
        _load_clazz(records)
        records = ClangParser._read_file(f'{output_path}/records.json', resource_path)
        _load_clazz(records)
        return clazz_map

    @staticmethod
    def _find_related_functions(s: Symbol, functions: Dict[Symbol, FuncDef]) -> List[FuncDef]:
        related = []
        for k, v in functions.items():
            for p in v.params:
                if p.symbol == s:
                    related.append(FuncDef(symbol=k, access='public'))
        return related

    @staticmethod
    def _load_sample_callgraph(output_path: str, functions: Dict[Symbol, FuncDef], starts: List[Symbol]) -> nx.DiGraph:
        callgraph = ClangParser._load_callgraph(output_path, functions)
        q = list(map(lambda x: x.base, starts))
        v = set()
        ng = nx.DiGraph()
        while len(q):
            s = q.pop(0)
            v.add(s)
            for t in list(filter(lambda t: t not in v, callgraph.successors(s))):
                q.append(t)
                ng.add_edge(s, t)
        logger.info(f'[ClangParser] sample callgraph: {len(callgraph.nodes)} -> {len(ng.nodes)}, starts: {starts}')
        return ng

    @staticmethod
    def _load_callgraph(output_path: str, functions: Dict[Symbol, FuncDef]) -> nx.DiGraph:
        # 解析.dot转为DiGraph
        (dot,) = pydot.graph_from_dot_file(f'{output_path}/cg.dot')
        callgraph = nx.DiGraph()
        name_map = {}
        # 添加节点
        for node in dot.get_nodes():
            if isinstance(node, pydot.Node):
                label = node.get('label')[1:-1]
                name_map[node.get_name()] = label
                if Symbol(base=label) in functions:
                    callgraph.add_node(label)
        # 添加边
        for edge in dot.get_edges():
            source = name_map[edge.get_source()]
            destination = name_map[edge.get_destination()]
            if source == destination:
                continue
            if Symbol(base=source) not in functions or Symbol(base=destination) not in functions:
                continue
            callgraph.add_edge(source, destination)

        # 去除环
        def _remove_cycles(g: nx.DiGraph):
            while not nx.is_directed_acyclic_graph(g):
                cycle = list(nx.find_cycle(g))
                edge_to_remove = cycle[0]
                logger.debug(f'remove {edge_to_remove}')
                g.remove_edge(*edge_to_remove)

        _remove_cycles(callgraph)

        return callgraph

    def eva(self, ctx: EvaContext):
        self._prepare(ctx.output_path, ctx.resource_path)
        logger.info(f'[ClangParser] prepared')
        clazz_typedefs_map = self._load_clazz_typedefs(ctx.output_path, ctx.resource_path)
        logger.info(f'[ClangParser] typedef size: {len(clazz_typedefs_map)}')
        ctx.function_map = self._load_functions(ctx.output_path, ctx.resource_path, clazz_typedefs_map)
        # ctx.callgraph = self._load_sample_callgraph(ctx.output_path, ctx.function_map, [
        #     Symbol(base='xmlDocPtr xmlReadFile(const char * URL, const char * encoding, int options)'),
        #     Symbol(base='xmlDocPtr xmlNewDoc(const xmlChar * version)'),
        #     Symbol(base='xmlNodePtr xmlNewNode(xmlNsPtr ns, const xmlChar * name)'),
        #     Symbol(base='xmlChar * xmlGetProp(const xmlNode * node, const xmlChar * name)'),
        #     Symbol(
        #         base='int xmlSaveFormatFileEnc(const char * filename, xmlDocPtr cur, const char * encoding, int format)'),
        #     Symbol(base='xmlNsPtr xmlSearchNs(xmlDocPtr doc, xmlNodePtr node, const xmlChar * nameSpace)'),
        #     Symbol(base='xmlXPathObjectPtr xmlXPathEval(const xmlChar * str, xmlXPathContextPtr ctx)'),
        #     Symbol(base='void xmlFreeDoc(xmlDocPtr cur)'),
        #     Symbol(base='int xmlCharEncOutFunc(xmlCharEncodingHandler * handler, xmlBufferPtr out, xmlBufferPtr in)'),
        #     Symbol(base='xmlNodePtr xmlAddChild(xmlNodePtr parent, xmlNodePtr cur)'),
        #     Symbol(base='void xmlCleanupParser()'),
        #     Symbol(base='int xmlSaveFile(const char * filename, xmlDocPtr cur)'),
        #     Symbol(base='xmlDocPtr xmlReadFd(int fd, const char * URL, const char * encoding, int options)'),
        #     Symbol(base='xmlAttrPtr xmlHasProp(const xmlNode * node, const xmlChar * name)'),
        #     Symbol(base='xmlNodePtr xmlDocGetRootElement(const xmlDoc * doc)'),
        #     Symbol(base='xmlXPathContextPtr xmlXPathNewContext(xmlDocPtr doc)'),
        #     Symbol(base='xmlXPathObjectPtr xmlXPathEvalExpression(const xmlChar * str, xmlXPathContextPtr ctxt)'),
        # ])
        ctx.callgraph = self._load_callgraph(ctx.output_path, ctx.function_map)
        ctx.function_map = {k: v for k, v in ctx.function_map.items() if k.base in ctx.callgraph.nodes}
        logger.info(f'[ClangParser] function size: {len(ctx.function_map)}')
        logger.info(f'[ClangParser] callgraph size: {len(ctx.callgraph.nodes)}, {len(ctx.callgraph.edges)}')
        ctx.clazz_map = self._load_clazz(ctx.output_path, ctx.resource_path, ctx.function_map, clazz_typedefs_map)
        logger.info(f'[ClangParser] class size: {len(ctx.clazz_map)}')
        ctx.clazz_callgraph = self._load_clazz_callgraph(ctx.clazz_map)
        logger.info(f'[ClangParser] class callgraph size: {len(ctx.clazz_callgraph.nodes)}, {len(ctx.clazz_callgraph.edges)}')

    @staticmethod
    def _load_clazz_callgraph(clazz_map):
        graph = nx.DiGraph()
        for s, clazz in clazz_map.items():
            graph.add_node(s.base)
            for f in clazz.fields:
                if f.symbol in clazz_map and f.symbol != s:
                    graph.add_edge(s.base, f.symbol.base)
        return graph

    @staticmethod
    def _prepare(output_path: str, resource_path: str):
        if os.path.exists(output_path):
            return

        def cmd(command: str, path: str = resource_path):
            subprocess.run(command, shell=True, cwd=path)
            logger.info('command executed: ' + command)

        os.environ['CC'] = 'clang-9'
        os.environ['CXX'] = 'clang++-9'
        # 生成makefile文件
        logger.info(f'{resource_path} content:{str(os.listdir(resource_path))}')
        if os.path.exists(f'{resource_path}/configure'):
            cmd('./configure')
        elif os.path.exists(f'{resource_path}/Configure'):
            cmd('./Configure')
        elif os.path.exists(f'{resource_path}/CMakeLists.txt'):
            cmd('cmake -DCMAKE_BUILD_TYPE=Release -DLLVM_PREFIX=/lib/llvm-9 .')
        if not os.path.exists(f'{resource_path}/Makefile'):
            raise Exception('Makefile not found in root')
        # 基于makefile生成compile_commands.json
        cmd('bear make -j`nproc`')
        # 生成 build ast 命令
        gen_sh(resource_path)
        # 生成.ast
        cmd('chmod +x buildast.sh')
        cmd('./buildast.sh')
        # 在resource_path目录下解析ast
        shutil.copy('lib/cge', resource_path)
        cmd(f'./cge astList.txt')
        # 将解析结果移动到output_path
        os.makedirs(output_path, exist_ok=True)
        shutil.move(f'{resource_path}/structs.json', output_path)
        shutil.move(f'{resource_path}/typedefs.json', output_path)
        shutil.move(f'{resource_path}/functions.json', output_path)
        shutil.move(f'{resource_path}/records.json', output_path)
        shutil.move(f'{resource_path}/cg.dot', output_path)
