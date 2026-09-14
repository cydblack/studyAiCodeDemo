# ===== 并行分发版主 Agent 流程：环境和对象准备 =====
import asyncio
import json
import os
from typing import Any, Awaitable, Callable, cast

from agently import Agently, TriggerFlow, TriggerFlowRuntimeData
from dotenv import find_dotenv, load_dotenv

# ========================== 配置模型 ==========================
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

# ========================== 创建 Agent ==========================
# 做好了分工：Board Agent 负责制定计划，Summary Agent 负责总结，Workers 负责执行。

# 创建 Board Agent
cyd_board_agent = Agently.create_agent("cyd-pipeline-board-agent")

# 创建 Summary Agent
cyd_summary_agent = Agently.create_agent("cyd-pipeline-summary-agent")

# 创建 Workers（两个 Worker，一个负责研究，一个负责计划）
cyd_workers = {
    "research": Agently.create_agent("cyd-pipeline-research-worker"),
    "plan": Agently.create_agent("cyd-pipeline-plan-worker"),
}

# 创建 Worker Notes
cyd_worker_notes = {
    "research": "信息侦察员：只整理已知事实、约束条件、信息缺口、风险和需要追问的问题；不设计方案，不写最终安排。",
    "plan": "方案草拟员：只基于用户原始输入产出可执行草案、步骤、安排和取舍；不等待 research，不引用 research 结果。",
}

# 创建 Worker Output Rules
cyd_worker_output_rules = {
    "research": "输出已知事实、关键缺口、风险提醒、需要追问的问题。",
    "plan": "输出并行草案、执行步骤、时间/资源安排、草案中暂时采用的假设。",
}

# ========================== 模拟用户的输入 ==========================
user_input = "杭州三日两晚团建，目标是团队融合、轻度协作活动和城市体验。"


# ==========================  创建 Flow  ==========================
pipeline_flow = TriggerFlow[Any, Any, Any](name="cyd-master-agent-pipeline")


# ===================== 实战 1 的缓存变量：对象和分工表 ==================
cached_setup = {
    "flow": "cyd-master-agent-pipeline",
    "user_input": user_input,
    "workers": list(cyd_workers),
    "worker_notes": cyd_worker_notes,
    "worker_output_rules": cyd_worker_output_rules,
}
print("===== 缓存变量：对象和分工表 =====")
print(json.dumps(cached_setup, ensure_ascii=False, indent=2))


# ===================== 实战 2. 用户输入拆成任务板 =====================
# ===== 拆任务：Agently 生成任务板，Python 只补运行字段 =====
async def create_simple_board(user_input: str) -> list[dict[str, object]]:
    raw_board = await (
        cyd_board_agent.input(
            {
                "用户输入": user_input,
                "可用 worker": cyd_worker_notes,
                "分工规则": "research 和 plan 必须并行工作。research 负责事实和缺口；plan 负责基于原始输入草拟方案。plan 不等待 research，也不能引用 research 结果。",
                "要求": "只拆成 2 张任务卡：一张 research，一张 plan。两张卡互相独立，任务说明都只能引用用户原始输入。",
            }
        )
        .output(
            {
                "tasks": [
                    {
                        "task_id": (str, "稳定任务 id，例如 research_facts", True),
                        "title": (str, "任务标题", True),
                        "worker": (str, "只能是 research 或 plan", True),
                        "prompt": (str, "发给 worker 的局部任务说明", True),
                    }
                ]
            },
            format="json",
        )
        .async_start()
    )
    if not isinstance(raw_board, dict) or not isinstance(raw_board.get("tasks"), list):
        raise RuntimeError("主 Agent 需要返回 {'tasks': [...]} 结构")

    board: list[dict[str, object]] = []
    for index, task in enumerate(raw_board["tasks"][:4], start=1):
        if not isinstance(task, dict):
            raise RuntimeError("每张任务卡都需要是 dict")

        worker = str(task["worker"]).strip()
        if worker not in cyd_workers:
            raise RuntimeError("worker 只能是 research 或 plan")

        board.append(
            {
                "task_id": str(task["task_id"]).strip() or f"task_{index}",
                "title": str(task["title"]).strip(),
                "worker": worker,
                "prompt": str(task["prompt"]).strip(),
                "status": "todo",
                "result": "",
            }
        )

    if len(board) != 2 or {task["worker"] for task in board} != {"research", "plan"}:
        raise RuntimeError("任务板需要且只需要一张 research 卡和一张 plan 卡")
    return board


def render_simple_board(board: list[dict[str, object]]) -> str:
    lines = ["task_id | status | worker | title"]
    for item in board:
        lines.append(
            f"{item['task_id']} | {item['status']} | {item['worker']} | {item['title']}"
        )
    return "\n".join(lines)


async def main() -> None:
    board = await create_simple_board(user_input)
    print("===== 用户输入拆成任务板 =====")
    print(render_simple_board(board))
    print(json.dumps(board, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

