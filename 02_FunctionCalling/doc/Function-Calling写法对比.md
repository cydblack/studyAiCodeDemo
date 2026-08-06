# Function Calling 写法对比

对比文件：

- `门票助手1.py` — 基于**Qwen-Agent 框架** 封装
- `天气-new-tools.py` — 基于**DashScope SDK 原生调用**（新版`tools` 写法）

两者底层都走百炼 / DashScope 的 Function Calling 能力，但抽象层级和代码组织方式不同。

---

## 1. 总体架构


| 维度     | 门票助手1.py                               | 天气-new-tools.py                |
| ---------- | -------------------------------------------- | ---------------------------------- |
| 依赖     | `qwen_agent`（Assistant、BaseTool、WebUI） | 仅`dashscope`                    |
| 调用方式 | `Assistant(...).run(messages)`             | `dashscope.Generation.call(...)` |
| 工具调度 | 框架自动完成                               | 开发者手动编排多轮对话           |
| 适用场景 | 完整 Agent 应用（TUI / WebUI）             | 学习底层流程、轻量脚本           |

---

## 2. 工具定义

### 门票助手1.py：继承 BaseTool + 装饰器注册

```python
@register_tool("exc_sql")
class ExcSQLTool(BaseTool):
    description = "对于生成的SQL，进行SQL查询"
    parameters = [
        {
            "name": "sql_input",
            "type": "string",
            "description": "生成的SQL语句",
            "required": True,
        }
    ]

    def call(self, params: str, **kwargs) -> str:
        args = json.loads(params)
        sql_input = args["sql_input"]
        # ... 执行 SQL，返回字符串结果
```

要点：

- 用`@register_tool("工具名")` 把类注册到 Qwen-Agent 工具池
- `parameters` 是**列表格式**（Qwen-Agent 约定），不是 JSON Schema 的`properties` 对象
- 统一入口是`call(self, params: str)`，参数是**JSON 字符串**，需自行`json.loads`
- 返回值必须是**字符串**

### 天气-new-tools.py：OpenAI 兼容的 tools 数组

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "获取指定地点的天气情况，当问到天气时，调用此函数",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市，如：大连、上海"},
                    "unit": {"type": "string", "enum": ["摄氏度", "华氏度"]},
                },
                "required": ["location"],
            },
        },
    }
]
```

要点：

- 工具描述直接传给 API，格式与 OpenAI`tools` 一致
- `parameters` 使用**JSON Schema**（`type: object` +`properties`）
- 本地执行函数`get_current_weather` 与 API 描述**分离**，需自己维护名称一致

---

## 3. 工具挂载 / 传给模型

### 门票助手1.py

```python
bot = Assistant(
    llm=llm_cfg,
    system_message=system_prompt,
    function_list=["exc_sql"],  # 只传已注册的工具名字符串
)
```

框架根据工具名找到 `ExcSQLTool`，自动转成模型所需的 tools 格式并注入请求。

### 天气-new-tools.py

```python
response = dashscope.Generation.call(
    model="qwen-flash",
    messages=messages,
    tools=tools,              # 完整 tools 数组直接传入
    result_format="message",  # 使用 message 格式时必须设置
)
```

开发者自己构造 `tools` 并传入每次 API 请求。

---

## 4. 对话与工具调用流程

### 门票助手1.py：框架闭环

```python
messages = []
messages.append({"role": "user", "content": query})

for response in bot.run(messages):
    print("bot response:", response)
messages.extend(response)
```

框架内部自动完成：

1. 调用模型
2. 解析`tool_calls`
3. 执行对应`BaseTool.call()`
4. 把工具结果以`role: tool` 写回`messages`
5. 再次调用模型，直到不再触发工具或达到终止条件

开发者 **不需要** 手动判断 `tool_calls`、不需要写第二次 `Generation.call`。

### 天气-new-tools.py：手动两轮（或多轮）

```python
# 第一次：用户提问
response = get_response(messages)
message = response.output.choices[0].message
messages.append(message)

