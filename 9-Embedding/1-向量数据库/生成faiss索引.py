# -*-coding: utf-8 -*-
# 用示例文档生成一个最简单的 FAISS 索引
import os
import numpy as np
import faiss
from openai import OpenAI

client = OpenAI(  # 创建百炼客户端
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

documents = [
    {  # 第 1 条：退票政策
        "id": "doc1",  # 文档编号
        "text": "迪士尼乐园的门票一经售出，原则上不予退换。但在特殊情况下，如恶劣天气导致园区关闭，可在官方指引下进行改期或退款。",  # 要转成向量的正文
        "metadata": {
            "source": "official_faq_v1.pdf",
            "category": "退票政策",  # 类别
            "author": "Admin",  # 作者
        },
    },
    {  # 第 2 条：会员权益
        "id": "doc2",  # 文档编号
        "text": "购买“奇妙年卡”的用户，可以享受一年内多次入园的特权，并且在餐饮和购物时有折扣。",  # 要转成向量的正文
        "metadata": {  # 附加信息
            "source": "annual_pass_rules.docx",  # 来源文件
            "category": "会员权益",  # 类别
            "author": "MarketingDept",  # 作者
        },
    },
    {  # 第 3 条：在线购票退票规则
        "id": "doc3",  # 文档编号
        "text": "对于在线购买的迪士尼门票，如果需要退票，必须在票面日期前48小时通过原购买渠道提交申请，并可能收取手续费。",  # 要转成向量的正文
        "metadata": {  # 附加信息
            "source": "online_policy.html",  # 来源文件
            "category": "退票政策",  # 类别
            "author": "E-commerceTeam",  # 作者
        },
    },
    {  # 第 4 条：园区公告
        "id": "doc4",  # 文档编号
        "text": "园区内的“加勒比海盗”项目因年度维护，将于下周暂停开放。",  # 要转成向量的正文
        "metadata": {  # 附加信息
            "source": "maintenance_notice.txt",  # 来源文件
            "category": "园区公告",  # 类别
            "author": "OpsDept",  # 作者
        },
    },
]

vectors = []
for doc in documents:
    completion = client.embeddings.create(
        model="text-embedding-v4",
        input=doc["text"],
        dimensions=1024,
        encoding_format="float",
    )
    vectors.append(completion.data[0].embedding)


# 里面每个数都是 Python 的 float（64 位）。np.array(vectors) 因此得到的是 float64 的二维数组，一行一条文档。
# FAISS 只接受 float32 的二维数组，一行一个向量
# 本机 FAISS 的 index.add 内部会执行 np.ascontiguousarray(x, dtype="float32")，所以直接把 float64 数组传进去也能写入。
# 删掉这句，这个脚本在当前环境里仍然能建索引。
vectors_np = np.array(vectors).astype("float32")

index = faiss.IndexFlatL2(vectors_np.shape[1])
index.add(vectors_np)
print(f"FAISS 索引已创建，共 {index.ntotal} 个向量，维度 {index.d}")
