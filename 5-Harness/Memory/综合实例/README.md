# 综合实例：文件记忆接入 Workspace

目录里三个文件：


| 文件 | 职责 |
|---|---|
| `memory_pipeline.py` | 自包含的文件记忆管线：raw → 会话压缩 → 升格 → 任务简报 |
| `memory_workspace.py` | 文件记忆 Workspace：ingest / search / build_context |
| `run.py` | 入口：跑管线、导入 Workspace、按任务打包上下文、对照「无记忆 / 有记忆」出行程 |


它不调用 `MemoryV1`、`MemoryV2` 里的单步脚本，是单独的操作、

压缩逻辑写在本目录的 `memory_pipeline.py` 里。变的是存储和召回后端（文件 → Workspace），不变的是「先整理、再按当前任务打包上下文」。

新任务写死在两个文件里：

> 带5岁的女儿去上海玩两天，孩子一直想去迪士尼乐园，帮我出行程，最终路线要可执行。

---

## 如何使用

依赖：Python 能 import `agently`；`.env` 里有 `DEEPSEEK_API_KEY`（可选 `DEEPSEEK_BASE_URL`、`DEEPSEEK_DEFAULT_MODEL`）。原始对话在 `Memory/materials/simulated_long_conversation.jsonl`。

在仓库根目录执行：

```bash
python Memory/综合实例/run.py
```

只跑文件管线、不接 Workspace 时，也可以在别的脚本里：

```python
from memory_pipeline import build_file_memory
await build_file_memory(某个目录)
```

`run.py` 每次都会删掉 `.demo_runs/integrated_workspace_case/` 再重建，适合演示，不要把该目录当长期库。

`LESSON_DIR` 是 `Memory/`。材料读 `Memory/materials/`，产物写 `Memory/.demo_runs/integrated_workspace_case/`。

当前安装的 Agently 4.1 没有 `Agently.create_workspace`（库里的 `TaskWorkspace` 是任务文件沙箱）。综合实例用本目录的 `FileMemoryWorkspace` 承接同样的 ingest / search / build_context。

---



## 代码功能

一次 `run.py` 做完四件事。

### 1. 从历史对话做出文件记忆

`build_file_memory` 读模拟长对话，写出：


| 产物                                        | 层       | 内容                     |
| ----------------------------------------- | ------- | ---------------------- |
| `file_memory/raw_events.jsonl`            | raw     | 事件原样保存，不总结             |
| `file_memory/event_index.jsonl`           | 证据索引    | 后续升格用来核对 event_id、工具失败 |
| `file_memory/consolidated_sessions.jsonl` | 会话压缩    | 每个会话一条摘要               |
| `file_memory/candidate_memories.jsonl`    | 候选      | 偏好 / 事实 / 教训           |
| `file_memory/semantic_rules.jsonl`        | 长期规则    | 通过三条升格通道的              |
| `file_memory/kept_candidates.jsonl`       | 未升格     | 证据不够，留着等新证据            |
| `file_memory/task_brief.json`             | 文件版工作记忆 | 按新任务筛过的规则 + 两条相关会话摘要   |




### 2. 导入 Workspace

把会话摘要和长期规则 `ingest` 进两个 collection：

- `memory-consolidated`：会话摘要，scope 带 `project_id` + `session_id`
- `memory-semantic`：规则，scope 只带 `project_id`

每条都带 `source`（来自哪个文件、哪个 `rule_id`）和 `meta`（如 `promotion_reason`），方便审计。

### 3. 按新任务打上下文包

- 用 filter 只搜 `travel-agent` 的语义规则（报销项目进不来）
- `build_context` 按 goal、scope、字数预算从 Workspace 里选条目
- 组成 `task_brief`：任务原文、稳定规则、最多 5 条选中记忆



### 4. A/B 出行程

同一句新任务调两次 `draft_itinerary`：

- `draft_without_memory`：不给长期规则，`规则遵守` 必须是空列表
- `draft_with_memory`：注入稳定规则和过往摘要，要求迪士尼独占一天、午睡窗口、输出附路线检查结论

有记忆的那次还会：

1. `apply_memory_guards`：规则里要求检查结论或午休，但模型没写进「输出附带」时，代码直接补上
2. `check_rule_compliance`：再让模型按规则原文逐条标 已满足 / 部分满足 / 未满足

控制台打印三段 JSON：`task_brief`、无记忆草案、有记忆草案，用来看记忆有没有改变行程结构。

---



## 实现功能：管线怎么压

`memory_pipeline.py` 对应 MemoryV1 的 02→05，但是一个函数跑完。

```
模拟对话 jsonl
    → 按 (project_id, session_id) 分组
    → 每个会话模型抽取：摘要 + memory_items
    → 按项目合并同义候选
    → 三条通道决定升格或留下
    → 按新任务过滤 travel-agent，关键词给会话摘要打分，取前 2 条
```

升格通道（都不满足则不进 `semantic_rules`）：


| `promotion_reason`          | 条件                        |
| --------------------------- | ------------------------- |
| `repeated_across_sessions`  | 合并后的成员来自至少两个会话            |
| `tool_failure_evidence`     | 证据事件里有 `status == failed` |
| `explicit_user_instruction` | 类型是偏好且有 `durable == true` |


模型调用（抽取、合并、出行程、核规则）遇到 503、忙服、结构解析失败会重试最多 4 次。

文件版 `task_brief` 里的会话摘要用写死关键词打分（孩子、亲子、路线、迪士尼等）。`run.py` 里真正给模型用的简报，来自 Workspace 的 `search` + `build_context`，不是这份文件打分结果。文件 `task_brief.json` 是管线自检产物，对照 Workspace 包可以看到两边是否一致。

---



## 实现功能：Workspace 怎么用记忆

```
file_memory/*.jsonl
    → workspace.ingest（带 collection / kind / scope / source）
    → search(project_id=travel-agent) 取出稳定规则
    → build_context(goal=新任务, budget=1600 字) 取出相关条目
    → 有记忆 / 无记忆 各出一份行程
```

和 MemoryV2 新会话召回的差别：V2 是模型生成检索词、代码按词匹配文件；这里把检索交给 Workspace（scope 隔离 + 上下文预算）。文件管线仍然负责「记忆从哪来、凭什么升格」。

`apply_memory_guards` 不是兼容旧数据，而是演示：长期规则不能只靠模型自觉。规则要求检查结论或午休，输出里没有对应句子，就由代码补一条，避免 A/B 对照时「有记忆却看不出落点」。

---



## 和另外两条讲义线的关系


|       | MemoryV2 Step1–Step5    | MemoryV1 02–05                   | 本综合实例                                   |
| ----- | ----------------------- | -------------------------------- | --------------------------------------- |
| 产物目录  | `.demo_runs/memory_v2/` | `.demo_runs/file_memory_layers/` | `.demo_runs/integrated_workspace_case/` |
| 怎么跑   | 单步脚本或 Step6 心跳          | 单步脚本或 06 心跳                      | 一次 `run.py`                             |
| 召回    | 文件 + 关键词匹配              | 文件 `task_brief.json`             | Workspace `build_context`               |
| 是否出行程 | 否（停在上下文文件）              | 07 只打印简报                         | 有/无记忆两份行程草案                             |


要看「记忆系统接到 Workspace 之后，新任务输出有什么不同」，跑本目录的 `run.py`。要单步看压缩或心跳，用 `MemoryV1` / `MemoryV2`。