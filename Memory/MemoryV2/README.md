# MemoryV2 脚本说明

以这个版本为主。`MemoryV1` 是文件分层管线存档，日常不用看。

每个脚本都是一条平铺的直线，没有函数封装。

主线三段：

1. 文档读取：从 `Memory/materials/` 或 `.demo_runs/memory_v2/memory/` 读 JSON/JSONL。
2. 模型压缩 / 模型生成检索关键词：自然语言的判断交给模型。
3. 文档写入：结果写回 `Memory/.demo_runs/memory_v2/memory/`。

依赖：课程目录或更上层 `.env` 里配置 `DASHSCOPE_API_KEY`（可选 `DASHSCOPE_BASE_URL`）。在 `Memory/` 下运行。

```bash
python MemoryV2/Step1_读取会话并压缩存入文件.py         # 会话压缩(Map)
python MemoryV2/Step2_升格把候选记忆升格成长期记忆.py    # 升格长期记忆(Reduce)
python MemoryV2/Step3_新会话召回.py                    # 新会话召回
python MemoryV2/Step4_过程记忆召回.py                  # 过程记忆召回
python MemoryV2/Step5_提取能力记忆.py                  # 能力/方法记忆
python MemoryV2/Step6_心跳触发.py                      # 有新事件才按序跑 Step1-Step5
```

也可以只跑心跳：`Step6_心跳触发.py` 会读 `materials/simulated_long_conversation.jsonl` 的 `event_id`，对比 `.demo_runs/memory_v2/heartbeat_state.json`。有新事件才调度 Step1–Step5；没有就 skip。`main` 连跑两次，用来对照第二次跳过。

| 脚本 | 作用 | 主要产物 |
|---|---|---|
| Step1 | 按会话压缩原始事件 | `session_memory.json` |
| Step2 | 三条通道升格长期记忆 | `long_term_memory.json` |
| Step3 | 新任务开始前召回长期记忆 | `new_session_context.json` |
| Step4 | 会话中途召回当前过程笔记 | `process_context.json` |
| Step5 | 把可复用做法展开成方法卡 | `capability_memory.json` |
| Step6 | 只做调度，不写记忆正文 | `heartbeat_state.json` |

召回脚本（Step3 / Step4）不内置任何业务关键词：先让模型根据当前任务或当前事件生成 `query_keywords`，代码再拿这些词做匹配。代码只负责稳定执行，不做语义判断。

要看「整理后的记忆接到 Workspace，再对照有/无记忆出行程」，跑 `Memory/综合实例/run.py`，不要改本目录脚本。
