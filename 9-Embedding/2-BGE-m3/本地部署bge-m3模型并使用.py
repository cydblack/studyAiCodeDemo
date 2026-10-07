#!/usr/bin/env python
# coding: utf-8

# STEP 1.模型下载
from modelscope import snapshot_download

model_dir = snapshot_download("BAAI/bge-m3", cache_dir="D:/models")

# STEP 2.加载模型
# use_fp16 为 True 时用半精度计算，速度更快，精度略有下降
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel("D:/models/BAAI/bge-m3", use_fp16=True)

sentences_1 = ["What is BGE M3?", "Defination of BM25"]
sentences_2 = [
    "BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.",
    "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document",
]

embeddings_1 = model.encode(
    sentences_1,
    batch_size=4,
    max_length=1024,  # 不需要这么长的文本时，把这个值改小可以加快编码
)["dense_vecs"]
print(embeddings_1)

embeddings_2 = model.encode(
    sentences_2,
    batch_size=4,
    max_length=1024,
)["dense_vecs"]
print(embeddings_2)

similarity = embeddings_1 @ embeddings_2.T
print(similarity)
# [
#    [0.6265, 0.3477],
#    [0.3499, 0.678 ]
# ]
