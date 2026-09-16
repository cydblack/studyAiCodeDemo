# studyAiCodeDemo

Dylan 自用 AI / Agent / Demo 代码库，按照我自己的笔记顺序，按主题分目录。

## 一、代码目录

与我的笔记顺序一致：

| # | 目录 | 文件 | 说明 |
| :---: | :---: | --- | --- |
| 1 | Agent | `baseQwenAgent` | 最基础的 `Qwen Agent` |
| | | `ACP` | Agent Client Protocol |
| 2 | FunctionCalling | `门票助手1` | 使用查 SQLite 库的 tool |
| | | `门票助手2` | 在 `门票助手1` 上，增加了图表信息展示 |
| 3 | MCP | `MCP使用-使用Tavily` | MCP 的使用，远程 Tavily MCP |
| | | `门票助手2` | 本地自建 MCP 服务（txt 计数） |
| 4 | OpenManus | `OpenManus_cyd` | OpenManus 本地改版 |
| 5 | Harness | `Memory` | 会话压缩、升格、召回、心跳 |
| 6 | LangChain | `LLMChain-参数传递` | Prompt 填变量，直接调模型 |
| | | `LLMChain-tool使用` | Agent + SerpAPI 网页搜索 |
| | | `LLMChain-调用Fuction` | 搜索工具 + 自定义计算器 |
| | | `带短期记忆的LLMChain` | 多轮对话记住上文 |
| | | `本地知识客服` | Agent 查本地产品/公司信息 |
| | | `ReAct私募基金问答助手` | 带 system prompt 的规则库问答 |
| | | `工具链组合形式-由LLM自己选工具` | 多个本地工具，模型自己选 |
| | | `网络故障诊断Agent` | 模拟 ping / DNS / 网卡 / 日志诊断 |
| | | `LCEL_demo` | LCEL 翻译 → 分析 → 回译，流式输出 |
| | | `LCEL_工具链组合形式-不使用大模型` | 工具顺序由代码写死，对照上一则 |

## 二、环境准备

```powershell
# 在仓库根目录
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

各章依赖各自维护在子目录 `requirements.txt`，学到哪装到哪即可。

### 环境变量一览

仓库脚本通过 `os.getenv` / `os.environ` 读取的变量如下（密钥放环境变量或本地 `.env`，已在 `.gitignore`，不要提交进仓库）。

| 变量 | 必需程度 | 用途 |
| --- | --- | --- |
| `DASHSCOPE_API_KEY` | 几乎所有章节必需 | 通义千问 / 百炼（模型调用） |
| `DASHSCOPE_BASE_URL` | 可选 | 百炼 OpenAI 兼容地址，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `SERPAPI_API_KEY` | 跑 LangChain 搜索 Agent 时必需 | `serpapi-search-tools` 网页搜索 |
| `DEEPSEEK_API_KEY` | 跑 ACP 主 Agent 拆任务板时必需 | `ACP/scripts/01`、`04` 的 DeepSeek 主 Agent |
| `LANGSMITH_API_KEY` | 跑 LangSmith 时必需 | LangSmith 鉴权（[smith.langchain.com](https://smith.langchain.com)） |
| `LANGCHAIN_TRACING_V2` | 跑 LangSmith 时必需 | 设为 `true` 开启追踪；代码里读此开关 |
| `LANGCHAIN_PROJECT` | 可选 | LangSmith 项目名，默认多为 `wealth-advisor-hybrid-agent` |
| `LANGCHAIN_ENDPOINT` | 可选 | LangSmith API 端点，不设则用官方默认 |
| `LANGFUSE_PUBLIC_KEY` | 跑 Langfuse 时必需 | Langfuse 公钥 |
| `LANGFUSE_SECRET_KEY` | 跑 Langfuse 时必需 | Langfuse 私钥 |
| `LANGFUSE_BASE_URL` | 可选 | 默认 `https://cloud.langfuse.com` |
| `OPENAI_API_KEY` | 跑 DeepEval 时必需 | DeepEval 评审模型（如 gpt-4o-mini） |
| `TAVILY_API_KEY` | 跑 Tavily MCP 时必需 | `MCP` 远程搜索 Agent |
| `DAYTONA_API_KEY` | 跑 OpenManus 沙箱时可选 | `OpenManus_cyd` Daytona 云沙箱；`config.toml` 中可留空由环境变量注入 |

### 按目录对照

