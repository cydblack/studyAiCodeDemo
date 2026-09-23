# -*-coding: utf-8 -*-
# 先运行 word_seg进行中文分词，然后再进行word_similarity计算
# 将Word转换成Vec，然后计算相似度

import os
import multiprocessing
from gensim.models import word2vec


# 如果目录中有多个文件，可以使用PathLineSentences
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
segment_folder = os.path.join(_BASE_DIR, "西游记", "segment")


# 切分之后的句子合集
sentences = word2vec.PathLineSentences(segment_folder)

# 设置模型参数，进行训练
model = word2vec.Word2Vec(sentences, vector_size=100, window=3, min_count=1)
model.save(os.path.join(_BASE_DIR, "models", "xyl_word2Vec_1.model"))

# print(model.wv['孙悟空'])
print(model.wv.similarity("孙悟空", "猪八戒"))
print(model.wv.similarity("孙悟空", "孙行者"))
print(model.wv.similarity("金角", "铁扇公主"))
print(model.wv.most_similar(positive=["孙悟空", "唐僧"], negative=["孙行者"]))

# 设置模型参数，进行训练
model2 = word2vec.Word2Vec(
    sentences,
    vector_size=128,
    window=4,
    min_count=3,
    workers=multiprocessing.cpu_count(),
)
# 保存模型
model.save(os.path.join(_BASE_DIR, "models", "xyl_word2Vec_2.model"))
print("-" * 400)
print(model2.wv.similarity("孙悟空", "猪八戒"))
print(model2.wv.similarity("孙悟空", "孙行者"))
print(model.wv.similarity("金角", "铁扇公主"))
print(model2.wv.most_similar(positive=["孙悟空", "唐僧"], negative=["孙行者"]))
