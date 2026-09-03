# 06 心跳触发器

脚本：`06_heartbeat_trigger.py`  
工作目录：课程目录 `Memory/`（不是 `MemoryV2/`）  
状态文件：`.demo_runs/file_memory_layers/heartbeat_state.json`  
记忆目录：`.demo_runs/file_memory_layers/memory/`

心跳**自己不做抽取、不升格、不打包任务上下文**。分层整理已经拆成 `02`–`05` 四个脚本。心跳只做调度：

1. 确保 raw 文件存在  
2. 对比 checkpoint，判断有没有新 raw 事件  
3. 有新事件时触发四层整理里的后三步  
4. 写回 `heartbeat_state.json`

对应讲义里的「什么时候激活压缩管线」，不是「压缩动作本身」。

---

## 作用：解决什么问题

`02`–`05` 可以手动一个个跑。生产里不能等人手点：对话在涨、历史在进，整理要在后台自动发生。

心跳回答的是：

> 现在要不要整理？如果要，按顺序跑哪几个脚本？跑完把进度记在哪，以免下次重复整理？

不是：

> 这段对话该抽出哪条规则、哪张方法卡？

后者仍由 `03`、`04`、`05` 负责。心跳只决定**何时启动它们**。

和 Step1–Step5 那条讲义主线不是同一套管线：

| | Step1–Step5 | 02–05 + 心跳 |
|---|---|---|
| 目录产物 | `.demo_runs/memory_v2/` | `.demo_runs/file_memory_layers/` |
| 谁触发整理 | 人手按顺序跑 | 心跳看 checkpoint，有新事件才跑 |
| 这一步的角色 | 每个脚本自己完成一段压缩 | 06 只调度，不写记忆正文 |

`07_file_recall.py` 读的是心跳（或手动 02–05）产出的 `task_brief.json`。没有心跳、也没有手动跑完 05，07 会直接报缺文件。

---

## 和 02–05、07 怎么串

四层整理（心跳要调度的对象）：

| 脚本 | 层 | 做什么 | 主要产物 |
|---|---|---|---|
| `02_collect_raw.py` | raw | 把 `materials/simulated_long_conversation.jsonl` 原样拷进记忆库，不总结 | `memory/raw_events.jsonl` |
| `03_extract_consolidated.py` | consolidated | 按会话压缩：摘要、候选记忆、事件索引 | `consolidated_sessions.jsonl`、`candidate_memories.jsonl`、`event_index.jsonl` |
| `04_promote_semantic.py` | semantic | 候选按三条通道升格；证据不够的留下 | `semantic_rules.jsonl`、`kept_candidates.jsonl`、`promotion_report.json` |
| `05_build_working_memory.py` | working | 按当前任务从规则和会话摘要里打一包临时上下文 | `task_brief.json` |

心跳里的调用顺序：

```
ensure_raw_file          → 缺 raw 时才跑 02
scan_checkpoint          → 和新事件 id 做差
run_consolidation_steps  → 有新事件才跑 03、04、05（不再跑 02）
write_checkpoint         → 把已处理 id 写进 heartbeat_state.json
```

`02` 只在 raw 文件不存在时跑一次，用来「建库」。之后心跳只扫新事件、跑整理。`07` 不参与心跳，它是整理完成之后的消费端：把 `task_brief.json` 打印成「新任务该看见的规则和摘要」。

注意：`02_collect_raw.py` 开头会删掉整个 `.demo_runs/file_memory_layers/`。所以它适合空库初始化，不适合在已有 checkpoint 的库上反复跑。心跳因此把 02 和 03–05 拆开：有库就不要再跑 02。

---

## 功能：代码怎么走

整段流程用 Agently 的 `TriggerFlow` 串成四个异步节点，一次心跳就是跑完这条链。

### 0. 路径和辅助函数

- `LESSON_DIR`：`Memory/`（脚本的上一级）
- `STEP_SCRIPTS`：四个整理脚本的相对路径，`subprocess` 的工作目录就是 `LESSON_DIR`
- `read_state` / `write_state`：读写 checkpoint；没有状态文件时当成「一个事件都没处理过」
- `adaptive_interval_seconds`：根据**本轮新事件数量**建议下次间隔  
  - 新事件 ≥ 10：60 秒（忙，加快扫）  
  - 新事件 ≥ 1：300 秒  
  - 没有新事件：900 秒（闲，放慢）  

脚本本身不会按这个秒数去 sleep，只把建议写进报告，留给 crontab / 任务计划程序使用。

### 1. `ensure_raw_file`：确保有 raw

`raw_events.jsonl` 不存在就跑 `02`。然后读出全部 `event_id` 放进 flow 状态 `raw_event_ids`。

这一步只保证「有完整事件流」，不做价值判断。

### 2. `scan_checkpoint`：找出新事件

读 `heartbeat_state.json` 里的 `processed_event_ids`，和当前 raw 里的 id 做差，得到 `new_event_ids`。

判断标准是**事件 id 集合**，不是文件修改时间。同一批事件整理过就不会因为文件还在而再跑一遍。

### 3. `run_consolidation_steps`：有新事件才整理

`new_event_ids` 为空：跳过，`skipped: true`，`reason: no_new_raw_events`。  
非空：按顺序跑 `03`、`04`、`05`。

语义判断仍在 03/04 的模型调用里；心跳这边只保证顺序和「有增量才跑」。

### 4. `write_checkpoint`：记进度、出报告

把旧的已处理 id 和本轮新 id 合并，写回状态文件：

