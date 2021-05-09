# encoding:UTF-8
# write by qbb95
# time:2021/5/9

import requests
import random
import json
from hashlib import md5

# url = 'https://fanyi-api.baidu.com/api/trans/vip/translate' # https链接
url = 'http://api.fanyi.baidu.com/api/trans/vip/translate' # http链接

from_lang = 'jp'
to_lang =  'zh'

appid = '20191013000341133'
appkey = 'j9QGaHfAKnfGtskGZcWB'

def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

salt = random.randint(32768, 65536)

headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# 传入字符串应为trf8格式
def translate(query):
    sign = make_md5(appid + query + str(salt) + appkey) #签名
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    return result['trans_result'][0]['dst']