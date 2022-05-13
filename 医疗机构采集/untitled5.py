# -*- coding: utf-8 -*-
"""
Created on Thu May 12 16:34:18 2022

@author: Ad
"""

import jieba.posseg as psg
from collections import defaultdict #defaultdict是经过封装的dict，它能够让我们设定默认值
from tqdm import tqdm #tqdm是一个非常易用的用来显示进度的库
from math import log
import re
# import csv
import pandas as pd

from collections import defaultdict #defaultdict是经过封装的dict，它能够让我们设定默认值
from tqdm import tqdm #tqdm是一个非常易用的用来显示进度的库
from math import log
import re
# import csv
import pandas as pd


# 导入数据
def csv2txt(path, nrows, outputs):
    '''
    将csv文件不同单元格中的文本串，输出为txt。一个单元格在txt中输出为1行。
    Parameters
    ----------
    path : str
        csv文本路径
    nrows : int
        读取csv的行数
    outputs : str
        txt文件的路径

    '''
    d = pd.read_csv(path, nrows= nrows, encoding = 'gbk')    
    data = []
    i = 0 
    for index, row in d.iterrows():
        xian_bing = str(row['现病史'])
        ji_wang = str(row['既往史'])
        guo_min = str(row['过敏史'])
        if xian_bing:               
            data.append(xian_bing.strip().replace(' ', '').replace(',','，'))
        if ji_wang:
            data.append(ji_wang.strip().replace(' ', '').replace(',','，'))
        if guo_min:
            data.append(guo_min.strip().replace(' ', '').replace(',','，'))
        i+=1
        print('当前正在处理第',i,'行')
    print('数据导入完成')
    data = list(set(data))
    output = open(outputs,'w',encoding=('utf-8'))
    for each in data:
        output.write(each)
        output.write('\n')
    output.close()



