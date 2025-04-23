from concurrent.futures.thread import ThreadPoolExecutor  # 导入线程池执行器
from dataclasses import field, dataclass  # 导入数据类相关工具
from enum import StrEnum  # 导入字符串枚举类型
from typing import Any  # 导入Any类型

from decouple import config  # 导入配置工具，用于从环境变量或.env文件加载配置
from loguru import logger  # 导入日志记录器
from transformers import AutoTokenizer, AutoModel  # 导入Hugging Face模型相关工具


class LogLevel(StrEnum):
    """日志级别枚举
    
    定义了系统支持的日志记录级别，从调试到严重错误
    与标准日志库的级别对应
    """
    DEBUG = "DEBUG"  # 调试级别，最详细的日志信息
    INFO = "INFO"  # 信息级别，一般运行信息
    WARNING = "WARNING"  # 警告级别，潜在问题
    ERROR = "ERROR"  # 错误级别，影响功能的错误
    CRITICAL = "CRITICAL"  # 严重级别，系统崩溃级别的错误


@dataclass
class ProjectSettings:
    """项目全局设置类
    
    包含项目的基本配置参数，如日志级别
    使用dataclass简化数据类的创建
    """
    # 从环境变量或.env文件加载日志级别，默认为INFO
    log_level: LogLevel = field(default_factory=lambda: config('LOG_LEVEL', cast=LogLevel, default=LogLevel.INFO))

    def is_debug(self):
        """检查是否为调试模式
        
        Returns:
            布尔值，表示当前是否处于调试模式
        """
        return self.log_level == LogLevel.DEBUG


# 创建线程池：调试模式下使用1个线程，否则使用16个线程
# 调试模式下单线程便于追踪问题，生产环境多线程提高性能
llm_thread_pool = ThreadPoolExecutor(1) if ProjectSettings().is_debug() else ThreadPoolExecutor(16)


@dataclass
class ChatCompletionSettings:
    """聊天完成设置类
    
    包含与大语言模型API通信的所有配置参数
    设置模型类型、温度、超时等参数
    """
    # 从环境变量加载API密钥
    openai_api_key: str = field(default_factory=lambda: config('OPENAI_API_KEY'))
    # 从.env文件加载API基础URL
    openai_base_url: str = field(default_factory=lambda: config('OPENAI_BASE_URL'))
    # 请求超时时间，默认30秒
    request_timeout: int = field(default_factory=lambda: config('MODEL_TIMEOUT', cast=int, default=30))
    # 使用的模型名称
    model: str = field(default_factory=lambda: config('MODEL'))
    # 模型温度参数，控制输出的随机性，默认为0（最确定性）
    temperature: float = field(default_factory=lambda: config('MODEL_TEMPERATURE', cast=float, default=0))
    # 模型输出的语言，默认为中文
    language: str = field(default_factory=lambda: config('MODEL_LANGUAGE', default='Chinese'))
    # 历史记录最大长度，默认为-1（无限制）
    history_max: int = field(default_factory=lambda: config('HISTORY_MAX', cast=int, default=-1))


@dataclass
class RagSettings:
    """检索增强生成(RAG)设置类
    
    包含与检索增强生成相关的配置参数
    设置Tokenizer、模型和嵌入维度等
    """
    # 加载分词器，默认使用'Amu/tao-8k'
    tokenizer: Any = field(default_factory=lambda: config('TOKENIZER', default='Amu/tao-8k',
                                                          cast=lambda x: AutoTokenizer.from_pretrained(x)))
    # 加载模型，默认使用'Amu/tao-8k'
    model: Any = field(default_factory=lambda: config('TOKENIZER_MODEL', default='Amu/tao-8k',
                                                      cast=lambda x: AutoModel.from_pretrained(x)))
    # 嵌入向量维度，默认为1024
    dim: int = field(default_factory=lambda: config('TOKENIZER_DIM', cast=int, default=1024))


# 配置日志记录器，设置日志文件、级别、轮换和保留策略
logger.add('application.log', level=ProjectSettings().log_level, rotation='1 day', retention='7 days', encoding='utf-8')
