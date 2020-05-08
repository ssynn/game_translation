# 一些常用功能的集合
import os
import re
import json
from Crypto.Cipher import AES  
import chardet
import sqlite3
from pdb import set_trace as int3
from struct import unpack, pack
from baidufanyi import translate as baidu_t
from tencentfanyi import translate as tencent_t


def _init_():
    file_all = os.listdir()
    if 'intermediate_file' not in file_all:
        os.mkdir('intermediate_file')
    if 'output' not in file_all:
        os.mkdir('output')
    if 'input' not in file_all:
        os.mkdir('input')
_init_()


def convert_code(to_code: str):
    file_all = os.listdir('input')
    for f in file_all:
        _data = pf.open_file_b(f'input/{f}')
        _code = chardet.detect(_data)['encoding']
        print(_code, f)
        _data = _data.decode(_code)
        _data = _data.encode(to_code)
        pf.save_file_b(f'input/{f}', _data)


def get_scenario_from_TyranoBuilder(data: list) -> list:
    '''
    TyranoBuilder通用方法
    '''
    jp = []
    for line_t in data:
        if line_t[0] == '[' or not line_t[:-4]:
            continue
        if line_t[-4:-1] in ('[p]', '[r]'):
            jp.append(line_t)
    return jp


def output_translated_scenrio_tyranobuilder(encoding='utf8'):
    '''
    输出翻译后的文件 tyranobuilder 专用
    '''
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        jp_chs = json.loads(f.read())

    file_origial = os.listdir('input')
    failed_text = []

    for file_name in file_origial:
        with open('input/'+file_name, 'r', encoding=encoding) as f:
            data = f.readlines()
        cnt = 0
        for line in data:
            key = line[:-4]
            suffix = line[-4:-1]
            if suffix in ('[p]', '[r]'):
                if key not in jp_chs:
                    failed_text.append(line)
                elif line[0] == '「':
                    data[cnt] = '「' + jp_chs[key][1:-1] + '」'+line[-4:]
                else:
                    data[cnt] = jp_chs[key] + line[-4:]
            cnt += 1

        with open('output/'+file_name, 'w', encoding=encoding) as f:
            for line in data:
                f.write(line)


def get_scenario_from_origin_sakura(data: list):
    '''
    如果遇到[cn 就开始读取
    如果开头为[则跳过
    读取一行判断是否有[en] 或[r]
    有[en]则结束
    '''
    text_all = []
    cnt = 0
    start = False
    for line in data:
        # if line[:3] == '[en' and has_jp(data[cnt-1]):
        #     text_all.append(data[cnt-1])
        # elif line[-4:-1] == '[r]' and has_jp(line[:-4]):
        #     text_all.append(line[:-4]+'\n')
        # elif line[-5:-1] == '[en]' and has_jp(line[:-5]):
        #     text_all.append(line[:-5]+'\n')
        if line[:3] == '[cn':
            start = True
            cnt += 1
            continue
        if line[:4] == '[en]':
            start = False
        if start and line[0] != '[' and line[0] != ';' and has_jp(line):
            line = line.replace('[r]', '')
            if line.count('[en]'):
                start = False
                line = line.replace('[en]', '')
            text_all.append(line)
        cnt += 1
    return text_all


def format_sakura(text: str):
    tags = re.findall(r'\[mruby .*?\]', text)
    for t in tags:
        _p = t.find('text="')
        if _p != -1:
            _value = t[_p+6:-2]
            text = text.replace(t, _value)
    return text


def output_translated_scenrio_sakura(encoding):
    # 输出翻译后的文件
    with open('intermediate_file/jp_chs.json', 'r', encoding='utf8') as f:
        jp_chs = json.loads(f.read())

    record = 0                          # 替换句数
    file_origial = os.listdir('input')  # 需替换的所有文件
    failed_text = []                    # 替换失败的记录

    for file_name in file_origial:
        with open('input/'+file_name, 'r', encoding=encoding) as f:
            data = f.readlines()
        cnt = 0                         # 当前行
        start = False
        for line in data:

            # FIXME 替换目标文本
            if line[:3] == '[cn':
                start = True
                cnt += 1
                continue
            if line[:4] == '[en]':
                start = False
            if start and line[0] != '[' and has_jp(line):
                line = line.replace('[r]', '')
                if line.count('[en]'):
                    start = False
                    line = line.replace('[en]', '')
                key = line[:-1]
                if key in jp_chs:
                    record += 1
                    data[cnt] = data[cnt].replace(key, jp_chs[key])
                else:
                    failed_text.append(key+'\n')
            cnt += 1

        with open('output/'+file_name, 'w', encoding=encoding) as f:
            for line in data:
                f.write(line)
    with open('intermediate_file/failed.txt', 'w', encoding="utf8") as f:
        for line in failed_text:
            f.write(line)
    print('共替换：'+str(record)+"句\n失败："+str(len(failed_text)))


def has_jp(line: str) -> bool:
    '''
    如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
    '''
    for ch in line:
        if ch >= '\u0800' and ch < '\u4e00' and ch not in ('「', '」', '…', '。', '，', '―', '”', '“', '☆', '♪', '、', '※', '‘', '’', '』', '『', '　', '゛', '・', '▁', '★', '〜', '！', '—', '【', '】'):
            return True
    return False


def extract_jp(get_scenario_from_origin, encoding):
    '''
    从input所有文件提取所有日文，保存到intermediate_file/jp_all.text
    '''
    file_origial = os.listdir('input')
    file_origial = list(map(lambda x: 'input/'+x, file_origial))

    jp = []
    for file_name in file_origial:
        with open(file_name, 'r', encoding=encoding, errors='ignore') as f:
            text_t = f.readlines()
        jp += get_scenario_from_origin(text_t)

    with open('intermediate_file/jp_all.txt', 'w', encoding='utf8') as f:
        for line in jp:
            f.write(line)


def get_text_all(encoding):
    '''
    从input所有文件提取所有日文，保存到intermediate_file/jp_all.text
    '''
    file_origial = os.listdir('input')
    file_origial = list(map(lambda x: 'input/'+x, file_origial))

    jp = []
    for file_name in file_origial:
        with open(file_name, 'r', encoding=encoding) as f:
            text_t = f.readlines()
        jp += text_t

    return jp


def get_untranslated():
    '''
    从jp_all中找出没有翻译的句子, 保存到intermediate_file/untranslated.txt
    '''
    encoding = "utf8"
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        text_jp = f.readlines()

    un_t = []
    for line in text_jp:
        if has_jp(line):
            un_t.append(line)

    print(len(un_t))
    with open('intermediate_file/untranslated.txt', 'w', encoding=encoding) as f:
        for line in un_t:
            f.write(line)


def create_dict(extract_jp_line):
    '''
    jp_all.txt文本建立空value字典，保存到 jp_chs.json
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        text_jp = f.readlines()
    try:
        with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
            j_c = json.loads(f.read())
    except Exception as e:
        print('第一次建立字典！')
        j_c = dict()
    print('总共', len(text_jp), '条')
    cnt = 0
    for line in text_jp:
        # 去掉每行多余的符号
        _t = extract_jp_line(line)
        if _t not in j_c:
            j_c[_t] = ''
            cnt += 1
    print('添加关键字：', cnt, '条')
    with open('intermediate_file/jp_chs.json', 'w', encoding=encoding) as f:
        f.write(json.dumps(j_c, ensure_ascii=False))


def check_dict():
    '''
    打开jp-chs.json文件检查
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        js = json.loads(f.read())
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        text_jp = f.readlines()
    cnt = 0
    for key in js:
        if not js[key]:
            cnt += 1
    print(list(js.keys())[:10])
    print('需要翻译：', len(list(js.keys())), '条')
    print('剩余翻译：', cnt, '条')
    print('共有日文：', len(text_jp), '条， 应翻译：', len(set(text_jp)), '条')


def new_translate(text, db=None):
    '''
    在提交给在线翻译前先在本地数据库检查是否存在已经翻译的词条
    '''
    # ans = translate_local(text, db)
    ans = ''
    if not ans:
        ans = tencent_t(text)
        if not ans or ans.count('不知道怎么说'):
            ans = baidu_t(text)
        if ans:
            to_database(text, ans, db)
    return ans


def _translate(text: str, db=None, delete_func=None) -> str:
    '''
    首先删除不必要的符号
    切割语句
    判断是否有日文
    逐个翻译
    '''
    if delete_func is not None:
        text = delete_func(text)
    _text_list = split_line(text)
    for _text in _text_list:
        if _text and has_jp(_text):
            # 补上标点,以提高翻译质量
            pun_positon = text.find(_text)+len(_text)
            if pun_positon < len(text):
                pun = text[pun_positon]
                if pun in ('？', '！', '。'):
                    _text += pun
            # 交给机器翻译
            ans = new_translate(_text, db)
            if ans:
                # 去掉翻译结果里的标点
                if ans[-1] in ('？', '！', '。', '!', '?', '.'):
                    ans = ans[:-1]
                if _text[-1] in ('？', '！', '。'):
                    _text = _text[:-1]

                text = text.replace(_text, ans, 1)
                # print(_text, ans, text)
            else:
                print(_text_list)
                print(_text, ans)
                return ''
    return text


def translate(delete_func=None, interval=30):
    '''
    把字典翻译
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        data = json.loads(f.read())

    need_translated = len(list(data.keys()))
    cnt = 0
    cnt_last = 0
    failed_list = []
    conn = sqlite3.connect('data/data.db')
    for key in data:
        if not data[key] or key == data[key] or has_jp(data[key]):
            ans = _translate(key, conn, delete_func)
            if ans:
                data[key] = ans
            else:
                failed_list.append(key)
        cnt += 1
        if cnt - cnt_last == interval:
            cnt_last = cnt
            print(cnt, '/', need_translated)
            with open('intermediate_file/jp_chs.json', 'w', encoding=encoding) as f:
                f.write(json.dumps(data, ensure_ascii=False))
    else:
        conn.commit()
        conn.close()
        with open('intermediate_file/jp_chs.json', 'w', encoding=encoding) as f:
            f.write(json.dumps(data, ensure_ascii=False))
        with open('intermediate_file/failed.txt', 'w', encoding=encoding) as f:
            for line in failed_list:
                f.write(line+'\n')
        print('失败：', len(failed_list), '个！')


def check_dict_untranslated():
    '''
    检查字典中是否有没翻译的日文，如value为空或和key相等或含有日文
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        data = json.loads(f.read())
    cnt = 0
    untranslated = []
    for key in data:
        if data[key] == '' or has_jp(data[key]):
            cnt += 1
            untranslated.append(key)
            print(key+' '+data[key])
    with open('intermediate_file/untranslated.txt', 'w', encoding=encoding) as f:
        for line in untranslated:
            f.write(line+' '+data[line]+'\n')
    print(cnt)


