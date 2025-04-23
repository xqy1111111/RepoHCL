#!/usr/bin python3
import json
import os

# =====###### must run make before runing this script #####=====

# 功能
# 1 提取 compile_commands.json(由bear生成) 里的编译命令
# 2 替换编译器名, 加上-emit-ast选项, 修改-o参数(以提高文件名的可读性), 其中
#     2.1 默认编译器名在第1个参数, 改成依赖于shell环境的$CC和$CXX
#     2.2 -emit-ast放在编译器名后面, 即第2个参数
#     2.3 将-o对应参数里的.o直接换成.ast后缀, 不修改路径(即不将ast文件都放到统一目录下, 而是跟随项目makefile里中间文件的生成规则)
# 3 将修改后的编译命令整合到的buildast.sh文件
# 4 生成astList.txt, 存放所有ast文件的绝对路径

# 预期的JSON格式说明，用于验证compile_commands.json文件格式是否符合要求
expected_json_format = """
// in ubuntu 18.04, bear 2.3.11
[
  {
    "directory": "xxx",
    "arguments": [
      "xxx",
      "xxx",
      ...
    ],
    "file": "xxx"
  },
  {
    ...
  },
  ...
]

OR

// in ubuntu 16.04, bear 2.1.5
[
  {
    "directory": "xxx",
    "command": "xxx",
    "file": "xxx"
  },
  {
    ...
  },
  ...
]
"""

# 环境变量定义，用于指定C和C++编译器
env_clang = "$CC"         # C语言编译器环境变量
env_clangplus = "$CXX"    # C++编译器环境变量
clang_emit_ast_opt = "-emit-ast"  # 生成AST的编译选项
astfile_ext = ".ast"      # AST文件扩展名


# 本脚本的输出文件:
# 1. buildast.sh - 包含所有生成AST的编译命令
# 2. astList.txt - 包含所有生成的AST文件路径列表


def logFormatErr():
    """
    打印JSON格式错误信息
    
    当compile_commands.json文件格式不符合预期时调用此函数
    打印错误信息和预期的JSON格式
    """
    print("[-] compile_commands.json format error!")
    print("[-] expected json format below:")
    print(expected_json_format)


def gen_sh(path: str):
    """
    生成构建AST的脚本和AST文件列表
    
    Args:
        path: 项目路径，应包含compile_commands.json文件
    
    功能:
        1. 读取compile_commands.json文件
        2. 修改编译命令，添加生成AST的选项
        3. 生成buildast.sh脚本文件
        4. 生成astList.txt文件列表
    """
    buildast_sh_list = []  # 存储buildast.sh文件的命令行列表
    astFile_list = []      # 存储AST文件路径的列表
    buildast_sh_fn = f"{path}/buildast.sh"  # buildast.sh文件路径
    astFile_fn = f"{path}/astList.txt"      # astList.txt文件路径
    compile_commands_files = f"{path}/compile_commands.json"  # compile_commands.json文件路径
    
    # 读取compile_commands.json文件
    with open(compile_commands_files, mode='r') as fr:
        ccjson = json.loads(fr.read())
    
    # 验证JSON格式是否为列表
    if type(ccjson) is not list:
        logFormatErr()
        exit(1)

    filesets = set()  # 用于去重，避免处理重复的源文件

    # 处理每个编译命令
    for cc in ccjson:
        cmdargs = cc.get("arguments")  # ubuntu 18.04, bear 2.3.11
        directory = cc.get("directory")  # 编译目录
        filename = cc.get("file")       # 源文件名
        
        # 跳过重复的文件
        if filename in filesets:
            continue
        filesets.add(filename)

        # 处理不同格式的compile_commands.json
        if cmdargs is None:
            command = cc.get("command")  # ubuntu 16.04, bear 2.1.5
            cmdargs = command.split(' ')  # 将命令字符串分割为参数列表
            
        # 根据编译器类型替换为对应的clang编译器并添加-emit-ast选项
        if cmdargs[0].lower() in ["c++", "g++", "cpp", "cxx"]:
            cmdargs[0] = ' '.join([env_clangplus, clang_emit_ast_opt])  # C++编译器
        else:
            cmdargs[0] = ' '.join([env_clang, clang_emit_ast_opt])      # C编译器
            
        # 移除参数中的引号
        for i, arg in enumerate(cmdargs):
            cmdargs[i] = arg.strip('\"\'')
            
        # 生成默认的AST文件名（源文件名.ast）
        default_ast_name = os.path.splitext(os.path.basename(filename))[0] + astfile_ext
        if not os.path.isabs(default_ast_name):
            default_ast_name = os.path.join(directory, default_ast_name)
            
        # 添加到AST文件列表
        astFile_list.append(default_ast_name)
        
        # 处理输出参数-o，确保输出AST文件
        if '-o' not in cmdargs:
            cmdargs = cmdargs[:-1] + ["-o", default_ast_name] + [filename]
        else:
            cmdargs[cmdargs.index('-o') + 1] = default_ast_name
            
        # 将参数列表组合成命令字符串
        cmd_exe = ' '.join(cmdargs)
        # 处理命令中的双引号，确保shell能正确解析
        cmd_exe = cmd_exe.replace('"', r'\"')  # 转义双引号，如 -DMARCO="string" => -DMARCO=\"string\"
        cmd_exe = cmd_exe.replace(r'\\"', r'\"')  # 处理已转义的双引号，防止重复转义
        
        # 生成切换到编译目录的命令
        cmd_cd = ' '.join(["cd", directory])
        
        # 获取源文件的绝对路径，用于日志输出
        abs_filepath = os.path.join(directory, filename)
        abs_filepath = os.path.abspath(abs_filepath)
        
        # 构建shell脚本命令，包含成功和失败的处理逻辑
        buildast_sh_list.append(cmd_cd)  # 切换目录
        buildast_sh_list.append(cmd_exe + " && (")  # 执行编译命令
        buildast_sh_list.append("  echo \"[+] succ: " + abs_filepath + "\"")  # 成功时的输出
        buildast_sh_list.append(") || (")  # 失败处理开始
        buildast_sh_list.append("  echo \"[-] failed: " + abs_filepath + "\"")  # 失败时的输出
        buildast_sh_list.append("  kill -9 0")  # 失败时终止所有相关进程
        buildast_sh_list.append(")")
        buildast_sh_list.append("\n")  # 添加空行，提高可读性

    # 写入buildast.sh文件
    with open(buildast_sh_fn, mode='w', encoding="utf-8") as fw:
        fw.write('\n'.join(buildast_sh_list))

    # 写入astList.txt文件
    with open(astFile_fn, mode='w', encoding="utf-8") as fw:
        fw.writelines('\n'.join(astFile_list))
