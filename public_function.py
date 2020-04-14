# 一些常用功能的集合
import os
import json
import re
import sqlite3
from tencentfanyi import translate as tencent_t
from baidufanyi import translate as baidu_t
from struct import unpack,pack
from pdb import set_trace as int3
import chardet



def convert_code(to_code:str):
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
        cnt+=1
    return text_all


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
        if ch >= '\u0800' and ch < '\u4e00' and ch not in ('「', '」', '…', '。', '，', '―', '”', '“', '☆', '♪', '、','※', '‘', '’', '』', '『', '　', '゛', '・', '▁', '★', '〜', '！', '—','【','】'):
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
        with open(file_name, 'r', encoding=encoding) as f:
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
    encoding="utf8"
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
    encoding='utf8'
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
        f.write(json.dumps(j_c,ensure_ascii=False))


def check_dict():
    '''
    打开jp-chs.json文件检查
    '''
    encoding='utf8'
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


def _translate(text: str, db=None) -> str:
    '''
    切割语句
    判断是否有日文
    逐个翻译
    '''
    _text_list = split_line(text)
    for _text in _text_list:
        if _text and has_jp(_text):
            # 补上标点,以提高翻译质量
            pun_positon = text.find(_text)+len(_text)
            if pun_positon < len(text):
                pun = text[pun_positon]
                if pun in ('？', '！', '。'):
                    _text+=pun
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


def translate(interval=30):
    '''
    把字典翻译
    '''
    encoding='utf8'
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        data = json.loads(f.read())

    need_translated = len(list(data.keys()))
    cnt = 0
    cnt_last = 0
    failed_list = []
    conn = sqlite3.connect('data/data.db')
    for key in data:
        if not data[key] or key == data[key] or has_jp(data[key]):
            ans = _translate(key, conn)
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
            f.write(json.dumps(data,ensure_ascii=False))
        with open('intermediate_file/failed.txt', 'w', encoding=encoding) as f:
            for line in failed_list:
                f.write(line+'\n')
        print('失败：', len(failed_list), '个！')


def check_dict_untranslated():
    '''
    检查字典中是否有没翻译的日文，如value为空或和key相等或含有日文
    '''
    encoding='utf8'
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
    encoding='utf8'
    with open('intermediate_file/jp_all.txt', 'r', encoding=encoding) as f:
        jp_all = f.readlines()
    with open('intermediate_file/jp_chs.json', 'r', encoding=encoding) as f:
        data = json.loads(f.read())
    cnt = 0
    with open('intermediate_file/contrast.txt', 'w', encoding=encoding) as f:
        for line in jp_all:
            key = line[:-1]
            if key in data:
                f.write(key+' '+ data[key]+'\n')


def split_line(text: str) -> list:
    '''
    用正则表达式切割文本，遇到'「', '」', '…', '。', '，', '―', '”', '“', '☆', '♪', '、', '‘', '’', '』', '『', '　', 
    '''
    split_str = r'\[.*?\]|<.+?>|「|」|…+|。|』|『|　|―+|）|（|・|？|！|★|☆|♪|※|\\|“|”|"|\]|\[|\/|\;|【|】'
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
    if encoding=='':
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


def to_database(jp:str, ch:str, db=None):
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


def translate_local(jp:str, db=None):
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

        with open('output/'+file_name, 'w', encoding=output_encoding) as f:
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
            for i,ch in enumerate(line):
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


# Majiro
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
    def __init__(self, data:bytes):
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
    
    def read(self, count:int) -> str:
        ans = self._stream[self._pos:self._pos+count]
        self._pos += count
        return ans.decode('cp932')
    
    def seek(self, pos:int):
        self._pos = pos

    def __len__(self):
        return len(self._stream)