# 判断是否需要调用工具
tool_calls = getattr(message, "tool_calls", None)
if tool_calls:
    for tool_call in tool_calls:
        arguments = json.loads(tool_call["function"]["arguments"])
        tool_response = get_current_weather(**arguments)
        messages.append({
            "role": "tool",
            "content": tool_response,
            "tool_call_id": tool_call["id"],
        })

    # 第二次：把工具结果交给模型总结
    response = get_response(messages)
    message = response.output.choices[0].message
```

开发者需要自行处理：


| 步骤     | 说明                                               |
| ---------- | ---------------------------------------------------- |
| 读响应   | `response.output.choices[0].message`               |
| 判断触发 | `message.tool_calls` 非空                          |
| 解析参数 | `json.loads(tool_call["function"]["arguments"])`   |
| 执行函数 | 按`function.name` 分发到本地函数                   |
| 回传结果 | `role: "tool"` + `tool_call_id` + 字符串 `content` |
| 再次请求 | 带着完整`messages` 发起第二次 API 调用             |

---

## 5. 模型响应结构

### 天气-new-tools.py 可直接观察到的响应

触发工具时：

```json
{
  "finish_reason": "tool_calls",
  "message": {
    "role": "assistant",
    "content": "",
    "tool_calls": [{
      "id": "call_xxx",
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "arguments": "{\"location\": \"常州\", \"unit\": \"摄氏度\"}"
      }
    }]
  }
}
```

不触发工具时，直接走 `message.content` 文本回复。

### 门票助手1.py

同样走 DashScope 新版 `tool_calls` 协议，但被 Qwen-Agent 封装在 `bot.run()` 内部，业务代码不直接接触原始响应 JSON。

---

## 6. System Prompt 与工具描述的分工

### 门票助手1.py

- **System Message**：承载业务上下文（表结构、SKU 规则、SQL 编写约束）
- **Tool description**：只描述工具本身（"对于生成的SQL，进行SQL查询"）
- 分工清晰：领域知识在 system，工具能力在 tool

### 天气-new-tools.py

- 无独立 system message，用户问题直接作为`role: user`
- 工具何时调用完全依赖`function.description` 和模型理解
- 若场景复杂，可额外加`role: system` 消息（当前示例未加）

---

## 7. 参数格式差异（易踩坑）


| 项目            | 门票助手1.py (Qwen-Agent)                             | 天气-new-tools.py (DashScope tools)                                  |
| ----------------- | ------------------------------------------------------- | ---------------------------------------------------------------------- |
| 工具参数 schema | `parameters: [{ name, type, description, required }]` | `parameters: { type: "object", properties: {...}, required: [...] }` |
| 工具执行入参    | `call(params: str)` 整段 JSON 字符串                  | 自行`json.loads(arguments)` 后按字段取值                             |
| 工具注册        | `@register_tool` + 类                                 | 无注册，靠`name` 字符串匹配                                          |
| 挂载方式        | `function_list=["工具名"]`                            | `tools=[{ type, function }]`                                         |
| 结果回传 role   | 框架处理（底层为`tool`）                              | 手动写`role: "tool"`                                                 |
| 关联 ID         | 框架处理                                              | 必须带`tool_call_id`                                                 |

---

## 8. 如何选择

**用 Qwen-Agent（门票助手1 写法）**，当：

- 需要 WebUI / 多轮对话 / 流式输出等 Agent 能力
- 工具较多，不想手写调度循环
- 希望参数 schema 与工具实现绑定在同一类里

**用 DashScope 原生 tools（天气-new-tools 写法）**，当：

- 学习 Function Calling 完整链路
- 项目轻量，不想引入`qwen_agent` 依赖
- 需要精细控制每一轮 API 请求和 messages 结构

---

## 9. 对应关系速查

```
门票助手1                          天气-new-tools
─────────────────────────────────────────────────────────
@register_tool("exc_sql")    →    tools[].function.name
BaseTool.description         →    tools[].function.description
BaseTool.parameters (list) →    tools[].function.parameters (JSON Schema)
ExcSQLTool.call(params)      →    本地函数 + json.loads(arguments)
function_list=["exc_sql"]    →    tools=tools
bot.run(messages)            →    get_response(messages) 循环
（框架自动）                  →    检查 tool_calls、回传 role:tool、二次调用
```
