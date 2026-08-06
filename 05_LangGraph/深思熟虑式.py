#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
深思熟虑智能体（Deliberative Agent）- 智能投研助手

基于LangGraph实现的深思熟虑型智能体，适用于投资研究场景，能够整合数据，
进行多步骤分析和推理，生成投资观点和研究报告。

核心流程：
1. 感知：收集市场数据和信息
2. 建模：构建内部世界模型，理解市场状态
3. 推理：生成多个候选分析方案并模拟结果
4. 决策：选择最优投资观点并形成报告
5. 报告：生成完整研究报告
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Literal, TypedDict, Optional, Union, Tuple
from datetime import datetime

import yaml
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Tongyi
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    PydanticOutputParser,
)
from pydantic import BaseModel, Field, field_validator
from langgraph.graph import StateGraph, END

# Prompt YAML 文件路径
PROMPTS_FILE = Path(__file__).parent / "prompts" / "深思熟虑式_prompts.yaml"


def load_prompts() -> Dict[str, str]:
    """从统一 YAML 文件加载全部提示词模板"""
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 加载全部提示词
_PROMPTS = load_prompts()
PERCEPTION_PROMPT = _PROMPTS["PERCEPTION"]
MODELING_PROMPT = _PROMPTS["MODELING"]
REASONING_PROMPT = _PROMPTS["REASONING"]
DECISION_PROMPT = _PROMPTS["DECISION"]
REPORT_PROMPT = _PROMPTS["REPORT"]

# 设置API密钥
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 创建LLM实例
llm = Tongyi(model_name="qwen-flash", dashscope_api_key=DASHSCOPE_API_KEY)


# 定义输出模型
class PerceptionOutput(BaseModel):
    """感知阶段输出的市场数据和信息"""

    market_overview: str = Field(..., description="市场概况和最新动态")
    key_indicators: Dict[str, str] = Field(..., description="关键经济和市场指标")
    recent_news: List[str] = Field(..., description="近期重要新闻")
    industry_trends: Dict[str, str] = Field(..., description="行业趋势分析")


class ModelingOutput(BaseModel):
    """建模阶段输出的内部世界模型"""

    market_state: str = Field(..., description="当前市场状态评估")
    economic_cycle: str = Field(..., description="经济周期判断")
    risk_factors: List[str] = Field(..., description="主要风险因素")
    opportunity_areas: List[str] = Field(..., description="潜在机会领域")
    market_sentiment: str = Field(..., description="市场情绪分析")


class ReasoningPlan(BaseModel):
    """推理阶段生成的候选分析方案"""

    plan_id: str = Field(..., description="方案ID")
    hypothesis: str = Field(..., description="投资假设")
    analysis_approach: str = Field(..., description="分析方法")
    expected_outcome: str = Field(..., description="预期结果")
    confidence_level: float = Field(..., description="置信度(0-1)")
    pros: List[str] = Field(..., description="方案优势")
    cons: List[str] = Field(..., description="方案劣势")


class DecisionOutput(BaseModel):
    """决策阶段选择的最优投资观点"""

    selected_plan_id: str = Field(..., description="选中的方案ID")
    investment_thesis: str = Field(..., description="投资论点")
    supporting_evidence: List[str] = Field(..., description="支持证据")
    risk_assessment: str = Field(..., description="风险评估")
    recommendation: str = Field(..., description="投资建议")
    timeframe: str = Field(..., description="时间框架")


# 定义智能体状态
class ResearchAgentState(TypedDict):
    """研究智能体的状态"""

    # 输入
    research_topic: str  # 研究主题
    industry_focus: str  # 行业焦点
    time_horizon: str  # 时间范围(短期/中期/长期)

    # 处理状态
    perception_data: Optional[Dict[str, Any]]  # 感知阶段收集的数据
    world_model: Optional[Dict[str, Any]]  # 内部世界模型
    reasoning_plans: Optional[List[Dict[str, Any]]]  # 候选分析方案
    selected_plan: Optional[Dict[str, Any]]  # 选中的最优方案

    # 输出
    final_report: Optional[str]  # 最终研究报告

    # 控制流
    current_phase: Literal["perception", "modeling", "reasoning", "decision", "report"]
    error: Optional[str]  # 错误信息


