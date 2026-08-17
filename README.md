# studyAiCodeDemo

Dylan 自用 AI Agent 学习笔记代码库，按主题分目录，从基础调用一路走到可观测、评估与通用 Agent。

## 我的学习路径

根据下列顺序阅读 / 运行：


| 目录                | 主题              | 要点                                                  |
| ----------------- | --------------- | --------------------------------------------------- |
| `基础的Agent`        | 最简 LLM 调用       | DashScope 直接调模型，做情感正负向判断                            |
| `FunctionCalling` | 工具调用            | Qwen-Agent 封装 vs DashScope 原生 `tools`；门票助手、天气助手     |
| `MCP`             | MCP 协议          | 远程 Tavily MCP；本地自建 MCP 服务（txt 计数）                   |
| `LangChain`       | LangChain Agent | 私募基金规则问答（工具检索 + Agent）                              |
| `LangGraph`       | 图编排 Agent       | 深思熟虑式 / 混合式投顾助手；Prompt 外置 YAML                      |
| `LangSmith`       | 可观测 + 评测        | LangSmith 追踪、用例集、evaluation                         |
| `OpenEvals`       | 开源评测器           | correctness、RAG、toxicity、hallucination 等指标脚本        |
| `DeepEval`        | DeepEval        | 对投顾助手做 AnswerRelevancy / Hallucination / GEval      |
| `langFuse`        | 可观测             | Langfuse 追踪（含 Qwen-Agent / 混合投顾）                    |
| `OpenManus_cyd`   | 通用 Agent 框架     | OpenManus 本地改版；`config.toml` + 环境变量；可选 Daytona 沙箱   |
| `gui-plus`        | GUI 视觉操作模型      | DashScope `gui-plus`：截图 → JSON 原子操作（CLICK / TYPE 等） |




## 环境准备

```powershell
# 在仓库根目录
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

各章依赖各自维护在子目录 `requirements.txt`，学到哪装到哪即可。

### 环境变量一览

仓库脚本通过 `os.getenv` / `os.environ` 读取的变量如下（密钥放环境变量或本地 `.env`，已在 `.gitignore`，不要提交进仓库）。


| 变量                     | 必需程度              | 用途                                                               |
| ---------------------- | ----------------- | ---------------------------------------------------------------- |
| `DASHSCOPE_API_KEY`    | 几乎所有章节必需          | 通义千问 / DashScope（模型调用）                                           |
| `LANGSMITH_API_KEY`    | 跑 LangSmith 时必需   | LangSmith 鉴权（[smith.langchain.com](https://smith.langchain.com)） |
| `LANGCHAIN_TRACING_V2` | 跑 LangSmith 时必需   | 设为 `true` 开启追踪；代码里读此开关                                           |
| `LANGCHAIN_PROJECT`    | 可选                | LangSmith 项目名，默认多为 `wealth-advisor-hybrid-agent`                 |
| `LANGCHAIN_ENDPOINT`   | 可选                | LangSmith API 端点，不设则用官方默认                                        |
| `LANGFUSE_PUBLIC_KEY`  | 跑 Langfuse 时必需    | Langfuse 公钥                                                      |
| `LANGFUSE_SECRET_KEY`  | 跑 Langfuse 时必需    | Langfuse 私钥                                                      |
| `LANGFUSE_BASE_URL`    | 可选                | 默认 `https://cloud.langfuse.com`                                  |
| `OPENAI_API_KEY`       | 跑 DeepEval 时必需    | DeepEval 评审模型（如 gpt-4o-mini）                                     |
| `TAVILY_API_KEY`       | 跑 Tavily MCP 时必需  | `MCP` 远程搜索 Agent                                                 |
| `DAYTONA_API_KEY`      | 跑 OpenManus 沙箱时可选 | `OpenManus_cyd` Daytona 云沙箱；`config.toml` 中可留空由环境变量注入            |




### 按目录对照


| 目录                | 需要的环境变量                                                                                         |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| `基础的Agent`        | `DASHSCOPE_API_KEY`                                                                             |
| `FunctionCalling` | `DASHSCOPE_API_KEY`                                                                             |
| `MCP`（本地 MCP）     | `DASHSCOPE_API_KEY`                                                                             |
| `MCP`（Tavily MCP） | `DASHSCOPE_API_KEY` + `TAVILY_API_KEY`                                                          |
| `LangChain`       | `DASHSCOPE_API_KEY`                                                                             |
| `LangGraph`       | `DASHSCOPE_API_KEY`                                                                             |
| `LangSmith`       | `DASHSCOPE_API_KEY` + `LANGSMITH_API_KEY` + `LANGCHAIN_TRACING_V2=true`（可选 `LANGCHAIN_PROJECT`） |
| `OpenEvals`       | `DASHSCOPE_API_KEY`；对接 LangSmith 时再加 `LANGSMITH_API_KEY`（及 tracing 相关）                          |
| `DeepEval`        | `DASHSCOPE_API_KEY`（被测 Agent）+ `OPENAI_API_KEY`（评审）                                             |
| `langFuse`        | `DASHSCOPE_API_KEY` + `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`（可选 `LANGFUSE_BASE_URL`）     |
| `OpenManus_cyd`   | `DASHSCOPE_API_KEY`；用 Daytona 沙箱时再加 `DAYTONA_API_KEY`                                           |
| `gui-plus`        | `DASHSCOPE_API_KEY`                                                                             |




### PowerShell 设置示例（当前会话）

```powershell
# 通义（多数脚本）
$env:DASHSCOPE_API_KEY="你的key"

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

持久化可写入「系统环境变量」或用户级环境变量；勿把真实 key 写进仓库文件。

## 目录速览

```
基础的Agent/             # 最基础的千问调用
FunctionCalling/         # Function Calling 两种写法 + 门票/天气助手
MCP/                     # Tavily MCP Agent + 本地 MCP 服务
LangChain/               # 私募基金问答助手
LangGraph/               # 深思熟虑式 / 混合式投顾（LangGraph）
LangSmith/               # 助手 + LangSmith 追踪与评测
OpenEvals/               # OpenEvals 各类 evaluator 示例
DeepEval/                # DeepEval 评估投顾助手
langFuse/                # 助手 + Langfuse
OpenManus_cyd/           # OpenManus 通用 Agent（本地改版）
gui-plus/                # gui-plus 视觉 GUI 操作示例
```



## 章节补充说明



### `OpenManus_cyd`

- 从 `config/config.example.toml` 复制出本地 `config/config.toml`（该文件已被 gitignore，勿提交密钥）。
- LLM：`config.toml` 里 `api_key` 可留空，启动时读 `DASHSCOPE_API_KEY`。
- Daytona：`daytona_api_key` 可留空，启动时读 `DAYTONA_API_KEY`。
- 入口：`python main.py`；沙箱相关见 `app/daytona/README.md`、`sandbox_main.py`。
- 依赖见该目录 `requirements.txt`；完整安装可能较慢，可按需分批安装。



### `gui-plus`

- `gui-plus使用.py`：本地图片 `pic.jpg` 转 base64 后调用 `gui-plus`，输出 GUI 原子操作 JSON。
- 依赖 `DASHSCOPE_API_KEY`。



## 说明

- 纯学习用途，代码以可跑通、好对照为主，不做生产封装。
- 同一业务场景（投顾助手）会在 LangGraph / LangSmith / Langfuse / DeepEval 中反复出现，方便横向对比「编排 → 追踪 → 评测」。
- Windows 环境；运行前确认已激活虚拟环境并设置好对应 API Key。