| 目录 | 需要的环境变量 |
| --- | --- |
| `BaseQwenAgent` | `DASHSCOPE_API_KEY` |
| `FunctionCalling` | `DASHSCOPE_API_KEY` |
| `MCP`（本地 MCP） | `DASHSCOPE_API_KEY` |
| `MCP`（Tavily MCP） | `DASHSCOPE_API_KEY` + `TAVILY_API_KEY` |
| `LangChain` | `DASHSCOPE_API_KEY`；搜索 Agent 再加 `SERPAPI_API_KEY` |
| `ACP` | `DEEPSEEK_API_KEY`（拆任务板 / 主循环）；Codex ACP worker 需要本机 Node |
| `LangGraph` | `DASHSCOPE_API_KEY` |
| `LangSmith` | `DASHSCOPE_API_KEY` + `LANGSMITH_API_KEY` + `LANGCHAIN_TRACING_V2=true`（可选 `LANGCHAIN_PROJECT`） |
| `OpenEvals` | `DASHSCOPE_API_KEY`；对接 LangSmith 时再加 `LANGSMITH_API_KEY`（及 tracing 相关） |
| `DeepEval` | `DASHSCOPE_API_KEY`（被测 Agent）+ `OPENAI_API_KEY`（评审） |
| `langFuse` | `DASHSCOPE_API_KEY` + `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`（可选 `LANGFUSE_BASE_URL`） |
| `OpenManus_cyd` | `DASHSCOPE_API_KEY`；用 Daytona 沙箱时再加 `DAYTONA_API_KEY` |
| `gui-plus` | `DASHSCOPE_API_KEY` |
| `Memory` | `DASHSCOPE_API_KEY` |

### PowerShell 设置示例（当前会话）

```powershell
# 通义 / 百炼（多数脚本）
$env:DASHSCOPE_API_KEY="你的key"
$env:DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

# SerpAPI（LangChain 搜索 Agent）
$env:SERPAPI_API_KEY="你的key"

# DeepSeek（ACP 主 Agent）
$env:DEEPSEEK_API_KEY="你的key"

# LangSmith（LangSmith / 部分 OpenEvals）
$env:LANGSMITH_API_KEY="你的key"
$env:LANGCHAIN_TRACING_V2="true"
$env:LANGCHAIN_PROJECT="wealth-advisor-hybrid-agent"

# Langfuse（langFuse）
$env:LANGFUSE_PUBLIC_KEY="你的公钥"
$env:LANGFUSE_SECRET_KEY="你的私钥"
# $env:LANGFUSE_BASE_URL="https://cloud.langfuse.com"

# DeepEval（DeepEval）
$env:OPENAI_API_KEY="你的key"

# Tavily MCP（MCP）
$env:TAVILY_API_KEY="你的key"

# OpenManus Daytona 沙箱（OpenManus_cyd，可选）
$env:DAYTONA_API_KEY="你的key"
```

## 三、模型选择

模型基本上都选的如 `deepseek-v`、`qwen-flash` 之类的便宜模型，主要是省金币

## 四、代码说明

### 1. Agent

1. `baseQwenAgent`

    - 最基础的 `Qwen Agent`
    - 使用 `DashScope` 直接调模型

2. `ACP`

    - 最简连接：`ACP最简连接 _Win.py` / `ACP最简连接_Mac.py`，拉起官方 `@agentclientprotocol/codex-acp`。
    - `scripts/` 可单独跑：`01` 拆任务板 → `02` ACP smoke → `03` 上下文隔离 → `04` TriggerFlow 主循环 → `05` 复盘结果。
    - 业务材料：`ACP/materials/product_goal.txt`；产物：`ACP/.demo_runs/`。
    - 另有 `ACP/Demo/demo1.py`（Agently TriggerFlow，不走 ACP）。
    - 说明见 `ACP/scripts/README.md`。Windows 上用 `node.exe` + `npx-cli.js` 启动 adapter，不要直接跑 `npx.cmd`。

### 2. FunctionCalling

1. `门票助手1`

    - 使用 `Qwen-Agent` 封装
    - 原本使用链接数据库，后来改为本地 `SQLite` 文件
    - 使用的是 `qwen` 的 `tools` 注册方式

2. `门票助手2`

    - 在 `门票助手1` 的基础上，增加了图表信息的展示

### 4. OpenManus_cyd（Manus）

1. `OpenManus_cyd`

    - OpenManus 本地改版
    - `config.toml` + 环境变量
    - 可选 Daytona 沙箱
    - 从 `config/config.example.toml` 复制出本地 `config/config.toml`（该文件已被 gitignore，勿提交密钥）。
    - LLM：`config.toml` 里 `api_key` 可留空，启动时读 `DASHSCOPE_API_KEY`。
    - Daytona：`daytona_api_key` 可留空，启动时读 `DAYTONA_API_KEY`。
    - 入口：`python main.py`；沙箱相关见 `app/daytona/README.md`、`sandbox_main.py`。
    - 依赖见该目录 `requirements.txt`；完整安装可能较慢，可按需分批安装。

