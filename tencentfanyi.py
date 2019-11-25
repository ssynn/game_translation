# coding: utf8

import json
import requests
import random
import hashlib
import time
import urllib

appid = '2123264405'  # 你的appid
appkey = 'qXorYuaiRDs3xSIj'  # 你的密钥
keys = ['app_id', 'nonce_str', 'source', 'target', 'text','time_stamp']


def get_req_sign(data):
    temp = ''
    for key in keys:
        temp+=(key+'='+urllib.parse.quote_plus(data[key])+'&')
    temp+=('app_key='+appkey)
    temp = temp.encode('utf-8')
    return hashlib.md5(temp).hexdigest().upper()

def translate(text, to='zhs', fr='ja'):
    try:
        query = text.encode('utf-8')

        data = {
            'app_id':appid,
            'source':'jp',
            'target':'zh',
            'text':query,
            'time_stamp':str(int(time.time())),
            'nonce_str': str(random.randint(10000000, 90000000))
        }
        data['sign'] = get_req_sign(data)
        # return data['sign']

        url = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_texttranslate'
        res = requests.post(url=url, data=data, timeout=5)
        if res.ok:
            result = json.loads(res.text)['data']['target_text']
            return result
        else:
            derror('error')
            return ''
    except Exception as e:
        print(e)
        pass
    else:
        pass

if __name__ == "__main__":
    text = u"高校一年生の桜庭理沙は平均的な少女。 ある日拾ったカードの力により魔法少女となり戦うお話"
    print(translate(text))