class Find_Words:
        
    def __init__(self, min_count=10, min_pmi=0):
        self.min_count = min_count # 词频
        self.min_pmi = min_pmi # 凝固度
        self.chars, self.pairs = defaultdict(int), defaultdict(int) #如果键不存在，那么就用int函数初始化一个值，int()的默认结果为0
        self.total = 0.
        
        
    def text_import(self, path):
        '''
        读取语料，输入格式为txt
        Parameters
        ----------
        path: str
            txt文件的路径

        Returns
        -------
        list
            语料，以list形式输出.

        '''
        with open(path, 'r', encoding='utf-8') as f:
            text= [line.strip()[1:-1] for line in f]
            return list(set(text)) # 去重
    
    #预切断句子，以免得到太多无意义（不是中文、英文、数字）的字符串
    def text_filter(self, texts): 
        for a in tqdm(texts):
            for t in re.split(u'[^\u4e00-\u9fa50-9a-zA-Z]+', a): #这个正则表达式匹配的是任意非中文、非英文、非数字，因此它的意思就是用任意非中文、非英文、非数字的字符断开句子
                if t:
                    yield t                    
    
    #计数函数，计算单字出现频数、相邻两字出现的频数                
    def count(self, texts):     
        for text in self.text_filter(texts):
            self.chars[text[0]] += 1
            for i in range(len(text)-1):
                self.chars[text[i+1]] += 1
                self.pairs[text[i:i+2]] += 1
                self.total += 1
        self.chars = {i:j for i,j in self.chars.items() if j >= self.min_count} #最少频数过滤
        self.pairs = {i:j for i,j in self.pairs.items() if j >= self.min_count} #最少频数过滤
        self.strong_segments = set()
        #self.mutal_info_score = defaultdict(int)
        for i,j in self.pairs.items(): #根据互信息找出比较“密切”的邻字
            mutal_info = log(self.total*j/(self.chars[i[0]]*self.chars[i[1]]))
        #    self.mutal_info_score[i] = mutal_info
            if mutal_info >= self.min_pmi:
                self.strong_segments.add(i)
          
    #根据前述结果来找词语            
    def find_words(self, texts): 
        self.words = defaultdict(int)
        for text in self.text_filter(texts):
            s = text[0]
            for i in range(len(text)-1):
                if text[i:i+2] in self.strong_segments: #如果比较“密切”则不断开
                    s += text[i+1]
                else:
                    self.words[s] += 1 #否则断开，前述片段作为一个词来统计
                    s = text[i+1]
            self.words[s] += 1 #最后一个“词”
        self.words = {i:j for i,j in self.words.items() if j >= self.min_count} #最后再次根据频数过滤
        return self.words



    def tail_word_segment(self, t_text): 
        '''
        首先对词进行扫描，获得所有的词的最后一个字；
        输入：t_text  即为词典 ： dic
        输出：word_list  所有最后一个字
             words  加了占位符的字典
        '''    
        words = {}
        one_word_list =[] # 记录字典中所有单个字的词    
        #获取所有尾字
        for n in t_text.keys(): 
            if len(n) ==1:
                one_word_list.append(n)
            new_word = '*' + n  # 防止单字前面没有其他词的情况
            words[new_word] = t_text[n]
        return one_word_list, words


    def short_word_segment(self, t_text):
        '''
        筛选出长度较短的词语（目前筛选单字）
        '''
        one_word_list =[] # 记录字典中所有单个字的词    
        #获取所有尾字
        for n in t_text.keys(): 
            if len(n) ==1:
                one_word_list.append(n)
        return one_word_list


    def head_freq_ratio(self, start_word, output_dic, alpha):
        '''
        计算一个词组中，首字与其余字（前提是两者都要在词典中）的词频的比例。如果大于某一比例则认为该词可以继续切分
        Parameters
        ----------
        start_word : str
            字符串的首字
        output_dic : dict
            词典，即可以进行增删查改的词典。输入时作为语料，运行时会进行更替
        alpha : float
            阈值。用于判断词的除了首字以外部分的词频与原词的词频的比值。如果删除首字后的词频超过原词词频alpha倍，则认为删除首字后的词组更为常用。

        Returns
        -------
        o_dic : dict
            切分的词语集合
        '''
        o_dic ={}
        two_gram_freq = {} # 记录所有以startwords开头的词频
        total_freq = 0 # 记录所有以startwords的词频
        corpus ={}
        for n in output_dic.keys():
            new_word = n +'*'  # 防止单字后面没有其他词的情况
            corpus[new_word] = output_dic[n]
        for each in list(corpus.keys()):
            if each.startswith(start_word):
                total_freq += corpus[each]
                two_gram_freq[each] = corpus[each]
                pw = each[len(start_word):]  # 判断去除startwords后的词是否在词典中
                if pw in corpus.keys(): 
                    pw_freq = corpus[pw]
                    if pw_freq/two_gram_freq[each] >= alpha and len(each)>3: #如果大于阈值，则将该词切开。最小长度的词为2，但因为我加了*作为占位符，因此最小长度为3
                        # print('-----------------')
                        # print('%s的词频为%d,%s的词频为%d'%(each, two_gram_freq[each], pw, pw_freq))
                        output_dic[pw[:-1]] += two_gram_freq[each]
                        output_dic[start_word] += two_gram_freq[each]
                        o_dic[each] = corpus[each]
                        del output_dic[each[:-1]]
                    else:
                        pass
                else: # 如果去掉结尾词后其他词不在词典中，则保留该词
                    pass
        return o_dic
    
    
    def tail_freq_ratio(self, end_word,output_dic,alpha):
        '''
        同head_freq_ratio
        '''
        o_dic ={}
        two_gram_freq = {} # 记录所有以endword结尾的词频
        total_freq = 0 # 记录所有以endwords为结尾的词频
        corpus ={}
        for n in output_dic.keys():
            new_word = '*' + n   # 防止单字后面没有其他词的情况
            corpus[new_word] = output_dic[n]
        for each in list(corpus.keys()):
            if each.endswith(end_word):
                total_freq += corpus[each]
                two_gram_freq[each] = corpus[each]
                
                pw = each[:-len(end_word)]  # 判断去除endword后的词是否在词典中
                if pw in corpus.keys(): 
                    pw_freq = corpus[pw]
                    if pw_freq/two_gram_freq[each] >= alpha and len(each)>3: #如果大于阈值，则将该词切开。最小长度的词为2，但因为我加了*作为占位符，因此最小长度为3
                        # print('-----------------')
                        # print('%s的词频为%d,%s的词频为%d'%(each, two_gram_freq[each], pw, pw_freq))
                        output_dic[pw[1:]] += two_gram_freq[each]
                        output_dic[end_word] += two_gram_freq[each]
                        o_dic[each] = corpus[each]
                        del output_dic[each[1:]]
                    else:
                        pass
                else: # 如果去掉结尾词后其他词不在词典中，则保留该词
                    pass
        return o_dic


def rebuild_dic( dic):
    '''
    重构字典，按照字典词的字数重构
    Parameters
    ----------
    dic : dict
        原词典
    Returns
    -------
    child_dic : dict
        按词的字数重新整理的词典
    '''
    child_dic = {}
    for k,v in dic.items():
        word_len = len(k)
        if word_len not in child_dic.keys():
            child_dic[word_len] = {}
        child_dic[word_len][k] = v
    return child_dic

