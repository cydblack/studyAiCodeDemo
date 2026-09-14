# studyAiCodeDemo

Dylan 自用 AI Agent 练习代码库，按主题分目录，从基础调用到可观测、评估与通用 Agent。

## 代码顺序

根据下列顺序阅读 / 运行：

#### 1. `BaseQwenAgent`**（最简 Qwen Agent）**

- 最基础的 Qwen Agent
- 使用 DashScope 直接调模型
- 功能：情感正负向判断

#### 2. `FunctionCalling`**（工具调用）**

（1） 门票助手1：

- 使用 `Qwen-Agent` 封装
- 原本使用链接数据库，后来改为本地 `SQLite` 文件
- 使用的是 `qwen` 的 `tools` 注册方式

（2） 门票助手2：

- 在（1）的基础上，增加了图表信息的展示


1. `MCP`（MCP 协议）
  远程 Tavily MCP；本地自建 MCP 服务（txt 计数）
2. `LangChain`（LangChain 1.x 写法）
  百炼 OpenAI 兼容接口（`ChatOpenAI` + `deepseek-v4-flash`）；LCEL 参数传递、SerpAPI 搜索 Agent、自定义 Function、短期记忆、本地知识客服；私募基金规则问答仍在
3. `ACP`（Agent Client Protocol）
  官方 Codex ACP 最简连接（Win/Mac）；主 Agent 拆任务板；worker smoke；上下文隔离；TriggerFlow 主循环跑杭州三日游团建
4. `LangGraph`（图编排 Agent）
  深思熟虑式 / 混合式投顾助手；Prompt 外置 YAML
5. `LangSmith`（可观测 + 评测）
  LangSmith 追踪、用例集、evaluation
6. `OpenEvals`（开源评测器）
  correctness、RAG、toxicity、hallucination 等指标脚本
7. `DeepEval`（DeepEval）
  对投顾助手做 AnswerRelevancy / Hallucination / GEval
8. `langFuse`（可观测）
  Langfuse 追踪（含 Qwen-Agent / 混合投顾）
9. `OpenManus_cyd`（通用 Agent 框架）
  OpenManus 本地改版；`config.toml` + 环境变量；可选 Daytona 沙箱
10. `gui-plus`（GUI 视觉操作模型）
  DashScope `gui-plus`：截图 → JSON 原子操作（CLICK / TYPE 等）
11. `Memory`（Agent 长期记忆）
  会话压缩、升格、召回、心跳；综合实例把文件记忆接入 Workspace 再对照出行程



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
| `DASHSCOPE_API_KEY`    | 几乎所有章节必需          | 通义千问 / 百炼（模型调用）                                                   |
| `DASHSCOPE_BASE_URL`   | 可选                  | 百炼 OpenAI 兼容地址，默认 `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `SERPAPI_API_KEY`      | 跑 LangChain 搜索 Agent 时必需 | `serpapi-search-tools` 网页搜索                                      |
| `DEEPSEEK_API_KEY`     | 跑 ACP 主 Agent 拆任务板时必需 | `ACP/scripts/01`、`04` 的 DeepSeek 主 Agent                           |
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
| `BaseQwenAgent`   | `DASHSCOPE_API_KEY`                                                                             |
| `FunctionCalling` | `DASHSCOPE_API_KEY`                                                                             |
| `MCP`（本地 MCP）     | `DASHSCOPE_API_KEY`                                                                             |
| `MCP`（Tavily MCP） | `DASHSCOPE_API_KEY` + `TAVILY_API_KEY`                                                          |
| `LangChain`       | `DASHSCOPE_API_KEY`；搜索 Agent 再加 `SERPAPI_API_KEY`                                               |
| `ACP`             | `DEEPSEEK_API_KEY`（拆任务板 / 主循环）；Codex ACP worker 需要本机 Node                                        |
| `LangGraph`       | `DASHSCOPE_API_KEY`                                                                             |
| `LangSmith`       | `DASHSCOPE_API_KEY` + `LANGSMITH_API_KEY` + `LANGCHAIN_TRACING_V2=true`（可选 `LANGCHAIN_PROJECT`） |
| `OpenEvals`       | `DASHSCOPE_API_KEY`；对接 LangSmith 时再加 `LANGSMITH_API_KEY`（及 tracing 相关）                          |
| `DeepEval`        | `DASHSCOPE_API_KEY`（被测 Agent）+ `OPENAI_API_KEY`（评审）                                             |
| `langFuse`        | `DASHSCOPE_API_KEY` + `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`（可选 `LANGFUSE_BASE_URL`）     |
| `OpenManus_cyd`   | `DASHSCOPE_API_KEY`；用 Daytona 沙箱时再加 `DAYTONA_API_KEY`                                           |
| `gui-plus`        | `DASHSCOPE_API_KEY`                                                                             |
| `Memory`          | `DASHSCOPE_API_KEY`                                                                             |




### PowerShell 设置示例（当前会话）

```powershell
# 通义 / 百炼（多数脚本）
$env:DASHSCOPE_API_KEY="你的key"
# $env:DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"

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

