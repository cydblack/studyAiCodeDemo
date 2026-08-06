# deepeval_wealth_advisor.py 讲解

用 **DeepEval** 对投顾 AI 助手做自动化质量评估：先跑 Agent 拿到真实回答，再交给多个 LLM 评审指标打分。

---

## 1. 使用的工具与依赖

| 工具 / 库 | 作用 |
|---|---|
| **DeepEval** | 评估框架：组装 `LLMTestCase`，用 `evaluate` / `assert_test` 跑指标 |
| **AnswerRelevancyMetric** | 答案是否切题（阈值 0.6） |
| **HallucinationMetric** | 是否相对给定上下文产生幻觉（阈值 0.5） |
| **GEval** | 自定义准则：是否考虑客户风险偏好（阈值 0.5） |
| **OpenAI（gpt-4o-mini）** | DeepEval 指标背后的评审模型，需 `OPENAI_API_KEY` |
| **投顾助手模块** | 被测系统；经 `importlib` 加载后调用 `run_wealth_advisor` |
| **通义千问** | 投顾助手内部 LLM，需 `DASHSCOPE_API_KEY` |

依赖文件（脚本期望同目录存在）：

```
1-hybrid_wealth_advisor_langgraph_langsmith.py
```

其中导出 `run_wealth_advisor`、`SAMPLE_CUSTOMER_PROFILES`。本目录若只有 `1-助手+LangSmith.py`，需自行对齐文件名或调整加载路径。

---

## 2. 整体实现逻辑

脚本分两阶段：

1. **采集阶段**：遍历预置用例 → 调用投顾助手 → 收集 `final_response` → 拼出 `LLMTestCase`
2. **评估阶段**：用 3 个指标对全部用例批量打分并打印结果

另外提供两个 **Pytest / `deepeval test run` 风格** 单测函数，走 `assert_test` 断言路径。

```mermaid
flowchart TB
    subgraph Entry["入口"]
        MAIN["if __name__ == '__main__'"]
        ENV["检查 OPENAI_API_KEY<br/>与 DASHSCOPE_API_KEY"]
        MAIN --> ENV
        ENV -->|通过| RUN["run_evaluation()"]
    end

    subgraph Collect["采集阶段"]
        MERGE["合并 REACTIVE + DELIBERATIVE 用例"]
        LOOP["遍历每个 test_data"]
        AGENT["run_agent_and_get_response()"]
        OUT["取 final_response"]
        CTX["拼 retrieval_context<br/>用例 context + 客户画像"]
        TC["create_test_case() → LLMTestCase"]
        MERGE --> LOOP --> AGENT --> OUT --> CTX --> TC
        TC --> LOOP
    end

    subgraph Judge["评估阶段"]
        METRICS["get_metrics()<br/>相关性 / 幻觉 / 风险偏好"]
        EVAL["evaluate(test_cases, metrics)"]
        METRICS --> EVAL
    end

    RUN --> Collect
    Collect --> Judge
```

---

## 3. 调用顺序（主流程）

按执行时间线：

```mermaid
sequenceDiagram
    participant Main as __main__
    participant Eval as run_evaluation
    participant Helper as run_agent_and_get_response
    participant Agent as run_wealth_advisor
    participant Build as create_test_case
    participant Metrics as get_metrics
    participant DE as deepeval.evaluate
    participant OpenAI as gpt-4o-mini

    Main->>Main: 校验环境变量
    Main->>Eval: 启动
    Eval->>Eval: 合并 4 条用例

    loop 每条用例
        Eval->>Helper: query, customer_id
        Helper->>Agent: 跑 LangGraph 投顾流程
        Agent-->>Helper: state（含 final_response）
        Helper-->>Eval: result
        Eval->>Eval: 拼 context + 客户风险/期限
        Eval->>Build: 构造 LLMTestCase
        Build-->>Eval: test_case
    end

    Eval->>Metrics: 创建 3 个指标
    Metrics-->>Eval: metrics
    Eval->>DE: evaluate(test_cases, metrics)
    DE->>OpenAI: 各指标 LLM 评审
    OpenAI-->>DE: score + reason
    DE-->>Eval: results
```

对应代码路径：

1. `__main__` 检查密钥 → `run_evaluation()`
2. `all_test_data = REACTIVE_TEST_CASES + DELIBERATIVE_TEST_CASES`（共 4 条）
3. 对每条：`run_agent_and_get_response` → `run_wealth_advisor`
4. 空响应则跳过；否则组装 `retrieval_context`，`create_test_case`
5. `get_metrics()` 建 3 个指标
6. `evaluate(...)` 批量打分，`print_results=True`

---

## 4. 模块调用关系

