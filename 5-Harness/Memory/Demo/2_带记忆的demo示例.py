"""
模拟一段记忆的场景，通过记忆功能，让LLM记住用户之前说过的话，并根据记忆回答用户的问题
"""

import os
from agently import Agently


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
llm = Agently.create_agent()


rules = "我不喜欢长篇大论，但我喜欢你在回复里用emoji如😄🎇等进行回复"
extra_info = "Todo list: [ ]今天要去超市买三个鸡蛋"
memory = ""  # 这里就可以加载记忆了
instruction = "暂无"
query = "刚才我们说了什么？"

chat_history = [
    {"role": "system", "content": rules},
    {"role": "user", "content": "帮我记一下，我今天要去超市买三个鸡蛋"},
    {"role": "assistant", "content": "好的，已经记下了！随时告诉我哦～ 🥚"},
]


result = (
    llm.set_chat_history(chat_history)
    .input(
        f"信息补充：{ extra_info }\n"
        f"重要记忆：{ memory }\n"
        f"本次处理时应该注意：{ instruction }\n"
        f"用户问题：{ query }\n"
    )
    .start()
)

print(result)
