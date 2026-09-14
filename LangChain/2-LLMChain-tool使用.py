# 使用 LangChain 的 LLMChain 和 SerpAPI 工具，实现一个简单的网页搜索 agent
# 现在的LangChain 和之前的写法有所不同了，原来LangChain里是自带SerpAPI工具的，现在需要自己安装
# 包括调用方式也有所调整了
# 这是2026.09.14的写法，可能会有所变化，仅供参考

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from serpapi_search_tools import web_search
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

# 2. 加载 SerpAPI 网页搜索工具（官方包 serpapi-search-tools，读取环境变量 SERPAPI_API_KEY）
tools = [web_search(provider="langchain", api_key=os.getenv("SERPAPI_API_KEY"))]

# 3. 创建 Agent
agent = create_agent(llm, tools)
result = agent.invoke({"messages": [("user", "十月一日是什么节日")]})
print(result["messages"][-1].content)
