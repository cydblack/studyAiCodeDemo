from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import sys

# Windows 控制台默认 GBK，模型输出里的特殊字符会把 print 打崩
sys.stdout.reconfigure(encoding="utf-8")

# 通过 OpenAI 兼容接口调用百炼模型（不再使用已停更的 langchain_community.Tongyi）
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
)

# 创建 Prompt Template
prompt = PromptTemplate(
    input_variables=["product"],
    template="给 {product} 方向的公司起名",
)

# 将 prompt、模型和字符串解析器组合成可运行序列
chain = prompt | llm

# 使用 invoke 方法传入输入
result1 = chain.invoke({"product": "模型玩具"})
print(result1.model_dump_json(ensure_ascii=False))
print("-" * 100)
result2 = chain.invoke({"product": "广告设计"})
print(result2.model_dump_json(ensure_ascii=False))
