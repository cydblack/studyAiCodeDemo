import os
from agently import Agently


"""
纯起一个LLM模型，没有加入任何记忆的情况
"""


def configure_model() -> None:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
    Agently.set_settings(
        "OpenAICompatible",
        {
            "base_url": os.getenv(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "model": "deepseek-v4-flash",
        },
    )


configure_model()

# 创建一个LLM，没有任何记忆功能，纯请求LLM
llm = Agently.create_agent()

# 第一次请求
result = llm.input("帮我记一下，我今天要去超市买三个鸡蛋").start()
print("轮次1：", result)

print("------------------------------------------------")

# 第二次请求
result = llm.input("我刚才说了什么？").start()
print("轮次2：", result)
