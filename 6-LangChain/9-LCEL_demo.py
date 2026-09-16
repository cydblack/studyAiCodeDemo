import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# stream=True 让LLM支持流式输出
llm = ChatOpenAI(
    model="qwen-turbo",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
)

# 定义三个子任务：翻译->处理->回译
translate_to_en = (
    ChatPromptTemplate.from_template("Translate this to English:{input}")
    | llm
    | StrOutputParser()
)
process_text = (
    ChatPromptTemplate.from_template("Analyze this text:{text}")
    | llm
    | StrOutputParser()
)
translate_to_cn = (
    ChatPromptTemplate.from_template("Translate this to Chinese:{output}")
    | llm
    | StrOutputParser()
)

# 组合成多任务链
workflow = {"text": translate_to_en} | process_text | translate_to_cn

# 一次性打印结果
# workflow.invoke({"input": "北京有哪些好吃的地方，简略回答不超过100字"})
# 使用stream方法，边生成边打印
for chunk in workflow.stream({"input": "北京有哪些好吃的地方，简略回答不超过100字"}):
    print(chunk, end="", flush=True)

print()
