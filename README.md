## RepoHCL
借助LLM理解C/C++项目，为项目中的每个源代码文件生成文档

### 工作流程
为C/C++项目生成AST
基于AST解析源代码文件中包含的类与函数，并生成Function/Class CallGraph
基于Function CallGraph的逆拓扑排序，与LLM交互，为各个函数生成文档
基于Class CallGraph的逆拓扑排序，与LLM交互，为各个类生成文档
### 项目结构
```
├── docker                      # docker封装的项目demo
│    ├── dockerfile.cg_python  
│    └── dockerfile.cg_service
├── lib                         # 项目依赖的库，主要包含Vanguard-V2-StaticChecker的编译产物
│    └── cge
├── Vanguard-V2-StaticChecker   # C/C++项目静态分析工具
├── 'resource'                  # 待分析C/C++项目源代码目录(运行时生成)
│    └── vanguard
├── 'docs'                      # 生成的文档目录(运行时生成)
├── 'output'                    # C/C++项目分析中间产物目录(运行时生成)
├── ast_generator.py            # 为C/C++项目生成AST
├── chat_engine.py              # LLM理解源代码
├── llm_helper.py               # LLM工具类库
├── log.py                      # 日志工具类
├── doc.py                      # 文档的对象表示
├── multi_task_dispatch.py      
├── project_manager.py          # 项目目录结构的对象表示
├── prompt.py                   # LLM Prompt常量
├── settings.py                 # 配置
├── main.py                     # 命令行入口
├── service.py                  # web服务入口
├── requirements.txt            # Python依赖管理
└── README.md                  
```
### 使用说明
- 项目基于OpenAI协议调用LLM，需在settings.py中设置调用的LLM服务的域名、模型、温度，并配置环境变量OPENAI_API_KEY作为密钥。默认采用阿里百炼。

- 目前提供了docker/dockerfile.cg_python，可以对项目Vanguard-V2-StaticChecker进行一次完整的分析。本地运行依赖可参考该dockerfile。

- 由于不同C/C++项目的编译方式不同，目前需要根据项目特征手动设置合适的命令以生成AST。