from PIL import Image
from google import genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# 图像理解。路径按脚本所在目录解析，从仓库根目录启动也能找到
image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "car.jpg")
image = Image.open(image_path)
# 注意：contents 变成了一个列表，里面同时放了图片对象和文字
response = client.models.generate_content(
    model="gemini-3.8-flash", contents=[image, "帮我解释下这张照片"]
)
print(response.text)
