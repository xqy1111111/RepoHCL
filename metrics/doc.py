from __future__ import annotations  # 启用未来版本的注解特性，允许在类型注解中使用尚未定义的类

import re  # 导入正则表达式模块，用于文本解析
from abc import abstractmethod, ABC  # 导入抽象基类和抽象方法，用于定义接口
from typing import List, Optional, override, TypeVar  # 导入类型提示工具

from pydantic import BaseModel, field_serializer  # 导入pydantic库的工具，用于数据验证和序列化

# T 表示Doc的子类，在Python中仅用于类型提示
T = TypeVar('T', bound='Doc')
# 文档对象基类，描述了怎么从md文件中解析出文档对象，如何将文档对象转化为md文件
class Doc(ABC, BaseModel):
    """
    文档对象的抽象基类，提供了从Markdown文件解析和生成Markdown的通用方法
    
    继承自ABC和BaseModel，既是抽象类又是数据模型
    """
    name: str  # 符号名称
    description: str  # 符号描述

    # 读取字符串，返回其中的所有文档对象
    @classmethod
    def from_doc(cls, s: str) -> List[T]:
        """
        从Markdown字符串中解析出所有文档对象
        
        使用正则表达式匹配以"###"开头的章节，每个章节对应一个文档对象
        
        Args:
            s: Markdown格式的字符串
            
        Returns:
            文档对象列表
        """
        function_pattern = re.compile(r'(###.*?)(?=\n### |\Z)', re.DOTALL)  # 匹配章节的正则表达式
        res: List[Doc] = []  # 初始化结果列表
        for match in function_pattern.finditer(s):  # 遍历所有匹配的章节
            res.append(cls.from_chapter(match.group(1)))  # 解析章节并添加到结果列表
        return res  # 返回所有文档对象

    # 读取字符串，返回其中的一个文档对象
    @classmethod
    def from_chapter(cls, s: str) -> T:
        """
        从一个Markdown章节字符串中解析出一个文档对象
        
        Args:
            s: 表示一个章节的Markdown字符串
            
        Returns:
            解析出的文档对象
        """
        module_pattern = re.search(r'### (.*?)\n(.*?)(?=\n### |\Z)', s, re.DOTALL)  # 匹配章节标题和内容
        name = module_pattern.group(1).strip()  # 提取名称
        block = module_pattern.group(2)  # 提取内容块
        return cls.from_chapter_hook(cls(name=name, description=cls.from_block(block, 'Description')), block)  # 创建并返回文档对象

    # 读取字符串，为文档对象附加属性
    @classmethod
    @abstractmethod
    def from_chapter_hook(cls, doc, block: str):
        """
        为文档对象附加额外属性的钩子方法
        
        这是一个抽象方法，需要子类实现
        
        Args:
            doc: 文档对象
            block: 内容块字符串
            
        Returns:
            更新后的文档对象
        """
        pass

    # 读取字符串block，返回 header（#### 四级标题）下的内容
    @classmethod
    def from_block(cls, block: str, header: str) -> Optional[str]:
        """
        从内容块中提取指定标题下的内容
        
        Args:
            block: 内容块字符串
            header: 要查找的标题
            
        Returns:
            标题下的内容，如果未找到则返回None
        """
        match = re.search(f'#### {header}' + r'(.*?)(?=####|\Z)', block, re.DOTALL)  # 匹配标题和内容
        content = match.group(1).strip() if match else None  # 提取内容并去除首尾空白
        return content  # 返回内容

    # 将文档对象转化为markdown格式的字符串
    def markdown(self) -> str:
        """
        将文档对象转换为Markdown格式的字符串
        
        Returns:
            Markdown格式的字符串
        """
        md = f'### {self.name}\n#### Description\n{self.description}\n\n'  # 基础Markdown格式
        return md + self._markdown_hook()  # 添加子类特定的内容

    # 使用文档对象的属性，为markdown附加内容
    @abstractmethod
    def _markdown_hook(self) -> str:
        """
        为Markdown输出添加子类特定内容的钩子方法
        
        这是一个抽象方法，需要子类实现
        
        Returns:
            子类特定的Markdown内容
        """
        pass

    # 文档对象类型
    @classmethod
    @abstractmethod
    def doc_type(cls) -> str:
        """
        返回文档类型的标识符
        
        这是一个抽象方法，需要子类实现
        
        Returns:
            表示文档类型的字符串
        """
        pass


