# -*- coding: utf-8 -*-
"""
读取酒店信息csv文件，并获取酒店描述中n-gram特征中的TopK个
输入：
    - csv文件路径
    - n-gram特征中的n
    - TopK个
输出：
    - 酒店描述中n-gram特征中的TopK个
    - 酒店描述中n-gram特征中的TopK个的词频
    - 酒店描述中n-gram特征中的TopK个的词频的柱状图
"""
import os
import sys
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

# Windows 控制台默认 GBK，酒店描述里的 latin-1 字符会打印失败
sys.stdout.reconfigure(encoding="utf-8")

# 创建英文停用词列表
# fmt: off
ENGLISH_STOPWORDS = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "you're", "you've", "you'll", "you'd", "your", "yours", 
"yourself", "yourselves", "he", "him", "his", "himself", "she", "she's", "her", "hers", "herself", "it", "it's", "its", "itself", "they", "them", 
"their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "that'll", "these", "those", "am", "is", "are", "was", "were", "be", 
"been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", 
"while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", 
"up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
 "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", 
 "will", "just", "don", "don't", "should", "should've", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "aren't", "couldn", "couldn't", 
 "didn",  "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn", "hasn't", "haven", "haven't", "isn", "isn't", "ma", "mightn", "mightn't", "mustn", 
 "mustn't",   "needn", "needn't", "shan", "shan't", "shouldn", "shouldn't", "wasn", "wasn't", "weren", "weren't", "won", "won't", "wouldn", "wouldn't"}
# fmt: on


# 得到酒店描述中n-gram特征中的TopK个
def get_top_n_words(corpus, n=1, k=None):
    # 统计ngram词频矩阵，使用自定义停用词列表
    vec = CountVectorizer(ngram_range=(n, n), stop_words=list(ENGLISH_STOPWORDS)).fit(
        corpus
    )
    bag_of_words = vec.transform(corpus)
    """
    print("feature names:")
    print(vec.get_feature_names_out())
    print("bag of words:")
    print(bag_of_words.toarray())
    """
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    # 按照词频从大到小排序
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:k]


if __name__ == "__main__":

    pd.options.display.max_columns = 30

    # 支持中文
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 用来正常显示中文标签

    # 按脚本所在目录读 CSV，避免从仓库根目录启动时找不到文件
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(_BASE_DIR, "Seattle_Hotels.csv"), encoding="latin-1")

    # 获取酒店描述中n-gram特征中的TopK个
    common_words = get_top_n_words(df["desc"], n=3, k=20)
    print(common_words)

    df1 = pd.DataFrame(common_words, columns=["desc", "count"])
    df1.groupby("desc").sum()["count"].sort_values().plot(
        kind="barh", title="去掉停用词后，酒店描述中的Top20单词"
    )
    plt.show()