def format_text(source_text: str, target_text: str):
    '''
    整理翻译后的字符串，规则如下：
    1、原文开头是否有日文空格
    2、原文开头是否有('（', '『', '「')
    3、原文末尾是否有('）', '」', '』')
    4、原文末尾是否有句号
    '''
    if source_text[0] == '　' and target_text[0] != '　':
        target_text = '　' + target_text

    if source_text[0] in ('（', '『', '「') and target_text[0] in ('“', '('):
        target_text = source_text[0] + target_text[1:]
    elif source_text[0] in ('（', '『', '「') and target_text[0] not in ('“', '('):
        target_text = source_text[0] + target_text

    if source_text[-1] in ('）', '」', '』') and target_text[-1] in ('“', '”', ')'):
        target_text = target_text[:-1] + source_text[-1]
    elif source_text[-1] in ('）', '」', '』') and target_text[-1] not in ('“', '”', ')'):
        target_text = target_text + source_text[-1]

    if source_text[-1] == '。' and target_text[-1] == '.':
        target_text = target_text[:-1] + '。'

    return target_text


def create_contrast():
    '''
    根据jp_all构建对比文件
    '''
    encoding = 'utf8'
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        jp_all = f.readlines()
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        data = json.loads(f.read())
    cnt = 0
    with open('intermediate_file/contrast.txt', 'w', encoding=encoding) as f:
        for line in jp_all:
            key = line[:-1]
            if key in data:
                f.write(key+' ' + data[key]+'\n')


def split_line(text: str) -> list:
    '''
    用正则表达式切割文本，遇到'「', '」', '…', '。', '，', '―', '”', '“', '☆', '♪', '、', '‘', '’', '』', '『', '　', 
    '''
    split_str = r'\[.*?\]|<.+?>|[a-z0-9A-Z]|,|\\n|\||「|」|…+|。|@|』|『|　|―+|）|（|・|？|！|★|☆|♪|※|\\|“|”|"|\]|\[|\/|\;|【|】'
    _text_list = re.split(split_str, text)
    _ans = []
    for i in _text_list:
        if i:
            _ans.append(i)
    return _ans


def delete_label(text: str) -> str:
    '''
    删除文本里面的标签
    '''
    label_str = r'<.+?>'
    return re.sub(label_str, '', text)


def open_json(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.loads(f.read())


def save_json(path, data):
    with open(path, 'w', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False))


def open_file(path, encoding='utf8'):
    if encoding == '':
        with open(path, 'rb') as f:
            return f.read()
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def save_file(path, data):
    with open(path, 'w', encoding='utf8') as f:
        f.write(data)


def open_file_b(path):
    with open(path, 'rb') as f:
        return f.read()


def save_file_b(path, data):
    with open(path, 'wb') as f:
        f.write(data)


def to_database(jp: str, ch: str, db=None):
    conn = db if db else sqlite3.connect('data/data.db')
    c = conn.cursor()
    ans = False
    try:
        if jp and ch:
            c.execute(f"insert into translate values('{jp}','{ch}')")
            conn.commit()
            ans = True
    except Exception as e:
        pass
    finally:
        if not db:
            conn.close()
        return ans


def translate_local(jp: str, db=None):
    conn = db if db else sqlite3.connect('data/data.db')
    c = conn.cursor()
    res = ''
    try:
        ans = c.execute(f'select ch from translate where jp="{jp}"').fetchall()
        if ans:
            res, = ans[0]
    except Exception as e:
        pass
    finally:
        if not db:
            conn.close()
        return res


