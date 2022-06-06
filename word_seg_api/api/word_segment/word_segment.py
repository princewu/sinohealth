from api.word_segment import locations, last_words, words, child_dic, preprocess
from app import app
from flask import request
import json


def third_part_cut(term):
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
    s_index = 0
    s_index_tail = 0
    for l in locations:
        if l in term:
            tmp_index = term.index(l)
            if tmp_index >= s_index and l:
                s_index = tmp_index
                s_index_tail = len(l) + s_index
        else:
            pass
    return s_index_tail


def add_word(left, name, right, equal='right'):
    ''' 
    对于长度较短的字符串，在其左侧或右侧添加字
    Parameters
    ----------
    left : str
        搜索关键词的左侧子串
    name : str
        搜索关键词
    right : str
        搜索关键词右侧子串
    words : dic
        完整的语料词频词典.
    equal : str
        等号的方向，默认为右侧。
    Returns
    -------
    name : str
        修改后的搜索关键词
    '''
    if len(left) > 0:
        l = left[-1]
    else:
        l = ''
    if len(right):
        r = right[0]
    else:
        r = ''
    try:
        # l = left[-1]
        left_mi = words[l + name]/(words[l]*words[name])
    except:
        left_mi = 0
    try:
        # r = right[0]
        right_mi = words[name + r]/(words[r]*words[name])
    except:
        right_mi = 0
    if equal == 'right':
        if left_mi > right_mi:
            if l:
                name = l+name
            else:
                name += r
        else:
            if r:
                name += r
            else:
                name = l + name
    if equal == 'left':
        if left_mi >= right_mi:
            if l:
                name = l+name
            else:
                name += r
        else:
            if r:
                name += r
            else:
                name = l + name
    return name


def sep_long_sent(w, child_dic, max_len):
    '''
    基于互信息（MI）进行切词，主要为了把较长的词拆为较小颗粒的词。
    Parameters
    ----------
    w: str
        待切分的长词
    child_dic : dict
        按词条字数整理的词典
    beta : int
        互信息的阈值
    Returns
    -------
    result : dict
        未切分的词及其互信息值。
    max_len : int
        词条最大长度
    '''
    while len(w) > max_len:
        left = ''
        left_freq = 0
        right = ''
        right_freq = 0
        for i in range(1, len(w)):  # 遍历子词典
            try:
                # 找字符串左边最短的词
                for s in child_dic[i]:
                    if w.startswith(s):
                        if child_dic[i][s] >= left_freq:
                            left_freq = child_dic[i][s]
                            left = s
                # 找字符串右边最短的词
                    if w.endswith(s):
                        if child_dic[i][s] >= right_freq:
                            right_freq = child_dic[i][s]
                            right = s
            except:
                pass
        if left_freq == right_freq == 0:
            w = w[:-1]
        elif left_freq >= right_freq:
            left_index = w.index(left)+len(left)
            w = w[left_index:]
        else:
            right_index = w.index(right)
            w = w[:right_index]
    return w


@app.route('/term_segment', methods=['get', 'post'])
def term_segment():
    """
    切词
    Parameters
    ----------
    data : s
        待拆的词
    Returns
    -------
    result : list
    """
    s = request.json['original_word']
    third_seg = third_part_cut(s)   
    first_seg = first_part_cut(s)
    locat = s[:first_seg] # 第一部分
    enti = s[third_seg:] # 第三部分
    core = names = s[first_seg : third_seg] # 第二部分，也是核心部分
    # 当核心词长度小于4时，分别向两侧扩展，计算互信息，选择互信息更大的作为连接的依据。
    while len(names) < 4:
        names = add_word(locat, names, enti)
        l_i = s.index(names)
        locat =s[:l_i]
        enti = s[l_i+len(names):]  
    # 当核心词长于20个字时，按照长词切割做，
    if len(names) >=20:
        names = sep_long_sent(names, child_dic, 19)  
    return json.dumps({'names':names, 'core':core})


@app.route('/word_cut', methods=['post'])
def word_cut():
    '''
    主要针对已经爬取过的(flag==1)，且无返回结果的情况。核心思路就是对词进行拆解。策略：1.基于互信息的词条拆解（类似于长词拆解）；
                                                                         2.词语替换（2-1：基于核心词重新组合；2-2：关键词的替换）
    Returns
    -------
    current_word
        搜索词
    '''
    current_word = request.json['current_word'] # str, 当前的搜索词
    original_word = request.json['original_word'] # str,原词汇
    core = request.json['core'] # str,核心词汇
    all_word = request.json['all_word'] # []，所有试过的词
    # 策略1  基于互信息一个字一个字地拆词。结尾如果是数字字母的，去除。
    # 如果切词后词的长度小于4，则保留原词汇。
    if len(preprocess(current_word)) < 4:
        pass
    else:
        current_word = preprocess(current_word)
    
    if len(current_word) > 4:
        if current_word[0] in child_dic[1].keys():
            l_freq = child_dic[1][current_word[0]]
        else:
            l_freq = 0
        if current_word[-1] in child_dic[1].keys():
            r_freq = child_dic[1][current_word[-1]]
        else:
            r_freq = 0
        if l_freq > r_freq:
            current_word = current_word[1:]
        else:
            current_word = current_word[:-1]
        if current_word not in all_word:
            return json.dumps({'current_word': current_word})
        else:
            pass
    else:
        pass
    #策略2 如果核心词长度小于4的话，换一种方式进行组合。
    if len(core) < 4:
        name = core
        while len(name) < 4:
            left = original_word[:original_word.index(name)]
            right = original_word[original_word.index(name)+len(name):]
            name = add_word(left, name, right, 'left')
        if name not in all_word:
            return json.dumps({'current_word': name})
        else:
            pass

    # 策略3 如果有endword在词的中间，且后半部分词的长度大于等于4，则以后半部分的前四个字作为搜索词
    if "附属" in original_word:
        if len(original_word) - original_word.index('附属') - 2 >= 4:
            start = original_word.index('附属') + 2
            current_word = original_word[start:start+4]
            if current_word not in all_word:
                return json.dumps({'current_word': current_word})
            else:
                pass
    if '有限公司' in original_word:
        if len(original_word) - original_word.index('有限公司') - 4 >= 4:
            start = original_word.index('有限公司') + 4
            current_word = original_word[start:start+4]
            if current_word not in all_word:
                return json.dumps({'current_word': current_word})
            else:
                pass
    else:
        pass


    # 策略4 含有一定关键词的进行替换
    current_word.replace('村', '社区')
    if current_word not in all_word:
        return json.dumps({'current_word': current_word})
    else:
        pass
    return json.dumps({'current_word': None})
    

@app.route('/word_addition', methods=['post'])
def words_addition():
    '''
    主要针对已经爬取过的(flag==1)且返回结果>20的情况。核心策略就是按互信息从两侧选词
    Parameters
    ----------
    current_word : TYPE
        DESCRIPTION.
    origin_word : TYPE
        DESCRIPTION.

    Returns
    -------
    name : TYPE
        DESCRIPTION.
    '''
    current_word = request.json['current_word']
    original_word = request.json['original_word'] 
    # 如果核心词大于等于4个字，或者更换了拼词方向以后的词仍未同一个词，则逐个加字
    left_index = original_word.index(current_word)
    right_index = left_index + len(current_word)
    left = original_word[:left_index]
    right = original_word[right_index:]
    current_word = add_word(left, current_word, right)
    return json.dumps({'current_word':current_word})




@app.route('/')
def hello_world():
    return 'Hello, World!'