持久化可写入「系统环境变量」或用户级环境变量；勿把真实 key 写进仓库文件。

### `LangChain`

- 2026-09 起不再用已停更的 `langchain_community.ChatTongyi` / `load_tools(["serpapi"])`。
- 模型：`ChatOpenAI` + 百炼 `compatible-mode/v1`，示例模型 `deepseek-v4-flash`。
- 搜索：`serpapi-search-tools` 的 `web_search(provider="langchain")`。
- 入口示例：`1-LLMChain-参数传递.py`、`2-LLMChain-tool使用.py`、`3-LLMChain-调用Fuction.py`、`4-带短期记忆的LLMChain.py`、`5-本地知识客服.py`。
- 私募基金问答仍在 `6-ReAct私募基金问答助手.py`。
- 依赖见 `LangChain/requirements.txt`。

### `ACP`

- 最简连接：`ACP最简连接 _Win.py` / `ACP最简连接_Mac.py`，拉起官方 `@agentclientprotocol/codex-acp`。
- `scripts/` 可单独跑：`01` 拆任务板 → `02` ACP smoke → `03` 上下文隔离 → `04` TriggerFlow 主循环 → `05` 复盘结果。
- 业务材料：`ACP/materials/product_goal.txt`；产物：`ACP/.demo_runs/`。
- 另有 `ACP/Demo/demo1.py`（Agently TriggerFlow，不走 ACP）。
- 说明见 `ACP/scripts/README.md`。Windows 上用 `node.exe` + `npx-cli.js` 启动 adapter，不要直接跑 `npx.cmd`。

### `OpenManus_cyd`

- 从 `config/config.example.toml` 复制出本地 `config/config.toml`（该文件已被 gitignore，勿提交密钥）。
- LLM：`config.toml` 里 `api_key` 可留空，启动时读 `DASHSCOPE_API_KEY`。
- Daytona：`daytona_api_key` 可留空，启动时读 `DAYTONA_API_KEY`。
- 入口：`python main.py`；沙箱相关见 `app/daytona/README.md`、`sandbox_main.py`。
- 依赖见该目录 `requirements.txt`；完整安装可能较慢，可按需分批安装。



### `gui-plus`

- `gui-plus使用.py`：本地图片 `pic.jpg` 转 base64 后调用 `gui-plus`，输出 GUI 原子操作 JSON。
- 依赖 `DASHSCOPE_API_KEY`。



### `Memory`

- 主线看 `Memory/MemoryV2/README.md`：Step1–Step5 压缩与召回，Step6 心跳（有新 `event_id` 才跑前五步）。
- `MemoryV1` 是文件分层管线存档，日常不用看。
- 综合实例：`python Memory/综合实例/run.py`，整理后导入本目录 `FileMemoryWorkspace`，对照有/无记忆两份行程。
- 材料在 `Memory/materials/`，产物在 `Memory/.demo_runs/`。



## 模型选择

模型基本上都选的如 `deepseek-v` 、 `qwen-flash` 之类的便宜模型，主要是省金币

## 说明

- 纯学习用途，代码以可跑通、好对照为主，不可用于生成环境。
- 同一业务场景（投顾助手）会在 LangGraph / LangSmith / Langfuse / DeepEval 中反复出现，方便横向对比「编排 → 追踪 → 评测」。
- `ACP` 用杭州三日游团建目标，对照「主 Agent 拆板 → Codex worker 执行 → 上下文隔离 → TriggerFlow 汇总」。
- `Memory` 用同一套亲子行程对话，对照「压缩 → 升格 → 召回 → 有/无记忆出行程」。
- Windows 环境；运行前确认已激活虚拟环境并设置好对应 API Key。