def create_database():
    conn = sqlite3.connect('data/data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE translate( 
        jp text PRIMARY KEY not null,
        ch text not null)
    ''')
    conn.commit()
    conn.close()


def create_failed_dict():
    data = open_file('intermediate_file/failed.txt').splitlines()
    failed_dict = dict()
    for line in data:
        line = split_line(line)
        for item in line:
            if has_jp(item):
                failed_dict[item] = ''
    save_json('intermediate_file/failed.json', failed_dict)


def replace_all(find_text, encoding, output_encoding):
    # 输出翻译后的文件
    jp_chs = open_json('intermediate_file/jp_chs.json')

    record = 0                          # 替换句数
    file_origial = os.listdir('input')  # 需替换的所有文件
    failed_text = []                    # 替换失败的记录

    for file_name in file_origial:
        with open('input/'+file_name, 'r', encoding=encoding) as f:
            data = f.readlines()
        cnt = 0                         # 当前行

        record += find_text(data, failed_text, jp_chs)

        with open('output/'+file_name, 'w', encoding=output_encoding, errors='ignore') as f:
            for line in data:
                f.write(line)
    with open('intermediate_file/failed.txt', 'w', encoding="utf8") as f:
        for line in failed_text:
            f.write(line)
    print('共替换：'+str(record)+"句\n失败："+str(len(failed_text)))


def break_line():
    # 给名字添加换行
    jp = pf.open_file('intermediate_file/jp_all.txt').splitlines()
    _name = set()
    for line in jp:
        if line[0] not in ('　', '「', '（'):
            _p = 0
            for i, ch in enumerate(line):
                if ch in ('（', '「'):
                    _p = i
                    break
            if _p < 5 and _p:
                _name.add(line[:_p])
    jp_chs = pf.open_json('intermediate_file/jp_chs.json')
    for key in jp_chs:
        line = jp_chs[key]
        for n in _name:
            if line.find(n) == 0:
                line = line.replace(n, n+'[r]')
                jp_chs[key] = line
                break
    pf.save_json('intermediate_file/jp_chs.json', jp_chs)


def to_bytes(a: int, _len: int) -> int:
    return int.to_bytes(a, _len, byteorder='little')


def from_bytes(a: bytes):
    return int.from_bytes(a, byteorder='little')


def byte_add(*args):
    ans = 0
    for i in args:
        ans += i
    return ans & 0xff


def delete_zero(name: bytes, encoding='utf8'):
    while not name[-1]:
        name = name[:-1]
    return name.decode(encoding)


class LzssCompressor():

    def __init__(self):
        self.frame_size = 0x1000
        self.frame_fill = 0
        self.frame_init_pos = 0xfee
    
    def get_byte(self, data):
        _t = data[0]
        data = data[1:]
        return _t
    
    def decompres(self, m_input:bytes, out_length:int):
        m_output = bytearray(b'\x00'*out_length)
        dst = 0
        frame = bytearray(b'\x00'*self.frame_size)
        frame_pos = self.frame_init_pos
        frame_mask = self.frame_size - 1
        remaining = len(m_input)
        while remaining > 0:
            ctl = self.get_byte(m_input)
            remaining -= 1
            bit = 1
            while remaining > 0 and bit != 0x100:
                if dst >= out_length:
                    return m_output
                if 0 != (ctl & bit):
                    b = self.get_byte(m_input)
                    remaining -= 1
                    frame[frame_pos] = b
                    frame_pos += 1
                    frame_pos &= frame_mask
                    m_output[dst] = b
                    dst += 1
                else:
                    if remaining < 2:
                        return m_output
                    lo = self.get_byte(m_input)
                    hi = self.get_byte(m_input)
                    remaining -= 2
                    offset = (hi & 0xf0) << 4 | lo
                    count = 3 + (hi & 0xf)
                    while count != 0:
                        if dst >= out_length:
                            break
                        v = frame[offset]
                        offset += 1
                        offset &= frame_mask
                        frame[frame_pos] = v
                        frame_pos += 1
                        frame_pos &= frame_mask
                        m_output[dst] = v
                        dst += 1
                        count -= 1
                bit <<= 1
        return m_input
        

class Majiro():
    '''
    解密Mjo引擎脚本，转换引擎脚本到明文
    '''
    class ByteIO:
        '''
        tell() 输出当前位置
        readu32()
        readu16()
        read(int)

        '''

        def __init__(self, data: bytes):
            self._stream = bytearray(data)
            self._pos = 0

        def tell(self) -> int:
            return self._pos

        def readu32(self) -> int:
            ans = self._stream[self._pos:self._pos+4]
            self._pos += 4
            return int.from_bytes(ans, byteorder='little')

        def readu16(self) -> int:
            ans = self._stream[self._pos:self._pos+2]
            self._pos += 2
            return int.from_bytes(ans, byteorder='little')

        def read(self, count: int) -> str:
            ans = self._stream[self._pos:self._pos+count]
            self._pos += count
            return ans.decode('cp932')

        def seek(self, pos: int):
            self._pos = pos

        def __len__(self):
            return len(self._stream)

    class MjoParser():
        'Parse a Mjo script.'

        def __init__(self, mjo):
            self.text = []
            self.code = 0
            self.hdr = [mjo._stream[0:0x10]]
            self.hdr += unpack('III', (mjo._stream[0x10:0x1c]))
            mjo.seek(0x1c)
            self.fidx = []
            for i in range(self.hdr[3]):
                self.fidx.append((mjo.readu32(), mjo.readu32()))
            size = mjo.readu32()
            print(size, mjo.tell(), self.hdr, self.fidx)
            self.vmcode = Majiro.ByteIO(
                mjo._stream[mjo.tell():mjo.tell()+size])
            self.XorDec(self.vmcode)
            # self.decoded = self.

        def XorDec(self, bf):
            for i in range(len(bf)):
                bf._stream[i] ^= aka2key[i & 0x3ff]

        def ru8(self):
            return self.vmcode.readu8()

        def ru16(self):
            return self.vmcode.readu16()

        def ru32(self):
            return self.vmcode.readu32()

        # 下面都是负责把函数对应到文本

        def p800(self):
            self.text[-1] += 'pushInt '+'%d' % self.vmcode.readu32()

        def p801(self):
            slen = self.vmcode.readu16()
            s = self.vmcode.read(slen)
            self.text[-1] += 'pushStr "'+s.rstrip('\0')+'"'

        def p802(self):
            p1 = self.vmcode.readu16()
            p2 = self.vmcode.readu32()
            p3 = self.vmcode.readu16()
            self.text[-1] += 'pushCopy '+'(%d,%08X,%d)' % (p1, p2, p3)

        def p803(self):
            self.text[-1] += 'pushFloat '+'%X' % self.vmcode.readu32()

        def p80f(self):
            p1 = self.ru32()
            p2 = self.ru32()
            p3 = self.ru16()
            self.text[-1] += 'OP80F '+'(%08X, %X, %d)' % (p1, p2, p3)

        def p810(self):
            self.text[-1] += 'OP810 ' + \
                '(%08X, %X, %d)' % (self.ru32(), self.ru32(), self.ru16())

        def p829(self):
            cnt = self.ru16()
            self.text[-1] += 'pushStackRepeat ' + \
                ' '.join(['%d' % self.ru8() for i in range(cnt)])

        def p82b(self):
            self.text[-1] += 'return'

        def p82c(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jmp '+'%08X' % dest

        def p82d(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jnz '+'%08X' % dest

        def p82e(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jz '+'%08X' % dest

        def p82f(self):
            self.text[-1] += 'pop'

        def p830(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jmp2 '+'%08X' % dest

        def p831(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jne '+'%08X' % dest

        def p832(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jbeC '+'%08X' % dest

        def p833(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jaeC '+'%08X' % dest

        def p834(self):
            self.text[-1] += 'Call '+'(%08X, %d)' % (self.ru32(), self.ru16())

        def p835(self):
            self.text[-1] += 'Callp '+'(%08X, %d)' % (self.ru32(), self.ru16())

        def p836(self):
            self.text[-1] += 'OP836 '+self.vmcode.read(self.ru16())

        def p837(self):
            self.text[-1] += 'OP837 ' + \
                '(%08X, %08X)' % (self.ru32(), self.ru32())

        def p838(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jbeUnk '+'%08X' % dest

        def p839(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jaeUnk '+'%08X' % dest

        def p83a(self):
            self.text[-1] += 'Line: '+'%d' % self.ru16()

        def p83b(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jmpSel0 '+'%08X' % dest

        def p83c(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jmpSel2 '+'%08X' % dest

        def p83d(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jmpSel1 '+'%08X' % dest

        def p83e(self):
            self.text[-1] += 'SetStack0'

        def p83f(self):
            self.text[-1] += 'Int2Float'

        def p840(self):
            self.text[-1] += 'CatString "' + \
                self.vmcode.read(self.ru16()).rstrip('\0')+'"'

        def p841(self):
            self.text[-1] += 'ProcessString'

        def p842(self):
            self.text[-1] += 'CtrlStr ' + \
                self.vmcode.read(self.ru16()).rstrip('\0')

        def p843(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'jmpSelX '+'%08X' % dest

        def p844(self):
            self.text[-1] += 'ClearJumpTbl'

        def p845(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'SetJmpAddr3 '+'%08X' % dest

        def p846(self):
            self.text[-1] += 'OP846'

        def p847(self):
            dest = self.ru32()+self.vmcode.tell()+4
            self.text[-1] += 'SetJmpAddr4 '+'%08X' % dest

        def p850(self):
            cnt = self.ru16()
            addrs = []
            sta = self.vmcode.tell()+cnt*4
            for i in range(cnt):
                addrs.append('%08X' % (self.ru32()+sta))
            self.text[-1] += 'JmpInTbl '+' '.join(addrs)

        code800 = [
            p800, p801, p802, p803, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, p80f,
            p810, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, p829, 0, p82b, p82c, p82d, p82e, p82f,
            p830, p831, p832, p833, p834, p835, p836, p837, p838, p839, p83a, p83b, p83c, p83d, p83e, p83f,
            p840, p841, p842, p843, p844, p845, p846, p847, 0, 0, 0, 0, 0, 0, 0, 0,
            p850
        ]

        code10X = {
            0x100: 'Mul', 0x101: 'Fmul', 0x108: 'Div', 0x109: 'Fdiv', 0x110: 'Mod', 0x118: 'Add',
            0x119: 'Fadd', 0x11a: 'StrAdd', 0x120: 'Sub', 0x121: 'Fsub', 0x128: 'Sar', 0x130: 'Shl',
            0x138: 'IsLE', 0x139: 'IsFLE', 0x13a: 'IsLEStr', 0x140: 'IsL', 141: 'IsFL', 0x142: 'IsLStr',
            0x148: 'IsGE', 0x149: 'IsFGE', 0x14a: 'IsGEStr', 0x150: 'IsG', 0x151: 'IsFG', 0x152: 'IsGStr',
            0x158: 'IsE', 0x159: 'IsFE', 0x15a: 'IsEStr', 0x15b: 'IsE', 0x15c: 'IsE', 0x15d: 'IsE',
            0x160: 'IsNE', 0x161: 'IsFNE', 0x162: 'IsNEStr', 0x163: 'IsNE', 0x164: 'IsNE', 0x165: 'IsNE',
            0x168: 'Xor', 0x170: 'CondAnd', 0x178: 'CondOr', 0x180: 'And', 0x188: 'Or', 0x190: 'IsZero',
            0x191: 'Nop', 0x198: 'Not', 0x1a0: 'Neg', 0x1a8: 'Nop', 0x1a9: 'Nop'
        }

        code1BX = {
            0x1b8: 'Mul', 0x1b9: 'Fmul', 0x1c0: 'Div', 0x1c1: 'Fdiv', 0x1c8: 'Mod', 0x1d0: 'Add',
            0x1d1: 'Fadd', 0x1d2: 'StrAdd', 0x1d8: 'Sub', 0x1d9: 'Fsub', 0x1e0: 'Shl', 0x1e8: 'Sar',
            0x1f0: 'And', 0x1f8: 'Xor', 0x200: 'Or'
        }

        code27X = {
            0x270: 'Mov', 0x271: 'Mov', 0x272: 'MovS', 0x278: 'Mul', 0x279: 'Fmul', 0x280: 'Div',
            0x281: 'Fdiv', 0x288: 'Mod', 0x290: 'Add', 0x291: 'Mov', 0x292: 'StrAdd', 0x298: 'Sub',
            0x299: 'Fsub', 0x2a0: 'Shl', 0x2a8: 'Sar', 0x2b0: 'And', 0x2b8: 'Xor', 0x2c0: 'Or'
        }

        def p10X(self):
            self.text[-1] += 'St'+self.code10X[self.code]

        def p1BX(self):
            self.text[-1] += 'Gbl'+self.code1BX[self.code] + \
                ' (%d, %08X, %d)' % (self.ru16(), self.ru32(), self.ru16())

        def p21X(self):
            newcode = self.code-(0x218-0x1b8)
            self.text[-1] += 'Gblp'+self.code1BX[newcode] + \
                ' (%d, %08X, %d)' % (self.ru16(), self.ru32(), self.ru16())

        def p27X(self):
            self.text[-1] += 'Ar'+self.code1BX[self.code] + \
                ' (%d, %08X, %d)' % (self.ru16(), self.ru32(), self.ru16())

        def p2DX(self):
            newcode = self.code-(0x2d0-0x270)
            self.text[-1] += 'Arp'+self.code1BX[newcode] + \
                ' (%d, %08X, %d)' % (self.ru16(), self.ru32(), self.ru16())

        def pLen8(self):
            self.text[-1] += 'OP%X ' % self.code + \
                '(%d, %08X, %d)' % (self.ru16(), self.ru32(), self.ru16())

        def Parse(self):
            while self.vmcode.tell() < len(self.vmcode):
                self.text.append('%08X\t' % self.vmcode.tell())
                self.code = self.vmcode.readu16()
                if self.code >= 0x800 and self.code <= 0x850:
                    func = self.code800[self.code-0x800]
                    if func == 0:
                        int3()
                    func(self)
                elif self.code <= 0x1a9 and self.code >= 0x100:
                    self.p10X()
                elif self.code >= 0x1b8 and self.code <= 0x200:
                    self.p1BX()
                elif self.code >= 0x218 and self.code <= 0x260:
                    self.p21X()
                elif self.code >= 0x270 and self.code <= 0x2c0:
                    self.p27X()
                elif self.code >= 0x2d0 and self.code <= 0x320:
                    self.p2DX()
                elif self.code <= 0x850:
                    self.pLen8()
                else:
                    int3()
            newt = [str(s) for s in self.text]
            return '\r\n'.join(newt)


class XFL():
    '''
    提取gsc文件内的文本和把翻译后的文本插入gsc文件
    '''
    def format_xfl(text: str):
        '''
        翻译用
        \[.*?\]|<.+?>|,|\\n|　|―+|\\|"|\]|\[|\/|\;|[a-z0-9A-Z]
        '''
        patt = r'\[.*?\]|<.+?>|\|'
        return re.sub(patt, '', text)

    def extract_gsc(path='input'):
        jp_all = []
        file_all = os.listdir(path)
        for f in file_all:
            _data = open_file_b(f'{path}/{f}')
            _data = bytearray(_data)
            _l_header = int.from_bytes(_data[4:8], byteorder='little')
            _l_unk = int.from_bytes(_data[8:12], byteorder='little')
            _l_offset = int.from_bytes(_data[12:16], byteorder='little')
            _l_str = int.from_bytes(_data[16:20], byteorder='little')

            cnt_offset = int(_l_offset/4)
            offset_p = _l_header + _l_unk
            str_p = offset_p + _l_offset

            for i in range(cnt_offset):
                _p = int.from_bytes(
                    _data[offset_p+i*4:offset_p+i*4+4], byteorder='little')
                _p += str_p

                _stack = b''
                while _data[_p]:
                    _stack += _data[_p:_p+1]
                    _p += 1
                _stack = _stack.decode('cp932')
                if len(_stack) and _stack[0] not in 'gR9T':
                    jp_all.append(_stack)

        save_file('intermediate_file/jp_all.txt', '\n'.join(jp_all))

    def output_gsc(path='input', dict='intermediate_file/jp_chs.json'):
        jp_all = []
        file_all = os.listdir(path)
        jp_chs = open_json(dict)
        for f in file_all:
            _data = open_file_b(f'{path}/{f}')
            _data = bytearray(_data)
            _l_header = int.from_bytes(_data[4:8], byteorder='little')
            _l_unk = int.from_bytes(_data[8:12], byteorder='little')
            _l_offset = int.from_bytes(_data[12:16], byteorder='little')
            _l_str = int.from_bytes(_data[16:20], byteorder='little')

            offset_all = []
            str_all = []

            cnt_offset = int(_l_offset/4)
            offset_p = _l_header + _l_unk
            str_p = offset_p + _l_offset

            for i in range(cnt_offset):
                _p = int.from_bytes(
                    _data[offset_p+i*4:offset_p+i*4+4], byteorder='little')
                offset_all.append(_p)

            for i in offset_all:
                _p = i
                while _data[str_p+_p]:
                    _p += 1
                _str = _data[str_p+i:str_p+_p].decode('cp932')
                if _str in jp_chs and jp_chs[_str]:
                    str_all.append(jp_chs[_str].encode(
                        'gbk', errors='ignore')+b'\x00')
                else:
                    str_all.append(_str.encode('gbk', errors='ignore')+b'\x00')

            offset = 0
            for i in range(len(offset_all)):
                offset_all[i] = int.to_bytes(
                    offset, length=4, byteorder='little')
                offset += len(str_all[i])

            _new_str = b''.join(str_all)
            _new_str_len = len(_new_str)

            _data[offset_p:offset_p+_l_offset] = b''.join(offset_all)
            _data[str_p:str_p+_l_str] = _new_str

            _data[16:20] = int.to_bytes(_new_str_len, 4, byteorder='little')
            _data[:4] = int.to_bytes(len(_data), 4, byteorder='little')

            if not os.path.exists('output'):
                os.mkdir('output')
            save_file_b(f'output/{f}', _data)


class LIVEMAKER():
    '''
    提取LIVAMEKER的文本，处理字典提高VNR命中率
    '''
    def get_text_from_lsb():
        for f in os.listdir('input'):
            os.system(
                f'lmlsb dump -m lines input/{f} -o intermediate_file/{f}')

    def dump_lsb(path='input'):
        file_all = os.listdir(path)
        for f in file_all:
            os.system(
                f'lmlsb dump -m text {path}/{f} -o intermediate_file/{f}')

    def optimize_livemaker_dict():
        jp_chs = pf.open_json('intermediate_file/jp_chs copy.json')
        jp_all = pf.open_file('intermediate_file/jp_all.txt').splitlines()
        ans = dict()
        stack_key = ''
        stack_value = ''
        for line in jp_all:
            if line[-1] != '>':
                ans[line] = jp_chs[line]
                continue
            stack_key += line
            stack_value += jp_chs[line]
            stack_key = stack_key.replace('<PG>', '')
            stack_key = stack_key.replace('<BR>', '')
            stack_key = stack_key.replace('　', '')
            stack_value = stack_value.replace('<PG>', '')
            stack_value = stack_value.replace('<BR>', '')
            ans[stack_key] = stack_value
            if line[-4:] == '<PG>':
                stack_key = ''
                stack_value = ''
        pf.save_json('intermediate_file/jp_chs.json', ans)

    def make_livemaker_dict():
        jp_all = pf.open_file('intermediate_file/jp_all.txt').splitlines()
        ans = dict()
        stack_key = ''
        stack_value = ''
        for line in jp_all:
            stack_key += line
            stack_key = stack_key.replace('<PG>', '')
            stack_key = stack_key.replace('<BR>', '')
            stack_key = stack_key.replace('　', '')
            ans[stack_key] = ''

            if line[-4:] == '<PG>':
                stack_key = ''
                stack_value = ''

            line = line.replace('<PG>', '')
            line = line.replace('<BR>', '')
            line = line.replace('　', '')
            ans[line] = ''
        pf.save_json('intermediate_file/jp_chs.json', ans)


class YU_RIS():
    '''
    解密ybn，提取文本，插入文本，加密ybn
    '''
    def decode_473(file_name):
        dec_tbl2 = [0xd3, 0x6f, 0xac, 0x96]
        with open(file_name, 'rb') as f:
            data = f.read()
        header = YU_RIS.create_head_ystb(data)
        # print(header)
        if not header or header['magic_8*4'] != 'YSTB':
            print('未知文件：', file_name)
            return None

        header_byte = data[:32]
        data = list(data)

        data1_pointer = 32
        for i in range(header['data1_length_32']):
            ch = data[data1_pointer+i]
            ch ^= dec_tbl2[i & 3]
            data[data1_pointer+i] = ch.to_bytes(1, 'little')

        data2_pointer = 32 + header['data1_length_32']
        for i in range(header['data2_length_32']):
            ch = data[data2_pointer+i]
            ch ^= dec_tbl2[i & 3]
            data[data2_pointer+i] = ch.to_bytes(1, 'little')

        data3_pointer = data2_pointer + header['data2_length_32']
        for i in range(header['data3_length_32']):
            ch = data[data3_pointer+i]
            ch ^= dec_tbl2[i & 3]
            data[data3_pointer+i] = ch.to_bytes(1, 'little')

        data4_pointer = data3_pointer + header['data3_length_32']
        for i in range(header['data4_length_32']):
            ch = data[data4_pointer+i]
            ch ^= dec_tbl2[i & 3]
            data[data4_pointer+i] = ch.to_bytes(1, 'little')

        data = header_byte + b''.join(data[32:])

        return data, header

    def create_head_ystb(data: bytes):
        header = {
            'magic_8*4': data[:4].decode(),
            'version_32': 0,
            'data1_length_div_4_32': 0,
            'data1_length_32': 0,
            'data2_length_32': 0,
            'data3_length_32': 0,
            'data4_length_32': 0,
            'reserved_32': 0
        }
        if header['magic_8*4'] != 'YSTB':
            return None
        cnt = 1
        for key in header:
            if key == 'magic_8*4':
                continue
            header[key] = int.from_bytes(
                data[cnt*4:cnt*4+4], byteorder='little')
            cnt += 1
        return header

    def create_ystb473_method_t(data: bytes):
        return {
            'code_8': data[0],
            'args_8': data[1],
            'un_8*2': data[2:]
        }

    def create_ystb473_parameter_t(data: bytes):
        return {
            'un_32': int.from_bytes(data[:4], byteorder='little'),
            'char_count_32': int.from_bytes(data[4:8], byteorder='little'),
            'char_offset_32': int.from_bytes(data[8:12], byteorder='little')
        }

    def cut_ybn(data: bytes, header=None):
        '''
        把ybn切割为：{
            'header':data[:32],
            'methord':data[p_m:p_p],
            'parameter':data[p_p:p_s],
            'str':data[p_s:p_u],
            'un':data[p_u:]
        }
        '''
        if not header:
            header = YU_RIS.create_head_ystb(data)
        p_m = 32
        p_p = 32+header['data1_length_32']
        p_s = p_p + header['data2_length_32']
        p_u = p_s + header['data3_length_32']
        body = {
            'header': data[:32],
            'methord': data[p_m:p_p],
            'parameter': data[p_p:p_s],
            'str': data[p_s:p_u],
            'un': data[p_u:]
        }
        return body

    def cut_by_len(data: bytes, _len: int, create):
        '''
        切割区域并构造字典式结构体
        '''
        __len = int(len(data)/_len)
        ans = []
        for i in range(__len):
            _t = create(data[i*_len:i*_len+_len])
            ans.append(_t)
        return ans

    def _extract_string(data: bytes):
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <= '\u9fa5'):
                    return True
            return False
        ans = ''
        try:
            _str = data.decode('cp932')

            if not _has_jp(_str):
                raise Exception('Not jp')
            if _str[0] in ("M", 'H', 'V', 'B', 'F', 'L', 'I', 'W', 'v'):
                raise Exception('Not jp')
            ans = _str
        except Exception as e:
            pass
        finally:
            return ans

    def ybn_script_export_string(data: bytes, extract=None):
        '''
        传入ybn的byte串，和提取方法，摘取字符串，返回[str,str...]
        '''
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <= '\u9fa5'):
                    return True
            return False

        def _extract_button(data: bytes):
            '''
            抽取 M开头且带引号且含日文的字符串
            '''
            ans = ''
            p = -1
            try:
                if data[0] != 77 and data.count(0x22) != 2:
                    ans = ''
                    raise Exception()
                _len = int.from_bytes(data[1:3], byteorder='little')
                _str = data[4:-1].decode('shiftjis')
                if _len and _has_jp(_str) and _str[0] not in '■◆':
                    ans = _str
            except Exception as e:
                ans = ''
            finally:
                return ans

        if not data:
            return
        header = YU_RIS.create_head_ystb(data)
        if not header:
            return None

        body = YU_RIS.cut_ybn(data, header)
        all_methord = YU_RIS.cut_by_len(
            body['methord'], 4, YU_RIS.create_ystb473_method_t)
        all_parameter = YU_RIS.cut_by_len(
            body['parameter'], 12, YU_RIS.create_ystb473_parameter_t)
        methord_code = []
        for i in all_methord:
            methord_code += [i['code_8'] for x in range(i['args_8'])]

        ans = []
        for i in range(len(all_parameter)):
            # 提取字符串
            _p = all_parameter[i]['char_offset_32']
            all_parameter[i]['str'] = body['str'][_p: _p +
                                                  all_parameter[i]['char_count_32']]
            _str = extract(all_parameter[i]['str'])
            if methord_code[i] == 91:
                ans.append(_str)
            _str = _extract_button(all_parameter[i]['str'])
            if _str and methord_code[i] == 29:
                ans.append(_str)

        return ans

    def create_parameter_bytes(para: list):
        ans = b''
        for i in para:
            ans += int.to_bytes(i['un_32'], 4, byteorder='little')
            ans += int.to_bytes(i['char_count_32'], 4, byteorder='little')
            ans += int.to_bytes(i['char_offset_32'], 4, byteorder='little')
        return ans

    def can_decoded_gb2312(data: str):
        ans = True
        try:
            for i in data:
                i.encode('gb2312')
        except Exception as e:
            ans = False
        finally:
            return ans

    def replace_string(data: bytes, jp_chs: dict):
        '''
        修改对应位置数据
        修改表头数据
        返回(ans:bytes, cnt:int, failed:list)

        首先把所有的字符串都放入parameter字典
        把函数类型也放入
        替换parameter字典内容，使用gb2312编码
        修改字典内的 count 和 offset
        修改head里字符串的长度
        链接二进制串
        '''
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <= '\u9fa5'):
                    return True
            return False

        def _extract_button(data: bytes):
            '''
            抽取 M开头且带引号且含日文的字符串
            '''
            ans = ''
            p = -1
            try:
                if data[0] != 77 and data.count(0x22) != 2:
                    ans = ''
                    raise Exception()
                _len = int.from_bytes(data[1:3], byteorder='little')
                _str = data[4:-1].decode('shiftjis')
                if _len and _has_jp(_str) and _str[0] not in '■◆':
                    ans = _str
            except Exception as e:
                ans = ''
            finally:
                return ans

        header = YU_RIS.create_head_ystb(data)
        if not data or not header:
            return None, 0, []

        body = YU_RIS.cut_ybn(data, header)
        all_methord = YU_RIS.cut_by_len(
            body['methord'], 4, YU_RIS.create_ystb473_method_t)
        all_parameter = YU_RIS.cut_by_len(
            body['parameter'], 12, YU_RIS.create_ystb473_parameter_t)
        methord_code = []
        for i in all_methord:
            methord_code += [i['code_8'] for x in range(i['args_8'])]

        failed = []
        cnt = 0

        for i in range(len(all_parameter)):
            _para = all_parameter[i]
            _para['index'] = i
            _p_str = _para['char_offset_32']
            _para['str'] = (body['str'][_p_str:_p_str+_para['char_count_32']])
            if len(_para['str']) < _para['char_count_32']:
                _cnt = _para['char_count_32'] - len(_para['str'])
                _para['str'] += b'\x00' * _cnt
            # _para['char_count_32'] = len(_para['str'])
            if methord_code[i] == 91 and _para['un_32'] == 0:
                _key = _para['str'].decode('cp932')
                if _key in jp_chs and jp_chs[_key]:
                    _para['str'] = jp_chs[_key].encode('gbk', errors='ignore')
                    _para['char_count_32'] = len(_para['str'])
                    cnt += 1
                else:
                    failed.append(_key)
            _key = _extract_button(_para['str'])
            if _key and methord_code[i] == 29:
                # print(_key, key in jp_chs)
                if _key in jp_chs and jp_chs[_key]:
                    _str = b'\x22' + \
                        jp_chs[_key].encode('gbk', errors='ignore')+b'\x22'
                    _para['str'] = b'\x4d' + \
                        int.to_bytes(len(_str), 2, byteorder='little')
                    _para['str'] += _str
                    _para['char_count_32'] = len(_para['str'])
                    # print(_para['str'])
                    cnt += 1
                else:
                    failed.append(_key)

        # # 没有替换则直接返回
        # if cnt == 0 and len(failed) == 0:
        #     return (data, cnt, failed)

        # 对齐参数, 需要排序
        # print(header)
        if len(all_parameter):
            all_parameter = sorted(
                all_parameter, key=lambda x: x['char_offset_32'])
            body['str'] = all_parameter[0]['str']
            for i in range(1, len(all_parameter)):
                _para_now = all_parameter[i]
                _para_pre = all_parameter[i-1]
                _para_now['char_offset_32'] = _para_pre['char_offset_32'] + \
                    _para_pre['char_count_32']
                body['str'] += all_parameter[i]['str']
            all_parameter = sorted(all_parameter, key=lambda x: x['index'])

        # 链接字符串
        body['header'] = bytearray(body['header'])
        body['header'][20:24] = int.to_bytes(
            len(body['str']), length=4, byteorder='little')

        body['parameter'] = YU_RIS.create_parameter_bytes(all_parameter)
        ans = body['header'] + body['methord'] + \
            body['parameter'] + body['str'] + body['un']

        # print(cnt, len(failed))
        # 检查parameter 和 字符串长度
        for i in all_parameter:
            _p_str = i['char_offset_32']
            if bytes(i['str']) != body['str'][_p_str:_p_str+i['char_count_32']]:
                print(header)
                print(len(all_parameter), len(
                    body['str']), header['data3_length_32'])
                print(i)
                print(bytes(i['str']))
                print(body['str'][_p_str:_p_str+i['char_count_32']])
                raise Exception('根本没拼对！！')
        _body = YU_RIS.cut_ybn(ans)
        _header = YU_RIS.create_head_ystb(ans)
        if _header['data3_length_32'] != len(body['str']):
            print(header)
            print(len(all_parameter), len(
                body['str']), header['data3_length_32'])
            print(_header['data3_length_32'], len(body['str']))
            raise Exception('头部字符串长度')

        return (ans, cnt, failed)

    # extract
    def extract_ybn(path='input'):
        '''
        1. 首先解密path文件夹内的ybn，存入path文件夹内
        2. 从input内解密的ybn提取字符串
        3. 保存到intermediate_file/jp_all.txt
        '''

        file_all = os.listdir(path)
        if 'decoded' not in file_all:
            for f in file_all:
                _t = YU_RIS.decode_473(f'{path}/{f}')
                if _t:
                    save_file_b(f'{path}/{f}', _t[0])
                    print(f'decode {f}')
                else:
                    print(f'can not decode {f}')
            save_file_b(f'{path}/decoded', b'')
        else:
            print('文件已经解密！')

        jp_all = []
        file_all = os.listdir(path)
        for f in file_all:
            _text = YU_RIS.ybn_script_export_string(
                open_file_b(f'{path}/{f}'), YU_RIS._extract_string)
            if _text:
                print(f, len(_text))
                jp_all += _text
            else:
                print(f'不存在文本：{f}')
        # jp_chs = {}
        with open('intermediate_file/jp_all.txt', 'w', encoding='utf8') as f:
            for line in jp_all:
                f.write(line+'\n')
        #         jp_chs[line] = ''

        # save_json('intermediate_file/jp_chs.json', jp_chs)

    # output
    def output_ybn(_input='input', output='output', jp_chs='intermediate_file/jp_chs.json'):
        '''
        1. 替换input文件夹内ybn的字符串，使用gbk编码，保存到output文件夹内
        2. 加密output文件夹内的ybn文件
        '''
        failed = []
        file_all = os.listdir(_input)
        jp_chs = open_json(jp_chs)
        for f in file_all:
            _t = YU_RIS.replace_string(open_file_b(f'{_input}/{f}'), jp_chs)
            failed += _t[-1]
            if _t[2]:
                # print(f, "失败：", len(_t[2]))
                ...
            if _t[1]:
                print(f, "替换：", _t[1])
                if not os.path.exists(output):
                    os.mkdir(output)
                save_file_b(f'{output}/{f}', _t[0])
        save_json('intermediate_file/failed.json', failed)

        file_all = os.listdir(output)
        for f in file_all:
            _t = YU_RIS.decode_473(f'{output}/{f}')
            if _t:
                save_file_b(f'{output}/{f}', _t[0])
                print(f'encode {f}')
            else:
                print(f'can not encode {f}')


class PAC():
    '''
    拆包、解密、替换、加密、打包
    FIXME 选择支没有汉化
    '''
    def extract_srp():
        '''
        ,[os].+」\n -> \n
        <.+?>       -> ''
        \\n         -> ''
        '　'        -> ''
        '''
        file_all = os.listdir('input')
        ans = []
        for f in file_all:
            if f[0] != '0':
                continue
            f_data = open_file_b(f'input/{f}')
            f_data = f_data[0xc:]
            cnt = 0
            cnt2 = 0
            while len(f_data):
                _len = int.from_bytes(f_data[:2], byteorder='little')
                _str = f_data[2:2+_len]
                if _str[:2] == b'\x00\x00':
                    _str = _str[4:].decode('cp932')
                    # if _str.find('】,') != -1:
                    #     _str = _str.replace('】,', '】「')
                    #     _str += '」'
                    #     _str = _str.replace(r'\\n', '')
                    ans.append(_str)
                    cnt2 += 1
                # else:
                #     '''
                #     ('「', '」', '』', '『', '　', '【', '】'):
                #     '''
                #     _s = _str
                #     try:
                #         _s = _s.decode('cp932')
                #         if _s.count('「') or _s.count('）') or _s.count('」') or _s.count('（'):
                #             ans.append(_s)
                #             print(_s)
                #     except Exception as e:
                #         pass
                f_data = f_data[2+_len:]
                cnt += 1
            print(f, cnt, cnt2)
        save_file('intermediate_file/jp_all.txt', '\n'.join(ans))

    def replace_srp():
        def _format(s: str):
            count = s.count(',')
            if count == 0:
                return '　'+s
            else:
                _t = s.split(',')
                _t[1] = '「'+_t[1]+'」'
                return ','.join(_t)
        file_all = os.listdir('input')
        jp_chs = open_json('intermediate_file/jp_chs.json')
        cnt_all = 0
        failed = []
        for f in file_all:
            f_data = open_file_b(f'input/{f}')
            if f[0] != '0':
                save_file_b(f'output/{f}', f_data)
                continue
            f_data = open_file_b(f'input/{f}')
            ans_data = f_data[:0xc]
            f_data = f_data[0xc:]
            cnt = 0

            while len(f_data):
                _len = int.from_bytes(f_data[:2], byteorder='little')
                _str = f_data[2:2+_len]
                if _str[:2] == b'\x00\x00':
                    key = _str[4:].decode('cp932')
                    if key in jp_chs and jp_chs[key]:
                        chs = jp_chs[key]
                        chs = chs.encode('gbk', errors='ignore')
                        ans_data += int.to_bytes(len(chs)+4,
                                                 2, byteorder='little')
                        ans_data += _str[:4]
                        ans_data += chs
                        cnt += 1
                        cnt_all += 1
                    else:
                        failed.append(key)
                else:
                    ans_data += f_data[:2+_len]
                f_data = f_data[2+_len:]
            print(f, cnt)
            save_file_b(f'output/{f}', ans_data)
        print('总共替换：', cnt_all)
        save_json('intermediate_file/failed.json', failed)

    def unpack_pac(path: str, decode=True):
        def rot_byte_r(data: bytes, count: int):
            # print(data)
            count &= 7
            return data >> count | (data << (8-count)) & 0xff

        def decode_srp(data: bytes):
            # print(len(data))
            data = bytearray(data)
            record_count = int.from_bytes(data[:4], byteorder='little')
            pos = 4
            for j in range(record_count):
                chunk_size = int.from_bytes(
                    data[pos:pos+2], byteorder='little')-4
                pos += 6
                if pos + chunk_size > len(data):
                    return data
                for i in range(chunk_size):
                    if pos >= len(data):
                        print(pos, len(data), chunk_size)
                    data[pos] = rot_byte_r(data[pos], 4)
                    pos += 1
            return data

        data = open_file_b(path)
        count = int.from_bytes(data[:2], byteorder='little')
        name_length = int.from_bytes(data[2:3], byteorder='little')
        data_offset = int.from_bytes(data[3:7], byteorder='little')
        version = 2
        index_offset = 7
        dir_name = os.path.splitext(path)[0]

        if not os.path.exists('input'):
            os.mkdir('input')

        for i in range(count):
            name = data[index_offset:index_offset+name_length]
            index_offset += name_length

            _entry_offset = int.from_bytes(
                data[index_offset:index_offset+8],
                byteorder='little'
            ) + data_offset

            _entry_size = int.from_bytes(
                data[index_offset+8:index_offset+12],
                byteorder='little'
            )

            index_offset += 12

            _entry_data = data[_entry_offset:_entry_offset+_entry_size]
            if decode:
                _entry_data = decode_srp(_entry_data)
            save_file_b(f'input/{delete_zero(name)}', _entry_data)

    def repack_pac(path='output', encode=True, name_length=0xb):
        def rot_byte_r(data: bytes, count: int):
            # print(data)
            count &= 7
            return data >> count | (data << (8-count)) & 0xff

        def decode_srp(data: bytes):
            # print(len(data))
            data = bytearray(data)
            record_count = int.from_bytes(data[:4], byteorder='little')
            pos = 4
            for j in range(record_count):
                chunk_size = int.from_bytes(
                    data[pos:pos+2], byteorder='little')-4
                pos += 6
                if pos + chunk_size > len(data):
                    return data
                for i in range(chunk_size):
                    if pos >= len(data):
                        print(pos, len(data), chunk_size)
                    data[pos] = rot_byte_r(data[pos], 4)
                    pos += 1
            return data

        file_all = os.listdir(path)
        count = int.to_bytes(len(file_all), 2, byteorder='little')
        n_length = int.to_bytes(name_length, 1, byteorder='little')
        index_offset = 7 + (name_length+12)*len(file_all)
        data_offset = int.to_bytes(index_offset, 4, byteorder='little')
        ans = count+n_length+data_offset
        entry_all = b''
        data_all = b''
        for f in file_all:
            _entry_data = open_file_b(f'{path}/{f}')
            name = f.encode()

            while len(name) < 0xb:
                name += b'\x00'

            _entry_offset = int.to_bytes(
                len(data_all),
                8,
                byteorder='little'
            )

            _entry_size = int.to_bytes(
                len(_entry_data),
                4,
                byteorder='little'
            )

            entry_all += (name+_entry_offset+_entry_size)
            if encode:
                _entry_data = decode_srp(_entry_data)
            data_all += _entry_data
        save_file_b(f"{path}.pac", ans+entry_all+data_all)