### 5. Harness

1. `Memory`（Agent 长期记忆）

    - 会话压缩、升格、召回、心跳
    - 综合实例把文件记忆接入 Workspace 再对照出行程
    - 主线看 `Memory/MemoryV2/README.md`：Step1–Step5 压缩与召回，Step6 心跳（有新 `event_id` 才跑前五步）。
    - `MemoryV1` 是文件分层管线存档，日常不用看。
    - 综合实例：`python Memory/综合实例/run.py`，整理后导入本目录 `FileMemoryWorkspace`，对照有/无记忆两份行程。
    - 材料在 `Memory/materials/`，产物在 `Memory/.demo_runs/`。

### 6. LangChain

> 写法以 2026.09 的 LangChain 1.x 为准。
> 不再用已停更的 `langchain_community.ChatTongyi` / `load_tools(["serpapi"])`（`6` 仍用 `ChatTongyi` + `qwen-plus`）。其余走 `ChatOpenAI` + 百炼 `compatible-mode/v1`；`1–7` 多为 `deepseek-v4-flash`，`8`、`9` 为 `qwen-turbo`。搜索用 `serpapi-search-tools` 的 `web_search(provider="langchain")`。

1. `LLMChain-参数传递`

    - **功能**：给公司起名字
    - **说明**：通过 `prompt | llm` 方式，`PromptTemplate` 把 `{product}` 填进「给某方向公司起名」

2. `LLMChain-tool使用`

    - Agent 挂上 SerpAPI 的 `web_search`，问「十月一日是什么节日」
    - 看 `create_agent` + 现成搜索工具的最小写法

3. `LLMChain-调用Fuction`

    - 搜索工具再加自定义 `calculator`，问北京气温（华氏）再算其 1/4
    - 看现成工具和 `@tool` 函数怎么拼进同一个 Agent

4. `带短期记忆的LLMChain`

    - `RunnableWithMessageHistory` 同一 `session_id` 连问三轮
    - 第三轮问「我叫什么名字」，看短期记忆怎么挂到 chain 上（不经过 Agent）

5. `本地知识客服`

    - 两个 `@tool`：按车型查描述、按问题查公司介绍；命令行循环提问
    - 看 Agent 在本地字典/固定文案上当客服，不联网

6. `ReAct私募基金问答助手`

    - 内存规则库 + 关键词/类别/直接问答三个工具
    - `system_prompt` 约束只答私募；循环对话
    - 仍用 `ChatTongyi`（`qwen-plus`），和其余走 `ChatOpenAI` 的文件不是同一套模型入口

7. `工具链组合形式-由LLM自己选工具`

    - 五个本地工具（情感分析、JSON/CSV 转换、行数、查找、替换）
    - 三个任务分别测组合调用和「没有对应工具」
    - 看工具链组合：模型按题自己选工具，而不是代码写死调用顺序

8. `网络故障诊断Agent`

    - 四个模拟工具：`ping`、DNS、网卡状态、日志分析
    - 跑「访问超时」和「eth1 连不上网」两个诊断任务
    - 看同一套 `create_agent` 用在故障排查场景，工具返回的是模拟结果

9. `LCEL_demo`

    - **功能**：LCEL 基本写法 Demo，`ChatPromptTemplate | llm | StrOutputParser` 组成翻译 → 分析 → 回译
    - `workflow.stream` 流式输出打印

10. `LCEL_工具链组合形式-不使用大模型`

    - 使用 `LCEL` 方式，对 7 的代码进行修改
    - 这里没有大模型，选哪个工具、什么顺序全是代码决定的

## 五、最终说明

- 纯学习用途，代码以可跑通、好对照为主，不可用于生成环境。
- 同一业务场景（投顾助手）会在 LangGraph / LangSmith / Langfuse / DeepEval 中反复出现，方便横向对比「编排 → 追踪 → 评测」。
- `ACP` 用杭州三日游团建目标，对照「主 Agent 拆板 → Codex worker 执行 → 上下文隔离 → TriggerFlow 汇总」。
- `Memory` 用同一套亲子行程对话，对照「压缩 → 升格 → 召回 → 有/无记忆出行程」。
- Windows 环境；运行前确认已激活虚拟环境并设置好对应 API Key。