```json
{
  "processed_event_ids": ["evt_a01", "..."],
  "last_report": {
    "new_raw_count": 36,
    "processed_event_count": 36,
    "steps_ran": ["scripts/03_extract_consolidated.py", "..."],
    "next_interval_seconds": 60
  }
}
```

`last_report` 用来审计：本轮新了多少条、跑了哪些脚本、建议下次隔多久。`processed_event_ids` 用来保证下次心跳可复现地跳过。

### 5. `main`：故意跑两次

```python
first = await heartbeat_once()
second = await heartbeat_once()
```

这是演示，不是生产循环：

- **第一次**：通常 raw 不存在或事件未处理 → 建库 + 跑 03–05 → `skipped: false`
- **第二次**：checkpoint 已覆盖全部 id → 不再跑整理 → `skipped: true`

用来对照「心跳不是每次都全量重压」，增量判断生效了。

---

## 如何结合脚本使用

当前四个整理脚本在 `MemoryV2/` 下。`06_heartbeat_trigger.py` 里 `STEP_SCRIPTS` 仍写着 `scripts/02_collect_raw.py` 这一类路径，而 `subprocess` 的工作目录是 `Memory/`。要让心跳真正调起它们，把四条改成：

```python
STEP_SCRIPTS = [
    "MemoryV2/02_collect_raw.py",
    "MemoryV2/03_extract_consolidated.py",
    "MemoryV2/04_promote_semantic.py",
    "MemoryV2/05_build_working_memory.py",
]
```

`07_file_recall.py` 报错文案里的 `scripts/` 同理，只是提示文字，不影响心跳调度。

### 方式 A：只跑心跳（推荐用来看调度）

在 `Memory/` 下：

```bash
python MemoryV2/06_heartbeat_trigger.py
```

依赖：`03`、`04` 会调模型，课程根目录或更上层的 `.env` 里要有 `DEEPSEEK_API_KEY`。`02`、`05` 不调模型。

第一次会较慢（03/04 要抽记忆、升格）。控制台最后打印类似：

```json
{
  "first_heartbeat": {
    "new_raw_count": 36,
    "processed_event_count": 36,
    "steps_ran": [
      "MemoryV2/03_extract_consolidated.py",
      "MemoryV2/04_promote_semantic.py",
      "MemoryV2/05_build_working_memory.py"
    ],
    "next_interval_seconds": 60
  },
  "second_heartbeat": {
    "new_raw_count": 0,
    "processed_event_count": 36,
    "steps_ran": [],
    "next_interval_seconds": 900
  }
}
```

然后可以看产物，或跑消费端：

```bash
python MemoryV2/07_file_recall.py
```

07 只读 `task_brief.json`，不再整理。

### 方式 B：不用心跳，手动跑四层

适合单步调试某一个压缩脚本：

```bash
python MemoryV2/02_collect_raw.py
python MemoryV2/03_extract_consolidated.py
python MemoryV2/04_promote_semantic.py
python MemoryV2/05_build_working_memory.py
python MemoryV2/07_file_recall.py
```

手动跑完 05 之后，如果再跑心跳：raw 已在、事件尚未记入 checkpoint，心跳仍会再跑一遍 03–05，然后写下状态。若要演示「第二次跳过」，应先让心跳写过 `heartbeat_state.json`，或先删状态再跑两次心跳。

### 方式 C：模拟「又来了新事件」

1. 先跑通一次心跳，确认第二次是 skip  
2. 向 `memory/raw_events.jsonl` 追加若干带新 `event_id` 的行（不要改已有 id）  
3. 再跑 `06_heartbeat_trigger.py`  

本轮 `new_raw_count > 0`，会再跑 03–05，并把新 id 并进 `processed_event_ids`。不要重新跑 `02`：它会清空整个 `file_memory_layers` 目录，checkpoint 和已整理文件一起没。

### 接到系统定时任务

讲义里的 crontab / `schtasks` 每 15 分钟跑压缩脚本；这份心跳把「有没有新事件」收进进程内部。定时任务只需反复启动 06（生产里可改成 `heartbeat_once()` 只跑一轮，不要 `main` 里连跑两次）：

```text
*/15 * * * * cd /path/to/Memory && python MemoryV2/06_heartbeat_trigger.py
```

间隔也可以读 `last_report.next_interval_seconds` 做成自适应，脚本已经把数字算好了，调度器还没接上。

两条触发线仍可并存：对话结束钩子抓「工具失败、用户说以后都这样」立刻投递一次心跳；定时任务兜底低频会话和漏跑。

---

## 为什么这样设计

**心跳不内置抽取逻辑。** 整理规则变了只改 03/04/05；触发策略变了只改 06。避免「调度器和压缩器写在同一个文件里」，改一处全乱。

**用事件 id 做 checkpoint，不用「距上次多少分钟」。** 没有新 raw 就跳过，省模型和重复写入。有新 id 才全量重跑 03–05（当前最小实现是：只要有增量，就对当前整库再整理一遍，而不是只处理那几条新事件）。

**第二次心跳是教材，不是 bug。** 用来看见 skip 和 `next_interval_seconds` 从 60 变成 900。

**后台自动写记忆仍要能审计。** 状态文件里能看到处理过哪些 `event_id`、本轮跑了哪些脚本。真正的来源和证据在 03/04 的 `supported_event_ids` / `promotion_reason` 里；心跳只保证「整理过没」可核对。没有 checkpoint 的定时全量重写，容易变成讲义里说的自动污染。