class NEKOSDK():
    def extract_pak_txt():
        file_all = os.listdir('input')
        ans = []
        exist = set()
        name = set()
        for f in file_all:
            data = open_file_b(f'input/{f}')
            p = 0
            while p < len(data)-8:
                if data[p:p+0x60] == b'\x05\x00\x00\x00\x64\x00\x00\x00'+b'\x00'*0x58:
                    p += 0xc8
                    _len = int.from_bytes(data[p:p+4], byteorder='little')
                    while _len != 1 and _len <= 0xff:
                        p += 4
                        _str = data[p:p+_len-1].decode('cp932')
                        _str = re.sub(
                            r'voice\\.+ogg|\r|\n|\[テキスト表示\]| |　', '', _str)
                        _p = _str.find('「')
                        if _p != -1 and _p < 6:
                            name.add(_str[:_p])
                            _str = _str[_p:]

                        if _str == '「おいおいおい、忘れたなんて言わせねぇぞ？\n':
                            print(ans)
                        if not ans or (ans[-1].find(_str) == -1 and _str not in name):
                            # ans.append(str(p)+' '+str(_len)+ ' '+ _str)
                            ans.append(_str)
                            # exist.add(_str)

                        p += _len
                        _len = int.from_bytes(data[p:p+4], byteorder='little')
                    p += 1
                else:
                    p += 1
        save_file('intermediate_file/jp_all.txt', '\n'.join(ans))
        print(name)


