## RepoHCL
借助LLM理解C/C++项目，为项目中的每个源代码文件生成文档

### 工作流程
- 为C/C++项目生成AST
- 基于AST解析源代码文件中包含的类与函数，并生成Function/Class CallGraph
- 按Function CallGraph的逆拓扑排序，为各个函数生成文档
- 按Class CallGraph的逆拓扑排序，为各个类生成文档
- 基于函数文档生成模块文档
- 基于模块文档生成仓库文档
### 项目结构
```
├── docker                      # docker封装的项目demo
│    ├── dockerfile.cg_python   # main.py的docker运行环境
│    └── dockerfile.cg_service  # service.py的docker运行环境
├── lib                         # 项目依赖的库，主要包含Vanguard-V2-StaticChecker的编译产物
│    └── cge
├── Vanguard-V2-StaticChecker   # C/C++项目静态分析工具
├── 'resource'                  # 待分析C/C++项目源代码目录(运行时生成)
│    └── vanguard
├── 'docs'                      # 生成的文档目录(运行时生成)
├── 'output'                    # C/C++项目分析中间产物目录(运行时生成)
├── metrics                     # 各个度量指标实现
│    ├── clazz.py               # 类级别度量
│    ├── doc.py                 # 度量结果文档对象
│    ├── function.py            # 函数级别度量
│    ├── metric.py              # 度量基类及上下文
│    ├── module.py              # 模块级别度量
│    ├── parser.py              # 软件解析
│    ├── repo.py                # 仓库级别度量
│    └── structure.py           # 目录结构度量
├── utils
│    ├── ast_generator.py       # C/C++项目生成AST
│    ├── file_helper.py         # 压缩文件工具类库
│    ├── llm_helper.py          # LLM工具类库
│    ├── multi_task_dispatch.py
│    ├── settings.py            # 配置工具类库
│    └── strings.py             # 字符串工具类库
├── .env                        # 配置文件/环境变量
├── main.py                     # 命令行入口
├── service.py                  # web服务入口
├── requirements.txt            # Python依赖管理
└── README.md                  
```
### 使用说明
- 项目基于OpenAI协议调用LLM，需在.env中设置调用的LLM服务的域名、模型、温度，并配置环境变量`OPENAI_API_KEY`作为密钥。默认采用阿里百炼。
- 目前提供了docker/dockerfile.cg_python，可以对测试项目md5进行一次完整的分析。本地运行依赖可参考该dockerfile。
- 由于不同C/C++项目的编译方式不同，目前需要根据项目特征手动设置合适的命令以生成AST。

### TODO
- 识别API，基于API优化模块文档和对比文档
- 增加验证环节，提高文档质量
- 结合RAG生成仓库文档
- 增加对其他语言的支持：RUST