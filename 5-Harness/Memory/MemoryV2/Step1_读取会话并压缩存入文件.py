"""01 会话压缩:把原始会话事件压成 session memory。

三段结构:
1. 文档读取:读 materials/simulated_long_conversation.jsonl
2. 模型压缩:每个会话压成 摘要 + 候选记忆 + 过程记忆(讲义里 Map 阶段的最小版本)
3. 文档写入:写 .demo_runs/memory_v2/memory/session_memory.json
"""

import json
import os
from pathlib import Path

from agently import Agently
from dotenv import find_dotenv, load_dotenv

# ========================== 0. 配置模型 ==========================
load_dotenv(find_dotenv())
Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": os.getenv(
            "DASHSCOPE_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        "api_key": os.getenv("DASHSCOPE_API_KEY"),
        "model": "deepseek-v4-flash",
    },
)

# 文件位置
LESSON_DIR = Path(__file__).resolve().parents[1]
MEMORY_DIR = LESSON_DIR / ".demo_runs" / "memory_v2" / "memory"


# ========================== 1. 文件读取 ==========================
# 虚拟对话的位置
raw_path = LESSON_DIR / "materials" / "simulated_long_conversation.jsonl"

events = []
for line in raw_path.read_text(encoding="utf-8").splitlines():
    if line.strip():
        events.append(json.loads(line))
print(f"读入 {len(events)} 条原始事件:")

# 打印一下原始事件
for index, event in enumerate(events):
    print(
        f"原始事件 {index + 1}",
        "\t project_id:",
        event["project_id"],
        "\t\t session_id:",
        event["session_id"],
    )
    print("\t\t", event["role"] if event["role"] else "user", ":", event["text"])
    print("-" * 100)


# 按会话分组:同一个 session_id 的事件放进同一组
sessions = {}
for event in events:
    key = (event["project_id"], event["session_id"])
    if key not in sessions:
        sessions[key] = []
    sessions[key].append(event)
print()


# 打印一下分组结果
print(f"按会话分组结果 {len(sessions)} 个会话:")
for key, value in sessions.items():
    print(key, ":")
    for event in value:
        print(event["turn"], event["text"])
    print("-" * 100)


# ========================== 2. 模型压缩:一个会话压一次 ==========================
compressed_sessions = []
for (project_id, session_id), session_events in sessions.items():
    session_events.sort(key=lambda e: e["turn"])  # 按对话轮次排好
    print(f"正在压缩会话 {session_id}({len(session_events)} 条事件)...")

    agent = Agently.create_agent()
    result = (
        agent.info({"对话事件流": session_events})  # 把这个会话的原始事件交给模型
        .input("对这段对话事件流做记忆抽取。")
        .output(
            {
                "episode_summary": (
                    "str",
                    "三句话以内,概括这次会话做了什么、失败过什么、怎么修正的。",
                ),
                "memory_items": (
                    [
                        (
                            {
                                "type": (
                                    "str",
                                    "user_preference | fact | lesson",
                                    "分为用户偏好、事实、教训三类",
                                ),
                                "statement": (
                                    "str",
                                    "学成脱离本次对话也能读懂的一句话",
                                ),
                                "supporting_event_ids": [
                                    ("str", "只能取给定事件里的 event_id")
                                ],
                                "durable": (
                                    "bool",
                                    "用户是否显式要求长期有效，用户明确说了以后一直有效才是 true",
                                ),
                            },
                            "用户把某个要求说成以后持续适用，必须抽取为 user_preference 类型，并把 durable 设为 true。任务失败后形成的修成原则要抽成 lesson 类型，不要只保留具体失败事实。用户对儿童作息、行程松紧、重点安排时间等稳定偏好要作为候选。",
                        )
                    ],
                    "只抽取以后任务还用得上的信息，寒暄、闲聊、口误、只对当次有效的问答不要抽。",
                ),
            }
        )
        .start()  # 脚本里用同步 start(),和 demo.py 一样
    )
    # 给结果补上会话信息,方便后面的脚本使用
    result["project_id"] = project_id
    result["session_id"] = session_id
    compressed_sessions.append(result)

# ========================== 3. 文档写入 ==========================
out_path = MEMORY_DIR / "session_memory.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(
    json.dumps({"sessions": compressed_sessions}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("已写入文件", out_path)