class SILKY():
    def extract_mes():
        file_all = os.listdir('input')
        for f in file_all:
            os.system(f'mestool.exe p input/{f} intermediate_file/{f}')

    def cut_MES(path: str):
        '''
        拆分MES文件用于研究结构
        '''
        data = open_file_b(path)
        count = int.from_bytes(data[:4], byteorder='little')
        offset = []
        data_p = 4+4*count
        for i in range(count):
            _t = data[4+i*4:8+i*4]
            _t = int.from_bytes(_t, byteorder='little')
            offset.append(_t)
        for i in range(count-1):
            _data = data[data_p+offset[i]:data_p+offset[i+1]]
            save_file_b(f'temp/{i}', _data)
        save_file_b(f'temp/{count-1}', data[data_p+offset[-1]:])

    def create_dict_sliky():
        jp_all = open_file('intermediate_file/jp_all.txt').splitlines()
        name = set()
        for i in jp_all:
            if len(i) < 7:
                for c in '「…・』。　':
                    if i.count(c):
                        break
                else:
                    name.add(i)
        name_buff = ''
        # print(name)
        try:
            jp_chs = open_json('intermediate_file/jp_chs.json')
        except Exception as e:
            print('第一次建立字典')
            jp_chs = dict()
        cnt = 0
        for i in jp_all:
            if i in name:
                name_buff = i
            else:
                key = i
                key = key.replace('　', '')
                if key not in jp_chs:
                    cnt += 1
                    jp_chs[key] = ''
                key += name_buff
                if key not in jp_chs:
                    cnt += 1
                    jp_chs[key] = ''
                name_buff = ''
        print('添加', cnt, '条')
        save_json('intermediate_file/jp_chs.json', jp_chs)