# 第一阶段：感知 - 收集市场数据和信息
def perception(state: ResearchAgentState) -> ResearchAgentState:
    """感知阶段：收集和整理市场数据和信息"""

    print("1. 感知阶段：收集市场数据和信息...")

    try:
        # 准备提示
        prompt = ChatPromptTemplate.from_template(PERCEPTION_PROMPT)

        # 构建输入
        input_data = {
            "research_topic": state["research_topic"],
            "industry_focus": state["industry_focus"],
            "time_horizon": state["time_horizon"],
        }

        # 调用LLM
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke(input_data)

        # 更新状态
        return {**state, "perception_data": result, "current_phase": "modeling"}
    except Exception as e:
        return {
            **state,
            "error": f"感知阶段出错: {str(e)}",
            "current_phase": "perception",  # 保持在当前阶段
        }


# 第二阶段：建模 - 构建内部世界模型
def modeling(state: ResearchAgentState) -> ResearchAgentState:
    """建模阶段：构建内部世界模型，理解市场状态"""

    print("2. 建模阶段：构建内部世界模型...")

    try:
        # 确保感知数据已存在
        if not state.get("perception_data"):
            return {
                **state,
                "error": "建模阶段缺少感知数据",
                "current_phase": "perception",  # 回到感知阶段
            }

        # 准备提示
        prompt = ChatPromptTemplate.from_template(MODELING_PROMPT)

        # 构建输入
        input_data = {
            "research_topic": state["research_topic"],
            "industry_focus": state["industry_focus"],
            "time_horizon": state["time_horizon"],
            "perception_data": json.dumps(
                state["perception_data"], ensure_ascii=False, indent=2
            ),
        }

        # 调用LLM
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke(input_data)

        # 更新状态
        return {**state, "world_model": result, "current_phase": "reasoning"}
    except Exception as e:
        return {
            **state,
            "error": f"建模阶段出错: {str(e)}",
            "current_phase": "modeling",  # 保持在当前阶段
        }


# 第三阶段：推理 - 生成候选分析方案
def reasoning(state: ResearchAgentState) -> ResearchAgentState:
    """推理阶段：生成多个候选分析方案并模拟结果"""

    print("3. 推理阶段：生成候选分析方案...")

    try:
        # 确保世界模型已存在
        if not state.get("world_model"):
            return {
                **state,
                "error": "推理阶段缺少世界模型",
                "current_phase": "modeling",  # 回到建模阶段
            }

        # 准备提示
        prompt = ChatPromptTemplate.from_template(REASONING_PROMPT)

        # 构建输入
        input_data = {
            "research_topic": state["research_topic"],
            "industry_focus": state["industry_focus"],
            "time_horizon": state["time_horizon"],
            "world_model": json.dumps(
                state["world_model"], ensure_ascii=False, indent=2
            ),
        }

        # 调用LLM
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke(input_data)

        # 更新状态
        return {**state, "reasoning_plans": result, "current_phase": "decision"}
    except Exception as e:
        return {
            **state,
            "error": f"推理阶段出错: {str(e)}",
            "current_phase": "reasoning",  # 保持在当前阶段
        }


# 第四阶段：决策 - 选择最优方案
def decision(state: ResearchAgentState) -> ResearchAgentState:
    """决策阶段：评估候选方案并选择最优投资观点"""

    print("4. 决策阶段：选择最优投资观点...")

    try:
        # 确保候选方案已存在
        if not state.get("reasoning_plans"):
            return {
                **state,
                "error": "决策阶段缺少候选方案",
                "current_phase": "reasoning",  # 回到推理阶段
            }

        # 准备提示
        prompt = ChatPromptTemplate.from_template(DECISION_PROMPT)

        # 构建输入
        input_data = {
            "research_topic": state["research_topic"],
            "industry_focus": state["industry_focus"],
            "time_horizon": state["time_horizon"],
            "world_model": json.dumps(
                state["world_model"], ensure_ascii=False, indent=2
            ),
            "reasoning_plans": json.dumps(
                state["reasoning_plans"], ensure_ascii=False, indent=2
            ),
        }

        # 调用LLM
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke(input_data)

        # 更新状态
        return {**state, "selected_plan": result, "current_phase": "report"}
    except Exception as e:
        return {
            **state,
            "error": f"决策阶段出错: {str(e)}",
            "current_phase": "decision",  # 保持在当前阶段
        }


