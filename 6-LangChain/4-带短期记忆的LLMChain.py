# 这里是带短期记忆的Demo
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
import os
import sys

# Windows 控制台默认 GBK，模型输出里的特殊字符会把 print 打崩
sys.stdout.reconfigure(encoding="utf-8")

# 通过 OpenAI 兼容接口调用百炼模型
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
)

# 创建带历史记录的 prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一位乐于助人的助手。"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# 创建 chain
chain = prompt | llm

# 存储会话历史
store = {}


def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


# 创建带记忆的对话链
conversation = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "default"}}


def invoke_llm(input: str):
    print("-" * 100)
    print("用户输入：", input)
    # 打印历史记录
    # history = get_session_history(config["configurable"]["session_id"]).messages
    # print(
    #     "历史记录：",
    #     json.dumps(
    #         [item.model_dump(mode="json") for item in history],
    #         ensure_ascii=False,
    #         separators=(",", ":"),
    #     ),
    # )
    output = conversation.invoke({"input": input}, config=config)
    print("LLM回答：", output.content)


# 第一轮对话
invoke_llm("你好! 我叫陈永达")
# 第二轮对话 (会记住上一轮)
invoke_llm("我过得不错！正在和一个人工智能聊天。")
# 第三轮对话 (会记住上一轮)
invoke_llm("你知道我叫什么名字吗？")
