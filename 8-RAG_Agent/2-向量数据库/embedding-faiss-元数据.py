import os
import numpy as np
import faiss
import pickle
import json
from openai import OpenAI

# FAISS 向量库目录。使用纯英文路径，faiss.write_index 在 Windows 上打不开中文路径
FAISS_DATABASE = r"D:\\vector_db"
dimension = 1024  # 向量维度
k = 3  # 查找最近的3个邻居


def build_faiss_database(documents, client):
    """调用嵌入接口生成向量，并建成带自定义 ID 的 FAISS 索引。"""
    # 每条文档的完整内容：id、正文 text、metadata。下标与 vector_ids 一致，搜索后用 ID 回查
    metadata_store = []
    # 嵌入接口返回的向量，每项是一条文档的 1024 维浮点列表
    vectors_list = []
    # 写入 FAISS 的自定义 ID，这里用文档在列表中的下标 0、1、2...
    vector_ids = []

    print("正在为文档生成向量...")
    for i, doc in enumerate(documents):
        try:
            completion = client.embeddings.create(
                model="text-embedding-v4",
                input=doc["text"],
                dimensions=dimension,
                encoding_format="float",
            )
            vector = completion.data[0].embedding
            vectors_list.append(vector)
            metadata_store.append(doc)
            vector_ids.append(i)
            print(f"  - 已处理文档 {i+1}/{len(documents)}")
        except Exception as e:
            print(f"处理文档 '{doc['id']}' 时出错: {e}")
            continue

    vectors_np = np.array(vectors_list).astype("float32")
    vector_ids_np = np.array(vector_ids)
    index = faiss.IndexIDMap(faiss.IndexFlatL2(dimension))
    index.add_with_ids(vectors_np, vector_ids_np)
    print(f"\nFAISS 索引已成功创建，共包含 {index.ntotal} 个向量。")
    return index, metadata_store


def save_faiss_database(index, metadata_store, save_path):
    """
    保存FAISS索引和元数据到本地文件

    Args:
        index: FAISS索引
        metadata_store: 元数据存储
        save_path: 保存路径
    """
    try:
        # 创建保存目录
        os.makedirs(save_path, exist_ok=True)

        # 保存FAISS索引
        index_path = os.path.join(save_path, "faiss_index.bin")
        faiss.write_index(index, index_path)
        print(f"FAISS索引已保存到: {index_path}")

        # 保存元数据
        metadata_path = os.path.join(save_path, "metadata.pkl")
        with open(metadata_path, "wb") as f:
            pickle.dump(metadata_store, f)
        print(f"元数据已保存到: {metadata_path}")

        # 保存配置信息
        config = {
            "dimension": dimension,
            "total_vectors": index.ntotal,
            "model": "text-embedding-v4",
            "encoding_format": "float",
        }
        config_path = os.path.join(save_path, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"配置信息已保存到: {config_path}")
        print(f"数据库保存完成，所有文件保存到: {save_path}")

    except Exception as e:
        print(f"保存FAISS索引和元数据时发生错误: {e}")
        raise e


def load_faiss_database(load_path):
    """
    加载FAISS索引和元数据

    Args:
        load_path: 加载路径

    Returns:
        tuple: (index, metadata_store, config) 或 (None,None,None)
    """
    try:
        # 加载FAISS索引
        index_path = os.path.join(load_path, "faiss_index.bin")
        metadata_path = os.path.join(load_path, "metadata.pkl")
        config_path = os.path.join(load_path, "config.json")

        if not all(
            [os.path.exists(path) for path in [index_path, metadata_path, config_path]]
        ):
            print(f"数据库文件不完整: {load_path}")
            return None, None, None

        # 加载FAISS索引
        index = faiss.read_index(index_path)
        print(f"FAISS索引已加载: {index_path}")

        # 加载元数据
        with open(metadata_path, "rb") as f:
            metadata_store = pickle.load(f)
        print(f"元数据已加载: {metadata_path}")

        # 加载配置信息
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"配置信息已加载: {config_path}")
        return index, metadata_store, config

    except Exception as e:
        print(f"加载FAISS索引时发生错误: {e}")
        raise e


def main():
    # Step1. 初始化 API 客户端
    try:
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    except Exception as e:
        print("初始化OpenAI客户端失败，请检查环境变量'DASHSCOPE_API_KEY'是否已设置。")
        print(f"错误信息: {e}")
        return

    # Step2. 准备示例文本和元数据
    documents = [
        {
            "id": "doc1",
            "text": "迪士尼乐园的门票一经售出，原则上不予退换。但在特殊情况下，如恶劣天气导致园区关闭，可在官方指引下进行改期或退款。",
            "metadata": {
                "source": "official_faq_v1.pdf",
                "category": "退票政策",
                "author": "Admin",
            },
        },
        {
            "id": "doc2",
            "text": "购买“奇妙年卡”的用户，可以享受一年内多次入园的特权，并且在餐饮和购物时有折扣。",
            "metadata": {
                "source": "annual_pass_rules.docx",
                "category": "会员权益",
                "author": "MarketingDept",
            },
        },
        {
            "id": "doc3",
            "text": "对于在线购买的迪士尼门票，如果需要退票，必须在票面日期前48小时通过原购买渠道提交申请，并可能收取手续费。",
            "metadata": {
                "source": "online_policy.html",
                "category": "退票政策",
                "author": "E-commerceTeam",
            },
        },
        {
            "id": "doc4",
            "text": "园区内的“加勒比海盗”项目因年度维护，将于下周暂停开放。",
            "metadata": {
                "source": "maintenance_notice.txt",
                "category": "园区公告",
                "author": "OpsDept",
            },
        },
    ]

    # Step3. 生成向量和 FAISS 索引
    index, metadata_store = build_faiss_database(documents, client)

    # Step4. 保存到本地
    save_faiss_database(index, metadata_store, FAISS_DATABASE)

     # Step5. 从本地加载，后续查询使用加载结果
    index, metadata_store, config = load_faiss_database(FAISS_DATABASE)
    print(f"已从本地加载向量库，共 {config['total_vectors']} 个向量。")

    # Step6. 执行搜索并检索元数据
    query_text = "我想了解一下迪士尼门票的退款流程"
    print(f"\n正在为查询文本生成向量: '{query_text}'")

    try:
        query_completion = client.embeddings.create(
            model="text-embedding-v4",
            input=query_text,
            dimensions=dimension,
            encoding_format="float",
        )
        query_vector = np.array([query_completion.data[0].embedding]).astype("float32")

        # search 返回距离 D 和 ID I
        distances, retrieved_ids = index.search(query_vector, k)

        print("\n--- 搜索结果 ---")
        for i in range(k):
            doc_id = retrieved_ids[0][i]
            if doc_id == -1:
                print(f"\n排名 {i+1}: 未找到更多结果。")
                continue

            retrieved_doc = metadata_store[doc_id]
            print(f"\n--- 排名 {i+1} (相似度得分/距离: {distances[0][i]:.4f}) ---")
            print(f"ID: {doc_id}")
            print(f"原始文本: {retrieved_doc['text']}")
            print(f"元数据: {retrieved_doc['metadata']}")
    except Exception as e:
        print(f"执行搜索时发生错误: {e}")


if __name__ == "__main__":
    main()