# 函数文档
class ApiDoc(Doc):
    """
    API文档类，用于表示函数的文档
    
    继承自Doc，添加了函数特有的属性
    """
    detail: Optional[str] = None  # 函数的详细描述
    example: Optional[str] = None  # 函数的使用示例
    parameters: Optional[str] = None  # 函数的参数列表
    code: Optional[str] = None  # 函数的源代码

    @classmethod
    @override
    def from_chapter_hook(cls, doc: ApiDoc, block: str) -> ApiDoc:
        """
        从章节内容块中提取API文档的特有属性
        
        Args:
            doc: API文档对象
            block: 内容块字符串
            
        Returns:
            更新后的API文档对象
        """
        doc.detail = cls.from_block(block, 'Code Details')  # 提取代码细节
        doc.example = cls.from_block(block, 'Example')  # 提取示例
        doc.parameters = cls.from_block(block, 'Parameters')  # 提取参数
        doc.code = cls.from_block(block, 'Source Code')  # 提取源代码
        return doc  # 返回更新后的文档

    @override
    def _markdown_hook(self) -> str:
        """
        生成API文档特有的Markdown内容
        
        Returns:
            Markdown格式的字符串
        """
        md = ''  # 初始化空字符串
        if self.parameters is not None:  # 如果有参数
            md += f'#### Parameters\n{self.parameters}\n\n'  # 添加参数部分
        if self.detail is not None:  # 如果有细节
            md += '#### Code Details\n{details}\n\n'.format(details=self.detail)  # 添加细节部分
        if self.example is not None:  # 如果有示例
            md += f'#### Example\n{self.example}\n\n'  # 添加示例部分
        if self.code is not None:  # 如果有源代码
            md += f'#### Source Code\n{self.code}\n\n'  # 添加源代码部分
        return md.strip()  # 返回去除首尾空白的字符串

    @classmethod
    @override
    def doc_type(cls) -> str:
        """
        返回API文档的类型标识符
        
        Returns:
            "function"字符串
        """
        return 'function'  # 返回函数类型标识符


# 类文档
class ClazzDoc(Doc):
    """
    类文档，用于表示类的文档
    
    继承自Doc，添加了类特有的属性
    """
    detail: Optional[str] = None  # 类的详细描述
    attributes: Optional[str] = None  # 类的属性列表

    @classmethod
    @override
    def from_chapter_hook(cls, doc: ClazzDoc, block: str) -> ClazzDoc:
        """
        从章节内容块中提取类文档的特有属性
        
        Args:
            doc: 类文档对象
            block: 内容块字符串
            
        Returns:
            更新后的类文档对象
        """
        doc.detail = cls.from_block(block, 'Code Details')  # 提取代码细节
        doc.attributes = cls.from_block(block, 'Attributes')  # 提取属性
        return doc  # 返回更新后的文档

    @override
    def _markdown_hook(self) -> str:
        """
        生成类文档特有的Markdown内容
        
        Returns:
            Markdown格式的字符串
        """
        md = ''  # 初始化空字符串
        if self.attributes is not None:  # 如果有属性
            md += f'#### Attributes\n{self.attributes}\n\n'  # 添加属性部分
        md += '#### Code Details\n{details}\n\n'.format(details=self.detail)  # 添加细节部分
        return md.strip()  # 返回去除首尾空白的字符串

    @classmethod
    @override
    def doc_type(cls) -> str:
        """
        返回类文档的类型标识符
        
        Returns:
            "class"字符串
        """
        return 'class'  # 返回类型标识符


