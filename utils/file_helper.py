import io  # 导入io模块，提供处理流的功能
import os  # 导入os模块，提供与操作系统交互的功能
import shutil  # 导入shutil模块，提供高级文件操作功能
import tarfile  # 导入tarfile模块，用于处理tar格式归档文件
import tempfile  # 导入tempfile模块，用于创建临时文件和目录
import zipfile  # 导入zipfile模块，用于处理zip格式归档文件
from abc import abstractmethod, ABCMeta  # 导入抽象基类相关工具，用于定义接口
from typing import Callable, IO, Union, Optional  # 导入类型提示工具

import chardet  # 导入chardet库，用于检测文本编码


class Archive(metaclass=ABCMeta):
    """归档文件抽象基类
    
    定义了处理归档文件的通用接口，为不同类型的归档文件提供统一的操作方法
    支持zip、tar等格式的文件操作
    """

    @abstractmethod
    def get_file_by_name(self, name: str) -> bytes:
        """从归档文件中获取指定名称的文件内容
        
        Args:
            name: 文件名称
            
        Returns:
            文件的二进制内容
        """
        pass

    @abstractmethod
    def decompress(self, path: str) -> Optional[str]:
        """将整个归档文件解压到指定路径
        
        Args:
            path: 目标路径
            
        Returns:
            解压后的路径，如果失败则返回None
        """
        pass

    @abstractmethod
    def decompress_by_name(self, name: str, path: str) -> None:
        """将归档文件中的指定文件解压到目标路径
        
        Args:
            name: 要解压的文件名
            path: 目标路径
        """
        pass

    @abstractmethod
    def iter(self, func: Callable[[str], None]) -> None:
        """遍历归档文件中的所有文件名
        
        Args:
            func: 对每个文件名执行的函数
        """
        pass


class ZipArchive(Archive):
    """Zip格式归档文件处理类
    
    实现了Archive抽象基类，提供对zip格式文件的具体操作
    """

    def __init__(self, f: IO[bytes]):
        """初始化zip归档处理器
        
        Args:
            f: zip文件的二进制流对象
        """
        self._f = zipfile.ZipFile(file=f, mode='r')  # 创建zipfile对象
        self._prefix = ''  # 初始化前缀为空字符串
        # 查找zip文件中可能的公共路径前缀（通常是压缩时的根目录）
        prefix = list(filter(lambda _n: _n.endswith(os.sep) and len(_n.split(os.sep)) == 2, self._f.namelist()))
        if len(prefix) == 1:
            self._prefix = prefix[0]  # 如果找到唯一前缀，则设置为该前缀

    def decompress(self, path: str):
        """解压整个zip文件到指定路径
        
        会检测并处理可能存在的单层嵌套目录结构
        
        Args:
            path: 解压目标路径
            
        Returns:
            解压后的实际路径
        """
        temp_path = tempfile.mkdtemp()  # 创建临时目录
        self._f.extractall(temp_path)  # 解压所有文件到临时目录
        # 处理嵌套情况：如果解压后只有一个目录且没有文件，则移动该目录内容
        while (len(list(filter(lambda f: os.path.isfile(os.path.join(temp_path, f)),os.listdir(temp_path)))) == 0 and
                len(os.listdir(temp_path)) == 1):
            temp_path = os.path.join(temp_path, os.listdir(temp_path)[0])
        shutil.move(temp_path, path)  # 将处理后的内容移动到目标路径


    def decompress_by_name(self, name: str, path: str) -> None:
        """解压zip文件中的指定文件到目标路径
        
        处理路径前缀，确保文件解压到正确位置
        
        Args:
            name: 要解压的文件名
            path: 目标路径
        """
        if self._prefix is not None and len(self._prefix):
            # 如果存在路径前缀，则去除前缀后再解压
            p = os.path.join(path, name.replace(self._prefix, ''))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as fw:
                fw.write(self._f.read(name=name))
        else:
            # 没有前缀则直接解压
            self._f.extract(member=name, path=path)

    def get_file_by_name(self, name: str) -> bytes:
        """获取zip文件中指定文件的内容
        
        Args:
            name: 文件名
            
        Returns:
            文件的二进制内容
        """
        return self._f.read(name=name)

    def iter(self, func: Callable[[str], None]):
        """遍历zip文件中的所有文件名
        
        对每个文件名应用指定的函数
        
        Args:
            func: 要应用的函数
        """
        for name in self._f.namelist():
            func(name)


