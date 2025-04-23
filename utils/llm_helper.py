import json  # 导入json模块，用于处理JSON数据
import time  # 导入time模块，用于处理时间相关操作
from typing import Callable  # 导入Callable类型，用于函数类型提示

from loguru import logger  # 导入日志记录工具
from openai import OpenAI, Stream  # 导入OpenAI客户端和Stream类型
from openai.types.chat import ChatCompletionChunk  # 导入聊天完成块类型
from httpx import ReadTimeout  # 导入超时异常

from .settings import ProjectSettings, ChatCompletionSettings  # 导入项目设置和聊天完成设置

# 通用的LLM代理
class SimpleLLM:
    """
    简单的LLM客户端类，封装了与OpenAI模型交互的基本功能
    
    提供了添加消息、发送请求和处理响应的方法
    """
    def __init__(self, setting: ChatCompletionSettings):
        """
        初始化LLM客户端
        
        Args:
            setting: 聊天完成设置对象
        """
        self._setting = setting  # 保存设置
        self._llm = OpenAI(
            api_key=self._setting.openai_api_key,  # 设置API密钥
            base_url=self._setting.openai_base_url,  # 设置API基础URL
            timeout=self._setting.request_timeout,  # 设置请求超时时间
            max_retries=5,  # 设置最大重试次数
        )  # 创建OpenAI客户端
        self._history = []  # 初始化对话历史

    def add_system_msg(self, content: str):
        """
        添加系统消息到对话历史
        
        Args:
            content: 消息内容
            
        Returns:
            self，用于链式调用
        """
        self._history.append({'role': 'system', 'content': content})  # 添加系统消息
        return self  # 返回self用于链式调用

    def add_user_msg(self, content: str):
        """
        添加用户消息到对话历史
        
        Args:
            content: 消息内容
            
        Returns:
            self，用于链式调用
        """
        self._history.append({'role': 'user', 'content': content})  # 添加用户消息
        return self  # 返回self用于链式调用

    def _add_response(self, content: str):
        """
        添加助手响应到对话历史
        
        Args:
            content: 响应内容
            
        Returns:
            self，用于链式调用
        """
        self._history.append({'role': 'assistant', 'content': content})  # 添加助手响应
        return self  # 返回self用于链式调用

    def _add_language_msg(self):
        """
        添加语言指令消息，要求模型用指定语言输出
        
        指定语言来自设置，但允许在分析和描述中使用英文单词，以提高可读性
        """
        self.add_user_msg(f'You must output in {self._setting.language} though the prompt is written in English.'
                          "You can write with some English words in the analysis and description "
                          "to enhance the document's readability because you do not need to translate the function name or variable name into the target language.\n")  # 添加语言指令

    def ask(self, post_processor: Callable[[str], str] = None) -> str:
        """
        向模型发送请求并获取响应
        
        支持流式响应和后处理函数
        
        Args:
            post_processor: 可选的响应后处理函数
            
        Returns:
            模型的响应内容
            
        Raises:
            各种异常：请求过程中可能发生的异常
        """
        try:
            self._add_language_msg()  # 添加语言指令
            response = self._llm.chat.completions.create(
                model=self._setting.model,  # 使用设置的模型
                messages=self._history,  # 传入对话历史
                temperature=self._setting.temperature,  # 设置温度参数
                stream=True,  # 启用流式响应
                stream_options={'include_usage': True}  # 包含使用统计
            )  # 创建聊天完成请求
            res = self._get_stream_response(response)  # 处理流式响应
            if post_processor:  # 如果有后处理函数
                res = post_processor(res)  # 应用后处理
            self._add_response(res)  # 将响应添加到历史
            return res  # 返回响应
        except ReadTimeout as e:  # 捕获超时异常
            logger.warning(f"[SimpleLLM] Timeout in chat call.")  # 记录警告
            time.sleep(1)  # 等待1秒
            return self.ask(post_processor)  # 重试请求
        except Exception as e:  # 捕获其他异常
            logger.error(f"[SimpleLLM] Error in chat call: {e}")  # 记录错误
            raise e  # 重新抛出异常

    def _get_stream_response(self, response: Stream[ChatCompletionChunk]) -> str:
        """处理流式响应，累积结果并处理调试输出
        
        逐块处理模型的流式响应，区分思考过程和回答内容，并根据调试模式设置进行输出
        
        Args:
            response: OpenAI的流式响应对象
            
        Returns:
            累积的完整响应文本
        """
        is_thinking = False  # 是否在思考模式的标志
        answer_content = ''  # 初始化响应内容
        for chunk in response:  # 遍历响应块
            if chunk.choices:  # 如果有选择
                delta = chunk.choices[0].delta  # 获取增量内容
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:  # 如果有推理内容
                    if not ProjectSettings().is_debug():  # 如果不是调试模式
                        continue  # 跳过
                    # 打印思考过程
                    if not is_thinking:  # 如果不在思考模式
                        print('=' * 10 + 'thinking' + '=' * 10)  # 打印思考标记
                        is_thinking = True  # 设置思考模式
                    print(delta.reasoning_content, end='', flush=True)  # 打印推理内容
                else:  # 如果是普通内容
                    answer_content += delta.content  # 累加响应内容
                    if not ProjectSettings().is_debug():  # 如果不是调试模式
                        continue  # 跳过
                    # 打印回复过程
                    if is_thinking:  # 如果在思考模式
                        print('\n' + '=' * 10 + 'answering' + '=' * 10)  # 打印回复标记
                        is_thinking = False  # 退出思考模式
                    print(delta.content, end='', flush=True)  # 打印内容


            if chunk.usage:  # 如果有使用统计
                if ProjectSettings().is_debug():  # 如果是调试模式
                    print()  # 打印换行
                logger.debug(
                    f'[SimpleLLM] chat {chunk.id}: token usage(prompt {chunk.usage.prompt_tokens}, response {chunk.usage.completion_tokens}')  # 记录令牌使用情况

        if ProjectSettings().is_debug():  # 如果是调试模式
            with open('prompt.md', 'a') as d:  # 打开提示文件
                d.write('\n'.join(list(map(lambda s: s.get('content'), self._history))) + '\n\n---\n\n')  # 写入对话历史
        return answer_content  # 返回完整响应

    def add_file(self, path: str):
        """添加文件到对话
        
        将指定路径的文件上传至OpenAI并添加到对话上下文中
        
        Args:
            path: 文件路径
            
        Returns:
            self，用于链式调用
            
        Raises:
            各种异常：文件操作和请求过程中可能发生的异常
        """
        try:
            # TODO file-extract 可能是qwen-long专用
            response = self._llm.files.create(file=open(path, 'rb'), purpose='file-extract')  # 上传文件
            self.add_system_msg(f'fileid://{response.id}')  # 添加文件ID消息
            return self  # 返回self用于链式调用
        except Exception as e:  # 捕获异常
            logger.error(f"[SimpleLLM] Error in add file: {e}")  # 记录错误
            raise e  # 重新抛出异常


