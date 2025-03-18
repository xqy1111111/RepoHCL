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

compile_commands_files = "compile_commands.json"

env_clang = "$CC"
env_clangplus = "$CXX"
clang_emit_ast_opt = "-emit-ast"
astfile_ext = ".ast"

# output of this script
buildast_sh_list = []
buildast_sh_fn = "buildast.sh"
astFile_list = []
astFile_fn = "astList.txt"

if not os.path.exists(compile_commands_files):
    print("[-] compile_commands.json not exist!")
    exit(1)


def logFormatErr():
    print("[-] compile_commands.json format error!")
    print("[-] expected json format below:")
    print(expected_json_format)


with open(compile_commands_files, mode='r') as fr:
    ccjson = json.loads(fr.read())

if type(ccjson) is not list:
    logFormatErr()
    exit(1)

filesets = set()

for cc in ccjson:
    cmdargs = cc.get("arguments")  # ubuntu 18.04, bear 2.3.11
    directory = cc.get("directory")
    filename = cc.get("file")
    if filename in filesets:
        continue
    filesets.add(filename)

    if cmdargs is None:
        command = cc.get("command")  # ubuntu 16.04, bear 2.1.5
        cmdargs = command.split(' ')
    # change C compile into clang and add option `-emit-ast`
    if cmdargs[0].lower() in ["c++", "g++", "cpp", "cxx"]:
        cmdargs[0] = ' '.join([env_clangplus, clang_emit_ast_opt])
    else:
        cmdargs[0] = ' '.join([env_clang, clang_emit_ast_opt])
    for i, arg in enumerate(cmdargs):
        cmdargs[i] = arg.strip('\"\'')
    default_ast_name = os.path.splitext(os.path.basename(filename))[0] + astfile_ext
    if not os.path.isabs(default_ast_name):
        default_ast_name = os.path.join(directory, default_ast_name)
    astFile_list.append(default_ast_name)
    if '-o' not in cmdargs:
        cmdargs = cmdargs[:-1] + ["-o", default_ast_name] + [filename]
    else:
        cmdargs[cmdargs.index('-o') + 1] = default_ast_name
    # join all options into a new cmd
    cmd_exe = ' '.join(cmdargs)
    cmd_exe = cmd_exe.replace('"',
                              r'\"')  # e.g. -DMARCO="string", the double quotation marks should be escaped => -DMARCO=\"string\"
    cmd_exe = cmd_exe.replace(r'\\"',
                              r'\"')  # in ubuntu 16.04, bear 2.1.5 will handle the double quotation, so here reverse last instructions
    # cd directory
    cmd_cd = ' '.join(["cd", directory])
    abs_filepath = os.path.join(directory, filename)
    abs_filepath = os.path.abspath(abs_filepath)
    # print(cmd_exe)
    buildast_sh_list.append(cmd_cd)
    buildast_sh_list.append(cmd_exe + " && (")
    buildast_sh_list.append("  echo \"[+] succ: " + abs_filepath + "\"")
    buildast_sh_list.append(") || (")
    buildast_sh_list.append("  echo \"[-] failed: " + abs_filepath + "\"")
    buildast_sh_list.append("  kill -9 0")
    buildast_sh_list.append(")")
    buildast_sh_list.append("\n")

with open(buildast_sh_fn, mode='w', encoding="utf-8") as fw:
    fw.write('\n'.join(buildast_sh_list))

with open(astFile_fn, mode='w', encoding="utf-8") as fw:
    fw.writelines('\n'.join(astFile_list))