class TarArchive(Archive):
    """Tar格式归档文件处理类
    
    实现了Archive抽象基类，提供对tar格式文件的具体操作
    支持常见的tar变种，如tar.gz, tar.bz2等
    """
    def __init__(self, f: IO[bytes]):
        """初始化tar归档处理器
        
        Args:
            f: tar文件的二进制流对象
        """
        self._f = tarfile.open(fileobj=f)  # 创建tarfile对象
        self._prefix = ''  # 初始化前缀为空字符串
        # 查找tar文件中可能的公共路径前缀
        prefix = list(filter(lambda _n: len(_n.split(os.sep)) == 1, self._f.getnames()))
        if len(prefix) == 1:
            self._prefix = prefix[0]  # 如果找到唯一前缀，则设置为该前缀

    def decompress(self, path: str):
        """解压整个tar文件到指定路径
        
        会检测并处理可能存在的单层嵌套目录结构
        
        Args:
            path: 解压目标路径
            
        Returns:
            解压后的实际路径
        """
        temp_path = tempfile.mkdtemp()  # 创建临时目录
        self._f.extractall(temp_path)  # 解压所有文件到临时目录
        # 处理嵌套情况：如果解压后只有一个目录且没有文件，则移动该目录内容
        while (len(list(filter(lambda f: os.path.isfile(os.path.join(temp_path,f)),os.listdir(temp_path)))) == 0 and
               len(os.listdir(temp_path)) == 1):
            temp_path =os.path.join(temp_path, os.listdir(temp_path)[0])
        shutil.move(temp_path, path)  # 将处理后的内容移动到目标路径


    def decompress_by_name(self, name: str, path: str) -> None:
        """解压tar文件中的指定文件到目标路径
        
        处理路径前缀，确保文件解压到正确位置
        
        Args:
            name: 要解压的文件名
            path: 目标路径
        """
        if self._prefix is not None and len(self._prefix):
            # 如果存在路径前缀，则去除前缀后再解压
            p = os.path.join(path, name.replace(self._prefix, ''))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with self._f.extractfile(member=name) as fr, open(p, 'wb') as fw:
                fw.write(fr.read())
        else:
            # 没有前缀则直接解压
            self._f.extract(member=name, path=path)

    def get_file_by_name(self, name: str) -> bytes:
        """获取tar文件中指定文件的内容
        
        Args:
            name: 文件名
            
        Returns:
            文件的二进制内容
        """
        return self._f.extractfile(member=name).read()

    def iter(self, func: Callable[[str], None]):
        """遍历tar文件中的所有文件名
        
        对每个文件名应用指定的函数
        
        Args:
            func: 要应用的函数
        """
        for name in self._f.getnames():
            func(name)


def resolve_archive(data: Union[bytes, IO[bytes]]) -> Archive:
    """识别并解析归档文件
    
    根据文件内容自动识别归档类型，并返回相应的处理器
    
    Args:
        data: 归档文件的二进制内容或流对象
        
    Returns:
        对应类型的归档处理器
    """
    f: IO[bytes] = data
    if isinstance(data, bytes):
        f = io.BytesIO(data)  # 如果是字节数据，转换为内存流
    archive = None
    # 检测是否为zip文件
    if zipfile.is_zipfile(f):
        archive = ZipArchive(f)
    # 检测是否为tar文件
    elif is_tarfile(f):
        archive = TarArchive(f)
    return archive


def is_tarfile(f: IO[bytes]) -> bool:
    """检测文件是否为tar格式
    
    尝试使用tarfile打开文件，根据结果判断是否为tar格式
    
    Args:
        f: 文件流对象
        
    Returns:
        布尔值，表示是否为tar文件
    """
    try:
        f.seek(0)  # 将文件指针移动到开头
        tarfile.open(fileobj=f, mode='r')  # 尝试以tar格式打开
    except tarfile.TarError:
        return False  # 如果出错，则不是tar文件
    f.seek(0)  # 重置文件指针
    return True  # 如果成功，则是tar文件


def is_text(b):
    """检测数据是否为文本内容
    
    使用chardet库检测字节数据的编码，判断是否为文本文件
    
    Args:
        b: 要检测的字节数据
        
    Returns:
        布尔值，表示是否为文本数据
    """
    return chardet.detect(b)['encoding'] is not None  # 如果能检测到编码，则是文本文件