import os.path  # 导入os.path模块，用于处理文件路径
import shutil  # 导入shutil模块，用于高级文件操作，如复制和删除文件夹

import click  # 导入click库，这是一个用于创建命令行界面的库

from metrics import EvaContext, ClangParser, FunctionMetric, ClazzMetric, ModuleMetric, RepoV2Metric, \
    PyParser  # 导入自定义的度量分析模块
from utils.common import LangEnum  # 导入语言枚举类，用于支持不同的编程语言


def response_with_gitbook(doc_path: str):
    """
    生成GitBook格式的摘要文件，整合文档目录结构
    
    Args:
        doc_path: 文档路径
    """
    def summary_sort(s: str):
        """
        对摘要文件进行排序的辅助函数
        
        Args:
            s: 文件名
            
        Returns:
            排序优先级元组，包含优先级数字和小写文件名
        """
        # 模块摘要优先级最高
        if 'modules.md' in s or 'cares.md' in s:
            return 1, s.lower()
        else:
            # 如果字符串不符合任何条件，给予最低优先级
            return 4, s.lower()

    summary = '# Summary\n'  # 初始化摘要文件内容
    for root, _, files in os.walk(doc_path):  # 遍历文档目录
        root = root[len(doc_path) + 1:]  # 获取相对路径
        if len(root) > 0:  # 如果有子目录
            summary += f'{(len(root.split(os.sep)) - 1) * "  "}* [{root}]\n'  # 添加目录条目，根据层级缩进
        for f in sorted(files, key=summary_sort):  # 对文件排序并遍历
            if len(root) > 0:  # 如果在子目录中
                summary += f'{len(root.split(os.sep)) * "  "}* [{f[:-3]}]({os.path.join(root, f)}\n'  # 添加文件条目，带缩进
            else:  # 如果在根目录中
                summary += f'* [{f[:-3]}]({f})\n'  # 添加文件条目，不带缩进
    with open(os.path.join(doc_path, 'SUMMARY.md'), 'w') as f:  # 打开摘要文件
        f.write(summary)  # 写入摘要内容
    with open(os.path.join(doc_path, 'README.md'), 'w') as f:  # 打开README文件
        f.write(f'### {os.path.basename(doc_path)}\n')  # 写入README内容，使用目录名作为标题




@click.command()  # 使用click装饰器创建命令行命令
@click.argument('path', type=click.Path(exists=True))  # 添加路径参数，要求路径必须存在
@click.option('--lang', default=LangEnum.cpp.cli,
              type=click.Choice([LangEnum.python.cli, LangEnum.cpp.cli], case_sensitive=False),
              help='编程语言')  # 添加语言选项，支持Python和C++
def main(path, lang):
    """
    主函数，分析指定路径下的代码并生成文档
    
    Args:
        path: 代码仓库路径
        lang: 编程语言
    """
    path = click.format_filename(path).strip(os.sep)  # 格式化路径，去除末尾的分隔符
    basename = os.path.basename(path)  # 获取路径的基本名称（最后一部分）
    # 移动到工作路径，复制代码仓库到resource目录
    shutil.copytree(path, os.path.join('resource', basename), dirs_exist_ok=True)
    # 初始化评估上下文，设置文档路径、资源路径和输出路径
    ctx = EvaContext(doc_path=os.path.join('docs', basename), resource_path=os.path.join('resource', basename),
                     output_path=os.path.join('output', basename), lang=lang)
    # 开始运行评估
    eva(ctx, LangEnum.from_cli(lang))
    # 生成gitbook输出格式
    response_with_gitbook(os.path.join('docs', basename))
    # 清理工作路径，删除临时文件
    shutil.rmtree(os.path.join('resource', basename))
    shutil.rmtree(os.path.join('output', basename))


def eva(ctx: EvaContext, lang: LangEnum):
    """
    执行代码评估流程，根据不同的语言选择不同的解析器，并应用各种度量分析
    
    Args:
        ctx: 评估上下文对象
        lang: 语言枚举值
    """
    # 生成函数列表、类列表、函数调用图、类调用图，根据语言选择不同的解析器
    if lang == LangEnum.cpp:  # 如果是C++语言
        ClangParser().eva(ctx)  # 使用Clang解析器
    elif lang == LangEnum.python:  # 如果是Python语言
        PyParser().eva(ctx)  # 使用Python解析器
    else:
        raise NotImplementedError(f'{lang} not supported')  # 不支持的语言抛出异常
    # 生成软件目录结构，TODO：暂时不用了
    # StructureMetric().eva(ctx)
    # 生成函数文档
    FunctionMetric().eva(ctx)
    # 生成类文档
    ClazzMetric().eva(ctx)
    # 生成模块文档
    ModuleMetric().eva(ctx)
    # 生成仓库文档
    RepoV2Metric().eva(ctx)


if __name__ == '__main__':
    main()  # 当作为脚本直接运行时，执行main函数
