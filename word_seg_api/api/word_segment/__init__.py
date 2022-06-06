import re
import pandas as pd

# name = "lina"

def preprocess(term):
    term_new = re.sub('[0-9A-Za-z]+$', '', term)
    term_new = re.sub('^[0-9A-Za-z]+', '', term)
    if term_new:
        return term_new
    else:
        return term


def rebuild_dic(dic):
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
    for k, v in dic.items():
        word_len = len(k)
        if word_len not in child_dic.keys():
            child_dic[word_len] = {}
        child_dic[word_len][k] = v
    return child_dic



# if __name__ == 'main':
    # 导入停用词
loc_seg = []  # 表示行政区域的标志词，如省市自治区等
with open('/root/HaoWu/word_seg_api/data/location_stopwords.txt', encoding='utf-8') as f:
    [loc_seg.append(line.strip()) for line in f]
locations = []
with open('/root/HaoWu/word_seg_api/data/location_list.txt', encoding='utf-8') as f:
    [locations.append(line.strip()) for line in f]
last_words = []  # 医疗机构术语名的第三部分，医疗机构的性质（如医院/保健院/诊所等）
with open('/root/HaoWu/word_seg_api/data/last_words.txt', encoding='utf-8') as f:
    [last_words.append(line.strip()) for line in f]

# 读入字典
print('----正在读入字典------')
words = {}
d = pd.read_csv('/root/HaoWu/word_seg_api/data/dic.csv', encoding='gbk')
for index, row in d.iterrows():
    row['keys'] = preprocess(row['keys'])
    words[row['keys']] = row['values']
sub_list = []
p = pd.read_csv('/root/HaoWu/word_seg_api/data/sub_dic.csv', encoding='utf-8')
sub_list =[]
# for index, row in p.iterrows():
#     sub_list.append([row['original_word'], row['new_word']])
print('----字典读入完毕----')
child_dic = rebuild_dic(words)
print('-----子字典构建完成-----')


