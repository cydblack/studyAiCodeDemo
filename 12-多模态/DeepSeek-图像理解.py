#!/usr/bin/env python
# coding: utf-8

import dashscope
import base64
import os
import dashscope
from dashscope import MultiModalConversation
from openai import OpenAI

dashscope.base_http_api_url = (
    "https://ws-q8b7jquakv6ldzfd.cn-beijing.maas.aliyuncs.com/api/v1"
)

MODEL = "deepseek-v4.1-flash"
API_KEY = os.getenv("DASHSCOPE_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://ws-q8b7jquakv6ldzfd.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
)

image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car.jpg")
with open(image_path, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
                {"type": "text", "text": "帮我解释下这张照片"},
            ],
        }
    ],
)

print(response.choices[0].message.content)