# TODO, 未接入流式API，不支持debug
class ToolsLLM(SimpleLLM):
    """
    支持工具调用的LLM客户端类
    
    继承自SimpleLLM，添加了工具调用的功能
    
    注意：尚未接入流式API，不支持调试
    """
    def __init__(self, setting: ChatCompletionSettings, tools, tools_map):
        """
        初始化工具LLM客户端
        
        Args:
            setting: 聊天完成设置对象
            tools: 工具描述列表
            tools_map: 工具名称到函数的映射
        """
        self._tools = tools  # 保存工具描述
        self._toolsMap = tools_map  # 保存工具映射
        super().__init__(setting)  # 调用父类初始化

    def ask(self, post_processor: Callable[[str], str] = None) -> str:
        """
        向模型发送请求，支持工具调用
        
        如果模型响应中包含工具调用，则执行相应工具并继续对话
        
        Args:
            post_processor: 可选的响应后处理函数
            
        Returns:
            模型的最终响应内容
            
        Raises:
            各种异常：请求过程中可能发生的异常
        """
        try:
            response = self._llm.chat.completions.create(
                model=self._setting.model,  # 使用设置的模型
                messages=self._history,  # 传入对话历史
                temperature=self._setting.temperature,  # 设置温度参数
                tools=self._tools  # 传入工具描述
            )  # 创建聊天完成请求
            logger.info(
                f'[ToolsLLM] chat {response.id}: token usage(prompt {response.usage.prompt_tokens}, response {response.usage.completion_tokens})')  # 记录令牌使用情况
            if response.choices[0].message.tool_calls:  # 如果有工具调用
                logger.info(f'[ToolsLLM] chat {response.id}: tool call{response.choices[0].message.tool_calls}')  # 记录工具调用
                for tool_call in response.choices[0].message.tool_calls:  # 遍历每个工具调用
                    self._history.append(response.choices[0].message)  # 将助手消息添加到历史
                    f = self._toolsMap.get(tool_call.function.name)  # 获取工具函数
                    arguments = json.loads(tool_call.function.arguments)  # 解析参数
                    r = f(**arguments)  # 调用工具函数
                    self._history.append({'role': 'tool', 'content': r})  # 将工具响应添加到历史
                    logger.info(
                        f"[ToolsLLM] chat {response.id}: tool call(name {f}, arguments {arguments}), result {r}")  # 记录工具调用结果
                return self.ask()  # 递归调用，继续对话
            res = response.choices[0].message.content  # 获取响应内容
            if post_processor:  # 如果有后处理函数
                res = post_processor(res)  # 应用后处理
            self._add_response(res)  # 将响应添加到历史
            return res  # 返回响应
        except Exception as e:  # 捕获异常
            logger.error(f"[ToolsLLM] Error in chat call: {e}")  # 记录错误
            raise e  # 重新抛出异常

    def debug(self) -> str:
        """
        调试方法，尚未实现
        
        Returns:
            调试信息
            
        Raises:
            NotImplementedError: 该方法尚未实现
        """
        raise NotImplementedError  # 抛出未实现异常