# 第五阶段：报告 - 生成完整研究报告
def report_generation(state: ResearchAgentState) -> ResearchAgentState:
    """报告阶段：生成完整的投资研究报告"""

    print("5. 报告阶段：生成完整研究报告...")

    try:
        # 确保选定方案已存在
        if not state.get("selected_plan"):
            return {
                **state,
                "error": "报告阶段缺少选定方案",
                "current_phase": "decision",  # 回到决策阶段
            }

        # 准备提示
        prompt = ChatPromptTemplate.from_template(REPORT_PROMPT)

        # 构建输入
        input_data = {
            "research_topic": state["research_topic"],
            "industry_focus": state["industry_focus"],
            "time_horizon": state["time_horizon"],
            "perception_data": json.dumps(
                state["perception_data"], ensure_ascii=False, indent=2
            ),
            "world_model": json.dumps(
                state["world_model"], ensure_ascii=False, indent=2
            ),
            "selected_plan": json.dumps(
                state["selected_plan"], ensure_ascii=False, indent=2
            ),
        }

        # 调用LLM
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke(input_data)

        # 更新状态
        return {**state, "final_report": result, "current_phase": "completed"}
    except Exception as e:
        return {
            **state,
            "error": f"报告生成阶段出错: {str(e)}",
            "current_phase": "report",  # 保持在当前阶段
        }


# 路由函数 - 根据当前阶段决定下一步
def router(state: ResearchAgentState) -> str:
    """根据当前阶段路由到下一步或结束"""

    # 如果有错误，保持在当前阶段
    if state.get("error"):
        return state["current_phase"]

    # 根据当前阶段决定下一步
    current = state["current_phase"]

    if current == "perception":
        return "modeling"
    elif current == "modeling":
        return "reasoning"
    elif current == "reasoning":
        return "decision"
    elif current == "decision":
        return "report"
    elif current == "report":
        return END
    else:
        return END


# 创建智能体工作流图
def create_research_agent_workflow() -> StateGraph:
    """创建深思熟虑型研究智能体工作流图"""

    # 创建状态图
    workflow = StateGraph(ResearchAgentState)

    # 添加节点
    workflow.add_node("perception", perception)
    workflow.add_node("modeling", modeling)
    workflow.add_node("reasoning", reasoning)
    workflow.add_node("decision", decision)
    workflow.add_node("report", report_generation)

    # 设置入口点
    workflow.set_entry_point("perception")

    # 设置边和转换条件
    workflow.add_edge("perception", "modeling")
    workflow.add_edge("modeling", "reasoning")
    workflow.add_edge("reasoning", "decision")
    workflow.add_edge("decision", "report")
    workflow.add_edge("report", END)

    # 编译工作流
    return workflow.compile()


# 测试函数
def run_research_agent(topic: str, industry: str, horizon: str) -> Dict[str, Any]:
    """运行研究智能体并返回结果"""

    # 创建工作流
    agent = create_research_agent_workflow()

    # 准备初始状态
    initial_state = {
        "research_topic": topic,
        "industry_focus": industry,
        "time_horizon": horizon,
        "perception_data": None,
        "world_model": None,
        "reasoning_plans": None,
        "selected_plan": None,
        "final_report": None,
        "current_phase": "perception",
        "error": None,
    }
    print("LangGraph Mermaid流程图：")
    print(agent.get_graph().draw_mermaid())

    # 运行智能体
    result = agent.invoke(initial_state)

    return result


# 主函数
if __name__ == "__main__":
    print("=== 深思熟虑智能体 - 智能投研助手 ===\n")

    # 用户输入
    topic = input("请输入研究主题 (例如: 新能源汽车行业投资机会): ")
    industry = input("请输入行业焦点 (例如: 电动汽车制造、电池技术): ")
    horizon = input("请输入时间范围 [短期/中期/长期]: ")

    print("\n智能投研助手开始工作...\n")

    try:
        # 运行智能体
        result = run_research_agent(topic, industry, horizon)

        # 处理结果
        if result.get("error"):
            print(f"\n发生错误: {result['error']}")
        else:
            print("\n=== 最终研究报告 ===\n")
            print(result.get("final_report", "未生成报告"))

            # 保存报告
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{timestamp}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(result.get("final_report", "未生成报告"))

            print(f"\n报告已保存为: {filename}")

    except Exception as e:
        print(f"\n运行过程中发生错误: {str(e)}")