def sep_long_sent( child_dic, beta):
    '''
    基于互信息（MI）进行切词，主要为了把较长的词拆为较小颗粒的词。
    Parameters
    ----------
    child_dic : dict
        按词条字数整理的词典
    beta : int
        互信息的阈值
    Returns
    -------
    result : dict
        未切分的词及其互信息值。
    sep_set : dict
        所有切分的词，及其互信息值。
    '''
    result =[]
    all_combos =[] # 所有的组合
    for i in range(len(child_dic), 2, -1):  #遍历子词典
    # 字典经过多轮更新后，可能出现某一个子字典里面为空的情况。try-except主要解决规避这个问题引起的报错。
        try: 
            print(i)
            for s in child_dic[i]:  # 遍历子词典中的词
                tmp = []
                tmp2 = []
                for p in range(len(s)-1, 0, -1): # 二分法去查找所有可能的结果。
                    for w in child_dic[p].keys():
                        if w == s[:p] and s[p:] in child_dic[len(s)-p].keys():
                            mi = words[s]/(words[w]*words[s[p:]])
                            tmp.append([s,w,s[p:], mi])
                            tmp2.append([w, s[p:], round(mi*100000, 2)])
                            # print(tmp2)
                tmp = sorted(tmp, key=lambda x: x[3],reverse=False)
                tmp2 = sorted(tmp2, key=lambda x: x[2],reverse=False)
                if tmp2:
                    for each in tmp2:
                        # print(s)
                        all_combos.append([s, words[s], str(tmp2)])
                else:
                    all_combos.append([s, words[s],'-'])
                if tmp:
                    result.append(tmp[0])
                    result = sorted(result, key=lambda x: x[3],reverse=True) # 按照互信息值从小到大排序
        except:
            pass
    print('-----------------------------')
    sep_set = []
    result = sorted(result, key=lambda x: len(x[0]),reverse=False) # 按词条字数，从多到少，进行排序
    for m in range(len(result)-1,-1,-1):
        if result[m][3] <= beta: # beta为MI的阈值
            words[result[m][1]] += words[result[m][0]]
            words[result[m][2]] += words[result[m][0]]
            del words[result[m][0]]
            print(result[m][0])
            sep_set.append(result[m])
            result.pop(m)  
        else:
            pass   
    return result, sep_set, all_combos
        




if __name__ == "__main__":

# text = '上海崇明巴士公共交通有限公司保健站'
# for w in psg.cut(text):
#     print(w)
    
    # texts = fw.text_import('D:/桌面/build-dict-unsupervised/医疗机构采集/full_data_90w.txt')
    # fw = Find_Words(5, 1)
    # fw.count(data)
    # fw.find_words(data)
    # words = fw.words
    
    
    # 生成省市的词典，需要保留标志词（市/镇/村等）以及地名
    # data =[]
    # test =[]
    # for i in range(11):
    #     print(i)
    #     f = pd.read_excel('D:/桌面/build-dict-unsupervised/医疗机构采集/dim_china_region_code.xls', header =0, sheet_name = i)
    #     for index, row in f.iterrows():
    #         if row[1]<=3:
    #             data.append(row['名称'])
    #         # elif row['名称'].endswith('村'):
    #             data.append(row['名称'])
    #         else:
    #             test.append(row['名称'])
    # fw = Find_Words(5, 1)
    # fw.count(data)
    # fw.find_words(data)
    # words = fw.words    
    posi_sig_wd = ['区','市','省','嘎查','苏木','左旗','右旗','自治旗','旗','自治区','县','自治州','村','乡','社区居委会','村民委员会','村委会','街道']
#     with open('location_stopwords.txt','w', encoding=('utf-8')) as f:
#         for l in posi_sig_wd:
#             f.write(l)
#             f.write('\n')
#         f.close()
#     seped = [] # 能找到关键词的
#     unfounded =[] # 找不到关键词的
    
#     location_list = []
#     for each in data:
#         p_index = 100
#         p_len = 0
#         for p in posi_sig_wd:
#             if p in each:
#                 tmp_index = each.index(p)              
#                 if tmp_index < p_index:
#                     p_index = tmp_index
#                     p_len = len(p)
#                     # print(each)
#                     # print(p_index)
#                     # print(each[:p_index])
#                     # print('--------------------------')
#         if p_index < 100:
#             seped.append([each[:p_index], each[p_index:]])
#             location_list.append(each[:p_index])
#         else:
#             unfounded.append(each)

# location_list = list(set(location_list))
# with open('location_list.txt','w', encoding=('utf-8')) as f:
#     for l in location_list:
#         if len(l)>1:
#             f.write(l)
#             f.write('\n')
#     f.close()
    

        
    
    