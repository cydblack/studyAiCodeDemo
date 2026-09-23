# -*-coding: utf-8 -*-
# 对txt文件进行中文分词
import jieba
import os
from utils import files_processing

# 按脚本所在目录定位，避免从仓库根目录启动时找不到文件
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
source_folder = os.path.join(_BASE_DIR, "西游记", "source")
segment_folder = os.path.join(_BASE_DIR, "西游记", "segment")


def segment_lines(file_list, segment_out_dir, stopwords=[]):
    """
    对txt文件进行中文分词, 用空格拼接后，输出到segment_out_dir目录中
    输入：
        file_list: 文件列表
        segment_out_dir: 输出目录
        stopwords: 停用词列表
    """
    for i, file in enumerate(file_list):
        segment_out_name = os.path.join(segment_out_dir, "segment_{}.txt".format(i))
        with open(file, "rb") as f:
            document = f.read()
            document_cut = jieba.cut(document)
            sentence_segment = []
            for word in document_cut:
                if word not in stopwords:
                    sentence_segment.append(word)
            result = " ".join(sentence_segment)
            result = result.encode("utf-8")
            with open(segment_out_name, "wb") as f2:
                f2.write(result)


# 对source中的txt文件进行分词，输出到segment目录中
file_list = files_processing.get_files_list(source_folder, postfix="*.txt")
segment_lines(file_list, segment_folder)
