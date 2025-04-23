import os  # 导入操作系统模块，用于文件和路径操作
from abc import ABCMeta, abstractmethod  # 导入抽象基类和抽象方法，用于定义接口
from dataclasses import dataclass, field  # 导入数据类装饰器和field工具，用于定义数据类
from typing import List, TypeVar, Optional, Type, Iterator  # 导入类型提示工具

import networkx as nx  # 导入networkx库，用于处理和分析图结构

from utils import LangEnum  # 导入自定义的语言枚举
from .doc import ApiDoc, ClazzDoc, ModuleDoc, Doc, RepoDoc  # 导入文档相关的类


# 变量定义
@dataclass
class FieldDef:
    """
    字段定义类，用于表示变量、属性或参数的定义
    """
    name: str  # 变量名称
    symbol: str  # 变量类型
    access: str = 'public'  # 访问权限，public/protected/private，作为函数参数时没有意义


# 函数定义
@dataclass
class FuncDef:
    """
    函数定义类，用于表示函数或方法的定义及其属性
    """
    symbol: str  # 函数名
    code: str  # 源代码
    filename: str  # 源代码文件名称
    visible: bool = True  # 可见性，指是否对三方软件可见
    access: str = 'public'  # 访问权限，public/protected/private
    params: List[FieldDef] = field(default_factory=list)  # 函数参数，默认为空

    # return_type: FieldDef = None # 函数返回值类型，默认为空

    def __hash__(self):
        """
        哈希方法，用于将函数对象作为字典键或集合元素
        
        Returns:
            函数符号的哈希值
        """
        return hash(self.symbol)

    def __eq__(self, other):
        """
        相等性比较方法
        
        Args:
            other: 要比较的对象
            
        Returns:
            布尔值，表示两个对象是否相等
        """
        if not isinstance(other, FuncDef):
            return False
        return self.symbol == other.symbol


# 类定义
@dataclass
class ClazzDef:
    """
    类定义，表示一个类的结构及其属性
    """
    symbol: str  # 类名
    code: str  # 源代码
    fields: List[FieldDef]  # 类属性
    functions: List[FuncDef]  # 类方法
    filename: str  # 源代码文件名称
    visible: bool = True  # 可见性，指是否对三方软件可见

    def __hash__(self):
        """
        哈希方法，用于将类对象作为字典键或集合元素
        
        Returns:
            类符号的哈希值
        """
        return hash(self.symbol)

    def __eq__(self, other):
        """
        相等性比较方法
        
        Args:
            other: 要比较的对象
            
        Returns:
            布尔值，表示两个对象是否相等
        """
        if not isinstance(other, ClazzDef):
            return False
        return self.symbol == other.symbol


# 定义泛型类型变量T，限制为Doc的子类
T = TypeVar('T', bound=Doc)