# 模块文档
class ModuleDoc(Doc):
    """
    模块文档，用于表示模块的文档
    
    继承自Doc，添加了模块特有的属性
    """
    example: Optional[str] = None  # 模块的使用示例
    functions: List[str] = None  # 模块的函数列表

    # 将字符串列表格式的函数列表在JSON序列化时，转为markdown格式的字符串
    @field_serializer('functions')
    def functions_serializer(self, v: List[str], _info) -> str:
        """
        将函数列表序列化为Markdown格式的字符串
        
        Args:
            v: 函数名称列表
            _info: 序列化信息
            
        Returns:
            Markdown格式的函数列表
        """
        return '\n'.join(map(lambda x: f'- {x}', v))  # 将每个函数名格式化为列表项

    @classmethod
    @override
    def from_chapter_hook(cls, doc: ModuleDoc, block: str) -> ModuleDoc:
        """
        从章节内容块中提取模块文档的特有属性
        
        Args:
            doc: 模块文档对象
            block: 内容块字符串
            
        Returns:
            更新后的模块文档对象
        """
        function_doc = cls.from_block(block, 'Functions')  # 提取函数部分
        doc.functions = list(filter(lambda x: len(x), map(lambda x: x.strip('- '), function_doc.splitlines())))  # 解析函数列表
        doc.example = cls.from_block(block, 'Use Case')  # 提取使用案例
        return doc  # 返回更新后的文档

    @override
    def _markdown_hook(self) -> str:
        """
        生成模块文档特有的Markdown内容
        
        Returns:
            Markdown格式的字符串
        """
        md = ''  # 初始化空字符串
        if self.functions:  # 如果有函数列表
            md += '#### Functions\n{}\n\n'.format('\n'.join(map(lambda x: f'- {x}', self.functions)))  # 添加函数列表部分
        if self.example:  # 如果有使用案例
            md += f'#### Use Case\n{self.example}\n\n'  # 添加使用案例部分
        return md.strip()  # 返回去除首尾空白的字符串

    @classmethod
    @override
    def doc_type(cls) -> str:
        """
        返回模块文档的类型标识符
        
        Returns:
            "module"字符串
        """
        return 'module'  # 返回类型标识符


# 仓库文档
class RepoDoc(Doc):
    """
    仓库文档，用于表示整个代码仓库的文档
    
    继承自Doc，添加了仓库特有的属性
    """
    features: List[str] = None  # 仓库的功能列表
    standards: List[str] = None  # 仓库的协议列表
    scenarios: List[str] = None  # 仓库的场景列表

    # 将字符串列表格式的功能列表在JSON序列化时，转为markdown格式的字符串
    @field_serializer('features', 'standards', 'scenarios')
    def features_serializer(self, v: List[str], _info) -> str:
        """
        将特性、标准和场景列表序列化为Markdown格式的字符串
        
        Args:
            v: 特性、标准或场景名称列表
            _info: 序列化信息
            
        Returns:
            Markdown格式的列表
        """
        return '\n'.join(map(lambda x: f'- {x}', v))  # 将每个项目格式化为列表项

    @classmethod
    @override
    def from_chapter_hook(cls, doc: RepoDoc, block: str) -> RepoDoc:
        """
        从章节内容块中提取仓库文档的特有属性
        
        Args:
            doc: 仓库文档对象
            block: 内容块字符串
            
        Returns:
            更新后的仓库文档对象
        """
        features_doc = cls.from_block(block, 'Features')  # 提取特性部分
        doc.features = list(filter(lambda x: len(x), map(lambda x: x.strip('- '), features_doc.splitlines())))  # 解析特性列表
        standards_doc = cls.from_block(block, 'Standards')  # 提取标准部分
        doc.standards = list(filter(lambda x: len(x), map(lambda x: x.strip('- '), standards_doc.splitlines())))  # 解析标准列表
        scenarios_doc = cls.from_block(block, 'Scenarios')  # 提取场景部分
        if scenarios_doc:  # 如果有场景部分
            doc.scenarios = list(filter(lambda x: len(x), map(lambda x: x.strip('- '), scenarios_doc.splitlines())))  # 解析场景列表
        return doc  # 返回更新后的文档

    @override
    def _markdown_hook(self) -> str:
        """
        生成仓库文档特有的Markdown内容
        
        Returns:
            Markdown格式的字符串
        """
        md = '#### Features\n{}\n\n'.format('\n'.join(map(lambda x: f'- {x}', self.features)))  # 添加特性列表部分
        md += '#### Standards\n{}\n\n'.format('\n'.join(map(lambda x: f'- {x}', self.standards)))  # 添加标准列表部分
        if self.scenarios:  # 如果有场景列表
            md += '#### Scenarios\n{}\n\n'.format('\n'.join(map(lambda x: f'- {x}', self.scenarios)))  # 添加场景列表部分
        return md.strip()  # 返回去除首尾空白的字符串

    @classmethod
    @override
    def doc_type(cls) -> str:
        """
        返回仓库文档的类型标识符
        
        Returns:
            "repo"字符串
        """
        return 'repo'  # 返回类型标识符
