# -*-coding: utf-8 -*-
# 加载已训练的 Word2Vec 模型，计算词语相似度

import os
from gensim.models import word2vec

BOOK = "西游记"
# BOOK = "三国演义"

# 按脚本所在目录定位模型文件
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(_BASE_DIR, BOOK, "model", "word2Vec_2.model")

model = word2vec.Word2Vec.load(model_path)
print("孙悟空和菩提的相似度：", model.wv.similarity("孙悟空", "菩提"))
print(
    model.wv.most_similar(positive=["唐僧", "孙悟空"], negative=["猪八戒"]),
)

# print(model.wv.similarity("曹操", "刘备"))
# print(model.wv.most_similar(positive=["曹操", "刘备"], negative=["张飞"]))
# print(model.wv.most_similar(positive=["刘备", "关羽"], negative=["张飞"]))