```mermaid
flowchart LR
    subgraph This["deepeval_wealth_advisor.py"]
        MAIN2["__main__"]
        RE["run_evaluation"]
        RAG["run_agent_and_get_response"]
        CTC["create_test_case"]
        GM["get_metrics"]
        T1["test_reactive_query"]
        T2["test_deliberative_query"]
    end

    subgraph AgentMod["投顾助手模块"]
        RWA["run_wealth_advisor"]
        SCP["SAMPLE_CUSTOMER_PROFILES"]
    end

    subgraph DeepEvalPkg["deepeval"]
        EV["evaluate"]
        AT["assert_test"]
        LTC["LLMTestCase"]
        ARM["AnswerRelevancyMetric"]
        HM["HallucinationMetric"]
        GE["GEval"]
    end

    MAIN2 --> RE
    RE --> RAG
    RE --> CTC
    RE --> GM
    RE --> EV
    RAG --> RWA
    CTC --> LTC
    RE --> SCP
    GM --> ARM
    GM --> HM
    GM --> GE
    T1 --> RAG
    T1 --> AT
    T2 --> RAG
    T2 --> AT
    AT --> ARM
    AT --> HM
```

动态加载细节（文件名以数字开头，不能普通 `import`）：

```python
spec = importlib.util.spec_from_file_location(
    "hybrid_wealth_advisor_langgraph_langsmith",
    "1-hybrid_wealth_advisor_langgraph_langsmith.py"
)
# ... exec_module 后 from ... import run_wealth_advisor, SAMPLE_CUSTOMER_PROFILES
```

---

## 5. 测试用例与指标

### 5.1 用例分组

| 分组 | 条数 | 意图 | 示例问题 |
|---|---|---|---|
| `REACTIVE_TEST_CASES` | 2 | 反应式：行情 / 概念解释 | 上证指数、ETF |
| `DELIBERATIVE_TEST_CASES` | 2 | 深思熟虑：组合调整 / 退休规划 | 风险偏好配置、退休计划 |

每条用例字段：

- `input`：用户问题
- `customer_id`：映射 `SAMPLE_CUSTOMER_PROFILES`
- `context`：幻觉检测等用的检索上下文
- `expected_keywords`：当前脚本**未参与评分**（仅数据预留）

### 5.2 三个指标

| 指标 | 阈值 | 评审模型 | 看什么 |
|---|---|---|---|
| `AnswerRelevancyMetric` | 0.6 | gpt-4o-mini | 回答是否相关于 `input` |
| `HallucinationMetric` | 0.5 | gpt-4o-mini | `actual_output` 相对 `retrieval_context` 是否编造 |
| `GEval(RiskConsideration)` | 0.5 | gpt-4o-mini | 是否考虑风险承受力与偏好（看 INPUT + ACTUAL_OUTPUT） |

`retrieval_context` 拼装逻辑：

```
用例自带 context
+ 客户风险等级
+ 投资期限
```

---

## 6. 两种运行方式

### 方式 A：脚本主入口（批量评估）

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:DASHSCOPE_API_KEY="sk-..."
python deepeval_wealth_advisor.py
```

走 `run_evaluation()` → `evaluate()`。

### 方式 B：DeepEval / Pytest 单测

```powershell
deepeval test run deepeval_wealth_advisor.py
```

会发现并执行：

- `test_reactive_query`：仅 `AnswerRelevancyMetric`
- `test_deliberative_query`：相关性 + 幻觉

二者都用 `assert_test`，失败即断言失败。

```mermaid
flowchart TB
    A["运行入口"] --> B{"方式"}
    B -->|python 脚本| C["run_evaluation"]
    C --> D["evaluate 批量打分"]
    B -->|deepeval test run| E["test_reactive_query<br/>test_deliberative_query"]
    E --> F["assert_test 断言"]
```

---

## 7. 关键数据流（单条用例）

```mermaid
flowchart LR
    Q["input 用户问题"] --> Agent["run_wealth_advisor"]
    CID["customer_id"] --> Agent
    Agent --> R["final_response"]
    CTX0["test_data.context"] --> RC["retrieval_context"]
    PROF["SAMPLE_CUSTOMER_PROFILES"] --> RC
    Q --> TC["LLMTestCase"]
    R --> TC
    RC --> TC
    TC --> M1["AnswerRelevancy"]
    TC --> M2["Hallucination"]
    TC --> M3["GEval Risk"]
    M1 --> S["分数 + 理由"]
    M2 --> S
    M3 --> S
```

---

## 8. 小结

- **被测对象**：LangGraph 混合投顾助手（`run_wealth_advisor`）
- **评估框架**：DeepEval；评审模型默认 OpenAI `gpt-4o-mini`
- **主路径**：采回答 → 建 `LLMTestCase` → 三指标批量 `evaluate`
- **旁路**：两个 `assert_test` 单测，便于 CI / `deepeval test run`
- **环境**：同时需要 `OPENAI_API_KEY`（评审）与 `DASHSCOPE_API_KEY`（被测 Agent）
