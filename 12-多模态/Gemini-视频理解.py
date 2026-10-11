from google import genai
import os
import time

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# 1. 上传视频文件
print("正在上传视频...")
video_file = client.files.upload(file="car.mp4")  # 汽车剐蹭视频
print(f"上传成功: {video_file.name}")

# 2. 等待视频处理 (关键步骤！)
# 视频上传后，Google 需要几秒钟在云端进行转码。
while video_file.state.name == "PROCESSING":
    print("视频处理中，请稍候...")
    time.sleep(2)
    video_file = client.files.get(name=video_file.name)

if video_file.state.name == "FAILED":
    raise ValueError("视频处理失败")

print("视频就绪，开始推理...")

# 3. 多模态推理
# 将上传好的 video_file 对象直接放入 contents 列表
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=[
        video_file,
        "详细描述视频里发生了什么？如果有对话，请把关键对话提取出来。",
    ],
)

print(response.text)