@dataclass
class EvaContext:
    """
    评估上下文类，存储分析过程中的状态和结果，提供文档读写方法
    """
    doc_path: str  # 文档存储路径
    resource_path: str  # 源代码路径
    output_path: str  # 中间产物存储路径
    lang: LangEnum  # 语言类型

    # 软件的函数调用图，用法：
    # - ctx.func_iter(), callgraph.nodes(data=True) 遍历软件内所有函数
    # - ctx.func('ex'), callgraph.nodes['ex']['attr'] 查找函数ex的FuncDef
    # - callgraph.nodes['ex'].successors() 查找函数ex调用的函数
    # - callgraph.nodes['ex'].predecessors() 查找调用函数ex的函数
    callgraph: nx.DiGraph = None  # 函数调用图，表示函数之间的调用关系
    
    # 软件的类调用图，用法：
    # - ctx.clazz_iter(), clazz_callgraph.nodes(data=True) 遍历软件内所有类
    # - ctx.clazz('ex'), clazz_callgraph.nodes['ex']['attr'] 查找类ex的ClazzDef
    # - clazz_callgraph.nodes['ex'].successors() 查找类ex引用的类
    # - clazz_callgraph.nodes['ex'].predecessors() 查找引用类ex的类
    clazz_callgraph: nx.DiGraph = None  # 类调用图，表示类之间的依赖关系

    # 软件的文件结构，字符串表示，例如：
    # dir1
    #   file1
    #   file2
    # dir2
    #   dir3
    #     file3
    # TODO: 改为类
    structure: str = None  # 文件结构的字符串表示

    def func(self, symbol: str) -> FuncDef:
        """
        通过函数名获取函数定义
        
        Args:
            symbol: 函数符号名
            
        Returns:
            对应的函数定义对象
        """
        return self.callgraph.nodes[symbol]['attr']

    def clazz(self, symbol: str) -> ClazzDef:
        """
        通过类名获取类定义
        
        Args:
            symbol: 类符号名
            
        Returns:
            对应的类定义对象
        """
        return self.clazz_callgraph.nodes[symbol]['attr']

    def func_iter(self) -> Iterator[FuncDef]:
        """
        获取全部函数定义的迭代器
        
        Returns:
            函数定义对象的迭代器
        """
        return iter(self.callgraph.nodes[symbol]['attr'] for symbol in self.callgraph.nodes())

    def clazz_iter(self) -> Iterator[ClazzDef]:
        """
        获取全部类定义的迭代器
        
        Returns:
            类定义对象的迭代器
        """
        return iter(self.clazz_callgraph.nodes[symbol]['attr'] for symbol in self.clazz_callgraph.nodes())

    @staticmethod
    def save_doc(filename: str, doc: Doc):
        """
        通用的文档写入方法
        
        Args:
            filename: 完整的文件路径名
            doc: 文档对象
        """
        _dir = os.path.dirname(filename)  # 获取目录路径
        if _dir:  # 如果目录不为空
            os.makedirs(_dir, exist_ok=True)  # 创建目录，如果已存在则不报错
        with open(filename, 'a') as t:  # 以追加模式打开文件
            t.write(doc.markdown() + '\n')  # 写入文档的Markdown表示

    @staticmethod
    def load_docs(filename: str, doc_type: Type[Doc]) -> List[T]:
        """
        通用的文档读取方法，加载指定类型的所有文档
        
        Args:
            filename: 完整的文件路径名
            doc_type: 文档类型
            
        Returns:
            文档对象列表
        """
        if not os.path.exists(filename):  # 如果文件不存在
            return []  # 返回空列表
        with open(filename, 'r') as t:  # 以读模式打开文件
            docs = doc_type.from_doc(t.read())  # 从文件内容解析文档
            return docs  # 返回文档列表

    @staticmethod
    def load_doc(symbol: str, filename: str, doc: Type[Doc]) -> Optional[Doc]:
        """
        通用的文档读取方法，加载指定符号的文档
        
        Args:
            symbol: 符号名称
            filename: 完整的文件路径名
            doc: 文档类型
            
        Returns:
            找到的文档对象，如果未找到则返回None
        """
        docs = EvaContext.load_docs(filename, doc)  # 加载所有文档
        for d in docs:  # 遍历文档
            if d.name == symbol:  # 如果找到匹配的文档
                return d  # 返回该文档
        return None  # 未找到则返回None

    def save_function_doc(self, symbol: str, doc: ApiDoc):
        """
        通过函数名写入函数文档
        
        Args:
            symbol: 函数符号名
            doc: API文档对象
        """
        func_def: FuncDef = self.func(symbol)  # 获取函数定义
        self.save_doc(os.path.join(self.doc_path, f'{func_def.filename}.{ApiDoc.doc_type()}.md'), doc)  # 保存文档

    def load_function_doc(self, symbol: str) -> Optional[ApiDoc]:
        """
        通过函数名加载函数文档
        
        Args:
            symbol: 函数符号名
            
        Returns:
            加载的API文档对象，如果未找到则返回None
        """
        func_def: FuncDef = self.func(symbol)  # 获取函数定义
        return self.load_doc(symbol, os.path.join(self.doc_path, f'{func_def.filename}.{ApiDoc.doc_type()}.md'),
                             ApiDoc)  # 加载文档

    def save_clazz_doc(self, symbol: str, doc: ClazzDoc):
        """
        通过类名写入类文档
        
        Args:
            symbol: 类符号名
            doc: 类文档对象
        """
        clazz_def: ClazzDef = self.clazz(symbol)  # 获取类定义
        self.save_doc(os.path.join(self.doc_path, f'{clazz_def.filename}.{ClazzDoc.doc_type()}.md'), doc)  # 保存文档

    def load_clazz_doc(self, symbol: str) -> Optional[ClazzDoc]:
        """
        通过类名加载类文档
        
        Args:
            symbol: 类符号名
            
        Returns:
            加载的类文档对象，如果未找到则返回None
        """
        clazz_def: ClazzDef = self.clazz(symbol)  # 获取类定义
        return self.load_doc(symbol, os.path.join(self.doc_path, f'{clazz_def.filename}.{ClazzDoc.doc_type()}.md'),
                             ClazzDoc)  # 加载文档

    def save_module_doc(self, doc: ModuleDoc):
        """
        写入单个模块文档
        
        Args:
            doc: 模块文档对象
        """
        self.save_doc(os.path.join(self.doc_path, 'modules.md'), doc)  # 保存文档

    def load_module_docs(self) -> List[ModuleDoc]:
        """
        读取所有模块文档
        
        Returns:
            模块文档对象列表
        """
        return self.load_docs(os.path.join(self.doc_path, 'modules.md'), ModuleDoc)  # 加载文档

    def save_repo_doc(self, doc):
        """
        写入仓库文档
        
        Args:
            doc: 仓库文档对象
        """
        self.save_doc(os.path.join(self.doc_path, 'repo.md'), doc)  # 保存文档

    def load_repo_doc(self) -> Optional[RepoDoc]:
        """
        读取仓库文档
        
        Returns:
            仓库文档对象，如果未找到则返回None
        """
        docs = self.load_docs(os.path.join(self.doc_path, 'repo.md'), RepoDoc)  # 加载文档
        if len(docs) == 0:  # 如果没有找到文档
            return None  # 返回None
        return docs[0]  # 返回第一个仓库文档


# 度量指标的基类，接受EvaContext作为参数，将被其他指标依赖的度量结果写回EvaContext
class Metric(metaclass=ABCMeta):
    """
    度量指标的抽象基类，定义了所有度量指标的共同接口
    使用ABCMeta元类来确保子类实现抽象方法
    """
    @abstractmethod
    def eva(self, ctx: EvaContext):
        """
        评估方法，是所有度量指标必须实现的抽象方法
        
        Args:
            ctx: 评估上下文对象，包含分析所需的所有信息
        """
        pass