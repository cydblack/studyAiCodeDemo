# LangChain DEMO

按编号从浅到深：先 LCEL 调模型，再 Agent 用工具，再记忆和本地知识。写法以 2026.09 的 LangChain 1.x 为准，可能会有所变化。

模型默认走百炼 OpenAI 兼容接口：`ChatOpenAI` + `deepseek-v4-flash`。依赖见同目录 `requirements.txt`。需要 `DASHSCOPE_API_KEY`；`2`、`3` 还需要 `SERPAPI_API_KEY`。

## 阅读顺序

1. `1-LLMChain-参数传递.py`：Prompt 填变量，直接调模型。
2. `2-LLMChain-tool使用.py`：Agent + 现成搜索工具。
3. `3-LLMChain-调用Fuction.py`：现成工具 + 自己写的 Function。
4. `4-带短期记忆的LLMChain.py`：多轮对话记住上文。
5. `5-本地知识客服.py`：Agent 查本地产品/公司信息。
6. `6-ReAct私募基金问答助手.py`：带 system prompt 的规则库问答。
7. `7-工具链组合形式-由LLM自己选工具.py`：多个本地工具，模型自己选。

## 文件说明


| 文件                        | 功能                                                                          | 作用                             |
| ------------------------- | --------------------------------------------------------------------------- | ------------------------------ |
| `1-LLMChain-参数传递.py`      | `PromptTemplate` 把 `{product}` 填进「给某方向公司起名」，`prompt | llm` 各跑一次「模型玩具」「广告设计」 | 看 LCEL 怎么传参、怎么 `invoke`，还不涉及工具 |
| `2-LLMChain-tool使用.py`    | Agent 挂上 SerpAPI 的 `web_search`，问「十月一日是什么节日」                                | 看 `create_agent` + 现成搜索工具的最小写法 |
| `3-LLMChain-调用Fuction.py` | 搜索工具再加自定义 `calculator`，问北京气温（华氏）再算其 1/4                                     | 看现成工具和 `@tool` 函数怎么拼进同一个 Agent |
| `4-带短期记忆的LLMChain.py`     | `RunnableWithMessageHistory` 同一 `session_id` 连问三轮，第三轮问「我叫什么名字」              | 看短期记忆怎么挂到 chain 上，不经过 Agent    |
| `5-本地知识客服.py`             | 两个 `@tool`：按车型查描述、按问题查公司介绍；命令行循环提问                                          | 看 Agent 在本地字典/固定文案上当客服，不联网     |
| `6-ReAct私募基金问答助手.py`      | 内存规则库 + 关键词/类别/直接问答三个工具；`system_prompt` 约束只答私募；循环对话                         | 看带系统提示的 ReAct：模型先选工具再查规则库      |
| `7-工具链组合形式-由LLM自己选工具.py`  | 五个本地工具（情感分析、JSON/CSV 转换、行数、查找、替换）；三个任务分别测组合调用和「没有对应工具」                      | 看工具链组合：模型按题自己选工具，而不是代码写死调用顺序   |


`6` 仍用 `ChatTongyi`（`qwen-plus`），和 `1–5`、`7` 的 `ChatOpenAI` 不是同一套模型入口。