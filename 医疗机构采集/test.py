# -*- coding: utf-8 -*-
"""
Created on Thu May 12 11:30:58 2022

@author: Ad
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd


def third_part_cut(term):
    last_words = [] #医疗机构术语名的第三部分，医疗机构的性质（如医院/保健院/诊所等）
    with open('last_words.txt', encoding='utf-8') as f:
        [last_words.append(line.strip()) for line in f]
    
    t_index = 100
    for t in last_words:
        if t in term:
            tmp_index = term.index(t)
            if tmp_index < t_index:
                t_index = tmp_index
    
    if t_index < 100:
        return t_index
    else:
        return len(term)-1    
 
    
 
def first_part_cut(term):
    
    loc_seg = [] #表示行政区域的标志词，如省市自治区等
    with open('location_stopwords.txt', encoding='utf-8') as f:
        [loc_seg.append(line.strip()) for line in f]
    locations = []
    with open('location_list.txt', encoding='utf-8') as f:
        [locations.append(line.strip()) for line in f]
    
    s_index = 0
    s_index_tail = 0
    # for s in loc_seg:
    #     if s in term:
    #         tmp_index = term.index(s)
    #         if tmp_index > s_index:
    #             s_index = tmp_index
    #             s_index_tail = len(s) + s_index
    
    for l in locations:
        if l in term:
            print(l)
            tmp_index = term.index(l)
            print(tmp_index)
            if tmp_index > s_index:
                s_index = tmp_index
                s_index_tail = len(l) + s_index
        else:
            pass
        
    return s_index_tail
    
    

#     p_index = 100
#     p_len = 0
#     for p in posi_sig_wd:
#         if p in each:
#             tmp_index = each.index(p)              
#             if tmp_index < p_index:
#                 p_index = tmp_index
#                 p_len = len(p)
#                 # print(each)
#                 # print(p_index)
#                 # print(each[:p_index])
#                 # print('--------------------------')
#     if p_index < 100:
#         seped.append([each[:p_index], each[p_index:]])
#         location_list.append(each[:p_index])
#     else:
#         unfounded.append(each)    
    
    
# def third_part_cut()






# # 导入数据

# loc_seg = [] #表示行政区域的标志词，如省市自治区等
# with open('location_stopwords.txt', encoding='utf-8') as f:
#     [loc_seg.append(line.strip()) for line in f]

# locations = []
# with open('location_list.txt', encoding='utf-8') as f:
#     [locations.append(line.strip()) for line in f]
    
# last_words = [] #医疗机构术语名的第三部分，医疗机构的性质（如医院/保健院/诊所等）
# with open('last_words.txt', encoding='utf-8') as f:
#     [last_words.append(line.strip()) for line in f]
    
data =[]
with open('test_data_20w.txt', encoding='utf-8') as f:
    [data.append(line.split()[1][1:-1]) for line in f]


# 将整个术语切分成三部分
for s in data[:100]:

    third_seg = third_part_cut(s)
    
    first_seg = first_part_cut(s)
    print(s)
    print(first_seg)
    print(s[:first_seg])
    print('-----')

        
    # last_seg = third_part_cut(last_words, s) # 返回的是index，如果有就返回实际的起始index，没有的话返回字符串最后一个字符的index
    
    
    
    
    
    
    
    
    
    
    
    















































    
    
    
    

