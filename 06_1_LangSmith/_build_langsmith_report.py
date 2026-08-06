#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""组装 LangSmith 讲解 HTML：复用既有讲解页的 head/CSS/Mermaid 能力。"""

from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT.parent / "05_LangGraph" / "混合式_讲解.html"
OUT = ROOT / "1-hybrid_wealth_advisor_langsmith_讲解.html"
RESULTS = ROOT / "step_demo_results.json"

EXTRA_CSS = """
    .run-step.err { border-left-color: var(--warn); }
    .run-step.ok { border-left-color: #2a7a5a; }
    .ls-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; margin: 1.1rem 0; }
    .ls-card { background: var(--card); border: 1px solid var(--line); padding: 1rem; border-top: 3px solid var(--accent); }
    .ls-card h4 { font-family: "IBM Plex Mono", monospace; font-size: 0.9rem; color: var(--accent); margin-bottom: 0.4rem; }
    .ls-card p { font-size: 0.86rem; color: var(--ink-muted); margin: 0; }
    .step-log {
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      background: var(--code-bg);
      color: var(--code-fg);
      padding: 0.85rem 1rem;
      margin-top: 0.6rem;
      white-space: pre-wrap;
      border-left: 3px solid #5a9aaa;
    }
"""


def load_head() -> str:
    src = TEMPLATE.read_text(encoding="utf-8")
    end = src.find("</head>")
    head = src[: end + len("</head>")]
    head = head.replace("混合式智能体 · 代码讲解", "LangSmith 混合财富顾问 · 代码讲解")
    head = head.replace("  </style>\n</head>", EXTRA_CSS + "  </style>\n</head>")
    return head


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_steps_section(payload: dict) -> str:
    parts = [
        '<section id="runs">',
        "<h2>10. 实测 Step 运行记录</h2>",
        f'<p class="muted">数据来自 <code>1-step_demo_langsmith.py</code>，生成时间 {esc(payload.get("generated_at", ""))}。'
        "控制台会按 Step 打印；此处同步落盘到 <code>step_demo_results.json</code>。</p>",
    ]
    for case in payload.get("results", []):
        mode = case.get("processing_mode") or "未知"
        err = case.get("error")
        status = "失败" if err else "成功"
        parts.append(f"<h3>用例：{esc(case.get('case_name', ''))}（{status}）</h3>")
        parts.append("<ul>")
        parts.append(f"<li>查询：{esc(case.get('user_query', ''))}</li>")
        parts.append(f"<li>客户：{esc(str(case.get('customer_id', '')))}</li>")
        parts.append(f"<li>模式：<code>{esc(str(mode))}</code> / 类型：<code>{esc(str(case.get('query_type')))}</code></li>")
        elapsed = case.get("elapsed_seconds")
        if elapsed is not None:
            parts.append(f"<li>耗时：{elapsed:.2f}s</li>")
        parts.append(
            f"<li>LangSmith：{'已启用' if case.get('langsmith_enabled') else '未启用'}，"
            f"项目 <code>{esc(str(case.get('langsmith_project')))}</code></li>"
        )
        parts.append("</ul>")

        for step in case.get("steps", []):
            css = "run-step err" if step.get("error") else "run-step ok"
            preview = step.get("final_response_preview") or ""
            err_text = step.get("error") or ""
            log_lines = [
                f"node={step.get('node')}",
                f"query_type={step.get('query_type')}",
                f"processing_mode={step.get('processing_mode')}",
                f"current_phase={step.get('current_phase')}",
            ]
            if preview:
                log_lines.append(f"final_response={preview}")
            if err_text:
                # 错误信息可能很长，截断展示
                short = err_text if len(err_text) < 500 else err_text[:500] + "..."
                log_lines.append(f"error={short}")
            parts.append(f'<div class="{css}">')
            parts.append('<div class="run-step-head">')
            parts.append(f'<span class="run-step-badge">Step {step.get("step")}</span>')
            parts.append(f'<span class="run-step-node">{esc(str(step.get("node")))}</span>')
            parts.append("</div>")
            parts.append(f'<div class="step-log">{esc(chr(10).join(log_lines))}</div>')
            parts.append("</div>")

        if case.get("final_response"):
            parts.append('<div class="callout">')
            parts.append(f"<strong>最终响应：</strong>{esc(str(case['final_response'])[:800])}")
            parts.append("</div>")

        if err and "Invalid json" in str(err):
            parts.append(
                '<div class="callout warn">'
                "<strong>根因分析：</strong>深思熟虑路径在 <code>collect_data</code> 使用 "
                "<code>JsonOutputParser</code>。本次 LLM 输出中出现未加引号的非法 token"
                "（如 <code>128.5_tco2e_million_revenue</code>），导致 JSON 解析失败，"
                "后续 analyze / recommend 因缺少 market_data 连锁失败。"
                "消除方式：约束提示词要求纯 JSON、数值字段必须是 number/string 合法字面量，"
                "或改用带 schema 的结构化输出，而不是给解析器加兜底。"
                "</div>"
            )
    parts.append("</section>")
    return "\n".join(parts)


