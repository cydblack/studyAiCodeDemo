#!/usr/bin/env python
# coding: utf-8

import base64
import os
import cv2
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


# 视频理解
# DeepSeek 只支持图片多模态，不能像 Gemini 那样直接上传 mp4。
# 这里采用抽帧的方式，再按图片理解的方式送给模型。
video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car.mp4")
frame_num = 6

cap = cv2.VideoCapture(video_path)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
if total <= 0:
    raise ValueError("无法读取视频帧")

indexes = [int(i * (total - 1) / (frame_num - 1)) for i in range(frame_num)]
content = [
    {
        "type": "text",
        "text": "详细描述视频里发生了什么？如果有对话，请把关键对话提取出来。",
    }
]

print("正在从视频抽帧...")
for idx in indexes:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, frame = cap.read()
    if not ok:
        raise ValueError(f"读取第 {idx} 帧失败")
    ok, buf = cv2.imencode(".jpg", frame)
    if not ok:
        raise ValueError(f"编码第 {idx} 帧失败")
    frame_b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    content.append(
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}"},
        }
    )
cap.release()
print(f"抽帧完成，共 {frame_num} 帧，开始推理...")

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": content}],
)

print(response.choices[0].message.content)
