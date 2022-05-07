# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from collections import defaultdict #defaultdict是经过封装的dict，它能够让我们设定默认值
from tqdm import tqdm #tqdm是一个非常易用的用来显示进度的库
from math import log
import re
# import csv
import pandas as pd

# 导入数据
def csv2txt(path, nrows, outputs):
    d = pd.read_csv(path, nrows= nrows, encoding = 'gbk')    
    data = []
    i = 0 
    for index, row in d.iterrows():
        # data.append(str(row['主诉']).strip().replace(' ', '').replace(',','，'))
        xian_bing = str(row['现病史'])
        ji_wang = str(row['既往史'])
        guo_min = str(row['过敏史'])
        if xian_bing:               
            data.append(xian_bing.strip().replace(' ', '').replace(',','，'))
        if ji_wang:
            data.append(ji_wang.strip().replace(' ', '').replace(',','，'))
        if guo_min:
            data.append(guo_min.strip().replace(' ', '').replace(',','，'))
        # data.append(str(row['体格检查']).strip().replace(' ', '').replace(',','，'))
        i+=1
        print('当前正在处理第',i,'行')
    print('数据导入完成')
    '''
    for each in data:
        if each =='nan' or  each =='[无]' or each =='无' or each =='同前':
            data.remove(each)
    print('数据去重完成')
    '''
    data = list(set(data))
    output = open(outputs,'w',encoding=('utf-8'))
    for each in data:
        output.write(each)
        output.write('\n')
    output.close()


class Find_Words:
    def __init__(self, min_count=10, min_pmi=0):
        self.min_count = min_count
        self.min_pmi = min_pmi # 凝固度
        self.chars, self.pairs = defaultdict(int), defaultdict(int) #如果键不存在，那么就用int函数
                                                                  #初始化一个值，int()的默认结果为0
        self.total = 0.
    def text_import(self, address):
        with open(address, 'r', encoding='utf-8') as f:
            text= [line.strip() for line in f]
            return list(set(text))
    
    
    def text_filter(self, texts): #预切断句子，以免得到太多无意义（不是中文、英文、数字）的字符串
        for a in tqdm(texts):
            for t in re.split(u'[^\u4e00-\u9fa50-9a-zA-Z]+', a): #这个正则表达式匹配的是任意非中文、
                                                              #非英文、非数字，因此它的意思就是用任
                                                              #意非中文、非英文、非数字的字符断开句子
                if t:
                    yield t
    def count(self, texts): #计数函数，计算单字出现频数、相邻两字出现的频数
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
                
    def find_words(self, texts): #根据前述结果来找词语
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



def tail_word_segment(t_text): 
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


def short_word_segment(t_text):
    '''
    筛选出长度较短的词语（目前筛选单字）
    '''
    one_word_list =[] # 记录字典中所有单个字的词    
    #获取所有尾字
    for n in t_text.keys(): 
        if len(n) ==1:
            one_word_list.append(n)
    return one_word_list


def head_freq_ratio(start_word, output_dic, alpha):
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
                    print('-----------------')
                    print('%s的词频为%d,%s的词频为%d'%(each, two_gram_freq[each], pw, pw_freq))
                    output_dic[pw[:-1]] += two_gram_freq[each]
                    output_dic[start_word] += two_gram_freq[each]
                    o_dic[each] = corpus[each]
                    del output_dic[each[:-1]]
                else:
                    pass
            else: # 如果去掉结尾词后其他词不在词典中，则保留该词
                pass
    return o_dic
    
    
    
    

def tail_freq_ratio(end_word,output_dic,alpha):
    '''
    输入：end _word 结尾字：str
         corpus 字典：[str,str,...]
         alpha 词频比例阈值。不包含结尾词的短语与包含结尾词的短语比值，如果大于alpha，则切开。否则保留： str
    输出：移除字典的词的列表
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
                    print('-----------------')
                    print('%s的词频为%d,%s的词频为%d'%(each, two_gram_freq[each], pw, pw_freq))
                    output_dic[pw[1:]] += two_gram_freq[each]
                    output_dic[end_word] += two_gram_freq[each]
                    o_dic[each] = corpus[each]
                    del output_dic[each[1:]]
                else:
                    pass
            else: # 如果去掉结尾词后其他词不在词典中，则保留该词
                pass
    return o_dic


          

        


# csv2txt('E:/HaoWu/data/duplicate_emrs.csv', 600000,'E:/HaoWu/data/raw_data.txt')

# fw = Find_Words(5, 1)
# texts = fw.text_import('E:/HaoWu/data/train_data.txt')
# fw.count(texts)
# fw.find_words(texts)
# # mutal_info_score = fw.mutal_info_score
# # 生成词典，输出词典 
# words = fw.words
# for word in list(words.keys()):
#     result = re.match('^[\u4e00-\u9fa5]*$', word)
#     if not result:
#         words.pop(word)
# # words.to_csv('dict_demo.txt', sep='\t',index=True)

# one_word_list = short_word_segment(words)

# start：
l = 1
while l > 0:
    p_count = len(words)
    for h in ['无','有','伴','能','一','为','且','不','于','以','也','仍','觉','但','及','和','咯','或','由','的','至']:
        test_h = head_freq_ratio('至', words, 2)
    if len(words) < p_count:
        l = 1
    else:
        l = 0
# end
d = 1
while d>0:
    p_count = len(words)
    for t in ['后','等','起','前','右','左','及','出','阵','上','下','时','来','在','或','和','多','少','未','被','有','好']:
        test_t = tail_freq_ratio('好', words, 2)
    if len(words) < p_count:
        d = 1
    else:
        d = 0
#     #     print(s)
#words = pd.Series(words).sort_values(ascending=False)
#pd.Series(mutal_info_score).sort_values(ascending=False).to_csv('score.txt',sep='\t',index=True)












































        #         total_freq += self.words[n]
        #         if n == string:
        #             pass
        #         else:
        #             candidates = n[len(string):] #所有候选词
        #             if candidates in self.words.keys(): # 如果候选词在我们的词库中，存入freqs字典中。
        #                 self.freqs[candidates] = self.words[n]
        #             else:
        #                 pass
        # # 计算信息熵，如果信息熵大于阈值，切开，否则保留
        # for k, v in self.freqs.items():
        #     entropy_num = -log(v/total_freq)
        #     self.freqs[k]=entropy_num
        #     if entropy_num >= alpha:
        #         pass
        #     else:
        #         print(k)
        #         self.words[k] += v  # 如果信息熵较小，代表比较稳定，此时分词
        #         self.words[string] += v
        #         del self.words[string+k]
        
        
        
        

# # 计算与最后一个字相邻字的熵（最后两个字）    
# def left_entropy_compute(end_word, corpus):
#     '''
#     计算左熵
#     输入：结尾字：str
#           预料：[str,str,...]
#     输出：得分
#     '''
#     entropy = 0
#     two_gram_list = [] # 记录所有词组组合
#     two_gram_freq = {} # 记录所有2元词组词频
#     total_freq = 0 # 记录所有以single为结尾的词频
#     for each in corpus.keys():
#         two_gram = each[-2:]
#         if each.endswith(end_word):
#             total_freq += corpus[each]
#             if two_gram not in two_gram_list:
#                 two_gram_list.append(two_gram)
#                 two_gram_freq[two_gram] = corpus[each]
#             else:
#                 two_gram_freq[two_gram] += corpus[each]
#     # 计算每个二元词组的概率
#     for each in two_gram_freq.values():
#         p = each/ total_freq
#         entropy -= p*log(p) 

    
#     return entropy,two_gram_freq
#     #return entropy