BODY = r"""
<body>
  <div class="page">
    <header class="hero">
      <h1 class="brand">LangSmith 混合财富顾问</h1>
      <p class="lede">
        讲解 <code>1-hybrid_wealth_advisor_langgraph_langsmith.py</code>：
        三层混合架构如何分流，以及 <strong>LangSmith</strong> 如何通过环境变量 +
        <code>RunnableConfig</code> 自动追踪每次 Agent 运行。
      </p>
      <div class="meta">
        <span>LangGraph</span>
        <span>LangSmith Tracing</span>
        <span>Tongyi / qwen-flash</span>
        <span>Hybrid Agent</span>
      </div>
    </header>

    <nav class="toc">
      <h2>目录</h2>
      <ol>
        <li><a href="#overview">整体架构</a></li>
        <li><a href="#langsmith">LangSmith 重点</a></li>
        <li><a href="#flow">工作流总图</a></li>
        <li><a href="#catalog">方法一览</a></li>
        <li><a href="#bootstrap">配置与提示词</a></li>
        <li><a href="#models">数据结构</a></li>
        <li><a href="#nodes">节点方法详解</a></li>
        <li><a href="#routing">路由与装配</a></li>
        <li><a href="#entry">入口 run_wealth_advisor</a></li>
        <li><a href="#runs">实测 Step 记录</a></li>
        <li><a href="#howto">如何复现</a></li>
      </ol>
    </nav>

    <section id="overview">
      <h2>1. 整体架构</h2>
      <p>
        本文件在 LangGraph 混合智能体上叠加 LangSmith 可观测性。业务上仍是三层：
        反应式快答、协调层分流、深思熟虑多步规划；工程上通过环境变量打开追踪，
        并在 <code>invoke</code> 时传入 tags / metadata / run_name。
      </p>
      <div class="layer-grid">
        <div class="layer-card">
          <div class="num">L1 · Reactive</div>
          <h4>反应式</h4>
          <p>assess 判定后进入 reactive：可选调用上证指数工具，快速生成 final_response。</p>
        </div>
        <div class="layer-card">
          <div class="num">L2 · Coordinator</div>
          <h4>协调层</h4>
          <p>assess_query 产出 query_type + processing_mode，条件边决定下一节点。</p>
        </div>
        <div class="layer-card delib">
          <div class="num">L3 · Deliberative</div>
          <h4>深思熟虑</h4>
          <p>collect_data → analyze → recommend → respond，多步 LLM 链完成投顾建议。</p>
        </div>
      </div>

      <div class="diagram">
        <pre class="mermaid">
flowchart TB
  U[用户查询] --> A[assess_query]
  A -->|reactive| R[reactive_processing]
  A -->|deliberative| C[collect_data]
  C --> AN[analyze_data]
  AN --> REC[generate_recommendations]
  R --> RSP[respond]
  REC --> RSP
  RSP --> ENDNODE[END]
  LS[(LangSmith Trace)] -.-> A
  LS -.-> R
  LS -.-> C
  LS -.-> AN
  LS -.-> REC
        </pre>
        <p class="caption">图 1 · 混合架构与 LangSmith 旁路追踪（点击「查看源代码」可看 Mermaid 原文）</p>
      </div>
    </section>

    <section id="langsmith">
      <h2>2. LangSmith 重点讲解</h2>
      <p>
        LangSmith 不改业务图结构：开启后，LangChain / LangGraph 的 Runnable
        （含 LLM chain、整张编译图）会自动上报 run tree。本文件做了三件事：
        检测开关、打标签元数据、在主程序提示查看地址。
      </p>

      <div class="ls-grid">
        <div class="ls-card">
          <h4>1. 环境变量开关</h4>
          <p><code>LANGCHAIN_TRACING_V2=true</code> 打开追踪；<code>LANGSMITH_API_KEY</code> 鉴权；
          <code>LANGCHAIN_PROJECT</code> 指定项目桶。</p>
        </div>
        <div class="ls-card">
          <h4>2. 代码侧探测</h4>
          <p><code>LANGSMITH_ENABLED</code> 读取 tracing 开关；未开启时仍可本地跑 Agent。</p>
        </div>
        <div class="ls-card">
          <h4>3. RunnableConfig</h4>
          <p>在 <code>agent.invoke(..., config=)</code> 注入 tags / metadata / run_name，便于过滤与检索。</p>
        </div>
        <div class="ls-card">
          <h4>4. 自动嵌套 Trace</h4>
          <p>每个节点内的 <code>prompt | llm | parser</code> 都会作为子 span 出现在同一条 Trace。</p>
        </div>
      </div>

      <h3>2.1 环境变量与探测代码</h3>
      <div class="code-block">
        <div class="code-label">1-hybrid_wealth_advisor_langgraph_langsmith.py · L60–72</div>
<pre><code># =============================== LangSmith 配置 =================================
LANGSMITH_ENABLED = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
LANGSMITH_PROJECT = os.getenv("LANGCHAIN_PROJECT", "wealth-advisor-hybrid-agent")
print("LANGSMITH_ENABLED=", LANGSMITH_ENABLED)
</code></pre>
      </div>
      <div class="callout">
        <strong>Windows PowerShell 示例：</strong>
        <code>$env:LANGSMITH_API_KEY="..."</code>；
        <code>$env:LANGCHAIN_TRACING_V2="true"</code>；
        <code>$env:LANGCHAIN_PROJECT="wealth-advisor-hybrid-agent"</code>。
        注意：若项目名被写成带引号的字面量（如 <code>"wealth-advisor-hybrid-agent"</code>），
        LangSmith 会把引号也当成项目名的一部分。
      </div>

      <h3>2.2 注入 RunnableConfig（核心）</h3>
      <p>
        仅当 <code>LANGSMITH_ENABLED</code> 为真时构造 config；否则走无 config 的 invoke。
        tags 用于过滤（客户、风险偏好），metadata 存结构化字段，run_name 让控制台列表可读。
      </p>
      <div class="code-block">
        <div class="code-label">run_wealth_advisor · LangSmith config</div>
<pre><code>if LANGSMITH_ENABLED:
    config = RunnableConfig(
        tags=[
            "wealth-advisor", "hybrid-agent",
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
        },
        run_name=f"wealth-advisor-{customer_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    )
result = agent.invoke(initial_state, config=config)  # 或无 config
</code></pre>
      </div>

      <div class="diagram">
        <pre class="mermaid">
sequenceDiagram
  participant App as run_wealth_advisor
  participant Graph as Compiled StateGraph
  participant LLM as Tongyi LLM
  participant LS as LangSmith API

  App->>App: 读取 LANGCHAIN_TRACING_V2
  alt tracing=true
    App->>Graph: invoke(state, RunnableConfig)
    Graph->>LS: 创建 root run + tags/metadata
    Graph->>LLM: 各节点 chain.invoke
    LLM-->>LS: 子 span（prompt/输出/耗时）
    Graph-->>LS: 节点完成事件
  else tracing=false
    App->>Graph: invoke(state)
    Note over LS: 不上报
  end
  Graph-->>App: 最终 WealthAdvisorState
        </pre>
        <p class="caption">图 2 · LangSmith 追踪时序</p>
      </div>

      <h3>2.3 在 LangSmith UI 能看到什么</h3>
      <table>
        <thead><tr><th>维度</th><th>本项目写入内容</th><th>用途</th></tr></thead>
        <tbody>
          <tr><td>Project</td><td><code>LANGCHAIN_PROJECT</code></td><td>按实验/课程隔离</td></tr>
          <tr><td>Run name</td><td><code>wealth-advisor-customer1-时间戳</code></td><td>人工扫一眼定位</td></tr>
          <tr><td>Tags</td><td>wealth-advisor / hybrid-agent / customer-* / 风险偏好</td><td>过滤、对比</td></tr>
          <tr><td>Metadata</td><td>客户、持仓、查询摘要、timestamp</td><td>排障关联业务上下文</td></tr>
          <tr><td>Spans</td><td>assess / reactive / collect_data / analyze / recommend</td><td>看哪步慢、哪步解析失败</td></tr>
        </tbody>
      </table>
    </section>

    <section id="flow">
      <h2>3. 工作流总图</h2>
      <p>与 <code>create_wealth_advisor_workflow</code> 中节点与边一一对应。</p>
      <div class="diagram">
        <pre class="mermaid">
flowchart LR
  subgraph entry [入口]
    AS[assess]
  end
  subgraph reactivePath [反应式]
    RX[reactive]
  end
  subgraph delibPath [深思熟虑]
    CD[collect_data]
    AZ[analyze]
    RC[recommend]
  end
  subgraph exit [汇合]
    RP[respond]
    ED[END]
  end
  AS -->|processing_mode=reactive| RX
  AS -->|processing_mode=deliberative| CD
  RX --> RP
  CD --> AZ --> RC --> RP --> ED
        </pre>
        <p class="caption">图 3 · StateGraph 节点与条件边</p>
      </div>
    </section>

    <section id="catalog">
      <h2>4. 方法一览</h2>
      <table>
        <thead><tr><th>符号</th><th>角色</th><th>LangSmith 相关</th></tr></thead>
        <tbody>
          <tr><td><code>_load_prompts</code></td><td>读 prompts/投顾助手+langsmith_prompts.yaml</td><td>否</td></tr>
          <tr><td><code>query_shanghai_index</code></td><td>模拟行情工具</td><td>作为工具调用出现在 reactive span</td></tr>
          <tr><td><code>assess_query</code></td><td>协调节点</td><td>含 JsonOutputParser LLM 子 span</td></tr>
          <tr><td><code>reactive_processing</code></td><td>反应式节点</td><td>1~2 次 LLM + 可选工具</td></tr>
          <tr><td><code>collect_data</code></td><td>收集节点</td><td>JSON 解析失败会在此 span 暴露</td></tr>
          <tr><td><code>analyze_data</code></td><td>分析节点</td><td>依赖 market_data</td></tr>
          <tr><td><code>generate_recommendations</code></td><td>建议节点</td><td>自然语言最终稿</td></tr>
          <tr><td><code>create_wealth_advisor_workflow</code></td><td>图工厂</td><td>compile 后整图可追踪</td></tr>
          <tr><td><code>run_wealth_advisor</code></td><td>业务入口</td><td>构造 RunnableConfig 并 invoke</td></tr>
        </tbody>
      </table>
    </section>

    <section id="bootstrap">
      <h2>5. 配置与提示词</h2>
      <div class="method-card">
        <h4>_load_prompts / 提示词常量</h4>
        <div class="sig">def _load_prompts() -&gt; Dict[str, str]</div>
        <div class="method-meta">
          <div class="k">功能</div>
          <div>从 <code>prompts/投顾助手+langsmith_prompts.yaml</code> 加载 ASSESSMENT / REACTIVE / DATA_COLLECTION / ANALYSIS / RECOMMENDATION / REACTIVE_AGENT / REACTIVE_FINAL。</div>
          <div class="k">LLM</div>
          <div><code>Tongyi(model_name="qwen-flash")</code>，密钥 <code>DASHSCOPE_API_KEY</code>。</div>
        </div>
      </div>
      <div class="code-block">
        <div class="code-label">兼容补丁 · 导入前设置 langchain 属性</div>
<pre><code>import langchain
if not hasattr(langchain, "verbose"):
    langchain.verbose = False
# debug / llm_cache 同理，避免 1.1.x 属性缺失
</code></pre>
      </div>
    </section>

    <section id="models">
      <h2>6. 数据结构</h2>
      <div class="method-card">
        <h4>WealthAdvisorState</h4>
        <div class="sig">TypedDict · StateGraph 共享状态</div>
        <div class="method-meta">
          <div class="k">输入</div>
          <div><code>user_query</code>、<code>customer_profile</code></div>
          <div class="k">分流</div>
          <div><code>query_type</code>、<code>processing_mode</code></div>
          <div class="k">深思熟虑</div>
          <div><code>market_data</code>、<code>analysis_results</code></div>
          <div class="k">输出</div>
          <div><code>final_response</code>、<code>error</code>、<code>current_phase</code></div>
        </div>
      </div>
      <p class="muted">
        <code>CustomerProfile</code> / <code>EmergencyResponseOutput</code> / <code>InvestmentAnalysisOutput</code>
        用 Pydantic 描述契约；运行时示例客户是普通 dict，未强制校验。
      </p>
    </section>

    <section id="nodes">
      <h2>7. 节点方法详解</h2>

      <div class="method-card">
        <h4>assess_query</h4>
        <div class="sig">assess 节点 · prompt | llm | JsonOutputParser</div>
        <p>根据用户问题输出 query_type（emergency/informational/analytical）与 processing_mode（reactive/deliberative）。非法枚举时回落到 reactive / emergency。</p>
      </div>

      <div class="method-card">
        <h4>reactive_processing</h4>
        <div class="sig">reactive 节点 · 工具标记协议</div>
        <p>
          先用 <code>REACTIVE_AGENT_PROMPT</code> 判断是否包含
          <code>[CALL_TOOL:上证指数查询]</code>；需要则调用 <code>query_shanghai_index</code>，
          再用 <code>REACTIVE_FINAL_PROMPT</code> 生成最终回答。这是字符串协议工具调用，不是 bind_tools。
        </p>
      </div>

      <div class="diagram">
        <pre class="mermaid">
flowchart TD
  Q[用户问题] --> L1[REACTIVE_AGENT_PROMPT + LLM]
  L1 -->|含 CALL_TOOL| T[query_shanghai_index]
  T --> L2[REACTIVE_FINAL_PROMPT + LLM]
  L1 -->|不含| A[直接作为回答]
  L2 --> F[final_response]
  A --> F
        </pre>
        <p class="caption">图 4 · 反应式工具调用协议</p>
      </div>

      <div class="method-card">
        <h4>collect_data / analyze_data / generate_recommendations</h4>
        <div class="sig">深思熟虑三段 · JSON → JSON → 文本</div>
        <div class="method-meta">
          <div class="k">collect</div>
          <div>产出 market_data（模拟 collected_data）</div>
          <div class="k">analyze</div>
          <div>缺 market_data 则报错并回指 collect_data 阶段</div>
          <div class="k">recommend</div>
          <div>StrOutputParser，生成可直接给客户看的建议</div>
        </div>
      </div>

      <div class="method-card">
        <h4>respond_function</h4>
        <div class="sig">respond 节点 · 汇合出口</div>
        <p>若仍无 final_response，填入默认错误文案。两条路径都边连到此节点后 END。</p>
      </div>
    </section>

    <section id="routing">
      <h2>8. 路由与装配</h2>
      <div class="code-block">
        <div class="code-label">create_wealth_advisor_workflow</div>
<pre><code>workflow = StateGraph(WealthAdvisorState)
workflow.add_node("assess", assess_query)
workflow.add_node("reactive", reactive_processing)
workflow.add_node("collect_data", collect_data)
workflow.add_node("analyze", analyze_data)
workflow.add_node("recommend", generate_recommendations)
workflow.add_node("respond", respond_function)
workflow.set_entry_point("assess")
workflow.add_conditional_edges(
    "assess",
    lambda x: "reactive" if x.get("processing_mode") == "reactive" else "collect_data",
    {"reactive": "reactive", "collect_data": "collect_data"},
)
# reactive→respond；collect_data→analyze→recommend→respond→END
return workflow.compile()
</code></pre>
      </div>
    </section>

    <section id="entry">
      <h2>9. 入口 run_wealth_advisor</h2>
      <ol>
        <li>compile 工作流，取出示例客户画像。</li>
        <li>打印 Mermaid（<code>agent.get_graph().draw_mermaid()</code>）。</li>
        <li>按开关组装 LangSmith <code>RunnableConfig</code>。</li>
        <li><code>invoke</code> 得到完整状态 dict。</li>
      </ol>
      <div class="callout">
        交互主程序在 <code>if __name__ == "__main__"</code>：展示 LangSmith 状态、示例查询菜单、客户选择，
        最后打印处理模式、最终响应与耗时。
      </div>
      <p>
        非交互分步演示请运行同目录 <code>1-step_demo_langsmith.py</code>：
        使用 <code>agent.stream</code>，每完成一个节点打印 <code>Step N</code>。
      </p>
    </section>

"""

