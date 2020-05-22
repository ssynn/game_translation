# coding=utf8

import json
import re
# with open('E:/Tools/VNR/jp_chs_split.json', 'r') as f:
#     jp_chs = json.loads(f.read())

# a = '【亮介】あ、お疲れさまですゲンさん。'

# a = a.replace('\n', '')
# a = a.replace('　', '')
# print('你好'.encode('gbk'))

def local_translate(text, jp_chs):
    def _split_line(text):
        split_str = [u'。',u'？',u'！',u'】']
        _ans = []
        _buffer = ''
        for i in text:
            _buffer += i
            if i in split_str and len(_buffer):
                _ans.append(_buffer)
                _buffer = ''
        return _ans

    text = text.replace('\n','')
    text = text.replace(u'　','')
    engine = 'default'
    if 'engine' in jp_chs:
        engine = jp_chs['engine']
    if engine == 'default':
        return jp_chs[text] if text in jp_chs else ''
    elif engine == 'snl':
        ans = ''
        # print text
        text_list = _split_line(text)
        print text_list
        for t in text_list:
            if t in jp_chs:
                ans += jp_chs[t]
            else:
                print t
                return ''
        return ans

    return ''


with open('intermediate_file/jp_chs.json', 'r') as f:
    jp_chs = json.loads(f.read())

# with open('intermediate_file/text.json', 'r') as f:
#     a = json.loads(f.read())

a = [
    u"晶ちゃんが怒っているのは、放課後須藤さん――晶ちゃんの友達からかけられた一言について。\nそれは――‥‥", 
    u"【カナ】よっ、お二人サン、これから生徒会か？",
    u"【カナ】今日も一緒に帰るんだろ？オマエらホント仲イイよな～。で、結婚式はいつにすんの？"
    ]
import time
a = time.time()
for i in range(100000):
    pass
print time.time() - a
