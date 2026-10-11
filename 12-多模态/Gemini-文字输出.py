from google import genai
from google.genai import types
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
if not GEMINI_API_KEY:
    raise ValueError("请设置环境变量 GEMINI_API_KEY")


# 文字输出
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="用中文解释AI大模型是如何工作的",
)

print(response.text)