FOOTER = """
    <section id="howto">
      <h2>11. 如何复现</h2>
      <ol>
        <li>安装依赖：<code>pip install -r requirements.txt</code></li>
        <li>设置 <code>DASHSCOPE_API_KEY</code>、<code>LANGSMITH_API_KEY</code>、
            <code>LANGCHAIN_TRACING_V2=true</code>、<code>LANGCHAIN_PROJECT</code></li>
        <li>分步演示：<code>python 1-step_demo_langsmith.py</code></li>
        <li>交互主程序：<code>python 1-hybrid_wealth_advisor_langgraph_langsmith.py</code></li>
        <li>打开 <a href="https://smith.langchain.com" target="_blank" rel="noopener">smith.langchain.com</a> 查看 Trace</li>
      </ol>
    </section>

    <footer>
      源码：<code>1-hybrid_wealth_advisor_langgraph_langsmith.py</code> ·
      分步脚本：<code>1-step_demo_langsmith.py</code> ·
      流程图可点「查看源代码」展开 Mermaid 原文。
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    import json

    head = load_head()
    results = {"generated_at": "", "results": []}
    if RESULTS.exists():
        results = json.loads(RESULTS.read_text(encoding="utf-8"))
    body = BODY + "\n" + render_steps_section(results) + "\n" + FOOTER
    OUT.write_text(head + "\n" + body, encoding="utf-8")
    print(f"已写入: {OUT}")


if __name__ == "__main__":
    main()
