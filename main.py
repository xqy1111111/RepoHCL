import os.path
import shutil

import click

from metrics import EvaContext, ClangParser, FunctionMetric, StructureMetric, ClazzMetric, ModuleMetric, RepoV2Metric


def response_with_gitbook(doc_path: str):
    def summary_sort(s: str):
        # 模块摘要优先级最高
        if 'modules.md' in s or 'cares.md' in s:
            return 1, s.lower()
        else:
            # 如果字符串不符合任何条件，给予最低优先级
            return 4, s.lower()

    summary = '# Summary\n'
    for root, _, files in os.walk(doc_path):
        root = root[len(doc_path) + 1:]
        if len(root) > 0:
            summary += f'{(len(root.split("/")) - 1) * "  "}* [{root}]\n'
        for f in sorted(files, key=summary_sort):
            if len(root) > 0:
                summary += f'{len(root.split("/")) * "  "}* [{f[:-3]}]({root}/{f})\n'
            else:
                summary += f'* [{f[:-3]}]({f})\n'
    with open(f'{doc_path}/SUMMARY.md', 'w') as f:
        f.write(summary)
    with open(f'{doc_path}/README.md', 'w') as f:
        f.write(f'### {os.path.basename(doc_path)}\n')


@click.command()
@click.argument('path', type=click.Path(exists=True))
def main(path):
    path = click.format_filename(path).strip('/')
    basename = os.path.basename(path)
    # 移动到工作路径
    shutil.copytree(path, f'resource/{basename}', dirs_exist_ok=True)
    # 初始化上下文
    ctx = EvaContext(doc_path=f'docs/{basename}', resource_path=f'resource/{basename}', output_path=f'output/{basename}')
    # 开始运行
    eva(ctx)
    # 生成gitbook输出
    response_with_gitbook(f'docs/{basename}')
    # 清扫工作路径
    shutil.rmtree(f'resource/{basename}')
    shutil.rmtree(f'output/{basename}')


def eva(ctx: EvaContext):
    # 生成函数列表、类列表、函数调用图、类调用图
    ClangParser().eva(ctx)
    # 生成软件目录结构
    StructureMetric().eva(ctx)
    # 生成函数文档
    FunctionMetric().eva(ctx)
    # 生成类文档
    ClazzMetric().eva(ctx)
    # 生成模块文档
    ModuleMetric().eva(ctx)
    # 生成仓库文档
    RepoV2Metric().eva(ctx)


if __name__ == '__main__':
    main()
