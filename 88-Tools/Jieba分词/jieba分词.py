# -*-coding: utf-8 -*-
# 对txt文件进行中文分词
import jieba


def segment_lines(text_list, stopwords=[]):
    """
    对字符串列表逐条做中文分词，用空格拼接后返回。
    输入：
        text_list: 待分词的字符串列表
        stopwords: 停用词列表
    返回：
        与输入等长的分词结果列表，每条是空格分隔的词
    """
    result_list = []
    for text in text_list:
        sentence_segment = []
        for word in jieba.cut(text):
            if word not in stopwords:
                sentence_segment.append(word)
        result_list.append(" ".join(sentence_segment))
    return result_list


# 传入字符串列表，逐条分词
STR_DATA = ["今天真是美好的一天", "今天天气不错"]
res = segment_lines(STR_DATA)
print(res)