class MjoParser():
    'Parse a Mjo script.'
    def __init__(self,mjo:ByteIO):
        self.text=[]
        self.code=0
        self.hdr=[mjo._stream[0:0x10]]
        self.hdr+=unpack('III',(mjo._stream[0x10:0x1c]))
        mjo.seek(0x1c)
        self.fidx=[]
        for i in range(self.hdr[3]):
            self.fidx.append((mjo.readu32(),mjo.readu32()))
        size=mjo.readu32()
        print(size, mjo.tell(), self.hdr, self.fidx)
        self.vmcode=ByteIO(mjo._stream[mjo.tell():mjo.tell()+size])
        self.XorDec(self.vmcode)
        # self.decoded = self.

    def XorDec(self,bf):
        for i in range(len(bf)):
            bf._stream[i]^=aka2key[i&0x3ff]
    def ru8(self):
        return self.vmcode.readu8()
    def ru16(self):
        return self.vmcode.readu16()
    def ru32(self):
        return self.vmcode.readu32()

    # 下面都是负责把函数对应到文本

    def p800(self):
        self.text[-1]+='pushInt '+'%d'%self.vmcode.readu32()
    def p801(self):
        slen=self.vmcode.readu16()
        s=self.vmcode.read(slen)
        self.text[-1]+='pushStr "'+s.rstrip('\0')+'"'
    def p802(self):
        p1=self.vmcode.readu16()
        p2=self.vmcode.readu32()
        p3=self.vmcode.readu16()
        self.text[-1]+='pushCopy '+'(%d,%08X,%d)'%(p1,p2,p3)
    def p803(self):
        self.text[-1]+='pushFloat '+'%X'%self.vmcode.readu32()
    def p80f(self):
        p1=self.ru32()
        p2=self.ru32()
        p3=self.ru16()
        self.text[-1]+='OP80F '+'(%08X, %X, %d)'%(p1,p2,p3)
    def p810(self):
        self.text[-1]+='OP810 '+'(%08X, %X, %d)'%(self.ru32(),self.ru32(),self.ru16())
    def p829(self):
        cnt=self.ru16()
        self.text[-1]+='pushStackRepeat '+' '.join(['%d'%self.ru8() for i in range(cnt)])
    def p82b(self):
        self.text[-1]+='return'
    def p82c(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jmp '+'%08X'%dest
    def p82d(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jnz '+'%08X'%dest
    def p82e(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jz '+'%08X'%dest
    def p82f(self):
        self.text[-1]+='pop'
    def p830(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jmp2 '+'%08X'%dest
    def p831(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jne '+'%08X'%dest
    def p832(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jbeC '+'%08X'%dest
    def p833(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jaeC '+'%08X'%dest
    def p834(self):
        self.text[-1]+='Call '+'(%08X, %d)'%(self.ru32(),self.ru16())
    def p835(self):
        self.text[-1]+='Callp '+'(%08X, %d)'%(self.ru32(),self.ru16())
    def p836(self):
        self.text[-1]+='OP836 '+self.vmcode.read(self.ru16())
    def p837(self):
        self.text[-1]+='OP837 '+'(%08X, %08X)'%(self.ru32(),self.ru32())
    def p838(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jbeUnk '+'%08X'%dest
    def p839(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jaeUnk '+'%08X'%dest
    def p83a(self):
        self.text[-1]+='Line: '+'%d'%self.ru16()
    def p83b(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jmpSel0 '+'%08X'%dest
    def p83c(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jmpSel2 '+'%08X'%dest
    def p83d(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jmpSel1 '+'%08X'%dest
    def p83e(self):
        self.text[-1]+='SetStack0'
    def p83f(self):
        self.text[-1]+='Int2Float'
    def p840(self):
        self.text[-1]+='CatString "'+self.vmcode.read(self.ru16()).rstrip('\0')+'"'
    def p841(self):
        self.text[-1]+='ProcessString'
    def p842(self):
        self.text[-1]+='CtrlStr '+self.vmcode.read(self.ru16()).rstrip('\0')
    def p843(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='jmpSelX '+'%08X'%dest
    def p844(self):
        self.text[-1]+='ClearJumpTbl'
    def p845(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='SetJmpAddr3 '+'%08X'%dest
    def p846(self):
        self.text[-1]+='OP846'
    def p847(self):
        dest=self.ru32()+self.vmcode.tell()+4
        self.text[-1]+='SetJmpAddr4 '+'%08X'%dest
    def p850(self):
        cnt=self.ru16()
        addrs=[]
        sta=self.vmcode.tell()+cnt*4
        for i in range(cnt):
            addrs.append('%08X'%(self.ru32()+sta))
        self.text[-1]+='JmpInTbl '+' '.join(addrs)
    
    code800=[
        p800,p801,p802,p803,0,0,0,0,0,0,0,0,0,0,0,p80f,
        p810,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,p829,0,p82b,p82c,p82d,p82e,p82f,
        p830,p831,p832,p833,p834,p835,p836,p837,p838,p839,p83a,p83b,p83c,p83d,p83e,p83f,
        p840,p841,p842,p843,p844,p845,p846,p847,0,0,0,0,0,0,0,0,
        p850
        ]

    code10X={
        0x100:'Mul',0x101:'Fmul',0x108:'Div',0x109:'Fdiv',0x110:'Mod',0x118:'Add',
        0x119:'Fadd',0x11a:'StrAdd',0x120:'Sub',0x121:'Fsub',0x128:'Sar',0x130:'Shl',
        0x138:'IsLE',0x139:'IsFLE',0x13a:'IsLEStr',0x140:'IsL',141:'IsFL',0x142:'IsLStr',
        0x148:'IsGE',0x149:'IsFGE',0x14a:'IsGEStr',0x150:'IsG',0x151:'IsFG',0x152:'IsGStr',
        0x158:'IsE',0x159:'IsFE',0x15a:'IsEStr',0x15b:'IsE',0x15c:'IsE',0x15d:'IsE',
        0x160:'IsNE',0x161:'IsFNE',0x162:'IsNEStr',0x163:'IsNE',0x164:'IsNE',0x165:'IsNE',
        0x168:'Xor',0x170:'CondAnd',0x178:'CondOr',0x180:'And',0x188:'Or',0x190:'IsZero',
        0x191:'Nop',0x198:'Not',0x1a0:'Neg',0x1a8:'Nop',0x1a9:'Nop'
        }

    code1BX={
        0x1b8:'Mul',0x1b9:'Fmul',0x1c0:'Div',0x1c1:'Fdiv',0x1c8:'Mod',0x1d0:'Add',
        0x1d1:'Fadd',0x1d2:'StrAdd',0x1d8:'Sub',0x1d9:'Fsub',0x1e0:'Shl',0x1e8:'Sar',
        0x1f0:'And',0x1f8:'Xor',0x200:'Or'
        }

    code27X={
        0x270:'Mov',0x271:'Mov',0x272:'MovS',0x278:'Mul',0x279:'Fmul',0x280:'Div',
        0x281:'Fdiv',0x288:'Mod',0x290:'Add',0x291:'Mov',0x292:'StrAdd',0x298:'Sub',
        0x299:'Fsub',0x2a0:'Shl',0x2a8:'Sar',0x2b0:'And',0x2b8:'Xor',0x2c0:'Or'
        }
    def p10X(self):
        self.text[-1]+='St'+self.code10X[self.code]
    def p1BX(self):
        self.text[-1]+='Gbl'+self.code1BX[self.code]+' (%d, %08X, %d)'%(self.ru16(),self.ru32(),self.ru16())
    def p21X(self):
        newcode=self.code-(0x218-0x1b8)
        self.text[-1]+='Gblp'+self.code1BX[newcode]+' (%d, %08X, %d)'%(self.ru16(),self.ru32(),self.ru16())
    def p27X(self):
        self.text[-1]+='Ar'+self.code1BX[self.code]+' (%d, %08X, %d)'%(self.ru16(),self.ru32(),self.ru16())
    def p2DX(self):
        newcode=self.code-(0x2d0-0x270)
        self.text[-1]+='Arp'+self.code1BX[newcode]+' (%d, %08X, %d)'%(self.ru16(),self.ru32(),self.ru16())
    def pLen8(self):
        self.text[-1]+='OP%X '%self.code+'(%d, %08X, %d)'%(self.ru16(),self.ru32(),self.ru16())
    def Parse(self):
        while self.vmcode.tell()<len(self.vmcode):
            self.text.append('%08X\t'%self.vmcode.tell())
            self.code=self.vmcode.readu16()
            if self.code>=0x800 and self.code<=0x850:
                func=self.code800[self.code-0x800]
                if func==0:
                    int3()
                func(self)
            elif self.code<=0x1a9 and self.code>=0x100:
                self.p10X()
            elif self.code>=0x1b8 and self.code<=0x200:
                self.p1BX()
            elif self.code>=0x218 and self.code<=0x260:
                self.p21X()
            elif self.code>=0x270 and self.code<=0x2c0:
                self.p27X()
            elif self.code>=0x2d0 and self.code<=0x320:
                self.p2DX()
            elif self.code<=0x850:
                self.pLen8()
            else:
                int3()
        newt=[str(s) for s in self.text]
        return '\r\n'.join(newt)



# .gsc
'''
提取gsc文件内的文本和把翻译后的文本插入gsc文件
'''

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
            _p = int.from_bytes(_data[offset_p+i*4:offset_p+i*4+4], byteorder='little')
            _p += str_p
            
            _stack = b''
            while _data[_p]:
                _stack +=_data[_p:_p+1]
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
            _p = int.from_bytes(_data[offset_p+i*4:offset_p+i*4+4], byteorder='little')
            offset_all.append(_p)
            
        for i in offset_all:
            _p = i
            while _data[str_p+_p]:
                _p += 1
            _str = _data[str_p+i:str_p+_p].decode('cp932')
            if _str in jp_chs and jp_chs[_str]:
                str_all.append(jp_chs[_str].encode('gbk', errors='ignore')+b'\x00')
            else:
                str_all.append(_str.encode('gbk', errors='ignore')+b'\x00')
        
        offset = 0
        for i in range(len(offset_all)):
            offset_all[i] = int.to_bytes(offset, length=4, byteorder='little')
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



# LIVEMAKER
'''
提取LIVAMEKER的文本，处理字典提高VNR命中率
'''
def get_text_from_lsb():
    for f in os.listdir('input'):
        os.system(f'lmlsb dump -m lines input/{f} -o intermediate_file/{f}')

def dump_lsb(path='input'):
    file_all = os.listdir(path)
    for f in file_all:
        os.system(f'lmlsb dump -m text {path}/{f} -o intermediate_file/{f}')

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



# YU-RIS
'''
解密ybn，提取文本，插入文本，加密ybn
'''
def decode_473(file_name):
    dec_tbl2 = [ 0xd3, 0x6f, 0xac, 0x96 ]
    with open(file_name, 'rb') as f:
        data = f.read()
    header = create_head_ystb(data)
    # print(header)
    if not header or header['magic_8*4'] != 'YSTB':
        print('未知文件：', file_name)
        return None
    
    header_byte = data[:32]
    data = list(data)
    
    data1_pointer = 32
    for i in range(header['data1_length_32']):
        ch = data[data1_pointer+i]
        ch ^= dec_tbl2[i&3]
        data[data1_pointer+i] = ch.to_bytes(1, 'little')
    
    data2_pointer = 32 + header['data1_length_32']
    for i in range(header['data2_length_32']):
        ch = data[data2_pointer+i]
        ch ^= dec_tbl2[i&3]
        data[data2_pointer+i] = ch.to_bytes(1, 'little')
    
    data3_pointer = data2_pointer + header['data2_length_32']
    for i in range(header['data3_length_32']):
        ch = data[data3_pointer+i]
        ch ^= dec_tbl2[i&3]
        data[data3_pointer+i] = ch.to_bytes(1, 'little')
    
    data4_pointer = data3_pointer + header['data3_length_32']
    for i in range(header['data4_length_32']):
        ch = data[data4_pointer+i]
        ch ^= dec_tbl2[i&3]
        data[data4_pointer+i] = ch.to_bytes(1, 'little')
    
    data = header_byte + b''.join(data[32:])

    return data, header

def create_head_ystb(data:bytes):
    header = {
        'magic_8*4':data[:4].decode(),
        'version_32':0,
        'data1_length_div_4_32':0,
        'data1_length_32':0,
        'data2_length_32':0,
        'data3_length_32':0,
        'data4_length_32':0,
        'reserved_32':0
    }
    if header['magic_8*4'] != 'YSTB':
        return None
    cnt = 1
    for key in header:
        if key == 'magic_8*4':
            continue
        header[key] = int.from_bytes(data[cnt*4:cnt*4+4],byteorder='little')
        cnt += 1
    return header

def create_ystb473_method_t(data:bytes):
    return {
        'code_8':data[0],
        'args_8':data[1],
        'un_8*2':data[2:]
    }

def create_ystb473_parameter_t(data:bytes):
    return {
        'un_32':int.from_bytes(data[:4],byteorder='little'),
        'char_count_32':int.from_bytes(data[4:8],byteorder='little'),
        'char_offset_32':int.from_bytes(data[8:12],byteorder='little')
    }

def cut_ybn(data:bytes, header=None):
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
        header = create_head_ystb(data)
    p_m = 32
    p_p = 32+header['data1_length_32']
    p_s = p_p + header['data2_length_32']
    p_u = p_s + header['data3_length_32']
    body = {
        'header':data[:32],
        'methord':data[p_m:p_p],
        'parameter':data[p_p:p_s],
        'str':data[p_s:p_u],
        'un':data[p_u:]
    }
    return body

def cut_by_len(data:bytes, _len:int, create):
    '''
    切割区域并构造字典式结构体
    '''
    __len = int(len(data)/_len)
    ans = []
    for i in range(__len):
        _t = create(data[i*_len:i*_len+_len])
        ans.append(_t)
    return ans

def _extract_string(data:bytes):
    def _has_jp(line: str) -> bool:
        '''
        如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
        '''
        for ch in line:
            if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <='\u9fa5'):
                return True
        return False
    ans = ''
    try:
        _str = data.decode('cp932')

        if not _has_jp(_str):
            raise Exception('Not jp')
        if _str[0] in ("M",'H', 'V', 'B', 'F', 'L', 'I', 'W','v'):
            raise Exception('Not jp')
        ans = _str
    except Exception as e:
        pass
    finally:
        return ans

def ybn_script_export_string(data:bytes, extract=None):
    '''
    传入ybn的byte串，和提取方法，摘取字符串，返回[str,str...]
    '''
    def _has_jp(line: str) -> bool:
        '''
        如果含有日文文字（除日文标点）则认为传入文字含有日文, 返回true
        '''
        for ch in line:
            if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <='\u9fa5'):
                return True
        return False
    def _extract_button(data:bytes):
        ans = ''
        try:
            if data[-1] != 34 or data[0] != 77:
                ans = ''
                raise Exception()
            p = data.find(0x22)
            _str = data[p+1:-1].decode('shiftjis')
            if p!=-1 and _has_jp(_str) and _str[0] not in '■◆':
                ans = _str
        except Exception as e:
            ans=''
        finally:
            return ans
    
    if not data:
        return
    header = create_head_ystb(data)
    if not header:
        return None

    body = cut_ybn(data, header)
    all_methord = cut_by_len(body['methord'], 4, create_ystb473_method_t)
    all_parameter = cut_by_len(body['parameter'], 12, create_ystb473_parameter_t)
    methord_code = []
    for i in all_methord:
        methord_code += [i['code_8'] for x in range(i['args_8'])]

    ans = []
    for i in range(len(all_parameter)):
        # 提取字符串
        _p = all_parameter[i]['char_offset_32']
        all_parameter[i]['str'] = body['str'][_p: _p+all_parameter[i]['char_count_32']]
        _str = extract(all_parameter[i]['str'])
        if methord_code[i] == 91:
            ans.append(_str)
        _str = _extract_button(all_parameter[i]['str'])
        if _str:
            ans.append(_str)

    return ans

def create_parameter_bytes(para:list):
    ans = b''
    for i in para:
        ans += int.to_bytes(i['un_32'], 4, byteorder='little')
        ans += int.to_bytes(i['char_count_32'], 4, byteorder='little')
        ans += int.to_bytes(i['char_offset_32'], 4, byteorder='little')
    return ans

def can_decoded_gb2312(data:str):
    ans = True
    try:
        for i in data:
            i.encode('gb2312')
    except Exception as e:
        ans = False
    finally:
        return ans
       
def replace_string(data:bytes, jp_chs:dict):
    '''
    修改对应位置数据
    修改表头数据
    返回(ans:bytes, cnt:int, faild:list)

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
            if (ch >= '\u0800' and ch < '\u9fa5') or ('\u4e00' <= ch and ch <='\u9fa5'):
                return True
        return False
    def _extract_button(data:bytes):
        ans = ''
        p = -1
        try:
            if data[-1] != 34 or data[0] != 77:
                ans = ''
                raise Exception()
            p = data.find(0x22)
            _str = data[p+1:-1].decode('shiftjis')
            if p!=-1 and _has_jp(_str) and _str[0] not in '■◆':
                ans = _str
        except Exception as e:
            ans=''
        finally:
            return ans, p

    header = create_head_ystb(data)
    if not data or not header:
        return None, 0, []
    
    body = cut_ybn(data, header)
    all_methord = cut_by_len(body['methord'], 4, create_ystb473_method_t)
    all_parameter = cut_by_len(body['parameter'], 12, create_ystb473_parameter_t)
    methord_code = []
    for i in all_methord:
        methord_code += [i['code_8'] for x in range(i['args_8'])]

    faild = []
    cnt = 0

    for i in range(len(all_parameter)):
        _para = all_parameter[i]
        _para['index'] = i
        _p_str = _para['char_offset_32']
        _para['str'] = (body['str'][_p_str:_p_str+_para['char_count_32']])
        _para['char_count_32'] = len(_para['str'])
        if methord_code[i] == 91 and _para['un_32'] == 0:
            _key = _para['str'].decode('cp932')
            if  _key in jp_chs and jp_chs[_key]:
                _para['str'] = jp_chs[_key].encode('gbk',errors='ignore')
                _para['char_count_32'] = len(_para['str'])
                cnt += 1
            else:
                faild.append(_key)
        _key, _p = _extract_button(_para['str'])
        if _key:
            # print(_key, key in jp_chs)
            if _key in jp_chs and jp_chs[_key]:
                _para['str'] = bytearray(_para['str'])
                _para['str'][_p+1:-1] = jp_chs[_key].encode('gbk',errors='ignore')
                _para['str'] = bytes(_para['str'])
                _para['char_count_32'] = len(_para['str'])
                cnt += 1
            else:
                faild.append(_key)
    
    # # 没有替换则直接返回
    # if cnt == 0 and len(faild) == 0:
    #     return (data, cnt, faild)

    # 对齐参数, 需要排序
    
    all_parameter = sorted(all_parameter, key=lambda x: x['char_offset_32'])
    body['str'] = all_parameter[0]['str']
    for i in range(1, len(all_parameter)):
        _para_now = all_parameter[i]
        _para_pre = all_parameter[i-1]
        _para_now['char_offset_32'] = _para_pre['char_offset_32'] + _para_pre['char_count_32']
        body['str'] += all_parameter[i]['str']
    all_parameter = sorted(all_parameter, key=lambda x: x['index'])

    # 链接字符串
    body['header'] = bytearray(body['header'])
    body['header'][20:24] = int.to_bytes(len(body['str']),length=4, byteorder='little')

    body['parameter'] = create_parameter_bytes(all_parameter)
    ans = body['header'] + body['methord'] + body['parameter'] + body['str'] + body['un']

    # print(cnt, len(faild))
    # 检查parameter 和 字符串长度
    for i in all_parameter:
        _p_str = i['char_offset_32']
        if bytes(i['str']) != body['str'][_p_str:_p_str+i['char_count_32']]:
            print(header)
            print(len(all_parameter), len(body['str']), header['data3_length_32'])
            print(i)
            print(bytes(i['str']))
            print(body['str'][_p_str:_p_str+i['char_count_32']])
            raise Exception('根本没拼对！！')
    _body = cut_ybn(ans)
    _header = create_head_ystb(ans)
    if _header['data3_length_32'] != len(body['str']):
        print(header)
        print(len(all_parameter), len(body['str']), header['data3_length_32'])
        print(_header['data3_length_32'], len(body['str']))
        raise Exception('头部字符串长度')

    return (ans, cnt, faild)

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
            _t = decode_473(f'{path}/{f}')
            if _t:
                save_file_b(f'{path}/{f}', _t[0])
                print(f'decode {f}')
            else:
                print(f'can not decode {f}')
        save_file_b(f'{path}/decoded',b'')
    else:
        print('文件已经解密！')

    jp_all = []
    file_all = os.listdir(path)
    for f in file_all:
        _text = ybn_script_export_string(open_file_b(f'{path}/{f}'), _extract_string)
        if _text:
            print(f, len(_text))
            jp_all += _text
        else:
            print(f'不存在文本：{f}')
    jp_chs = {}
    with open('intermediate_file/jp_all.txt', 'w', encoding='utf8') as f:
        for line in jp_all:
            f.write(line+'\n')
            jp_chs[line] = ''

    save_json('intermediate_file/jp_chs.json', jp_chs)

# output
def output_ybn(_input='input', output='output',jp_chs='intermediate_file/jp_chs.json'):
    '''
    1. 替换input文件夹内ybn的字符串，使用gbk编码，保存到output文件夹内
    2. 加密output文件夹内的ybn文件
    '''
    faild = []
    file_all = os.listdir(_input)
    jp_chs = load_json(jp_chs)
    for f in file_all:
        _t = replace_string(open_file_b(f'{_input}/{f}'), jp_chs)
        faild+=_t[-1]
        if _t[2]:
            print(f, "失败：", len(_t[2]))
        if _t[1]:
            print(f, "替换：", _t[1])
            if not os.path.exists(output):
                os.mkdir(output)
            save_file_b(f'{output}/{f}', _t[0])
    save_json('intermediate_file/faild.json', faild)

    file_all = os.listdir(output)
    for f in file_all:
        _t = decode_473(f'{output}/{f}')
        if _t:
            save_file_b(f'{output}/{f}', _t[0])
            print(f'encode {f}')
        else:
            print(f'can not encode {f}')



if __name__ == "__main__":
    _text = '「んぐっ、んぐっ、んぐっ、んぐっ、んぐっ、んぐっ、んぐっ………ブフゥーーッッ！　ゲホゲホッ！　はぁっ！　はぁはぁっ！　ゲホゲホッ……！」'
    print(delete_label(_text))
    print(split_line(delete_label(_text)))