class SNL():
    '''
    VNR的问题
    のの 
    '''
    def _split_line(text: str) -> list:
        '''
        用正则表达式切割文本，遇到'「', '」', '…', '。', '，', '―', '”', '“', '☆', '♪', '、', '‘', '’', '』', '『', '　', 
        '''
        split_str = '。？！】'
        _ans = []
        _buffer = ''
        for i in text:
            _buffer += i
            if i in split_str and len(_buffer):
                _ans.append(_buffer)
                _buffer = ''
        return _ans

    def extract_snl():
        file_all = os.listdir('input')
        ans = []
        for f in file_all:
            data = open_file_b(f'input/{f}')
            _len = int.from_bytes(data[8:12], byteorder='little')
            _str = data[-1*_len:]
            buff = b''
            for i in _str:
                if i == 0 and len(buff):
                    try:
                        _t = buff.decode('cp932')
                        _t = re.sub(r'\[.+?\]|\n|\r', '', _t)
                        ans.append(_t)
                    except Exception as e:
                        print(buff)
                        print(e)
                    buff = b''
                elif i == 0:
                    pass
                else:
                    buff += int.to_bytes(i, 1, byteorder='little')
        save_file('intermediate_file/jp_all.txt', '\n'.join(ans))

    def create_dict():
        jp_all = open_file('intermediate_file/jp_all.txt').splitlines()
        try:
            jp_chs = open_json('intermediate_file/jp_chs.json')
        except Exception as e:
            print('第一次建立字典')
            jp_chs = dict()
        cnt = 0
        for i in jp_all:
            text_list = SNL._split_line(i)
            for t in text_list:
                if t not in jp_chs:
                    jp_chs[t] = ''
                    cnt += 1
        print('添加', cnt, '条')
        jp_chs['engine'] = 'snl'
        save_json('intermediate_file/jp_chs.json', jp_chs)


class DXLib():
    '''
    _VIEW 前24字节完全一样
    name: [120224][ルネ Team Bitters] マリッジブルー[婚約者がいるのに、どうしてこんな男に……]
    key: b'\xb5\xbf\xad\xbf\xa7\xbf'

    name: [110325][ルネ Team Bitters] それでも妻を愛してる
    key: b'\xa1\xb2\xbb\xa9\xb2\xbf\xb2\xbf\xb3\xb7'

    name: [130222][ルネ Team Bitters]魔法少女はキスして変身る
    key: b'\xb7\xb1\xae\xb7'

    name: [150529]光翼戦姫エクスティア1
    key: b'\x9b\xd0\xcf\xd0\x9b\x88\x8d\x8c\x97\x9f\xd0\xcf\x94\x8b\x8d\x8c\x9b\x8e\x97\x8d'

    name: [160129]光翼戦姫エクスティア２
    key: b'\x9b\xd0\xcf\xce\x9b\x88\x8d\x8c\x97\x9f\xd0\xce\x94\x8b\x8d\x8c\x9b\x8e\x97\x8d'

    name: [170512]光翼戦姫エクスティアA
    key: b'\xd0\xcf\xcd\x9b\x88\x8d\x8c\x97\x9f\xbf\x94\x8b\x8d\x8c\x9b\x8e\x97\x8d\x9b'

    '''
    key = b'\xd0\xcf\xcd\x9b\x88\x8d\x8c\x97\x9f\xbf\x94\x8b\x8d\x8c\x9b\x8e\x97\x8d\x9b'

    def create_key_dx():
        Key = b'\xAA'*12
        Key = bytearray(Key)
        Key[0] ^= 0xff
        Key[1] = ((Key[1] >> 4) | (Key[1] << 4)) & 0xff
        Key[2] = Key[2] ^ 0x8a
        Key[3] = ((((Key[3] >> 4) | (Key[3] << 4))) ^ 0xff) & 0xff
        Key[4] ^= 0xff
        Key[5] = Key[5] ^ 0xac
        Key[6] ^= 0xff
        Key[7] = ((((Key[7] >> 3) | (Key[7] << 5))) ^ 0xff) & 0xff
        Key[8] = ((Key[8] >> 5) | (Key[8] << 3)) & 0xff
        Key[9] = Key[9] ^ 0x7f
        Key[10] = (((Key[10] >> 4) | (Key[10] << 4)) ^ 0xd6) & 0xff
        Key[11] = Key[11] ^ 0xcc
        return Key

    def decrypt(_data: bytes):
        '''

        '''
        _data = bytearray(_data)

        for i in range(0x10, len(_data)):
            _data[i] = (_data[i]-DXLib.key[(i-0x10) % len(DXLib.key)]) & 0xff

        return _data

    def extract_med(name=None):
        '''
        ＄０ 主人公名字
        '''
        def _has_jp(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            for ch in line:
                if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <= '\u9fa5'):
                    return True
            return False

        file_all = os.listdir('input')
        ans = []
        for f in file_all:
            _data = open_file_b(f'input/{f}')
            _data = DXLib.decrypt(_data)
            _offset = int.from_bytes(_data[4:8], byteorder='little') + 0x10
            _str = _data[_offset:]
            _buff = b''
            for i in _str:
                if i:
                    _buff += to_bytes(i, 1)
                else:
                    try:
                        _buff = _buff.decode('cp932')
                        if _has_jp(_buff) and _buff[0] not in ';':
                            if name:
                                _buff = _buff.replace('＄０', name)
                            ans.append(_buff)
                        # ans.append(_buff)
                    except Exception as e:
                        print(e)
                        print(f, _buff)
                    _buff = b''
        save_file('intermediate_file/jp_all.txt', '\n'.join(ans))

    def decode_mes():
        file_all = os.listdir('input')
        for f in file_all:
            _data = open_file_b(f'input/{f}')
            _data = DXLib.decrypt(_data)
            save_file_b(f'output/{f}', _data)

    def create_key(raw: bytes):
        base = 0x2d
        ans = ''
        for i in raw:
            ans += ('\\x'+hex(i-base)[2:])
        print(ans)

    def create_key_2():
        a = b'\x00\x23\x52\x55\x4C\x45\x5F\x56\x49\x45\x57\x45\x52\x00\x3A\x56\x49\x45\x57\x5F\x30\x00\x7B\x00'
        b = b'\xD0\xF2\x1F\xF0\xD4\xD2\xEB\xED\xE8\x04\xEB\xD0\xDF\x8C\xD5\xE4\xE0\xD2\xF2\x2F\xFF\xCD\x16\x88'
        base = 0x2d
        ans = ''
        for i in range(len(a)):
            ans += ('\\x'+hex((b[i]-a[i]) & 0xff)[2:])
        print(ans)


