from __future__ import annotations  # 启用未来版本的注解特性，允许在类型注解中使用尚未定义的类

import sys  # 导入sys模块，用于系统相关操作
import uuid  # 导入uuid模块，用于生成唯一标识符
from collections import deque, defaultdict  # 导入集合类，用于队列和默认字典
from concurrent.futures import as_completed  # 导入并发执行工具
from concurrent.futures.thread import ThreadPoolExecutor  # 导入线程池执行器
from typing import List, TypeVar, Any  # 导入类型提示工具

import networkx as nx  # 导入networkx库，用于处理图结构
from loguru import logger  # 导入loguru库的logger，用于日志记录
from typing_extensions import Callable, Optional  # 导入扩展类型提示工具

P = TypeVar("P")  # 定义泛型类型P，用于任务参数


class Task:
    """任务类
    
    表示一个可执行的任务，包含执行函数、参数和依赖关系
    每个任务有唯一的ID，用于标识和比较
    """
    def __init__(self, f: Callable[[P]], args: P, dependencies: Optional[List[Task]] = None):
        """初始化任务
        
        Args:
            f: 要执行的函数
            args: 函数参数
            dependencies: 依赖的其他任务列表，默认为None
        """
        self.f = f  # 要执行的函数
        self.dependencies = dependencies  # 依赖的任务列表
        self.args = args  # 函数参数
        self.id = uuid.uuid4().hex  # 生成唯一ID

    def __hash__(self):
        """哈希方法，用于将任务对象作为字典键或集合元素
        
        Returns:
            任务ID的哈希值
        """
        return hash(self.id)

    def __eq__(self, other):
        """相等性比较方法
        
        Args:
            other: 要比较的对象
            
        Returns:
            布尔值，表示两个对象是否相等
        """
        if not isinstance(other, Task):
            return False
        return self.id == other.id

    def __repr__(self):
        """生成任务的字符串表示
        
        Returns:
            表示任务的字符串
        """
        return f'Task({self.f.__name__}, {self.args})'


# 任务调度器，将一组任务按照依赖关系分组，并行执行
class TaskDispatcher:
    """任务分发器
    
    负责管理和执行一组具有依赖关系的任务，能够按照依赖顺序有效地并行执行
    使用有向图表示任务之间的依赖关系，确保依赖任务优先执行
    """
    def __init__(self, pool: ThreadPoolExecutor):
        """初始化任务分发器
        
        Args:
            pool: 线程池执行器，用于并行执行任务
        """
        self._pool = pool  # 线程池
        self._tasks = nx.DiGraph()  # 任务依赖图，有向图表示

    def adds(self, tasks: List[Task]):
        """批量添加多个任务
        
        Args:
            tasks: 任务列表
            
        Returns:
            self，用于链式调用
        """
        for task in tasks:
            self.add(task)  # 逐个添加任务
        return self  # 返回self用于链式调用

    def add(self, f: Task):
        """添加单个任务
        
        将任务添加到依赖图中，包括其依赖关系
        
        Args:
            f: 要添加的任务
            
        Returns:
            self，用于链式调用
        """
        self._tasks.add_node(f)  # 添加任务节点
        if f.dependencies is None:  # 如果没有依赖
            return self  # 直接返回
        for dep in f.dependencies:  # 遍历依赖项
            self._tasks.add_edge(f, dep)  # 添加依赖边：f依赖于dep
        return self  # 返回self用于链式调用

    def map(self, dg: nx.DiGraph, f: Callable):
        """从图结构映射生成任务
        
        将图中的每个节点映射为一个任务，保留原图中的依赖关系
        
        Args:
            dg: 有向图，表示节点间的依赖关系
            f: 对每个节点执行的函数
            
        Returns:
            self，用于链式调用
        """
        tasks = {}  # 节点到任务的映射
        # 为每个节点创建任务
        for node in dg.nodes:
            tasks[node] = Task(f=f, args=(node,))
        # 建立任务间的依赖关系
        for node in dg.nodes:
            tasks[node].dependencies = []
            for dep in dg.successors(node):  # 遍历节点的后继
                tasks[node].dependencies.append(tasks[dep])  # 添加依赖
            self.add(tasks[node])  # 添加任务到分发器
        return self  # 返回self用于链式调用

    def run(self):
        """执行所有任务
        
        按照依赖关系的拓扑排序，分组并行执行任务
        
        Raises:
            ValueError: 如果任务图中存在循环依赖
        """
        # 检查是否有环
        if not nx.is_directed_acyclic_graph(self._tasks):
            raise ValueError("Graph is not acyclic")  # 存在循环依赖，抛出异常
        groups = reverse_topo(self._tasks)  # 获取分组后的任务（按逆拓扑排序）
        logger.debug(f'[TaskDispatcher] split {len(self._tasks)} tasks into {len(groups)} groups')  # 记录任务分组情况
        # 逐组执行任务
        for i, g in enumerate(groups):
            futures = {self._pool.submit(task.f, *task.args): task for task in g}  # 提交任务到线程池
            for future in as_completed(futures):  # 等待任务完成
                future.result()  # 获取结果，可能抛出异常
            logger.debug(f'[TaskDispatcher] finished group {i + 1}, size: {len(g)}')  # 记录组执行完成


