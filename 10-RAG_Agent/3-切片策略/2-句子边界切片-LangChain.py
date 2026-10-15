#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句子边界切片（LangChain）

用 RecursiveCharacterTextSplitter 先在句子结束符处断开，
再合并到 max_chunk_size。chunk_overlap=0，块与块之间不重叠。
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 与手写版的 [.!?。！？\n] 对应；不放空字符串，超长句子保持完整
SENTENCE_SEPARATORS = ["。", "！", "？", ".", "!", "?", "\n"]


def semantic_chunking(text, max_chunk_size=512):
    """按句子边界切分，再合并到最大长度。"""
    splitter = RecursiveCharacterTextSplitter(
        separators=SENTENCE_SEPARATORS,
        chunk_size=max_chunk_size,
        chunk_overlap=0,
        length_function=len,
        keep_separator="end",
    )
    return splitter.split_text(text)


def print_chunk_analysis(chunks, method_name):
    """打印切片分析结果"""
    if not chunks:
        print("❌ 未生成任何切片")
        return

    sizes = len(chunks)
    total_length = sum(len(chunk) for chunk in chunks)
    avg_length = total_length / sizes
    min_length = min(len(chunk) for chunk in chunks)
    max_length = max(len(chunk) for chunk in chunks)

    print(f"\n【统计信息】")
    print(f"   - 切片方法: {method_name}")
    print(f"   - 切片数量: {sizes}")
    print(f"   - 平均长度: {avg_length:.1f} 字符")
    print(f"   - 最短长度: {min_length} 字符")
    print(f"   - 最长长度: {max_length} 字符")
    print(f"   - 长度方差: {max_length - min_length} 字符")

    print(f"\n【切片内容】")
    for i, chunk in enumerate(chunks, 1):
        print(f"----- 块{i} -- {len(chunk)} 字符 ", "-" * 130)
        print(f"{chunk}")


if __name__ == "__main__":
    text = """
    迪士尼乐园提供多种门票类型以满足不同游客需求。一日票是最基础的门票类型，可在购买时选定日期使用，价格根据季节浮动。
    两日票需要连续两天使用，总价比购买两天单日票优惠约9折。特定日票包含部分节庆活动时段，需注意门票标注的有效期限。
    购票渠道以官方渠道为主，包括上海迪士尼官网、官方App、微信公众号及小程序。第三方平台如飞猪、携程等合作代理商也可购票，但需认准官方授权标识。
    所有电子票需绑定身份证件，港澳台居民可用通行证，外籍游客用护照，儿童票需提供出生证明或户口本复印件。
    生日福利需在官方渠道登记，可获赠生日徽章和甜品券。半年内有效结婚证持有者可购买特别套票，含皇家宴会厅双人餐。
    军人优惠现役及退役军人凭证件享8折，需至少提前3天登记审批。
    """

    print("=" * 150)
    print("🎯 句子边界切片策略（LangChain） 测试，文本长度：", len(text), "字符")
    chunks = semantic_chunking(text, max_chunk_size=300)
    print_chunk_analysis(chunks, "句子边界切片")