class ANIM():
    '''
    exe需要修改
    1. 字符范围检测 cmp   eax, 0x9F
    2. LOGFONT 8x0h -> 86h add   CreateFontIndirectA
    3. 修改空格 81 40 -> A1A1 
    '''
    def switch_key(key: bytearray, ch: int):
        t = ch
        ch &= 7
        if ch == 0:
            key[0] = byte_add(key[0], t)
            key[3] = byte_add(key[3], t, 2)
            key[4] = byte_add(key[2], t, 11)
            key[8] = byte_add(key[6]+7)
        elif ch == 1:
            key[2] = byte_add(key[9], key[10])
            key[6] = byte_add(key[7], key[15])
            key[8] = byte_add(key[8], key[1])
            key[15] = byte_add(key[5], key[3])
        elif ch == 2:
            key[1] = byte_add(key[1], key[2])
            key[5] = byte_add(key[5], key[6])
            key[7] = byte_add(key[7], key[8])
            key[10] = byte_add(key[10], key[11])
        elif ch == 3:
            key[9] = byte_add(key[2], key[1])
            key[11] = byte_add(key[6], key[5])
            key[12] = byte_add(key[8], key[7])
            key[13] = byte_add(key[11], key[10])
        elif ch == 4:
            key[0] = byte_add(key[1], 111)
            key[3] = byte_add(key[4], 71)
            key[4] = byte_add(key[5], 17)
            key[14] = byte_add(key[15], 64)
        elif ch == 5:
            key[2] = byte_add(key[2], key[10])
            key[4] = byte_add(key[5], key[12])
            key[6] = byte_add(key[8], key[14])
            key[8] = byte_add(key[11], key[0])
        elif ch == 6:
            key[9] = byte_add(key[11], key[1])
            key[11] = byte_add(key[13], key[3])
            key[13] = byte_add(key[15], key[5])
            key[15] = byte_add(key[9], key[7])
            key[1] = byte_add(key[9], key[5])
            key[2] = byte_add(key[10], key[6])
            key[3] = byte_add(key[11], key[7])
            key[4] = byte_add(key[12], key[8])
        elif ch == 7:
            key[1] = byte_add(key[9], key[5])
            key[2] = byte_add(key[10], key[6])
            key[3] = byte_add(key[11], key[7])
            key[4] = byte_add(key[12], key[8])
        return key

    def decrypt(data: bytes):
        '''
        key  54 C8 58 54 0A D8 CD 3C B5 EC 98 0F E6 9E F3 E8
        data 1F 6C 5C 54 71 0E C9 3C FE ED DA 23 E7 9E F3 AA
        ans  4B A4 04 00 7B D6 04 00 4B 01 42 2C 01 00 00 42
        '''
        key = bytearray(data[4:20])
        data = bytearray(data[20:])
        length = len(data)
        v = 0
        for i in range(length):
            data[i] = key[v] ^ data[i]
            v += 1
            if v == 16:
                v = 0
                key = ANIM.switch_key(key, data[i-1])
        return data

    def extract():
        '''
        需要提取*_define.dat和*_sce.dat
        '''
        def format_vnr(buff: str):
            buff = buff.replace('　', '')
            buff = buff.replace('@n', '')
            # [a-zA-Z].*?\n
            if buff and not (buff[0] <= 'z' and buff[0] >= 'a') and not (buff[0] <= 'Z' and buff[0] >= 'A'):
                tags = re.findall(r'@\[.*?\]', buff)
                for tag in tags:
                    _t = tag.find(':')
                    name = tag[2:_t]
                    value = tag[_t+1:-1]
                    buff = buff.replace(tag, name) + value
            return buff
        file_all = os.listdir('input')
        ans = []
        for f in file_all:
            data = open_file_b(f'input/{f}')
            data = ANIM.decrypt(data)
            if f[-6:] == 'ce.dat':
                str_offset = int.from_bytes(data[4:8], byteorder='little')
                data = data[str_offset:]
                buff = b''

                for i in data:
                    if i == 0:
                        buff = buff.decode('cp932')
                        # buff = format_vnr(buff)
                        if buff and not (buff[0] <= 'z' and buff[0] >= 'a') and not (buff[0] <= 'Z' and buff[0] >= 'A'):
                            ans.append(buff)
                        buff = b''
                    else:
                        buff += to_bytes(i, 1)
            elif f[-6:] == 'ne.dat':
                p = 0
                while p < len(data):
                    if data[p:p+2] == b'\x81\x79':
                        _p = p+2
                        while data[_p]:
                            _p += 1
                        ans.append(data[p:_p].decode('cp932'))
                        p = _p
                    p += 1
        save_file('intermediate_file/jp_all.txt', '\n'.join(ans))
        if os.path.exists('intermediate_file/jp_chs.json'):
            jp_chs = open_json('intermediate_file/jp_chs.json')
        else:
            jp_chs = dict()
        cnt = 0
        for i in ans:
            if i not in jp_chs:
                jp_chs[i] = ''
                cnt += 1
        jp_chs['engine'] = 'anim'
        save_json('intermediate_file/jp_chs.json', jp_chs)
        print('共：', len(ans))
        print('添加：', cnt)
        # save_file_b(f'intermediate_file/{f}', data)

    def encrypt(data: bytes):
        length = len(data)
        key = bytearray(b'\x00'*16)
        new_data = b'\x00\x00\x00\x01'+key+b'\x00'*length
        new_data = bytearray(new_data)

        v = 0
        print(length)
        for i in range(length):
            new_data[20+i] = key[v] ^ data[i]
            v += 1
            if v == 16:
                v = 0
                key = ANIM.switch_key(key, data[i-1])
        print(len(new_data))
        return new_data
        # save_file_b(f'output/{os.path.split(path)[-1]}', new_data)

    def output():
        def _is_name(line: str) -> bool:
            '''
            如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
            '''
            if len(line) > 4:
                return False
            for ch in line:
                if ch in ('「', '」', '…', '。', '，', '―', '”', '“', '☆', '♪', '、', '※', '‘', '’', '』', '『', '　', '゛', '・', '▁', '★', '〜', '！', '—', '【', '】'):
                    return False
            return True

        def format_vnr(buff: str):
            buff = buff.replace('　', '')
            buff = buff.replace('@n', '')
            # [a-zA-Z].*?\n
            if buff and not (buff[0] <= 'z' and buff[0] >= 'a') and not (buff[0] <= 'Z' and buff[0] >= 'A'):
                tags = re.findall(r'@\[.*?\]', buff)
                for tag in tags:
                    _t = tag.find(':')
                    name = tag[2:_t]
                    value = tag[_t+1:-1]
                    buff = buff.replace(tag, name) + value
            return buff
        jp_chs = open_json('intermediate_file/jp_chs.json')
        file_all = os.listdir('input')
        cnt = 0
        failed = []
        for f in file_all:
            data = open_file_b(f'input/{f}')
            data = ANIM.decrypt(data)
            if f[-6:] == 'ce.dat':
                data = open_file_b(f'input/{f}')
                data = ANIM.decrypt(data)
                str_offset = int.from_bytes(data[4:8], byteorder='little')
                str_data = data[str_offset:]
                str_all = []
                buff = b''
                for i in str_data:
                    if i == 0:
                        str_all.append(buff.decode('cp932'))
                        buff = b''
                    else:
                        buff += to_bytes(i, 1)

                for i in range(len(str_all)):
                    # key = format_vnr(str_all[i])
                    key = str_all[i]
                    if key in jp_chs and jp_chs[key]:
                        if _is_name(key):
                            _t = ''
                        elif key[0] in "「（『":
                            _t = '　　　'
                        else:
                            _t = '　'
                        str_all[i] = _t + jp_chs[key] + _t
                        cnt += 1
                    else:
                        failed.append(key)
                data = data[:str_offset]
                for i in str_all:
                    data += (i.encode('gbk', errors='ignore')+b'\x00')
                data += b'\x00'
                data = ANIM.encrypt(data)
                save_file_b(f'output/{f}', data)
            elif f[-6:] == 'ne.dat':
                p = 0
                data = bytearray(data)
                while p < len(data):
                    if data[p:p+2] == b'\x81\x79':
                        _p = p+2
                        while data[_p]:
                            _p += 1
                        key = data[p:_p].decode('cp932')
                        if key in jp_chs and jp_chs[key]:
                            data[p:_p] = jp_chs[key].encode(
                                'gbk', errors='ignore')
                            cnt += 1
                        else:
                            failed.append(key)
                        # p = _p
                    p += 1
                data = ANIM.encrypt(data)
                save_file_b(f'output/{f}', data)
        print('替换：', cnt)
        print('失败：', len(failed))

        save_file('intermediate_file/failed.txt', '\n'.join(failed))

    def format_t(buff: str):
        if buff and not (buff[0] <= 'z' and buff[0] >= 'a') and not (buff[0] <= 'Z' and buff[0] >= 'A'):
            tags = re.findall(r'@\[.*?\]', buff)
            for tag in tags:
                _t = tag.find(':')
                name = tag[2:_t]
                value = tag[_t+1:-1]
                buff = buff.replace(tag, name)
        return buff