# 获取有向图的逆拓扑排序
def reverse_topo(G: nx.DiGraph) -> List[List[Any]]:
    """获取有向图的逆拓扑排序分组
    
    将图中的节点按照依赖关系分组，同一组内的节点可以并行执行
    组的顺序遵循拓扑排序，后面的组依赖于前面的组
    
    Args:
        G: 有向无环图
        
    Returns:
        分组列表，每组包含可以并行执行的节点
    """
    # 初始化所有节点的出度为分数
    out_degree = {node: G.out_degree(node) for node in G.nodes()}  # 计算每个节点的出度
    scores = {node: -1 for node in G.nodes()}  # -1表示未评分

    # 将所有出度为0且尚未评分的节点加入队列
    queue = deque([node for node, degree in out_degree.items() if degree == 0])

    current_score = 0  # 当前层级分数
    while queue:  # 当队列不为空时
        # 处理当前层的所有节点
        for _ in range(len(queue)):
            node = queue.popleft()  # 取出一个节点
            if scores[node] == -1:  # 确保只评一次分
                scores[node] = current_score  # 设置分数

                # 对于每个邻居，减少其入度；如果入度变为0，则加入队列
                for neighbor in G.predecessors(node):  # 遍历前驱节点（依赖于当前节点的节点）
                    out_degree[neighbor] -= 1  # 减少前驱节点的出度
                    if out_degree[neighbor] == 0:  # 如果前驱节点出度为0
                        queue.append(neighbor)  # 将前驱节点加入队列

        # 进入下一层
        current_score += 1  # 层级分数递增

    # 根据得分对节点进行分组
    groups = defaultdict(list)  # 分数到节点列表的映射
    for node, score in scores.items():
        groups[score].append(node)  # 按分数分组

    return list(map(lambda x: x[1], sorted(groups.items(), key=lambda x: x[0])))  # 返回按分数排序的分组列表


if __name__ == '__main__':
    import time  # 导入time模块，用于示例中的延时


    def task(n):
        """示例任务函数
        
        Args:
            n: 任务编号
        """
        print(f"Task {n} started")  # 打印任务开始
        time.sleep(1)  # 休眠1秒，模拟任务执行
        print(f"Task {n} finished")  # 打印任务完成


    pool = ThreadPoolExecutor(max_workers=4)  # 创建4线程的线程池
    dispatcher = TaskDispatcher(pool)  # 创建任务分发器

    # 创建具有依赖关系的任务
    task1 = Task(f=task, args=1)
    task2 = Task(f=task, args=2, dependencies=[task1])  # 依赖于task1
    task3 = Task(f=task, args=3, dependencies=[task1])  # 依赖于task1
    task4 = Task(f=task, args=4, dependencies=[task2, task3])  # 依赖于task2和task3

    # 添加任务
    dispatcher.add(task1)
    dispatcher.add(task2)
    dispatcher.add(task3)
    dispatcher.add(task4)

    # 执行任务
    dispatcher.run()

    # 使用map方法的示例
    dispatcher2 = TaskDispatcher(pool)  # 创建另一个任务分发器

    # 创建依赖图
    graph = nx.DiGraph()
    graph.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])  # 添加边表示依赖关系

    # 使用map方法从图生成任务
    dispatcher2.map(graph, task)
    # 执行任务
    dispatcher2.run()
