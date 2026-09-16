# ACP scripts

`scripts/` 是可以单独运行的课后路径，和 Notebook 没有依赖。每个文件都重复定义自己的数据类和 ACP 会话，打开单个文件就能按顺序读完。

对应提交：`ACP demo代码`。同一次提交还加了 Windows/Mac 最简连接、`Demo/demo1.py` 和 `materials/product_goal.txt`。

仓库里另有 `LangChain/` 示例（提交：`LangChain的一些写法`），用百炼 OpenAI 兼容接口，和本目录的 Codex ACP 脚本不是一条链路。

## 阅读顺序

1. `../ACP最简连接 _Win.py` / `../ACP最简连接_Mac.py`：先看怎么拉起官方 Codex ACP adapter。
2. `01_plan_board.py`：主 Agent 拆任务板，不连 Codex。
3. `02_worker_acp_smoke.py`：只验证 ACP 连接和同 session 多轮 prompt。
4. `03_context_isolation.py`：把任务板裁成子 Agent 私有上下文。
5. `04_triggerflow_master_loop.py`：完整主循环，调度两个 Codex worker。
6. `05_hangzhou_team_building_run.py`：只复盘 04 的运行产物。

业务目标文件：`../materials/product_goal.txt`（杭州三日游团建规划助手）。  
运行结果写到：`../.demo_runs/multi_agent/`。

## 脚本说明

| 文件 | 作用 | 依赖 |
|---|---|---|
| `01_plan_board.py` | DeepSeek 主 Agent 读目标，生成 2–6 张任务卡，校验 DAG 后保存 `01_task_board.json` | `DEEPSEEK_API_KEY` |
| `02_worker_acp_smoke.py` | 启动 `@agentclientprotocol/codex-acp`，initialize / new_session / prompt | Node.js、本机 Codex ACP |
| `03_context_isolation.py` | 读 01 的任务板，构造私有任务包，观察下游卡只能看到显式上游结果 | 先跑 01，再连 Codex ACP |
| `04_triggerflow_master_loop.py` | TriggerFlow 托管调度：拆板、按依赖把卡交给 `codex_research` / `codex_plan`，汇总最终报告 | DeepSeek + Codex ACP |
| `05_hangzhou_team_building_run.py` | 读取 `05_hangzhou_team_building_result.json`，检查任务是否完成并打印报告 | 先跑 04 |

`../Demo/demo1.py` 是另一条 Agently TriggerFlow 演示（Board / Summary / research / plan 并行拆任务），不走 ACP。

## 环境

在 `ACP/` 目录安装依赖：

```text
agent-client-protocol==0.12.1
```

主 Agent 走 DeepSeek，需要环境变量：

```text
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_DEFAULT_MODEL=deepseek-chat
```

ACP worker 走本机 Node + 官方 Codex adapter。Windows 上不要直接 `npx.cmd`，应使用 `node.exe` 执行 `npx-cli.js`（见 `ACP最简连接 _Win.py`）。

示例：

```powershell
e:\code\studyAiCodeDemo\.venv\Scripts\python.exe e:\code\studyAiCodeDemo\ACP\scripts\01_plan_board.py
```
