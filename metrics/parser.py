# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import subprocess
import sys
from typing import List, Dict

import networkx as nx
import pydot
from loguru import logger

from utils import gen_sh, remove_cycle
from .metric import Metric, FuncDef, FieldDef, EvaContext, ClazzDef


# ClangParser类: 用于解析C/C++软件，生成函数调用关系图和类图
class ClangParser(Metric):
    """ClangParser类
    
    使用Clang工具解析C/C++代码，生成函数调用图和类结构信息
    该类作为度量工具的一部分，可以分析代码结构和依赖关系
    """

    @classmethod
    def _flush_file(cls, path: str, records: Dict) -> None:
        """将记录写入文件
        
        将字典数据以JSON格式写入指定路径的文件
        
        Args:
            path: 文件路径
            records: 要写入的字典数据
        """
        with open(path, 'w') as fp:
            json.dump(records, fp, indent=4)

    @classmethod
    def _read_file(cls, path: str, resource_path: str) -> Dict:
        """读取文件内容
        
        从指定路径的JSON文件中读取数据，并转换为字典
        
        Args:
            path: 文件路径
            resource_path: 资源文件夹路径
            
        Returns:
            读取的字典数据
        """
        ctime = time.time()
        try:
            with open(path, 'r') as fp:
                data = json.load(fp)
                logger.info(f'[ClangParser] read file {path}({len(data)}), cost: {time.time() - ctime:.3f}s')
                return data
        except FileNotFoundError:
            logger.error(f'[ClangParser] file not found {path}')
            # 如果resource_path为空，尝试在resource_path下找结果文件夹
            file_name = os.path.basename(path)
            if not resource_path:
                return {}
            try:
                with open(os.path.join(resource_path, file_name), 'r') as fp:
                    data = json.load(fp)
                    logger.info(
                        f'[ClangParser] read file {os.path.join(resource_path, file_name)}({len(data)}), '
                        f'cost: {time.time() - ctime:.3f}s')
                    return data
            except:
                return {}
        except Exception as e:
            logger.error(f'[ClangParser] read file {path} error: {e}')
            return {}

    @classmethod
    def _trim_type(cls, t: str) -> str:
        """清理类型字符串
        
        去除类型字符串中的指针、引用、常量和数组等符号，提取纯类型名
        
        Args:
            t: 类型字符串
            
        Returns:
            清理后的类型名
        """
        t = t.strip()
        t = t.replace('std::', '')
        t = t.replace('const ', '')
        t = t.replace('struct ', '')
        t = t.split('[')[0]
        t = t.split('<')[0]
        t = t.split('(')[0]
        t = t.replace('*', '')
        t = t.replace('&', '')
        return t.strip()

    @classmethod
    def _load_clazz_typedefs(cls, output_path: str, resource_path: str) -> Dict[str, str]:
        """加载类型别名定义
        
        从typedefs.json中加载类型别名映射，建立类型别名到实际类型的映射关系
        
        Args:
            output_path: 输出目录路径
            resource_path: 资源目录路径
            
        Returns:
            类型别名到实际类型的映射字典
        """
        typedefs = cls._read_file(os.path.join(output_path, 'typedefs.json'), resource_path)
        typedefs_map = {}
        for k, v in typedefs.items():
            k = cls._trim_type(k)
            # 类型别名到实际类型的映射，清理掉类型中的指针、引用等符号
            typedefs_map[k] = cls._trim_type(v)
        return typedefs_map

    @classmethod
    def _load_functions(cls, output_path: str, resource_path: str) -> Dict[str, FuncDef]:
        """加载函数定义
        
        从functions.json中加载函数定义，构建函数名到FuncDef对象的映射
        
        Args:
            output_path: 输出目录路径
            resource_path: 资源目录路径
            
        Returns:
            函数名到FuncDef对象的映射字典
        """
        functions = cls._read_file(os.path.join(output_path, 'functions.json'), resource_path)
        function_map = {}
        # 从functions.json中构建函数名到FuncDef对象的映射
        for name, func in functions.items():
            # 跳过参数未知的函数
            if not func['params']:
                continue
            # 跳过本文件不在包含列表中的函数（名称中无::表示是全局函数）
            if '::' not in name and func['file'] not in ['', 'unknown']:
                continue
            function_map[name] = FuncDef(
                symbol=name,
                file=func['file'],
                content=func['content'],
                params=func['params'] or []
            )
        return function_map

    @classmethod
    def _build_class_code(cls, symbol: str, fields: List[FieldDef], functions: List[FuncDef]) -> str:
        """构建类代码字符串
        
        根据类的字段和方法信息，生成类的伪代码表示
        
        Args:
            symbol: 类名
            fields: 类的字段列表
            functions: 类的方法列表
            
        Returns:
            类的伪代码字符串
        """
        # 构建类的伪代码表示
        codes = [
            f'class {symbol} {{',
            'public:'
        ]
        # 添加字段定义
        if fields:
            codes.append('    /* fields */')
            for field in fields:
                codes.append(f'    {field.symbol};')
        # 添加函数/方法定义
        if functions:
            codes.append('    /* methods */')
            for function in functions:
                func_name = function.symbol.split('::')[-1]
                # 获取方法参数
                param_str = ", ".join(function.params)
                # 生成方法声明
                codes.append(f'    {func_name}({param_str});')
        codes.append('};')
        # 返回完整的类伪代码
        return '\n'.join(codes)

    @classmethod
    def _load_clazz(cls, output_path: str, resource_path: str, callgraph: nx.DiGraph,
                    typedefs: Dict[str, str]) -> Dict[str, ClazzDef]:
        """加载类定义
        
        从records.json中加载类定义信息，构建类名到ClazzDef对象的映射
        
        Args:
            output_path: 输出目录路径
            resource_path: 资源目录路径
            callgraph: 函数调用图
            typedefs: 类型别名映射字典
            
        Returns:
            类名到ClazzDef对象的映射字典
        """
        records = cls._read_file(os.path.join(output_path, 'records.json'), resource_path)
        clazz_map = {}
        for symbol, clazz in records.items():
            # 收集类的字段信息
            fields = []
            # 解析类中的字段定义，构建FieldDef对象列表
            for field_name, field_type in clazz['fields'].items():
                fields.append(FieldDef(field_name, cls._trim_type(field_type)))
            # 查找与该类相关的方法
            functions = cls._find_related_functions(symbol, callgraph, typedefs)
            # 构建类的伪代码表示
            code = cls._build_class_code(symbol, fields, functions)
            # 创建ClazzDef对象并添加到映射中
            clazz_map[symbol] = ClazzDef(
                symbol=symbol,
                code=code,
                functions=functions,
                fields=fields
            )
        return clazz_map

    @classmethod
    def _find_related_functions(cls, clazz: str, callgraph: nx.DiGraph, typedefs: Dict[str, str]) -> List[
        FuncDef]:
        """查找与类相关的函数
        
        识别与指定类相关的所有方法和函数
        
        Args:
            clazz: 类名
            callgraph: 函数调用图
            typedefs: 类型别名映射字典
            
        Returns:
            与该类相关的FuncDef对象列表
        """
        # 识别与给定类相关的函数
        # 1. 基于命名约定: 如className::methodName
        # 2. 可能存在typedefs中定义的别名
        class_names = [clazz]
        for k, v in typedefs.items():
            if v == clazz:
                class_names.append(k)
        functions = []
        for node in callgraph.nodes:
            attr: FuncDef = callgraph.nodes[node]['attr']
            # 检查函数是否属于该类(通过命名约定className::methodName)
            for class_name in class_names:
                if attr.symbol.startswith(f'{class_name}::'):
                    functions.append(attr)
                    break
        return functions

    @classmethod
    def _load_sample_callgraph(cls, output_path: str, functions: Dict[str, FuncDef], starts: List[str]) -> nx.DiGraph:
        """加载样本调用图
        
        从指定的起始函数开始，加载子图，生成更小的调用图
        
        Args:
            output_path: 输出目录路径
            functions: 函数名到FuncDef对象的映射字典
            starts: 起始函数名列表
            
        Returns:
            样本调用图（有向无环图）
        """
        callgraph = cls._load_callgraph(output_path, functions)
        # 函数名转FuncDef，找不到则报错
        q = list(map(lambda x: functions[x], starts))
        v = set()
        ng = nx.DiGraph()
        while len(q):
            s = q.pop(0)
            v.add(s)
            for t in list(filter(lambda x: x not in v, callgraph.successors(s))):
                q.append(t)
                ng.add_edge(s, t)
        logger.info(f'[ClangParser] sample callgraph: {len(callgraph.nodes)} -> {len(ng.nodes)}, starts: {starts}')
        return ng

    # 生成函数间调用图
    @classmethod
    def _load_callgraph(cls, output_path: str, functions: Dict[str, FuncDef]) -> nx.DiGraph:
        """加载函数调用图
        
        从Clang生成的dot文件中加载函数调用图
        
        Args:
            output_path: 输出目录路径
            functions: 函数名到FuncDef对象的映射字典
            
        Returns:
            函数调用图（有向无环图）
        """
        # 解析.dot转为DiGraph
        (dot,) = pydot.graph_from_dot_file(os.path.join(output_path, 'cg.dot'))
        callgraph = nx.DiGraph()
        # 记录.dot中节点ID和名称的映射关系
        id_map: Dict[str, str] = {}
        # 添加节点
        for node in dot.get_nodes():
            # 删除前后的"符号
            label = node.get('label').strip('"')
            # 仅同时在functions.json和cg.dot中存在的节点才添加到callgraph中
            if label in functions:
                # callgraph的节点是str函数名称,属性为FuncDef
                callgraph.add_node(label, attr=functions[label])
                id_map[node.get_name()] = label

        # 添加边
        for edge in dot.get_edges():
            # 排除自引用
            if edge.get_source() == edge.get_destination():
                continue
            # 边的起点和终点必须在functions.json中存在
            if edge.get_source() not in id_map or edge.get_destination() not in id_map:
                continue
            callgraph.add_edge(id_map[edge.get_source()], id_map[edge.get_destination()])
        return remove_cycle(callgraph)

    def eva(self, ctx: EvaContext):
        """执行代码解析和分析
        
        解析C/C++代码，生成函数调用图和类调用图
        
        Args:
            ctx: 评估上下文，包含输出路径和资源路径
        """
        self._prepare(ctx.output_path, ctx.resource_path)
        logger.info(f'[ClangParser] prepared')
        clazz_typedefs_map = self._load_clazz_typedefs(ctx.output_path, ctx.resource_path)
        logger.info(f'[ClangParser] typedef size: {len(clazz_typedefs_map)}')
        function_map = self._load_functions(ctx.output_path, ctx.resource_path)
        ctx.callgraph = self._load_callgraph(ctx.output_path, function_map)
        logger.info(f'[ClangParser] callgraph size: {len(ctx.callgraph.nodes)}, {len(ctx.callgraph.edges)}')
        clazz_map = self._load_clazz(ctx.output_path, ctx.resource_path, ctx.callgraph, clazz_typedefs_map)
        ctx.clazz_callgraph = self._load_clazz_callgraph(clazz_map, clazz_typedefs_map)
        logger.info(
            f'[ClangParser] class callgraph size: {len(ctx.clazz_callgraph.nodes)}, {len(ctx.clazz_callgraph.edges)}')

    @classmethod
    def _load_clazz_callgraph(cls, clazz_map: Dict[str, ClazzDef], typedefs: Dict[str, str]):
        """加载类调用图
        
        构建类与类之间的关系图，包括组合关系
        
        Args:
            clazz_map: 类名到ClazzDef对象的映射字典
            typedefs: 类型别名映射字典
            
        Returns:
            类调用图（有向无环图）
        """
        graph = nx.DiGraph()
        for s, clazz in clazz_map.items():
            graph.add_node(s, attr=clazz)
        for s, clazz in clazz_map.items():
            # 描述类间的组合关系
            # class A {
            #   B b;
            # }
            # A -> B
            for f in clazz.fields:
                t = cls._trim_type(f.symbol)
                t = typedefs.get(t, t)
                # 如果不在类的声明图中，说明该类型不是项目中定义的类。例如：int
                if t in graph:
                    graph.add_edge(s, t)
            # TODO，描述类间的继承关系
        return remove_cycle(graph)

    # 调用clang解析软件
    @staticmethod
    def _prepare(output_path: str, resource_path: str):
        """准备解析环境
        
        调用Clang工具解析C/C++代码，生成解析结果
        
        Args:
            output_path: 输出目录路径
            resource_path: 源代码资源目录路径
        """
        # 已经生成过解析文件，直接返回
        if os.path.exists(output_path):
            return
        # TODO windows当前不支持，下列命令行及gen_sh在windows下无法执行
        if sys.platform.startswith("win"):
            raise Exception("Windows is not supported")

        def cmd(command: str, path: str = resource_path):
            """执行命令
            
            在指定目录中执行shell命令，并记录日志
            
            Args:
                command: 要执行的命令
                path: 执行命令的目录路径，默认为resource_path
            """
            subprocess.run(command.replace('/', os.sep), shell=True, cwd=path.replace('/', os.sep))
            logger.info('[ClangParser] command executed: ' + command)

        os.environ['CC'] = 'clang-9'
        os.environ['CXX'] = 'clang++-9'
        # 生成makefile文件
        if os.path.exists(os.path.join(resource_path, 'configure')):
            cmd('./configure')
        elif os.path.exists(os.path.join(resource_path, 'Configure')):
            cmd('./Configure')
        elif os.path.exists(os.path.join(resource_path, 'CMakeLists.txt')):
            cmd('cmake -DCMAKE_BUILD_TYPE=Release -DLLVM_PREFIX=/lib/llvm-9 .')
        if not os.path.exists(os.path.join(resource_path, 'Makefile')):
            raise Exception('Makefile not found in root')
        # 基于makefile生成compile_commands.json
        cmd('bear make -j`nproc`')
        # 生成 build ast 命令
        gen_sh(resource_path)
        # 生成.ast
        cmd('chmod +x buildast.sh')
        cmd('./buildast.sh')
        # 在resource_path目录下解析ast
        shutil.copy(os.path.join('lib', 'cge'), resource_path)
        cmd(f'./cge astList.txt')
        # 将解析结果移动到output_path
        os.makedirs(output_path, exist_ok=True)
        shutil.move(os.path.join(resource_path, 'structs.json'), output_path)
        shutil.move(os.path.join(resource_path, 'typedefs.json'), output_path)
        shutil.move(os.path.join(resource_path, 'functions.json'), output_path)
        shutil.move(os.path.join(resource_path, 'records.json'), output_path)
        shutil.move(os.path.join(resource_path, 'cg.dot'), output_path)
