#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分步演示：混合财富顾问 + LangSmith 追踪

对 投顾助手+langsmith.py 做非交互式 Step 执行，
每个图节点结束后打印中间状态，便于对照 LangSmith Trace。
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.runnables import RunnableConfig

# Windows 控制台按 UTF-8 打印 Step，避免中文乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _load_advisor_module():
    """动态加载同目录主脚本（文件名含连字符，无法直接 import）。"""
    path = Path(__file__).parent / "投顾助手+langsmith.py"
    spec = importlib.util.spec_from_file_location("wealth_advisor_langsmith", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _brief(value: Any, limit: int = 280) -> str:
    """把状态字段压缩成可读短文本。"""
    if value is None:
        return "None"
    if isinstance(value, str):
        text = value.strip().replace("\n", " ")
        return text if len(text) <= limit else text[: limit - 3] + "..."
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        text = str(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _print_step(step_no: int, node_name: str, state: Dict[str, Any]) -> None:
    """按 Step 打印节点输出的关键字段。"""
    print("\n" + "=" * 64)
    print(f"Step {step_no}: 节点 [{node_name}]")
    print("=" * 64)
    keys = [
        "query_type",
        "processing_mode",
        "current_phase",
        "market_data",
        "analysis_results",
        "final_response",
        "error",
    ]
    for key in keys:
        if key in state and state.get(key) is not None:
            print(f"  - {key}: {_brief(state.get(key))}")


def _build_config(
    mod, customer_id: str, customer_profile: Dict[str, Any], user_query: str
):
    """构造 LangSmith RunnableConfig（仅在追踪开启时返回）。"""
    if not mod.LANGSMITH_ENABLED:
        return None
    return RunnableConfig(
        tags=[
            "wealth-advisor",
            "hybrid-agent",
            "step-demo",
            f"customer-{customer_id}",
            customer_profile.get("risk_tolerance", "unknown"),
        ],
        metadata={
            "customer_id": customer_id,
            "risk_tolerance": customer_profile.get("risk_tolerance", "unknown"),
            "investment_horizon": customer_profile.get("investment_horizon", "unknown"),
            "portfolio_value": customer_profile.get("portfolio_value", 0),
            "user_query": user_query[:100],
            "timestamp": datetime.now().isoformat(),
            "demo": "step_demo",
        },
        run_name=f"step-demo-{customer_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )


def run_case(
    mod,
    case_name: str,
    user_query: str,
    customer_id: str = "customer1",
) -> Dict[str, Any]:
    """运行单个用例，stream 每个节点并打印 Step。"""
    print("\n" + "#" * 72)
    print(f"# 用例: {case_name}")
    print(f"# 查询: {user_query}")
    print(f"# 客户: {customer_id}")
    print("#" * 72)

    agent = mod.create_wealth_advisor_workflow()
    customer_profile = mod.SAMPLE_CUSTOMER_PROFILES.get(
        customer_id, mod.SAMPLE_CUSTOMER_PROFILES["customer1"]
    )

    initial_state = {
        "user_query": user_query,
        "customer_profile": customer_profile,
        "query_type": None,
        "processing_mode": None,
        "emergency_response": None,
        "market_data": None,
        "analysis_results": None,
        "final_response": None,
        "current_phase": "assess",
        "error": None,
    }

    config = _build_config(mod, customer_id, customer_profile, user_query)
    steps: List[Dict[str, Any]] = []
    final_state: Optional[Dict[str, Any]] = None
    step_no = 0
    started = datetime.now()

    # LangGraph stream：每个事件是 {node_name: state_delta_or_full}
    stream_kwargs = {"config": config} if config else {}
    for event in agent.stream(initial_state, **stream_kwargs):
        for node_name, node_state in event.items():
            step_no += 1
            _print_step(step_no, node_name, node_state)
            steps.append(
                {
                    "step": step_no,
                    "node": node_name,
                    "query_type": node_state.get("query_type"),
                    "processing_mode": node_state.get("processing_mode"),
                    "current_phase": node_state.get("current_phase"),
                    "final_response_preview": (
                        _brief(node_state.get("final_response"), 160)
                        if node_state.get("final_response")
                        else None
                    ),
                    "error": node_state.get("error"),
                }
            )
            final_state = node_state

    elapsed = (datetime.now() - started).total_seconds()
    print("\n" + "-" * 64)
    print(
        f"用例完成 | 模式={final_state.get('processing_mode') if final_state else '未知'} | 用时={elapsed:.2f}s"
    )
    if final_state and final_state.get("final_response"):
        print(f"最终响应预览: {_brief(final_state['final_response'], 400)}")
    print("-" * 64)

    return {
        "case_name": case_name,
        "user_query": user_query,
        "customer_id": customer_id,
        "processing_mode": final_state.get("processing_mode") if final_state else None,
        "query_type": final_state.get("query_type") if final_state else None,
        "elapsed_seconds": elapsed,
        "steps": steps,
        "final_response": final_state.get("final_response") if final_state else None,
        "error": final_state.get("error") if final_state else None,
        "langsmith_enabled": mod.LANGSMITH_ENABLED,
        "langsmith_project": mod.LANGSMITH_PROJECT,
    }


def main() -> int:
    print("=== 开始执行 智能体 + LangSmith ===\n")
    mod = _load_advisor_module()

    print(f"LANGSMITH_ENABLED = {mod.LANGSMITH_ENABLED}")
    print(f"LANGCHAIN_PROJECT = {mod.LANGSMITH_PROJECT}")
    print(f"DASHSCOPE_API_KEY 已设置 = {bool(os.getenv('DASHSCOPE_API_KEY'))}")

    cases = [
        ("反应式-行情查询", "今天上证指数的表现如何？", "customer1"),
        (
            "深思熟虑-组合优化",
            "根据当前市场情况，我应该如何调整投资组合以应对可能的经济衰退？",
            "customer1",
        ),
    ]

    results = []
    for name, query, cid in cases:
        try:
            results.append(run_case(mod, name, query, cid))
        except Exception as exc:
            print(f"\n[ERROR] 用例 [{name}] 失败: {exc}")
            results.append(
                {
                    "case_name": name,
                    "user_query": query,
                    "customer_id": cid,
                    "error": str(exc),
                    "steps": [],
                    "langsmith_enabled": mod.LANGSMITH_ENABLED,
                    "langsmith_project": mod.LANGSMITH_PROJECT,
                }
            )

    # 写出 JSON，供 HTML 报告引用
    out_path = Path(__file__).parent / "step_demo_results.json"
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "results": results,
    }
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nStep 结果已写入: {out_path}")
    return 0 if all(not r.get("error") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