class Lilim():
    class BitStream:
        def __init__(self, data: bytes):
            self.m_input = data
            self.m_bits = 0         # bit缓存
            self.m_chached_bits = 0  # 记录bit缓存剩余的bit数
            self.pos = 0            # bit位
            self.tree = []

        def get_bits(self, count: int) -> int:
            '''
            获取n位bit，转换成int后输出，指针后移count位
            '''
            self.pos += count
            if count > 24:
                return -1
            while self.m_chached_bits < count:
                if not len(self.m_input):
                    return -1
                b = self.m_input[0]
                self.m_input = self.m_input[1:]

                self.m_bits = (self.m_bits << 8) | b
                self.m_bits = self.m_bits & 0xffffffff
                self.m_chached_bits += 8
            mask = (1 << count) - 1
            self.m_chached_bits -= count
            ans = ((self.m_bits >> self.m_chached_bits) & mask)
            self.tree.append(ans)
            return ans

        def get_next_bit(self):
            return self.get_bits(1)

        def display(self):
            print(self.m_bits, self.m_chached_bits, self.m_input[:20])

    class HuffmanCompressor:
        def __init__(self, data_decoded: bytes):
            self.data = data_decoded
            self.code_table = {}
            self.new_tree = []

            node_dict = dict()
            tree = []
            for ch in data_decoded:
                if ch not in node_dict:
                    node_dict[ch] = 0
                node_dict[ch] += 1
            for key in node_dict:
                tree.append(Lilim.node(key, node_dict[key]))

            self.root = self.build_tree(tree)[0]
            self.disp_tree(self.root, [])

            # print(self.code_table)
            # print(self.new_tree)

        # FIXME
        def compress(self):
            new_data = ''
            # 先全变成01串
            for i in self.new_tree:
                _t = bin(i)[2:]
                if _t not in ('0', '1'):
                    _t = self.fill_zero(_t)
                new_data += _t
            for i in self.data:
                if i not in self.code_table:
                    raise Exception(f'编码错误：{i}')
                new_data += self.code_table[i]

            # 把01串转换成bytes串
            bytes_length = int(len(new_data)/8+0.5)
            ans = int.to_bytes(len(self.data)+1, 4, byteorder='little')
            for i in range(bytes_length):
                _t = new_data[i*8:i*8+8]
                if len(_t) < 8:
                    _t = self.fill_zero(_t, False)
                _t = (self.bin_to_byte_8(_t))
                ans += int.to_bytes(_t, 1, byteorder='little')

            return ans

        # 哈夫曼树构建
        def build_tree(self, l):
            if len(l) == 1:
                return l
            sorts = sorted(l, key=lambda x: x.value, reverse=False)
            n = Lilim.node.build_father(sorts[0], sorts[1])
            sorts.pop(0)
            sorts.pop(0)
            sorts.append(n)
            return self.build_tree(sorts)
        def disp_tree(self, node: 'node', path):
            if not node.left and not node.right:
                self.code_table[node.ch] = ''.join(map(str, path))
                self.new_tree.append(0)
                self.new_tree.append(node.ch)
                return
            self.new_tree.append(1)
            self.disp_tree(node.left, path+[0])
            self.disp_tree(node.right, path+[1])

        def bin_to_byte_8(self, data: str) -> bytes:
            if len(data) != 8:
                raise Exception(f'长度错误！{len(data)}')
            ans = 0
            for i in data:
                ans = ans << 1
                ans |= (1 if i == '1' else 0)
            return ans

        def fill_zero(self, data: str, front=True) -> str:
            '''
            吧字符串前面或后面补上0
            '''
            if len(data) > 8:
                raise Exception(f'长度错误！{len(data)}')
            if front:
                return data.rjust(8, '0')
            else:
                return data.ljust(8, '0')

        def int_to_byte_8(self, data: int):
            _data = bin(data)[2:]
            _data = self.fill_zero(_data)
            return bin_to_byte_8(_data)

    class node:
        def __init__(self, ch=None, value=None, left=None, right=None, father=None):
            self.ch = ch          # 字符
            self.value = value    # 数据域
            self.left = left      # 左孩子
            self.right = right    # 右孩子
            self.father = father  # 父亲结点

        def build_father(left, right):
            n = Lilim.node(value=left.value + right.value,
                           left=left, right=right)
            left.father = right.father = n
            return n

    class HuffmanDecompressor:
        def __init__(self, data: bytearray, tree=None):
            self.m_length = int.from_bytes(
                data[:4], byteorder='little')  # 解压后大小
            self.tree_size = 512
            self.lhs = [0 for i in range(512)]
            self.rhs = [0 for i in range(512)]
            self.m_token = 256
            self.m_buffer = bytearray()
            self.m_input = Lilim.BitStream(data[4:])

        def unpack(self):
            self.m_token = 256
            root = self.create_tree()
            # print(self.rhs)
            # print(self.lhs)
            # print('root:', root, 'bit pos:', self.m_input.pos)
            while self.m_length > 1:
                symbol = root
                while symbol >= 0x100:
                    bit = self.m_input.get_bits(1)
                    if bit == -1:
                        print('error')
                        return
                    if (bit == 1):
                        symbol = self.rhs[symbol]
                    else:
                        symbol = self.lhs[symbol]
                self.m_buffer.append(symbol)
                self.m_length -= 1

        def decode(self):
            self.unpack()
            # print(self.m_buffer)
            return self.m_buffer

        def create_tree(self):
            bit = self.m_input.get_bits(1)
            if (-1 == bit):
                raise Exception(
                    'Unexpected end of the Huffman-compressed stream.')
            elif bit != 0:
                v = self.m_token
                self.m_token += 1
                if (v > self.tree_size):
                    raise Exception('Invalid Huffman-compressed stream.')
                self.lhs[v] = self.create_tree()
                self.rhs[v] = self.create_tree()
                return v
            else:
                return self.m_input.get_bits(8)

    def extract():
        def get_scenario_from_origin(data: list) -> list:
            text_all = []
            buff = ''
            cnt = 0
            # START FIXME
            for line in data:
                line = line[:-1]
                if not line and buff:
                    buff = buff.replace('[', '')
                    buff = buff.replace(']', '')
                    buff = buff.replace('　', '')
                    text_all.append(buff+'\n')
                    buff = ''
                elif line:
                    if line[0] not in '#:^%\t$ｔ' and not ('a' <= line[0] <= 'z'):
                        buff += line
                cnt += 1
            # END

            return text_all
        extract_jp(get_scenario_from_origin, 'cp932')


class RPM():
    '''
    exe 只需要改 createfont 80

    0-4 filecount
    4-8 isconpressed 0|1

    struct ARCHDR {
        unsigned long entry_count;
        unsigned long unknown;
    };

    struct ARCENTRY {
        char          filename[32];
        unsigned long original_length;
        unsigned long length;
        unsigned long offset;
    };
    '''
    '''
    def guess_scheme(index_offset: int, possible_name_sizes: list, m_file: bytes, m_count: int):
        first_entry = m_file[index_offset:possible_name_sizes[0] + 12+index_offset]
        key_bits = [0, 0, 0, 0]
        actual_offset = [0, 0, 0, 0]
        for name_length in possible_name_sizes:
            first_offset = index_offset + m_count*(name_length+12)
            actual_offset = to_bytes(first_offset, 4)

            for i in range(4):
                key_bits[i] = first_entry[name_length+8+i]-actual_offset[i]
                key_bits[i] = byte_add(key_bits[i])

            first_match = RPM.reverse_find(
                first_entry, name_length-4, key_bits)
            # print(first_match)
            if first_match < 4:
                continue
            second_match = RPM.reverse_find(
                first_entry, first_match-4, key_bits)
            if second_match <= 0:
                continue
            key_length = first_match - second_match
            key = [0]*key_length
            print(key_length, first_match, second_match, key_bits)
            for i in range(key_length):
                sym = byte_add(-first_entry[second_match+i])
                if sym < 0x21 or sym > 0x75:
                    break
                key[(second_match+i) % key_length] = sym
            if i == key_length:
                return (key, name_length)

    def reverse_find(array: bytes, pos: int, pattern: list):
        print(list(map(hex, array)), '\n', pos, '\n', list(map(hex, pattern)))
        pattern_end_pos = len(pattern)-1
        pattern_pos = pattern_end_pos
        i = pos + pattern_pos
        while i >= 0:
            if array[i] == pattern[pattern_pos]:
                if 0 == pattern_pos:
                    return i
                pattern_pos -= 1
            elif pattern_end_pos != pattern_pos:
                i += (pattern_end_pos - pattern_pos)
                pattern_pos = pattern_end_pos
            i -= 1
        return -1

    def decrypt_index(data: bytes, key: list):
        data = bytearray(data)
        for i in range(len(data)):
            data[i] = byte_add(data[i], key[i % len(key)])
        return bytes(data)

    def read_index(offset: int, scheme: tuple, m_count: int, m_file: bytes):
        index_size = m_count * (scheme[1]+12)
        index = m_file[offset:offset+index_size]
        index = RPM.decrypt_index(index, scheme[0])

        return index

    def unpack_arc(path='msg.arc', key='NTR', name_length=0x20):
        data = open_file_b(path)
        m_count = from_bytes(data[:4])
        # scheme = RPM.guess_scheme(8, [0x20,0x18], data, m_count)
        scheme = [list(map(ord, key)), name_length]

        print(scheme)
        index = RPM.read_index(8, scheme, m_count, data)
        c = LzssCompressor()
        pos = 0
        while pos < len(index):
            name = index[pos:pos+name_length]
            name = delete_zero(name, 'cp932')
            pos += name_length
            _out_length = from_bytes(index[pos:pos+4])
            pos += 4
            _length = from_bytes(index[pos:pos+4])
            pos += 4
            _offset = from_bytes(index[pos:pos+4])
            pos += 4
            _data = data[_offset:_offset+_length]
            _data = c.decompres(_data, _out_length)
            print(name, len(name), len(_data))
            save_file_b(f'input/{name}', _data)
    '''
    def formate(text:str):
        tags = re.findall(r'<WinRubi.*?>', text)
        for t in tags:
            p = t.find(',')
            name = t[9:p]
            text = text.replace(t, name, 1)
        return text

    def repack_arc(key='NTR', name_length=0x20):
        key = list(map(ord, key))
        file_all = os.listdir('output')
        index = [to_bytes(len(file_all), 4)+b'\x00\x00\x00\x00']
        data = []
        data_offset = 8+len(file_all)*(name_length+12)
        for f in file_all:
            _file = open_file_b(f'output/{f}')
            data.append(_file)
            _name = f.encode('cp932')
            if len(_name) < name_length:
                _name += b'\x00' * (name_length-len(_name))
            _name += to_bytes(len(_file),4)*2
            _name += to_bytes(data_offset, 4)
            index.append(_name)
            data_offset += len(_file)
        index += data
        output_data = b''.join(index)
        output_data = bytearray(output_data)
        index_length = len(file_all)*(name_length+12)
        for pos in range(index_length):
            # print(output_data[pos+8] , key[pos%len(key)])
            output_data[pos+8] = (output_data[pos+8] - key[pos%len(key)]) & 0xff
        save_file_b('msg.arc', output_data)
        


if __name__ == "__main__":
    # print(SNL._split_line('えっ！？いや、そんなつもりは‥‥ないけど。'))
    # SNL.create_dict()

    # DXLib.extract_med()
    # DXLib.create_key(b'\xC8\xFD\xFC\xFD\xC8\xB5\xBA\xB9\xC4\xCC\xFD\xFC\xC1\xB8\xBA\xB9\xC8\xBB\xC4\xBA')
    # DXLib.decode_mes()

    # ANIM.extract()
    # ANIM.output()

    # Lilim.extract()

    # PAC.extract_srp()
    # PAC.replace_srp()
    # PAC.repack_pac()

    # RPM.unpack_arc()
    # RPM.repack_arc()
    # print(RPM.formate('　なあ、<WinRubi 福永,ふくなが><WinRubi 裕人,ゆうと>よ！！」'))

    pass