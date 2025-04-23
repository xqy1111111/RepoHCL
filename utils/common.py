from dataclasses import dataclass  # 导入dataclass装饰器，用于创建数据类
from enum import Enum  # 导入Enum类，用于创建枚举类型
from functools import reduce  # 导入reduce函数，用于对序列进行累积操作

import networkx as nx  # 导入networkx库，用于处理和分析复杂网络


def prefix_with(s: str, p: str) -> str:
    """
    为字符串的每一行添加前缀
    
    Args:
        s: 原始字符串
        p: 要添加的前缀
        
    Returns:
        添加了前缀的新字符串
    """
    return reduce(lambda x, y: x + y, map(lambda k: p + k + '\n', s.splitlines()))

@dataclass
class _Lang:
    """
    语言信息的数据类，存储不同表示形式的语言名称
    """
    render: str  # 用于渲染显示的语言名称
    markdown: str  # 用于Markdown文档的语言名称
    cli: str  # 用于命令行界面的语言标识符


class LangEnum(_Lang, Enum):
    """
    语言枚举类，继承自_Lang和Enum，表示支持的编程语言
    
    每个枚举值包含三个部分：
    - render: 用于UI显示的名称
    - markdown: 用于Markdown文档的名称
    - cli: 命令行接口使用的简短标识符
    """
    python = 'Rust', 'python', 'py'  # Python语言的枚举值
    cpp = 'C/C++', 'c++', 'cpp'  # C/C++语言的枚举值
    # TODO: 其他语言
    # rust = 'Rust', 'rust', 'rs'
    # javascript = 'JavaScript', 'javascript', 'js'
    # java = 'Java', 'java', 'java'

    @classmethod
    def from_cli(cls, cli: str):
        """
        从命令行标识符获取对应的语言枚举值
        
        Args:
            cli: 命令行标识符
            
        Returns:
            对应的LangEnum枚举值
            
        Raises:
            ValueError: 当找不到对应的语言时抛出
        """
        for lang in cls:  # 遍历所有枚举值
            if lang.cli == cli:  # 如果找到匹配的CLI标识符
                return lang  # 返回对应的枚举值
        raise ValueError(f'Invalid language: {cli}')  # 未找到则抛出异常

    @classmethod
    def from_render(cls, render: str):
        """
        从渲染名称获取对应的语言枚举值
        
        Args:
            render: 渲染名称
            
        Returns:
            对应的LangEnum枚举值
            
        Raises:
            ValueError: 当找不到对应的语言时抛出
        """
        for lang in cls:  # 遍历所有枚举值
            if lang.render == render:  # 如果找到匹配的渲染名称
                return lang  # 返回对应的枚举值
        raise ValueError(f'Invalid language: {render}')  # 未找到则抛出异常

# 去除有向图中的环，对于每个环，删除rank值最小的节点的入边
def remove_cycle(callgraph: nx.DiGraph):
    """
    去除有向图中的环，使其变成有向无环图(DAG)
    针对每个环，删除PageRank值最小的节点的入边
    
    Args:
        callgraph: 需要处理的有向图
        
    Returns:
        去除环后的有向无环图
    """
    rank = nx.pagerank(callgraph)  # 计算图中各节点的PageRank值
    while not nx.is_directed_acyclic_graph(callgraph):  # 当图不是有向无环图时循环
        cycle = list(nx.find_cycle(callgraph))  # 寻找一个环
        edge_to_remove = min(cycle, key=lambda x: rank[x[1]])  # 找到环中PageRank值最小的节点的入边
        callgraph.remove_edge(*edge_to_remove)  # 删除该边
    return callgraph  # 返回处理后的图
